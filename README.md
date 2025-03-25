# CyCalendar

CyCalendar est un outil qui synchronise automatiquement votre emploi du temps CY Tech avec Google Calendar.

## Fonctionnalités

- Authentification automatique avec le système CY Tech
- Récupération de votre emploi du temps
- Conversion au format ICS
- Synchronisation avec Google Calendar
- Formatage intelligent des événements :
  - Suppression des doublons de préfixes (ex: "CM CM" devient "CM")
  - Correction des caractères spéciaux
  - Coloration automatique : bleu pour les CM, rouge doux pour les TD
- Stockage des fichiers ICS générés dans le dossier `generated/`

## Configuration requise

- Python 3.x
- Les dépendances listées dans `requirements.txt`
- Un compte Google avec accès à l'API Google Calendar
- Des identifiants OAuth2 Google (fichier `client_secret_*.json`)

  Des erreurs sont susceptibles d'arriver et pourtant de ne pas gêner l'execution du programme. Vérifiez par vous même le fonctionnement ou non du programme.

### Prérequis

- **Windows** : Python 3.8+ et Chrome ou Microsoft Edge
- **Linux** : Python 3.8+ et Chrome/Chromium

### Généralités

**Si vous comptez aller jusqu'à l'étape 3 (automatisation + mises à jours automatiques), alors ne clonez pas le repo mais forkez le plutôt. Cela vous permettra d'avoir une copie de mon repo dans vos repo, vous en aurez besoin pour l'ajout du scheduler.**

![1741238356019](image/README/1741238356019.png)
(Bouton fork juste au dessus du bouton code en vert à droite)

### Installation assistée

En suivant les étapes du setup.py que j'ai créé vous pouvez mettre en place l'installation de ce service de manière plus ou moins automatique. Certaines actions seront à faire par vos soins, j'ai automatisé ça du mieux que j'ai pu. (Le setup.py vous laisse choisir le mode désiré, vous pouvez faire une installation du mode manuel avec). Les étapes du setup.py et de l'installation diffèrent sur certains points puisque j'automatise certain aspects (pas besoin de vous embêter avec les explications dans ce cas).

### Installation manuelle

Cette catégorie n'est pas utile si vous avez choisi l'utilisation du setup.py puisque celui ci vous guide déjà dans la configuration du service. Elle peut servir à vérifier que votre installation s'est faite correctement à la limite mais normalement vous n'en aurez pas besoin si vous êtes passés par le setup.py.

#### 1. Mode manuel

   Cette utilisation est de loin la plus simple. Voici ses étapes :

##### Pour Linux :

1. Installer les dépendances ubuntu et python en éxecutant la commande suivante : ``./setup.bash # à la racine du projet``

##### Pour Windows :

1. Installer les dépendances python en exécutant le script ``setup.bat`` (double-cliquez dessus ou exécutez-le en ligne de commande)

##### Pour tous les systèmes :

2. Créer un fichier nommé '.env' à la racine du projet contenant ces informations :
3. Clonez ce dépôt
4. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```
5. Placez votre fichier d'identifiants OAuth2 Google (`client_secret_*.json`) dans le dossier `google/`

## Utilisation

1. Exécutez le script :
   ```bash
   python cyCalendar.py
   ```
2. Suivez les étapes d'authentification CY Tech
3. Le programme créera automatiquement un calendrier "Cours CY" dans votre Google Calendar et y importera vos cours

## Problèmes possibles

Parfois le programme peut s'arrêter en pleine execution après avoir généré un token. Avant de paniquer et d'abandonner, essayez de relancer le programme tout simplement (surtout durant le setup).	

Le seul token pouvant expirer est le GOOGLE_TOKEN que nous avons générés ensembles. Si celui ci expire vous aurez cette erreur sur github actions :

![1742893329665](image/README/1742893329665.png)

Puisque le programme attend que vous mettiez le token à jour. Cela ne sert à rien de cliquer sur le lien sur github actions, ça fonctionne avec du localhost. La solution est de lancer cyCalendar.py en local ``python3 cyCalendar.py``. Une fenêtre google s'ouvrira, choisissez votre compte puis cliquez sur continuer 2 fois. Ceci re-génèrera votre token et le mettra à jour automatiquement sur github.

## Structure des dossiers

- `generated/` : Stockage des fichiers ICS générés
- `google/` : Stockage des fichiers d'authentification Google (credentials et token)
- `src/` : Code source du projet

## Notes

- Le calendrier est automatiquement recréé à chaque synchronisation pour éviter les doublons
- Les CM sont colorés en bleu (#4a4aff)
- Les TD sont colorés en rouge clair (#FF6666)
- Le calendrier lui-même est coloré en bleu (#2660aa)
