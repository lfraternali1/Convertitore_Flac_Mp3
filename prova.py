import wx

class CustomFileDialog(wx.Dialog):
    def __init__(self, parent, id=wx.ID_ANY, title="", size=wx.DefaultSize):
        super(CustomFileDialog, self).__init__(parent, id, title, size=size)

        self.paths = []
        self.selected_paths = wx.TextCtrl(self, style=wx.TE_READONLY)
        browse_button = wx.Button(self, label="Sfoglia")
        ok_button = wx.Button(self, id=wx.ID_OK, label="OK")
        cancel_button = wx.Button(self, id=wx.ID_CANCEL, label="Annulla")

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.selected_paths, 1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(browse_button, 0, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(ok_button, 0, flag=wx.ALL, border=10)
        hbox.Add(cancel_button, 0, flag=wx.ALL, border=10)

        vbox.Add(hbox, flag=wx.ALIGN_CENTER)
        self.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_browse, browse_button)

    def on_browse(self, event):
        with wx.FileDialog(self, "Scegli file o cartella", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.paths = dlg.GetPaths()
                if self.paths:
                    self.selected_paths.SetValue("\n".join(self.paths))

app = wx.App()
dlg = CustomFileDialog(None, title="Selezione File o Cartella")
result = dlg.ShowModal()

if result == wx.ID_OK:
    print("Percorsi selezionati:")
    for path in dlg.paths:
        print(path)

dlg.Destroy()
app.MainLoop()