from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from thelastchapter.db import get_db

bp = Blueprint('book', __name__, url_prefix='/books')

def get_book(id):
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (id,)
    ).fetchone()
    if book is None:
        abort(404, f"Book id {id} doesn't exist.")
    return book

@bp.route('/create', methods=('GET', 'POST'))
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
        genre = request.form['genre']
        if title is None or author is None or info is None or price is None or isbn is None or image is None or lang is None or genre is None:
            error = "Must fill in all required fields!"
            flash(error)
            return redirect(url_for('book.create'))
        db = get_db()
        cursor = db.cursor()
        # will be
        # db.execute('INSERT INTO books (title, author, image, published, genre, info, lang, pages, isbn, price)'
        #             ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
        #             (title, author, image, published, genre, info, lang, pages, isbn, price))
        # current
        cursor.execute('INSERT INTO books (title, author, image, published, genre, info, lang, pages, price)'
                    ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (title, author, image, published, genre, info, lang, pages, price))
        db.commit()
        return redirect(url_for('book.display', id=cursor.lastrowid))
    return render_template('book/create.html')

@bp.route('/<int:id>')
def display(id):
    book = get_book(id)
    return render_template('book/display.html', book=book)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    book = get_book(id)
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
        genre = request.form['genre']
        if title is None or author is None or info is None or price is None or isbn is None or image is None or lang is None or genre is None:
            error = "Must fill in all required fields!"
            flash(error)
            return redirect(url_for('book.update'))
        book = get_book(id)
        db = get_db()
        # will be
        # db.execute('UPDATE books SET title=?, author=?, image=?, published=?, genre=?, info=?, lang=?, pages=?, isbn=?, price=? WHERE id = ?',
        #     (title, author, image, published, genre, info, lang, pages, isbn, price, id))
        # current
        db.execute('UPDATE books SET title=?, author=?, image=?, published=?, genre=?, info=?, lang=?, pages=?, price=? WHERE id = ?',
            (title, author, image, published, genre, info, lang, pages, price, id))
        db.commit()
        return redirect(url_for('book.display', id=book['id']))
    return render_template('book/update.html', book=book)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    book = get_book(id)
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (id,))
    db.execute('DELETE FROM book_lists WHERE book_id = ?', (id,))
    db.commit()
    flash(f'Deleted entry for {book["title"]}')
    return redirect(url_for('account.display'))