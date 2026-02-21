# SNIM Smart Dispatch — Lancer les applications

## 1. App Mobile (terrain, détection camions)
```bash
cd "c:\Users\symoh\Desktop\app sy"
streamlit run app_snim_mobile.py
```
→ Utilise la caméra, détecte les camions, sauvegarde en local.

## 2. Tableau de bord (supervision)
```bash
cd "c:\Users\symoh\Desktop\app sy"
streamlit run dashboard_snim.py
```
→ Affiche les statistiques, graphiques, filtres par site/shift.

**Astuce :** Les deux apps lisent la même base `snim_detections.db`. Vous pouvez lancer le dashboard sur un PC pour voir les données collectées par l'app mobile.
