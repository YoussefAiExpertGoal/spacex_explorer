from flask import Flask
from flask_caching import Cache
from config import Config

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    cache.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app