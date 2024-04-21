from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {'origins': '*'}})

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/dataGenerator?client_encoding==utf8'

    from app.models import db
    db.init_app(app)

    from app.api import (
        test, auth
    )

    app.register_blueprint(test.bp)
    app.register_blueprint(auth.bp)

    return app

