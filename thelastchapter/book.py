from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from thelastchapter.db import get_db
from thelastchapter.auth import actions, check_permissions, login_required

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
        error = None
        title = request.form['title']
        author = request.form['author']
        info = request.form['info']
        price = request.form['price']
        isbn = request.form['isbn']
        image = request.form['image']
        published = request.form['published']
        lang = request.form['lang']
        pages = request.form['pages']
        stock = request.form['stock']
        genre_id = request.form['genre']
        if title is None or author is None or info is None or price is None or isbn is None or image is None or lang is None or genre_id is None:
            error = "Must fill in all required fields!"
            flash(error)
            return redirect(url_for('book.create'))
        db = get_db()
        data = db.execute('SELECT name FROM genres WHERE id = ?', (genre_id,)).fetchone()
        if data is None:
            abort(404, "Genre not found")
        genre = data['name']
        cursor = db.cursor()
        cursor.execute('INSERT INTO books (title, author, image, published, genre, genre_id, info, lang, pages, isbn, stock, price)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (title, author, image, published, genre, genre_id, info, lang, pages, isbn, stock, price))
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
        error = None
        title = request.form['title']
        author = request.form['author']
        info = request.form['info']
        stock = request.form['stock']
        price = request.form['price']
        isbn = request.form['isbn']
        image = request.form['image']
        published = request.form['published']
        lang = request.form['lang']
        pages = request.form['pages']
        genre_id = request.form['genre']
        if title is None or author is None or info is None or price is None or isbn is None or image is None or lang is None or genre_id is None:
            error = "Must fill in all required fields!"
            flash(error)
            return redirect(url_for('book.update'))
        book = get_book(id)
        db = get_db()
        data = db.execute('SELECT name FROM genres WHERE id = ?', (genre_id,)).fetchone()
        if data is None:
            abort(404, 'Genre not found')
        genre = data['name']
        db.execute('UPDATE books SET title=?, author=?, image=?, published=?, genre=?, genre_id=?, info=?, lang=?, pages=?, isbn=?, stock=?, price=? WHERE id = ?',
            (title, author, image, published, genre, genre_id, info, lang, pages, isbn, stock, price, id))
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