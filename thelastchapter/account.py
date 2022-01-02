import functools

from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from thelastchapter.auth import login_required, check_password_hash, generate_password_hash

from werkzeug.exceptions import abort

from thelastchapter.db import get_db

bp = Blueprint('account', __name__, url_prefix='/account')

def get_lists(id):
    db = get_db()
    lists = db.execute('SELECT * FROM list_names WHERE user_id = ?',
    (g.user['id'],)).fetchall()
    if lists is None:
        return None
    return lists

def get_books(list):
    db = get_db()
    books = db.execute('SELECT * from book_lists l JOIN books b ON l.book_id = b.id' +  
    ' WHERE l.list_id = ?', (list['id'],)).fetchall()
# SELECT * from book_lists l JOIN books b ON l.book_id = b.id WHERE l.list_id = 1
    if books is None:
        return None
    return (list['name'], list['id'], books)

@bp.route('/')
@login_required
def display():
    lists_data = get_lists(g.user['id'])
    if lists_data == None:
        lists = []
    else:
        lists = [ get_books(list) for list in lists_data ]
    return render_template('account/display.html', lists=lists)

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        old_password = request.form['old-password']
        check_password = request.form['check-password']
        new_password = request.form['new-password']
        print('\n\n\n', email, username, old_password, check_password, new_password, '\n\n\n')
        error = None
        if new_password != check_password:
            error = 'Confirmed password did not match!'
        if error is None and not check_password_hash(g.user['password'], old_password):
            error = 'Original password incorrect'
        if error is None:
            db = get_db()
            try:
                db.execute('UPDATE users SET email = ?, username = ?, password = ?'
                        'WHERE id = ?',
                        (email, username, generate_password_hash(new_password), g.user['id']))
                db.commit()
                user = db.execute('SELECT * FROM users WHERE id = ?', (g.user['id'],)).fetchone()
                g.user = user
            except db.IntegrityError:
                error = f"Email {email} is already in use"
            else:
                return redirect(url_for('account.display'))
        flash(error)
        return redirect(url_for('account.update'))
    return render_template('account/update.html')