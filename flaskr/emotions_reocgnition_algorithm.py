'''
import joblib
import librosa as lb
import soundfile as sf
import numpy as np
import os, glob, pickle

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score
'''

import librosa as lb
import soundfile as sf
import numpy as np
import os
import joblib
from flaskr.helper import split_audio_to_chunks
from flaskr.Algorithm import Algorithm


emotion_labels = {
    '01': 'neutral',
    '02': 'calm',
    '03': 'happy',
    '04': 'sad',
    '05': 'angry',
    '06': 'fearful',
    '07': 'disgust',
    '08': 'surprised'
}

focused_emotion_labels = ['happy', 'sad', 'angry']

class Emotions_Recognition_Alg(Algorithm):
    loaded_model = joblib.load("flaskr/Completed_model.joblib")

    def filter(self, chunk_filename, emotion):
        X_test = []
        feature = audio_features(chunk_filename, mfcc=True, chroma=True, mel=True)
        X_test.append(feature)
        result = self.loaded_model.predict(X_test)
        print(result)
        return result[0] == emotion


def audio_features(file_title, mfcc, chroma, mel):
    with sf.SoundFile(file_title) as audio_recording:
        audio = audio_recording.read(dtype="float32")
        sample_rate = audio_recording.samplerate
        if chroma:
            stft = np.abs(lb.stft(audio))
            result = np.array([])
        if mfcc:
            mfccs = np.mean(lb.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma = np.mean(lb.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0)
            result = np.hstack((result, chroma))
        if mel:
            mel = np.mean(lb.feature.melspectrogram(y=audio, sr=sample_rate).T, axis=0)
            result = np.hstack((result, mel))
        return result
