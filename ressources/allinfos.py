import os
import csv
import hashlib

# Chemin absolu du dossier ressources
path = os.path.dirname(os.path.abspath(__file__))

# Fichier de configuration
config_file = os.path.join(path, "config.csv")

# Nom de l'application
name_main = "Meca'stuff"

# Mode actuel (sombre par défaut)
is_dark_mode = True

# Chargement des préférences au démarrage
def load_infos():
    """Charge les préférences depuis le fichier CSV."""
    global is_dark_mode
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    is_dark_mode = row['theme'].lower() == 'dark'
                    
                    # Mise à jour des couleurs selon le thème chargé
                    theme = dark_theme if is_dark_mode else light_theme
                    update_colors(theme)
    except Exception as e:
        print(f"Erreur lors du chargement des préférences : {e}")
        # En cas d'erreur, on garde les valeurs par défaut

def save_infos():
    """Sauvegarde les préférences dans un fichier CSV."""
    try:
        with open(config_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['theme'])
            writer.writeheader()
            writer.writerow({
                'theme': 'dark' if is_dark_mode else 'light'
            })
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des préférences : {e}")

def update_colors(theme):
    """Met à jour les couleurs globales avec le thème spécifié."""
    global bg_color, ctrl_color, label_color, text_color, hover_color, error_color, separator_color
    
    bg_color = theme["bg_color"]
    ctrl_color = theme["ctrl_color"]
    label_color = theme["label_color"]
    text_color = theme["text_color"]
    hover_color = theme["hover_color"]
    error_color = theme["error_color"]
    separator_color = theme["separator_color"]

# Couleurs du mode sombre
dark_theme = {
    "bg_color": "#1A1A1A",  # Noir anthracite comme la carrosserie
    "ctrl_color": "#FF4400",  # Orange vif comme les accents de la Bugatti
    "label_color": "#FF4400",  # Orange vif pour la cohérence
    "text_color": "#FFFFFF",  # Blanc pour le contraste
    "hover_color": "#FF6633",  # Orange plus clair pour le hover
    "error_color": "#FF0000",  # Rouge vif pour les actions critiques
    "separator_color": "#FF4400"  # Orange pour les séparateurs
}

# Couleurs du mode clair
light_theme = {
    "bg_color": "#F5F5F5",  # Gris très clair
    "ctrl_color": "#FF4400",  # Orange vif comme les accents de la Bugatti
    "label_color": "#FF4400",  # Orange vif pour la cohérence
    "text_color": "#1A1A1A",  # Noir pour le contraste
    "hover_color": "#FF6633",  # Orange plus clair pour le hover
    "error_color": "#FF0000",  # Rouge vif pour les actions critiques
    "separator_color": "#FF4400"  # Orange pour les séparateurs
}

# Couleurs actuelles (initialisées en mode sombre par défaut)
bg_color = dark_theme["bg_color"]
ctrl_color = dark_theme["ctrl_color"]
label_color = dark_theme["label_color"]
text_color = dark_theme["text_color"]
hover_color = dark_theme["hover_color"]
error_color = dark_theme["error_color"]
separator_color = dark_theme["separator_color"]

def toggle_theme():
    """Bascule entre le mode clair et sombre et met à jour les couleurs."""
    global is_dark_mode
    
    is_dark_mode = not is_dark_mode
    theme = dark_theme if is_dark_mode else light_theme
    update_colors(theme)
    
    return is_dark_mode

# Chargement des préférences au démarrage
load_infos()

# Styles de police
title_font = ("Helvetica", 24, "bold")  # Police pour les titres principaux
subtitle_font = ("Helvetica", 16, "bold")  # Police pour les sous-titres
button_font = ("Helvetica", 14)  # Police pour les boutons

# Dimensions
main_button_width = 200  # Largeur des boutons principaux
main_button_height = 40  # Hauteur des boutons principaux
bottom_button_width = 150  # Largeur des boutons du bas
small_button_width = 30  # Largeur des petits boutons (retour, fermer)
icon_button_size = int(small_button_width * 1.4)  # Taille des boutons icônes (42px)

# Espacements
default_pad = 20  # Espacement par défaut
small_pad = 10  # Petit espacement
tiny_pad = 5  # Très petit espacement
