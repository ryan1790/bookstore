from flask import g, session
from thelastchapter.db import get_db
import stripe
from werkzeug.exceptions import abort
from dotenv import dotenv_values
config = dotenv_values('.env')
stripe.api_key = config['STRIPE_SECRET']
stripe_key = config['STRIPE_KEY']

STATES = [ 'AK','AL','AR','AS', 'AZ','CA', 'CM', 'CO', 'CT', 'DC', 'DE', 
'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KY', 'KS', 'LA','MA', 
'MD', 'ME','MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 
'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 
'TT', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY' ]

def res_format(dbStatus, message, list_id=None, list_name=None):
    if not list_id:
        return { 'dbStatus': dbStatus, 'message': message }
    return { 
        'dbStatus': dbStatus, 
        'message': message, 
        'list_id': list_id, 
        'list_name': list_name 
    }

def get_books(list):
    list_owner = list['user_id']
    db = get_db()
    books = db.execute('SELECT * FROM book_lists l JOIN books b ON l.book_id = b.id' +  
    ' WHERE l.list_id = ?', (list['id'],)).fetchall()
    if books is None:
        return None
    return (list['name'], list['id'], books, list_owner)

def get_displayed_lists():
    db = get_db()
    lists = db.execute(
        'SELECT l.id, l.user_id, l.name FROM home_display hd JOIN list_names l ON hd.list_id = l.id'
    ).fetchall()
    return lists

def get_full_displayed_lists():
    list_data = get_displayed_lists()
    lists = [ get_books(entry) for entry in list_data ]
    return lists

def get_cart():
    db = get_db()
    cart = db.execute(
        'SELECT c.id as id, b.id AS book_id, b.title AS title, b.author AS author,' 
        ' b.image AS image, b.price AS price, c.quantity AS quantity, b.stock as stock' 
        ' FROM carts c JOIN books b ON c.book_id = b.id' 
        ' WHERE c.user_id = ? ORDER BY c.id ASC', (g.user['id'],)
    ).fetchall()
    if cart is None:
        return []
    return cart

def get_order_details(order_id):
    db = get_db()
    order_data = db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order_data is None:
        abort(404, "Order not found")
    order = db.execute(
        'SELECT o.book_id, o.price, o.quantity, b.title, b.author' 
        ' FROM order_books o JOIN books b ON o.book_id = b.id'
        ' WHERE o.order_id = ?', (order_id,)
    ).fetchall()
    address = db.execute('SELECT * FROM addresses WHERE id = ?', (order_data['address_id'],)).fetchone()
    return order_data, order, address

def get_order_data(full_fetch=False):
    db = get_db()
    orders = db.execute('SELECT * FROM orders WHERE user_id = ?', (g.user['id'],)).fetchall()
    if full_fetch:
        orders_list = [ get_order_details(o['id']) for o in orders ]
        return orders_list
    return orders

def get_payment_intent(update_intent=True):
    cart = get_cart()
    if len(cart) == 0:
        return None, [], 0, None
    total = int(sum([ int(b['quantity']) * float(b['price']) for b in cart ]) * 100)
    intent_id = session.get('intent_id')
    if intent_id and update_intent or False:
        intent = stripe.PaymentIntent.modify(
            intent_id,
            amount = total
        )
    elif intent_id or False:
        intent = stripe.PaymentIntent.retrieve(intent_id)
    else:
        intent = stripe.PaymentIntent.create(
            amount = total,
            currency = 'usd',
            payment_method_types = ["card"],
            receipt_email = g.user['email']
        )
        session['intent_id'] = intent['id']
    if 'a_id' in intent['metadata']:
        db = get_db()
        a_id = intent['metadata']['a_id']
        address = db.execute('SELECT * FROM addresses WHERE id = ?', (a_id,)).fetchone()
    else:
        address = None
    return intent['client_secret'], cart, intent['amount'], address