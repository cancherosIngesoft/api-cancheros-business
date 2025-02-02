from datetime import datetime
from enum import Enum
from app.models.Duenio import Duenio
from app.models.Solicitud import Solicitud
from app.utils.auth_0 import create_auth_user
from app.utils.cloud_storage import upload_file, upload_to_gcs
from app.utils.mailing import send_auth_mail, send_rejected_mail
from app.routes.Establecimientos_route import post_establecimiento
from .. import db
from app.schemas.Solicitud_sch import SolicitudBaseSchema, SolicitudSchema
from flask import request, Blueprint, jsonify
from flask_restful import Api, Resource
from flasgger import swag_from

solicitudes_bp = Blueprint('requests', __name__)
solicitud_schema =  SolicitudSchema(only=["id_solicitud",
                "comentario_rechazo",
                "personalInfo.name",
                "personalInfo.email",
                "businessInfo.name",
                "locationInfo.address"] )

general_solicitud_schema =  SolicitudSchema()



requests_schema = SolicitudSchema(only=["id_solicitud",
                "comentario_rechazo",                       
                "personalInfo.name",
                "personalInfo.email",
                "personalInfo.phone",
                "businessInfo.name",
                "locationInfo.address"], many=True)

create_schema = SolicitudBaseSchema()

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
    solicitudes_data = []
    if not status_param:
        solicitudes = Solicitud.query.all()
    else:
        if status_param in status["valid_statuses_query"]: 
            solicitudes = Solicitud.query.filter(Solicitud.resultado == status["status"][status_param]).all()

    for solicitud in solicitudes:
    
        solicitud_data = {
            "id_solicitud": solicitud.id_solicitud,
            "comentario_rechazo": solicitud.comentario_rechazo,
            "personalInfo": solicitud.get_personal_info(),
            "businessInfo": solicitud.get_business_info(),
            "locationInfo": solicitud.get_location_info()
        }
        solicitudes_data.append(solicitud_data)

    return requests_schema.dump(solicitudes_data), 200

@solicitudes_bp.route('/requests/<int:solicitud_id>', methods = ['GET'])
def get_solicitud(solicitud_id):
    try:
        
        solicitud = Solicitud.query.get(solicitud_id)
        solicitud_data = {
        "id_solicitud": solicitud.id_solicitud,
        "personalInfo": solicitud.get_personal_info(),
        "businessInfo": {**solicitud.get_business_info(), "courtTypes": ["Futbol 7"]},
        "locationInfo": solicitud.get_location_info(),
        
        }
        
        return general_solicitud_schema.dump(solicitud_data), 200
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@solicitudes_bp.route('/requests', methods = ['POST'])
def create_solicitud():
    try:
        data = request.get_json()
        solicitud_data = create_schema.load(data)
        solicitud_data["ya_procesada"] = False

        email = solicitud_data["email_duenio"]
        existing_record = Solicitud.query.filter(Solicitud.email_duenio == email).first()
        if existing_record:
            return jsonify({"error": "El email ya existe"}), 500



        nueva_solicitud = Solicitud(**solicitud_data)

        db.session.add(nueva_solicitud)
        db.session.commit()
        
        solicitud_data = {
            "id_solicitud": nueva_solicitud.id_solicitud,
            "personalInfo": nueva_solicitud.get_personal_info(),
            "businessInfo": nueva_solicitud.get_business_info(),
            "locationInfo": nueva_solicitud.get_location_info()
        }

        return solicitud_schema.dump(solicitud_data), 201

    except Exception as e:
        db.session.rollback()
        
        return jsonify({"error": str(e)}), 500
    
@solicitudes_bp.route('/requests/upload-rut/<int:solicitud_id>', methods = ['POST'])
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

        # if len(file_name) > 80:
        #     return jsonify({"error": "Nombre de archivo muy grande"}), 400
        
        file_url = upload_to_gcs(file_data, file_name)
        solicitud.rut = file_url
        db.session.commit()
        return jsonify({"message": "Archivo subido"}), 200
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@solicitudes_bp.route('/requests/<int:solicitud_id>/approve', methods = ['POST'])
def approve_request(solicitud_id):
    try:
        print(datetime.today())

        solicitud = Solicitud.query.get(solicitud_id)
        if not solicitud:
            return jsonify({"error": "Solicitud no encontrada"}), 404

        serialized_solicitud = solicitud_schema.dump({
            "id_solicitud": solicitud.id_solicitud,
            "personalInfo": solicitud.get_personal_info(),
        })

        name = serialized_solicitud["personalInfo"]["nombre_duenio"]
        email_duenio = serialized_solicitud["personalInfo"]["email_duenio"]
        
        
        solicitud.ya_procesada = True
        solicitud.fecha_procesada = datetime.today()
        solicitud.resultado = True  

        owner_data =  {
            "nombre": name,
            "correo": email_duenio
        }
        new_owner = Duenio(**owner_data)

        db.session.add(new_owner)
        db.session.commit()
        business_data = {          
            "nombre": solicitud.nombre_est,
            "RUT": solicitud.rut,
            "altitud": solicitud.latitud,
            "longitud": solicitud.longitud,
            "localidad": solicitud.localidad,
            "direccion": solicitud.direccion,
            "telefono": solicitud.tel_est,
            "id_duenio": new_owner.id_duenio
        }
        post_establecimiento(business_data)
        # email, password = create_auth_user(email_duenio, name)
        # send_auth_mail(name,email,password)

        return jsonify({"message": "La solicitud ha sido aprobada"}), 200
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@solicitudes_bp.route('/requests/<int:solicitud_id>/reject', methods = ['POST'])
def reject_request(solicitud_id):
    try:
        data = request.get_json()
        comentario = data.get("reason")
        if not comentario:
            return jsonify({"error": "Debe incluir un comentario para la solicitud"}), 400

        solicitud = Solicitud.query.get(solicitud_id)
        if not solicitud:
            return jsonify({"error": "Solicitud no encontrada"}), 404

        serialized_solicitud = solicitud_schema.dump({
            "id_solicitud": solicitud.id_solicitud,
            "personalInfo": solicitud.get_personal_info(),
        })

        name = serialized_solicitud["personalInfo"]["nombre_duenio"]
        email_duenio = serialized_solicitud["personalInfo"]["email_duenio"]
        
        solicitud.ya_procesada = True
        solicitud.fecha_procesada = datetime.today()
        solicitud.resultado = False
        solicitud.comentario_rechazo = comentario
        db.session.commit()

        send_rejected_mail(email_duenio, name, comentario)
        
        return jsonify({"message": "La solicitud ha sido rechazada"}), 200
       

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


