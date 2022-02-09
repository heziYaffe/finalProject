import functools
import os
import pathlib
from datetime import datetime

from flaskr.vad_algorithm import main

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify, send_from_directory
)

from flaskr.vad_algorithm import main
#from flaskr.key_words_algorithm import find_specific_word
from flaskr.key_words_algorithm import Key_Words_Alg
from flaskr.emotions_reocgnition_algorithm import find_specific_emotion


from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('files', __name__, url_prefix='/files')

@bp.route('/upload', methods=('GET', 'POST'))
def upload():

    if request.method == 'POST':
        error = None
        # f is files storage
        f = request.files.get('file')
        file_name = f.filename
        # file location relative to UPLOAD_PATH directory
        file_location = f"\\{file_name}"
        db = get_db()
        try:
            # insert file attributes (id of owner, name, location, upload date) into audios table
            db.execute(
                "INSERT INTO audio (user_id, file_name, file_location, upload_date) VALUES (?, ?, ?, ?)",
                (session['user_id'], file_name, file_location, datetime.today().strftime('%Y-%m-%d')),
            )

            db.commit()

        except db.IntegrityError:
            error = f"Audio file {file_name} is already exist."

        if error is None:
            # save file in upload directory
            f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
            print("the absoulte path of the new file you just upload is:")
            print(os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], f.filename)))

        flash(error)

    return render_template('files/upload.html')

@bp.route('/')
def index():

    return render_template('files/index.html')

@bp.route('/choose_file', methods=('GET', 'POST'))
def choose_file():
    db = get_db()
    # get all the audio files that the user upload
    audios = db.execute(
        'SELECT * FROM audio where user_id = ?', (int(session['user_id']),)
    ).fetchall()

    if request.method == 'POST':
        # name of the chosen file
        file_name = request.form['file_name']

        error = None

        # get location of the given file if it exists
        # f is sqlite3.Row object
        f = db.execute(
            'SELECT file_location FROM audio WHERE file_name = ? and user_id = ?',
            (file_name, session['user_id'],)
        ).fetchone()

        if f is None:
            error = f'File: {file_name} doesnt exist.'

        # if file exists, for
        if error is None:
            for x in f:
                print("file location is:")
                print(x)
                filter_by(request.form['filter'], file_name, x)

    return render_template('files/choose_file.html', audios=audios)


def filter_by(alg, file_name, param):
    print(f"filter {file_name} according to {alg}")
    path_of_original_file = current_app.config['UPLOADED_PATH']
    #os.path.abspath(os.path.join(, file_name))
    path_of_chunks_directory = current_app.config['CHUNKS_PATH']
    args = ['3', path_of_original_file]
    if alg == "VAD":
        print("VAD is used")
        main(args, path_of_chunks_directory, file_name)
    if alg == "Key_Words":
        print("Key Words is used")
        alg = Key_Words_Alg()
        audio_chunks = alg.find_specific_object(path_of_original_file, path_of_chunks_directory, file_name, param)
        #audio_chunks = find_specific_word(path_of_original_file, path_of_chunks_directory, file_name, param)
        for f in audio_chunks:
            print(f)
        return audio_chunks
    if alg == "Specific_Sounds":
        print("Specific_Sounds is used")
        find_specific_emotion(path_of_original_file, path_of_chunks_directory, file_name, param)
    else:
        print("Not Valid")


@bp.route('/analyze/<string:file_name>', methods=('GET', 'POST'))
def analyze(file_name):
    if request.method == 'POST':
        alg = request.form['algorithm']
        if alg == "Specific_sounds":
            param = request.form['sound']
        if alg == "Key_Words":
            param = request.form['word']
        if alg == "Specific_Sounds":
            param = request.form['sound']
        print("post")
        answer = filter_by(alg, file_name, param)
        #return jsonify(chunks=[chunk.serialize() for chunk in answer])

        return render_template('files/analyze_results.html', file_name=file_name, audios=answer)

        #return answer
        #if alg == "VAD":
         #   args = ['3', os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], file_name))]
          #  print("this is the path of the file we want to filter:\n")
           # print(os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], file_name)))
            #main(args, current_app.config['CHUNKS_PATH'], file_name)
    return render_template('files/analyze.html', file_name=file_name)

@bp.route('/audio/<path:filename>')
def download_file(filename):
    print("HERE")
    print(filename)
    return send_from_directory(current_app.config['CHUNKS_PATH'], filename)


