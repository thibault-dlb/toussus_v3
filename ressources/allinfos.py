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

# Couleurs (thème sombre)
bg_color = "#1A1A1A"
ctrl_color = "#FF4400"
label_color = "#FF4400"
text_color = "#FFFFFF"
hover_color = "#FF6633"
error_color = "#FF0000"
separator_color = "#FF4400"

# Variables pour stocker les dernières valeurs
last_plane = ''
last_material = ''
last_quantity = ''
last_date = ''


def load_infos() -> None:
    """Charge les préférences depuis le fichier CSV."""
    global last_plane, last_material, last_quantity, last_date
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    last_plane = row.get('last_plane', '')
                    last_material = row.get('last_material', '')
                    last_quantity = row.get('last_quantity', '')
                    last_date = row.get('last_date', '')
                    
    except Exception as e:
        print(f"Erreur lors du chargement des préférences : {e}")


def save_infos() -> None:
    """Sauvegarde les préférences dans un fichier CSV."""
    try:
        with open(CONFIG_FILE, 'w', newline='') as file:
            fieldnames = ['last_plane', 'last_material', 'last_quantity', 'last_date', 'theme']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'last_plane': last_plane,
                'last_material': last_material,
                'last_quantity': last_quantity,
                'last_date': last_date,
                'theme': 'dark'
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
    """Fonction désactivée pour le switch thème."""
    pass


# Chargement des préférences au démarrage
load_infos()
