from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'iniciar_sesion'

from app import routes  # Importar al final para evitar problemas de importación

if __name__ == '__main__':
    app.run(debug=True)
