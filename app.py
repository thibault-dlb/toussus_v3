import wx, csv, os, re, hashlib
from ressources import allinfos as infos

icon_path = os.path.join(infos.path, "main_icon.ico")

class SignUpFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="ATCF parts - Connexion", size=(300, 210))
        # Icone de la fenêtre
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        self.panel_name = "Connexion"
        
        # Création du Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)        
        
        # Création des widgets
        self.label_main = wx.StaticText(self.panel, label="Nom d'utilisateur")
        self.ctrl_main = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER)
        self.label_snd = wx.StaticText(self.panel, label="Mot de passe")
        self.ctrl_snd = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.btn_next = wx.Button(self.panel, label="Suivant")
        
        # Couleurs
        # self.panel.SetBackgroundColour(infos.bg_color)
        # self.ctrl_main.SetBackgroundColour(infos.ctrl_color)
        # self.ctrl_snd.SetBackgroundColour(infos.ctrl_color)
        # self.label_main.SetForegroundColour(infos.label_color)
        # self.label_snd.SetForegroundColour(infos.label_color)
        # self.btn_next.SetBackgroundColour(infos.ctrl_color)
        
        # Actions
        self.btn_next.Bind(wx.EVT_BUTTON, self.on_next)
        self.ctrl_main.Bind(wx.EVT_TEXT_ENTER, self.on_next)
        self.ctrl_snd.Bind(wx.EVT_TEXT_ENTER, self.on_next)
        
        # Ajout des widgets
        self.main_sizer.Add(self.label_main, 0, wx.UP | wx.CENTER, 15)
        self.main_sizer.Add(self.ctrl_main, 0, wx.UP | wx.CENTER, 10)
        self.main_sizer.Add(self.label_snd, 0, wx.UP | wx.CENTER, 10)
        self.main_sizer.Add(self.ctrl_snd, 0, wx.UP | wx.CENTER, 10)
        self.main_sizer.Add(self.btn_next, 0, wx.UP | wx.CENTER, 10)
        
        # Ajout du Sizer au panel
        self.panel.SetSizer(self.main_sizer)
        
        # Affichage de la fenêtre
        self.Centre()
        self.Show()
    
    def on_next(self, event):
        if self.panel_name == "Connexion":
            self.check_connexion()
    
    def check_connexion(self):
        username = self.ctrl_main.GetValue()
        password = self.ctrl_snd.GetValue()
        new_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(infos.path + "/users.csv", "r") as f:
            reader = csv.reader(f, delimiter=";")
            for row in reader:
                if row[0] == username and row[1] == new_hash:
                    self.first_name = row[3]
                    self.isAdmin = row[6]
                    print(f"Connexion réussie pour {self.first_name}")
                    print(f"Admin : {self.isAdmin}")
                    self.Close(True)
                    MainMenu(username, self.first_name, self.isAdmin)
                    return
        # message box d'erreur
        wx.MessageDialog(self, "Nom d'utilisateur ou mot de passe incorrect", "Erreur", wx.OK | wx.ICON_ERROR).ShowModal()

class MainMenu(wx.Frame):
    def __init__(self, username, first_name, isAdmin):
        super().__init__(parent=None, title=f"{infos.name_main} - Bienvenue", size=(300, 210))
        self.username = username
        self.first_name = first_name
        self.isAdmin = isAdmin
        
        # Icone de la fenêtre
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
        # Notebook
        self.notebook = wx.Notebook(self)
        self.panel_name = "Menu principal"
        
        # Splitter
        self.splitter = wx.SplitterWindow(self.notebook)
        self.splitter.SetMinimumPaneSize(50)
        self.splitter.SetSashGravity(0.5)
        
        
        # Affichage du menu principal
        self.Centre()
        self.Show()
        
        

if __name__ == "__main__":
    app = wx.App(False)
    frame = SignUpFrame()
    app.MainLoop()