import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://absensi_user:12345@localhost/absensi_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secretkey123'
