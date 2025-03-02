"""
Module de gestion des utilisateurs.

Ce module gère les opérations liées aux utilisateurs (création, vérification, etc.).
"""

import sqlite3
import hashlib
import os
from ressources import allinfos as infos
from ressources.request_bd import db
from typing import Tuple, Dict, Any, Optional

def init_db():
    """Initialise la base de données si elle n'existe pas."""
    try:
        db_path = os.path.join(infos.PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path)
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
        
        # Vérifier si la table est vide
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Ajouter les utilisateurs par défaut
            users = [
                ("jules.glt", "azerty", "Gillet", "Jules", "jules.gillet83@gmail.com", "0652003002", False),
                ("thibault.dlb", "Epicier", "de Laubrière", "Thibault", "thibdelaub@outlook.fr", "0769145620", True)
            ]
            
            for user in users:
                username, password, name, firstname, email, tel, isAdmin = user
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password, name, firstname, email, tel, isAdmin)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, name, firstname, email, tel, isAdmin))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")
        return False

def new_user(
    username: str,
    password: str,
    name: str,
    firstname: str,
    email: str,
    tel: str,
    isAdmin: bool
) -> Tuple[bool, str]:
    """Crée un nouvel utilisateur dans la base de données.
    
    Args:
        username: Nom d'utilisateur
        password: Mot de passe en clair
        name: Nom de famille
        firstname: Prénom
        email: Adresse email
        tel: Numéro de téléphone
        isAdmin: Droits administrateur
        
    Returns:
        Tuple contenant (succès, message)
    """
    try:
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Connexion à la base de données
        conn = sqlite3.connect(os.path.join(infos.PATH, "bdd_all.db"))
        cursor = conn.cursor()
        
        # Insertion du nouvel utilisateur
        cursor.execute('''
            INSERT INTO users (
                username, password, name, firstname, email, tel, isAdmin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, name, firstname, email, tel, isAdmin))
        
        conn.commit()
        conn.close()
        
        return True, "Utilisateur créé avec succès"
        
    except sqlite3.IntegrityError:
        return False, "Ce nom d'utilisateur existe déjà"
    except Exception as e:
        return False, f"Erreur lors de la création de l'utilisateur : {str(e)}"

def check_co(username: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """Vérifie les identifiants de connexion d'un utilisateur.
    
    Args:
        username: Nom d'utilisateur
        password: Mot de passe en clair
        
    Returns:
        Tuple contenant (succès, message, données utilisateur)
    """
    try:
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Connexion à la base de données
        db_path = os.path.join(infos.PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérification des identifiants
        cursor.execute('''
            SELECT username, name, firstname, email, tel, isAdmin
            FROM users
            WHERE username = ? AND password = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Création du dictionnaire de données utilisateur
            user_data = {
                "username": row[0],
                "name": row[1],
                "firstname": row[2],
                "email": row[3],
                "tel": row[4],
                "isAdmin": bool(row[5])
            }
            return True, "Connexion réussie", user_data
        else:
            return False, "Nom d'utilisateur ou mot de passe incorrect", None
            
    except Exception as e:
        return False, f"Erreur lors de la connexion : {str(e)}", None

# Initialisation de la base de données au démarrage
init_db()
