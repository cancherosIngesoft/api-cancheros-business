
from flask import Blueprint
from app.routes.Solicitud_route import solicitudes_bp
from app.routes.Rol_user import usuarios_bp
from app.routes.Establecimientos_route import establecimiento_bp
from app.routes.Horarios_route import horarios_bp
from app.routes.Reservas_route import reservas_bp
from app.routes.Clubes_route import clubes_bp
from app.routes.Payment_route import payment_bp

def register_blueprints(app):
    app.register_blueprint(solicitudes_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(establecimiento_bp, url_prefix='/api')
    app.register_blueprint(horarios_bp, url_prefix='/api')
    app.register_blueprint(reservas_bp, url_prefix='/api')
    app.register_blueprint(clubes_bp, url_prefix='/api')
    app.register_blueprint(payment_bp, url_prefix='/api')