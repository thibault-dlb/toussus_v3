@echo off
echo ================================
echo 🔨 Création du nouvel exécutable avec icône...
echo ================================
pyinstaller --onefile --noconsole --add-data "ressources;ressources" --icon="ressources\final_icon.ico" app.py

echo ================================
echo 🚀 Nettoyage des fichiers inutiles...
echo ================================
del /f /q app.spec
rmdir /s /q build

echo ================================
echo 📂 Déplacement de l'exécutable...
echo ================================
move /y "dist\app.exe" "app.exe"

echo ================================
echo 🗑 Suppression du dossier dist...
echo ================================
rmdir /s /q dist

echo ================================
echo ✅ Tout est propre et terminé !
echo ================================
timeout /t 1 >nul
exit
