"""
Module de gestion des requêtes de lecture de la base de données.

Ce module centralise toutes les requêtes de lecture vers la base de données,
en suivant les normes PEP 8 et en utilisant une approche orientée objet.
"""

import os
import sqlite3
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass

# Constantes de sécurité
MAX_QUERY_RESULTS = 1000  # Limite maximale de résultats par requête
MAX_FIELD_LENGTH = 255   # Longueur maximale des champs texte
MAX_COST = 1000000.0    # Coût maximum autorisé
MIN_COST = 0.0          # Coût minimum autorisé
MAX_QUANTITY = 10000    # Quantité maximale autorisée
MIN_QUANTITY = 0        # Quantité minimale autorisée

@dataclass
class DatabaseConfig:
    """Configuration de la base de données."""
    
    path: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "bdd_all.db"
    )
    
    def __post_init__(self):
        """Validation post-initialisation."""
        assert os.path.exists(self.path), f"La base de données n'existe pas : {self.path}"
        assert os.path.isfile(self.path), f"Le chemin n'est pas un fichier : {self.path}"
        assert os.access(self.path, os.R_OK), f"La base de données n'est pas accessible en lecture : {self.path}"


class DatabaseConnection:
    """Gestionnaire de connexion à la base de données."""
    
    def __init__(self, config: DatabaseConfig = DatabaseConfig()) -> None:
        """Initialise la connexion à la base de données.
        
        Args:
            config: Configuration de la base de données
            
        Raises:
            AssertionError: Si la configuration est invalide
        """
        assert isinstance(config, DatabaseConfig), "La configuration doit être de type DatabaseConfig"
        self.config = config
    
    def __enter__(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Établit la connexion à la base de données.
        
        Returns:
            Tuple contenant la connexion et le curseur
            
        Raises:
            sqlite3.Error: En cas d'erreur de connexion
        """
        try:
            self.conn = sqlite3.connect(self.config.path, timeout=30)  # Timeout de 30 secondes
            self.conn.execute("PRAGMA foreign_keys = ON")  # Active les contraintes de clés étrangères
            self.cursor = self.conn.cursor()
            return self.conn, self.cursor
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Erreur de connexion à la base de données : {str(e)}")
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ferme la connexion à la base de données de manière sécurisée."""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            if exc_type is None:
                self.conn.commit()  # Commit uniquement si pas d'exception
            else:
                self.conn.rollback()  # Rollback en cas d'exception
            self.conn.close()


class DatabaseQueries:
    """Classe regroupant toutes les requêtes de lecture de la base de données."""
    
    def __init__(self, config: DatabaseConfig = DatabaseConfig()) -> None:
        """Initialise le gestionnaire de requêtes.
        
        Args:
            config: Configuration de la base de données
            
        Raises:
            AssertionError: Si la configuration est invalide
        """
        assert isinstance(config, DatabaseConfig), "La configuration doit être de type DatabaseConfig"
        self.config = config
    
    def _validate_text_input(self, text: str, field_name: str, max_length: int = MAX_FIELD_LENGTH) -> None:
        """Valide une entrée texte.
        
        Args:
            text: Texte à valider
            field_name: Nom du champ pour le message d'erreur
            max_length: Longueur maximale autorisée
            
        Raises:
            ValueError: Si le texte est invalide
        """
        if not isinstance(text, str):
            raise ValueError(f"Le champ {field_name} doit être une chaîne de caractères")
        if len(text) > max_length:
            raise ValueError(f"Le champ {field_name} est trop long (max {max_length} caractères)")
        if any(c for c in text if ord(c) < 32 or ord(c) > 126):
            raise ValueError(f"Le champ {field_name} contient des caractères invalides")
    
    def check_user_credentials(
        self, 
        username: str, 
        password_hash: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Vérifie les identifiants d'un utilisateur.
        
        Args:
            username: Nom d'utilisateur
            password_hash: Hash du mot de passe
            
        Returns:
            Tuple (succès, message, données utilisateur)
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        try:
            self._validate_text_input(username, "nom d'utilisateur")
            self._validate_text_input(password_hash, "mot de passe")
            
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT username, name, firstname, email, tel, isAdmin
                    FROM users
                    WHERE username = ? AND password = ?
                    LIMIT 1
                ''', (username, password_hash))
                
                row = cursor.fetchone()
                
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
                
        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Erreur lors de la vérification : {str(e)}", None
    
    def check_plane_exists(self, name: str) -> bool:
        """Vérifie si un avion existe dans la base de données.
        
        Args:
            name: Nom de l'avion
            
        Returns:
            True si l'avion existe, False sinon
            
        Raises:
            ValueError: Si le nom est invalide
        """
        try:
            self._validate_text_input(name, "nom de l'avion")
            
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute(
                    'SELECT COUNT(*) FROM planes WHERE "name" = ? LIMIT 1', 
                    (name,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except ValueError as e:
            print(f"Erreur de validation : {str(e)}")
            return False
        except Exception as e:
            print(f"Erreur lors de la vérification de l'avion : {str(e)}")
            return False
    
    def get_all_planes(self) -> List[Tuple[str]]:
        """Récupère la liste de tous les avions.
        
        Returns:
            Liste des noms d'avions
            
        Note:
            La liste est limitée à MAX_QUERY_RESULTS éléments
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute(f'SELECT "name" FROM planes LIMIT {MAX_QUERY_RESULTS}')
                return cursor.fetchall()
        except Exception as e:
            print(f"Erreur lors de la récupération des avions : {str(e)}")
            return []
    
    def get_material_by_id(self, material_id: int) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un matériel par son ID.
        
        Args:
            material_id: ID du matériel
            
        Returns:
            Dictionnaire contenant les informations du matériel ou None si non trouvé
            
        Raises:
            ValueError: Si l'ID est invalide
        """
        try:
            if not isinstance(material_id, int) or material_id <= 0:
                raise ValueError("L'ID du matériel doit être un entier positif")
            
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT *
                    FROM magasin
                    WHERE "ID stuff" = ?
                    LIMIT 1
                ''', (material_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "ID stuff": row[0],
                        "Numero": row[1],
                        "Rayonnage": row[2],
                        "Etagere": row[3],
                        "Description": row[4],
                        "Providers": row[5],
                        "PN": row[6],
                        "Order": row[7],
                        "Quantity": max(MIN_QUANTITY, min(MAX_QUANTITY, row[8])),
                        "Minimum": max(MIN_QUANTITY, min(MAX_QUANTITY, row[9])),
                        "50H": bool(row[10]),
                        "100H": bool(row[11]),
                        "200H_ou_annuelle": bool(row[12]),
                        "Providers_ACTF": row[13],
                        "Cost_Estimate": max(MIN_COST, min(MAX_COST, row[14])),
                        "Stock_Estimate_HT": max(MIN_COST, min(MAX_COST, row[15])),
                        "Remarks": row[16]
                    }
                return None
        except ValueError as e:
            print(f"Erreur de validation : {str(e)}")
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du matériel : {str(e)}")
            return None
    
    def search_material(
        self, 
        search_term: str, 
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Recherche du matériel selon différents critères.
        
        Args:
            search_term: Terme de recherche
            fields: Liste des champs dans lesquels chercher (tous par défaut)
            
        Returns:
            Liste des matériels correspondants
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        try:
            self._validate_text_input(search_term, "terme de recherche")
            
            if fields is None:
                fields = ["Numero", "Description", "PN", "Providers"]
            else:
                allowed_fields = {"Numero", "Description", "PN", "Providers", "Rayonnage", "Etagere"}
                if not all(field in allowed_fields for field in fields):
                    raise ValueError("Champs de recherche invalides")
            
            with DatabaseConnection(self.config) as (_, cursor):
                where_clauses = [f'"{field}" LIKE ?' for field in fields]
                where_statement = " OR ".join(where_clauses)
                params = [f"%{search_term}%" for _ in fields]
                
                query = f'''
                    SELECT *
                    FROM magasin
                    WHERE {where_statement}
                    LIMIT {MAX_QUERY_RESULTS}
                '''
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [{
                    "ID stuff": row[0],
                    "Numero": row[1],
                    "Rayonnage": row[2],
                    "Etagere": row[3],
                    "Description": row[4],
                    "Providers": row[5],
                    "PN": row[6],
                    "Order": row[7],
                    "Quantity": max(MIN_QUANTITY, min(MAX_QUANTITY, row[8])),
                    "Minimum": max(MIN_QUANTITY, min(MAX_QUANTITY, row[9])),
                    "50H": bool(row[10]),
                    "100H": bool(row[11]),
                    "200H_ou_annuelle": bool(row[12]),
                    "Providers_ACTF": row[13],
                    "Cost_Estimate": max(MIN_COST, min(MAX_COST, row[14])),
                    "Stock_Estimate_HT": max(MIN_COST, min(MAX_COST, row[15])),
                    "Remarks": row[16]
                } for row in rows]
                
        except ValueError as e:
            print(f"Erreur de validation : {str(e)}")
            return []
        except Exception as e:
            print(f"Erreur lors de la recherche de matériel : {str(e)}")
            return []
    
    def get_material_planes(self, material_id: int) -> List[str]:
        """Récupère la liste des avions associés à un matériel.
        
        Args:
            material_id: ID du matériel
            
        Returns:
            Liste des noms d'avions
            
        Raises:
            ValueError: Si l'ID est invalide
        """
        try:
            if not isinstance(material_id, int) or material_id <= 0:
                raise ValueError("L'ID du matériel doit être un entier positif")
            
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT p.name
                    FROM planes p
                    JOIN planes_magasin pm ON p."ID plane" = pm."ID plane"
                    WHERE pm."ID stuff" = ?
                    LIMIT ?
                ''', (material_id, MAX_QUERY_RESULTS))
                
                return [row[0] for row in cursor.fetchall()]
                
        except ValueError as e:
            print(f"Erreur de validation : {str(e)}")
            return []
        except Exception as e:
            print(f"Erreur lors de la récupération des avions : {str(e)}")
            return []


# Instance globale pour un accès facile aux requêtes
db = DatabaseQueries()
