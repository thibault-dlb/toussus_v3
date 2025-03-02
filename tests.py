"""
Module de tests de la base de données.

Ce module permet de vérifier la structure et l'intégrité de la base de données.
"""

import sqlite3
from ressources.request_bd import DatabaseConnection, DatabaseConfig

def test_database_structure():
    """Teste la structure de la base de données."""
    config = DatabaseConfig()
    
    with DatabaseConnection(config) as (_, cursor):
        # Vérifier si la table users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ La table 'users' existe bien.")
        else:
            print("❌ La table 'users' n'existe pas !")
        
        # Vérifier la structure des tables
        cursor.execute("PRAGMA table_info(magasin)")
        magasin_columns = cursor.fetchall()
        print("\nStructure de la table 'magasin':")
        for col in magasin_columns:
            print(f"- {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(planes)")
        planes_columns = cursor.fetchall()
        print("\nStructure de la table 'planes':")
        for col in planes_columns:
            print(f"- {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(planes_magasin)")
        planes_magasin_columns = cursor.fetchall()
        print("\nStructure de la table 'planes_magasin':")
        for col in planes_magasin_columns:
            print(f"- {col[1]} ({col[2]})")

if __name__ == "__main__":
    test_database_structure()
