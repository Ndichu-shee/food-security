from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    """Initialize the database with the app."""
    db.init_app(app)
