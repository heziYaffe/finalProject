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

def audio_features(file_title, mfcc, chroma, mel):
    with sf.SoundFile(file_title) as audio_recording:
        audio = audio_recording.read(dtype="float32")
        sample_rate = audio_recording.samplerate
        if chroma:
            stft=np.abs(lb.stft(audio))
            result=np.array([])
        if mfcc:
            mfccs=np.mean(lb.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40).T, axis=0)
            result=np.hstack((result, mfccs))
        if chroma:
            chroma=np.mean(lb.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
            result=np.hstack((result, chroma))
        if mel:
            mel=np.mean(lb.feature.melspectrogram(y=audio, sr=sample_rate).T, axis=0)
            result=np.hstack((result, mel))
        return result

def find_specific_emotion(path_of_original_file, path_of_chunks_directory, file_name, emotion):
    chunks = split_audio_to_chunks(upload_dir_path, file_name)

    filename = "flaskr/Completed_model.joblib"
    loaded_model = joblib.load(filename)
    X_test = []
    basedir = os.path.dirname(os.path.realpath(__file__))
    UPLOADED_PATH = os.path.join(basedir, 'uploads')
    file = "C:\\Users\\Mirit\\PycharmProjects\\FinalCsProject\\uploads\\Welcome2.wav" #f"{UPLOADED_PATH}\Welcome2.wav"
    #audio_file = file
    #x, sampling_rate = lb.load(audio_file)
    #lb.feature.melspectrogram(y=x, sr=sampling_rate)
    feature = audio_features(file, mfcc=True, chroma=True, mel=True)
    X_test.append(feature)
    result = loaded_model.predict(X_test)
    print(result)
