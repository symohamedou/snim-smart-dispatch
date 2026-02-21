# Corrige l'URL du depot GitHub (symohamedou)
cd $PSScriptRoot
git remote remove origin 2>$null
git remote add origin https://github.com/symohamedou/snim-smart-dispatch.git
Write-Host "Remote configure : https://github.com/symohamedou/snim-smart-dispatch.git" -ForegroundColor Green
git remote -v
