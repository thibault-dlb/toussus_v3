"""
Module utilitaire contenant les fonctionnalités de diagrammes et d'emails
pour l'application Méca'STUFF.
"""

# Imports de la bibliothèque standard
import io
import os
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Imports des bibliothèques tierces
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

def generer_diagrammes():
    """
    Génère les trois diagrammes statistiques.

    Returns:
        list: Liste des images des diagrammes générés en format BytesIO
    """
    diagrammes = []

    # Configuration des diagrammes
    diag_configs = [
        {
            'title': 'Proportion des types de pièces',
            'labels': ['Type A', 'Type B', 'Type C'],
            'values': [30, 45, 25]
        },
        {
            'title': 'Ratio de disponibilité des pièces',
            'labels': ['Disponible', 'Indisponible'],
            'values': [70, 30]
        },
        {
            'title': 'Consommation de pièces par avion',
            'labels': ['Avion 1', 'Avion 2', 'Avion 3', 'Avion 4', 'Avion 5'],
            'values': [30, 25, 20, 15, 10]
        }
    ]

    # Génération des diagrammes
    for config in diag_configs:
        plt.figure(figsize=(8, 6))
        plt.pie(config['values'], labels=config['labels'], autopct='%1.1f%%')
        plt.title(config['title'])

        img = io.BytesIO()
        plt.savefig(img, format='png')
        plt.close()
        diagrammes.append(img)

    return diagrammes


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

    def get_last_send_date(self):
        """
        Récupère la date du dernier envoi de mail depuis le fichier config.csv.

        Returns:
            str: Date du dernier envoi ou message par défaut
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Recherche de la ligne 'last_send_date'
                for i, line in enumerate(lines):
                    if line.strip() == 'last_send_date':
                        if i + 1 < len(lines):
                            return lines[i + 1].strip()
                return "Aucun envoi précédent"
        except FileNotFoundError:
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
        Sauvegarde la date d'envoi et le destinataire dans config.csv.

        Args:
            destinataire (str): Adresse email du destinataire

        Returns:
            str: Date actuelle au format JJ/MM/AAAA à HH:MM
        """
        current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        try:
            # Lecture du fichier existant
            lines = []
            date_found = False
            recipient_found = False
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Mise à jour des valeurs existantes
                i = 0
                while i < len(lines):
                    if lines[i].strip() == 'last_send_date':
                        lines[i + 1] = current_date + '\n'
                        date_found = True
                        i += 2
                    elif lines[i].strip() == 'last_recipient':
                        lines[i + 1] = destinataire + '\n'
                        recipient_found = True
                        i += 2
                    else:
                        i += 1
            
            # Ajout des nouvelles valeurs si non trouvées
            if not date_found:
                lines.extend(['last_send_date\n', current_date + '\n'])
            if not recipient_found:
                lines.extend(['last_recipient\n', destinataire + '\n'])
            
            # Écriture du fichier
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            return current_date
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des informations : {str(e)}")
            return current_date

    def envoie_mail(self, destinataire, objet, contenu, avec_diagrammes=False):
        """
        Envoie un email via SMTP.

        Args:
            destinataire (str): Adresse email du destinataire
            objet (str): Objet du mail
            contenu (str): Contenu du mail
            avec_diagrammes (bool): Si True, inclut les diagrammes statistiques

        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        try:
            message = self._create_message(destinataire, objet, contenu)

            if avec_diagrammes:
                self._attach_diagrams(message)

            success = self._send_message(message, avec_diagrammes)
            
            if success:
                self.save_last_send_info(destinataire)
                
            return success

        except Exception as e:
            print(f"Erreur lors de l'envoi du mail : {str(e)}")
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
        Crée le contenu HTML du message.

        Args:
            contenu (str): Contenu du message

        Returns:
            str: Contenu formaté en HTML
        """
        return f"""
        <html>
            <body>
                <p>{contenu.replace('\n', '<br>')}</p>
                <br>
                <p>Cordialement,</p>
                <img src="https://drive.google.com/uc?export=view&id=18g47sUPXEQ4enbYHXf8rBVO7GAIewIBz"
                     alt="Signature"
                     style="width: 200px;">
                <br>
                <p>Méca'STUFF</p>
            </body>
        </html>
        """

    def _attach_diagrams(self, message):
        """
        Attache les diagrammes au message.

        Args:
            message (MIMEMultipart): Message auquel ajouter les diagrammes
        """
        diagrammes = generer_diagrammes()
        for i, img_data in enumerate(diagrammes, 1):
            img_data.seek(0)
            image = MIMEImage(img_data.read(), _subtype="png")
            image.add_header('Content-ID', f'<image{i}>')
            image.add_header(
                'Content-Disposition',
                'inline',
                filename=f'diagramme{i}.png'
            )
            message.attach(image)

    def _send_message(self, message, avec_diagrammes):
        """
        Envoie le message via SMTP.

        Args:
            message (MIMEMultipart): Message à envoyer
            avec_diagrammes (bool): Si True, sauvegarde la date d'envoi

        Returns:
            bool: True si l'envoi a réussi, False sinon
        """
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.expediteur, self.mot_de_passe)
            server.send_message(message)

            if avec_diagrammes:
                self.save_last_send_info(message["To"])

            return True


# Instance globale
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