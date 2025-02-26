import os
import hashlib
path = os.path.dirname(os.path.realpath(__file__))

def init (username, mdp, nom, prénom, mail, tel, admin):
    f = open(path+"/users.csv", "w")
    password = hashlib.sha256(mdp.encode()).hexdigest()
    f.write(f"{username};{password};{nom};{prénom};{mail};{tel};{admin};\n")
    f.close()

def snd (username, mdp, nom, prénom, mail, tel, admin):
    f = open(path+"/users.csv", "a")
    password = hashlib.sha256(mdp.encode()).hexdigest()
    f.write(f"{username};{password};{nom};{prénom};{mail};{tel};{admin};\n")
    f.close()    
    
    
init("jules.glt", "azerty", "Gillet", "Jules", "jules.gillet83@gmail.com", "0652003002", "False")
snd("thibault.dlb", "Epicier", "de Laubrière", "Thibault", "thibdelaub@outlook.fr", "0769145620", "True")


import sqlite3
import hashlib

def ajouter_utilisateur(username, password, name, firstname, email, tel, isAdmin):
    # Connexion à la base de données
    conn = sqlite3.connect("ressources/bdd_all.db")  # Mets le chemin correct si nécessaire
    cursor = conn.cursor()
    
    # Requête SQL pour insérer un utilisateur
    query = """INSERT INTO users (username, password, name, firstname, email, tel, isAdmin) 
               VALUES (?, ?, ?, ?, ?, ?, ?)"""
    
    try:
        hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(query, (username, hash, name, firstname, email, tel, isAdmin))
        conn.commit()  # Sauvegarde les modifications
        print("✅ Utilisateur ajouté avec succès !")
    except sqlite3.IntegrityError as e:
        print(f"❌ Erreur : {e}")  # Affiche le type d'erreur (ex: contrainte UNIQUE violée)
    
    # Fermeture de la connexion
    conn.close()

# Exemple d'utilisation
ajouter_utilisateur("thibault.dlb", "Epicier", "de Laubrière", "Thibault", "thibdelaub@outlook.fr", "0769145620", 1)
ajouter_utilisateur("jules.glt", "azerty", "Gillet", "Jules", "jules.gillet83@gmail.com", "0652003002", 0)