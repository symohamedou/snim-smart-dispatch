# Envoyer le projet SNIM Smart Dispatch sur GitHub
# 1. Creer d'abord le depot sur https://github.com/new (nom: snim-smart-dispatch)
# 2. Executer ce script

$url = Read-Host "Collez l'URL de votre depot GitHub (ex: https://github.com/symoh/snim-smart-dispatch.git)"

if (-not $url) {
    Write-Host "URL requise. Exemple: https://github.com/VOTRE_USER/snim-smart-dispatch.git" -ForegroundColor Red
    exit
}

Set-Location $PSScriptRoot

# Supprimer l'ancien remote si existe
git remote remove origin 2>$null

# Ajouter et pousser
git remote add origin $url
git branch -M main
git push -u origin main

Write-Host "`nProjet envoye sur GitHub !" -ForegroundColor Green
Write-Host "Allez sur $url pour voir votre code." -ForegroundColor Cyan
