import sqlite3
import hashlib
import os
from ressources import allinfos as infos
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk

def init_db():
    """Initialise la base de données si elle n'existe pas."""
    try:
        db_path = os.path.join(infos.path, "bdd_all.db")
        # Supprimer la base de données si elle existe
        if os.path.exists(db_path):
            os.remove(db_path)
            
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

def new_user(username, password, name, firstname, email, tel, isAdmin=False):
    """
    Crée un nouveau compte utilisateur.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe (sera hashé)
        name (str): Nom de famille
        firstname (str): Prénom
        email (str): Adresse email
        tel (str): Numéro de téléphone
        isAdmin (bool, optional): Droits administrateur. Par défaut False
    
    Returns:
        tuple: (success, message)
    """
    try:
        if not init_db():
            return False, "Erreur d'initialisation de la base de données"
            
        conn = sqlite3.connect(os.path.join(infos.path, "bdd_all.db"))
        cursor = conn.cursor()
        
        # Vérification si l'utilisateur existe déjà
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Nom d'utilisateur déjà existant"
        
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Ajout du nouvel utilisateur
        cursor.execute('''
            INSERT INTO users (username, password, name, firstname, email, tel, isAdmin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, name, firstname, email, tel, isAdmin))
        
        conn.commit()
        conn.close()
        return True, "Compte créé avec succès"
    
    except Exception as e:
        return False, f"Erreur lors de la création du compte : {str(e)}"

def check_co(username, password):
    """
    Vérifie les identifiants de connexion.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe (sera hashé pour la comparaison)
    
    Returns:
        tuple: (success, message, user_data)
    """
    try:
        if not init_db():
            return False, "Erreur d'initialisation de la base de données", None
            
        conn = sqlite3.connect(os.path.join(infos.path, "bdd_all.db"))
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT username, name, firstname, email, tel, isAdmin
            FROM users
            WHERE username = ? AND password = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user_data = {
                "username": row[0],
                "name": row[1],
                "firstname": row[2],
                "email": row[3],
                "tel": row[4],
                "isAdmin": bool(row[5])
            }
            return True, "Connexion réussie", user_data
        
        return False, "Nom d'utilisateur ou mot de passe incorrect", None
        
    except Exception as e:
        return False, f"Erreur lors de la vérification des identifiants : {str(e)}", None

# Initialisation de la base de données au démarrage
init_db()
