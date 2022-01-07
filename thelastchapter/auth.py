import functools

from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from thelastchapter.db import get_db

bp = Blueprint('auth', __name__)

permissions = {
    'BOOK_EDIT': ('ADMIN',),
    'HOME_LISTS_EDIT': ('ADMIN', 'EDITOR'),
}

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        if not email:
            error = 'Email is required'
        elif not password:
            error = 'Password is required'
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)",
                    (email, generate_password_hash(password))
                )
                db.commit()
                user = db.execute(
                    "SELECT * FROM users where email = ?", (email,)
                ).fetchone()
                if user is None:
                    return redirect(url_for('auth.login'))
                session.clear()
                session['user_id'] = user['id']
                g.user = user
                return redirect(url_for('home'))
            except db.IntegrityError:
                error = f"User {email} is already registered"
            flash(error)
            return redirect(url_for('auth.register'))
        else:
            flash(error)
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        flash(error)
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Must be logged in to access')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def check_list_ownership(list_id):
    db = get_db()
    list_owner = db.execute('SELECT user_id FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if (g.user['id'] != list_owner['user_id']):
        flash('You are not authorized to do that')
        return redirect(url_for('account.display'))
    return

def check_permissions(action):
    if (g.user['permissions'] not in permissions[action]):
        flash('You are not authorized to do that')
        return redirect(url_for('home'))
    return