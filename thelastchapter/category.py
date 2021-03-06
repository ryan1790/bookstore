from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from thelastchapter.db import get_db
from math import ceil

bp = Blueprint('category', __name__, url_prefix='/genre')
LIMIT = 8

def get_by_genre(genre_id, page=1):
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    db = get_db()
    genre = db.execute('SELECT * FROM genres WHERE id = ?', (genre_id,)).fetchone()
    if genre is None:
        return None
    cur = db.cursor()
    data = cur.execute('SELECT COUNT(id) as count FROM books WHERE genre_id = ?' ,(genre_id,)).fetchone()
    count = data['count']
    if count == 0:
        return None, genre
    lastpage = ceil(count/LIMIT)
    if page > lastpage:
        page = lastpage
    if page == 1:
        cutoff = { 'title': '', 'id': 0 }
    else:
        offset = LIMIT * (page - 1) - 1
        cutoff = db.execute(
            'SELECT id, title FROM books WHERE genre_id = ?'
            ' ORDER BY title ASC, id ASC LIMIT 1 OFFSET ?',
            (genre_id, offset)
        ).fetchone()
    books = db.execute(
        'SELECT id, title, author, price, stock, image'
        ' FROM books WHERE genre_id = ? AND (title, id) > ( ?, ? ) ORDER BY title, id'
        ' LIMIT ?'
        , (genre_id, cutoff['title'], cutoff['id'], LIMIT)
    ).fetchall()
    return genre, books, page, lastpage

def get_search_results(query, page=1):
    split = query.split(' ')
    adjusted_query = ''
    for entry in split:
        if len(adjusted_query) == 0:
            adjusted_query = f'"{entry}"'
        else:
            adjusted_query = f'{adjusted_query} "{entry}"'
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    db = get_db()
    cur = db.cursor()
    data = cur.execute(
        'SELECT COUNT(rowid) as count, MIN(rank) as rank'
        ' FROM books_fts WHERE books_fts MATCH ?', (adjusted_query,)
    ).fetchone()
    count = data['count']
    lastpage = ceil(count/LIMIT)
    if data['rank'] is None:
        return [], page, lastpage
    if page == 1:
        cutoff = { 'rank': data['rank'] - 1, 'id': 0 }
    else:
        offset = LIMIT * (page - 1) - 1
        cutoff = db.execute(
            'SELECT rowid as id, rank FROM books_fts WHERE books_fts MATCH ?'
            ' ORDER BY rank ASC, id ASC LIMIT 1 OFFSET ?',
            (adjusted_query, offset)
        ).fetchone()
    books = db.execute(
        'SELECT b.author, b.title, b.image, b.stock, b.price, b.id'
        ' FROM books_fts JOIN books b ON books_fts.rowid = b.id'
        ' WHERE books_fts MATCH ? AND (rank, id) > (?, ?)'
        ' ORDER BY rank ASC, id ASC LIMIT ?',
        (adjusted_query, cutoff['rank'], cutoff['id'], LIMIT)
    ).fetchall()
    if books is None:
        books = []
    return books, page, lastpage


@bp.route('/<int:genre_id>')
def display(genre_id):
    args = request.args
    if 'page' in args:
        page = args['page']
    else:
        page = 1
    data = get_by_genre(genre_id, page)
    print('\n\n\n', data, '\n\n\n')
    if data is None:
        flash('Genre not found. Double check URL if entered manually')
        return redirect(url_for('home'))
    if data[0] == None:
        _, genre = data
        books, page, lastpage = [], 1, 1
    else:
        genre, books, page, lastpage = data
    return render_template('category/display.html', genre=genre, books=books, page=page, lastpage=lastpage)
    
def search():
    args = request.args
    if 'query' not in args:
        print('um')
        return redirect(url_for('home'))
    if 'page' in args:
        page = args['page']
    else:
        page = 1
    query = args['query']
    if len(query) == 0:
        flash('Must enter a query to search')
        return redirect(url_for('home'))
    books, page, lastpage = get_search_results(query, page)
    return render_template('category/search.html', query=query, books=books, page=page, lastpage=lastpage)