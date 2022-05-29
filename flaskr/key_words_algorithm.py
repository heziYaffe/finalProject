#import math

import speech_recognition as sr

from flaskr.Algorithm import Algorithm

class Key_Words_Alg(Algorithm):
    r = sr.Recognizer()

    def filter(self, chunk_filename, word):
        text = self.convert_audio_to_text(chunk_filename)
        print(text)
        if word in text:
            return True
        else:
            return False

    def convert_audio_to_text(self, chunk_file_name):
        with sr.AudioFile(chunk_file_name) as source:
            audio_listened = self.r.record(source)
            # try converting it to text
            try:
                text = self.r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                return text




