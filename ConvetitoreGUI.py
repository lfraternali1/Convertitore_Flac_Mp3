import wx
import os 
import time
from Convertitore import Convertitore
from pathlib import Path

# FINESTRA PRINCIPALE
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(None, *args, **kwargs)
        self.Title = 'FLAC to MP3 CONVERTER'
        self.SetMinSize((700,300))
        self.SetMenuBar(MenuBar(self))
        self.Bind(wx.EVT_CLOSE, self.on_quit_click)
        self.main_panel = MainPanel(self)
        self.Centre()
        self.Show()

    # GESTIONE CHIUSURA
    def on_quit_click(self, event):
        del event
        wx.CallAfter(self.Destroy)

# BARRA DEI MENU
class MenuBar(wx.MenuBar):
    def __init__(self, parent, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)

        fileMenu = wx.Menu()
        infoMenu = wx.Menu()
        
        close = wx.MenuItem(fileMenu, wx.ID_EXIT, "&Chiudi\tCtrl+Q", "Chiudi il programma")
        close.SetBitmap(wx.Bitmap('.\\icons\\close.png'))

        info = wx.MenuItem(fileMenu, wx.ID_HELP, "?\tCtrl+H", "Informazioni")
        info.SetBitmap(wx.Bitmap('.\\icons\\info.png'))

        self.Bind(wx.EVT_MENU, parent.on_quit_click, close)
        self.Bind(wx.EVT_MENU, self.on_info_click, info)

        self.Append(fileMenu, "&File")
        self.Append(infoMenu, "&Info")

        fileMenu.Append(close)
        infoMenu.Append(info)

    def on_info_click(self, event):
        wx.MessageBox('Convertitore FLAC-MP3 by Cipo', 'Info')

# PANNELLO PRINCIPALE
class MainPanel(wx.Panel):
    

    def __init__(self, parent, *args, **kwargs):
        super(MainPanel, self).__init__(parent, *args, **kwargs)
        PATH_PREDEFINITO = os.path.join(Path.home(), "Downloads")
        self.converter_logic = Convertitore(max_threads = 5)
        self.converter_logic.add_handler(self)

        # Creo il sizer principale
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Etichetta di testo per la cartella di origine
        self.origine_label = wx.StaticText(self, label="Cartella di origine:")
        # Casella di testo per cartella di origine
        self.origine_text =  wx.TextCtrl(self)
        # Pulsante sfoglia per casella di origine 
        self.origine_button = wx.Button(self, label="Origine",size = (100,25))
        self.origine_button.Bind(wx.EVT_BUTTON, lambda event: self.OnBrowse(event, "Origine"))

        # Etichetta di testo per la cartella di destinazione
        self.destinazione_label = wx.StaticText(self, label="Cartella di destinazione:", style = wx.EXPAND)
        # Casella di testo per cartella di destinazione
        self.destinazione_text =  wx.TextCtrl(self,value = PATH_PREDEFINITO)
                                              
        # Pulsante sfoglia per cartella di destinazione 
        self.destinazione_button = wx.Button(self, label="Destinazione", size = (100,25))
        self.destinazione_button.Bind(wx.EVT_BUTTON, lambda event: self.OnBrowse(event, "Destinazione"))

        # Pulsante converti
        self.converti_button = wx.Button(self, label="Converti")
        self.Bind(wx.EVT_BUTTON, self.OnConvert, self.converti_button)
        
        # Barra di progressione
        self.progress_bar = wx.Gauge(self)
        
        # Etichetta che si aggiorna 
        self.update_label = wx.StaticText(self, label="0/0")
        
        # Aggiungo i componenti ai vari sizer 
        self.main_sizer.Add(self.origine_label, 0, wx.LEFT | wx.TOP |wx.EXPAND, 10)
        self.origine_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.origine_sizer.Add(self.origine_text, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        self.origine_sizer.Add(self.origine_button, 0, wx.RIGHT, 20)
        self.main_sizer.Add(self.origine_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(self.destinazione_label, 0, wx.LEFT | wx.TOP| wx.EXPAND, 10)
        self.destinazione_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.destinazione_sizer.Add(self.destinazione_text, 1, wx.LEFT | wx.RIGHT |wx.EXPAND, 10)
        self.destinazione_sizer.Add(self.destinazione_button, 0, wx.RIGHT, 20)
        self.main_sizer.Add(self.destinazione_sizer,0,wx.EXPAND)
        self.main_sizer.Add(self.converti_button, 0, wx.ALIGN_CENTER_HORIZONTAL| wx.TOP, 20)
        self.main_sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.update_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizer(self.main_sizer)

    def CheckFolders(self):
        check = 1 
        if not self.origine_text.GetValue() or not os.path.exists(self.origine_text.GetValue()):
            check = 0
            wx.MessageBox(f"Inserisci correttamente la cartella di origine.","Errore", wx.OK | wx.ICON_ERROR)
        elif not self.destinazione_text.GetValue() or not os.path.exists(self.destinazione_text.GetValue()):
            wx.MessageBox(f"Inserisci correttamente la cartella di destinazione.","Errore", wx.OK | wx.ICON_ERROR)
            check = 0 
        return check
    
    def OnConvert(self, event):
        self.on_progress_range(0)
        if self.CheckFolders():
            # Disabilita il pulsante durante la conversione
            self.converti_button.Disable()
            self.converter_logic.convert(self.origine_text.GetValue(), self.destinazione_text.GetValue())

    def OnBrowse(self, event, casella):
        # Azione quando l'utente preme il pulsante "Browse"
        if casella == "Origine":
            wildcard = "Cartella o file FLAC (*.flac)|*.flac|Cartella (*.*)|*.*"
            dialog = wx.FileDialog(self, "Scegli una cartella o un file .flac", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)
        else:
            dialog = wx.DirDialog(self, "Scegli una cartella", style=wx.DD_DEFAULT_STYLE)
        if dialog.ShowModal() == wx.ID_OK:
            selected_path = dialog.GetPaths()
            if casella == "Origine":
                self.origine_text.SetValue(selected_path)
            else:
                self.destinazione_text.SetValue(selected_path)
        dialog.Destroy()

    def on_progress(self):
        current_value = self.progress_bar.GetValue()
        self.progress_bar.SetValue(current_value + 1)
        self.update_label.SetLabel(f"{current_value + 1}/{self.progress_bar.GetRange()}")

    def on_status(self, message):
        # Riabilita il pulsante converti
        self.converti_button.Enable()  
        wx.MessageBox(message, "...", wx.OK | wx.ICON_INFORMATION)
       
    def on_progress_range(self, total_files):
        self.progress_bar.SetValue(0)
        self.update_label.SetLabel("0/" + str(total_files))
        
        self.progress_bar.SetRange(total_files)

if __name__ == '__main__':
    """Run the application."""
    screen_app = wx.App()
    main_frame = MainFrame()
    screen_app.MainLoop()



