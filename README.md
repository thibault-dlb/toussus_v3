# Méca'stuff

Application de gestion de stock pour le matériel de maintenance aéronautique.

## Installation rapide (Version exécutable)

Si vous avez téléchargé la version exécutable (.exe) :
1. Aucune installation n'est requise
2. Double-cliquez simplement sur le fichier `app.exe` pour lancer l'application

## Description

Méca'stuff est une application de bureau développée en Python qui permet de gérer efficacement le stock de pièces et de matériel de maintenance aéronautique. Elle offre une interface graphique intuitive pour suivre l'inventaire, gérer les commandes et maintenir une traçabilité complète du matériel.

## Fonctionnalités principales

- 🔐 Système d'authentification sécurisé avec gestion des droits administrateurs
- ✈️ Gestion des avions et association des pièces
- 📦 Suivi complet du stock (ajout, retrait, recherche)
- 📊 Statistiques et rapports détaillés
- 📧 Export et envoi de rapports par email
- 🎨 Interface moderne avec support des thèmes clair/sombre
- 🔄 Maintenance préventive (50h, 100h, 200h)

## Installation développeur

### Prérequis

- Python 3.8 ou supérieur
- Bibliothèques Python requises :
  - customtkinter
  - Pillow
  - sqlite3 (inclus dans Python)

### Installation des dépendances

Installez les bibliothèques requises en exécutant les commandes suivantes dans l'invite de commandes (cmd) :
```bash
pip install customtkinter
pip install Pillow
```

## Structure du projet (principale)

```toussus_v3/
├── app.py             # Application principale
├── ressources/        # Ressources et modules
│   ├── allinfos.py    # Configuration globale
│   ├── bdd_users.py   # Gestion des utilisateurs
│   ├── manip_bd.py    # Manipulation de la base de données
│   └── request_bd.py  # Requêtes base de données
└── README.md          # Documentation
```

## Utilisation

1. Lancez l'application
2. Connectez-vous avec vos identifiants
3. Accédez aux différentes fonctionnalités via le menu principal :
   - Ajout/retrait de matériel
   - Recherche dans l'inventaire
   - Gestion des avions
   - Statistiques et rapports
   - Paramètres utilisateur

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## Licence

Ce projet est sous licence privée. Tous droits réservés.

## Contact

Pour toute question, suggestion ou signalement de bugs, veuillez contacter l'équipe de développement à l'adresse suivante : thibdelaub@outlook.fr.

