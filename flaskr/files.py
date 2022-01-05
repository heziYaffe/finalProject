import functools
import os
import pathlib

from flaskr.vad_algorithm import main

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from flaskr.vad_algorithm import main

from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('files', __name__, url_prefix='/files')

@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    uploaded_files = session['uploaded_files']
    print("after assignment")
    print(uploaded_files)
    if request.method == 'POST':
        f = request.files.get('file')
        file_name = f.filename
        file_location = f"\\{file_name}"
        uploaded_files.append(file_name)
        print("after first adding")
        print(uploaded_files)
        db = get_db()
        error = None
        if error is None:
            try:
                db.execute(
                    "INSERT INTO audio (file_name, file_location) VALUES (?, ?)",
                    (file_name, file_location),
                )
                db.commit()
                # store uploaded files in user session
                session['uploaded_files'] = uploaded_files
                print("after adding")
                print(session['uploaded_files'])
            except db.IntegrityError:
                error = f"Audio file {file_name} is already exist."
            #else:
                #return redirect(url_for("auth.login"))
        flash(error)

        f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
        args = ['3', os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))]
        print("this is the path of the file we want to filter:\n")
        print(os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], f.filename)))
        #main(args, current_app.config['CHUNKS_PATH'], f.filename)

    return render_template('files/upload.html')

@bp.route('/')
def index():

    return render_template('files/index.html')

@bp.route('/choose_file', methods=('GET', 'POST'))
def choose_file():
    if request.method == 'POST':
        file_name = request.form['file_name']
        db = get_db()
        error = None
        f = db.execute(
            'SELECT file_location FROM audio WHERE file_name = ?', (file_name,)
        ).fetchone()
        if f is None:
            error = f'File: {file_name} dosent exist.'
        if error is None:
            for x in f:
                print(x)
                filter_by(request.form, x)

            #session.clear()
            #session['user_id'] = user['id']
            #return redirect(url_for('index'))

        #flash(error)

    #return render_template('auth/login.html')


    return render_template('files/choose_file.html')


def filter_by(form, x):
    alg = request.form['filter']
    file_name = request.form['file_name']
    args = ['3', os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], file_name))]
    print("helel")
    if (alg == "VAD"):
        print("vad is used")
        main(args, current_app.config['CHUNKS_PATH'], file_name)

@bp.route('/analyze/<string:file_name>', methods=('GET', 'POST'))
def analyze(file_name):
    if request.method == 'POST':
        alg = request.form['algorithm']
        if alg == "VAD":
            args = ['3', os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], file_name))]
            print("this is the path of the file we want to filter:\n")
            print(os.path.abspath(os.path.join(current_app.config['UPLOADED_PATH'], file_name)))
            main(args, current_app.config['CHUNKS_PATH'], file_name)
    return render_template('files/analyze.html', file_name=file_name )


