"""
Application de gestion de matériel ATCF parts.

Ce module contient l'interface graphique principale de l'application,
incluant la fenêtre de connexion et le menu principal.
"""

import os
from PIL import Image, ImageTk
import customtkinter as ctk
from tkinter import messagebox

from ressources import allinfos as infos
from ressources import bdd_users

icon_path = os.path.join(infos.path, "main_icon.ico")

class SignUpFrame(ctk.CTk):
    """Fenêtre de connexion de l'application.
    
    Cette classe gère l'interface de connexion utilisateur avec
    les champs nom d'utilisateur et mot de passe.
    """

    def __init__(self):
        """Initialise la fenêtre de connexion."""
        super().__init__()
        
        # Configuration de base de la fenêtre
        self.title("ATCF parts - Connexion")
        self.geometry("300x300")  # Taille fixe de 300x300 pixels
        
        # Chargement de l'icône de l'application
        self.icon_path = os.path.join(infos.path, "main_icon.ico")
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
        super().__init__()
        
        # Configuration de base
        self._init_window_config()
        self._init_user_info(username, first_name, isAdmin)
        self._init_keyboard_shortcuts()
        self._init_resources()
        
        # Création de l'interface
        self._init_tab_system()
        self._create_main_menu()
        
        # Dictionnaire pour stocker les onglets
        self.tabs = {}
    
    def _init_window_config(self):
        """Configure les paramètres de base de la fenêtre."""
        self.title(f"{infos.name_main} - Bienvenue")
        self.geometry("1000x700")
        self.configure(fg_color=infos.bg_color)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def _init_user_info(self, username, first_name, isAdmin):
        """Initialise les informations utilisateur."""
        self.username = username
        self.first_name = first_name
        self.isAdmin = isAdmin
        self.closed_tabs_history = []
    
    def _init_keyboard_shortcuts(self):
        """Configure les raccourcis clavier."""
        self.bind("<Control-w>", self.on_ctrl_w)
        self.bind("<Control-T>", self.on_ctrl_shift_t)
        self.bind("<Escape>", self.on_escape)
        self.bind("<Control-q>", self.on_close)
        self.bind("<Control-s>", lambda e: self.on_settings())
        self.bind("<Control-i>", lambda e: self.on_infos())
        self.bind("<Control-a>", lambda e: self.on_add())
        self.bind("<Control-n>", lambda e: self.on_add())
        self.bind("<Control-r>", lambda e: self.on_withdraw())
        self.bind("<Control-f>", lambda e: self.on_search())
        
        if self.isAdmin:
            self.bind("<Control-u>", lambda e: self.on_users())
    
    def _init_resources(self):
        """Charge les ressources graphiques."""
        settings_icon_path = os.path.join(infos.path, "logo_settings.png")
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
        self.tab_control.pack(expand=1, fill="both", padx=infos.default_pad, 
                            pady=infos.default_pad)
        
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
        title_frame.pack(fill="x", padx=infos.default_pad, pady=(infos.default_pad, 40))
        
        self.label_welcome = ctk.CTkLabel(
            title_frame,
            text=f"Bienvenue {self.first_name}",
            font=infos.title_font,
            text_color=infos.text_color
        )
        self.label_welcome.pack()
    
    def _create_main_buttons(self):
        """Crée les boutons principaux."""
        # Frame pour les boutons principaux
        self.buttons_frame = ctk.CTkFrame(self.tab_menu_principal, fg_color="transparent")
        self.buttons_frame.pack(expand=True, fill="both", padx=infos.default_pad)
        
        # Configuration de la grille
        self.buttons_frame.grid_columnconfigure(0, weight=1, pad=infos.default_pad)
        self.buttons_frame.grid_columnconfigure(1, weight=1, pad=infos.default_pad)
        
        # Création des boutons
        self.btn_add = self._create_main_button(
            self.buttons_frame, "Ajouter du matériel", self.on_add, 0, 0)
        self.btn_withdraw = self._create_main_button(
            self.buttons_frame, "Retirer du matériel", self.on_withdraw, 0, 1)
        self.btn_search = self._create_main_button(
            self.buttons_frame, "Rechercher du matériel", self.on_search, 1, 0)
        self.btn_stats = self._create_main_button(
            self.buttons_frame, "Statistiques", self.on_stats, 1, 1)
    
    def _create_main_button(self, parent, text, command, row, column):
        """Crée un bouton principal standardisé."""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=infos.main_button_width,
            height=infos.main_button_height,
            font=infos.button_font,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color
        )
        btn.grid(row=row, column=column, padx=infos.default_pad, 
                pady=infos.default_pad, sticky="nsew")
        return btn
    
    def _create_bottom_bar(self):
        """Crée la barre de boutons du bas."""
        self.bottom_frame = ctk.CTkFrame(self.tab_menu_principal, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=(40, infos.default_pad))
        
        if self.isAdmin:
            self.btn_users = ctk.CTkButton(
                self.bottom_frame,
                text="Gestion des utilisateurs",
                command=self.on_users,
                width=infos.bottom_button_width,
                font=infos.button_font,
                fg_color=infos.ctrl_color,
                hover_color=infos.hover_color
            )
            self.btn_users.pack(side="left", padx=infos.small_pad)
        
        self._create_utility_buttons(self.bottom_frame)
        
        spacer = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        spacer.pack(side="left", expand=True, fill="x")
        
        self._create_logout_button(self.bottom_frame)
    
    def _create_utility_buttons(self, parent):
        """Crée les boutons utilitaires (info et paramètres)."""
        self.btn_infos = ctk.CTkButton(
            parent,
            text="ⓘ",
            command=self.on_infos,
            width=infos.icon_button_size,
            height=infos.icon_button_size,
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 24)
        )
        self.btn_infos.pack(side="left", padx=infos.small_pad)
        
        self.btn_settings = ctk.CTkButton(
            parent,
            text="",
            image=self.settings_image,
            command=self.on_settings,
            width=infos.icon_button_size,
            height=infos.icon_button_size
        )
        self.btn_settings.pack(side="left", padx=infos.small_pad)
    
    def _create_logout_button(self, parent):
        """Crée le bouton de déconnexion."""
        self.btn_logout = ctk.CTkButton(
            parent,
            text="⮐",
            text_color=infos.text_color,
            width=infos.icon_button_size,
            height=infos.icon_button_size,
            command=self.on_close,
            fg_color=infos.ctrl_color,
            hover_color=infos.error_color,
            font=("Segoe UI Symbol", 24)
        )
        self.btn_logout.pack(side="right", padx=infos.small_pad)
    
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
        btn.grid(row=row, column=column, padx=infos.default_pad, 
                pady=infos.default_pad, sticky="nsew")
        return btn
    
    def create_tab_header(self, tab, title, tab_name):
        """Crée l'en-tête standard d'un onglet avec les boutons de navigation."""
        # Association du raccourci Ctrl+W à l'onglet
        tab.bind("<Control-w>", lambda e: self.close_tab(tab_name))
        
        # --- Création de la structure de l'en-tête ---
        # Frame principale contenant tous les éléments
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=infos.small_pad, pady=infos.tiny_pad)
        
        # Organisation en trois zones : gauche (retour), centre (titre), droite (fermer)
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=infos.tiny_pad)
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", expand=True, fill="x", padx=infos.tiny_pad)
        
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=infos.tiny_pad)
        
        # --- Création des boutons de navigation ---
        # Bouton retour avec flèche
        btn_home = ctk.CTkButton(
            left_frame,
            text="↩",
            width=int(infos.small_button_width * 1.4),  # 40% plus large
            height=int(infos.small_button_width * 1.4),  # 40% plus haut
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
            font=infos.subtitle_font,
            text_color=infos.text_color
        )
        label_title.pack(expand=True)
        
        # Bouton de fermeture avec croix
        btn_close = ctk.CTkButton(
            right_frame,
            text="✕",
            width=int(infos.small_button_width * 1.4),
            height=int(infos.small_button_width * 1.4),
            command=lambda: self.close_tab(tab_name),
            fg_color=infos.ctrl_color,
            hover_color=infos.hover_color,
            font=("Segoe UI Symbol", 16)
        )
        btn_close.pack(side="right")
        
        # Ligne de séparation sous l'en-tête
        separator = ctk.CTkFrame(tab, height=2, fg_color=infos.separator_color)
        separator.pack(fill="x", padx=infos.small_pad, pady=(0, infos.small_pad))

    def on_add(self):
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
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(content_frame, text="Nom du matériel")
        self.ctrl_materiel = ctk.CTkComboBox(content_frame, values=["Matériel 1", "Matériel 2", "Matériel 3"])
        self.label_quantity = ctk.CTkLabel(content_frame, text="Quantité")
        self.ctrl_quantity = ctk.CTkEntry(content_frame)
        
        # Ajout des widgets
        self.label_name.pack(pady=10)
        self.ctrl_materiel.pack(pady=10)
        self.label_quantity.pack(pady=10)
        self.ctrl_quantity.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Ajouter du matériel")
    
    def on_withdraw(self):
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
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(content_frame, text="Nom du matériel")
        self.ctrl_materiel = ctk.CTkComboBox(content_frame, values=["Matériel 1", "Matériel 2", "Matériel 3"])
        self.label_quantity = ctk.CTkLabel(content_frame, text="Quantité")
        self.ctrl_quantity = ctk.CTkEntry(content_frame)
        
        # Ajout des widgets
        self.label_name.pack(pady=10)
        self.ctrl_materiel.pack(pady=10)
        self.label_quantity.pack(pady=10)
        self.ctrl_quantity.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Retirer du matériel")
    
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
        # Nouvel onglet ou focus sur l'ancien
        if "Statistiques" in self.tabs:
            self.tab_control.set("Statistiques")
            return
            
        on_stats_tab = self.tab_control.add("Statistiques")
        self.tabs["Statistiques"] = on_stats_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_stats_tab, "Statistiques", "Statistiques")
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Statistiques")
    
    def on_users(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Gestion des utilisateurs" in self.tabs:
            self.tab_control.set("Gestion des utilisateurs")
            return
            
        on_users_tab = self.tab_control.add("Gestion des utilisateurs")
        self.tabs["Gestion des utilisateurs"] = on_users_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_users_tab, "Gestion des utilisateurs", "Gestion des utilisateurs")
        
        # Frame pour le contenu
        content_frame = ctk.CTkFrame(on_users_tab, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(content_frame, text="Nom d'utilisateur")
        self.ctrl_username = ctk.CTkEntry(content_frame)
        self.label_password = ctk.CTkLabel(content_frame, text="Mot de passe")
        self.ctrl_password = ctk.CTkEntry(content_frame, show="*")
        self.label_firstname = ctk.CTkLabel(content_frame, text="Prénom")
        self.ctrl_firstname = ctk.CTkEntry(content_frame)
        self.label_lastname = ctk.CTkLabel(content_frame, text="Nom")
        self.ctrl_lastname = ctk.CTkEntry(content_frame)
        self.label_email = ctk.CTkLabel(content_frame, text="Email")
        self.ctrl_email = ctk.CTkEntry(content_frame)
        self.label_phone = ctk.CTkLabel(content_frame, text="Téléphone")
        self.ctrl_phone = ctk.CTkEntry(content_frame)
        self.ctrl_isAdmin = ctk.CTkCheckBox(content_frame, text="Peux gérer les utilisateurs")
        self.btn_valider = ctk.CTkButton(content_frame, text="Valider", command=self.create_account)
        
        # Ajout des widgets
        self.label_name.pack(pady=10)
        self.ctrl_username.pack(pady=10)
        self.label_password.pack(pady=10)
        self.ctrl_password.pack(pady=10)
        self.label_firstname.pack(pady=10)
        self.ctrl_firstname.pack(pady=10)
        self.label_lastname.pack(pady=10)
        self.ctrl_lastname.pack(pady=10)
        self.label_email.pack(pady=10)
        self.ctrl_email.pack(pady=10)
        self.label_phone.pack(pady=10)
        self.ctrl_phone.pack(pady=10)
        self.ctrl_isAdmin.pack(pady=10)
        self.btn_valider.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Gestion des utilisateurs")
    
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
        # Nouvel onglet ou focus sur l'ancien
        if "Informations" in self.tabs:
            self.tab_control.set("Informations")
            return
            
        on_infos_tab = self.tab_control.add("Informations")
        self.tabs["Informations"] = on_infos_tab
        
        # Création de l'en-tête
        self.create_tab_header(on_infos_tab, "Informations", "Informations")
        
        # Focus sur le Nouvel onglet
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
        
        # Titre de la section
        appearance_title = ctk.CTkLabel(
            appearance_frame,
            text="Apparence",
            font=infos.subtitle_font,
            text_color=infos.text_color
        )
        appearance_title.pack(pady=10)
        
        # Switch pour le thème
        self.theme_switch = ctk.CTkSwitch(
            appearance_frame,
            text="Mode sombre",
            command=self.toggle_theme,
            font=infos.button_font,
            progress_color=infos.ctrl_color,
            button_color=infos.hover_color,
            button_hover_color=infos.error_color,
            text_color=infos.text_color
        )
        self.theme_switch.pack(pady=10)
        
        # État initial du switch basé sur le thème actuel
        if infos.is_dark_mode:
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Paramètres")
    
    def toggle_theme(self):
        """Gère le changement de thème."""
        is_dark = infos.toggle_theme()
        
        # Sauvegarde du thème dans le fichier de configuration
        infos.save_infos()
        
        # Mise à jour des couleurs de la fenêtre principale
        self.configure(fg_color=infos.bg_color)
        self.tab_control.configure(fg_color=infos.bg_color)
        self.tab_menu_principal.configure(fg_color=infos.bg_color)
        
        # Fonction récursive pour mettre à jour tous les widgets
        def update_widget_colors(widget):
            # Mise à jour des couleurs selon le type de widget
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=infos.text_color)
            elif isinstance(widget, ctk.CTkButton):
                widget.configure(
                    fg_color=infos.ctrl_color,
                    hover_color=infos.hover_color,
                    text_color=infos.text_color
                )
            elif isinstance(widget, ctk.CTkFrame):
                if widget.cget("fg_color") != "transparent":
                    widget.configure(fg_color=infos.bg_color)
            elif isinstance(widget, ctk.CTkSwitch):
                widget.configure(
                    text_color=infos.text_color,
                    progress_color=infos.ctrl_color,
                    button_color=infos.hover_color,
                    button_hover_color=infos.error_color
                )
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(
                    text_color=infos.text_color,
                    fg_color=infos.bg_color,
                    border_color=infos.ctrl_color
                )
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.configure(
                    text_color=infos.text_color,
                    fg_color=infos.ctrl_color,
                    hover_color=infos.hover_color
                )
            
            # Récursion sur tous les widgets enfants
            for child in widget.winfo_children():
                update_widget_colors(child)
        
        # Mise à jour des labels
        self.label_welcome.configure(text_color=infos.text_color)
        
        # Mise à jour des boutons principaux
        for btn in [self.btn_add, self.btn_withdraw, self.btn_search, self.btn_stats]:
            btn.configure(
                fg_color=infos.ctrl_color,
                hover_color=infos.hover_color,
                text_color=infos.text_color
            )
        
        # Mise à jour des boutons du bas
        for btn in [self.btn_settings, self.btn_logout]:
            btn.configure(
                fg_color=infos.ctrl_color,
                text_color=infos.text_color
            )
        
        if hasattr(self, 'btn_users'):
            self.btn_users.configure(
                fg_color=infos.ctrl_color,
                hover_color=infos.hover_color,
                text_color=infos.text_color
            )
        
        if hasattr(self, 'btn_infos'):
            self.btn_infos.configure(
                fg_color=infos.ctrl_color,
                hover_color=infos.hover_color,
                text_color=infos.text_color
            )
        
        # Mise à jour récursive de tous les onglets
        for tab_name, tab in self.tabs.items():
            tab.configure(fg_color=infos.bg_color)
            update_widget_colors(tab)
    
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
            self.destroy()
        except Exception as e:
            print(f"Erreur lors de la destruction de la fenêtre : {e}")

if __name__ == "__main__":
    app = SignUpFrame()