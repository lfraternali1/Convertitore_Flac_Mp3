import wx
import os
import datetime 
from Convertitore import Convertitore
from pathlib import Path
from MusicFile import MusicFile

# FINESTRA PRINCIPALE ---------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(None, *args, **kwargs)
        self.Title = 'FLAC to MP3 CONVERTER'
        icon = wx.Icon(".\\icons\\onion.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        self.SetMinSize((1000, 600))
        self.SetMenuBar(MenuBar(self))
        self.Bind(wx.EVT_CLOSE, self.on_quit_click)
        self.main_panel = MainPanel(self)
        self.Show()

    def on_quit_click(self, event):
        del event
        wx.CallAfter(self.Destroy)


# BARRA DEI MENU -------------------------------------------------------------- 
class MenuBar(wx.MenuBar):
    def __init__(self, parent, *args, **kwargs):
        super(MenuBar, self).__init__(*args, **kwargs)

        fileMenu = wx.Menu()
        infoMenu = wx.Menu()
        
        close = wx.MenuItem(fileMenu, wx.ID_EXIT, "&Chiudi\tCtrl+Q", 
                            "Chiudi il programma")
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

# PANNELLO PRINCIPALE ---------------------------------------------------------
class MainPanel(wx.Panel):

    def __init__(self, parent, *args, **kwargs):
        super(MainPanel, self).__init__(parent, *args, **kwargs)
        self.default_path = os.path.join(Path.home(), "Downloads")
        self.music_files = []
        self.converter_logic = Convertitore(max_threads = 5)
        self.converter_logic.add_handler(self)
        # Creo il sizer principale
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Etichetta di testo per file di origine
        self.origine_label = wx.StaticText(self, label = "Seleziona i file \".flac\" da convertire: ")
                                           
        # Pulsante sfoglia per casella di origine
        
        self.origine_button = wx.Button(self, label = "Origine", size = (100,25))
        self.origine_button.Bind(wx.EVT_BUTTON, 
                                 lambda event: self.on_browse(event, "Origine"))
        # Etichetta di testo per la cartella di destinazione
        
        self.destinazione_label = wx.StaticText(self, 
                                                label="Cartella di destinazione:", style = wx.EXPAND)

        # Casella di testo per cartella di destinazione
        self.destinazione_text =  wx.TextCtrl(self,value = self.default_path)
                                              
        # Pulsante sfoglia per cartella di destinazione 
        
        self.destinazione_button = wx.Button(self, label="Destinazione", size = (100,25))
        self.destinazione_button.Bind(wx.EVT_BUTTON, 
                                      lambda event: self.on_browse(event, "Destinazione"))

        # Pulsante converti
        self.converti_button = wx.Button(self, label="Converti")
        self.Bind(wx.EVT_BUTTON, self.on_convert, self.converti_button)
        
        # Barra di progressione
        self.progress_bar = wx.Gauge(self)
        
        # Etichetta che si aggiorna 
        self.update_label = wx.StaticText(self, label="0/0")
        
        # Casella di testo per messaggi di log 
        self.log_text = wx.ListBox(self, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.log_text.SetWindowStyleFlag(wx.NO_BORDER)
        self.log_text.SetBackgroundColour(wx.Colour(240, 240, 240))
        ###### TABELLA ######
        self.grid = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)       
        self.grid.InsertColumn(0, "Percorso", width = 245)
        self.grid.InsertColumn(1, "Titolo",   width = 110)
        self.grid.InsertColumn(2, "Artista",  width = 90)        
        self.grid.InsertColumn(3, "Album",    width = 100)        
        self.grid.InsertColumn(4, "Anno",     width = 50)        
        self.grid.InsertColumn(5, "#",        width = 30)        
        self.grid.InsertColumn(6, "Genere",   width = 70)        
        self.grid.InsertColumn(7, "Durata",   width = 60)
        self.grid.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
        self.popup_menu = wx.Menu()
        self.delete_item = self.popup_menu.Append(wx.ID_ANY, "Elimina")
        self.Bind(wx.EVT_MENU, self.on_delete, self.delete_item)
        image = wx.Image('.\\icons\\onion.png', wx.BITMAP_TYPE_ANY)
        image = image.Scale(184, 256, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.StaticBitmap(self, bitmap=image.ConvertToBitmap())

        # Aggiungo i componenti ai vari sizer 
        self.origine_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.origine_sizer.Add(self.origine_label,  0, wx.LEFT | wx.TOP | wx.EXPAND, 10)
        self.origine_sizer.Add(self.origine_button, 0, wx.LEFT | wx.TOP | wx.EXPAND,  5)
        self.main_sizer.Add(self.origine_sizer, 0, wx.EXPAND)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.grid, 1, wx.RIGHT|wx.EXPAND, 10)
        self.sizer.Add(bitmap, 0, wx.LEFT|wx.RIGHT|wx.EXPAND, 10)
        
        self.main_sizer.Add(self.sizer, 0, wx.LEFT | wx.TOP | wx.EXPAND, 10)
        self.main_sizer.Add(self.destinazione_label, 0, wx.LEFT | wx.TOP| wx.EXPAND, 10)

        self.destinazione_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.destinazione_sizer.Add(self.destinazione_text, 1, wx.LEFT | wx.RIGHT |wx.EXPAND, 10)
        self.destinazione_sizer.Add(self.destinazione_button, 0, wx.RIGHT, 20)
        
        self.main_sizer.Add(self.destinazione_sizer,0,wx.EXPAND)
        self.main_sizer.Add(self.converti_button, 0, wx.ALIGN_CENTER_HORIZONTAL| wx.TOP, 20)
        self.main_sizer.Add(self.progress_bar, 0, wx.EXPAND | wx.ALL, 10)
        self.main_sizer.Add(self.update_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        self.main_sizer.Add(self.log_text, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(self.main_sizer)

    def on_context_menu(self, event):
        if self.grid.GetSelectedItemCount() > 0:
            self.PopupMenu(self.popup_menu)
        
    def on_delete(self, event):
        selected_indices = []
        index = self.grid.GetFirstSelected()
        while index != -1:
            selected_indices.append(index)
            index = self.grid.GetNextSelected(index)
        
        for index in reversed(selected_indices):
            self.grid.DeleteItem(index)
            del self.music_files[index]
    
    def on_update_log(self, text):
        current_time = datetime.datetime.now()
        self.log_text.Append(str(current_time.strftime("%Y-%m-%d %H:%M:%S")) +" - " + text)

    def check_folder(self):
        check = 1 
        if len(self.music_files) == 0:
            check = 0
            wx.MessageBox(f"Inserisci le canzoni da convertire!","Errore", wx.OK | wx.ICON_ERROR)
        elif not self.destinazione_text.GetValue() or not os.path.exists(self.destinazione_text.GetValue()):
            wx.MessageBox(f"Inserisci una cartella di destinazione esistente!","Errore", wx.OK | wx.ICON_ERROR)
            check = 0 
        return check
    
    def on_convert(self, event):
        self.on_progress_range(0)
        if self.check_folder():
            # Disabilita il pulsante durante la conversione
            self.converti_button.Disable()
            self.origine_button.Disable()
            self.converter_logic.convert(self.music_files, self.destinazione_text.GetValue())
            self.music_files = []
            self.grid.DeleteAllItems()
            
    def on_browse(self, event, casella):
        # Azione quando l'utente preme il pulsante "Browse"
        if casella == "Origine":
            wildcard = "File FLAC (*.flac)|*.flac"
            dialog = wx.FileDialog(self, "Seleziona i file .flac", wildcard=wildcard, style= wx.FD_MULTIPLE)
            if dialog.ShowModal() == wx.ID_OK:
                paths = dialog.GetPaths()
                for path in paths:
                    if os.path.splitext(path)[1]== ".flac" and not self.song_exist(path):
                        music_file = MusicFile(path)
                        index = self.grid.InsertItem(self.grid.GetItemCount(), path)
                        self.grid.SetItem(index, 0, music_file.path)
                        self.grid.SetItem(index, 1, music_file.get_metadata('TITLE'))
                        self.grid.SetItem(index, 2, music_file.get_metadata('ARTIST'))
                        self.grid.SetItem(index, 3, music_file.get_metadata('ALBUM'))
                        self.grid.SetItem(index, 4, music_file.get_metadata('DATE'))
                        self.grid.SetItem(index, 5, music_file.get_metadata('TRACKNUMBER'))
                        self.grid.SetItem(index, 6, music_file.get_metadata('GENRE'))
                        self.grid.SetItem(index, 7, music_file.duration)
                        self.music_files.append(music_file)
        else:
            dialog = wx.DirDialog(self, "Scegli una cartella", style=wx.DD_DEFAULT_STYLE)      
            if dialog.ShowModal() == wx.ID_OK:
                self.destinazione_text.SetValue(dialog.GetPath())       
        dialog.Destroy()

    def song_exist(self, path):
        exist = False
        index = 0
        while(index < len(self.music_files) and not exist):
            if self.music_files[index].path == path:
                exist =  True
            index += 1 
        return exist
    
    def on_progress(self):
        current_value = self.progress_bar.GetValue()
        self.progress_bar.SetValue(current_value + 1)
        self.update_label.SetLabel(f"{current_value + 1}/{self.progress_bar.GetRange()}")

    def on_status(self, message):
        # Riabilita il pulsante converti
        self.converti_button.Enable() 
        self.origine_button.Enable() 
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



