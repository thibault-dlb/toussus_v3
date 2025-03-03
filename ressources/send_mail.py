"""
Module utilitaire contenant les fonctionnalités de diagrammes et d'emails
pour l'application Méca'STUFF.
"""

# Imports de la bibliothèque standard
import io
import os
import json
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from smtplib import SMTPException
import ssl

# Imports des bibliothèques tierces
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

class EmailError(Exception):
    """Exception personnalisée pour les erreurs d'envoi d'email."""
    pass

def generer_diagrammes():
    """
    Génère les trois diagrammes statistiques.

    Returns:
        list: Liste des images des diagrammes générés en format BytesIO
    """
    diagrammes = []
    
    try:
        # Configuration du style matplotlib
        plt.style.use('default')
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'font.size': 8,  # Réduction de la taille de police
            'font.family': 'sans-serif'
        })

        # Configuration des diagrammes
        diag_configs = [
            {
                'title': 'Proportion des types de pièces',
                'labels': ['Type A', 'Type B', 'Type C'],
                'values': [30, 45, 25],
                'colors': ['#FF9999', '#66B2FF', '#99FF99']
            },
            {
                'title': 'Ratio de disponibilité des pièces',
                'labels': ['Disponible', 'Indisponible'],
                'values': [70, 30],
                'colors': ['#99FF99', '#FF9999']
            },
            {
                'title': 'Consommation de pièces par avion',
                'labels': ['Avion 1', 'Avion 2', 'Avion 3', 'Avion 4', 'Avion 5'],
                'values': [30, 25, 20, 15, 10],
                'colors': ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC']
            }
        ]

        for config in diag_configs:
            # Création d'une nouvelle figure avec un fond blanc - taille réduite
            fig, ax = plt.subplots(figsize=(5, 3.5), facecolor='white')
            
            # Configuration du graphique en camembert
            wedges, texts, autotexts = ax.pie(
                config['values'],
                labels=config['labels'],
                autopct='%1.1f%%',
                colors=config['colors'],
                shadow=True,
                startangle=90,
                explode=[0.05] * len(config['values'])
            )
            
            # Personnalisation du texte - taille réduite
            plt.setp(autotexts, size=7, weight="bold")
            plt.setp(texts, size=7)
            
            # Ajout du titre - taille réduite
            ax.set_title(config['title'], pad=10, size=9, weight='bold')

            # Sauvegarde de l'image avec DPI réduit
            img = io.BytesIO()
            plt.savefig(img, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            img.seek(0)
            diagrammes.append(img)

        return diagrammes
    except Exception as e:
        print(f"Erreur lors de la génération des diagrammes : {str(e)}")
        messagebox.showerror("Erreur", f"Erreur lors de la génération des diagrammes : {str(e)}")
        return []

class EmailManager:
    """Gestionnaire d'envoi d'emails."""

    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        """
        Initialise le gestionnaire d'emails.

        Args:
            smtp_server (str): Adresse du serveur SMTP
            smtp_port (int): Port du serveur SMTP
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.expediteur = "jules.gillet83@gmail.com"
        self.mot_de_passe = "natw uorn wqsv gaix"
        self.config_file = os.path.join(os.path.dirname(__file__), "config.csv")
        self.last_send_file = os.path.join(os.path.dirname(__file__), "last_send_date.json")

    def get_last_send_date(self):
        """
        Récupère la date du dernier envoi de mail depuis le fichier JSON.

        Returns:
            str: Date du dernier envoi ou message par défaut
        """
        try:
            if os.path.exists(self.last_send_file):
                with open(self.last_send_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('last_send_date', "Aucun envoi précédent")
            return "Aucun envoi précédent"
        except Exception as e:
            print(f"Erreur lors de la lecture de la date : {str(e)}")
            return "Aucun envoi précédent"

    def get_last_recipient(self):
        """
        Récupère le dernier destinataire depuis le fichier config.csv.

        Returns:
            str: Dernier destinataire ou chaîne vide
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Recherche de la ligne 'last_recipient'
                for i, line in enumerate(lines):
                    if line.strip() == 'last_recipient':
                        if i + 1 < len(lines):
                            return lines[i + 1].strip()
                return ""
        except FileNotFoundError:
            return ""
        except Exception as e:
            print(f"Erreur lors de la lecture du destinataire : {str(e)}")
            return ""

    def save_last_send_info(self, destinataire):
        """
        Sauvegarde la date d'envoi dans le fichier JSON.

        Args:
            destinataire (str): Adresse email du destinataire

        Returns:
            str: Date actuelle au format JJ/MM/AAAA à HH:MM
        """
        current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        data = {
            'last_send_date': current_date,
            'last_recipient': destinataire
        }
        
        try:
            with open(self.last_send_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            return current_date
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des informations : {str(e)}")
            return current_date

    def envoie_mail(self, destinataire, objet, contenu, avec_diagrammes=False):
        """
        Envoie un email via SMTP avec gestion des erreurs améliorée.

        Args:
            destinataire (str): Adresse email du destinataire
            objet (str): Objet du mail
            contenu (str): Contenu du mail
            avec_diagrammes (bool): Si True, inclut les diagrammes statistiques

        Returns:
            bool: True si l'envoi a réussi, False sinon

        Raises:
            EmailError: En cas d'erreur lors de l'envoi
        """
        try:
            message = self._create_message(destinataire, objet, contenu)

            if avec_diagrammes:
                diagrammes = generer_diagrammes()
                if not diagrammes:
                    raise EmailError("Erreur lors de la génération des diagrammes")
                self._attach_diagrams(message, diagrammes)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.expediteur, self.mot_de_passe)
                server.send_message(message)

            self.save_last_send_info(destinataire)
            return True

        except SMTPException as e:
            error_msg = f"Erreur SMTP lors de l'envoi : {str(e)}"
            messagebox.showerror("Erreur d'envoi", error_msg)
            return False
        except Exception as e:
            error_msg = f"Erreur inattendue lors de l'envoi : {str(e)}"
            messagebox.showerror("Erreur", error_msg)
            return False

    def _create_message(self, destinataire, objet, contenu):
        """
        Crée le message email avec le contenu HTML.

        Args:
            destinataire (str): Adresse email du destinataire
            objet (str): Objet du mail
            contenu (str): Contenu du mail

        Returns:
            MIMEMultipart: Message email formaté
        """
        message = MIMEMultipart('related')
        message["From"] = self.expediteur
        message["To"] = destinataire
        message["Subject"] = objet

        last_send_date = self.get_last_send_date()
        contenu_complet = f"{contenu}\n\nDernier rapport envoyé le : {last_send_date}"

        html_content = self._create_html_content(contenu_complet)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)

        return message

    def _create_html_content(self, contenu):
        """
        Crée le contenu HTML du message avec un style moderne.

        Args:
            contenu (str): Contenu du message

        Returns:
            str: Contenu formaté en HTML
        """
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background-color: #007bff;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .content {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .footer {{
                    margin-top: 30px;
                    padding: 20px;
                    border-top: 2px solid #dee2e6;
                    text-align: center;
                    font-size: 0.9em;
                    color: #6c757d;
                }}
                .signature {{
                    margin-top: 30px;
                    padding: 20px;
                    border-top: 1px solid #dee2e6;
                }}
                .logo {{
                    max-width: 200px;
                    height: auto;
                    margin-top: 20px;
                }}
                h3, h4 {{
                    color: #007bff;
                }}
                ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                li {{
                    margin: 10px 0;
                    padding-left: 20px;
                    position: relative;
                }}
                li:before {{
                    content: "•";
                    color: #007bff;
                    font-weight: bold;
                    position: absolute;
                    left: 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Méca'STUFF - Rapport</h2>
            </div>
            <div class="content">
                {contenu.replace('\n', '<br>')}
            </div>
            <div class="signature">
                <p>Cordialement,</p>
                <img src="https://drive.google.com/uc?export=view&id=18g47sUPXEQ4enbYHXf8rBVO7GAIewIBz"
                     alt="Signature"
                     class="logo">
                <p>Méca'STUFF</p>
            </div>
            <div class="footer">
                <p>Ce message a été généré automatiquement par Méca'STUFF</p>
                <p>© {datetime.now().year} Méca'STUFF - Tous droits réservés</p>
            </div>
        </body>
        </html>
        """

    def _attach_diagrams(self, message, diagrammes):
        """
        Attache les diagrammes au message.

        Args:
            message (MIMEMultipart): Message auquel ajouter les diagrammes
            diagrammes (list): Liste des images des diagrammes
        """
        for i, img_data in enumerate(diagrammes, 1):
            img_data.seek(0)
            image = MIMEImage(img_data.read())
            image.add_header('Content-ID', f'<image{i}>')
            image.add_header(
                'Content-Disposition',
                'inline',
                filename=f'diagramme{i}.png'
            )
            message.attach(image)

    def envoyer_email(self, destinataire: str, sujet: str, corps: str, piece_jointe: str):
        """Envoie un email avec une pièce jointe.
        
        Args:
            destinataire (str): Adresse email du destinataire
            sujet (str): Sujet de l'email
            corps (str): Corps de l'email
            piece_jointe (str): Chemin du fichier à joindre
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.expediteur
            message["To"] = destinataire
            message["Subject"] = sujet

            message.attach(MIMEText(corps, "plain"))

            with open(piece_jointe, "rb") as attachment:
                part = MIMEImage(attachment.read(), Name=os.path.basename(piece_jointe))
                part["Content-Disposition"] = f'attachment; filename="{os.path.basename(piece_jointe)}"'
                message.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(self.expediteur, self.mot_de_passe)
                server.send_message(message)

            print(f"Email envoyé à {destinataire}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {str(e)}")

    def envoyer_rapport_statistiques(self, destinataire: str):
        """
        Envoie un rapport statistique complet par email.

        Args:
            destinataire (str): Adresse email du destinataire
        """
        try:
            rapport = self.generer_rapport_statistiques()
            sujet = "Rapport statistique Méca'STUFF"
            
            success = self.envoie_mail(
                destinataire=destinataire,
                objet=sujet,
                contenu=rapport,
                avec_diagrammes=True
            )
            
            if success:
                messagebox.showinfo(
                    "Succès",
                    f"Le rapport a été envoyé avec succès à {destinataire}"
                )
            
        except EmailError as e:
            messagebox.showerror(
                "Erreur",
                f"Impossible d'envoyer le rapport : {str(e)}"
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Une erreur inattendue est survenue : {str(e)}"
            )

    def generer_rapport_statistiques(self):
        """
        Génère le contenu du rapport statistique.

        Returns:
            str: Contenu formaté du rapport
        """
        try:
            return f"""
            <h3>Rapport statistique Méca'STUFF</h3>
            
            <h4>1. Vue d'ensemble</h4>
            <p>Ce rapport présente une analyse détaillée de l'état actuel du stock et de son utilisation.</p>
            
            <h4>2. Répartition des pièces</h4>
            <p>Le premier graphique montre la répartition des différents types de pièces dans notre inventaire.</p>
            <img src="cid:image1" style="max-width: 100%; height: auto; margin: 20px 0;">
            
            <h4>3. Disponibilité du stock</h4>
            <p>Le deuxième graphique présente le ratio entre les pièces disponibles et indisponibles.</p>
            <img src="cid:image2" style="max-width: 100%; height: auto; margin: 20px 0;">
            
            <h4>4. Utilisation par avion</h4>
            <p>Le troisième graphique illustre la consommation de pièces par type d'avion.</p>
            <img src="cid:image3" style="max-width: 100%; height: auto; margin: 20px 0;">
            
            <h4>5. Recommandations</h4>
            <ul>
                <li>Surveiller les pièces dont le stock est bas</li>
                <li>Planifier les commandes en fonction des statistiques d'utilisation</li>
                <li>Optimiser la gestion des pièces les plus utilisées</li>
            </ul>
            """
        except Exception as e:
            print(f"Erreur lors de la génération du rapport : {str(e)}")
            return "Erreur lors de la génération du rapport statistique."

# Création d'une instance globale du gestionnaire d'emails
global_email_manager = EmailManager()

def envoyer_rapport_statistiques(destinataire="jules.gillet83@gmail.com"):
    """
    Envoie un rapport par email avec les diagrammes statistiques.

    Args:
        destinataire (str): Adresse email du destinataire

    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    contenu = """
Bonjour,

Veuillez trouver ci-joint le rapport statistique du matériel Méca'STUFF.

Les diagrammes joints présentent :
1. La proportion des différents types de pièces
2. Le ratio de pièces disponibles/indisponibles
3. La consommation de pièces par avion depuis le dernier rapport
"""

    success = global_email_manager.envoie_mail(
        destinataire=destinataire,
        objet="Rapport statistique Méca'STUFF",
        contenu=contenu,
        avec_diagrammes=True
    )
    
    root = tk.Tk()
    root.withdraw()  # Cacher la fenêtre principale de Tkinter
    
    if success:
        messagebox.showinfo("Succès", "Le mail a été envoyé avec succès.")
    else:
        messagebox.showerror("Échec", "Échec de l'envoi du mail.")
    
    return success