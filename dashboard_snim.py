"""
SNIM Smart Dispatch - Tableau de bord central
Visualise les données de tous les sites en temps réel.
"""
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import os

# --- Configuration ---
# Même base que l'app mobile (à côté du script ou dans le dossier courant)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FICHIER_DB = os.path.join(SCRIPT_DIR, "snim_detections.db")

def charger_toutes_donnees():
    """Charge toutes les détections depuis la base locale."""
    if not os.path.exists(FICHIER_DB):
        return pd.DataFrame()
    conn = sqlite3.connect(FICHIER_DB)
    df = pd.read_sql_query(
        """SELECT id, date, heure, camion, nature, point, site, tonnage, shift, created_at 
           FROM detections ORDER BY created_at DESC""",
        conn
    )
    conn.close()
    return df

def generer_donnees_demo():
    """Génère des données de démo pour tester le dashboard (ex: déploiement Streamlit Cloud)."""
    import random
    conn = sqlite3.connect(FICHIER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, heure TEXT, camion TEXT, nature TEXT, point TEXT,
            site TEXT, tonnage INTEGER, shift TEXT, sync INTEGER DEFAULT 0, created_at TEXT
        )
    """)
    sites = ["Guelb El Rhein", "M'Haoudat", "TO14", "Tazadit"]
    shifts = ["Matin", "Soir", "Nuit"]
    natures = ["VIDE", "RICHE", "STERILE", "MIXTE"]
    for i in range(50):
        jours = random.randint(0, 7)
        dt = datetime.now() - timedelta(days=jours, hours=random.randint(0, 12))
        conn.execute(
            """INSERT INTO detections (date, heure, camion, nature, point, site, tonnage, shift, sync, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)""",
            (dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S"), str(random.randint(100, 999)),
             random.choice(natures), "Demo", random.choice(sites), 200, random.choice(shifts),
             dt.strftime("%Y-%m-%d %H:%M:%S"))
    conn.commit()
    conn.close()

# --- Page config ---
st.set_page_config(
    page_title="SNIM Dashboard | Supervision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar : Logo + Filtres ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Logo_SNIM.svg/1200px-Logo_SNIM.svg.png", width=180)
    st.title("📊 Tableau de bord")
    st.caption("Supervision multi-sites")
    st.divider()
    
    # Filtres
    st.subheader("🔍 Filtres")
    df_raw = charger_toutes_donnees()
    
    if df_raw.empty:
        st.warning("Aucune donnée pour le moment.")
        if st.button("📥 Charger des données de démo"):
            generer_donnees_demo()
            st.rerun()
        st.info("Lancez l'app mobile sur le terrain pour collecter des détections réelles.")
        st.stop()
    
    # Convertir date pour filtrage
    df_raw["date"] = pd.to_datetime(df_raw["date"], errors="coerce")
    
    sites = ["Tous"] + sorted(df_raw["site"].dropna().unique().tolist())
    shifts = ["Tous"] + sorted(df_raw["shift"].dropna().unique().tolist())
    
    filtre_site = st.selectbox("Site", sites)
    filtre_shift = st.selectbox("Shift", shifts)
    
    date_min = df_raw["date"].min()
    date_max = df_raw["date"].max()
    if pd.notna(date_min) and pd.notna(date_max):
        try:
            filtre_date = st.date_input(
                "Période",
                value=(date_min.date(), date_max.date()),
                min_value=date_min.date(),
                max_value=date_max.date()
            )
            if isinstance(filtre_date, tuple) and len(filtre_date) == 2:
                date_debut, date_fin = filtre_date
            else:
                date_debut = date_fin = filtre_date
        except Exception:
            date_debut = date_fin = None
    else:
        date_debut = date_fin = None
    
    st.divider()
    st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

# --- Application des filtres ---
df = df_raw.copy()
if date_debut:
    df = df[df["date"].dt.date >= date_debut]
if date_fin:
    df = df[df["date"].dt.date <= date_fin]
if filtre_site != "Tous":
    df = df[df["site"] == filtre_site]
if filtre_shift != "Tous":
    df = df[df["shift"] == filtre_shift]

# --- En-tête ---
st.title("🛰️ SNIM Smart Dispatch — Supervision centrale")
st.markdown("Vue d'ensemble des opérations sur tous les sites miniers.")

# --- KPIs principaux ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    tonnage_total = df["tonnage"].sum()
    st.metric("📦 Tonnage total", f"{tonnage_total:,.0f} T", help="Tonnage cumulé sur la période")

with col2:
    cycles = len(df)
    st.metric("🔄 Cycles", f"{cycles:,}", help="Nombre de passages de camions détectés")

with col3:
    sites_actifs = df["site"].nunique()
    st.metric("🏭 Sites actifs", sites_actifs, help="Nombre de sites avec des détections")

with col4:
    camions_uniques = df["camion"].nunique()
    st.metric("🚛 Camions", camions_uniques, help="Nombre de camions différents")

st.divider()

# --- Graphiques ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📊 Tonnage par site")
    if not df.empty and "site" in df.columns:
        tonnage_site = df.groupby("site")["tonnage"].sum().sort_values(ascending=True)
        st.bar_chart(tonnage_site, height=350)
    else:
        st.info("Pas de données à afficher")

with col_g2:
    st.subheader("⏰ Tonnage par shift")
    if not df.empty and "shift" in df.columns:
        tonnage_shift = df.groupby("shift")["tonnage"].sum()
        # Ordre logique : Matin, Soir, Nuit
        ordre = ["Matin", "Soir", "Nuit"]
        tonnage_shift = tonnage_shift.reindex([s for s in ordre if s in tonnage_shift.index]).fillna(0)
        st.bar_chart(tonnage_shift, height=350)
    else:
        st.info("Pas de données à afficher")

# --- Tonnage par jour (si on a des dates) ---
if not df.empty and "date" in df.columns and df["date"].notna().any():
    st.subheader("📈 Évolution du tonnage par jour")
    tonnage_jour = df.groupby(df["date"].dt.date)["tonnage"].sum()
    st.line_chart(tonnage_jour, height=300)

st.divider()

# --- Nature des chargements ---
st.subheader("📋 Répartition par nature (vide / riche / stérile / mixte)")
if not df.empty and "nature" in df.columns:
    nature_counts = df["nature"].value_counts()
    df_nature = nature_counts.reset_index()
    df_nature.columns = ["Nature", "Nombre"]
    col_n1, col_n2 = st.columns([1, 2])
    with col_n1:
        st.dataframe(
            df_nature,
            use_container_width=True,
            hide_index=True
        )
    with col_n2:
        st.bar_chart(nature_counts, height=250)
else:
    st.info("Pas de données à afficher")

st.divider()

# --- Tableau des détections ---
st.subheader("📋 Détails des détections")

# Colonnes affichées
colonnes_affichage = ["date", "heure", "camion", "nature", "site", "shift", "tonnage", "point"]
colonnes_dispo = [c for c in colonnes_affichage if c in df.columns]
df_affichage = df[colonnes_dispo].rename(columns={
    "date": "Date", "heure": "Heure", "camion": "Camion", "nature": "Nature",
    "site": "Site", "shift": "Shift", "tonnage": "Tonnage", "point": "Point"
})

if not df_affichage.empty:
    df_affichage["Date"] = pd.to_datetime(df_affichage["Date"]).dt.strftime("%Y-%m-%d")
    st.dataframe(df_affichage, use_container_width=True, hide_index=True)
    
    # Export
    st.download_button(
        "📥 Exporter en CSV",
        data=pd.DataFrame(df_affichage).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"snim_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
else:
    st.info("Aucune détection pour les filtres sélectionnés.")
