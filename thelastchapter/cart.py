from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.exceptions import abort
from thelastchapter.db import get_db
from thelastchapter.auth import actions, check_permissions, login_required
from thelastchapter.utilities import (
    res_format, get_cart, STATES, get_order_details, get_payment_intent
)
from dotenv import dotenv_values
import stripe

bp = Blueprint('cart', __name__, url_prefix='/cart')
config = dotenv_values('.env')
stripe.api_key = config['STRIPE_SECRET']
stripe_key = config['STRIPE_KEY']
webhook_secret=config['WEBHOOK_SECRET']

def check_in_cart(book_id):
    db = get_db()
    book = db.execute(
        'SELECT * FROM carts WHERE user_id = ? AND book_id = ?',
        (g.user['id'], book_id)
    ).fetchone()
    return book

def cart_to_order(pi_id, address_id):
    cart = get_cart()
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'INSERT INTO orders (user_id, address_id, payment_id) VALUES (?, ?, ?)',
        (g.user['id'], address_id, pi_id)
    )
    order_id = cur.lastrowid
    for b in cart:
        db.execute(
            'INSERT INTO order_books (order_id, book_id, quantity, price)'
            ' VALUES (?, ?, ?, ?)', (order_id, b['book_id'], b['quantity'], b['price'])
        )
        db.execute('DELETE FROM carts WHERE id = ?', (b['id'],))
    db.commit()
    return get_order_details(order_id)

@bp.route('/')
@login_required
def display():
    _, cart, total, _ = get_payment_intent()
    display = "{:,.2f}".format(total/100)
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
        return redirect(url_for('address.add_address'))
    else:
        return redirect(url_for('cart.display'))

@bp.route('/checkout')
@login_required
def checkout():
    client_secret, cart, total, address = get_payment_intent()

    return render_template( 'cart/checkout.html', 
        client_secret=client_secret, 
        cart=cart, 
        total=total, 
        address=address,
        stripe_key=stripe_key
    )

@bp.route('/checkout/status')
@login_required
def status():
    args = request.args
    if 'payment_intent_client_secret' not in args and 'payment_intent' not in args:
        return redirect(url_for('cart.display'))
    client_secret = args['payment_intent_client_secret']
    pi_id = args['payment_intent']
    intent = stripe.PaymentIntent.retrieve(pi_id)
    if intent is None:
        return redirect(url_for('cart.display'))
    if intent['status'] == 'succeeded':
        total = intent['amount']
        db = get_db()
        order = db.execute(
            'SELECT id FROM orders WHERE user_id=? AND payment_id=?',
            (g.user['id'], pi_id)
        ).fetchone()
        if order is None:
            order_data, order, address = cart_to_order(pi_id, intent.metadata['a_id']) # double check this
            session['intent_id'] = None
        else:
            order_data, order, address = get_order_details(order['id'])

    return render_template(
        'cart/status.html', 
        order_data=order_data,
        order=order,
        address=address,
        total=total,
        client_secret=client_secret,
        stripe_key=stripe_key
    )

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
