from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

# Crear instancia de db SIN asociarla a una app a?n
db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    db.init_app(app)
    return db
