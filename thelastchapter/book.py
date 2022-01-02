import functools

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

@bp.route('/<int:id>')
def display(id):
    book = get_book(id)
    return render_template('book/display.html', book=book)
