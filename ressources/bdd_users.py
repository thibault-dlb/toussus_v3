"""
Module de gestion des utilisateurs.

Ce module gère les opérations liées aux utilisateurs (création, vérification, etc.).
"""

import sqlite3
import hashlib
import os
import re
from ressources import allinfos as infos
from ressources.request_bd import db
from typing import Tuple, Dict, Any, Optional, List

# Constantes de sécurité
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 100
MAX_NAME_LENGTH = 50
MAX_EMAIL_LENGTH = 100
MAX_TEL_LENGTH = 20
MAX_USERS = 1000
MIN_PASSWORD_LENGTH = 8

# Expressions régulières de validation
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
TEL_PATTERN = re.compile(r'^\+?[0-9]{10,15}$')
NAME_PATTERN = re.compile(r'^[a-zA-ZÀ-ÿ\s-]+$')

def validate_input(value: str, pattern: re.Pattern, field_name: str, max_length: int) -> None:
    """Valide une entrée selon un pattern et une longueur maximale.
    
    Args:
        value: Valeur à valider
        pattern: Pattern de validation
        field_name: Nom du champ pour le message d'erreur
        max_length: Longueur maximale autorisée
        
    Raises:
        ValueError: Si la valeur est invalide
    """
    if not isinstance(value, str):
        raise ValueError(f"Le champ {field_name} doit être une chaîne de caractères")
    if not value.strip():
        raise ValueError(f"Le champ {field_name} ne peut pas être vide")
    if len(value) > max_length:
        raise ValueError(f"Le champ {field_name} est trop long (max {max_length} caractères)")
    if not pattern.match(value):
        raise ValueError(f"Le champ {field_name} contient des caractères invalides")

def init_db() -> bool:
    """Initialise la base de données si elle n'existe pas.
    
    Returns:
        bool: True si l'initialisation est réussie, False sinon
        
    Raises:
        AssertionError: Si le chemin de la base de données est invalide
    """
    try:
        db_path = os.path.join(infos.PATH, "bdd_all.db")
        assert os.path.exists(os.path.dirname(db_path)), "Le répertoire de la base de données n'existe pas"
        assert os.access(os.path.dirname(db_path), os.W_OK), "Le répertoire n'est pas accessible en écriture"
        
        conn = sqlite3.connect(db_path, timeout=30)  # Timeout de 30 secondes
        cursor = conn.cursor()
        
        # Activation des clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Création de la table users si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL CHECK(length(password) >= 64),
                name TEXT NOT NULL CHECK(length(name) <= ?),
                firstname TEXT NOT NULL CHECK(length(firstname) <= ?),
                email TEXT NOT NULL CHECK(length(email) <= ?),
                tel TEXT NOT NULL CHECK(length(tel) <= ?),
                isAdmin BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''', (MAX_NAME_LENGTH, MAX_NAME_LENGTH, MAX_EMAIL_LENGTH, MAX_TEL_LENGTH))
        
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
                
                # Validation des données
                validate_input(username, USERNAME_PATTERN, "nom d'utilisateur", MAX_USERNAME_LENGTH)
                validate_input(name, NAME_PATTERN, "nom", MAX_NAME_LENGTH)
                validate_input(firstname, NAME_PATTERN, "prénom", MAX_NAME_LENGTH)
                validate_input(email, EMAIL_PATTERN, "email", MAX_EMAIL_LENGTH)
                validate_input(tel, TEL_PATTERN, "téléphone", MAX_TEL_LENGTH)
                
                # Hash du mot de passe
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO users (
                        username, password, name, firstname, email, tel, isAdmin
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (username, password_hash, name, firstname, email, tel, isAdmin))
        
        conn.commit()
        conn.close()
        return True
        
    except (AssertionError, ValueError) as e:
        print(f"Erreur de validation : {str(e)}")
        return False
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
        
    Raises:
        ValueError: Si les paramètres sont invalides
    """
    try:
        # Validation des entrées
        validate_input(username, USERNAME_PATTERN, "nom d'utilisateur", MAX_USERNAME_LENGTH)
        validate_input(name, NAME_PATTERN, "nom", MAX_NAME_LENGTH)
        validate_input(firstname, NAME_PATTERN, "prénom", MAX_NAME_LENGTH)
        validate_input(email, EMAIL_PATTERN, "email", MAX_EMAIL_LENGTH)
        validate_input(tel, TEL_PATTERN, "téléphone", MAX_TEL_LENGTH)
        
        # Validation du mot de passe
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Le mot de passe doit faire au moins {MIN_PASSWORD_LENGTH} caractères")
        if len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Le mot de passe est trop long (max {MAX_PASSWORD_LENGTH} caractères)")
        
        # Vérification du type de isAdmin
        if not isinstance(isAdmin, bool):
            raise ValueError("isAdmin doit être un booléen")
        
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Connexion à la base de données
        db_path = os.path.join(infos.PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # Vérification du nombre d'utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] >= MAX_USERS:
            conn.close()
            return False, f"Nombre maximum d'utilisateurs atteint ({MAX_USERS})"
        
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
        
    except ValueError as e:
        return False, str(e)
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
        
    Raises:
        ValueError: Si les paramètres sont invalides
    """
    try:
        # Validation des entrées
        validate_input(username, USERNAME_PATTERN, "nom d'utilisateur", MAX_USERNAME_LENGTH)
        if not password:
            raise ValueError("Le mot de passe ne peut pas être vide")
        if len(password) > MAX_PASSWORD_LENGTH:
            raise ValueError(f"Le mot de passe est trop long (max {MAX_PASSWORD_LENGTH} caractères)")
        
        # Hash du mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Connexion à la base de données
        db_path = os.path.join(infos.PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # Vérification des identifiants
        cursor.execute('''
            SELECT username, name, firstname, email, tel, isAdmin
            FROM users
            WHERE username = ? AND password = ?
            LIMIT 1
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        
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
            conn.close()
            return True, "Connexion réussie", user_data
        else:
            conn.close()
            return False, "Nom d'utilisateur ou mot de passe incorrect", None
            
    except ValueError as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Erreur lors de la connexion : {str(e)}", None

# Initialisation de la base de données au démarrage
init_db()
