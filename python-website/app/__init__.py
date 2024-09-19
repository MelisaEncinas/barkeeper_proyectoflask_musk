from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configurar la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
db = SQLAlchemy(app)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes  # Importar las rutas después de crear la instancia de la aplicación
