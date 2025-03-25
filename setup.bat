@echo off
echo.
echo === Installation de CyCalendar pour Windows ===
echo Démarrage de l'installation...

echo.
echo Installation des dépendances Python...
echo Cette opération peut prendre plusieurs minutes selon votre connexion internet
pip install --upgrade pip
pip install colorama
pip install -r requirements.txt

echo.
echo Création des répertoires nécessaires...
if not exist google mkdir google
if not exist generated mkdir generated

echo.
echo Installation terminée !