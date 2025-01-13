
from flask import Blueprint
from app.routes.Solicitud_route import solicitudes_bp
from app.routes.Rol_user import usuarios_bp
from app.routes.Register_cancha import cancha_bp
from app.routes.Register_est import establecimiento_bp

def register_blueprints(app):
    app.register_blueprint(solicitudes_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(cancha_bp, url_prefix='/api')
    app.register_blueprint(establecimiento_bp, url_prefix='/api')