from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app
)
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
import functools
import json
import os


bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_users():
    json_path = os.path.join(current_app.instance_path, 'users.json')
    users = json.load(open(json_path, 'r'))
    return users

class LoginForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data
        error = None
        users = get_users()
        result = [d for d in users if d['name'] == username]
        if not result:
            error = 'Incorrect username.'
        elif not check_password_hash(pwhash=result[0]['password'], password=password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = result[0]['user_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('login.html', form=form)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    # print(user_id)
    if user_id is None:
        g.user = None
    else:
        users = get_users()
        result = [d for d in users if d['user_id'] == user_id]
        g.user = result[0]


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Please log in to access this page.')
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))



