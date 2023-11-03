import threading
import os
from mutagen import File 
from pydub import AudioSegment
from MusicFile import MusicFile
from pydub.utils import mediainfo

class Convertitore ():

    def __init__ (self, max_threads = 5):
        self._handlers   = []
        self.max_threads = max_threads
        self.semaphore   = threading.Semaphore(self.max_threads)
        self.to_convert  = []
        self.tot         = 0

    def add_handler(self, handler):
        self._handlers.append(handler)

    def remove_handler(self, handler):
        self._handlers.remove(handler)

    def load_files(self, music_files, dest_folder):
        self.to_convert = []
        if os.path.exists(dest_folder):
            for file in music_files:
                path_mp3  = os.path.join(dest_folder, os.path.splitext(os.path.basename (file.path))[0] + ".mp3")
                if os.path.exists(path_mp3):
                     self.update_log(os.path.basename(file.path) + " non verrà convertito in quanto già presente nella cartella di destinazione!")
                else:
                    self.to_convert.append((file, path_mp3))
                    
        else:
             self.update_log("Path cartella di destinazione non validi")

    def convertAndUpdate(self, file, file_mp3):
            try:
                self.semaphore.acquire()
                self.update_log("\n INIZIO CONVERSIONE: " + file.path)
                audio = AudioSegment.from_file(file.path, format="flac")
                audio.export(file_mp3, format='mp3', tags = mediainfo(file.path
                                                                      ).get('TAG', {}))
                self.tot += 1
                self.notify_progress()
                if self.tot == len(self.to_convert):
                    self.notify_status("Fine conversione!")
                    self.tot = 0 
                self.update_log("\n FINE CONVERSIONE: " + file_mp3)
                self.semaphore.release()
            except Exception as e:
                self.update_log("Errore nella conversione di "+ file_mp3 + " " + str(e))
    
    def convert(self, music_files, dest_folder):
        self.load_files(music_files, dest_folder)
        if len(self.to_convert) == 0:
            self.notify_status("Nessun file FLAC da convertire!")

        self.notify_progress_range(len(self.to_convert))
        for file in self.to_convert:
            thread = threading.Thread(target= self.convertAndUpdate, args=(file[0], file[1]))
            thread.start()
        
    def notify_progress(self):
        for handler in self._handlers:
            handler.on_progress()

    def notify_progress_range(self, total_files):
        for handler in self._handlers:
            handler.on_progress_range(total_files)

    def notify_status(self, message):
        for handler in self._handlers:
            handler.on_status(message)
    
    def update_log(self, text):
        for handler in self._handlers:
            handler.on_update_log(text)

    