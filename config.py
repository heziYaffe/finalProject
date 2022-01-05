"""Flask configuration."""
import os

from flask import app

basedir = os.path.dirname(os.path.realpath(__file__))

SECRET_KEY='dev'
#DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
FLASK_ENV = 'development'
BASE_DIR = basedir
UPLOADED_PATH = os.path.join(basedir, 'uploads')
CHUNKS_PATH = os.path.join(basedir, 'audioChunks')
#VAD_PATH = os.path.join(CHUNKS_PATH, "VAD")
DROPZONE_MAX_FILE_SIZE = 1024
DROPZONE_TIMEOUT = 5 * 60 * 1000
