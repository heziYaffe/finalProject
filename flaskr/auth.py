
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# This creates a Blueprint named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined,
# so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

# When the user visits the /auth/register URL,
# the register view will return HTML with a form for them to fill out.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Check if one of the fields is empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # takes a SQL query with ? placeholders for any user input,
                # and a tuple of values to replace the placeholders with.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                # save the changes in DB.
                db.commit()

            # will occur if the username already exists
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # After storing the user, they are redirected to the login page.
                # url_for() generates the URL for the login view based on its name.
                # redirect() generates a redirect response to the generated URL.
                return redirect(url_for("auth.login"))

        flash(error)

    # When the user initially navigates to auth/register, or there was a validation error,
    # an HTML page with the registration form should be shown.
    # render_template() will render a template containing the HTML
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # fetchone() returns one row from the query.
        # If the query returned no results, it returns None.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across requests.
            # When validation succeeds, the user’s id is stored in a new session.
            # The data is stored in a cookie that is sent to the browser,
            # and the browser then sends it back with subsequent requests.
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('files.index'))

        flash(error)

    return render_template('auth/login.html')

# bp.before_app_request() registers a function that runs before
# the view function, no matter what URL is requested.
# load_logged_in_user checks if a user id is stored in the session
# and gets that user’s data from the database, storing it on g.user,
# which lasts for the length of the request.
# If there is no user id, or if the id doesn’t exist, g.user will be None.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    # remove the user id from the session
    session.clear()
    return redirect(url_for('index'))

# upload, analyze, and save audio files will require a user to be logged in.
# A decorator can be used to check this for each view it’s applied to.

def login_required(view):
    # This decorator returns a new view function that wraps the original view it’s applied to.
    # The new function checks if a user is loaded and redirects to the login page otherwise.
    # If a user is loaded the original view is called and continues normally.
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

