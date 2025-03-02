"""
Module d'initialisation de la base de données.

Ce module gère la création et l'initialisation des tables de la base de données.
"""

import sqlite3
import os

# Chemin absolu du dossier ressources
RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))

def init_db():
    """Initialise la base de données et crée les tables si elles n'existent pas."""
    try:
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Création de la table magasin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS magasin (
                "ID stuff" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Numero" TEXT,
                "Rayonnage" TEXT,
                "Etagere" TEXT,
                "Description" TEXT,
                "Providers" TEXT,
                "PN" TEXT,
                "Order" TEXT,
                "Quantity" INTEGER,
                "Minimum" INTEGER,
                "50H" INTEGER,
                "100H" INTEGER,
                "200H_ou_annuelle" INTEGER,
                "Providers_ACTF" TEXT,
                "Cost_Estimate" INTEGER,
                "Stock_Estimate_HT" INTEGER,
                "Remarks" TEXT
            )
        ''')
        
        # Création de la table planes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planes (
                "ID plane" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Planes" TEXT
            )
        ''')
        
        # Création de la table de relations entre planes et magasin
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planes_magasin (
                "ID stuff" INTEGER,
                "ID plane" INTEGER,
                PRIMARY KEY ("ID stuff", "ID plane")
        ''')
        
        conn.commit()
        conn.close()
        print("Base de données initialisée avec succès")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")
        return False

def get_db_connection():
    """Établit et retourne une connexion à la base de données."""
    try:
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        return sqlite3.connect(db_path)
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {str(e)}")
        return None

def drop_tables():
    """Supprime complètement les tables planes et magasin de la base de données."""
    try:
        conn = get_db_connection()
        if conn is None:
            print("Impossible de se connecter à la base de données")
            return False
            
        cursor = conn.cursor()
        
        # Suppression complète des tables
        cursor.execute('DROP TABLE IF EXISTS planes')
        cursor.execute('DROP TABLE IF EXISTS magasin')
        
        conn.commit()
        conn.close()
        print("Tables supprimées avec succès")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la suppression des tables : {str(e)}")
        return False


if __name__ == "__main__":
    init_db()