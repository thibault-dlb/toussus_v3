"""
Module de gestion des requêtes de lecture de la base de données.

Ce module centralise toutes les requêtes de lecture vers la base de données,
en suivant les normes PEP 8 et en utilisant une approche orientée objet.
"""

import os
import sqlite3
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Configuration de la base de données."""
    
    path: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        "bdd_all.db"
    )


class DatabaseConnection:
    """Gestionnaire de connexion à la base de données."""
    
    def __init__(self, config: DatabaseConfig = DatabaseConfig()) -> None:
        """Initialise la connexion à la base de données.
        
        Args:
            config: Configuration de la base de données
        """
        self.config = config
    
    def __enter__(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Établit la connexion à la base de données.
        
        Returns:
            Tuple contenant la connexion et le curseur
        """
        self.conn = sqlite3.connect(self.config.path)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ferme la connexion à la base de données."""
        self.cursor.close()
        self.conn.close()


class DatabaseQueries:
    """Classe regroupant toutes les requêtes de lecture de la base de données."""
    
    def __init__(self, config: DatabaseConfig = DatabaseConfig()) -> None:
        """Initialise le gestionnaire de requêtes.
        
        Args:
            config: Configuration de la base de données
        """
        self.config = config
    
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
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT username, name, firstname, email, tel, isAdmin
                    FROM users
                    WHERE username = ? AND password = ?
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
                
        except Exception as e:
            return False, f"Erreur lors de la vérification : {str(e)}", None
    
    def check_plane_exists(self, name: str) -> bool:
        """Vérifie si un avion existe dans la base de données.
        
        Args:
            name: Nom de l'avion
            
        Returns:
            True si l'avion existe, False sinon
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute(
                    'SELECT COUNT(*) FROM planes WHERE "name" = ?', 
                    (name,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"Erreur lors de la vérification de l'avion : {str(e)}")
            return False
    
    def get_all_planes(self) -> List[Tuple[str]]:
        """Récupère la liste de tous les avions.
        
        Returns:
            Liste des noms d'avions
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('SELECT "name" FROM planes')
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
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT *
                    FROM magasin
                    WHERE "ID stuff" = ?
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
                        "Quantity": row[8],
                        "Minimum": row[9],
                        "50H": row[10],
                        "100H": row[11],
                        "200H_ou_annuelle": row[12],
                        "Providers_ACTF": row[13],
                        "Cost_Estimate": row[14],
                        "Stock_Estimate_HT": row[15],
                        "Remarks": row[16]
                    }
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
        """
        if fields is None:
            fields = ["Numero", "Description", "PN", "Providers"]
            
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                where_clauses = [f'"{field}" LIKE ?' for field in fields]
                where_statement = " OR ".join(where_clauses)
                params = [f"%{search_term}%" for _ in fields]
                
                query = f'''
                    SELECT *
                    FROM magasin
                    WHERE {where_statement}
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
                    "Quantity": row[8],
                    "Minimum": row[9],
                    "50H": row[10],
                    "100H": row[11],
                    "200H_ou_annuelle": row[12],
                    "Providers_ACTF": row[13],
                    "Cost_Estimate": row[14],
                    "Stock_Estimate_HT": row[15],
                    "Remarks": row[16]
                } for row in rows]
                
        except Exception as e:
            print(f"Erreur lors de la recherche de matériel : {str(e)}")
            return []
    
    def get_material_planes(self, material_id: int) -> List[str]:
        """Récupère la liste des avions associés à un matériel.
        
        Args:
            material_id: ID du matériel
            
        Returns:
            Liste des noms d'avions
        """
        try:
            with DatabaseConnection(self.config) as (_, cursor):
                cursor.execute('''
                    SELECT p.name
                    FROM planes p
                    JOIN planes_magasin pm ON p."ID plane" = pm."ID plane"
                    WHERE pm."ID stuff" = ?
                ''', (material_id,))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Erreur lors de la récupération des avions : {str(e)}")
            return []


# Instance globale pour un accès facile aux requêtes
db = DatabaseQueries()
