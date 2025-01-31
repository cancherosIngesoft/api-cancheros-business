import importlib
from flask import Flask
import os

from .config import Config
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
# loading environment variables
load_dotenv()
db = SQLAlchemy()
migrate = Migrate()

config = Config().dev_config

def register_models(models_package: str):

    models_path = os.path.join(os.path.dirname(__file__), models_package.replace('.', '\\'))
    for filename in os.listdir(models_path):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{models_package}.{filename[:-3]}"
            importlib.import_module(module_name)

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuración de la base de datos
    app.config["ENVIRONMENT"] = os.getenv("ENVIRONMENT")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["AUTH0_DOMAIN"] = os.getenv('AUTH0_DOMAIN')
    app.config["AUTH0_CLIENT_ID"] = os.getenv('AUTH0_CLIENT_ID')
    app.config["AUTH0_CLIENT_SECRET"] = os.getenv('AUTH0_CLIENT_SECRET')
    app.config["AUTH0_AUDIENCE"] = os.getenv('AUTH0_AUDIENCE')
    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = os.getenv("EMAIL")
    app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar los modelos o rutas
    with app.app_context():
        # from app.models
        # register_models("models")
        from app.models import Cancha,Duenio,Equipo,Establecimiento,Horario,Horario_establecimiento,Notificacion_estadistica,Notificacion_reserva
        from app.models import Partido,Plantilla,Reporte,Resenia,Reserva,Reservante,Solicitud,Subequipo,Usuario,Admin,Miembro_equipo
        db.create_all()
        from app.routes import register_blueprints
        register_blueprints(app)
    
    @app.route("/")
    def hello_world():
        return "Api cancheros"
    
    return app