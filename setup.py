import sys
import platform
import subprocess
import getpass
import base64
import time
import shutil
import random
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

class CyCalendarInstaller:
    def __init__(self):
        self.os_type = platform.system()
        self.project_root = Path.cwd()
        self.env_path = self.project_root / '.env'
        self.google_dir = self.project_root / 'google'
        self.credentials_path = None
        self.mode = None
        
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
        
        # Demander les informations d'identification CY Tech
        cy_username = input("Entrez votre identifiant CY Tech (e-1erelettreprenom+nom): ")
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

    def install_gh_cli(self):
        try:
            # Vérifier si GitHub CLI est déjà installé
            subprocess.run(["gh", "--version"], check=True, capture_output=True)
            print("✅ GitHub CLI est déjà installé!")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Installation de GitHub CLI...")
            try:
                if self.os_type == "Linux":
                    # Installation pour distributions basées sur Debian/Ubuntu
                    subprocess.run(["type", "-p", "curl"], check=True)
                    subprocess.run(["curl", "-fsSL", "https://cli.github.com/packages/githubcli-archive-keyring.gpg", 
                                    "|", "sudo", "dd", "of=/usr/share/keyrings/githubcli-archive-keyring.gpg"], shell=True)
                    subprocess.run(['echo', 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main', 
                                    '|', 'sudo', 'tee', '/etc/apt/sources.list.d/github-cli.list'], shell=True)
                    subprocess.run(["sudo", "apt", "update"])
                    subprocess.run(["sudo", "apt", "install", "gh", "-y"])
                elif self.os_type == "Windows":
                    subprocess.run(["winget", "install", "--id", "GitHub.cli"])
                else:
                    print(f"⚠️ Installation manuelle requise pour {self.os_type}.")
                    print("Veuillez installer GitHub CLI depuis: https://cli.github.com/")
                    input("Appuyez sur Entrée une fois que vous avez installé GitHub CLI...")
                
                # Vérification de l'installation
                subprocess.run(["gh", "--version"], check=True)
                print("✅ GitHub CLI installé avec succès!")
            except subprocess.CalledProcessError:
                print("❌ Erreur lors de l'installation de GitHub CLI")
                print("Veuillez l'installer manuellement depuis: https://cli.github.com/")
                input("Appuyez sur Entrée une fois que vous avez installé GitHub CLI...")

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
        while(True):
            try:
                repos = subprocess.run(["gh", "repo", "list", "--limit", "100"], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True).stdout.strip().split('\n')
                
                print("\nVos dépôts GitHub :")
                print(f"0. Je n'ai pas encore fork le repo CyCalendar et donc je ne le vois pas dans les options")
                for i, repo in enumerate(repos, 1):
                    print(f"{i}. {repo}")
                
                choice = input("Sélectionnez votre fork de CyCalendar (ou 0 si vous ne l'avez pas encore fork) : ")

                if(choice == 0):
                    subprocess.run(["gh", "repo", "fork", "NayJi7/CyCalendar", f"--clone-directory={Path.home}"], check=True)
                    print("✅ Fork de CyCalendar effectué avec succès!")
                    break
                
                # Sélectionner un repo existant
                selected_repo = repos[int(choice) - 1].split()[0]
                return selected_repo
            
            except subprocess.CalledProcessError:
                print("❌ Impossible de récupérer la liste des dépôts.")
                sys.exit(1)

    def setup_github_actions(self):
        if self.mode != 3:
            print("\n[4/5] Mode GitHub Actions non sélectionné - Étape ignorée.")
            return
        
        # Installation de GitHub CLI
        self.install_gh_cli()
        
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
        
        print("\n[4/5] Configuration de GitHub Actions...")
        
        try:
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
            while(google_token == None):
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

            # Ajout des secrets
            print("\nConfiguration des secrets GitHub...")
            secrets = {
                'CY_USERNAME': cy_username,
                'CY_PASSWORD': cy_password,
                'GOOGLE_CREDENTIALS': google_credentials,
                'GOOGLE_TOKEN': google_token,
                'WORKFLOW_PAT': gh_token
            }

            for secret_name, secret_value in secrets.items():
                print(f"Ajout du secret {secret_name}...")
                subprocess.run(["gh", "secret", "set", secret_name, "-b", secret_value], check=True)
                print(f"✅ Secret {secret_name} ajouté avec succès!")

            # Liste et activation du workflow
            print("\nRécupération de la liste des workflows...")
            try:
                result = subprocess.run(["gh", "workflow", "list"], capture_output=True, text=True, check=True)
                print(result.stdout)

                # Extraction de l'ID du workflow
                workflows = result.stdout.splitlines()
                workflow_line = next((line for line in workflows if "Update Google Calendar" in line), None)
                
                if workflow_line:
                    workflow_id = workflow_line.split()[-1]  # Dernier élément (ID)
                    
                    # Activation du workflow
                    print("\nActivation du workflow...")
                    subprocess.run(["gh", "workflow", "enable", workflow_id], check=True)
                    print("✅ Workflow GitHub Actions activé!")
                    
                    # Lancement du workflow
                    print("\nLancement du workflow...")
                    subprocess.run(["gh", "workflow", "run", workflow_id], check=True)
                    print("✅ Workflow lancé!")
                else:
                    raise ValueError("Workflow 'Update Google Calendar' non trouvé")

            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de la configuration du workflow : {e}")
                import traceback
                traceback.print_exc()
            except Exception as e:
                print(f"❌ Une erreur s'est produite : {e}")
                import traceback
                traceback.print_exc()

            print("\n✅ Configuration de GitHub Actions terminée!")
            
            # Écriture du log
            self.write_log(4)

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'ajout des secrets: {e}")
            print("Veuillez résoudre l'erreur affichée ou les ajouter manuellement dans les paramètres de votre repo GitHub")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Une erreur s'est produite: {e}")
            print("Veuillez résoudre l'erreur affichée ou ajouter les secrets manuellement dans les paramètres de votre repo GitHub")
            sys.exit(1)

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