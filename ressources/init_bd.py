"""
Module d'initialisation de la base de données.

Ce module gère la création et l'initialisation des tables de la base de données.
"""

import os
import sqlite3
from typing import Optional, Tuple, Dict, List

# Constantes de sécurité
MAX_TEXT_LENGTH = 1000
MAX_QUANTITY = 10000
MIN_QUANTITY = 0
MAX_COST = 1000000
MIN_COST = 0
DB_TIMEOUT = 30
MAX_RETRIES = 3

# Chemin absolu du dossier ressources
RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))

def check_db_path() -> Tuple[bool, str]:
    """Vérifie que le chemin de la base de données est valide et accessible.
    
    Returns:
        Tuple[bool, str]: (True si valide, message d'erreur sinon)
    """
    try:
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        db_dir = os.path.dirname(db_path)
        
        if not os.path.exists(db_dir):
            return False, f"Le répertoire {db_dir} n'existe pas"
            
        if not os.access(db_dir, os.W_OK):
            return False, f"Le répertoire {db_dir} n'est pas accessible en écriture"
            
        if os.path.exists(db_path) and not os.access(db_path, os.W_OK):
            return False, f"La base de données {db_path} n'est pas accessible en écriture"
            
        return True, ""
        
    except Exception as e:
        return False, f"Erreur lors de la vérification du chemin : {str(e)}"

def init_db() -> bool:
    """Initialise la base de données et crée les tables si elles n'existent pas.
    
    Returns:
        bool: True si l'initialisation est réussie, False sinon
        
    Raises:
        AssertionError: Si le chemin de la base de données est invalide
    """
    try:
        # Vérification du chemin de la base de données
        valid, message = check_db_path()
        if not valid:
            raise AssertionError(message)
        
        db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
        conn = sqlite3.connect(db_path, timeout=DB_TIMEOUT)
        cursor = conn.cursor()
        
        # Activation des clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Création de la table users avec la colonne last_login
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL CHECK(length(password) >= 64),
                name TEXT NOT NULL CHECK(length(name) <= 50),
                firstname TEXT NOT NULL CHECK(length(firstname) <= 50),
                email TEXT NOT NULL CHECK(length(email) <= 100),
                tel TEXT NOT NULL CHECK(length(tel) <= 20),
                isAdmin BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Création de la table magasin avec contraintes
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS magasin (
                "ID stuff" INTEGER PRIMARY KEY AUTOINCREMENT,
                "Numero" TEXT CHECK(length("Numero") <= {MAX_TEXT_LENGTH}),
                "Rayonnage" TEXT CHECK(length("Rayonnage") <= {MAX_TEXT_LENGTH}),
                "Etagere" TEXT CHECK(length("Etagere") <= {MAX_TEXT_LENGTH}),
                "Description" TEXT CHECK(length("Description") <= {MAX_TEXT_LENGTH}),
                "Providers" TEXT CHECK(length("Providers") <= {MAX_TEXT_LENGTH}),
                "PN" TEXT CHECK(length("PN") <= {MAX_TEXT_LENGTH}),
                "Order" TEXT CHECK(length("Order") <= {MAX_TEXT_LENGTH}),
                "Quantity" INTEGER CHECK("Quantity" >= {MIN_QUANTITY} AND "Quantity" <= {MAX_QUANTITY}),
                "Minimum" INTEGER CHECK("Minimum" >= {MIN_QUANTITY} AND "Minimum" <= {MAX_QUANTITY}),
                "50H" INTEGER CHECK("50H" IN (0, 1)),
                "100H" INTEGER CHECK("100H" IN (0, 1)),
                "200H_ou_annuelle" INTEGER CHECK("200H_ou_annuelle" IN (0, 1)),
                "Providers_ACTF" TEXT CHECK(length("Providers_ACTF") <= {MAX_TEXT_LENGTH}),
                "Cost_Estimate" INTEGER CHECK("Cost_Estimate" >= {MIN_COST} AND "Cost_Estimate" <= {MAX_COST}),
                "Stock_Estimate_HT" INTEGER CHECK("Stock_Estimate_HT" >= {MIN_COST} AND "Stock_Estimate_HT" <= {MAX_COST}),
                "Remarks" TEXT CHECK(length("Remarks") <= {MAX_TEXT_LENGTH}),
                "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                "updated_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Création de la table planes avec contraintes
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS planes (
                "ID plane" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL UNIQUE CHECK(length("name") <= {MAX_TEXT_LENGTH}),
                "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Création de la table de relations avec contraintes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planes_magasin (
                "ID stuff" INTEGER,
                "ID plane" INTEGER,
                "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY ("ID stuff", "ID plane"),
                FOREIGN KEY ("ID stuff") REFERENCES magasin("ID stuff") ON DELETE CASCADE,
                FOREIGN KEY ("ID plane") REFERENCES planes("ID plane") ON DELETE CASCADE
            )
        ''')
        
        # Création des index pour optimiser les recherches
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasin_numero ON magasin("Numero")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasin_description ON magasin("Description")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_planes_name ON planes("name")')
        
        # Création des triggers pour la mise à jour automatique
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_magasin_timestamp 
            AFTER UPDATE ON magasin
            BEGIN
                UPDATE magasin SET updated_at = CURRENT_TIMESTAMP 
                WHERE "ID stuff" = NEW."ID stuff";
            END;
        ''')
        
        conn.commit()
        conn.close()
        print("Base de données initialisée avec succès")
        return True
        
    except AssertionError as e:
        print(f"Erreur de validation : {str(e)}")
        return False
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")
        return False

def get_db_connection() -> Optional[sqlite3.Connection]:
    """Établit et retourne une connexion à la base de données.
    
    Returns:
        Optional[sqlite3.Connection]: Connexion à la base de données ou None si erreur
        
    Note:
        La connexion doit être fermée par l'appelant après utilisation
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            # Vérification du chemin
            valid, message = check_db_path()
            if not valid:
                print(message)
                return None
            
            db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
            conn = sqlite3.connect(db_path, timeout=DB_TIMEOUT)
            
            # Activation des clés étrangères
            conn.execute("PRAGMA foreign_keys = ON")
            
            return conn
            
        except sqlite3.Error as e:
            print(f"Tentative {retries + 1}/{MAX_RETRIES} - Erreur : {str(e)}")
            retries += 1
            if retries < MAX_RETRIES:
                import time
                time.sleep(1)  # Attente d'une seconde avant la prochaine tentative
    
    print(f"Échec de connexion après {MAX_RETRIES} tentatives")
    return None

def drop_tables() -> bool:
    """Supprime complètement les tables planes et magasin de la base de données.
    
    Returns:
        bool: True si la suppression est réussie, False sinon
        
    Note:
        Cette opération est irréversible et doit être utilisée avec précaution
    """
    try:
        conn = get_db_connection()
        if conn is None:
            print("Impossible de se connecter à la base de données")
            return False
            
        cursor = conn.cursor()
        
        # Désactivation temporaire des clés étrangères pour la suppression
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Suppression des tables dans l'ordre inverse des dépendances
        cursor.execute('DROP TABLE IF EXISTS planes_magasin')
        cursor.execute('DROP TABLE IF EXISTS planes')
        cursor.execute('DROP TABLE IF EXISTS magasin')
        
        # Réactivation des clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        conn.close()
        print("Tables supprimées avec succès")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la suppression des tables : {str(e)}")
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False

def check_db_integrity() -> Tuple[bool, List[str]]:
    """Vérifie l'intégrité de la base de données.
    
    Returns:
        Tuple[bool, List[str]]: (True si ok, liste des problèmes détectés)
    """
    problems = []
    try:
        conn = get_db_connection()
        if conn is None:
            return False, ["Impossible de se connecter à la base de données"]
            
        cursor = conn.cursor()
        
        # Vérification de l'intégrité de la base
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        if integrity_result != "ok":
            problems.append(f"Échec du contrôle d'intégrité: {integrity_result}")
            
        # Vérification des clés étrangères
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            for violation in fk_violations:
                problems.append(f"Violation de clé étrangère dans la table {violation[0]}")
                
        # Vérification des index
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        required_indexes = [
            "idx_magasin_numero",
            "idx_magasin_description",
            "idx_planes_name"
        ]
        existing_indexes = [idx[0] for idx in indexes]
        for required_idx in required_indexes:
            if required_idx not in existing_indexes:
                problems.append(f"Index manquant: {required_idx}")
                
        # Vérification des triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        if "update_magasin_timestamp" not in [t[0] for t in triggers]:
            problems.append("Trigger de mise à jour manquant: update_magasin_timestamp")
            
        conn.close()
        
        if not problems:
            return True, []
        else:
            return False, problems
            
    except Exception as e:
        error_msg = f"Erreur lors de la vérification de l'intégrité : {str(e)}"
        return False, [error_msg]

def repair_db() -> bool:
    """Tente de réparer la base de données.
    
    Returns:
        bool: True si la réparation est réussie
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return False
            
        cursor = conn.cursor()
        
        # Vacuum pour optimiser et réparer la base
        cursor.execute("VACUUM")
        
        # Recréation des index manquants
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasin_numero ON magasin("Numero")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_magasin_description ON magasin("Description")')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_planes_name ON planes("name")')
        
        # Recréation du trigger de mise à jour
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_magasin_timestamp 
            AFTER UPDATE ON magasin
            BEGIN
                UPDATE magasin SET updated_at = CURRENT_TIMESTAMP 
                WHERE "ID stuff" = NEW."ID stuff";
            END;
        ''')
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False

def migrate_users_table() -> bool:
    """Met à jour la structure de la table users si nécessaire.
    
    Returns:
        bool: True si la migration est réussie, False sinon
    """
    try:
        conn = get_db_connection()
        if conn is None:
            print("Impossible de se connecter à la base de données")
            return False
            
        cursor = conn.cursor()
        
        # Vérification de l'existence de la colonne last_login
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "last_login" not in columns:
            # Création d'une table temporaire avec la nouvelle structure
            cursor.execute('''
                CREATE TABLE users_new (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL CHECK(length(password) >= 64),
                    name TEXT NOT NULL CHECK(length(name) <= 50),
                    firstname TEXT NOT NULL CHECK(length(firstname) <= 50),
                    email TEXT NOT NULL CHECK(length(email) <= 100),
                    tel TEXT NOT NULL CHECK(length(tel) <= 20),
                    isAdmin BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Copie des données existantes
            cursor.execute('''
                INSERT INTO users_new (
                    username, password, name, firstname, email, tel, isAdmin, created_at
                )
                SELECT username, password, name, firstname, email, tel, isAdmin, created_at
                FROM users
            ''')
            
            # Suppression de l'ancienne table et renommage de la nouvelle
            cursor.execute('DROP TABLE users')
            cursor.execute('ALTER TABLE users_new RENAME TO users')
            
            print("Table users mise à jour avec succès")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erreur lors de la migration de la table users : {str(e)}")
        if 'conn' in locals() and conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return False

if __name__ == "__main__":
    # Initialisation et vérification de la base
    if init_db():
        # Migration de la table users si nécessaire
        migrate_users_table()
        
        integrity_ok, problems = check_db_integrity()
        if not integrity_ok:
            print("Tentative de réparation de la base de données...")
            if repair_db():
                print("Base de données réparée avec succès")
            else:
                print("Échec de la réparation de la base de données")