import sys
import platform
import subprocess
import getpass
import base64
import time
import shutil
import os
import webbrowser
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import urllib.request

class CyCalendarInstaller:
    def __init__(self):
        self.os_type = platform.system()
        self.platform = self.os_type.lower()  # Conversion en minuscule pour faciliter les comparaisons
        self.project_root = Path.cwd()
        self.env_path = self.project_root / '.env'
        self.google_dir = self.project_root / 'google'
        self.credentials_path = None
        self.mode = None
        self.temp_dir = tempfile.gettempdir()  # Répertoire temporaire pour les téléchargements
        
    def write_log(self, step):
        # Écriture du log
        try:
            with open(".setup.log", "w") as f:
                f.write(str(step))
        except Exception as e:
            print(f"⚠️ Impossible d'écrire dans le fichier .setup.log: {e}")

    def display_welcome(self):
        print("""
=================================================
    CyCalendar - Assistant d'Installation
=================================================
Bienvenue dans l'assistant d'installation de CyCalendar!
Ce script va vous guider à travers les étapes d'installation.
""")

    def select_installation_mode(self):
        print("\nVeuillez choisir un mode d'installation:")
        print("1. Mode Manuel (génération ICS simple)")
        print("2. Mode Automatique (synchronisation avec Google Calendar)")
        print("3. Mode Automatique et périodique (mises à jour périodiques avec GitHub Actions)")
        
        while True:
            choice = input("\nVotre choix (1/2/3): ")
            if choice in ["1", "2", "3"]:
                self.mode = int(choice)
                return
            print("Choix invalide. Veuillez réessayer.")

    def install_dependencies(self):
        print("\n[1/5] Installation des dépendances...")
        
        if self.os_type == "Linux":
            print("Installation des dépendances Linux...")
            try:
                subprocess.run(["bash", "setup.bash"], check=True)
                print("✅ Dépendances Linux installées avec succès.")
                self.write_log(1)
            except subprocess.CalledProcessError:
                print("⚠️ Erreur lors de l'installation des dépendances Linux.")
                print("Tentative d'installation manuelle des dépendances Python...")
                self.install_python_dependencies()
        
        elif self.os_type == "Windows":
            print("Installation des dépendances Windows...")
            try:
                subprocess.run(["setup.bat"], shell=True, check=True)
                print("✅ Dépendances Windows installées avec succès.")
                self.write_log(1)
            except subprocess.CalledProcessError:
                print("⚠️ Erreur lors de l'installation des dépendances Windows.")
                print("Tentative d'installation manuelle des dépendances Python...")
                self.install_python_dependencies()
        
        else:
            print(f"Système d'exploitation non reconnu: {self.os_type}")
            print("Tentative d'installation des dépendances Python uniquement...")
            self.install_python_dependencies()

    def install_python_dependencies(self):
        print("Installation des dépendances Python...")
        try:
            requirements_path = self.project_root / "requirements.txt"
            if not requirements_path.exists():
                with open(requirements_path, "w") as f:
                    f.write("selenium\nrequests\npython-dotenv\ngoogle-api-python-client\ngoogle-auth-httplib2\ngoogle-auth-oauthlib\npytz\nxvfbwrapper\n")
            
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dépendances Python installées avec succès.")
        except subprocess.CalledProcessError:
            print("❌ Échec de l'installation des dépendances Python.")
            sys.exit(1)

    def setup_environment(self):
        print("\n[2/5] Configuration du fichier .env...")
        
        # Demander les informations d'identification CY Tech avec une meilleure gestion sous Windows
        cy_username = ""
        while not cy_username:
            cy_username = input("Entrez votre identifiant CY Tech (e-1erelettreprenom+nom): ")
            if not cy_username:
                print("Identifiant vide, veuillez réessayer.")
        
        # Pour Windows, utiliser getpass.win_getpass si disponible ou fallback sur input si nécessaire
        if self.os_type == "Windows":
            try:
                cy_password = getpass.getpass("Entrez votre mot de passe CY Tech: ")
            except Exception:
                print("La saisie sécurisée n'est pas disponible, veuillez entrer votre mot de passe:")
                cy_password = input("Mot de passe (attention: visible à l'écran): ")
        else:
            cy_password = getpass.getpass("Entrez votre mot de passe CY Tech: ")
        
        # Créer le fichier .env
        with open(self.env_path, 'w') as env_file:
            env_file.write(f"CY_USERNAME={cy_username}\n")
            env_file.write(f"CY_PASSWORD={cy_password}\n")
        
        print("✅ Fichier .env créé avec succès.")
        self.write_log(2)

    def setup_google_api(self):
        if self.mode == 1:
            print("\n[3/5] Mode manuel sélectionné - Étape Google API ignorée.")
            return True
            
        print("\n[3/5] Configuration de l'API Google Calendar...")
        
        # Vérifier si un fichier de credentials existe déjà
        credentials_files = list(self.google_dir.glob('client_secret_*.apps.googleusercontent.com.json'))

        if credentials_files:
            print(f"Fichier de credentials trouvé : {credentials_files[0]}")
            choice = input("Voulez-vous utiliser ce fichier ? (y/n): ")
            if choice.lower() == 'y':
                self.credentials_path = credentials_files[0]
                self.write_log(3)
                return True
        
        print("\nConfiguration automatique avec redirections...")
        print("Plusieurs pages vont s'ouvrir, suivez les instructions sur le terminal afin de compléter la configuration google.")

        print("\nOuverture de https://console.cloud.google.com/ ...")
        print("Sur cette page il vous suffit de créer un projet avec le nom que vous voulez. (Connectez vous au compte google que vous souhaitez utiliser)")
        time.sleep(2)        
        webbrowser.open("https://console.cloud.google.com/")
        
        input("\nAppuyez sur Entrée une fois que le projet est créé et a fini de charger...")

        print("\nOuverture de https://console.cloud.google.com/marketplace/product/google/calendar-json.googleapis.com ...")
        print("Sur cette page, cliquez sur le bouton 'Activer' pour activer l'API Google Calendar.")
        time.sleep(2)
        webbrowser.open("https://console.cloud.google.com/marketplace/product/google/calendar-json.googleapis.com")

        input("\nAppuyez sur Entrée une fois que l'API Google Calendar est activée et a fini de charger...")

        print("\nOuverture de https://console.cloud.google.com/auth/overview ...")
        print("Sur cette page, cliquez sur le bouton premiers pas puis complétez comme suit :")
        print("-> Nom d'application : cycalendar et mettez votre adresse mail en adresse d'assistance")
        print("-> Cible : externe")
        print("-> Coordonées : votre adresse mail")
        print("-> Acceptez puis créer")
        time.sleep(2)
        webbrowser.open("https://console.cloud.google.com/auth/overview")

        input("\nAppuyez sur Entrée une fois que la page Présentation d'OAuth a fini de charger...")

        print("\nOuverture de https://console.cloud.google.com/auth/audience ...")
        print("Sur cette page, sous utilisateurs tests cliquez sur ADD USERS, entrez votre adresse mail et cliquez sur Enregistrer.")
        time.sleep(2)
        webbrowser.open("https://console.cloud.google.com/auth/audience")

        input("\nAppuyez sur Entrée une fois que vous avez ajouté votre adresse mail...")

        print("\nOuverture de https://console.cloud.google.com/auth/clients/create ...")
        print("Sur cette page, choisissez application de bureau pour le type et mettez le nom que vous souhaitez puis cliquez sur créer")
        time.sleep(2)
        webbrowser.open("https://console.cloud.google.com/auth/clients/create")

        input("\nAppuyez sur Entrée une fois que le client OAuth 2.0 a été créé et a fini de charger...")

        print("\nIl ne vous reste plus qu'à cliquer sur l'icone de téléchargement tout à droite de votre clé créée, puis sur télécharger au format json.")       
        
        input("\nAppuyez sur Entrée une fois que le fichier de credentials a été téléchargé...")

        # Try to find the credentials file in common Downloads locations
        possible_paths = [
            Path.home() / "Downloads",
            Path("/Downloads"),
            Path("/data/Downloads"),
            Path.home() / "Téléchargements",
            Path("/Téléchargements"),
            Path("/data/Téléchargements")
        ]
        
        credentials_files = []
        for path in possible_paths:
            if path.exists():
                credentials_files.extend(list(path.glob('client_secret_*.apps.googleusercontent.com.json')))

        if credentials_files:
            latest_file = max(credentials_files, key=lambda x: x.stat().st_mtime)
            print(f"\nFichier de credentials trouvé dans vos téléchargements: {latest_file}")
            choice = input("Est ce le bon ? (y/n): ")
            if choice.lower() == 'y':
                try:
                    # Try to use project directory first
                    self.google_dir.mkdir(exist_ok=True)
                    shutil.copy2(latest_file, self.google_dir)
                    self.credentials_path = self.google_dir / latest_file.name
                except PermissionError:
                    print(f"\n❌ Permission refusée pour copier le fichier de credentials de {latest_file} vers {self.google_dir}, veuillez le faire manuellement sans changer le nom ni le contenu.")
                    input("\nAppuyez sur Entrée une fois que vous avez copié le fichier...")
                    self.credentials_path = self.google_dir / latest_file

        # If not found automatically or user declined, ask for manual path
        if not self.credentials_path:
            while True:
                manual_path = Path(input("Entrez le chemin du fichier de credentials téléchargé: "))
                if "client_secret_" in manual_path.name and ".apps.googleusercontent.com.json" in manual_path.name:
                    self.google_dir.mkdir(exist_ok=True) 
                    shutil.copy(manual_path, self.google_dir)
                    self.credentials_path = self.google_dir / manual_path.name
                    break
                else:
                    print("Fichier de credentials invalide. Veuillez réessayer.")
                    
        self.write_log(3)
        
        return True

    def download_file(self, url, destination):
        """Télécharge un fichier depuis une URL vers une destination spécifiée."""
        try:
            print(f"Téléchargement de {url}...")
            
            # Créer un affichage de progression simple
            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(int(downloaded * 100 / total_size), 100)
                    progress_bar = '█' * int(percent / 2)
                    print(f"\r  {progress_bar.ljust(50)} {downloaded / 1024 / 1024:.1f} MB / {total_size / 1024 / 1024:.1f} MB", end='', flush=True)
            
            # Télécharger le fichier avec affichage de la progression
            urllib.request.urlretrieve(url, destination, reporthook=report_progress)
            print()  # Nouvelle ligne après la barre de progression
            
            return True
        except Exception as e:
            print(f"\n❌ Erreur lors du téléchargement du fichier: {e}")
            return False

    def install_gh_cli(self):
        """Détecte GitHub CLI déjà installé ou propose une installation manuelle."""
        try:
            # Essayer d'exécuter gh pour voir s'il est déjà installé
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
            print("GitHub CLI est déjà installé.")
            return "gh"
        except (subprocess.CalledProcessError, FileNotFoundError):
            if self.platform == "windows":
                print("\n⚠️ GitHub CLI n'est pas détecté sur votre système.")
                
                # Recherche gh.exe dans les emplacements courants
                possible_locations = [
                    os.path.expandvars("%ProgramFiles%\\GitHub CLI"),
                    os.path.expandvars("%ProgramFiles(x86)%\\GitHub CLI"),
                    os.path.expandvars("%LOCALAPPDATA%\\Programs\\GitHub CLI"),
                    # Ajout d'emplacements courants d'installation de GitHub CLI
                    "C:\\Program Files\\GitHub CLI",
                    "C:\\Program Files (x86)\\GitHub CLI"
                ]
                
                for location in possible_locations:
                    if os.path.exists(location):
                        print(f"Recherche de GitHub CLI dans {location}...")
                        gh_exe = os.path.join(location, "gh.exe")
                        if os.path.exists(gh_exe):
                            print(f"✅ GitHub CLI trouvé à {gh_exe}")
                            # Ajouter le chemin à PATH pour cette session
                            os.environ["PATH"] = location + os.pathsep + os.environ["PATH"]
                            return gh_exe
                
                # Aucune installation trouvée, demander à l'utilisateur
                print("Veuillez l'installer manuellement en suivant ces étapes:")
                print("1. Ouvrez un navigateur et visitez: https://cli.github.com/")
                print("2. Téléchargez et installez GitHub CLI")
                print("3. Après l'installation, redémarrez ce script ou votre terminal\n")
                print("\nVoulez-vous continuer sans GitHub CLI? (y/n)")
                choice = input("Si vous continuez, vous devrez configurer GitHub Actions manuellement: ")
                if choice.lower() == 'y':
                    return None
                else:
                    sys.exit(1)
            elif self.platform == "linux":
                # Seulement montrer les instructions pour Linux
                print("\n⚠️ GitHub CLI n'est pas détecté sur votre système Linux.")
                print("Pour l'installer, exécutez les commandes suivantes dans un terminal:")
                print("sudo apt update && sudo apt install gh -y")
                
                choice = input("Voulez-vous continuer sans GitHub CLI? (y/n): ")
                if choice.lower() == 'y':
                    return None
                else:
                    sys.exit(1)
            elif self.platform == "darwin":  # macOS
                print("\n⚠️ GitHub CLI n'est pas détecté sur votre Mac.")
                print("Pour l'installer, exécutez la commande suivante dans un terminal:")
                print("brew install gh")
                
                choice = input("Voulez-vous continuer sans GitHub CLI? (y/n): ")
                if choice.lower() == 'y':
                    return None
                else:
                    sys.exit(1)
            else:
                print(f"❌ Système d'exploitation non pris en charge: {self.platform}")
                return None

    def github_login(self):
        try:
            # Vérifier la connexion
            result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
            
            # Si déjà connecté, récupérer le token
            if "Logged in to" in result.stdout:
                print("✅ Déjà connecté à GitHub!")
                return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()
            
            print("\nOuverture de la page de création de token...")
            print("Créez le token en suivant ces instructions :")
            print("- Nom : Votre choix")
            print("- Repository : Cochez ")
            print("- Expiration : Jamais ou selon vos préférences (l'app ne marchera plus après l'expiration)")
            print("- Permissions : sous Repository cochez (en read/write) Actions, Contents, Pull Requests, Secrets et Workflows")
            print("Puis cliquez sur Generate token et copiez le token généré.")
            time.sleep(3)
            webbrowser.open("https://github.com/settings/personal-access-tokens/new")
            
            token = input("\nCollez votre Personal Access Token : ")
            
            # Connexion avec le token
            subprocess.run(["gh", "auth", "login", "--with-token"], 
                           input=token.encode(), 
                           check=True)
            
            return token
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur de connexion : {e}")
            sys.exit(1)

    def select_repo(self):
        while True:
            try:
                # Vérifier si un fork existe déjà
                repos = subprocess.run(["gh", "repo", "list", "--limit", "100"], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True).stdout.strip().split('\n')
                
                # Vérifier si CyCalendar est déjà forké
                cy_repos = [repo for repo in repos if "CyCalendar" in repo]
                
                print("\nVos dépôts GitHub :")
                print(f"0. Je n'ai pas encore fork le repo CyCalendar et donc je ne le vois pas dans les options")
                
                if cy_repos:
                    print("Dépôts CyCalendar existants :")
                    for i, repo in enumerate(cy_repos, 1):
                        print(f"{i}. {repo} [RECOMMANDÉ]")
                    
                print("\nAutres dépôts :")
                for i, repo in enumerate(repos, len(cy_repos) + 1):
                    if repo not in cy_repos:
                        print(f"{i}. {repo}")
                
                choice = input("\nSélectionnez votre fork de CyCalendar (ou 0 pour en créer un nouveau) : ")
                
                if choice == "0":
                    print("\nCréation d'un fork du dépôt CyCalendar...")
                    fork_result = subprocess.run(
                        ["gh", "repo", "fork", "NayJi7/CyCalendar", "--clone=false"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    print("✅ Fork de CyCalendar effectué avec succès!")
                    
                    # Extraire le nom du nouveau fork à partir des résultats
                    for line in fork_result.stdout.splitlines():
                        if "Created fork" in line:
                            parts = line.split()
                            for part in parts:
                                if "/" in part and "CyCalendar" in part:
                                    return part.strip()
                    
                    # Si on ne peut pas extraire le nom automatiquement, récupérer la liste mise à jour
                    print("Récupération de la liste mise à jour des dépôts...")
                    updated_repos = subprocess.run(
                        ["gh", "repo", "list", "--limit", "100"],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout.strip().split('\n')
                    
                    for repo in updated_repos:
                        if "CyCalendar" in repo:
                            return repo.split()[0]  # Premier élément (nom du repo)
                    
                    # Vérification alternative avec le nom d'utilisateur
                    username_result = subprocess.run(
                        ["gh", "api", "user", "-q", ".login"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    username = username_result.stdout.strip()
                    
                    if username:
                        print(f"Fork créé sous: {username}/CyCalendar")
                        return f"{username}/CyCalendar"
                        
                    raise ValueError("Impossible de déterminer le nom du dépôt forké")
                
                # Sélectionner un repo existant
                choice = int(choice)
                if 1 <= choice <= len(cy_repos):
                    # Sélection d'un dépôt CyCalendar
                    selected_repo = cy_repos[choice - 1].split()[0]
                else:
                    # Sélection d'un autre dépôt
                    index = choice - len(cy_repos) - 1
                    if 0 <= index < len(repos):
                        selected_repo = repos[index].split()[0]
                    else:
                        print("❌ Choix invalide.")
                        continue
                
                print(f"Dépôt sélectionné: {selected_repo}")
                return selected_repo
            
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de l'accès aux dépôts: {e}")
                print(f"Détails: {e.stderr}")
                
                # Proposer de créer manuellement un fork
                print("\nImpossible de lister ou créer un fork automatiquement.")
                print("Veuillez vous rendre sur https://github.com/NayJi7/CyCalendar et cliquer sur 'Fork'.")
                
                manual_fork = input("\nAvez-vous créé manuellement un fork? (y/n): ")
                if manual_fork.lower() == 'y':
                    username = input("Entrez votre nom d'utilisateur GitHub: ")
                    return f"{username}/CyCalendar"
                else:
                    sys.exit(1)

    def setup_github_actions(self):
        """Configure GitHub Actions."""
        if self.mode != 3:
            print("\n[4/5] Mode GitHub Actions non sélectionné - Étape ignorée.")
            return
            
        print("\n[4/5] Configuration de GitHub Actions...")
        
        # Recherche de GitHub CLI
        gh_path = self.install_gh_cli()
        
        # Si gh_path est None, proposer une configuration manuelle
        if gh_path is None:
            print("\n⚠️ GitHub CLI n'est pas disponible. Configuration manuelle de GitHub Actions requise.")
            print("Instructions de configuration manuelle:")
            print("1. Ouvrez votre navigateur et allez sur https://github.com/votre-nom/CyCalendar")
            print("2. Allez dans 'Settings' > 'Secrets and variables' > 'Actions'")
            print("3. Ajoutez les secrets suivants:")
            print("   - CY_USERNAME: Votre identifiant CY Tech")
            print("   - CY_PASSWORD: Votre mot de passe CY Tech")
            print("   - GOOGLE_CREDENTIALS: Le contenu du fichier client_secret_*.json")
            print("   - GOOGLE_TOKEN: Le contenu encodé en base64 du fichier token.pickle")
            print("   - WORKFLOW_PAT: Un token d'accès personnel GitHub avec les permissions nécessaires")
            
            # Autres instructions pour la configuration manuelle...
            self.print_secret_values_for_manual_setup()
            return
        
        # Utiliser le chemin absolu vers gh si disponible
        gh_cmd = gh_path if os.path.isfile(gh_path) else "gh"
        
        # Connexion à GitHub
        gh_token = self.github_login()
        
        # Ajouter le token au fichier .env pour une utilisation future
        print("Sauvegarde du token GitHub dans le fichier .env...")
        try:
            with open(self.env_path, 'a') as env_file:
                env_file.write(f"WORKFLOW_PAT={gh_token}\n")
            print("✅ Token GitHub ajouté au fichier .env")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'ajout du token au fichier .env: {e}")
        
        # Mise à jour de la variable d'environnement pour cette session
        os.environ["WORKFLOW_PAT"] = gh_token
        
        # Sélection ou création du dépôt
        repo_name = self.select_repo()
        
        print(f"\nConfiguration des actions pour le dépôt {repo_name}...")
        
        try:
            # Vérifier si le dépôt existe et est accessible
            try:
                subprocess.run([gh_cmd, "repo", "view", repo_name], 
                              capture_output=True, check=True)
                print(f"✅ Dépôt {repo_name} accessible")
            except subprocess.CalledProcessError:
                print(f"❌ Impossible d'accéder au dépôt {repo_name}")
                print("Veuillez vérifier si le dépôt existe et si vous avez les permissions nécessaires.")
                return
            
            # Préparation des secrets
            with open(self.env_path, 'r') as f:
                env_content = f.read()
                cy_username = env_content.split('CY_USERNAME=')[1].split('\n')[0]
                cy_password = env_content.split('CY_PASSWORD=')[1].split('\n')[0]
            
            # Récupération des credentials Google
            credentials_files = list(self.google_dir.glob('client_secret_*.apps.googleusercontent.com.json'))
            if not credentials_files:
                print("❌ Fichier de credentials Google introuvable")
                sys.exit(1)
            
            with open(credentials_files[0], 'r') as f:
                google_credentials = f.read()

            google_token = None
            while google_token == None:
                try:
                    # Lecture du token Google
                    with open(self.google_dir / "token.pickle", 'rb') as f:
                        google_token = base64.b64encode(f.read()).decode('utf-8')
                except FileNotFoundError:
                    print("Fichier de token Google non généré.")
                    print("Execution de cyCalendar.py pour générer le token...")
                    print("Veuillez suivre les instructions affichées.")
                    time.sleep(3)
                    subprocess.run([sys.executable, "cyCalendar.py"], check=True)

            # Ajout des secrets - avec spécification explicite du repo
            print("\nConfiguration des secrets GitHub pour le dépôt", repo_name)
            secrets = {
                'CY_USERNAME': cy_username,
                'CY_PASSWORD': cy_password,
                'GOOGLE_CREDENTIALS': google_credentials,
                'GOOGLE_TOKEN': google_token,
                'WORKFLOW_PAT': gh_token
            }

            for secret_name, secret_value in secrets.items():
                print(f"Ajout du secret {secret_name}...")
                # Utiliser -R pour spécifier explicitement le dépôt
                subprocess.run([gh_cmd, "secret", "set", secret_name, "-R", repo_name, "-b", secret_value], check=True)
                print(f"✅ Secret {secret_name} ajouté avec succès!")

            # Liste et activation du workflow avec spécification du dépôt
            print("\nRécupération de la liste des workflows...")
            try:
                result = subprocess.run([gh_cmd, "workflow", "list", "-R", repo_name], 
                                       capture_output=True, text=True, check=True)
                print(result.stdout)

                # Extraction de l'ID du workflow
                workflows = result.stdout.splitlines()
                workflow_line = next((line for line in workflows if "Update Google Calendar" in line), None)
                
                if workflow_line:
                    workflow_id = workflow_line.split()[-1]  # Dernier élément (ID)
                    
                    # Activation du workflow
                    print("\nActivation du workflow...")
                    subprocess.run([gh_cmd, "workflow", "enable", workflow_id, "-R", repo_name], check=True)
                    print("✅ Workflow GitHub Actions activé!")
                    
                    # Lancement du workflow
                    print("\nLancement du workflow...")
                    subprocess.run([gh_cmd, "workflow", "run", workflow_id, "-R", repo_name], check=True)
                    print("✅ Workflow lancé!")
                else:
                    print("⚠️ Workflow 'Update Google Calendar' non trouvé")
                    print("Vérifiez que le fichier .github/workflows existe dans votre dépôt")
                    
                    # Proposer de pousser les workflows depuis le dépôt source
                    push_workflows = input("Voulez-vous copier les workflows depuis le dépôt source? (y/n): ")
                    if push_workflows.lower() == 'y':
                        try:
                            # Cloner temporairement le dépôt source et le fork
                            temp_dir = Path(tempfile.mkdtemp())
                            source_dir = temp_dir / "source"
                            fork_dir = temp_dir / "fork"
                            
                            print(f"Clonage du dépôt source dans {source_dir}...")
                            subprocess.run(["git", "clone", "https://github.com/NayJi7/CyCalendar.git", source_dir], check=True)
                            
                            print(f"Clonage de votre fork dans {fork_dir}...")
                            subprocess.run(["git", "clone", f"https://github.com/{repo_name}.git", fork_dir], check=True)
                            
                            # Copier les workflows
                            source_workflows = source_dir / ".github" / "workflows"
                            fork_workflows = fork_dir / ".github" / "workflows"
                            
                            if source_workflows.exists():
                                os.makedirs(fork_workflows, exist_ok=True)
                                for workflow_file in source_workflows.glob("*.yml"):
                                    shutil.copy2(workflow_file, fork_workflows)
                                
                                # Ajouter, commit et pousser
                                os.chdir(fork_dir)
                                subprocess.run(["git", "config", "user.name", "GitHub Actions Setup"], check=True)
                                subprocess.run(["git", "config", "user.email", "noreply@github.com"], check=True)
                                subprocess.run(["git", "add", ".github/workflows"], check=True)
                                subprocess.run(["git", "commit", "-m", "Add GitHub Actions workflows from original repo"], check=True)
                                subprocess.run(["git", "push"], check=True)
                                
                                print("✅ Workflows copiés et poussés vers votre fork")
                                
                                # Retour au répertoire du projet
                                os.chdir(self.project_root)
                                
                                # Nouvelle tentative de lister et activer le workflow
                                time.sleep(2)  # Attendre que GitHub détecte les changements
                                print("\nNouvelle tentative de lister les workflows...")
                                result = subprocess.run([gh_cmd, "workflow", "list", "-R", repo_name], 
                                                      capture_output=True, text=True, check=True)
                                workflows = result.stdout.splitlines()
                                workflow_line = next((line for line in workflows if "Update Google Calendar" in line), None)
                                
                                if workflow_line:
                                    workflow_id = workflow_line.split()[-1]
                                    print("\nActivation du workflow...")
                                    subprocess.run([gh_cmd, "workflow", "enable", workflow_id, "-R", repo_name], check=True)
                                    print("✅ Workflow GitHub Actions activé!")
                                    subprocess.run([gh_cmd, "workflow", "run", workflow_id, "-R", repo_name], check=True)
                                    print("✅ Workflow lancé!")
                                else:
                                    print("⚠️ Workflow toujours non trouvé. Veuillez vérifier manuellement.")
                        except Exception as e:
                            print(f"❌ Erreur lors de la copie des workflows: {e}")
                            import traceback
                            traceback.print_exc()

            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de la configuration du workflow : {e}")
                print(f"Détails: {e.stderr}")
            except Exception as e:
                print(f"❌ Une erreur s'est produite : {e}")
                import traceback
                traceback.print_exc()

            print("\n✅ Configuration de GitHub Actions terminée!")
            
            # Écriture du log
            self.write_log(4)

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'ajout des secrets: {e}")
            print(f"Détails: {e.stderr}")
            print("Veuillez résoudre l'erreur affichée ou les ajouter manuellement dans les paramètres de votre repo GitHub")
        except Exception as e:
            print(f"❌ Une erreur s'est produite: {e}")
            print("Veuillez résoudre l'erreur affichée ou ajouter les secrets manuellement dans les paramètres de votre repo GitHub")
            import traceback
            traceback.print_exc()

    def print_secret_values_for_manual_setup(self):
        """Affiche les valeurs des secrets pour une configuration manuelle."""
        try:
            # Récupérer les informations d'identification CY Tech du fichier .env
            if os.path.exists(self.env_path):
                with open(self.env_path, 'r') as f:
                    env_content = f.read()
                    cy_username = env_content.split('CY_USERNAME=')[1].split('\n')[0] if 'CY_USERNAME=' in env_content else "Non trouvé"
                    print(f"\nCY_USERNAME: {cy_username}")
                    print("CY_PASSWORD: [Votre mot de passe]")
            
            # Récupérer les chemins des fichiers de credentials Google
            credentials_files = list(self.google_dir.glob('client_secret_*.apps.googleusercontent.com.json'))
            if credentials_files:
                print(f"\nGOOGLE_CREDENTIALS: [Contenu du fichier {credentials_files[0]}]")
                print(f"Pour obtenir le contenu: ouvrez le fichier {credentials_files[0]} et copiez tout son contenu")
            
            token_path = self.google_dir / "token.pickle"
            if os.path.exists(token_path):
                print(f"\nGOOGLE_TOKEN: [Token encodé en base64]")
                print(f"Pour l'obtenir, exécutez la commande suivante dans un terminal Python:")
                print(f"import base64; print(base64.b64encode(open('{token_path}', 'rb').read()).decode('utf-8'))")
            
            print("\nWORKFLOW_PAT: [Votre token d'accès personnel GitHub]")
            print("Créez-en un sur: https://github.com/settings/tokens/new")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction des valeurs des secrets: {e}")

    def run(self):
        try:
            try:
                with open(".setup.log", "r") as f:
                    log = f.read()
                    log = int(log)
                    choice = input("Une installation précédente a été détectée. Souhaitez-vous reprendre cette installation ? (y/n): ")
                    if choice.lower() != 'y':
                        log = 0
            except FileNotFoundError:
                log = 0
                pass
            
            self.display_welcome()
            self.select_installation_mode()
            if log < 1: self.install_dependencies()
            if log < 2: self.setup_environment()
            
            if self.mode > 1 and log < 3:
                success = self.setup_google_api()
                if not success:
                    print("❌ Configuration de l'API Google Calendar échouée.")
                    return
            
            if self.mode == 3 and log < 4:
                self.setup_github_actions()
                print("\n\nConfiguration de GitHub Actions terminée! Vous pouvez maintenant vérifier le statut du workflow dans l'onglet Actions de votre repo GitHub.")
                print("Ou plus simplement patientez quelques minutes et consultez votre calendrier Google.")
            
            print("""
    =================================================
        Installation terminée!
    =================================================
    """)
            
            if self.mode == 1:
                print("N'oubliez pas d'importer manuellement le fichier ICS dans Google Calendar.")
            elif self.mode == 2:
                print("Vous pouvez maintenant réexécuter CyCalendar.py quand vous souhaitez mettre à jour votre calendrier.")
            else:
                print("GitHub Actions mettra automatiquement à jour votre calendrier chaque jour à une heure aléatoire entre 18h et 20h.")
                
        except KeyboardInterrupt:
            print("\n\nInstallation annulée par l'utilisateur.")
        except Exception as e:
            print(f"\n❌ Une erreur s'est produite: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    installer = CyCalendarInstaller()
    installer.run()