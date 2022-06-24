
import os
from datetime import datetime
import boto3


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify, send_from_directory
)

#from flaskr.vad_algorithm import main
#from flaskr.key_words_algorithm import find_specific_word
from flaskr.key_words_algorithm import Key_Words_Alg
from flaskr.emotions_reocgnition_algorithm import Emotions_Recognition_Alg
from flaskr.vad_algorithm import Vad_Alg
from flaskr.helper import convert_seconds_to_time
from flaskr.helper import de_serialize_audio_chunk



#from flaskr.emotions_reocgnition_algorithm import find_specific_emotion


from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('files', __name__, url_prefix='/files')

def download_file_from_cloud_to_disk(key):
    s3 = boto3.client("s3")
    s3.download_file(
        Bucket="hezi1-flaskr", Key=key, Filename="data/downloaded_from_s3.csv"
    )

def upload_file_to_cloud_from_disk(s3, path, key):
    s3.meta.client.upload_file(Filename=path,
                               Bucket='hezi1-flaskr', Key=key)

def upload_file_to_s3(file_storage):
    print()
    # s3_resource = boto3.resource(service_name='s3')
    # object = s3_resource.Object('hezi1-flaskr', f'{username[0]}/{f.filename}')
    # object.put(Body=f.read())

    # s3 = boto3.resource(service_name='s3')
    # s3.meta.client.upload_file(Filename=os.path.join(current_app.config['UPLOADED_PATH'], f.filename),
    #                          Bucket='hezi1-flaskr', Key=f'{username[0]}/{f.filename}')

@bp.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        error = None
        # f is files storage
        f = request.files.get('file')
        file_name = f.filename
        # file location relative to UPLOAD_PATH directory
        file_location = f"\\{file_name}"
        username = g.user['username']
        db = get_db()
        #cursur = db.cursor()
        #username = cursur.execute(
         #   'SELECT username FROM user where id = ?', (int(session['user_id']),)
        #).fetchone()
        #print(username[0])


        try:
            # insert file attributes (id of owner, name, location, upload date) into audios table
            # insert file attributes (id of owner, name, location, upload date) into audios table
            db.cursor().execute(
                """INSERT INTO audios (user_id, file_name, file_location, upload_date) VALUES (%s, %s, %s, %s);""",
                (session['user_id'], file_name, file_location, datetime.today().strftime('%Y-%m-%d')),
            )
            '''
            db.execute(
                "INSERT INTO audio (user_id, file_name, file_location, upload_date) VALUES (?, ?, ?, ?)",
                (session['user_id'], file_name, file_location, datetime.today().strftime('%Y-%m-%d')),
            )
            '''
            db.commit()

        except db.IntegrityError:
            error = f"Audio file {file_name} is already exist."

        if error is None:
            # save file in upload directory
            f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))

            #upload_file_to_s3(f)
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
    if request.method == 'POST':
        # name of the chosen file
        file_name = request.form['file_name']

        error = None

        # get location of the given file if it exists
        # f is sqlite3.Row object
        curr.execute(
            'SELECT file_location FROM audios WHERE file_name = (%s) and user_id = (%s)',
            (file_name, session['user_id'],)
        )
        f = curr.fetchone()
        if f is None:
            error = f'File: {file_name} doesnt exist.'

        # if file exists, for
        if error is None:
            for x in f:
                print("file location is:")
                print(x)
                filter_by(request.form['filter'], file_name, x)

    return render_template('files/choose_file.html', audios=audios)

'''
def filter_by(alg, file_name, param):
    print(f"filter {file_name} according to {alg}")
    path_of_original_file = current_app.config['UPLOADED_PATH']
    #os.path.abspath(os.path.join(, file_name))
    path_of_chunks_directory = current_app.config['CHUNKS_PATH']
    args = ['3', path_of_original_file]
    if alg == "VAD":
        print("VAD is used")
        alg = Vad_Alg()
        audio_chunks = alg.split_by_silence(path_of_original_file, path_of_chunks_directory, file_name, param)
        return audio_chunks
        #main(args, path_of_chunks_directory, file_name)
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
        alg = Emotions_Recognition_Alg()
        audio_chunks = alg.find_specific_object(path_of_original_file, path_of_chunks_directory, file_name, param)
        for f in audio_chunks:
            print(f)
        return audio_chunks
        #find_specific_emotion(path_of_original_file, path_of_chunks_directory, file_name, param)
    else:
        print("Not Valid")
'''

def filter_by2(alg, file_name, param, alg_name):
    print(f"filter {file_name} according to {alg_name}")
    path_of_original_file = current_app.config['UPLOADED_PATH']
    path_of_chunks_directory = current_app.config['CHUNKS_PATH']
    audio_chunks = alg.find_specific_object(path_of_original_file, path_of_chunks_directory, file_name, param, alg_name)
    return audio_chunks


def save_to_cloud(files, original_file_name, alg_name):
    user_name = g.user['username']
    print(user_name)

    s3 = boto3.resource(service_name='s3')
    #s3.meta.client.upload_file(Filename=os.path.join(current_app.config['UPLOADED_PATH'], f.filename),
     #                         Bucket='hezi1-flaskr', Key=f'{user_name[0]}/{f.filename}')
    chunks_path = current_app.config['CHUNKS_PATH']
    print("saving files:")
    db = get_db()
    curr = db.cursor()
    for f in files:
        path = os.path.join(chunks_path, original_file_name, alg_name)
        path = os.path.join(path, f)
        print(f"path of saved file is: {path}")
        key = f'{user_name}/{original_file_name}/{alg_name}/{f}'
        #upload_file_to_cloud_from_disk(s3, path, key)
        curr.execute(
            """INSERT INTO audios (user_id, file_name, file_location, upload_date) VALUES (%s, %s, %s, %s);""",
            (session['user_id'], f, key, datetime.today().strftime('%Y-%m-%d')),
        )

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

    alg_name = ds_audios[0].alg
    original_file_name = ds_audios[0].original_file_name

    # saving chosen files in cloud
    if request.method == 'POST':
        files_to_save = request.form.getlist('file_name')
        save_to_cloud(files_to_save, original_file_name, alg_name)

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
            algorithm = Vad_Alg();
        elif alg_name == "Key_Words":
            param = request.form['word']
            algorithm = Key_Words_Alg();
        else:
            param = request.form['sound']
            algorithm = Emotions_Recognition_Alg();
        print("post")

        # apply algorithm on the original file and get
        # results that suit to the algorithm (in case of Key Words we
        # get audio chunks that contain the specific word, in case of VAD
        # we chunks that contain voice)
        answer = filter_by2(algorithm, file_name, param, alg_name)
        s_answer = []

        # convert Audio Chunk objects to json in order to
        # save the data about every chunk in the user session
        for chunk in answer:
            s_answer.append(chunk.serialize())
        session['audios'] = s_answer
        if alg_name == "Specific_Sounds":
            return render_template('files/analyze_emotion_results.html', file_name=file_name, audios=answer)
        else:
            #return render_template('files/analyze_results.html', file_name=file_name, audios=answer)
            return redirect(url_for('files.results', file_name=file_name))
    return render_template('files/analyze.html', file_name=file_name)


#send file from given source.
@bp.route('/audio/<original_file_name>/<alg_name>/<file_name>')
def download_file(original_file_name, file_name, alg_name):
    chunks_path = current_app.config['CHUNKS_PATH']
    path = os.path.join(chunks_path, original_file_name, alg_name)
    print(f"Download the file {file_name} from {path}")
    return send_from_directory(path, file_name)
