from app.models.Solicitud import Solicitud
from flask import request, Blueprint, jsonify
from flask_restful import Api, Resource

solicitudes_bp = Blueprint('solicitud', __name__)

@solicitudes_bp.route('/solicitud', methods = ['GET'])
def get_solicitud():
    solicitudes = Solicitud.query.all()
    solicitudes_serializados = [
        {"id": solicitud.id_solicitud, "nombre": solicitud.nombre_duenio, "email": solicitud.email_duenio}
        for solicitud in solicitudes
    ]
    return jsonify(solicitudes_serializados)


