@echo off
chcp 65001 > nul

echo.
echo === Installation de CyCalendar pour Windows ===
echo Demarrage de l'installation...

echo.
echo Installation des dependances Python...
echo Cette operation peut prendre plusieurs minutes selon votre connexion internet
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Creation des repertoires necessaires...
if not exist google mkdir google
if not exist generated mkdir generated

echo.
echo Installation terminee !