import os
import pathlib

from flask import Flask
from flask_dropzone import Dropzone
from flaskr.helper import create_dir_in_path


#basedir = os.path.dirname(os.path.realpath(__file__))
dropzone = Dropzone()

ALGORITHMS = ["VAD", "a", "b"]

def create_app(test_config=None):
    # creates the Flask instance,__name__ is the name of the current Python module.
    # The app needs to know where it’s located to set up some paths
    app = Flask(__name__)
    dropzone.init_app(app)
    # sets some configuration that the app will use
    app.config.from_object('config')
    app.config.update(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    create_dir_in_path(app.config["BASE_DIR"], "uploads")
    create_dir_in_path(app.config["BASE_DIR"], "audioChunks")
    #for algorithm in ALGORITHMS:
        #create_dir_in_path(app.config["CHUNKS_PATH"], algorithm)


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # register close_db and init_db_command functions with the app instance
    from . import db
    db.init_app(app)

    # register auth.bp blueprint with the app instance
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    #from . import vad
    #app.register_blueprint(vad.bp)

    from . import files
    app.register_blueprint(files.bp)

    return app

    '''
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    dropzone.init_app(app)
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config.update(
        UPLOADED_PATH=os.path.join(basedir, 'uploads'),
        CHUNKS_PATH=os.path.join(basedir, 'audioChunks'),
        VAD_PATH=os.path.join(app.config["CHUNKS_PATH"], "VAD"),
        DROPZONE_MAX_FILE_SIZE=1024,
        DROPZONE_TIMEOUT=5*60*1000
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    from . import vad
    app.register_blueprint(vad.bp)

    return app
    
    '''
