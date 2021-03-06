import functools
from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from thelastchapter.db import get_db
from thelastchapter.validation.account_validation import LogIn, AlterPermissions

bp = Blueprint('auth', __name__)

roles = ( 'ADMIN', 'EDITOR', 'USER' )

permissions = {
    'ALTER_USER_PERMISSIONS': ('ADMIN',),
    'BOOK_CREATE': ('ADMIN', 'EDITOR'),
    'BOOK_UPDATE': ('ADMIN', 'EDITOR'),
    'BOOK_DELETE': ('ADMIN',),
    'HOME_LISTS_UPDATE': ('ADMIN', 'EDITOR'),
}

actions = {
    'alter_user_permissions': 'ALTER_USER_PERMISSIONS',
    'create_book': 'BOOK_CREATE',
    'update_book': 'BOOK_UPDATE',
    'delete_book': 'BOOK_DELETE',
    'update_home_list': 'HOME_LISTS_UPDATE',
}

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Must be logged in to access')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def check_permissions(action):
    def decorator_permissions(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if (g.user['permissions'] not in permissions[action]):
                flash('You are not authorized to do that')
                return redirect(url_for('home'))
            return view(**kwargs)
        return wrapped_view
    return decorator_permissions

def check_list_ownership(list_id, AJAX=False):
    db = get_db()
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if list_data is None:
        flash('List not found')
        return None
    if (g.user['id'] != list_data['user_id']):
        if not AJAX:
            flash('You are not authorized to do that')
            return None
        else:
            error = {
                'dbStatus': 'error',
                'message': 'Unauthorized access'
            }
            return (False, error)
    if not AJAX:
        return list_data
    else:
        return (True, list_data)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        form = LogIn()
        form.validate()
        error = form.error
        db = get_db()
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (email, password) VALUES (?, ?)",
                    (form.email, generate_password_hash(form.password))
                )
                db.commit()
                user = db.execute(
                    "SELECT * FROM users where email = ?", (form.email,)
                ).fetchone()
                if user is None:
                    return redirect(url_for('auth.login'))
                session.clear()
                session['user_id'] = user['id']
                g.user = user
                return redirect(url_for('home'))
            except db.IntegrityError:
                error = f"Email {form.email} is already registered"
                flash(error)
            return redirect(url_for('auth.register'))
        else:
            flash(error)
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        form = LogIn()
        form.validate()
        error = form.error
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (form.email,)
        ).fetchone()
        if user is None:
            error = 'Incorrect email'
        if not error and not check_password_hash(user['password'], form.password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    g.permissions = permissions
    g.actions = actions
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if g.user:
        db = get_db()
        cart_data = db.execute('SELECT book_id FROM carts WHERE user_id = ?', (g.user['id'],)).fetchall()
        g.cart = [ entry['book_id'] for entry in cart_data ]

@bp.before_app_request
def load_genres():
    db = get_db()
    g.genres = db.execute('SELECT * FROM genres ORDER BY name ASC').fetchall()
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@bp.route('/permissions', methods=('GET', 'POST'))
@login_required
@check_permissions(actions['alter_user_permissions'])
def update_permissions():
    if request.method == 'POST':
        form = AlterPermissions()
        form.validate()
        error = form.error
        if error is None:
            db = get_db()
            user = db.execute('SELECT id FROM users WHERE email = ?', (form.email,)).fetchone()
            if user is None:
                flash('User not found')
                return redirect(url_for('auth.update_permissions'))
            db.execute('UPDATE users SET permissions = ? WHERE id = ?', (form.role, user['id']))
            db.commit()
            flash("User's permissions updated")
            return redirect(url_for('auth.update_permissions'))
        flash(error)
    return render_template('auth/permissions.html', roles=roles)