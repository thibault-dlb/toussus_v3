"""Module d'initialisation de la base de données utilisateurs.

Ce module gère la création et l'initialisation de la table des utilisateurs
avec les comptes par défaut.
"""

import os
import sqlite3
import hashlib
from typing import List, Tuple

from ressources import allinfos as infos


# Liste des utilisateurs par défaut
DEFAULT_USERS: List[Tuple[str, str, str, str, str, str, bool]] = [
    (
        "jules.glt",
        "azerty",
        "Gillet",
        "Jules",
        "jules.gillet83@gmail.com",
        "0652003002",
        False
    ),
    (
        "thibault.dlb",
        "Epicier",
        "de Laubrière",
        "Thibault",
        "thibdelaub@outlook.fr",
        "0769145620",
        True
    )
]


def init_database() -> None:
    """Initialise la base de données avec les utilisateurs par défaut."""
    conn = sqlite3.connect(os.path.join(infos.PATH, "bdd_all.db"))
    cursor = conn.cursor()
    
    # Création de la table users si elle n'existe pas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            firstname TEXT NOT NULL,
            email TEXT NOT NULL,
            tel TEXT NOT NULL,
            isAdmin BOOLEAN NOT NULL
        )
    ''')
    
    # Suppression des données existantes
    cursor.execute('DELETE FROM users')
    
    # Ajout des utilisateurs par défaut
    for user in DEFAULT_USERS:
        username, password, name, firstname, email, tel, isAdmin = user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('''
                INSERT INTO users (
                    username, password, name, firstname, email, tel, isAdmin
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password_hash, name, firstname, email, tel, isAdmin))
            print(f"✅ Utilisateur {username} ajouté avec succès !")
        except sqlite3.IntegrityError as e:
            print(f"❌ Erreur lors de l'ajout de {username} : {e}")
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()