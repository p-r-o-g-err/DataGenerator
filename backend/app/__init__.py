from flask import Flask
from flask_cors import CORS
# from flask_caching import Cache

# cache = Cache(config={'CACHE_TYPE': 'redis'})

def create_app():
    app = Flask(__name__)
    # cache.init_app(app)
    CORS(app, resources={r"/*": {'origins': '*'}})

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/dataGenerator?client_encoding==utf8'

    from app.models import db
    db.init_app(app)

    from app.api import (
        auth, generator
    )

    app.register_blueprint(auth.bp)
    app.register_blueprint(generator.bp)
    
    return app

