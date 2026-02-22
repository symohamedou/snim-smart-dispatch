import streamlit as st
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from datetime import datetime, timedelta
import io
import easyocr
import re
import os
import time
import sqlite3
import queue
import threading
import av
from streamlit_webrtc import webrtc_streamer

# --- 0. MODE HORS-LIGNE : Stockage local SQLite ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FICHIER_DB = os.path.join(SCRIPT_DIR, "snim_detections.db")

def init_db():
    """Crée la base de données locale si elle n'existe pas."""
    conn = sqlite3.connect(FICHIER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            heure TEXT,
            camion TEXT,
            nature TEXT,
            point TEXT,
            site TEXT,
            tonnage INTEGER,
            shift TEXT,
            sync INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def charger_donnees_locales():
    """Charge toutes les détections depuis la base locale."""
    init_db()
    conn = sqlite3.connect(FICHIER_DB)
    cur = conn.execute(
        "SELECT heure, camion, nature, point, site, tonnage, shift FROM detections ORDER BY id"
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {"Heure": r[0], "Camion": r[1], "Nature": r[2], "Point": r[3], "Site": r[4], "Tonnage": r[5], "Shift": r[6] or "Matin"}
        for r in rows
    ]

def sauvegarder_detection(d):
    """Sauvegarde une détection dans la base locale (mode hors-ligne)."""
    init_db()
    conn = sqlite3.connect(FICHIER_DB)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """INSERT INTO detections (date, heure, camion, nature, point, site, tonnage, shift, sync, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)""",
        (datetime.now().strftime("%Y-%m-%d"), d["Heure"], d["Camion"], d["Nature"],
         d["Point"], d["Site"], d["Tonnage"], d.get("Shift", "Matin"), now)
    )
    conn.commit()
    conn.close()

# --- 1. CONFIGURATION MOBILE ---
# On utilise la caméra native (0) pour le mode hors-ligne sur Android
LISTE_CAMERAS = {
    "Caméra Android": 0
}

# --- 2. INITIALISATION IA (TFLITE) ---
@st.cache_resource
def initialiser_ia():
    # On pointe sur le fichier que je vois dans ton dossier
    chemin_model = os.path.join(SCRIPT_DIR, "best_float32.tflite") 
    model_yolo = YOLO(chemin_model, task='detect')
    reader_ocr = easyocr.Reader(['en'], gpu=False)
    return model_yolo, reader_ocr

try:
    model, reader = initialiser_ia()
except Exception as e:
    st.error(f"Erreur : Assure-toi que 'best_float32.tflite' est dans le même dossier que ce script.")
    st.stop()

# --- 3. INTERFACE DISPATCHER (IDENTIQUE) ---
st.set_page_config(page_title="SNIM SMART DISPATCH | MOBILE", layout="wide")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Logo_SNIM.svg/1200px-Logo_SNIM.svg.png", width=180)
    st.title("🛰️ Smart Operations")
    st.success("📴 Mode hors-ligne actif — Données sauvegardées localement")
    site_actuel = st.selectbox("Site", ["Guelb El Rhein", "M'Haoudat", "TO14", "Tazadit"])
    poste_actuel = st.radio("Shift", ["Matin", "Soir", "Nuit"])
    seuil_conf = st.slider("Confiance IA", 0.1, 1.0, 0.75, 0.05)
    
    if 'flotte' not in st.session_state:
        st.session_state.flotte = {"Panne": 0, "Crevaison": 0}

# Charger les données depuis le stockage local (mode hors-ligne)
if 'data_log' not in st.session_state:
    try:
        st.session_state.data_log = charger_donnees_locales()
    except Exception:
        st.session_state.data_log = []
if 'last_detections' not in st.session_state:
    st.session_state.last_detections = {} 
if 'frame_count' not in st.session_state:
    st.session_state.frame_count = 0

# --- 4. LOGIQUE DE TRAITEMENT ---
DETECTION_QUEUE = queue.Queue()
FRAME_SKIP = 4
_frame_count = [0]
_lock = threading.Lock()

def traiter_frame_webrtc(frame_bgr, site, poste):
    """Version pour callback WebRTC (thread-safe, pas de session_state)."""
    results = model.predict(frame_bgr, conf=seuil_conf, imgsz=640, verbose=False)
    donnees = []
    if not results:
        return [], frame_bgr
    for result in results:
        for box in result.boxes:
            label = model.names[int(box.cls[0])]
            if label in ["vide", "riche", "sterile", "mixte"]:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                crop = frame_bgr[y1:y2, x1:x2]
                if crop.size > 0:
                    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    ocr_res = reader.readtext(gray, allowlist='0123456789')
                    num = "N/A"
                    for res in ocr_res:
                        match = re.search(r'\d{3}', res[1])
                        if match: num = match.group(); break
                    if num != "N/A":
                        donnees.append({
                            "Heure": datetime.now().strftime("%H:%M:%S"),
                            "Camion": num, "Nature": label.upper(),
                            "Point": "Mobile", "Site": site, "Tonnage": 200, "Shift": poste
                        })
    plot_img = results[0].plot() if results else frame_bgr
    return donnees, plot_img

def video_frame_callback(frame):
    with _lock:
        _frame_count[0] += 1
        skip = _frame_count[0] % FRAME_SKIP != 0
    if skip:
        return frame
    img = frame.to_ndarray(format="bgr24")
    data, plot = traiter_frame_webrtc(img, site_actuel, poste_actuel)
    if data:
        for d in data:
            DETECTION_QUEUE.put_nowait(d)
    return av.VideoFrame.from_ndarray(plot, format="bgr24")

# Traiter les détections en attente (depuis le callback)
while not DETECTION_QUEUE.empty():
    try:
        d = DETECTION_QUEUE.get_nowait()
        maintenant = datetime.now()
        if d["Camion"] not in st.session_state.last_detections or \
           maintenant > st.session_state.last_detections[d["Camion"]] + timedelta(minutes=5):
            st.session_state.last_detections[d["Camion"]] = maintenant
            sauvegarder_detection(d)
            st.session_state.data_log.append(d)
    except queue.Empty:
        break

# --- 5. AFFICHAGE ---
st.title(f"📊 Supervision Mobile : {site_actuel}")
col_v, col_s = st.columns([2, 1])

with col_v:
    # Caméra arrière iPhone (facingMode: environment) + temps réel
    webrtc_streamer(
        key="cam",
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": {"facingMode": "environment"}, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )

# --- 6. ANALYSE + EXPORT ---
if st.session_state.data_log:
    df = pd.DataFrame(st.session_state.data_log)
    with col_s:
        st.subheader("📈 Statistiques")
        st.metric("Tonnage", f"{df['Tonnage'].sum()} T")
        st.metric("Cycles", len(df))
        st.metric("Données locales", f"{len(df)} enregistrements")
        # Export Excel (quand connexion disponible)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Détections')
        st.download_button(
            "📥 Exporter Excel",
            data=buffer.getvalue(),
            file_name=f"snim_detections_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    st.data_editor(df, use_container_width=True)