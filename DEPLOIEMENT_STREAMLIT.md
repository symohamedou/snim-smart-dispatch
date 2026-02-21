# Déployer sur Streamlit Cloud

> Le fichier `requirements.txt` est configuré pour un déploiement rapide (streamlit + pandas uniquement).
> Pour l'app mobile en local : `pip install -r requirements-full.txt`

## Étapes

### 1. Aller sur Streamlit Cloud
Ouvrez : **https://share.streamlit.io**

### 2. Se connecter
Cliquez sur **"Sign up with GitHub"** et connectez-vous avec votre compte **symohamedou**.

### 3. Créer une nouvelle app
- Cliquez sur **"New app"**
- **Repository** : `symohamedou/snim-smart-dispatch`
- **Branch** : `main`
- **Main file path** : `dashboard_snim.py`
- Cliquez sur **"Deploy!"**

### 4. Attendre le déploiement
La première fois, cela peut prendre 2 à 5 minutes. Streamlit Cloud va :
- Cloner votre dépôt
- Installer les dépendances (streamlit, pandas)
- Lancer le tableau de bord

### 5. Votre app en ligne
Vous obtiendrez une URL du type :
```
https://snim-smart-dispatch-xxxxx.streamlit.app
```

Partagez cette URL pour accéder au tableau de bord depuis n'importe quel appareil (PC, iPhone, tablette).

### 6. Données de démo
Sur Streamlit Cloud, il n'y a pas de base de données au départ. Cliquez sur **"Charger des données de démo"** dans la barre latérale pour afficher des données d'exemple.

---

## Mise à jour
À chaque push sur GitHub, Streamlit Cloud redéploie automatiquement votre app.
