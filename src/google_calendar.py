from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from icalendar import Calendar
from src.google_colors import *
import os.path
import pickle
import glob
import html
import base64
import subprocess

# Dictionary for agenda colors
# Equivalence in ../google/google_calendar_colors.png (Modern colors)
calendar_colors = {
    "Cocoa": 1, 
    "Flamingo": 2,
    "Tomato": 3,
    "Tangerine": 4,
    "Pumpkin": 5,
    "Mango": 6,
    "Eucalyptus": 7,
    "Basil": 8,
    "Pistachio": 9,
    "Avocado": 10,
    "Citron": 11,
    "Banana": 12,
    "Sage": 13,
    "Peacock": 14,
    "Cobalt": 15,
    "Blueberry": 16,
    "Lavender": 17,
    "Wisteria": 18,
    "Graphite": 19,
    "Birch": 20,
    "Radicchio": 21,
    "CherryBlossom": 22,
    "Grape": 23,
    "Amethyst": 24
}

# Dictionary for event colors
# Equivalence in ../google/google_event_colors.png (Modern colors)
event_colors = {
    "Lavender": 1,
    "Sage": 2,
    "Grape": 3,
    "Flamingo": 4,
    "Banana": 5,
    "Tangerine": 6,
    "Peacock": 7,
    "Graphite": 8,
    "Blueberry": 9,
    "Basil": 10,
    "Tomato": 11
    # None is calendar color
}

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_NAME = "Cours CY"
GOOGLE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'google')
TOKEN_PATH = os.path.join(GOOGLE_DIR, 'token.pickle')

def find_credentials_file():
    """
    Trouve le premier fichier client_secret*.json dans le répertoire google
    """
    json_files = glob.glob(os.path.join(GOOGLE_DIR, 'client_secret*.json'))
    return json_files[0] if json_files else None

def get_google_credentials():
    """
    Gère l'authentification Google avec une meilleure gestion des erreurs
    """
    creds = None
    credentials_path = find_credentials_file()
    
    if not credentials_path:
        print("Erreur: Aucun fichier client_secret*.json trouvé dans le dossier 'google'")
        return None
        
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Sauvegarder les credentials mis à jour
                with open(TOKEN_PATH, 'wb') as token:
                    pickle.dump(creds, token)
                # Pousser le token mis à jour vers GitHub si nous sommes en environnement CI
                update_github_token()
            except Exception as e:
                print("Erreur lors du rafraîchissement du token:", str(e))
                os.remove(TOKEN_PATH)  # Supprimer le token invalide
                return None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, 
                    SCOPES,
                    redirect_uri='http://localhost:8080/'
                )
                creds = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    access_type='offline'
                )
                
            except Exception as e:
                print("\nErreur d'authentification Google:")
                print("1. Vérifiez que votre compte est ajouté comme testeur dans la console Google Cloud")
                print("2. Accédez à https://console.cloud.google.com/apis/credentials")
                print("3. Sélectionnez votre projet")
                print("4. Dans 'OAuth 2.0 Client IDs', ajoutez votre email comme testeur")
                print("\nDétails de l'erreur:", str(e))
                return None
        
        # Sauvegarder les credentials
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
            
        # Pousser le token mis à jour vers GitHub si nous sommes en environnement CI
        update_github_token()
            
    return creds

def update_github_token():
    """
    Met à jour le secret GitHub avec le nouveau token si GitHub CLI est disponible
    """
    try:
        # Vérifier si nous avons un token d'authentification GitHub en variable d'environnement
        # Ce token devrait être défini lors de l'installation ou via le fichier .env
        workflow_pat = os.environ.get("WORKFLOW_PAT")
        
        if workflow_pat:
            print("Mise à jour du token Google dans les secrets GitHub...")
            
            # Lire le token
            with open(TOKEN_PATH, 'rb') as f:
                token_data = f.read()
                encoded_token = base64.b64encode(token_data).decode('utf-8')
            
            # Authentification avec GitHub CLI
            print("Authentification avec GitHub CLI...")
            result = subprocess.run(
                ["gh", "auth", "login", "--with-token"],
                input=workflow_pat.encode(),
                capture_output=True
            )
            
            if result.returncode == 0:
                # Mettre à jour le secret
                print("Mise à jour du secret GOOGLE_TOKEN...")
                subprocess.run(
                    ["gh", "secret", "set", "GOOGLE_TOKEN", "-b", encoded_token],
                    check=True
                )
                print("✅ Token Google mis à jour dans les secrets GitHub")
            else:
                print("⚠️ Échec de l'authentification GitHub, impossible de mettre à jour le token")
                print(f"Erreur: {result.stderr.decode()}")
    except Exception as e:
        print(f"⚠️ Impossible de mettre à jour le token GitHub: {e}")
        # Ne pas bloquer le processus principal en cas d'erreur

def find_or_create_calendar(service):
    """
    Cherche l'agenda 'Cours CY', le supprime s'il existe et en crée un nouveau
    """
    try:
        # Lister tous les calendriers
        calendar_list = service.calendarList().list().execute()
        
        # Chercher et supprimer le calendrier 'Cours CY' s'il existe
        for calendar_list_entry in calendar_list['items']:
            if (calendar_list_entry['summary'] == CALENDAR_NAME):
                print(f"Suppression de l'ancien agenda '{CALENDAR_NAME}'...")
                service.calendars().delete(calendarId=calendar_list_entry['id']).execute()
                break
        
        # Créer un nouveau calendrier
        print(f"Création d'un nouvel agenda '{CALENDAR_NAME}'...")
        calendar = {
            'summary': CALENDAR_NAME,
            'timeZone': 'Europe/Paris'
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        
        # Colorer le calendrier
        calendar_list_entry = service.calendarList().get(calendarId=created_calendar['id']).execute()
        # Couleur de l'agenda
        calendar_list_entry['colorId'] = calendar_colors['Cobalt'] # Bleu
        service.calendarList().update(calendarId=created_calendar['id'], body=calendar_list_entry).execute()
        
        return created_calendar['id']
        
    except HttpError as error:
        print(f"Erreur lors de la création du calendrier: {error}")
        raise

def clean_event_summary(summary):
    """
    Nettoie le titre de l'événement en supprimant la première occurrence de 'CM ', 'TD ' ou 'TP '
    quand ces termes apparaissent en double
    """
    for prefix in ['CM ', 'TD ', 'TP ']:
        if summary.count(prefix) > 1:
            # Trouve la première occurrence et la supprime
            first_pos = summary.find(prefix)
            if (first_pos != -1):
                summary = summary[:first_pos] + summary[first_pos + len(prefix):]
    return summary

def decode_html_entities(text):
    """
    Décode les entités HTML (comme &#224; pour à) en caractères Unicode
    """
    if not text:
        return text
    return html.unescape(text)

def get_event_color(summary):
    """
    Détermine la couleur de l'événement selon son type (CM/TD/TP/Examen)
    """
    summary = summary.upper()
    # Couleurs des événements
    if any(term in summary.lower() for term in ['examen', 'rattrapage', 'rattrapages', 'partiel']):
        return event_colors['Sage']  # Vert pour les examens
    elif 'CM' in summary:
        return event_colors['Peacock']  # Bleu pour les CM
    elif 'TD' in summary:
        return event_colors['Tomato']  # Rouge pour les TD
    elif 'TP' in summary:
        return event_colors['Tangerine']  # Orange pour les TP
    return event_colors['Graphite']  # Couleur par défaut

def import_to_google_calendar(ics_file_path, calendar_id=None):
    """
    Importe les événements d'un fichier ICS dans Google Calendar avec des opérations batch
    
    Args:
        ics_file_path (str): Chemin vers le fichier ICS à importer
        calendar_id (str, optional): ID du calendrier existant où importer les événements
        
    Returns:
        bool: True si l'import a réussi, False sinon
    """
    try:
        # Authentification Google
        creds = get_google_credentials()
        if not creds:
            return False
            
        service = build('calendar', 'v3', credentials=creds)
        
        # Créer un nouveau calendrier (l'ancien est automatiquement supprimé)
        calendar_id = find_or_create_calendar(service)
        
        # Lecture du fichier ICS
        with open(ics_file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
            
        print(f"Import des événements dans l'agenda '{CALENDAR_NAME}'...")
        events_count = 0
        batch_size = 50  # Google Calendar API limite à 50 requêtes par batch
        events_batch = []
        
        # Préparer les événements par lots
        for component in cal.walk('VEVENT'):
            try:
                # Nettoyer le titre de l'événement et décoder les entités HTML
                summary = str(component.get('summary'))
                cleaned_summary = clean_event_summary(summary)
                cleaned_summary = decode_html_entities(cleaned_summary)
                
                # Décoder aussi la description et le lieu
                location = decode_html_entities(str(component.get('location', '')))
                description = decode_html_entities(str(component.get('description', '')))
                
                event = {
                    'summary': cleaned_summary,
                    'location': location,
                    'description': description,
                    'start': {
                        'dateTime': component.get('dtstart').dt.isoformat(),
                        'timeZone': 'Europe/Paris',
                    },
                    'end': {
                        'dateTime': component.get('dtend').dt.isoformat(),
                        'timeZone': 'Europe/Paris',
                    }
                }
                
                # Définir la couleur selon le type d'événement
                color_id = get_event_color(cleaned_summary)
                if color_id:
                    event['colorId'] = color_id
                
                events_batch.append(event)
                events_count += 1
                
                # Traiter le lot quand il atteint la taille maximale
                if len(events_batch) >= batch_size:
                    batch = service.new_batch_http_request()
                    for evt in events_batch:
                        batch.add(service.events().insert(calendarId=calendar_id, body=evt))
                    batch.execute()
                    print(f"Progression: {events_count} événements importés...")
                    events_batch = []
                
            except Exception as e:
                print(f"Erreur lors de l'import d'un événement: {e}")
                continue
        
        # Traiter le dernier lot s'il reste des événements
        if events_batch:
            batch = service.new_batch_http_request()
            for evt in events_batch:
                batch.add(service.events().insert(calendarId=calendar_id, body=evt))
            batch.execute()
            
        print(f"Import terminé avec succès! {events_count} événements importés dans l'agenda '{CALENDAR_NAME}'")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'import: {str(e)}")
        print("\nSi vous voyez une erreur d'accès refusé:")
        print("Votre limite doit etre dépassée. Attendez quelques minutes et réessayez.")
        print("Si le problème persiste, contactez le développeur.")
        return False