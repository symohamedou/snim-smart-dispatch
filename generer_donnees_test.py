"""
Génère des données de test pour tester le dashboard sans caméra.
Lancez ce script une fois, puis ouvrez le dashboard.
"""
import sqlite3
from datetime import datetime, timedelta
import random
import os

FICHIER_DB = os.path.join(os.path.dirname(__file__), "snim_detections.db")
SITES = ["Guelb El Rhein", "M'Haoudat", "TO14", "Tazadit"]
SHIFTS = ["Matin", "Soir", "Nuit"]
NATURES = ["VIDE", "RICHE", "STERILE", "MIXTE"]

def generer():
    conn = sqlite3.connect(FICHIER_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, heure TEXT, camion TEXT, nature TEXT, point TEXT,
            site TEXT, tonnage INTEGER, shift TEXT, sync INTEGER DEFAULT 0, created_at TEXT
        )
    """)
    
    # Générer ~50 détections sur les 7 derniers jours
    for i in range(50):
        jours = random.randint(0, 7)
        heures = random.randint(6, 22)
        minutes = random.randint(0, 59)
        dt = datetime.now() - timedelta(days=jours, hours=random.randint(0, 12))
        date_str = dt.strftime("%Y-%m-%d")
        heure_str = f"{heures:02d}:{minutes:02d}:00"
        camion = f"{random.randint(100, 999)}"
        nature = random.choice(NATURES)
        site = random.choice(SITES)
        shift = random.choice(SHIFTS)
        tonnage = 200
        created = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        conn.execute(
            """INSERT INTO detections (date, heure, camion, nature, point, site, tonnage, shift, sync, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)""",
            (date_str, heure_str, camion, nature, "Android_Internal", site, tonnage, shift, created)
        )
    
    conn.commit()
    conn.close()
    print(f"✅ 50 données de test créées dans {FICHIER_DB}")
    print("   Lancez le dashboard : streamlit run dashboard_snim.py")

if __name__ == "__main__":
    generer()
