from mutagen.flac import FLAC
from mutagen.mp3 import MP3, EasyMP3

class MusicFile():

    def __init__ (self, path):
        self.path = path
        self.audio = FLAC(path)
        self.duration = self.calc_duration(self.audio.info.length)

    def calc_duration(self, length):
        minutes = int(length // 60)
        seconds = int(length % 60)
        duration = "{:02d}:{:02d}".format(minutes, seconds)   
        return duration
    
    def set_metadata(self):
        metadata = self.audio.tags
        for key in metadata.keys():
            setattr(self, key, metadata[key])

    def get_metadata(self, metadata):
        ret = ""
        if metadata in self.audio:
            if len(self.audio[metadata]) > 1: 
                ret = ";".join(self.audio[metadata][:-1]) + ";" + self.audio[metadata][-1]
            else:
                ret = self.audio[metadata][0]
        return ret 
    

        