import sqlite3
import hashlib
import os
import sys

# Ajout du répertoire parent au path Python pour permettre l'importation des modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ressources import bdd_users, manip_bd
from ressources.request_bd import db

def add_materials():
    """Ajoute des matériels à la base de données."""
    materials = [
        {
            "numero": "2509",
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
            "cost_estimate": 79.00,
            "stock_estimate_ht": 1896.00,
            "remarks": "1 896,00 €",
            "plane_ids": []
        },
        {
            "numero": "2509",
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
            "cost_estimate": 0.00,
            "stock_estimate_ht": 79.00,
            "remarks": "79",
            "plane_ids": []
        }
    ]

    for material in materials:
        try:
            # Insertion dans la base de données
            success, message = manip_bd.ajouter_materiel(
                numero=material["numero"],
                rayonnage=material["rayonnage"],
                etagere=material["etagere"],
                description=material["description"],
                providers=material["providers"],
                pn=material["pn"],
                order=material["order"],
                quantity=material["quantity"],
                minimum=material["minimum"],
                maintenance=material["maintenance"],
                providers_actf=material["providers_actf"],
                cost_estimate=material["cost_estimate"],
                stock_estimate_ht=material["stock_estimate_ht"],
                remarks=material["remarks"],
                plane_ids=material["plane_ids"]
            )
            
            if success:
                print(f"Matériel ajouté avec succès : {material['description']}")
            else:
                print(f"Erreur lors de l'ajout du matériel : {message}")
                
        except Exception as e:
            print(f"Erreur inattendue lors de l'ajout du matériel : {str(e)}")

def add_material_from_excel(
    date: str,
    rayonnage: str = "A1",
    etagere: str = "1",
    description: str = "",
    providers: str = "",
    pn: str = "",
    order: str = "",
    aquila: bool = False,
    pa28: bool = False,
    da40: bool = False,
    sr20: bool = False,
    sr22: bool = False,
    quantity: int = 0,
    minimum: int = 0,
    h50: bool = False,
    h100: bool = False,
    h200: bool = False,
    providers_actf: str = "",
    cost: float = 0.0,
    stock: float = 0.0,
    remarks: str = ""
) -> tuple[bool, str]:
    """Ajoute un matériel à partir des données d'Excel.
    
    Args:
        date (str): Date d'ajout au format YYYY-MM-DD
        rayonnage (str): Numéro du rayonnage
        etagere (str): Numéro de l'étagère
        description (str): Description du matériel
        providers (str): Fournisseur
        pn (str): Référence PN
        order (str): Numéro de commande
        aquila (bool): Si True, associé à l'avion AQUILA
        pa28 (bool): Si True, associé à l'avion PA28-181
        da40 (bool): Si True, associé à l'avion DA40
        sr20 (bool): Si True, associé à l'avion SR20
        sr22 (bool): Si True, associé à l'avion SR22
        quantity (int): Quantité
        minimum (int): Quantité minimum
        h50 (bool): Maintenance 50h
        h100 (bool): Maintenance 100h
        h200 (bool): Maintenance 200h ou annuelle
        providers_actf (str): Fournisseurs ATCF
        cost (float): Coût unitaire
        stock (float): Valeur du stock
        remarks (str): Remarques
        
    Returns:
        tuple[bool, str]: (True si succès, message)
    """
    try:
        # Validation des données minimales requises
        if not description:
            return False, "La description est obligatoire"
            
        # Extraction de l'année et de la semaine de la date
        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        year_last_two = str(date_obj.year)[-2:]
        week_number = date_obj.strftime("%V")
        numero = f"{year_last_two}{week_number}"
        
        # Récupération des IDs des avions sélectionnés
        plane_ids = []
        planes_map = {
            "AQUILA": aquila,
            "PA28-181": pa28,
            "DA40": da40,
            "SR20": sr20,
            "SR22": sr22
        }
        
        for plane_name, is_selected in planes_map.items():
            if is_selected:
                try:
                    result = db.query('SELECT "ID plane" FROM planes WHERE name = ?', (plane_name,))
                    if result:
                        plane_ids.append(result[0][0])
                except Exception as e:
                    print(f"Erreur lors de la récupération de l'ID de l'avion {plane_name}: {str(e)}")
        
        # Configuration de la maintenance
        maintenance = {
            "50h": h50,
            "100h": h100,
            "200h": h200
        }
        
        # Ajout du matériel
        success, message = manip_bd.ajouter_materiel(
            numero=numero,
            date=date,
            rayonnage=rayonnage,
            etagere=etagere,
            description=description,
            providers=providers,
            pn=pn,
            order=order,
            quantity=quantity,
            minimum=minimum,
            maintenance=maintenance,
            providers_actf=providers_actf,
            cost=cost,
            stock=stock,
            remarks=remarks
        )
        
        # Si l'ajout a réussi et qu'il y a des avions sélectionnés, ajouter les relations
        if success and plane_ids:
            # Récupérer l'ID de la pièce qui vient d'être ajoutée
            piece_result = db.query(
                'SELECT "ID stuff" FROM magasin WHERE "Numero" = ? AND "Description" = ? ORDER BY created_at DESC LIMIT 1',
                (numero, description)
            )
            if piece_result:
                piece_id = piece_result[0][0]
                success, rel_message = manip_bd.ajouter_relations_piece_avions(piece_id, plane_ids)
                if not success:
                    return False, f"Matériel ajouté mais erreur lors de l'association aux avions : {rel_message}"
        
        return success, message
        
    except Exception as e:
        return False, f"Erreur inattendue : {str(e)}"

if __name__ == "__main__":
    add_materials()
