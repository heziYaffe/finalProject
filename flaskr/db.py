'''
import os
import psycopg2
import click
from flask import current_app, g
from flask.cli import with_appcontext
from psycopg2.extras import RealDictCursor


def get_db():
    # g is a special object that is unique for each request.
    # It is used to store data that might be accessed by multiple functions during the request.
    # The connection is stored and reused instead of creating a new connection
    # if get_db is called a second time in the same request.
    if 'db' not in g:
        # current_app is another special object that points to the Flask application handling the request.
        # Since you used an application factory, there is no application object when writing the rest of your code.
        # get_db will be called when the application has been created and is handling a request, so current_app can be used
        # establishes a connection to the file pointed at by the DATABASE configuration key
        conn = psycopg2.connect(host='localhost',
                                database='postgres',
                                user='postgres',
                                password='10531105',
                                cursor_factory=RealDictCursor)
        g.db = conn
        cur = conn.cursor()
        try:
            cur.execute("""CREATE TABLE users (
            		id SERIAL PRIMARY KEY,
            		username TEXT UNIQUE NOT NULL,
            		password TEXT NOT NULL
            		);""")

            cur.execute("""CREATE TABLE audios (
            		id SERIAL PRIMARY KEY,
            		user_id INTEGER NOT NULL,
            		file_name TEXT UNIQUE NOT NULL,
            		file_location TEXT NOT NULL,
            		upload_date TEXT NOT NULL
            		);""")

            cur.execute("""CREATE TABLE useraudios (
            		id SERIAL PRIMARY KEY,
            		user_id INTEGER NOT NULL,
            		file_name TEXT UNIQUE NOT NULL
            		);""")

            conn.commit()

        except:
                print("tables already exists!")
        #g.db = sqlite3.connect(
         #   current_app.config['DATABASE'],
          #  detect_types=sqlite3.PARSE_DECLTYPES
        #)

        # tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
        #g.db.row_factory = sqlite3.Row

    return g.db

def init_db():
    # returns a database connection, which is used to execute the commands read from the file.
    db = get_db()
    # opens a file relative to the flaskr package.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# defines a command line command called init-db that calls the
# init_db function and shows a success message to the user.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# The close_db and init_db_command functions need to be registered with the application instance,
# otherwise, they won’t be used by the application.
# However, since we’re using a factory function, that instance isn’t available when writing the functions.
# Instead, init_app takes an application and does the registration.
def init_app(app):
    # tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)

# checks if a connection was created by checking if g.db was set.
# If the connection exists, it is closed.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
'''


import sqlite3

import click
import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext
from psycopg2.extras import RealDictCursor


def get_db():
    # g is a special object that is unique for each request.
    # It is used to store data that might be accessed by multiple functions during the request.
    # The connection is stored and reused instead of creating a new connection
    # if get_db is called a second time in the same request.
    if 'db' not in g:
        # current_app is another special object that points to the Flask application handling the request.
        # Since you used an application factory, there is no application object when writing the rest of your code.
        # get_db will be called when the application has been created and is handling a request, so current_app can be used

        # establishes a connection to the file pointed at by the DATABASE configuration key
        #g.db = sqlite3.connect(
         #   current_app.config['DATABASE'],
          #  detect_types=sqlite3.PARSE_DECLTYPES
        #)

        # tells the connection to return rows that behave like dicts. This allows accessing the columns by name.
        #g.db.row_factory = sqlite3.Row

        conn = psycopg2.connect(host='ec2-3-228-235-79.compute-1.amazonaws.com',
                                database='d44176tbc8sl5d',
                                user='pqkykfpufawecb',
                                password='d12ea022294161269a064919c304051290c19992cc4f48d28d62cd38bdba67c7',
                                cursor_factory=RealDictCursor)
        g.db = conn

    return g.db

def init_db():
    # returns a database connection, which is used to execute the commands read from the file.
    db = get_db()
    curr = db.cursor()

    curr.execute(
        'CREATE TABLE IF NOT EXISTS users (id SERIAL, username text UNIQUE NOT NULL, password text NOT NULL)'
    )
    # opens a file relative to the flaskr package.
    #with current_app.open_resource('schema.sql') as f:
     #   db.executescript(f.read().decode('utf8'))

# defines a command line command called init-db that calls the
# init_db function and shows a success message to the user.
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# The close_db and init_db_command functions need to be registered with the application instance,
# otherwise, they won’t be used by the application.
# However, since we’re using a factory function, that instance isn’t available when writing the functions.
# Instead, init_app takes an application and does the registration.
def init_app(app):
    # tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)

# checks if a connection was created by checking if g.db was set.
# If the connection exists, it is closed.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
