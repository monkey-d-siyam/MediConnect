# extensions.py
from flask_mysqldb import MySQL
from flask_mail import Mail
from flask_caching import Cache

mysql = MySQL()

def init_app(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'jubor'
    app.config['MYSQL_PASSWORD'] = 'password'  # Replace with the correct password
    app.config['MYSQL_DB'] = 'mediconnect_db'        # Replace with your database name
    mysql.init_app(app)
mail = Mail()
cache = Cache()
