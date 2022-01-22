from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from thelastchapter.db import get_db

from thelastchapter.account import get_books

from thelastchapter.auth import (
    login_required, check_permissions, permissions, check_list_ownership, actions
)

bp = Blueprint('list', __name__, url_prefix='/lists')

def get_displayed_lists():
    db = get_db()
    lists = db.execute(
        'SELECT l.id, l.user_id, l.name FROM home_display hd JOIN list_names l ON hd.list_id = l.id'
    ).fetchall()
    return lists

def get_books(list):
    list_owner = list['user_id']
    db = get_db()
    books = db.execute('SELECT * FROM book_lists l JOIN books b ON l.book_id = b.id' +  
    ' WHERE l.list_id = ?', (list['id'],)).fetchall()
# SELECT * from book_lists l JOIN books b ON l.book_id = b.id WHERE l.list_id = 1
    if books is None:
        return None
    return (list['name'], list['id'], books, list_owner)

def get_full_displayed_lists():
    list_data = get_displayed_lists()
    lists = [ get_books(entry) for entry in list_data ]
    return lists

def check_existence(list_id, book_id):
    db = get_db()
    book = db.execute('SELECT * from books where id = ?', (book_id,)).fetchone()
    book_list = db.execute('SELECT * from list_names where id = ?', (list_id,)).fetchone()
    if book is None or book_list is None:
        abort(404)
    return None

def res_format(dbStatus, message, list_id=None, list_name=None):
    if not list_id:
        return { 'dbStatus': dbStatus, 'message': message }
    return { 'dbStatus': dbStatus, 'message': message, 'list_id': list_id, 'list_name': list_name }

@bp.route('/create', methods=('POST',))
@login_required
def create():
    name = request.form['name']
    book_id = request.form['book-id']
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    if book is None:
        return res_format('error', 'Book not found')
    cursor = db.cursor()
    cursor.execute('INSERT INTO list_names (user_id, name) VALUES( ?, ? )', (g.user['id'], name))
    list_id = cursor.lastrowid
    cursor.execute('INSERT INTO book_lists (list_id, book_id) VALUES ( ?, ? )',
        (list_id, book_id))
    db.commit()
    return res_format('success', 'New list successfully created!', list_id, name)

@bp.route('/display')
@login_required
@check_permissions(actions['update_home_list'])
def update_display():
    db = get_db()
    lists = get_displayed_lists()
    used = [ entry['id'] for entry in lists ]
    user_lists = db.execute('SELECT * FROM list_names WHERE user_id = ?', (g.user['id'],)).fetchall()
    return render_template('/list/updateDisplay.html', lists=lists, user_lists=user_lists, used=used)

@bp.route('/display/remove/<int:list_id>', methods=('POST',))
@login_required
@check_permissions(actions['update_home_list'])
def home_remove(list_id):
    error = None
    db = get_db()
    list_data = db.execute('SELECT * FROM home_display WHERE list_id = ?', (list_id,)).fetchone()
    if list_data is None:
        flash('List not found in display')
        error = True
    if not error:
        db.execute('DELETE FROM home_display WHERE list_id = ?', (list_id,))
        db.commit()
    return redirect(url_for('list.update_display'))

@bp.route('/display/add/<int:list_id>', methods=('POST',))
@login_required
@check_permissions(actions['update_home_list'])
def home_add(list_id):
    error = None
    db = get_db()
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    list_on_display = db.execute('SELECT * FROM home_display WHERE list_id = ?', (list_id,)).fetchone()
    if list_data is None:
        flash('List not found')
        error = True
    if list_on_display and error is None:
        flash('List already displayed!')
        error = True
    if not error:
        db.execute('INSERT INTO home_display (list_id) VALUES (?)', (list_id,))
        db.commit()
    return redirect(url_for('list.update_display'))
    

@bp.route('/<int:list_id>')
def display(list_id):
    db = get_db()
    error = None
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if list_data is None:
        error = "Cannot find list."
    if error is None:
        book_data = get_books(list_data)
    if error is None and (book_data is None or book_data[2] is None):
        error = "No books found"
    if error is not None:
        flash(error)
        return redirect(url_for('home'))
    list_name, list_id, books, list_owner = book_data
    return render_template('list/display.html', 
        list_name=list_name, 
        list_id=list_id,
        books=books,
        list_owner=list_owner
    )

@bp.route('/<int:list_id>/update', methods=('GET', 'POST'))
@login_required
def update(list_id):
    list_data = check_list_ownership(list_id)
    if list_data is None:
        return redirect(request.referrer)
    if request.method == 'POST':
        db = get_db()
        name = request.form['name']
        db.execute('UPDATE list_names SET name=? WHERE id = ?', (name, list_id)).fetchone()
        db.commit()
        return redirect(url_for('list.display', list_id=list_id))
    return render_template('list/update.html', list_data=list_data)

@bp.route('<int:list_id>/delete', methods=('POST',))
def delete(list_id):
    check_list_ownership(list_id)
    db = get_db()
    db.execute('DELETE FROM book_lists WHERE list_id = ?', (list_id,))
    db.execute('DELETE FROM list_names WHERE id = ?', (list_id,))
    db.commit()
    return redirect(url_for('account.display'))

@bp.route('/<int:list_id>/<int:book_id>/remove', methods=("POST",))
def remove(list_id, book_id):
    check_list_ownership(list_id)
    db = get_db()
    db.execute('DELETE FROM book_lists WHERE list_id = ? AND book_id = ?', (list_id, book_id))
    db.commit()
    return redirect(url_for('list.display', list_id=list_id))

@bp.route('/<int:list_id>/<int:book_id>/add', methods=("POST",))
def add(list_id, book_id):
    cont, data = check_list_ownership(list_id, True)
    if not cont:
        return data
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    if book is None:
        return res_format('error', 'Book not found')
    book_in_list = db.execute('SELECT * FROM book_lists WHERE list_id = ? AND book_id = ?',
    (list_id, book_id)).fetchone()
    if book_in_list is not None:
        return res_format('error', 'Book already in list!')
    db.execute('INSERT INTO book_lists (list_id, book_id) VALUES (?, ?)',
    (list_id, book_id))
    db.commit()
    
    return res_format('success', 'Book added to list!')

