import customtkinter as ctk
import csv, os, re, hashlib
from ressources import allinfos as infos
from tkinter import messagebox
from PIL import Image, ImageTk

icon_path = os.path.join(infos.path, "main_icon.ico")

class SignUpFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ATCF parts - Connexion")
        self.geometry("300x300")
        
        # Charger et définir l'icône de la fenêtre
        icon_path = os.path.join(infos.path, "main_icon.ico")
        if not os.path.exists(icon_path):
            print("Erreur : Le fichier de l'icône n'existe pas.")
        else:
            self.iconbitmap(icon_path)
        
        # Création des widgets
        self.label_main = ctk.CTkLabel(self, text="Nom d'utilisateur")
        self.ctrl_main = ctk.CTkEntry(self)
        self.label_snd = ctk.CTkLabel(self, text="Mot de passe")
        self.ctrl_snd = ctk.CTkEntry(self, show="*")
        self.btn_next = ctk.CTkButton(self, text="Suivant", command=self.on_next)
        self.ctrl_snd.bind("<Return>", lambda event: self.on_next())
        self.after(100, lambda: self.ctrl_main.focus_set())  # Ajout de l'appel après un délai
        
        # Ajout des widgets
        self.label_main.pack(pady=10)
        self.ctrl_main.pack(pady=10)
        self.label_snd.pack(pady=10)
        self.ctrl_snd.pack(pady=10)
        self.btn_next.pack(pady=10)
       
        # Affichage de la fenêtre
        self.mainloop()
    
    def on_next(self):
        self.check_connexion()
    
    def check_connexion(self):
        username = self.ctrl_main.get()
        password = self.ctrl_snd.get()
        new_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(infos.path + "/users.csv", "r") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if row[0] == username and row[1] == new_hash:
                    self.first_name = row[3]
                    self.isAdmin = row[6] == "True"
                    print(f"Connexion réussie pour {self.first_name}")
                    print(f"Admin : {self.isAdmin}")
                    self.destroy()
                    main_menu = MainMenu(username, self.first_name, self.isAdmin)
                    main_menu.mainloop()
                    return
        # message box d'erreur
        messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")  # Remplacement de l'appel

class MainMenu(ctk.CTk):
    def __init__(self, username, first_name, isAdmin):
        super().__init__()
        self.title(f"{infos.name_main} - Bienvenue")
        self.geometry("800x600")
        self.username = username
        self.first_name = first_name
        self.isAdmin = isAdmin
        
        # Lier l'événement de fermeture de la fenêtre à la méthode self.on_close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Création des onglets
        self.tab_control = ctk.CTkTabview(self)
        self.tab_control.pack(expand=1, fill="both")
        
        # Onglet Menu Principal
        self.tab_menu_principal = self.tab_control.add("Menu Principal")
        
        # Création des widgets dans l'onglet Menu Principal
        self.label_welcome = ctk.CTkLabel(self.tab_menu_principal, text=f"Bienvenue {self.first_name}")
        self.btn_add = ctk.CTkButton(self.tab_menu_principal, text="Ajouter du matériel")
        self.btn_withdraw = ctk.CTkButton(self.tab_menu_principal, text="Retirer du matériel")
        self.btn_search = ctk.CTkButton(self.tab_menu_principal, text="Rechercher du matériel")
        self.btn_stats = ctk.CTkButton(self.tab_menu_principal, text="Statistiques")
        self.btn_users = ctk.CTkButton(self.tab_menu_principal, text="Gestion des utilisateurs") if self.isAdmin else None
        self.btn_infos = ctk.CTkButton(self.tab_menu_principal, text="Informations")
        self.btn_settings = ctk.CTkButton(self.tab_menu_principal, text="Paramètres")
        self.btn_logout = ctk.CTkButton(self.tab_menu_principal, text="Déconnexion")
        
        # Ajout des commandes aux boutons
        self.btn_add.configure(command=self.on_add)
        self.btn_withdraw.configure(command=self.on_withdraw)
        self.btn_search.configure(command=self.on_search)
        self.btn_stats.configure(command=self.on_stats)
        if self.isAdmin:
            self.btn_users.configure(command=self.on_users)
        self.btn_infos.configure(command=self.on_infos)
        self.btn_settings.configure(command=self.on_settings)
        self.btn_logout.configure(command=self.on_close)
                
        # Ajout des widgets dans l'onglet Menu Principal
        self.label_welcome.pack(pady=10)
        self.btn_add.pack(pady=10)
        self.btn_withdraw.pack(pady=10)
        self.btn_search.pack(pady=10)
        self.btn_stats.pack(pady=10)
        if self.isAdmin:
            self.btn_users.pack(pady=10)
        self.btn_infos.pack(pady=10)
        self.btn_settings.pack(pady=10)
        self.btn_logout.pack(pady=10)
        
        # Dictionnaire pour stocker les onglets
        self.tabs = {}
        
        # Affichage de la fenêtre
        self.mainloop()
    
    def on_add(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Ajouter du matériel" in self.tabs:
            self.tab_control.set("Ajouter du matériel")
            return
        on_add_tab = self.tab_control.add("Ajouter du matériel")
        self.tabs["Ajouter du matériel"] = on_add_tab
        self.label_title = ctk.CTkLabel(on_add_tab, text="Ajouter du matériel")
        self.label_title.pack(pady=10)
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(on_add_tab, text="Nom du matériel")
        self.ctrl_materiel = ctk.CTkComboBox(on_add_tab, values=["Matériel 1", "Matériel 2", "Matériel 3"])
        self.label_quantity = ctk.CTkLabel(on_add_tab, text="Quantité")
        self.ctrl_quantity = ctk.CTkEntry(on_add_tab)
        
        # Ajout des widgets
        self.label_name.pack(pady=10)
        self.ctrl_materiel.pack(pady=10)
        self.label_quantity.pack(pady=10)
        self.ctrl_quantity.pack(pady=10)
        
        # Home et fermeture de l'onglet
        
        self.btn_close = ctk.CTkButton(on_add_tab, text="Fermer", command=lambda: self.close_tab("Ajouter du matériel"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_add_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Ajouter du matériel")
    
    def on_withdraw(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Retirer du matériel" in self.tabs:
            self.tab_control.set("Retirer du matériel")
            return
        on_withdraw_tab = self.tab_control.add("Retirer du matériel")
        self.tabs["Retirer du matériel"] = on_withdraw_tab
        self.label_title = ctk.CTkLabel(on_withdraw_tab, text="Retirer du matériel")
        self.label_title.pack(pady=10)
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(on_withdraw_tab, text="Nom du matériel")
        self.ctrl_materiel = ctk.CTkComboBox(on_withdraw_tab, values=["Matériel 1", "Matériel 2", "Matériel 3"])
        self.label_quantity = ctk.CTkLabel(on_withdraw_tab, text="Quantité")
        self.ctrl_quantity = ctk.CTkEntry(on_withdraw_tab)
        
        # Ajout des widgets
        self.label_name.pack(pady=10)
        self.ctrl_materiel.pack(pady=10)
        self.label_quantity.pack(pady=10)
        self.ctrl_quantity.pack(pady=10)
        
        # Home et fermeture de l'onglet
        
        self.btn_close = ctk.CTkButton(on_withdraw_tab, text="Fermer", command=lambda: self.close_tab("Retirer du matériel"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_withdraw_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Retirer du matériel")
    
    def on_search(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Rechercher du matériel" in self.tabs:
            self.tab_control.set("Rechercher du matériel")
            return
        on_search_tab = self.tab_control.add("Rechercher du matériel")
        self.tabs["Rechercher du matériel"] = on_search_tab
        self.label_title = ctk.CTkLabel(on_search_tab, text="Rechercher du matériel")
        self.label_title.pack(pady=10)
        
        self.btn_close = ctk.CTkButton(on_search_tab, text="Fermer", command=lambda: self.close_tab("Rechercher du matériel"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_search_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Rechercher du matériel")
    
    def on_stats(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Statistiques" in self.tabs:
            self.tab_control.set("Statistiques")
            return
        on_stats_tab = self.tab_control.add("Statistiques")
        self.tabs["Statistiques"] = on_stats_tab
        self.label_title = ctk.CTkLabel(on_stats_tab, text="Statistiques")
        self.label_title.pack(pady=10)
        
        self.btn_close = ctk.CTkButton(on_stats_tab, text="Fermer", command=lambda: self.close_tab("Statistiques"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_stats_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Statistiques")
    
    def on_users(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Gestion des utilisateurs" in self.tabs:
            self.tab_control.set("Gestion des utilisateurs")
            return
        on_users_tab = self.tab_control.add("Gestion des utilisateurs")
        self.tabs["Gestion des utilisateurs"] = on_users_tab
        self.label_title = ctk.CTkLabel(on_users_tab, text="Gestion des utilisateurs")
        self.label_title.pack(pady=10)
        
        # Création des widgets
        self.label_name = ctk.CTkLabel(on_users_tab, text="Nom d'utilisateur")
        self.ctrl_username = ctk.CTkEntry(on_users_tab)
        self.label_password = ctk.CTkLabel(on_users_tab, text="Mot de passe")
        self.ctrl_password = ctk.CTkEntry(on_users_tab, show="*")
        self.label_firstname = ctk.CTkLabel(on_users_tab, text="Prénom")
        self.ctrl_firstname = ctk.CTkEntry(on_users_tab)
        self.label_lastname = ctk.CTkLabel(on_users_tab, text="Nom")
        self.ctrl_lastname = ctk.CTkEntry(on_users_tab)
        self.label_email = ctk.CTkLabel(on_users_tab, text="Email")
        self.ctrl_email = ctk.CTkEntry(on_users_tab)
        self.label_phone = ctk.CTkLabel(on_users_tab, text="Téléphone")
        self.ctrl_phone = ctk.CTkEntry(on_users_tab)
        self.ctrl_isAdmin = ctk.CTkCheckBox(on_users_tab, text="Peux gérer les utilisateurs")
        self.btn_valider = ctk.CTkButton(on_users_tab, text="Valider", command=self.create_account)
        
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
        
        # Fermerture de l'onglet
        
        self.btn_close = ctk.CTkButton(on_users_tab, text="Fermer", command=lambda: self.close_tab("Gestion des utilisateurs"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_users_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Gestion des utilisateurs")
    
    def create_account(self):
        username = self.ctrl_username.get()
        password = self.ctrl_password.get()
        firstname = self.ctrl_firstname.get()
        lastname = self.ctrl_lastname.get()
        email = self.ctrl_email.get()
        phone = self.ctrl_phone.get()
        isAdmin = True if self.ctrl_isAdmin.get() == 1 else False
        infos.create_account(username, password, lastname, firstname, email, phone, isAdmin)
        messagebox.showinfo("Confirmation", "Utilisateur ajouté avec succès")
        self.ctrl_username.delete(0, "end")
        self.ctrl_password.delete(0, "end")
        self.ctrl_firstname.delete(0, "end")
        self.ctrl_lastname.delete(0, "end")
        self.ctrl_email.delete(0, "end")
        self.ctrl_phone.delete(0, "end")
        self.ctrl_isAdmin.deselect()

    def on_infos(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Informations" in self.tabs:
            self.tab_control.set("Informations")
            return
        on_infos_tab = self.tab_control.add("Informations")
        self.tabs["Informations"] = on_infos_tab
        self.label_title = ctk.CTkLabel(on_infos_tab, text="Informations")
        self.label_title.pack(pady=10)
        
        self.btn_close = ctk.CTkButton(on_infos_tab, text="Fermer", command=lambda: self.close_tab("Informations"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_infos_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Informations")
    
    def on_settings(self):
        # Nouvel onglet ou focus sur l'ancien
        if "Paramètres" in self.tabs:
            self.tab_control.set("Paramètres")
            return
        on_settings_tab = self.tab_control.add("Paramètres")
        self.tabs["Paramètres"] = on_settings_tab
        self.label_title = ctk.CTkLabel(on_settings_tab, text="Paramètres")
        self.label_title.pack(pady=10)
        
        self.btn_close = ctk.CTkButton(on_settings_tab, text="Fermer", command=lambda: self.close_tab("Paramètres"))
        self.btn_close.pack(pady=10)
        
        self.btn_home = ctk.CTkButton(on_settings_tab, text="Retour au menu principal", command=lambda: self.tab_control.set("Menu Principal"))
        self.btn_home.pack(pady=10)
        
        # Focus sur le Nouvel onglet
        self.tab_control.set("Paramètres")
    
    def close_tab(self, tab_name):
        self.tab_control.delete(tab_name)
        del self.tabs[tab_name]
    
    def on_close(self):
        print('Fermeture de la fenêtre')
        self.destroy()
    
if __name__ == "__main__":
    app = SignUpFrame()