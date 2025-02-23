
from flask import Blueprint
from app.routes.Solicitud_route import solicitudes_bp
from app.routes.Rol_user import usuarios_bp
from app.routes.Establecimientos_route import establecimiento_bp
from app.routes.Horarios_route import horarios_bp
from app.routes.Reservas_route import reservas_bp
from app.routes.Clubes_route import clubes_bp
from app.routes.Subequipo_route import subequipo_bp
from app.routes.Equipo_route import equipo_bp
from app.routes.Partido_route import partido_bp
from app.routes.Payment_route import payment_bp
from app.routes.Duenios_route import duenios_bp
from app.routes.Notificaciones_route import notificaciones_bp

def register_blueprints(app):
    app.register_blueprint(solicitudes_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(establecimiento_bp, url_prefix='/api')
    app.register_blueprint(horarios_bp, url_prefix='/api')
    app.register_blueprint(reservas_bp, url_prefix='/api')
    app.register_blueprint(clubes_bp, url_prefix='/api')
    app.register_blueprint(subequipo_bp, url_prefix='/api')
    app.register_blueprint(payment_bp, url_prefix='/api')
    app.register_blueprint(equipo_bp, url_prefix='/api')
    app.register_blueprint(partido_bp, url_prefix='/api')
    app.register_blueprint(duenios_bp, url_prefix='/api')
    app.register_blueprint(notificaciones_bp, url_prefix='/api')
