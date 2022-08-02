
import os
import shutil
from datetime import datetime
import boto3


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify, send_from_directory
)


from flaskr.key_words_algorithm import Key_Words_Alg
from flaskr.vad_algorithm import Vad_Alg
from flaskr.helper import de_serialize_audio_chunk


from flaskr.db import get_db

bp = Blueprint('files', __name__, url_prefix='/files')

def download_file_from_cloud_to_disk(key, file_path):
    s3 = boto3.client("s3")
    s3.download_file(
        Bucket="hezi1-flaskr", Key=key, Filename=file_path
    )


def upload_file_to_cloud_from_disk(s3, path, key):
    s3.meta.client.upload_file(Filename=path,
                               Bucket='hezi1-flaskr', Key=key)


@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        error = None
        # f is files storage
        f = request.files.get('file')
        file_name = f.filename
        username = g.user['username']
        file_location = f"{username}/{file_name}"

        db = get_db()

        try:
            # insert file attributes (id of owner, name, location, upload date) into audios table
            db.cursor().execute(
                """INSERT INTO audios (user_id, file_name, file_location, upload_date) VALUES (%s, %s, %s, %s);""",
                (session['user_id'], file_name, file_location, datetime.today().strftime('%Y-%m-%d')),
            )

            db.commit()

        except db.IntegrityError:
            error = f"Audio file {file_name} is already exist."
            print(error)

        if error is None:
            # save file in upload directory
            path = os.path.join(current_app.config['UPLOADED_PATH'], f.filename)
            f.save(path)
            # upload file to cloud
            s3 = boto3.resource(service_name='s3')
            upload_file_to_cloud_from_disk(s3, path, f"{username}/{file_name}")

            print("the absolute path of the new file you just upload is:")
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
    curr = db.cursor()
    curr.execute(
        'SELECT * FROM audios where user_id = (%s)', (int(session['user_id']),)
    )
    audios = curr.fetchall()

    return render_template('files/choose_file.html', audios=audios)


def filter_by2(alg, file_name, param, alg_name):
    print(f"filter {file_name} according to {alg_name}")
    path_of_original_file = current_app.config['UPLOADED_PATH']
    path_of_chunks_directory = current_app.config['CHUNKS_PATH']

    '''
    download the file the user want to analyze from cloud to disk
    '''

    db = get_db()

    curr = db.cursor()
    # get location of the given file if it exists
    # f is sqlite3.Row object
    curr.execute(
        'SELECT file_location FROM audios WHERE file_name = (%s) and user_id = (%s)',
        (file_name, session['user_id'],)
    )
    f = curr.fetchone()
    f_path = f['file_location']
    print(f_path)

    download_file_from_cloud_to_disk(f_path, os.path.join(path_of_original_file, file_name))

    '''
    the output of the below function are audio chunks according to the algorithm the
    user choose
    '''
    audio_chunks = alg.find_specific_object(path_of_original_file, path_of_chunks_directory, file_name, param, alg_name)
    return audio_chunks


def save_to_cloud(files, original_file_name, alg_name):
    user_name = g.user['username']
    print(user_name)

    s3 = boto3.resource(service_name='s3')
    chunks_path = current_app.config['CHUNKS_PATH']
    print("saving files:")
    db = get_db()
    curr = db.cursor()
    for f in files:
        path = os.path.join(chunks_path, original_file_name, alg_name)
        path = os.path.join(path, f)
        print(f"path of saved file is: {path}")
        key = f'{user_name}/{original_file_name}/{alg_name}/{f}'
        try:
            upload_file_to_cloud_from_disk(s3, path, key)
            curr.execute(
                """INSERT INTO audios (user_id, file_name, file_location, upload_date) VALUES (%s, %s, %s, %s);""",
                (session['user_id'], f, key, datetime.today().strftime('%Y-%m-%d')),
            )
            # save the changes in DB.
            db.commit()
        except db.IntegrityError:
            error = f"user already has file with this name"

        print(f"saved the file {f}")

def get_audios_by_user_id(curr):
    curr.execute('SELECT * FROM audios where user_id = (%s)', (int(session['user_id']),)
                 )

def get_audios_by_parent_file(curr, parent_file):
    curr.execute('SELECT * FROM audios where user_id = (%s)'
                 ' and original original_file_name=(%s)', (int(session['user_id']), parent_file,)
                 )

def get_audios_by_upload_date_asc_order(curr):
    curr.execute('SELECT * FROM audios ORDER BY upload_date ASC where user_id = (%s);'
                 , (int(session['user_id']),)
                 )

def get_audios_by_upload_date(curr, upload_date):
    curr.execute('SELECT * FROM audios where user_id = (%s)'
                 'and upload_date =(%s)'
                 , (int(session['user_id']), upload_date,)
                 )


'''
remove all files from directory.
this function used when the file analyzing is done
'''
def remove_tmp_files(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def clean_disk():
    remove_tmp_files(current_app.config['CHUNKS_PATH'])
    remove_tmp_files(current_app.config['UPLOADED_PATH'])


'''
display analyze results and give the user
option to save some or all of the audio chunks in 
cloud. 
'''
@bp.route('/<string:file_name>/results', methods=('GET', 'POST'))
def results(file_name):
    # restore data on audio chunks from user session
    audios = session['audios']
    ds_audios = []

    # the data saved in user session in bytes,
    # now we de serialize the data back to
    # Audio Chunk objects
    for chunk in audios:
        ds_audios.append(de_serialize_audio_chunk(chunk))

    if len(ds_audios) > 0:
        alg_name = ds_audios[0].alg
        original_file_name = ds_audios[0].original_file_name

    # saving chosen files in cloud
    if request.method == 'POST':
        files_to_save = request.form.getlist('file_name')
        save_to_cloud(files_to_save, original_file_name, alg_name)
        clean_disk()
        return render_template('files/index.html')

    # display analyze results
    print("Showing results...")

    return render_template('files/analyze_results.html', file_name=file_name, audios=ds_audios)

'''
analyze chosen file according to specific algorithm.
when choosing VAD - no additional parameters requires, so param value will be None.
when choosing Specific Sound - additional parameter require,
so param value will be sound name (happy, sad, etc...)
when choosing Key Words - additional parameter require - so param value will be word.
'''
@bp.route('/analyze/<string:file_name>', methods=('GET', 'POST'))
def analyze(file_name):
    if request.method == 'POST':
        alg_name = request.form['algorithm']
        if alg_name == "VAD":
            param = None
            algorithm = Vad_Alg()
        else:
            param = request.form['word']
            algorithm = Key_Words_Alg()

        # apply algorithm on the original file and get
        # results that suit to the algorithm (in case of Key Words we
        # get audio chunks that contain the specific word, in case of VAD
        # we get chunks that contain voice)
        answer = filter_by2(algorithm, file_name, param, alg_name)
        s_answer = []

        # convert Audio Chunk objects to json in order to
        # save the data about every chunk in the user session
        for chunk in answer:
            s_answer.append(chunk.serialize())
        session['audios'] = s_answer
        return redirect(url_for('files.results', file_name=file_name))

    return render_template('files/analyze.html', file_name=file_name)


#send file from given source.
@bp.route('/audio/<original_file_name>/<alg_name>/<file_name>')
def download_file(original_file_name, file_name, alg_name):
    chunks_path = current_app.config['CHUNKS_PATH']
    path = os.path.join(chunks_path, original_file_name, alg_name)
    print(f"Download the file {file_name} from {path}")
    return send_from_directory(path, file_name)
