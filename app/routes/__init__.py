
from flask import Blueprint
from app.routes.SolicitudRoute import solicitudes_bp

def register_blueprints(app):
    app.register_blueprint(solicitudes_bp, url_prefix='/api')
