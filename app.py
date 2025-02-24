import customtkinter as ctk
import csv, os, re, hashlib
from ressources import allinfos as infos

icon_path = os.path.join(infos.path, "main_icon.ico")

class SignUpFrame(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ATCF parts - Connexion")
        self.geometry("300x210")
        
        # Création des widgets
        self.label_main = ctk.CTkLabel(self, text="Nom d'utilisateur")
        self.ctrl_main = ctk.CTkEntry(self)
        self.label_snd = ctk.CTkLabel(self, text="Mot de passe")
        self.ctrl_snd = ctk.CTkEntry(self, show="*")
        self.btn_next = ctk.CTkButton(self, text="Suivant", command=self.on_next)
        
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
        ctk.CTkMessageBox.show_error("Erreur", "Nom d'utilisateur ou mot de passe incorrect")

class MainMenu(ctk.CTk):
    def __init__(self, username, first_name, isAdmin):
        super().__init__()
        self.title(f"{infos.name_main} - Bienvenue")
        self.geometry("800x600")
        self.username = username
        self.first_name = first_name
        self.isAdmin = isAdmin
        
        # Création des widgets
        self.label_welcome = ctk.CTkLabel(self, text=f"Bienvenue {self.first_name}")
        self.btn_add = ctk.CTkButton(self, text="Ajouter du matériel")
        self.btn_withdraw = ctk.CTkButton(self, text="Retirer du matériel")
        self.btn_search = ctk.CTkButton(self, text="Rechercher du matériel")
        self.btn_stats = ctk.CTkButton(self, text="Statistiques")
        self.btn_users = ctk.CTkButton(self, text="Gestion des utilisateurs") if self.isAdmin else None
        self.btn_infos = ctk.CTkButton(self, text="Informations")
        self.btn_settings = ctk.CTkButton(self, text="Paramètres")
        self.btn_logout = ctk.CTkButton(self, text="Déconnexion")
        
        # Ajout des widgets
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
        
        # Affichage de la fenêtre
        self.mainloop()

if __name__ == "__main__":
    app = SignUpFrame()