"""
Module de manipulation de la base de données.

Ce module gère les opérations d'écriture dans la base de données.
"""

import os
import sqlite3
from typing import Tuple, Optional
from ressources.request_bd import db

# Chemin absolu du dossier ressources
RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))

def check_plane_exists(name: str) -> bool:
    """Vérifie si un avion existe déjà dans la base de données.
    
    Args:
        name: Nom de l'avion à vérifier
        
    Returns:
        bool: True si l'avion existe, False sinon
    """
    try:
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM planes WHERE "name" = ?', (name,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"Erreur lors de la vérification de l'avion : {str(e)}")
        return False

def ajout_plane(name: str) -> Tuple[bool, str]:
    """Ajoute un nouvel avion à la table planes.
    
    Args:
        name: Nom de l'avion à ajouter
        
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    try:
        # Vérification si l'avion existe déjà en utilisant request_bd
        if db.check_plane_exists(name):
            return False, "Cet avion existe déjà dans la base de données"
            
        # Connexion à la base de données
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Insertion du nouvel avion
        cursor.execute('INSERT INTO planes ("name") VALUES (?)', (name,))
        
        conn.commit()
        conn.close()
        return True, "Succès"
        
    except Exception as e:
        return False, f"Erreur lors de l'ajout de l'avion : {str(e)}"

if __name__ == "__main__":
    ajout_plane()
