"""
Module de manipulation de la base de données.

Ce module gère les opérations d'écriture dans la base de données.
"""

import os
import sqlite3
import re
import time
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from ressources.request_bd import db

# Constantes de sécurité
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 1000
MAX_PROVIDER_LENGTH = 200
MAX_PN_LENGTH = 50
MAX_ORDER_LENGTH = 50
MAX_QUANTITY = 10000
MIN_QUANTITY = 0
MAX_COST = 1000000.0
MIN_COST = 0.0
DB_TIMEOUT = 30
MAX_RETRIES = 3
MAX_BATCH_SIZE = 100

# Expression régulière pour la validation des noms d'avions
PLANE_NAME_PATTERN = re.compile(r'^[A-Z0-9-]{2,}$')

# Expressions régulières pour la validation des autres champs
PN_PATTERN = re.compile(r'^[A-Z0-9-]+$')
ORDER_PATTERN = re.compile(r'^[A-Z0-9-]+$')
PROVIDER_PATTERN = re.compile(r'^[A-Za-z0-9\s\-\.]+$')

# Chemin absolu du dossier ressources
RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))

class ValidationError(Exception):
    """Exception personnalisée pour les erreurs de validation."""
    pass

def validate_field(
    value: str,
    pattern: re.Pattern,
    field_name: str,
    max_length: int
) -> None:
    """Valide un champ selon un pattern et une longueur maximale.
    
    Args:
        value: Valeur à valider
        pattern: Pattern de validation
        field_name: Nom du champ pour le message d'erreur
        max_length: Longueur maximale autorisée
        
    Raises:
        ValidationError: Si la valeur est invalide
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"Le champ {field_name} doit être une chaîne de caractères"
        )
    if not value.strip():
        raise ValidationError(
            f"Le champ {field_name} ne peut pas être vide"
        )
    if len(value) > max_length:
        raise ValidationError(
            f"Le champ {field_name} est trop long "
            f"(max {max_length} caractères)"
        )
    if not pattern.match(value):
        raise ValidationError(
            f"Le champ {field_name} contient des caractères invalides"
        )

def validate_numeric(
    value: float,
    min_value: float,
    max_value: float,
    field_name: str
) -> None:
    """Valide une valeur numérique.
    
    Args:
        value: Valeur à valider
        min_value: Valeur minimale autorisée
        max_value: Valeur maximale autorisée
        field_name: Nom du champ pour le message d'erreur
        
    Raises:
        ValidationError: Si la valeur est invalide
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"Le champ {field_name} doit être un nombre")
    if value < min_value or value > max_value:
        raise ValidationError(
            f"Le champ {field_name} doit être entre {min_value} et {max_value}"
        )

def validate_plane_name(name: str) -> Tuple[bool, str]:
    """Valide le nom d'un avion.
    
    Args:
        name: Nom de l'avion à valider
        
    Returns:
        Tuple[bool, str]: (True si valide, message d'erreur sinon)
    """
    try:
        validate_field(
            name,
            PLANE_NAME_PATTERN,
            "nom de l'avion",
            MAX_NAME_LENGTH
        )
        return True, ""
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Erreur lors de la validation : {str(e)}"

def get_db_connection() -> Optional[sqlite3.Connection]:
    """Établit une connexion sécurisée à la base de données.
    
    Returns:
        Optional[sqlite3.Connection]: Connexion à la base de données ou None si erreur
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            db_path = os.path.join(RESOURCES_PATH, "bdd_all.db")
            
            if not os.path.exists(db_path):
                print(f"La base de données n'existe pas : {db_path}")
                return None
                
            if not os.access(db_path, os.W_OK):
                print(
                    f"La base de données n'est pas accessible en écriture : {db_path}"
                )
                return None
            
            conn = sqlite3.connect(db_path, timeout=DB_TIMEOUT)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            
            return conn
            
        except sqlite3.Error as e:
            print(f"Tentative {retries + 1}/{MAX_RETRIES} - Erreur : {str(e)}")
            retries += 1
            if retries < MAX_RETRIES:
                time.sleep(1)
    
    print(f"Échec de connexion après {MAX_RETRIES} tentatives")
    return None

def check_plane_exists(name: str) -> bool:
    """Vérifie si un avion existe déjà dans la base de données.
    
    Args:
        name: Nom de l'avion à vérifier
        
    Returns:
        bool: True si l'avion existe, False sinon
    """
    try:
        valid, message = validate_plane_name(name)
        if not valid:
            print(f"Validation du nom d'avion échouée : {message}")
            return False
        
        return db.check_plane_exists(name)
        
    except Exception as e:
        print(f"Erreur lors de la vérification de l'avion : {str(e)}")
        return False

def ajout_plane(name: str) -> Tuple[bool, str]:
    """Ajoute un nouvel avion à la table planes.
    
    Args:
        name: Nom de l'avion à ajouter
        
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    conn = None
    try:
        valid, message = validate_plane_name(name)
        if not valid:
            raise ValidationError(message)
            
        if db.check_plane_exists(name):
            print(f"Tentative d'ajout d'un avion existant : {name}")
            return False, "Cet avion existe déjà dans la base de données"
            
        conn = get_db_connection()
        if conn is None:
            return False, "Impossible de se connecter à la base de données"
            
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO planes ("name", created_at) 
            VALUES (?, CURRENT_TIMESTAMP)
            ''',
            (name,)
        )
        
        if cursor.rowcount != 1:
            conn.rollback()
            print(f"Échec de l'insertion de l'avion : {name}")
            return False, "Échec de l'insertion dans la base de données"
        
        conn.commit()
        print(f"Avion ajouté avec succès : {name}")
        return True, "Avion ajouté avec succès"
        
    except ValidationError as e:
        print(f"Erreur de validation pour l'avion {name}: {str(e)}")
        return False, str(e)
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité pour l'avion {name}: {str(e)}")
        return False, "Cet avion existe déjà dans la base de données"
    except Exception as e:
        print(
            f"Erreur inattendue lors de l'ajout de l'avion {name}: "
            f"{str(e)}"
        )
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False, f"Erreur lors de l'ajout de l'avion : {str(e)}"
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def ajouter_relations_piece_avions(
    piece_id: int,
    plane_ids: list[int]
) -> Tuple[bool, str]:
    """Ajoute des relations entre une pièce et plusieurs avions.
    
    Args:
        piece_id: ID de la pièce
        plane_ids: Liste des IDs des avions
        
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    conn = None
    try:
        if not isinstance(piece_id, int) or piece_id <= 0:
            raise ValidationError(
                "L'ID de la pièce doit être un entier positif"
            )
        
        if not isinstance(plane_ids, list) or not plane_ids:
            raise ValidationError(
                "La liste des IDs d'avions ne peut pas être vide"
            )
            
        if len(plane_ids) > MAX_BATCH_SIZE:
            raise ValidationError(
                f"Trop de relations à ajouter (maximum {MAX_BATCH_SIZE})"
            )
            
        for plane_id in plane_ids:
            if not isinstance(plane_id, int) or plane_id <= 0:
                raise ValidationError(
                    "Tous les IDs d'avions doivent être des entiers positifs"
                )
        
        conn = get_db_connection()
        if conn is None:
            return False, "Impossible de se connecter à la base de données"
            
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM magasin WHERE id = ?", (piece_id,))
        if not cursor.fetchone():
            return False, f"La pièce avec l'ID {piece_id} n'existe pas"
            
        for plane_id in plane_ids:
            cursor.execute("SELECT 1 FROM planes WHERE id = ?", (plane_id,))
            if not cursor.fetchone():
                return False, f"L'avion avec l'ID {plane_id} n'existe pas"
        
        for plane_id in plane_ids:
            try:
                cursor.execute(
                    '''
                    INSERT INTO planes_magasin (
                        magasin_id,
                        plane_id,
                        created_at
                    ) VALUES (?, ?, CURRENT_TIMESTAMP)
                    ''',
                    (piece_id, plane_id)
                )
            except sqlite3.IntegrityError:
                conn.rollback()
                return False, (
                    f"La relation entre la pièce {piece_id} "
                    f"et l'avion {plane_id} existe déjà"
                )
        
        conn.commit()
        return True, f"Relations ajoutées avec succès pour la pièce {piece_id}"
        
    except ValidationError as e:
        print(f"Erreur de validation: {str(e)}")
        return False, str(e)
    except Exception as e:
        print(f"Erreur inattendue lors de l'ajout des relations: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False, f"Erreur lors de l'ajout des relations : {str(e)}"
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

def ajouter_materiel(
    rayonnage: str,
    etagere: str,
    description: str,
    providers: str,
    pn: str,
    order: str,
    quantity: int,
    minimum: int,
    h50: int,
    h100: int,
    h200: int,
    providers_actf: str,
    cost_estimate: int,
    stock_estimate_ht: int,
    remarks: str,
    plane_ids: list[int]
) -> Tuple[bool, str]:
    """Ajoute un nouveau matériel et crée les relations avec les avions.
    
    Args:
        rayonnage: Position rayonnage
        etagere: Position étagère
        description: Description de la pièce
        providers: Fournisseurs
        pn: Part Number
        order: Numéro de commande
        quantity: Quantité en stock
        minimum: Stock minimum
        h50: Maintenance 50H
        h100: Maintenance 100H
        h200: Maintenance 200H ou annuelle
        providers_actf: Fournisseurs ACTF
        cost_estimate: Estimation du coût
        stock_estimate_ht: Estimation du stock HT
        remarks: Remarques
        plane_ids: Liste des IDs des avions associés
        
    Returns:
        Tuple[bool, str]: (succès, message)
    """
    conn = None
    try:
        # Génération automatique du numéro au format [YY][semaine]
        import datetime as dt
        now = dt.datetime.now()
        year_suffix = str(now.year)[-2:]  # Deux derniers chiffres de l'année
        week_number = now.isocalendar()[1]  # Numéro de la semaine
        week_str = f"{week_number:02d}"  # Format sur 2 chiffres
        numero = f"{year_suffix}{week_str}"
        
        if (not isinstance(quantity, int) or
                quantity < MIN_QUANTITY or
                quantity > MAX_QUANTITY):
            raise ValidationError(
                f"La quantité doit être entre {MIN_QUANTITY} et {MAX_QUANTITY}"
            )
            
        if (not isinstance(minimum, int) or
                minimum < MIN_QUANTITY or
                minimum > MAX_QUANTITY):
            raise ValidationError(
                f"Le stock minimum doit être entre "
                f"{MIN_QUANTITY} et {MAX_QUANTITY}"
            )
            
        validate_field(pn, PN_PATTERN, "PN", MAX_PN_LENGTH)
        validate_field(order, ORDER_PATTERN, "Order", MAX_ORDER_LENGTH)
        validate_field(
            providers,
            PROVIDER_PATTERN,
            "Providers",
            MAX_PROVIDER_LENGTH
        )
        
        conn = get_db_connection()
        if conn is None:
            return False, "Impossible de se connecter à la base de données"
            
        cursor = conn.cursor()
        
        cursor.execute(
            '''
            INSERT INTO magasin (
                Numero, Rayonnage, Etagere, Description, Providers,
                PN, "Order", Quantity, Minimum, "50H", "100H",
                "200H_ou_annuelle", Providers_ACTF, Cost_Estimate,
                Stock_Estimate_HT, Remarks, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
            )
            ''',
            (
                numero, rayonnage, etagere, description, providers,
                pn, order, quantity, minimum, h50, h100,
                h200, providers_actf, cost_estimate,
                stock_estimate_ht, remarks
            )
        )
        
        piece_id = cursor.lastrowid
        
        if plane_ids:
            success, message = ajouter_relations_piece_avions(
                piece_id,
                plane_ids
            )
            if not success:
                conn.rollback()
                return False, (
                    f"Erreur lors de l'ajout des relations avions : {message}"
                )
        
        conn.commit()
        return True, f"Matériel ajouté avec succès (ID: {piece_id})"
        
    except ValidationError as e:
        print(f"Erreur de validation: {str(e)}")
        return False, str(e)
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False, "Une contrainte d'unicité n'a pas été respectée"
    except Exception as e:
        print(f"Erreur inattendue lors de l'ajout du matériel: {str(e)}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False, f"Erreur lors de l'ajout du matériel : {str(e)}"
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python manip_bd.py <nom_avion>")
        sys.exit(1)
        
    success, message = ajout_plane(sys.argv[1])
    print(message)
    sys.exit(0 if success else 1)
