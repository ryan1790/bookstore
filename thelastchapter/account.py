import functools
from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from thelastchapter.auth import login_required, check_password_hash, generate_password_hash
from thelastchapter.db import get_db
from thelastchapter.utilities import get_books, get_cart, get_order_data, get_order_details

bp = Blueprint('account', __name__, url_prefix='/account')

def get_lists(id):
    db = get_db()
    lists = db.execute('SELECT * FROM list_names WHERE user_id = ?',
    (g.user['id'],)).fetchall()
    if lists is None:
        return None
    return lists

@bp.route('/')
@login_required
def display():
    lists_data = get_lists(g.user['id'])
    if lists_data == None:
        lists = []
    else:
        lists = [ get_books(book_list) for book_list in lists_data ]
    cart = get_cart()
    orders = get_order_data()
    return render_template('account/display.html', lists=lists, cart=cart, orders=orders)

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        old_password = request.form['old-password']
        new_password = request.form['new-password']
        check_password = request.form['check-password']
        error = None
        update_password = len(old_password) != 0
        if update_password:
            if new_password != check_password:
                error = 'Confirmed password did not match!'
            if len(new_password) == 0:
                error = 'Must enter a new password!'
            if error is None and not check_password_hash(g.user['password'], old_password):
                error = 'Original password incorrect'
        if error is None:
            db = get_db()
            if update_password:
                try:
                    db.execute('UPDATE users SET email = ?, username = ?, password = ?'
                            ' WHERE id = ?',
                            (email, username, generate_password_hash(new_password), g.user['id']))
                except db.IntegrityError:
                    error = f"Email {email} is already in use"
            else:
                try:
                    db.execute(
                        'UPDATE users SET email = ?, username = ? WHERE id = ?',
                        (email, username, g.user['id'])
                        )
                except db.IntegrityError as er:
                    error = f"{er}"
            if error is None:
                db.commit()
                user = db.execute('SELECT * FROM users WHERE id = ?', (g.user['id'],)).fetchone()
                g.user = user
        if (error):
            flash(error)
        return redirect(url_for('account.update'))
    return render_template('account/update.html')

@bp.route('/<int:order_id>', methods=('GET', 'POST'))
@login_required
def display_order(order_id):
    order_data, order, address = get_order_details(order_id)
    total = sum([ int(b['quantity']) * float(b['price']) for b in order ])
    display = "{:,.2f}".format(total)
    if request.method == 'POST':
        # remove_order(order_id)
        return redirect(url_for('account.display'))
    return render_template('account/order.html', order_data=order_data, order=order, address=address, total=display)
