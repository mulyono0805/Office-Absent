from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Absensi(db.Model):
    __tablename__ = 'absensi'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_time = db.Column(db.DateTime, default=None)
    checkout_time = db.Column(db.DateTime, default=None)
    latitude = db.Column(db.Float, default=None)
    longitude = db.Column(db.Float, default=None)
    image_path = db.Column(db.String(200), default=None)

    user = db.relationship('User', backref='absensi')

