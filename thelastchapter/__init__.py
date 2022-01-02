from flask import Flask, render_template
import os

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
        return render_template('home.html')

    from thelastchapter import auth, book, account
    app.register_blueprint(account.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(book.bp)

    return app