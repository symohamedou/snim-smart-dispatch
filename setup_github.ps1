# Script de configuration GitHub pour SNIM Smart Dispatch
# Executez ce script dans PowerShell

Write-Host "=== Configuration Git pour SNIM Smart Dispatch ===" -ForegroundColor Cyan
Write-Host ""

# Demander le nom et l'email
$nom = Read-Host "Entrez votre nom (pour Git)"
$email = Read-Host "Entrez votre email (pour Git)"

if ($nom -and $email) {
    git config --global user.name $nom
    git config --global user.email $email
    Write-Host "Identite Git configuree." -ForegroundColor Green
} else {
    Write-Host "Annule. Relancez le script." -ForegroundColor Yellow
    exit
}

# Aller dans le dossier du projet
Set-Location $PSScriptRoot

# Commit si pas encore fait
$status = git status --porcelain
if ($status) {
    git add .
    git commit -m "Premiere version - SNIM Smart Dispatch"
    Write-Host "Commit cree." -ForegroundColor Green
}

# Demander l'URL du depot GitHub
Write-Host ""
Write-Host "Creer un depot sur https://github.com/new (nom: snim-smart-dispatch)" -ForegroundColor Yellow
$url = Read-Host "Collez l'URL de votre depot (ex: https://github.com/user/snim-smart-dispatch.git)"

if ($url) {
    git remote remove origin 2>$null
    git remote add origin $url
    git branch -M main
    git push -u origin main
    Write-Host "Projet envoye sur GitHub !" -ForegroundColor Green
} else {
    Write-Host "URL non fournie. Executez manuellement:" -ForegroundColor Yellow
    Write-Host "  git remote add origin VOTRE_URL"
    Write-Host "  git push -u origin main"
}
