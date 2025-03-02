"""Module de configuration et de gestion des thèmes de l'application.

Ce module gère les préférences utilisateur, les thèmes et les styles de l'interface.
"""

import os
import csv
import hashlib
from typing import Dict, Any


# Chemin absolu du dossier ressources
PATH = os.path.dirname(os.path.abspath(__file__))

# Chemin absolu de l'icone de l'application
ICON_PATH = os.path.join(PATH, "final_icon.ico")

# Fichier de configuration
CONFIG_FILE = os.path.join(PATH, "config.csv")

# Nom de l'application
NAME_MAIN = "Méca'stuff"

# Mode actuel (sombre par défaut)
is_dark_mode = True

# Styles de police
TITLE_FONT = ("Helvetica", 24, "bold")
SUBTITLE_FONT = ("Helvetica", 16, "bold")
BUTTON_FONT = ("Helvetica", 14)

# Dimensions
MAIN_BUTTON_WIDTH = 200
MAIN_BUTTON_HEIGHT = 40
BOTTOM_BUTTON_WIDTH = 150
SMALL_BUTTON_WIDTH = 30
ICON_BUTTON_SIZE = int(SMALL_BUTTON_WIDTH * 1.4)

# Espacements
DEFAULT_PAD = 20
SMALL_PAD = 10
TINY_PAD = 5

# Thèmes
DARK_THEME = {
    "bg_color": "#1A1A1A",
    "ctrl_color": "#FF4400",
    "label_color": "#FF4400",
    "text_color": "#FFFFFF",
    "hover_color": "#FF6633",
    "error_color": "#FF0000",
    "separator_color": "#FF4400"
}

LIGHT_THEME = {
    "bg_color": "#F5F5F5",
    "ctrl_color": "#FF4400",
    "label_color": "#FF4400",
    "text_color": "#1A1A1A",
    "hover_color": "#FF6633",
    "error_color": "#FF0000",
    "separator_color": "#FF4400"
}

# Initialisation des couleurs en mode sombre par défaut
bg_color = DARK_THEME["bg_color"]
ctrl_color = DARK_THEME["ctrl_color"]
label_color = DARK_THEME["label_color"]
text_color = DARK_THEME["text_color"]
hover_color = DARK_THEME["hover_color"]
error_color = DARK_THEME["error_color"]
separator_color = DARK_THEME["separator_color"]


def load_infos() -> None:
    """Charge les préférences depuis le fichier CSV."""
    global is_dark_mode
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    is_dark_mode = row['theme'].lower() == 'dark'
                    
                    # Mise à jour des couleurs selon le thème chargé
                    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
                    update_colors(theme)
    except Exception as e:
        print(f"Erreur lors du chargement des préférences : {e}")


def save_infos() -> None:
    """Sauvegarde les préférences dans un fichier CSV."""
    try:
        with open(CONFIG_FILE, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['theme'])
            writer.writeheader()
            writer.writerow({
                'theme': 'dark' if is_dark_mode else 'light'
            })
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des préférences : {e}")


def update_colors(theme: Dict[str, str]) -> None:
    """Met à jour les couleurs globales avec le thème spécifié.
    
    Args:
        theme: Dictionnaire contenant les couleurs du thème
    """
    global bg_color, ctrl_color, label_color, text_color, hover_color
    global error_color, separator_color
    
    bg_color = theme["bg_color"]
    ctrl_color = theme["ctrl_color"]
    label_color = theme["label_color"]
    text_color = theme["text_color"]
    hover_color = theme["hover_color"]
    error_color = theme["error_color"]
    separator_color = theme["separator_color"]


def toggle_theme() -> bool:
    """Bascule entre le mode clair et sombre et met à jour les couleurs.
    
    Returns:
        bool: True si le mode sombre est activé, False sinon
    """
    global is_dark_mode
    
    is_dark_mode = not is_dark_mode
    theme = DARK_THEME if is_dark_mode else LIGHT_THEME
    update_colors(theme)
    
    return is_dark_mode


# Chargement des préférences au démarrage
load_infos()
