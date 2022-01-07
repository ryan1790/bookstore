from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.exceptions import abort

from thelastchapter.db import get_db

from thelastchapter.account import get_books

from thelastchapter.auth import login_required

bp = Blueprint('list', __name__, url_prefix='/lists')

def check_existence(list_id, book_id):
    db = get_db()
    book = db.execute('SELECT * from books where id = ?', (book_id,)).fetchone()
    book_list = db.execute('SELECT * from list_names where id = ?', (list_id,)).fetchone()
    if book is None or book_list is None:
        abort(404)
    return None

def res_format(dbStatus, message, list_id=None):
    if not list_id:
        return { 'dbStatus': dbStatus, 'message': message }
    return { 'dbStatus': dbStatus, 'message': message, 'list_id': list_id }

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
    return res_format('success', 'New list successfully created!')

@bp.route('/<int:list_id>')
def display(list_id):
    db = get_db()
    error = None
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if list_data is None:
        error = "Cannot find list."
    if error is None:
        book_list = get_books(list_data)
    if error is None and (book_list is None or book_list[2] is None):
        error = "No books found"
    if error is not None:
        flash(error)
        return redirect(url_for('home'))
    return render_template('list/display.html', book_list=book_list)

@bp.route('/<int:list_id>/update', methods=('GET', 'POST'))
def update(list_id):
    db = get_db()
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if list_data is None:
        flash('List not found')
        return redirect(url_for('account.display'))
    if request.method == 'POST':
        name = request.form['name']
        db.execute('UPDATE list_names SET name=? WHERE id = ?', (name, list_id))
        db.commit()
        return redirect(url_for('list.display', list_id=list_id))
    return render_template('list/update.html', list_data=list_data)

@bp.route('<int:list_id>/delete', methods=('POST',))
def delete(list_id):
    error = None
    db = get_db()
    list_data = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if list_data is None:
        error = "List not found!"
        flash(error)
        return redirect('home')
    db.execute('DELETE FROM book_lists WHERE list_id = ?', (list_id,))
    db.execute('DELETE FROM list_names WHERE id = ?', (list_id,))
    db.commit()
    return redirect(url_for('account.display'))

@bp.route('/<int:list_id>/<int:book_id>/remove', methods=("POST",))
def remove(list_id, book_id):
    check_existence(list_id, book_id)
    db = get_db()
    db.execute('DELETE FROM book_lists WHERE list_id = ? AND book_id = ?', (list_id, book_id))
    db.commit()
    return redirect(url_for('list.display', list_id=list_id))

@bp.route('/<int:list_id>/<int:book_id>/add', methods=("POST",))
def add(list_id, book_id):
    db = get_db()
    book_list = db.execute('SELECT * FROM list_names WHERE id = ?', (list_id,)).fetchone()
    if book_list is None:
        return res_format('error', 'List not found')
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
