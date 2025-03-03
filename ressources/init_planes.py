import sqlite3
import os
import sys

# Ajout du répertoire parent au path Python pour permettre l'importation des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ressources import manip_bd

def add_planes():
    """Ajoute des avions à la base de données."""
    planes = [
        "AQUILA",
        "PA28-181",
        "DA40",
        "SR20",
        "SR22"
    ]

    for plane in planes:
        try:
            # Insertion dans la base de données
            success, message = manip_bd.ajout_plane(plane)
            
            if success:
                print(f"Avion ajouté avec succès : {plane}")
            else:
                print(f"Erreur lors de l'ajout de l'avion : {message}")
                
        except Exception as e:
            print(f"Erreur inattendue lors de l'ajout de l'avion : {str(e)}")

if __name__ == "__main__":
    add_planes() 