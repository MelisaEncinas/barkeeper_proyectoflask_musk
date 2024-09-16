from flask import Flask
from flask_login import LoginManager
from app import db

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Importar las rutas después de crear la instancia de la aplicación
from app import routes

# Configurar la base de datos si la tienes (este es solo un ejemplo)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
