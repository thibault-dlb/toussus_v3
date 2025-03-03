import sqlite3
import os

def clear_magasin_table():
    """Vide la table magasin et réinitialise l'auto-increment."""
    try:
        # Chemin absolu vers le répertoire du projet
        project_path = r"C:\Users\thibd\OneDrive\Projet_python_toussus\V3\toussus_v3"
        
        # Chemin complet vers la base de données
        db_path = os.path.join(project_path, 'ressources', 'bdd_all.db')
        
        if not os.path.exists(db_path):
            print(f"Erreur : Base de données non trouvée à {db_path}")
            return
            
        print(f"Connexion à la base de données : {db_path}")
        
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Désactiver les contraintes de clés étrangères temporairement
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Supprimer toutes les entrées de la table planes_magasin
        cursor.execute("DELETE FROM planes_magasin")
        print("Table planes_magasin vidée")
        
        # Supprimer toutes les entrées de la table magasin
        cursor.execute("DELETE FROM magasin")
        print("Table magasin vidée")
        
        # Réinitialiser l'auto-increment
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='magasin'")
        print("Auto-increment réinitialisé")
        
        # Réactiver les contraintes de clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Valider les changements
        conn.commit()
        
        print("La table magasin a été vidée avec succès.")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage de la table : {str(e)}")
        
    finally:
        # Fermer la connexion
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_magasin_table() 