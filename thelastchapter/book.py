from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from thelastchapter.db import get_db
from thelastchapter.auth import actions, check_permissions, login_required
from thelastchapter.validation.book_validation import NewBook

bp = Blueprint('book', __name__, url_prefix='/books')

def get_book(id):
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (id,)
    ).fetchone()
    if book is None:
        abort(404, f"Book id {id} doesn't exist.")
    return book

def get_list_data(user_id):
    db = get_db()
    lists = db.execute('SELECT * FROM list_names WHERE user_id = ?', (user_id,)).fetchall()
    return lists

@bp.route('/create', methods=('GET', 'POST'))
@login_required
@check_permissions(actions['create_book'])
def create():
    if request.method == 'POST':
        form = NewBook()
        form.validate()
        error = form.error
        if error:
            flash(error)
            return redirect(url_for('book.create'))
        db = get_db()
        data = db.execute('SELECT name FROM genres WHERE id = ?', (form.genre_id,)).fetchone()
        if data is None:
            abort(404, "Genre not found")
        genre = data['name']
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO books (title, author, image, published, genre, genre_id, info, lang, pages, isbn, stock, price)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
            (form.title, form.author, form.image, form.published, genre, form.genre_id,
            form.info, form.lang, form.pages, form.isbn, form.stock, form.price)
        )
        db.commit()
        return redirect(url_for('book.display', id=cursor.lastrowid))
    return render_template('book/create.html')

@bp.route('/<int:id>')
def display(id):
    book = get_book(id)
    if g.user:
        lists = get_list_data(g.user['id'])
    else: lists = []
    return render_template('book/display.html', book=book, lists=lists)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@check_permissions(actions['update_book'])
def update(id):
    book = get_book(id)
    if request.method == 'POST':
        form = NewBook()
        form.validate()
        error = form.error
        
        if error:
            flash(error)
            return redirect(url_for('book.update', id=book['id']))
        book = get_book(id)
        db = get_db()
        data = db.execute('SELECT name FROM genres WHERE id = ?', (form.genre_id,)).fetchone()
        if data is None:
            abort(404, 'Genre not found')
        genre = data['name']
        db.execute(
            'UPDATE books SET title = ?, author = ?, image = ?, published = ?, genre = ?, genre_id= ?,'
            ' info = ?, lang = ?, pages = ?, isbn = ?, stock = ?, price = ? WHERE id = ?',
            (form.title, form.author, form.image, form.published, genre, form.genre_id, 
            form.info, form.lang, form.pages, form.isbn, form.stock, form.price, id)
        )
        # db.execute(
        #     'UPDATE books SET title = ?, author = ?, image = ?, published = ?, genre = ?, genre_id= ?,'
        #     ' info = ?, lang = ?, pages = ?, isbn = ?, stock = ?, price = ? WHERE id = ?',
        #     ('Free Love', "Tessa Hadley", 'https://cdn.pixabay.com/photo/2017/03/31/15/35/leaves-2191649_1280.jpg', '', 'Classics', 8, 
        #     'form.info', 'English', 44, '9780063137776', 33, '5.20', id)
        # )
        db.commit()
        return redirect(url_for('book.display', id=book['id']))
    return render_template('book/update.html', book=book)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
@check_permissions(actions['delete_book'])
def delete(id):
    book = get_book(id)
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (id,))
    db.execute('DELETE FROM book_lists WHERE book_id = ?', (id,))
    db.commit()
    flash(f'Deleted entry for {book["title"]}')
    return redirect(url_for('account.display'))