from enum import Enum
from app.models.Solicitud import Solicitud
from app.utils.cloud_storage import upload_file, upload_to_gcs
from .. import db
from app.schemas.schemas import SolicitudSchema
from flask import request, Blueprint, jsonify
from flask_restful import Api, Resource

solicitudes_bp = Blueprint('requests', __name__)
solicitud_schema = SolicitudSchema()
requests_schema = SolicitudSchema(only=("id_solicitud",
                "nombre_duenio",
                "email_duenio",
                "tel_duenio",
                "nombre_est",
                "direccion"), many=True)
solicitudes_schema = SolicitudSchema(many=True)

status = {
    "valid_statuses_query" : ['pending', 'rejected', 'approved'],
    "status" : {
        'pending': None,
        'rejected': False,
        'approved': True
    }
}

@solicitudes_bp.route('/requests', methods = ['GET'])
def get_solicitudes():
    status_param = request.args.get('status')
    solicitudes = None
    if not status_param:
        solicitudes = Solicitud.query.all()
    else:
        print(status_param)
        if status_param in status["valid_statuses_query"]:
             
            solicitudes = Solicitud.query.filter(Solicitud.resultado == status["status"][status_param]).all()
            
    solicitudes_serializados = [
        {"id": solicitud.id_solicitud, "nombre": solicitud.nombre_duenio, "email": solicitud.email_duenio}
        for solicitud in solicitudes
    ]
    return requests_schema.dump(solicitudes), 200

@solicitudes_bp.route('/requests/<int:solicitud_id>', methods = ['GET'])
def get_solicitud(solicitud_id):
    try:

        solicitud = Solicitud.query.get(solicitud_id)
        
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@solicitudes_bp.route('/requests', methods = ['POST'])
def create_solicitud():
    try:
        data = request.get_json()
        solicitud_data = solicitud_schema.load(data)
        solicitud_data["ya_procesada"] = False
        direccion = solicitud_data["direccion"]

        if not direccion:
            return jsonify({"error": "Nombre y email son requeridos"}), 400

        nueva_solicitud = Solicitud(**solicitud_data)

        db.session.add(nueva_solicitud)
        db.session.commit()

        return solicitud_schema.dump(nueva_solicitud), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@solicitudes_bp.route('/requests/upload-rut', methods = ['POST'])
def upload_rut(solicitud_id):
    try:

        solicitud = Solicitud.query.get(solicitud_id)
        if not solicitud:
            return jsonify({"error": "Solicitud no encontrada"}), 404
        
        file = request.files["file"]
        file_data = file.read()
        file_name = file.filename
        
        if not file:
            return jsonify({"error": "No se ha subido ningún archivo"}), 400

        file_url = upload_to_gcs(file_data, file_name)
        solicitud.rut = file_url
        db.session.commit()
        return "Exitoso", 200
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


