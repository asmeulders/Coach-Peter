from flask import Flask
from coach_peter.db import db


def create_app(config_name="testing"):
    app = Flask(__name__)
    
    # Example test config — adjust for your project
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = True

    db.init_app(app)

    return app
