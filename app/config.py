import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "veryverysusthatyourareloolingformysecretkey")

    # MySQL Config
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'mediconnect_db'

    # Session Lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # Mail Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')  # onlywebs3500@gmail.com
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # abcd1234
