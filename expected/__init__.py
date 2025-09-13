from flask import Flask, render_template
from .auth import login_required

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import imarine
    app.register_blueprint(imarine.bp)

    from . import imarin_
    app.register_blueprint(imarin_.bp)

    from . import agnes4
    app.register_blueprint(agnes4.bp)

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app