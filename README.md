# SNIM Smart Dispatch

Application de supervision pour dispatchers miniers — détection de camions par IA, mode hors-ligne, tableau de bord central.

## Démarrage rapide

```bash
pip install -r requirements.txt
streamlit run dashboard_snim.py
```

## Fichiers

- `app_snim_mobile.py` — App terrain (caméra + détection IA)
- `dashboard_snim.py` — Tableau de bord de supervision
- `best_float32.tflite` — Modèle YOLO (à placer dans ce dossier)
