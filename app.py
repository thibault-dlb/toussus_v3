import wx
from ressources import allinfos as infos
import os
import re

regex_mail = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
regex_tel = r'^0[1-9](?:[\s.-]?\d{2}){4}$'
regex_prenom = r'^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüÿýçčćďđłńňśšťžżÁÀÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜŸÝÇČĆĎĐŁŃŇŚŠŤŽŻ\-\' ]+$'
regex_nom = r'^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüÿýçčćďđłńňśšťžżÁÀÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜŸÝÇČĆĎĐŁŃŇŚŠŤŽŻ\-\' ]+$'

path = infos.path
icon_path = os.path.join(path, "main_icon.ico")

class SignUpFrame (wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="ATCF parts - Connexion", size=(300, 180))
        # Icone de la fenêtre
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)
        self.panel_name = "Connexion"
        
        # Création du FlexGridSizer (2 colonnes, ajustable)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Création des widgets
        self.label_username = wx.StaticText(self.panel, label="Nom d'utilisateur")
        
        # Ajout des widgets
        self.main_sizer.Add(self.label_username, 0, wx.ALL | wx.CENTER, 5)
        
        # Affichage de la fenêtre
        self.Centre()
        self.Show()
        
if __name__ == "__main__":
    app = wx.App(False)
    frame = SignUpFrame()
    app.MainLoop()