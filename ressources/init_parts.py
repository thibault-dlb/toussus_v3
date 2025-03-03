import sqlite3
import hashlib
import os
import bdd_users, manip_bd, db

def add_materials():
    """Ajoute des matériels à la base de données."""
    materials = [
        {
            "date": "2509",
            "rayonnage": "A0",
            "etagere": "A0",
            "description": "Door seal custom extrusion per roll",
            "providers": "Cirrus",
            "pn": "52010-008U",
            "order": "0",
            "quantity": 1,
            "minimum": 1,
            "maintenance": {
                "50h": 0,
                "100h": 0,
                "200h": 0
            },
            "providers_actf": "None",
            "cost": 79.00,
            "remarks": "1 896,00 €"
        },
        {
            "date": "2509",
            "rayonnage": "A1",
            "etagere": "A1.1",
            "description": "Recognition Light (28V)",
            "providers": "Whelen",
            "pn": "01-0770346-03",
            "order": "0",
            "quantity": 1,
            "minimum": 1,
            "maintenance": {
                "50h": 0,
                "100h": 0,
                "200h": 0
            },
            "providers_actf": "None",
            "cost": 0,
            "remarks": "79"
        }
    ]

    for material in materials:
        # Préparation des données
        material_data = {
            "rayonnage": material["rayonnage"],
            "etagere": material["etagere"],
            "description": material["description"],
            "providers": material["providers"],
            "pn": material["pn"],
            "order": material["order"],
            "quantity": material["quantity"],
            "minimum": material["minimum"],
            "providers_actf": material["providers_actf"],
            "cost": material["cost"],
            "remarks": material["remarks"],
            "maintenance": material["maintenance"]
        }

        # Insertion dans la base de données
        success, message = db.insert_material(material_data)
        if success:
            print(f"Matériel ajouté avec succès : {material_data['description']}")
        else:
            print(f"Erreur lors de l'ajout du matériel : {message}")

if __name__ == "__main__":
    add_materials()
