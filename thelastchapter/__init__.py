from flask import Flask, render_template
import os
from thelastchapter.utilities import get_full_displayed_lists

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            SECRET_KEY='dev',
            DATABASE=os.path.join(app.instance_path, 'tlc.sqlite')
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db

    db.init_app(app)

    @app.route('/')
    def home():
        lists = get_full_displayed_lists()
        return render_template('home.html', lists=lists)

    from thelastchapter import auth, book, book_list, account, cart, category, address
    app.register_blueprint(auth.bp)
    app.register_blueprint(account.bp)
    app.register_blueprint(book.bp)
    app.register_blueprint(book_list.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(category.bp)
    app.register_blueprint(address.bp)
    app.add_url_rule('/search', 'search', category.search)
    app.add_url_rule('/stripe', 'my_webhook_view', cart.my_webhook_view, methods=('POST',))
    app.add_url_rule('/cart/checkout/address', 'address.add_address', address.add_address, methods=('GET', 'POST'))

    return app