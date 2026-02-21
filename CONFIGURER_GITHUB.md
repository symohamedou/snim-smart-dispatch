# Configuration GitHub — À faire une seule fois

## 1. Configurer Git (votre identité)

Ouvrez PowerShell et exécutez (remplacez par vos vraies infos) :

```powershell
git config --global user.name "VotreNom"
git config --global user.email "votre@email.com"
```

Exemple :
```powershell
git config --global user.name "symoh"
git config --global user.email "symoh@gmail.com"
```

## 2. Créer le dépôt sur GitHub.com

1. Allez sur **https://github.com** et connectez-vous
2. Cliquez sur **+** → **New repository**
3. Nom : `snim-smart-dispatch`
4. **Ne cochez rien** (pas de README)
5. Cliquez **Create repository**

## 3. Lier et envoyer votre projet

Copiez l’URL de votre dépôt (ex: `https://github.com/VOTRE_USER/snim-smart-dispatch.git`), puis :

```powershell
cd "c:\Users\symoh\Desktop\app sy"
git remote add origin https://github.com/VOTRE_USER/snim-smart-dispatch.git
git branch -M main
git push -u origin main
```

Remplacez `VOTRE_USER` par votre nom d’utilisateur GitHub.

---

## Cloner le projet sur un autre PC

Une fois le projet sur GitHub, pour le recuperer ailleurs :

```powershell
git clone https://github.com/VOTRE_USER/snim-smart-dispatch.git
cd snim-smart-dispatch
``` 

Pensez a copier best_float32.tflite dans le dossier (il n'est pas sur GitHub).
