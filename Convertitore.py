import threading
import os 
from pydub import AudioSegment

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

    def load_files(self, source_folder, dest_folder):
        self.to_convert  = []
        if os.path.exists(source_folder) and os.path.exists(dest_folder):
            for file_name in os.listdir(source_folder):
                if file_name.endswith(".flac"):
                    file_flac = os.path.join(source_folder, file_name)
                    file_mp3  = os.path.join(dest_folder, os.path.splitext(file_name)[0] + ".mp3")
                    if os.path.exists(file_mp3):
                        print(file_name, ".mp3 già presente nella cartella di destinazione!")
                    else:
                        self.to_convert.append((file_flac, file_mp3))
        else:
            print("Path cartella origine o destinazione non validi")
    
    def convertAndUpdate(self, file_flac, file_mp3):
        try:
            self.semaphore.acquire()
            print("\n INIZIO CONVERSIONE: " + file_mp3)
            audio = AudioSegment.from_file(file_flac, format="flac")
            audio.export(file_mp3, format="mp3")
            self.tot += 1
            self.notify_progress()
            if self.tot == len(self.to_convert):
                self.notify_status("Fine conversione!")
            print("\n FINE CONVERSIONE: " + file_mp3)
            self.semaphore.release()
        except Exception as e:
            print("Errore nella conversione di "+ file_mp3 + " " + str(e))
    
    def convert(self, source_folder, dest_folder):
        self.load_files(source_folder, dest_folder)
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
