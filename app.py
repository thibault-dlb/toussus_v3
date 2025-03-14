"""Application de gestion de matériel ATCF parts.

Ce module contient l'interface graphique principale de l'application,
incluant la fenêtre de connexion et le menu principal.
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List, Union

import customtkinter as ctk
import hashlib
import sqlite3
from PIL import Image, ImageTk
from tkinter import messagebox
import matplotlib.pyplot as plt
import pygame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ressources import allinfos as infos
from ressources import bdd_users
from ressources import manip_bd
from ressources.request_bd import db
from ressources.send_mail import global_email_manager

# Initialisation de pygame pour la musique
pygame.mixer.init()

# Configurer la gestion des erreurs
def log_error(error_type, error_value, error_traceback):
    with open('error_log.txt', 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Type: {error_type.__name__}\n")
        f.write(f"Message: {str(error_value)}\n")
        f.write("Traceback:\n")
        f.write(''.join(traceback.format_tb(error_traceback)))
        f.write(f"\n{'='*50}\n")

sys.excepthook = log_error

class SignUpFrame(ctk.CTk):
    """Fenêtre de connexion de l'application.
    
    Cette classe gère l'interface de connexion utilisateur avec
    les champs nom d'utilisateur et mot de passe.
    """

    def __init__(self):
        """Initialise la fenêtre de connexion."""
        super().__init__()
        
        # Configuration de base de la fenêtre
        self.title(f"{infos.NAME_MAIN} - Connexion")
        self.geometry("300x300")  # Taille fixe de 300x300 pixels
        
        # Chargement de l'icône de l'application
        self.icon_path = infos.ICON_PATH
        if not os.path.exists(self.icon_path):
            print("Erreur : Le fichier de l'icône n'existe pas.")
        else:
            self.iconbitmap(self.icon_path)
        
        # Variable pour gérer l'affichage du mot de passe (visible/masqué)
        self.password_visible = False
        
        # --- Création des widgets de l'interface ---
        
        # Champ nom d'utilisateur
        self.label_main = ctk.CTkLabel(self, text="Nom d'utilisateur")
        self.ctrl_main = ctk.CTkEntry(self)
        
        # Champ mot de passe avec bouton de visibilité
        self.label_snd = ctk.CTkLabel(self, text="Mot de passe")
        self.password_frame = ctk.CTkFrame(self)
        self.ctrl_snd = ctk.CTkEntry(self.password_frame, show="*")  # Le mot de passe est masqué par défaut
        self.show_password = ctk.CTkButton(
            self.password_frame, 
            text="👁",  # Icône œil pour la visibilité
            width=30, 
            command=self.toggle_password_visibility
        )
        
        # Organisation des widgets du mot de passe
        self.ctrl_snd.pack(side="left", padx=(0,5))
        self.show_password.pack(side="left")
        
        # Bouton de connexion
        self.btn_next = ctk.CTkButton(self, text="Suivant", command=self.on_next)
        
        # Gestion des événements
        self.ctrl_snd.bind("<Return>", self.on_return)  # Touche Entrée pour se connecter
        self._focus_after_id = self.after(100, lambda: self.ctrl_main.focus_set())  # Focus automatique
        
        # --- Placement des widgets dans la fenêtre ---
        self.label_main.pack(pady=10)
        self.ctrl_main.pack(pady=10)
        self.label_snd.pack(pady=10)
        self.password_frame.pack(pady=10)
        self.btn_next.pack(pady=10)
       
        # Lancement de la boucle principale
        self.mainloop()
    
    def toggle_password_visibility(self):
        """Bascule l'affichage du mot de passe entre visible et masqué."""
        self.password_visible = not self.password_visible
        self.ctrl_snd.configure(show="" if self.password_visible else "*")
        self.show_password.configure(text="🔒" if self.password_visible else "👁")
    
    def on_next(self):
        """Gère l'action du bouton suivant."""
        self.check_connexion()
    
    def on_return(self, event):
        """Gère l'appui sur la touche Entrée.
        
        Args:
            event: L'événement de touche pressée.
        """
        self.after(10, self.on_next)
    
    def check_connexion(self):
        """Vérifie les identifiants de connexion et ouvre le menu principal si valides."""
        username = self.ctrl_main.get()
        password = self.ctrl_snd.get()
        
        # Utilisation de la fonction check_co de bdd_users
        success, message, user_data = bdd_users.check_co(username, password)
        
        if success:
            print(f"Connexion réussie pour {user_data['firstname']}")
            print(f"Admin : {user_data['isAdmin']}")
            # On quitte la boucle principale avant de détruire
            self.quit()
            # On détruit la fenêtre
            self._safe_destroy()
            # Création et affichage du menu principal
            main_menu = MainMenu(
                user_data['username'],
                user_data['firstname'],
                user_data['isAdmin']
            )
            main_menu.mainloop()
        else:
            messagebox.showerror("Erreur", message)
    
    def _safe_destroy(self):
        """Détruit proprement la fenêtre en annulant les tâches en attente."""
        if hasattr(self, '_focus_after_id'):
            self.after_cancel(self._focus_after_id)
        try:
            self.destroy()
        except Exception as e:
            print(f"Erreur lors de la destruction de la fenêtre : {e}")

class MainMenu(ctk.CTk):
    """Menu principal de l'application.
    
    Cette classe gère l'interface principale de l'application avec
    un système d'onglets et différentes fonctionnalités.
    """

    def __init__(self, username, first_name, isAdmin):
        """Initialise le menu principal."""
        assert isinstance(username, str), "Le nom d'utilisateur doit être une chaîne"
        assert isinstance(first_name, str), "Le prénom doit être une chaîne"
        assert isinstance(isAdmin, bool), "isAdmin doit être un booléen"
        
        super().__init__()
        
        # Configuration de base
        self._init_window_config()
        self._init_user_info(username, first_name, isAdmin)
        self._init_keyboard_shortcuts()
        self._init_resources()
        
        # Initialisation de la musique
        self.music_playing = False
        self.music_path = os.path.join(infos.PATH, "immortal.mp3")
        if os.path.exists(self.music_path):
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(0.5)
        else:
            print("Erreur : Le fichier de musique n'a pas été trouvé")
        
        # Création de l'interface
        self._init_tab_system()
        self._create_main_menu()
        
        # Dictionnaire pour stocker les onglets
        self.tabs = {}
        
        # Chargement de l'icône de l'application
        self.icon_path = infos.ICON_PATH
        if not os.path.exists(self.icon_path):
            print("Erreur : Le fichier de l'icône n'existe pas.")
        else:
            try:
                self.iconbitmap(self.icon_path)
            except Exception as e:
                print(f"Erreur lors du chargement de l'icône : {e}")
    
    def _init_window_config(self):
        """Configure les paramètres de base de la fenêtre."""
        try:
            self.title(f"{infos.NAME_MAIN} - Bienvenue")
            self.geometry("1000x700")
            self.configure(fg_color=infos.bg_color)
            self.protocol("WM_DELETE_WINDOW", self.on_close)
        except Exception as e:
            print(f"Erreur lors de la configuration de la fenêtre : {e}")
            raise
    
    def _init_user_info(self, username: str, first_name: str, isAdmin: bool) -> None:
        """Initialise les informations utilisateur.
        
        Args:
            username: Nom d'utilisateur
            first_name: Prénom de l'utilisateur
            isAdmin: Droits d'administration
        """
        assert len(username) > 0, "Le nom d'utilisateur ne peut pas être vide"
        assert len(first_name) > 0, "Le prénom ne peut pas être vide"
        
        self.username = username
        self.first_name = first_name
        self.isAdmin = isAdmin
        self.closed_tabs_history = []
        
        # Vérification post-initialisation
        assert hasattr(self, 'username'), "username non initialisé"
        assert hasattr(self, 'first_name'), "first_name non initialisé"
        assert hasattr(self, 'isAdmin'), "isAdmin non initialisé"
    
    def _init_keyboard_shortcuts(self):
        """Configure les raccourcis clavier."""
        self.bind("<Control-w>", self.on_ctrl_w)
        self.bind("<Control-T>", self.on_ctrl_shift_t)
        self.bind("<Escape>", self.on_escape)
        self.bind("<Control-q>", self.on_close)
        self.bind("<Control-s>", lambda e: self.on_settings())
        self.bind("<Control-i>", lambda e: self.on_infos())
        self.bind("<Control-n>", lambda e: self.on_add())
        self.bind("<Control-r>", lambda e: self.on_withdraw())
        self.bind("<Control-f>", lambda e: self.on_search())
        
        if self.isAdmin:
            self.bind("<Control-u>", lambda e: self.on_users())
    
    def _init_resources(self):
        """Charge les ressources graphiques."""
        settings_icon_path = os.path.join(infos.PATH, "logo_settings.png")
        if os.path.exists(settings_icon_path):
            self.settings_image = ctk.CTkImage(
                light_image=Image.open(settings_icon_path),
                dark_image=Image.open(settings_icon_path),
                size=(20, 20)
            )
        else:
            print("Erreur : L'icône des paramètres n'a pas été trouvée")
            self.settings_image = None
    
    def _init_tab_system(self):
        """Initialise le système d'onglets."""
        self.tab_control = ctk.CTkTabview(self, fg_color=infos.bg_color)
        self.tab_control.pack(expand=1, fill="both", padx=infos.DEFAULT_PAD, 
                            pady=infos.DEFAULT_PAD)
        
        self.tab_menu_principal = self.tab_control.add("Menu Principal")
        self.tab_menu_principal.configure(fg_color=infos.bg_color)
    
    def _create_main_menu(self):
        """Crée l'interface du menu principal."""
        self._create_welcome_section()
        self._create_main_buttons()
        self._create_bottom_bar()
    
    def _create_welcome_section(self):
        """Crée la section de bienvenue."""
        title_frame = ctk.CTkFrame(self.tab_menu_principal, fg_color="transparent")
        title_frame.pack(fill="x", padx=infos.DEFAULT_PAD, pady=(infos.DEFAULT_PAD, 40))
        
        self.label_welcome = ctk.CTkLabel(
            title_frame,
            text=f"Bienvenue {self.first_name}",
            font=infos.TITLE_FONT,
            text_color=infos.text_color
        )
        self.label_welcome.pack()
    
    def _create_main_buttons(self):
        """Crée les boutons principaux."""
        # Frame pour les boutons principaux
        self.buttons_frame = ctk.CTkFrame(self.tab_menu_principal, fg_color="transparent")
        self.buttons_frame.pack(expand=True, fill="both", padx=infos.DEFAULT_PAD)
        
        # Configuration de la grille
        self.buttons_frame.grid_columnconfigure(0, weight=1, pad=infos.DEFAULT_PAD)
        self.buttons_frame.grid_columnconfigure(1, weight=1, pad=infos.DEFAULT_PAD)
        self.buttons_frame.grid_columnconfigure(2, weight=1, pad=infos.DEFAULT_PAD)
        
        # Création des boutons
        self.btn_new_plane = self._create_main_button(
            self.buttons_frame, "Nouvel avion", self.on_new_plane, 0, 0)
        self.btn_new_material = self._create_main_button(
            self.buttons_frame, "Nouveau matériel", self.on_new_material, 0, 1)
        self.btn_add = self._create_main_button(
            self.buttons_frame, "Ajouter du matériel", self.on_add, 0, 2)
        self.btn_withdraw = self._create_main_button(
            self.buttons_frame, "Retirer du matériel", self.on_withdraw, 1, 0)
        self.btn_stats = self._create_main_button(
            self.buttons_frame, "Statistiques", self.on_stats, 1, 1)
    
    def _create_main_button(self, parent, text, command, row, column):
        """Crée un bouton principal standardisé."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=infos.MAIN_BUTTON_WIDTH,
            height=infos.MAIN_BUTTON_HEIGHT,
            font=infos.BUTTON_FONT,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color
        )
        btn.grid(row=row, column=column, padx=infos.DEFAULT_PAD, 
                pady=infos.DEFAULT_PAD, sticky="nsew")
        return btn
    
    def _create_bottom_bar(self):
        """Crée la barre de boutons du bas."""
        self.bottom_frame = ctk.CTkFrame(self.tab_menu_principal, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=(40, infos.DEFAULT_PAD))
        
        if self.isAdmin:
            self.btn_users = ctk.CTkButton(
                self.bottom_frame,
                text="Gestion des utilisateurs",
                command=self.on_users,
                width=infos.BOTTOM_BUTTON_WIDTH,
                font=infos.BUTTON_FONT,
                fg_color=infos.ctrl_color,
                hover_color=infos.hover_color
            )
            self.btn_users.pack(side="left", padx=infos.SMALL_PAD)
        
        self._create_utility_buttons(self.bottom_frame)
        
        spacer = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        spacer.pack(side="left", expand=True, fill="x")
        
        self._create_logout_button(self.bottom_frame)
    
    def _create_utility_buttons(self, parent):
        """Crée les boutons utilitaires (info, musique et paramètres)."""
        self.btn_infos = ctk.CTkButton(
            parent,
            text="ⓘ",
            command=self.on_infos,
            width=infos.ICON_BUTTON_SIZE,
            height=infos.ICON_BUTTON_SIZE,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 24)
        )
        self.btn_infos.pack(side="left", padx=infos.SMALL_PAD)
        
        # Bouton musique
        self.btn_music = ctk.CTkButton(
            parent,
            text="▶",
            command=self.toggle_music,
            width=infos.ICON_BUTTON_SIZE,
            height=infos.ICON_BUTTON_SIZE,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 24)
        )
        self.btn_music.pack(side="left", padx=infos.SMALL_PAD)
        
        self.btn_settings = ctk.CTkButton(
            parent,
            text="",
            image=self.settings_image,
            command=self.on_settings,
            width=infos.ICON_BUTTON_SIZE,
            height=infos.ICON_BUTTON_SIZE
        )
        self.btn_settings.pack(side="left", padx=infos.SMALL_PAD)
    
    def _create_logout_button(self, parent):
        """Crée le bouton de déconnexion."""
        self.btn_logout = ctk.CTkButton(
            parent,
            text="⮐",
            text_color=infos.text_color,
            width=infos.ICON_BUTTON_SIZE,
            height=infos.ICON_BUTTON_SIZE,
            command=self.on_close,
            fg_color=infos.ctrl_color,
            hover_color=infos.error_color,
            font=("Segoe UI Symbol", 24)
        )
        self.btn_logout.pack(side="right", padx=infos.SMALL_PAD)
    
    def create_button(self, text, command, row, column, width, height, font):
        """Crée un bouton stylisé pour le menu principal.
        
        Args:
            text (str): Texte du bouton
            command: Fonction à exécuter lors du clic
            row (int): Ligne dans la grille
            column (int): Colonne dans la grille
            width (int): Largeur du bouton
            height (int): Hauteur du bouton
            font: Police du texte
            
        Returns:
            CTkButton: Le bouton créé
        """
        btn = ctk.CTkButton(
            self.tab_menu_principal,  # Parent modifié
            text=text,
            command=command,
            width=width,
            height=height,
            font=font,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color
        )
        btn.grid(row=row, column=column, padx=infos.DEFAULT_PAD, 
                pady=infos.DEFAULT_PAD, sticky="nsew")
        return btn
    
    def create_tab_header(self, tab, title, tab_name):
        """Crée l'en-tête standard d'un onglet avec les boutons de navigation."""
        # Association du raccourci Ctrl+W à l'onglet
        tab.bind("<Control-w>", lambda e: self.close_tab(tab_name))
        
        # --- Création de la structure de l'en-tête ---
        # Frame principale contenant tous les éléments
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=infos.SMALL_PAD, pady=infos.TINY_PAD)
        
        # Organisation en trois zones : gauche (retour), centre (titre), droite (fermer)
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=infos.TINY_PAD)
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", expand=True, fill="x", padx=infos.TINY_PAD)
        
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=infos.TINY_PAD)
        
        # --- Création des boutons de navigation ---
        # Bouton retour avec flèche
        btn_home = ctk.CTkButton(
            left_frame,
            text="↩",
            width=int(infos.SMALL_BUTTON_WIDTH * 1.4),  # 40% plus large
            height=int(infos.SMALL_BUTTON_WIDTH * 1.4),  # 40% plus haut
            command=lambda: self.tab_control.set("Menu Principal"),
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 16)
        )
        btn_home.pack(side="left")
        
        # Titre de l'onglet
        label_title = ctk.CTkLabel(
            title_frame,
            text=title,
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        label_title.pack(expand=True)
        
        # Bouton de fermeture avec croix
        btn_close = ctk.CTkButton(
            right_frame,
            text="✕",
            width=int(infos.SMALL_BUTTON_WIDTH * 1.4),
            height=int(infos.SMALL_BUTTON_WIDTH * 1.4),
            command=lambda: self.close_tab(tab_name),
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 16)
        )
        btn_close.pack(side="right")
        
        # Ligne de séparation sous l'en-tête
        separator = ctk.CTkFrame(tab, height=2, fg_color=infos.separator_color)
        separator.pack(fill="x", padx=infos.SMALL_PAD, pady=(0, infos.SMALL_PAD))

    def on_add(self):
        """Gère l'ouverture de l'onglet Ajouter du matériel."""
        # Nouvel onglet ou focus sur l'ancien
        if "Ajouter du matériel" in self.tabs:
            self.tab_control.set("Ajouter du matériel")
            return
            
        on_add_tab = self.tab_control.add("Ajouter du matériel")
        self.tabs["Ajouter du matériel"] = on_add_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_add_tab, "Ajouter du matériel", "Ajouter du matériel")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(on_add_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Récupération des descriptions depuis la base de données
        try:
            descriptions = db.query("SELECT Description FROM magasin ORDER BY Description")
            descriptions = [desc[0] for desc in descriptions if desc[0]]  # Extraction des descriptions non vides
        except Exception as e:
            print(f"Erreur lors de la récupération des descriptions : {str(e)}")
            descriptions = []
        
        # Section recherche de matériel
        search_frame = ctk.CTkFrame(content_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # Label et combobox pour la recherche
        self.label_search = ctk.CTkLabel(search_frame, text="Rechercher un matériel")
        self.label_search.pack(pady=(10,0))
        
        self.ctrl_search = ctk.CTkComboBox(
            search_frame, 
            values=descriptions,
            width=300
        )
        self.ctrl_search.pack(pady=10)
        
        # Ajout du gestionnaire d'événements pour la molette
        self.ctrl_search._entry.bind(
            "<MouseWheel>",
            lambda e: self._handle_mousewheel(e, self.ctrl_search, descriptions)
        )
        
        # Section quantité
        quantity_frame = ctk.CTkFrame(content_frame)
        quantity_frame.pack(fill="x", padx=20, pady=10)
        
        # Label et champ pour la quantité
        self.label_quantity = ctk.CTkLabel(quantity_frame, text="Quantité à ajouter")
        self.label_quantity.pack(pady=(10,0))
        
        self.ctrl_quantity = ctk.CTkEntry(quantity_frame, width=100)
        self.ctrl_quantity.pack(pady=10)
        
        # Bouton de validation
        self.btn_validate = ctk.CTkButton(
            content_frame,
            text="Valider",
            command=self.validate_add,
            width=200
        )
        self.btn_validate.pack(pady=20)
        
        # Bind des touches
        self.ctrl_search.bind("<Return>", lambda e: self.ctrl_quantity.focus())
        self.ctrl_quantity.bind("<Return>", lambda e: self.validate_add())
        
        # Focus sur le premier champ
        self.ctrl_search.focus()
        
        # Focus sur le nouvel onglet
        self.tab_control.set("Ajouter du matériel")

    def validate_add(self):
        """Valide l'ajout de matériel."""
        description = self.ctrl_search.get()
        quantity = self.ctrl_quantity.get()
        
        # Validation des champs
        if not description:
            messagebox.showerror("Erreur", "Veuillez sélectionner un matériel")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Erreur", "La quantité doit être un nombre positif")
                return
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier")
            return
        
        # Mise à jour de la base de données
        try:
            # Récupération de la quantité actuelle
            result = db.query(
                "SELECT Quantity FROM magasin WHERE Description = ?",
                (description,)
            )
            
            if not result:
                messagebox.showerror("Erreur", "Matériel non trouvé dans la base de données")
                return
            
            current_quantity = result[0][0]
            new_quantity = current_quantity + quantity
            
            # Mise à jour de la quantité
            db.query(
                "UPDATE magasin SET Quantity = ? WHERE Description = ?",
                (new_quantity, description)
            )
            
            # Message de succès
            messagebox.showinfo(
                "Succès", 
                f"Ajout de {quantity} unité(s) de {description}\nNouveau stock : {new_quantity}"
            )
            
            # Réinitialisation des champs
            self.ctrl_quantity.delete(0, "end")
            self.ctrl_search.set("")
            self.ctrl_search.focus()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {str(e)}")

    def on_withdraw(self):
        """Gère l'ouverture de l'onglet Retirer du matériel."""
        # Nouvel onglet ou focus sur l'ancien
        if "Retirer du matériel" in self.tabs:
            self.tab_control.set("Retirer du matériel")
            return
            
        on_withdraw_tab = self.tab_control.add("Retirer du matériel")
        self.tabs["Retirer du matériel"] = on_withdraw_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_withdraw_tab, "Retirer du matériel", "Retirer du matériel")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(on_withdraw_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Récupération des descriptions depuis la base de données
        try:
            descriptions = db.query("SELECT Description FROM magasin ORDER BY Description")
            descriptions = [desc[0] for desc in descriptions if desc[0]]  # Extraction des descriptions non vides
        except Exception as e:
            print(f"Erreur lors de la récupération des descriptions : {str(e)}")
            descriptions = []
        
        # Section recherche de matériel
        search_frame = ctk.CTkFrame(content_frame)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # Label et combobox pour la recherche
        self.label_search = ctk.CTkLabel(search_frame, text="Rechercher un matériel")
        self.label_search.pack(pady=(10,0))
        
        self.ctrl_search = ctk.CTkComboBox(
            search_frame, 
            values=descriptions,
            width=300
        )
        self.ctrl_search.pack(pady=10)
        
        # Ajout du gestionnaire d'événements pour la molette
        self.ctrl_search._entry.bind(
            "<MouseWheel>",
            lambda e: self._handle_mousewheel(e, self.ctrl_search, descriptions)
        )
        
        # Section quantité
        quantity_frame = ctk.CTkFrame(content_frame)
        quantity_frame.pack(fill="x", padx=20, pady=10)
        
        # Label et champ pour la quantité
        self.label_quantity = ctk.CTkLabel(quantity_frame, text="Quantité à retirer")
        self.label_quantity.pack(pady=(10,0))
        
        self.ctrl_quantity = ctk.CTkEntry(quantity_frame, width=100)
        self.ctrl_quantity.pack(pady=10)
        
        # Bouton de validation
        self.btn_validate = ctk.CTkButton(
            content_frame,
            text="Valider",
            command=self.validate_withdraw,
            width=200
        )
        self.btn_validate.pack(pady=20)
        
        # Bind des touches
        self.ctrl_search.bind("<Return>", lambda e: self.ctrl_quantity.focus())
        self.ctrl_quantity.bind("<Return>", lambda e: self.validate_withdraw())
        
        # Focus sur le premier champ
        self.ctrl_search.focus()
        
        # Focus sur le nouvel onglet
        self.tab_control.set("Retirer du matériel")

    def validate_withdraw(self):
        """Valide le retrait de matériel."""
        description = self.ctrl_search.get()
        quantity = self.ctrl_quantity.get()
        
        # Validation des champs
        if not description:
            messagebox.showerror("Erreur", "Veuillez sélectionner un matériel")
            return
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                messagebox.showerror("Erreur", "La quantité doit être un nombre positif")
                return
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier")
            return
        
        # Mise à jour de la base de données
        try:
            # Récupération de la quantité actuelle
            result = db.query(
                "SELECT Quantity FROM magasin WHERE Description = ?",
                (description,)
            )
            
            if not result:
                messagebox.showerror("Erreur", "Matériel non trouvé dans la base de données")
                return
            
            current_quantity = result[0][0]
            
            # Vérification qu'il y a assez de stock
            if current_quantity < quantity:
                messagebox.showerror(
                    "Erreur", 
                    f"Stock insuffisant\nQuantité disponible : {current_quantity}"
                )
                return
            
            new_quantity = current_quantity - quantity
            
            # Mise à jour de la quantité
            db.query(
                "UPDATE magasin SET Quantity = ? WHERE Description = ?",
                (new_quantity, description)
            )
            
            # Message de succès
            messagebox.showinfo(
                "Succès", 
                f"Retrait de {quantity} unité(s) de {description}\nNouveau stock : {new_quantity}"
            )
            
            # Réinitialisation des champs
            self.ctrl_quantity.delete(0, "end")
            self.ctrl_search.set("")
            self.ctrl_search.focus()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {str(e)}")

    def on_search(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Rechercher du matériel" in self.tabs:
            self.tab_control.set("Rechercher du matériel")
            return
            
        on_search_tab = self.tab_control.add("Rechercher du matériel")
        self.tabs["Rechercher du matériel"] = on_search_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_search_tab, "Rechercher du matériel", "Rechercher du matériel")
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Rechercher du matériel")
    
    def on_stats(self):
        #Gère l'ouverture de l'onglet Statistiques.
        if "Statistiques" in self.tabs:
            self.tab_control.set("Statistiques")
            return
            
        on_stats_tab = self.tab_control.add("Statistiques")
        self.tabs["Statistiques"] = on_stats_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_stats_tab, "Statistiques", "Statistiques")
        
        # Frame principale avec scrollbar
        main_frame = ctk.CTkScrollableFrame(on_stats_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame pour les graphiques
        self.stats_frame = ctk.CTkFrame(main_frame)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Bouton de rafraîchissement
        refresh_btn = ctk.CTkButton(
            main_frame,
            text="Rafraîchir les statistiques",
            command=self.update_statistics
        )
        refresh_btn.pack(pady=10)
        
        # Section email (code existant)
        email_frame = ctk.CTkFrame(main_frame)
        email_frame.pack(fill="x", padx=20, pady=10)
        
        # Titre de la section
        email_title = ctk.CTkLabel(
            email_frame,
            text="Envoi du rapport statistique par email",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        email_title.pack(pady=10)
        
        # Description
        description = """Le rapport contiendra les diagrammes suivants :
        1. Proportion des types de pièces
        2. Ratio de disponibilité des pièces
        3. Consommation de pièces par avion"""
        
        description_label = ctk.CTkLabel(
            email_frame,
            text=description,
            justify="left",
            wraplength=500
        )
        description_label.pack(pady=10)
        
        # Frame pour le champ email
        input_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Label et champ pour l'email
        email_label = ctk.CTkLabel(input_frame, text="Adresse email :")
        email_label.pack(side="left", padx=5)
        
        self.email_entry = ctk.CTkEntry(input_frame, width=300)
        self.email_entry.pack(side="left", padx=5)
        
        # Récupération du dernier destinataire
        last_recipient = global_email_manager.get_last_recipient()
        if last_recipient:
            self.email_entry.insert(0, last_recipient)
        
        # Frame pour les boutons
        button_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Bouton d'envoi
        self.send_button = ctk.CTkButton(
            button_frame,
            text="Envoyer le rapport",
            command=self.send_stats_report,
            width=200
        )
        self.send_button.pack(side="left", padx=5)
        
        # Label pour afficher la date du dernier envoi
        last_send_date = global_email_manager.get_last_send_date()
        
        self.last_send_label = ctk.CTkLabel(
            button_frame,
            text=f"Dernier envoi : {last_send_date}",
            text_color=infos.text_color
        )
        self.last_send_label.pack(side="left", padx=20)
        
        # Afficher les statistiques initiales
        self.update_statistics()
        
        # Focus sur le nouvel onglet
        self.tab_control.set("Statistiques")
    
    def create_pie_chart(self, data: Dict[str, Union[float, int]], title: str) -> FigureCanvasTkAgg:
        """Crée un graphique en camembert."""
        # Augmentation de la taille de 6x4 à 12x8
        fig, ax = plt.subplots(figsize=(12, 8))
        labels = list(data.keys())
        values = list(data.values())
        
        if sum(values) > 0:  # Vérifier qu'il y a des données à afficher
            # Augmenter la taille de la police pour le titre et les labels
            ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'fontsize': 12})
            ax.set_title(title, pad=20, fontsize=14)
        else:
            ax.text(0.5, 0.5, "Pas de données", ha='center', va='center', fontsize=14)
        
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        return canvas

    def update_statistics(self):
        """Met à jour les graphiques statistiques."""
        # Nettoyer les anciens graphiques
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Récupérer les données
        cost_stats = db.get_cost_stats_by_plane()
        availability_stats = db.get_availability_ratio()

        # Créer les graphiques
        cost_canvas = self.create_pie_chart(
            cost_stats, 
            "Coût moyen des pièces par avion"
        )
        availability_canvas = self.create_pie_chart(
            availability_stats, 
            "Ratio de disponibilité des pièces"
        )

        # Afficher les graphiques
        cost_canvas.get_tk_widget().pack(pady=10)
        availability_canvas.get_tk_widget().pack(pady=10)

        # Rafraîchir les graphiques
        cost_canvas.draw()
        availability_canvas.draw()

    def send_stats_report(self):
        """Envoie le rapport statistique par email."""
        try:
            destinataire = self.email_entry.get()
            global_email_manager.envoyer_rapport_statistiques(destinataire)
        except Exception as e:
            print(f"Erreur lors de l'envoi du rapport : {str(e)}")

    def on_users(self):
        # Vérification des droits admin
        if not self.isAdmin:
            messagebox.showerror("Erreur", "Vous n'avez pas les droits administrateur")
            return
            
        # Nouvel onglet ou focus sur l'ancien
        if "Gestion des utilisateurs" in self.tabs:
            self.tab_control.set("Gestion des utilisateurs")
            return
            
        on_users_tab = self.tab_control.add("Gestion des utilisateurs")
        self.tabs["Gestion des utilisateurs"] = on_users_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_users_tab, "Gestion des utilisateurs", "Gestion des utilisateurs")
        
        # Frame principale avec scrollbar
        main_frame = ctk.CTkScrollableFrame(on_users_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Section: Création d'utilisateur
        creation_frame = ctk.CTkFrame(main_frame)
        creation_frame.pack(fill="x", padx=20, pady=10)
        
        # Titre de la section
        creation_title = ctk.CTkLabel(
            creation_frame,
            text="Créer un nouvel utilisateur",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        creation_title.pack(pady=10)
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(creation_frame, text="Nom d'utilisateur")
        self.ctrl_username = ctk.CTkEntry(creation_frame)
        self.label_password = ctk.CTkLabel(creation_frame, text="Mot de passe")
        self.ctrl_password = ctk.CTkEntry(creation_frame, show="*")
        self.label_firstname = ctk.CTkLabel(creation_frame, text="Prénom")
        self.ctrl_firstname = ctk.CTkEntry(creation_frame)
        self.label_lastname = ctk.CTkLabel(creation_frame, text="Nom")
        self.ctrl_lastname = ctk.CTkEntry(creation_frame)
        self.label_email = ctk.CTkLabel(creation_frame, text="Email")
        self.ctrl_email = ctk.CTkEntry(creation_frame)
        self.label_phone = ctk.CTkLabel(creation_frame, text="Téléphone")
        self.ctrl_phone = ctk.CTkEntry(creation_frame)
        self.ctrl_isAdmin = ctk.CTkCheckBox(creation_frame, text="Droits administrateur")
        self.btn_valider = ctk.CTkButton(creation_frame, text="Créer l'utilisateur", command=self.create_account)
        
        # Ajout des widgets
        self.label_name.pack(pady=(10,0))
        self.ctrl_username.pack(pady=(0,10))
        self.label_password.pack(pady=(10,0))
        self.ctrl_password.pack(pady=(0,10))
        self.label_firstname.pack(pady=(10,0))
        self.ctrl_firstname.pack(pady=(0,10))
        self.label_lastname.pack(pady=(10,0))
        self.ctrl_lastname.pack(pady=(0,10))
        self.label_email.pack(pady=(10,0))
        self.ctrl_email.pack(pady=(0,10))
        self.label_phone.pack(pady=(10,0))
        self.ctrl_phone.pack(pady=(0,10))
        self.ctrl_isAdmin.pack(pady=10)
        self.btn_valider.pack(pady=10)
        
        # Bind de la touche Entrée
        self.ctrl_username.bind("<Return>", lambda e: self.ctrl_password.focus())
        self.ctrl_password.bind("<Return>", lambda e: self.ctrl_firstname.focus())
        self.ctrl_firstname.bind("<Return>", lambda e: self.ctrl_lastname.focus())
        self.ctrl_lastname.bind("<Return>", lambda e: self.ctrl_email.focus())
        self.ctrl_email.bind("<Return>", lambda e: self.ctrl_phone.focus())
        self.ctrl_phone.bind("<Return>", lambda e: self.create_account())
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Gestion des utilisateurs")
        # Focus sur le premier champ
        self.ctrl_username.focus()
    
    def create_account(self):
        username = self.ctrl_username.get()
        password = self.ctrl_password.get()
        firstname = self.ctrl_firstname.get()
        name = self.ctrl_lastname.get()
        email = self.ctrl_email.get()
        tel = self.ctrl_phone.get()
        isAdmin = True if self.ctrl_isAdmin.get() == 1 else False
        
        # Utilisation de la fonction new_user de bdd_users
        success, message = bdd_users.new_user(
            username=username,
            password=password,
            name=name,
            firstname=firstname,
            email=email,
            tel=tel,
            isAdmin=isAdmin
        )
        
        if success:
            messagebox.showinfo("Confirmation", message)
            # Réinitialisation des champs
            self.ctrl_username.delete(0, "end")
            self.ctrl_password.delete(0, "end")
            self.ctrl_firstname.delete(0, "end")
            self.ctrl_lastname.delete(0, "end")
            self.ctrl_email.delete(0, "end")
            self.ctrl_phone.delete(0, "end")
            self.ctrl_isAdmin.deselect()
        else:
            messagebox.showerror("Erreur", message)

    def on_infos(self):
        """Gère l'ouverture de l'onglet Informations."""
        # Nouvel onglet ou focus sur l'ancien
        if "Informations" in self.tabs:
            self.tab_control.set("Informations")
            return
            
        on_infos_tab = self.tab_control.add("Informations")
        self.tabs["Informations"] = on_infos_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_infos_tab, "Informations", "Informations")
        
        # Frame principale avec scrollbar
        main_frame = ctk.CTkScrollableFrame(on_infos_tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Section développeurs
        dev_frame = ctk.CTkFrame(main_frame)
        dev_frame.pack(fill="x", padx=20, pady=10)
        
        dev_title = ctk.CTkLabel(
            dev_frame,
            text="Développeurs",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        dev_title.pack(pady=10)
        
        devs = ctk.CTkLabel(
            dev_frame,
            text="Thibault de Laubrière\nJules Gillet",
            justify="center"
        )
        devs.pack(pady=10)
        
        # Section mentions spéciales
        special_frame = ctk.CTkFrame(main_frame)
        special_frame.pack(fill="x", padx=20, pady=10)
        
        special_title = ctk.CTkLabel(
            special_frame,
            text="Mentions spéciales",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        special_title.pack(pady=10)
        
        special_mentions = ctk.CTkLabel(
            special_frame,
            text="Jacques Truchet, client initial du projet, directeur technique chez ATCF\n"
                 "Christopher Madi, ami Software Engineer at Murex (nous a conseillé et a testé le projet)\n"
                 "Cédric Couette, ami ingénieur chez Safran (nous a conseillé pour les bases SQL)\n"
                 "Mehdi Ben-Thaier, superviseur du projet\n"
                 "V2F, youtubeur qui nous a donné quelques idées (règles de la NASA)",
            justify="left",
            wraplength=600
        )
        special_mentions.pack(pady=10)
        
        # Section contact
        contact_frame = ctk.CTkFrame(main_frame)
        contact_frame.pack(fill="x", padx=20, pady=10)
        
        contact_title = ctk.CTkLabel(
            contact_frame,
            text="Contact",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        contact_title.pack(pady=10)
        
        contact_info = ctk.CTkLabel(
            contact_frame,
            text="Pour toute question, suggestion ou signalement de bug :\nthibdelaub@outlook.fr",
            justify="center"
        )
        contact_info.pack(pady=10)
        
        # Focus sur le nouvel onglet
        self.tab_control.set("Informations")
    
    def on_settings(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Paramètres" in self.tabs:
            self.tab_control.set("Paramètres")
            return
            
        on_settings_tab = self.tab_control.add("Paramètres")
        self.tabs["Paramètres"] = on_settings_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_settings_tab, "Paramètres", "Paramètres")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(on_settings_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Section Apparence
        appearance_frame = ctk.CTkFrame(content_frame)
        appearance_frame.pack(fill="x", padx=20, pady=10)
        
        # Titre de la section Apparence
        appearance_title = ctk.CTkLabel(
            appearance_frame,
            text="Apparence",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        appearance_title.pack(pady=10)
        
        # Switch pour le thème
        self.theme_switch = ctk.CTkSwitch(
            appearance_frame,
            text="Thème sombre",
            command=self.toggle_theme,
            font=infos.BUTTON_FONT,
            progress_color=infos.ctrl_color,
            button_color=infos.hover_color,
            button_hover_color=infos.error_color
        )
        self.theme_switch.pack(pady=10)
        self.theme_switch.select()  # Force le switch en position activée
        
        # État initial du switch basé sur le thème actuel
        if infos.is_dark_mode:
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        
        # Section Sécurité
        security_frame = ctk.CTkFrame(content_frame)
        security_frame.pack(fill="x", padx=20, pady=10)
        
        # Titre de la section Sécurité
        security_title = ctk.CTkLabel(
            security_frame,
            text="Sécurité",
            font=infos.SUBTITLE_FONT,
            text_color=infos.text_color
        )
        security_title.pack(pady=10)
        
        # Champs pour le changement de mot de passe
        self.old_password_label = ctk.CTkLabel(security_frame, text="Ancien mot de passe")
        self.old_password_entry = ctk.CTkEntry(security_frame, show="*")
        self.new_password_label = ctk.CTkLabel(security_frame, text="Nouveau mot de passe")
        self.new_password_entry = ctk.CTkEntry(security_frame, show="*")
        self.confirm_password_label = ctk.CTkLabel(security_frame, text="Confirmer le mot de passe")
        self.confirm_password_entry = ctk.CTkEntry(security_frame, show="*")
        self.change_password_button = ctk.CTkButton(
            security_frame,
            text="Changer le mot de passe",
            command=self.change_password
        )
        
        # Placement des widgets de mot de passe
        self.old_password_label.pack(pady=(10, 0))
        self.old_password_entry.pack(pady=(0, 10))
        self.new_password_label.pack(pady=(10, 0))
        self.new_password_entry.pack(pady=(0, 10))
        self.confirm_password_label.pack(pady=(10, 0))
        self.confirm_password_entry.pack(pady=(0, 10))
        self.change_password_button.pack(pady=10)
        
        # Bind de la touche Entrée pour les champs de mot de passe
        self.old_password_entry.bind("<Return>", lambda e: self.new_password_entry.focus())
        self.new_password_entry.bind("<Return>", lambda e: self.confirm_password_entry.focus())
        self.confirm_password_entry.bind("<Return>", lambda e: self.change_password())
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Paramètres")
    
    def toggle_theme(self):
        """Méthode désactivée pour le switch thème."""
        pass

    def close_tab(self, tab_name):
        """Ferme un onglet et sauvegarde ses informations."""
        # Création d'un dictionnaire avec les informations de l'onglet
        tab_info = {
            'name': tab_name,
            'method': {
                'Ajouter du matériel': self.on_add,
                'Retirer du matériel': self.on_withdraw,
                'Rechercher du matériel': self.on_search,
                'Statistiques': self.on_stats,
                'Gestion des utilisateurs': self.on_users,
                'Informations': self.on_infos,
                'Paramètres': self.on_settings
            }.get(tab_name)
        }
        
        # Sauvegarde dans l'historique si une méthode est associée
        if tab_info['method']:
            self.closed_tabs_history.insert(0, tab_info)  # Ajout en début de liste
        
        # Suppression de l'onglet
        self.tab_control.delete(tab_name)
        del self.tabs[tab_name]
    
    def on_ctrl_w(self, event):
        """Gère le raccourci Ctrl+W pour fermer l'onglet actif."""
        # Récupération de l'onglet actif
        current_tab = self.tab_control.get()
        
        # Ne pas fermer l'onglet Menu Principal
        if current_tab != "Menu Principal":
            self.close_tab(current_tab)
    
    def on_ctrl_shift_t(self, event):
        """Gère le raccourci Ctrl+Shift+T pour rouvrir le dernier onglet fermé."""
        # Vérification qu'il y a des onglets dans l'historique
        if self.closed_tabs_history:
            # Récupération et suppression du dernier onglet fermé
            last_tab = self.closed_tabs_history.pop(0)
            
            # Réouverture de l'onglet avec sa méthode associée
            if last_tab['method']:
                last_tab['method']()
    
    def on_escape(self, event=None):
        """Gère la touche Échap pour retourner au menu principal."""
        # Changement de l'onglet actif vers Menu Principal
        self.tab_control.set("Menu Principal")
    
    def on_close(self):
        """Gère la fermeture de l'application."""
        # Destruction sécurisée de la fenêtre
        self._safe_destroy()
        
        # Fermeture de l'application
        self.quit()
    
    def _safe_destroy(self):
        """Détruit proprement la fenêtre en annulant les tâches en attente."""
        try:
            # Arrêt de la musique
            if hasattr(self, 'music_playing') and self.music_playing:
                pygame.mixer.music.stop()
            self.destroy()
        except Exception as e:
            print(f"Erreur lors de la destruction de la fenêtre : {e}")

    def on_new_plane(self):
        """Gère l'ouverture de l'onglet Nouvel avion."""
        # Nouvel onglet ou focus sur l'ancien
        if "Nouvel avion" in self.tabs:
            self.tab_control.set("Nouvel avion")
            return
            
        new_plane_tab = self.tab_control.add("Nouvel avion")
        self.tabs["Nouvel avion"] = new_plane_tab
        
        # Création de l'en-tête
        self.create_tab_header(new_plane_tab, "Nouvel avion", "Nouvel avion")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(new_plane_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Création des widgets
        self.label_plane = ctk.CTkLabel(content_frame, text="Nom de l'avion")
        self.ctrl_plane = ctk.CTkEntry(content_frame)
        self.btn_validate_plane = ctk.CTkButton(content_frame, text="Valider", command=self.validate_new_plane)
        
        # Ajout des widgets
        self.label_plane.pack(pady=10)
        self.ctrl_plane.pack(pady=10)
        self.btn_validate_plane.pack(pady=10)
        
        # Bind de la touche Entrée
        self.ctrl_plane.bind("<Return>", lambda e: self.validate_new_plane())
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Nouvel avion")
        # Focus sur le champ de saisie
        self.ctrl_plane.focus()
    
    def validate_new_plane(self):
        """Valide l'ajout d'un nouvel avion."""
        plane_name = self.ctrl_plane.get()
        if not plane_name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom d'avion")
            return
            
        success, message = manip_bd.ajout_plane(plane_name)
        if success:
            messagebox.showinfo("Succès", f"L'avion '{plane_name}' a été ajouté avec succès")
            self.ctrl_plane.delete(0, "end")  # Efface le champ
        else:
            messagebox.showerror("Erreur", message)
    
    def _create_section1_widgets(self, section1_frame: ctk.CTkFrame, entry_width: int) -> None:
        """Crée les widgets de la section 1 (Informations de base).
        
        Args:
            section1_frame: Frame contenant les widgets
            entry_width: Largeur des champs de saisie
        """
        # Configuration de la grille
        for i in range(8):  # 4 colonnes * 2 (pour les espacements)
            section1_frame.grid_columnconfigure(i, weight=1)
            
        # Création des widgets
        self.ctrl_rayonnage = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_etagere = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_description = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_providers = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_pn = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_order = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_quantity = ctk.CTkEntry(section1_frame, width=entry_width)
        self.ctrl_minimum = ctk.CTkEntry(section1_frame, width=entry_width)
        
        # Labels correspondants
        labels = [
            ("Rayonnage", self.ctrl_rayonnage),
            ("Étagère", self.ctrl_etagere),
            ("Description", self.ctrl_description),
            ("Fournisseur", self.ctrl_providers),
            ("PN", self.ctrl_pn),
            ("Order", self.ctrl_order),
            ("Quantité", self.ctrl_quantity),
            ("Minimum", self.ctrl_minimum)
        ]
        
        # Placement des widgets dans la grille (4x4)
        for idx, (label_text, ctrl) in enumerate(labels):
            row = (idx // 4) * 2  # 4 colonnes
            col = (idx % 4) * 2   # 4 lignes
            
            label = ctk.CTkLabel(section1_frame, text=label_text)
            label.grid(row=row, column=col, columnspan=2, padx=10, pady=(10,0))
            ctrl.grid(row=row+1, column=col, columnspan=2, padx=10, pady=(0,10))
        
        return [(label, ctrl) for label, ctrl in labels]

    def _create_section2_widgets(self, section2_frame: ctk.CTkFrame, entry_width: int) -> None:
        """Crée les widgets de la section 2 (Options et maintenance).
        
        Args:
            section2_frame: Frame contenant les widgets
            entry_width: Largeur des champs de saisie
        """
        # Configuration de la grille
        for i in range(6):  # 3 colonnes * 2
            section2_frame.grid_columnconfigure(i, weight=1)
        
        # Création des widgets
        self.ctrl_50h = ctk.CTkCheckBox(section2_frame, text="")
        self.ctrl_100h = ctk.CTkCheckBox(section2_frame, text="")
        self.ctrl_200h = ctk.CTkCheckBox(section2_frame, text="")
        self.ctrl_providers_actf = ctk.CTkEntry(section2_frame, width=entry_width)
        self.ctrl_cost = ctk.CTkEntry(section2_frame, width=entry_width)
        self.ctrl_remarks = ctk.CTkEntry(section2_frame, width=entry_width)
        
        # Liste des widgets
        section2_widgets = [
            ("50H", self.ctrl_50h),
            ("100H", self.ctrl_100h),
            ("200H ou annuelle", self.ctrl_200h),
            ("Fournisseurs ACTF", self.ctrl_providers_actf),
            ("Estimation coût individuel", self.ctrl_cost),
            ("Remarques", self.ctrl_remarks)
        ]
        
        # Placement des widgets
        for idx, (label_text, ctrl) in enumerate(section2_widgets):
            col = (idx % 3) * 2
            row = idx // 3 * 2
            
            # Création du label centré
            label = ctk.CTkLabel(section2_frame, text=label_text, anchor="center")
            label.grid(row=row, column=col, columnspan=2, padx=10, pady=(10,0))
            
            # Placement du contrôle
            ctrl.grid(row=row+1, column=col, columnspan=2, padx=10, pady=(0,10))
            if isinstance(ctrl, ctk.CTkEntry):
                ctrl.configure(justify="center")
        
        return section2_widgets

    def _create_section3_widgets(self, section3_frame: ctk.CTkFrame) -> None:
        """Crée les widgets de la section 3 (Avions associés).
        
        Args:
            section3_frame: Frame contenant les widgets
        """
        # Configuration de la grille
        for i in range(10):  # 5 colonnes * 2
            section3_frame.grid_columnconfigure(i, weight=1)
        
        # Récupération de la liste des avions
        try:
            planes = db.get_all_planes()
            self.plane_checkboxes = {}
            
            # Création et placement des checkboxes
            for idx, plane in enumerate(planes):
                col = (idx % 5) * 2
                row = idx // 5 * 2
                
                # Label au-dessus
                label = ctk.CTkLabel(section3_frame, text=plane[0], anchor="center")
                label.grid(row=row, column=col, columnspan=2, padx=10, pady=(10,0))
                
                # Création d'un frame container pour la checkbox avec une hauteur fixe
                container = ctk.CTkFrame(section3_frame, fg_color="transparent", height=30)
                container.grid(row=row+1, column=col, columnspan=2, padx=10, pady=(0,10))
                container.pack_propagate(False)  # Empêche le frame de se redimensionner
                
                # Création et placement de la checkbox
                checkbox = ctk.CTkCheckBox(container, text="")
                checkbox.pack(expand=True)
                self.plane_checkboxes[plane[0]] = checkbox
                
        except Exception as e:
            print(f"Erreur lors de la récupération des avions : {str(e)}")
            self.plane_checkboxes = {}

    def _setup_navigation(self, all_widgets: list) -> None:
        """Configure la navigation avec la touche Entrée.
        
        Args:
            all_widgets: Liste des widgets à lier
        """
        for i in range(len(all_widgets)-1):
            if isinstance(all_widgets[i][1], ctk.CTkEntry):
                all_widgets[i][1].bind("<Return>", 
                    lambda e, next_widget=all_widgets[i+1][1]: next_widget.focus())
        
        if all_widgets:
            all_widgets[-1][1].bind("<Return>", lambda e: self.validate_new_material())

    def on_new_material(self):
        """Gère l'ouverture de l'onglet Nouveau matériel."""
        # Vérification de l'existence de l'onglet
        if "Nouveau matériel" in self.tabs:
            self.tab_control.set("Nouveau matériel")
            return
            
        # Création de l'onglet
        new_material_tab = self.tab_control.add("Nouveau matériel")
        self.tabs["Nouveau matériel"] = new_material_tab
        
        # Création de l'en-tête
        self.create_tab_header(new_material_tab, "Nouveau matériel", "Nouveau matériel")
        
        # Frame principale
        main_frame = ctk.CTkFrame(new_material_tab, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Largeur fixe pour les champs de saisie
        entry_width = 200
        
        # Section 1 : Informations de base
        section1_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        section1_frame.pack(fill="x", pady=(0, 10))
        section1_widgets = self._create_section1_widgets(section1_frame, entry_width)
        
        # Séparateur 1
        separator1 = ctk.CTkFrame(main_frame, height=1, fg_color=infos.separator_color)
        separator1.pack(fill="x", padx=infos.SMALL_PAD, pady=10)
        
        # Section 2 : Options et maintenance
        section2_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        section2_frame.pack(fill="x", pady=(0, 10))
        section2_widgets = self._create_section2_widgets(section2_frame, entry_width)
        
        # Séparateur 2
        separator2 = ctk.CTkFrame(main_frame, height=1, fg_color=infos.separator_color)
        separator2.pack(fill="x", padx=infos.SMALL_PAD, pady=10)
        
        # Section 3 : Avions associés
        section3_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        section3_frame.pack(fill="x", pady=(0, 20))
        self._create_section3_widgets(section3_frame)
        
        # Bouton de validation
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_validate_material = ctk.CTkButton(
            button_frame,
            text="Valider",
            command=self.validate_new_material,
            width=200
        )
        self.btn_validate_material.pack()
        
        # Configuration de la navigation
        self._setup_navigation(section1_widgets + section2_widgets)
        
        # Focus sur le premier champ
        self.ctrl_rayonnage.focus()
        
        # Focus sur le nouvel onglet
        self.tab_control.set("Nouveau matériel")
    
    def _validate_required_fields(self) -> Tuple[bool, str]:
        """Vérifie que les champs obligatoires sont remplis.
        
        Returns:
            Tuple[bool, str]: (True si valide, message d'erreur sinon)
        """
        required_fields = {
            "Rayonnage": self.ctrl_rayonnage.get(),
            "Étagère": self.ctrl_etagere.get(),
            "Description": self.ctrl_description.get(),
            "Quantité": self.ctrl_quantity.get(),
            "Minimum": self.ctrl_minimum.get()
        }
        
        for field_name, value in required_fields.items():
            if not value.strip():
                return False, f"Le champ {field_name} est obligatoire."
                
        return True, ""

    def _validate_numeric_fields(self) -> Tuple[bool, str, Dict[str, float]]:
        """Vérifie que les champs numériques sont valides.
        
        Returns:
            Tuple[bool, str, Dict[str, float]]: (True si valide, message d'erreur, valeurs converties)
        """
        numeric_fields = {
            "Quantité": self.ctrl_quantity.get(),
            "Minimum": self.ctrl_minimum.get(),
            "Coût": self.ctrl_cost.get() if self.ctrl_cost.get() else "0"
        }
        
        converted_values = {}
        for field_name, value in numeric_fields.items():
            try:
                converted_values[field_name] = float(value)
                if converted_values[field_name] < 0:
                    return False, f"Le champ {field_name} ne peut pas être négatif.", {}
                
                # Validation spécifique pour la quantité et le minimum
                if field_name in ["Quantité", "Minimum"]:
                    if not float(value).is_integer():
                        return False, f"Le champ {field_name} doit être un nombre entier.", {}
                    if converted_values[field_name] > 10000:
                        return False, f"Le champ {field_name} ne peut pas dépasser 10000.", {}
                
                # Validation spécifique pour les coûts
                if field_name == "Coût":
                    if converted_values[field_name] > 1000000:
                        return False, f"Le champ {field_name} ne peut pas dépasser 1 000 000.", {}
                    
            except ValueError:
                return False, f"Le champ {field_name} doit être un nombre.", {}
                
        return True, "", converted_values

    def _get_selected_planes(self) -> List[str]:
        """Récupère la liste des avions sélectionnés.
        
        Returns:
            List[str]: Liste des immatriculations des avions sélectionnés
        """
        return [plane for plane, checkbox in self.plane_checkboxes.items() 
                if checkbox.get()]

    def _insert_material(self, numeric_values: Dict[str, float]) -> Tuple[bool, str]:
        """Insère le nouveau matériel dans la base de données.
        
        Args:
            numeric_values: Dictionnaire des valeurs numériques validées
            
        Returns:
            Tuple[bool, str]: (True si succès, message d'erreur sinon)
        """
        try:
            # Génération automatique du numéro
            from datetime import datetime
            current_date = datetime.now()
            year_last_two = str(current_date.year)[-2:]
            week_number = current_date.strftime("%V")  # Numéro de la semaine sur 2 chiffres
            numero = f"{year_last_two}{week_number}"
            
            # Préparation des données
            maintenance = {
                "50h": int(self.ctrl_50h.get()),
                "100h": int(self.ctrl_100h.get()),
                "200h": int(self.ctrl_200h.get())
            }
            
            # Récupération des IDs des avions sélectionnés
            selected_planes = self._get_selected_planes()
            plane_ids = []
            
            # Conversion des noms d'avions en IDs
            for plane_name in selected_planes:
                try:
                    result = db.query('SELECT "ID plane" FROM planes WHERE name = ?', (plane_name,))
                    if result:
                        plane_ids.append(result[0][0])
                except Exception as e:
                    print(f"Erreur lors de la récupération de l'ID de l'avion {plane_name}: {str(e)}")
            
            # Calcul du stock_estimate_ht (coût total)
            stock_estimate_ht = numeric_values["Coût"] * int(numeric_values["Quantité"])
            
            # Vérification et préparation du champ order
            order = self.ctrl_order.get().strip()
            if not order:  # Si vide, on met 0 par défaut
                order = "0"
            
            # Appel de la fonction d'ajout
            success, message = manip_bd.ajouter_materiel(
                numero=numero,
                rayonnage=self.ctrl_rayonnage.get().strip(),
                etagere=self.ctrl_etagere.get().strip(),
                description=self.ctrl_description.get().strip(),
                providers=self.ctrl_providers.get().strip(),
                pn=self.ctrl_pn.get().strip(),
                order=order,
                quantity=int(numeric_values["Quantité"]),
                minimum=int(numeric_values["Minimum"]),
                maintenance=maintenance,
                providers_actf=self.ctrl_providers_actf.get().strip(),
                cost_estimate=numeric_values["Coût"],
                stock_estimate_ht=stock_estimate_ht,
                remarks=self.ctrl_remarks.get().strip(),
                plane_ids=plane_ids
            )
            
            return success, message
            
        except Exception as e:
            return False, f"Erreur inattendue : {str(e)}"

    def validate_new_material(self):
        """Valide et enregistre le nouveau matériel."""
        # Validation des champs obligatoires
        valid, message = self._validate_required_fields()
        if not valid:
            messagebox.showerror("Erreur", message)
            return
            
        # Validation des champs numériques
        valid, message, numeric_values = self._validate_numeric_fields()
        if not valid:
            messagebox.showerror("Erreur", message)
            return
            
        # Insertion dans la base de données
        success, message = self._insert_material(numeric_values)
        if success:
            messagebox.showinfo("Succès", message)
            self.tab_control.delete("Nouveau matériel")
            del self.tabs["Nouveau matériel"]
        else:
            messagebox.showerror("Erreur", message)

    def change_password(self):
        """Gère le changement de mot de passe."""
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Vérification que tous les champs sont remplis
        if not all([old_password, new_password, confirm_password]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Vérification que les deux nouveaux mots de passe correspondent
        if new_password != confirm_password:
            messagebox.showerror("Erreur", "Les nouveaux mots de passe ne correspondent pas")
            return
        
        # Vérification de l'ancien mot de passe
        success, message, _ = bdd_users.check_co(self.username, old_password)
        if not success:
            messagebox.showerror("Erreur", "Ancien mot de passe incorrect")
            return
        
        # Mise à jour du mot de passe dans la base de données
        try:
            conn = sqlite3.connect(os.path.join(infos.PATH, "bdd_all.db"))
            cursor = conn.cursor()
            
            # Hash du nouveau mot de passe
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Mise à jour du mot de passe
            cursor.execute("""
                UPDATE users 
                SET password = ? 
                WHERE username = ?
            """, (new_password_hash, self.username))
            
            conn.commit()
            conn.close()
            
            # Réinitialisation des champs
            self.old_password_entry.delete(0, "end")
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            
            messagebox.showinfo("Succès", "Mot de passe modifié avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification du mot de passe : {str(e)}")

    def _handle_mousewheel(self, event, combobox, values):
        """Gère le défilement de la molette pour les combobox.
        
        Args:
            event: L'événement de la molette
            combobox: Le combobox à mettre à jour
            values: La liste des valeurs possibles
        """
        if not values:  # Si la liste est vide, on ne fait rien
            return
        
        current = combobox.get()
        try:
            # Trouver l'index actuel
            current_index = values.index(current)
            
            # Calculer le nouvel index en fonction du sens de rotation
            # event.delta > 0 signifie que la molette tourne vers le haut
            new_index = current_index - 1 if event.delta > 0 else current_index + 1
            
            # S'assurer que le nouvel index est dans les limites
            new_index = max(0, min(new_index, len(values) - 1))
            
            # Mettre à jour la valeur
            combobox.set(values[new_index])
        except ValueError:
            # Si la valeur actuelle n'est pas dans la liste, on commence au début
            combobox.set(values[0])

    def toggle_music(self):
        """Bascule la lecture/pause de la musique."""
        if not os.path.exists(self.music_path):
            messagebox.showerror("Erreur", "Le fichier de musique n'a pas été trouvé")
            return
            
        try:
            if self.music_playing:
                pygame.mixer.music.pause()
                self.btn_music.configure(text="▶")
            else:
                pygame.mixer.music.unpause() if pygame.mixer.music.get_pos() > 0 else pygame.mixer.music.play(-1)
                self.btn_music.configure(text="⏸")
            self.music_playing = not self.music_playing
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la lecture de la musique : {str(e)}")

if __name__ == "__main__":
    app = SignUpFrame()