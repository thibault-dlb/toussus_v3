import wx

class SplitterExample(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxSplitterWindow Example", size=(800, 600))
        
        # Création du wxSplitterWindow
        splitter = wx.SplitterWindow(self)
        
        # Création des panneaux gauche et droit
        panel_left = wx.Panel(splitter, style=wx.BORDER_SUNKEN)
        panel_left.SetBackgroundColour("light blue")
        
        panel_right = wx.Panel(splitter, style=wx.BORDER_SUNKEN)
        panel_right.SetBackgroundColour("light gray")
        
        # Diviser la fenêtre avec une partie gauche prenant 1/3 de l'écran
        splitter.SplitVertically(panel_left, panel_right, int(800 * 1/3))
        
        # Permet à l'utilisateur de redimensionner librement
        splitter.SetSashGravity(1/3)
        
        self.Centre()
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    frame = SplitterExample()
    app.MainLoop()