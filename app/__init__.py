from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager 
from dotenv import load_dotenv
from .routes import main 
import os

from .database import db

migrate = Migrate()
jwt = JWTManager()

def create_app():
    load_dotenv()  

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY") 

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    with app.app_context():
        from . import models 
        db.create_all() 
        app.register_blueprint(main)  


    return app
