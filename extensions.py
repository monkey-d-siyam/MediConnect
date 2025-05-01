# extensions.py
from flask_mysqldb import MySQL
from flask_mail import Mail
from flask_caching import Cache

mysql = MySQL()
mail = Mail()
cache = Cache()
