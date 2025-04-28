from flask import Flask
from extensions import mysql, mail
from core import core
from appointment import appointment  # Import the blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mediconnect_db'
mysql.init_app(app)

# Mail config
mail.init_app(app)

# Register the blueprints
app.register_blueprint(core)
app.register_blueprint(appointment, url_prefix='/appointment')

# Debugging: Print registered blueprints and routes
print("Registered Blueprints:", app.blueprints)
print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)