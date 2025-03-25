@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo.
echo === Installation de CyCalendar pour Windows ===
echo Demarrage de l'installation...

echo.
echo Installation des dependances Python...
echo Cette operation peut prendre plusieurs minutes selon votre connexion internet
python -m pip install --upgrade pip
python -m pip install colorama
python -m pip install pyreadline3
python -m pip install -r requirements.txt

echo.
echo Creation des repertoires necessaires...
if not exist google mkdir google
if not exist generated mkdir generated

echo.
echo Installation terminee !
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=1
echo Lancement du script principal...