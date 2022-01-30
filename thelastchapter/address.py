from flask import ( 
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)
from werkzeug.exceptions import abort
from thelastchapter.db import get_db
from thelastchapter.auth import actions, check_permissions, login_required
from thelastchapter.utilities import res_format, get_cart, STATES, get_order_details
from dotenv import dotenv_values
import stripe

bp = Blueprint('address', __name__, url_prefix='/address')
config = dotenv_values('.env')
stripe.api_key = config['STRIPE_SECRET']
stripe_key = config['STRIPE_KEY']
webhook_secret=config['WEBHOOK_SECRET']

@login_required
def add_address():
    if session.get('intent_id') is None:
        return redirect(url_for('cart.display'))
    intent_id = session.get('intent_id')
    db = get_db()
    if request.method == 'POST':
        form = request.form
        if 'address_id' in form:
            address_id = form['address_id']
        else:
            if 'name' in form:
                name = form['name']
            else:
                name = ''
            city = form['city']
            address = form['address']
            state = form['state']
            country = 'US'
            zip_code = form['zip-code']
            cur = db.cursor()
            cur.execute(
                'INSERT INTO addresses'
                ' (user_id, city, address, zip_code, state, country, name) VALUES'
                ' (?, ?, ?, ?, ?, ?, ?)',
                (g.user['id'], city, address, zip_code, state, country, name)   
            )
            address_id = cur.lastrowid
            db.commit()
        metadata = { 'a_id': address_id }
        stripe.PaymentIntent.modify(intent_id, metadata=metadata)
        return redirect(url_for('cart.checkout'))
    addresses = db.execute('SELECT * FROM addresses WHERE user_id = ?', (g.user['id'],)).fetchall()
    if addresses is None:
        addresses = []
    return render_template('address/address.html', addresses=addresses, states=STATES)

@bp.route('/address/<int:address_id>', methods=('GET', 'POST'))
@login_required
def update_address(address_id):
    db = get_db()
    address = db.execute('SELECT * FROM addresses WHERE id = ?', (address_id,)).fetchone()
    if address is None:
        flash('Address not found')
        return redirect(request.referrer)
    if address['user_id'] != g.user['id']:
        flash('Permission denied')
        return redirect(request.referrer)
    if request.method == 'POST':
        form = request.form
        if 'name' in form:
            name = form['name']
        else:
            name = ''
        city = form['city']
        address = form['address']
        zip_code = form['zip-code']
        state = form['state']
        db.execute(
            'UPDATE addresses SET city=?, address=?, zip_code=?, state=?, name=?'
            ' WHERE id = ?', (city, address, zip_code, state, name, address_id)
            )
        db.commit()
        return redirect(url_for('address.add_address'))
    return render_template('address/update.html', address=address, states=STATES)

@bp.route('/address/<int:address_id>/delete', methods=('POST',))
@login_required
def delete_address(address_id):
    db = get_db()
    address = db.execute('SELECT * FROM addresses WHERE id = ?', (address_id,)).fetchone()
    if address is None:
        flash('Address not found')
        return redirect(url_for('address.add_address'))
    if address['user_id'] != g.user['id']:
        flash('Permission denied')
        return redirect('address.add_address')
    db.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
    db.commit()
    return redirect(url_for('address.add_address'))