import os
import sys
import pyexcel_ods
from datetime import datetime
from typing import Dict, Any, List, Tuple
import re
import pandas as pd
import random  # Ajouter cet import en haut du fichier

# Ajout du répertoire parent au path Python pour permettre l'importation des modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ressources.init_parts import add_material_from_excel

PN_PATTERN = re.compile(r'^[A-Za-z0-9\-\./\s\(\)]+$')
ORDER_PATTERN = re.compile(r'^[A-Z0-9-]+$')
PROVIDER_PATTERN = re.compile(r'^[A-Za-z0-9\s\-\.\(\)]*$')

def convert_to_bool(value: str) -> bool:
    """Convertit une valeur en booléen.
    
    Args:
        value: Valeur à convertir (x, X, 1 = True, reste = False)
    
    Returns:
        bool: True si la valeur est x, X ou 1, False sinon
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in ['x', '1', 'true', 'oui', 'yes']
    return False

def clean_string(value: Any, default: str = "") -> str:
    """Nettoie une chaîne de caractères.
    
    Args:
        value: Valeur à nettoyer
        default: Valeur par défaut si vide
        
    Returns:
        str: Chaîne nettoyée
    """
    if value is None:
        return default
    cleaned = str(value).strip()
    return cleaned if cleaned else default

def convert_to_float(value: Any) -> float:
    """Convertit une valeur en float.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        float: Valeur convertie ou 0.0 si impossible
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Nettoyer la chaîne
        value = value.strip().replace(' ', '').replace(',', '.')
        # Supprimer les symboles monétaires courants
        value = value.replace('€', '').replace('$', '')
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0

def convert_to_int(value: Any) -> int:
    """Convertit une valeur en int.
    
    Args:
        value: Valeur à convertir
        
    Returns:
        int: Valeur convertie ou 0 si impossible
    """
    try:
        return int(float(convert_to_float(value)))
    except (ValueError, TypeError):
        return 0

def import_from_ods(file_path: str) -> None:
    """Importe les données depuis un fichier ODS."""
    try:
        data = pyexcel_ods.get_data(file_path)
        sheet_name = list(data.keys())[0]
        rows = data[sheet_name]
        
        header = rows[0]
        data_rows = rows[1:]
        
        success_count = 0
        error_count = 0
        
        # Variable pour stocker le dernier rayonnage non vide
        last_rayonnage = None
        last_etagere = None
        
        for row in data_rows:
            try:
                # Ignorer les lignes trop courtes
                if len(row) < 4:  # Au minimum besoin jusqu'à la description
                    print(f"Ligne ignorée (pas assez de colonnes): {row}")
                    error_count += 1
                    continue
                
                # Gestion du rayonnage (colonne 2)
                current_rayonnage = clean_string(row[1] if len(row) > 1 else None)
                if current_rayonnage:  # Si un nouveau rayonnage est spécifié
                    last_rayonnage = current_rayonnage
                rayonnage = last_rayonnage if last_rayonnage else "A1"
                print(f"Debug - Traitement rayonnage:")
                print(f"  Current: '{current_rayonnage}'")
                print(f"  Last: '{last_rayonnage}'")
                print(f"  Final: '{rayonnage}'")
                
                # Gestion de l'étagère (colonne 3)
                etagere = clean_string(row[2] if len(row) > 2 else None)
                if not etagere:
                    etagere = last_etagere if last_etagere else ""
                last_etagere = etagere
                
                # Autres champs
                description = clean_string(row[3] if len(row) > 3 else None)
                providers = clean_string(row[4] if len(row) > 4 else None)
                pn = clean_string(row[5] if len(row) > 5 else None)
                order = clean_string(row[6] if len(row) > 6 else "0")
                
                # Avions (colonnes 8-12) - convertir toute valeur non vide en True
                aquila = bool(clean_string(row[7] if len(row) > 7 else None))
                pa28 = bool(clean_string(row[8] if len(row) > 8 else None))
                da40 = bool(clean_string(row[9] if len(row) > 9 else None))
                sr20 = bool(clean_string(row[10] if len(row) > 10 else None))
                sr22 = bool(clean_string(row[11] if len(row) > 11 else None))
                
                # Quantités (colonnes 13-14)
                quantity = convert_to_int(row[12] if len(row) > 12 else 0)
                minimum = convert_to_int(row[13] if len(row) > 13 else 0)
                
                # Maintenance (colonnes 15-17)
                h50 = bool(clean_string(row[14] if len(row) > 14 else None))
                h100 = bool(clean_string(row[15] if len(row) > 15 else None))
                h200 = bool(clean_string(row[16] if len(row) > 16 else None))
                
                # Autres informations
                providers_actf = clean_string(row[17] if len(row) > 17 else None)
                
                # Remplacer la gestion du coût par un nombre aléatoire
                cost = random.randint(1, 2000)
                
                print(f"Debug - Coût aléatoire généré: {cost}")
                
                # Calcul du stock (coût * quantité)
                stock = cost * quantity
                
                # Remarques (colonne 21)
                remarks = clean_string(row[20] if len(row) > 20 else None)
                
                # Vérification des données minimales requises
                if not description:
                    print(f"Ligne ignorée (description manquante): {row}")
                    error_count += 1
                    continue
                
                # Debug print pour vérifier les valeurs
                print(f"Debug - Rayonnage: {rayonnage}, Étagère: {etagere}, Coût: {cost}")
                
                # Ajouter plus de debug avant l'envoi à add_material_from_excel
                print(f"Debug - Données envoyées :")
                print(f"  Rayonnage: '{rayonnage}'")
                print(f"  Étagère: '{etagere}'")
                print(f"  Description: '{description}'")
                print(f"  Coût: {cost}")
                
                success, message = add_material_from_excel(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    rayonnage=rayonnage,
                    etagere=etagere,
                    description=description,
                    providers=providers,
                    pn=pn,
                    order=order,
                    aquila=aquila,
                    pa28=pa28,
                    da40=da40,
                    sr20=sr20,
                    sr22=sr22,
                    quantity=quantity,
                    minimum=minimum,
                    h50=h50,
                    h100=h100,
                    h200=h200,
                    providers_actf=providers_actf,
                    cost=cost,
                    stock=stock,
                    remarks=remarks
                )
                
                if success:
                    success_count += 1
                    print(f"Matériel ajouté avec succès : {description}")
                else:
                    error_count += 1
                    print(f"Erreur lors de l'ajout du matériel {description} : {message}")
                    
            except Exception as e:
                error_count += 1
                print(f"Erreur lors du traitement de la ligne : {str(e)}")
                print(f"Ligne problématique : {row}")
        
        print("\nStatistiques d'importation :")
        print(f"Matériels ajoutés avec succès : {success_count}")
        print(f"Erreurs : {error_count}")
        print(f"Total traité : {success_count + error_count}")
        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {str(e)}")

def read_magasin_ods(file_path: str) -> Tuple[bool, str, List[Dict]]:
    """Lit le fichier ODS du magasin et retourne une liste de dictionnaires.
    
    Args:
        file_path (str): Chemin vers le fichier .ods
        
    Returns:
        Tuple[bool, str, List[Dict]]: 
            - bool: True si succès, False si erreur
            - str: Message de succès ou d'erreur
            - List[Dict]: Liste des matériels (vide si erreur)
    """
    try:
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return False, f"Le fichier {file_path} n'existe pas", []

        # Lire le fichier ODS avec pyexcel_ods
        data = pyexcel_ods.get_data(file_path)
        
        if not data:
            return False, "Le fichier est vide", []
            
        # Récupérer la première feuille
        sheet_name = list(data.keys())[0]
        rows = data[sheet_name]
        
        if len(rows) < 2:  # Au moins l'en-tête et une ligne de données
            return False, "Le fichier ne contient pas assez de lignes", []
            
        # Récupérer les en-têtes
        headers = [str(col).strip() for col in rows[0]]
        
        # Convertir les lignes en dictionnaires
        materials = []
        for row in rows[1:]:  # Ignorer l'en-tête
            # S'assurer que la ligne a assez de colonnes
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            
            material = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ''
                
                # Convertir les valeurs selon leur type
                if header in ['Quantity', 'Minimum']:
                    material[header] = convert_to_int(value)
                elif header in ['Cost_Estimate', 'Stock_Estimate_HT']:
                    material[header] = convert_to_float(value)
                elif header in ['AQUILA', 'PA28', 'DA40', 'SR20', 'SR22', '50H', '100H', '200H']:
                    material[header] = convert_to_bool(value)
                else:
                    material[header] = clean_string(value)
            
            materials.append(material)

        return True, f"{len(materials)} lignes trouvées", materials

    except Exception as e:
        print(f"Exception détaillée : {str(e)}")
        return False, f"Erreur lors de la lecture du fichier : {str(e)}", []

def import_materials_from_df(df: pd.DataFrame) -> Tuple[int, int, int]:
    """Importe les matériels depuis le DataFrame dans la base de données.
    
    Args:
        df (pd.DataFrame): DataFrame contenant les données à importer
        
    Returns:
        Tuple[int, int, int]: 
            - Nombre de matériels ajoutés avec succès
            - Nombre d'erreurs
            - Nombre total de lignes traitées
    """
    success_count = 0
    error_count = 0
    total_count = 0

    for index, row in df.iterrows():
        try:
            # Convertir la ligne en dictionnaire
            material_data = {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'rayonnage': str(row.get('Rayonnage', '')),
                'etagere': str(row.get('Etagere', '')),
                'description': str(row.get('Description', '')),
                'providers': str(row.get('Providers', '')),
                'pn': str(row.get('PN', '')),
                'order': str(row.get('Order', '')),
                'quantity': int(row.get('Quantity', 0)),
                'minimum': int(row.get('Minimum', 0)),
                'providers_actf': str(row.get('Providers_ACTF', '')),
                'cost': float(row.get('Cost_Estimate', 0.0)),
                'stock': float(row.get('Stock_Estimate_HT', 0.0)),
                'remarks': str(row.get('Remarks', '')),
                # Colonnes pour les avions (à adapter selon votre structure)
                'aquila': bool(row.get('AQUILA', False)),
                'pa28': bool(row.get('PA28', False)),
                'da40': bool(row.get('DA40', False)),
                'sr20': bool(row.get('SR20', False)),
                'sr22': bool(row.get('SR22', False)),
                # Colonnes pour la maintenance
                'h50': bool(row.get('50H', False)),
                'h100': bool(row.get('100H', False)),
                'h200': bool(row.get('200H', False))
            }

            # Ajouter le matériel
            success, message = add_material_from_excel(**material_data)
            
            if success:
                success_count += 1
                print(f"Matériel ajouté avec succès : {material_data['description']}")
            else:
                error_count += 1
                print(f"Erreur lors de l'ajout du matériel {material_data['description']} : {message}")

        except Exception as e:
            error_count += 1
            print(f"Erreur inattendue à la ligne {index + 2} : {str(e)}")
        
        total_count += 1

    return success_count, error_count, total_count

def main():
    """Fonction principale pour l'import des données."""
    file_path = os.path.join(current_dir, "MagasinV5c.ods")
    print(f"Lecture du fichier : {file_path}")
    
    # Utiliser directement import_from_ods au lieu de read_magasin_ods
    import_from_ods(file_path)

if __name__ == "__main__":
    main() 