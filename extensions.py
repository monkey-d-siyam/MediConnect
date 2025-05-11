# extensions.py
from flask_mysqldb import MySQL
from flask_mail import Mail
from flask_caching import Cache
from flask_socketio import SocketIO

mysql = MySQL()
socketio = SocketIO()

def init_app(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'  # MySQL username
    app.config['MYSQL_PASSWORD'] = ''  # MySQL password (empty string)
    app.config['MYSQL_DB'] = 'mediconnect_db'  # Database name
    mysql.init_app(app)

mail = Mail()
cache = Cache()
