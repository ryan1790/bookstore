from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from thelastchapter.db import get_db

from thelastchapter.auth import actions, check_permissions, login_required

from thelastchapter.book_list import res_format

bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_cart():
    db = get_db()
    cart = db.execute(
        'SELECT b.id AS book_id, b.title AS title, b.author AS author,' 
        ' b.image AS image, b.price AS price, c.quantity AS quantity' 
        ' FROM carts c JOIN books b ON c.book_id = b.id' 
        ' WHERE c.user_id = ? ORDER BY c.id ASC', (g.user['id'],)
    ).fetchall()
    if cart is None:
        return []
    return cart

def check_in_cart(book_id):
    db = get_db()
    book = db.execute(
        'SELECT * FROM carts WHERE user_id = ? AND book_id = ?',
        (g.user['id'], book_id)
    ).fetchone()
    return book

@bp.route('/')
@login_required
def display():
    print(g.cart)
    cart = get_cart()
    total = round(sum([ float(book['price']) * float(book['quantity']) for book in cart ]), 2)
    display = "{:,.2f}".format(total)
    return render_template('cart/display.html', cart=cart, total=display)

@bp.route('/update/<checkout>', methods=('POST',))
@login_required
def update(checkout):
    db = get_db()
    values = request.form
    # make sure keys are just numbers/strings of numbers?
    for key in values:
        if values[key]  == '0':
            db.execute(
                'DELETE FROM carts WHERE user_id = ? AND book_id = ?',
                (g.user['id'], key)
            )
        else:
            db.execute(
                'UPDATE carts SET quantity = ? WHERE user_id = ? AND book_id = ?',
                (values[key], g.user['id'], key)
            )
    db.commit()
    if checkout == "True":
        return redirect(url_for('cart.display'))
    else:
        return redirect(url_for('cart.display'))

@bp.route('/<int:book_id>/add', methods=('POST',))
@login_required
def add(book_id):
    check = check_in_cart(book_id)
    if check is not None:
        return res_format('error', 'Book already in cart!')
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    if book is None:
        return res_format('error', 'Book not found')
    db.execute(
        'INSERT INTO carts (user_id, book_id, quantity)'
        ' VALUES (?, ?, ?)', (g.user['id'], book_id, 1)
    )
    db.commit()
    return res_format('success', 'Book added to cart!')

@bp.route('/<int:book_id>/remove', methods=('POST',))
@login_required
def remove(book_id):
    check = check_in_cart(book_id)
    error = None
    if check is None:
        flash('Book not in cart')
        error = True
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,))
    if book is None and error is None:
        flash('Book not found')
        error = True
    if error is None:
        db.execute(
            'DELETE FROM carts WHERE'
            ' user_id = ? AND book_id = ?', (g.user['id'], book_id)
        )
        db.commit()
    return redirect(url_for('cart.display'))


