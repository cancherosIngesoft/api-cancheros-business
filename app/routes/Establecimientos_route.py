from app.models.Establecimiento import Establecimiento
from app.schemas.Canchas_sch import CanchaSchema
from app.models.Cancha import Cancha
from app.utils.cloud_storage import gcs_upload_image, upload_to_gcs
from app.routes.Horarios_route import validate_data_time
import geopandas as gpd
import os
import requests
from app import db
from shapely.geometry import Point
from flask import request, Blueprint, jsonify,current_app

establecimiento_bp = Blueprint('establecimiento', __name__)

@establecimiento_bp.route('/register_est', methods = ['GET', 'POST'])
def post_establecimiento():
    data = request.get_json()

    is_valid,error = validate_data_est(data)
    if(is_valid):
        nuevo_est = Establecimiento( RUT = data.get('RUT'), altitud =  data.get('altitud'), longitud= data.get('longitud'))
        db.session.add(nuevo_est)
        db.session.commit()
    return error

@establecimiento_bp.route('/register_courts/<int:est_id>', methods = ['POST'])
def post_cancha(est_id):
    try:
        data = request.get_json()
        data['id_establecimiento'] = est_id
        msg,cod = validate_data_cancha(data)
        if cod != 200:
            return msg
        # files = request.files.getlist('files') 
        # urls = []
        # for file in files:
        #     file_data = file.read()
        #     file_name = file.filename
            
        #     if not file:
        #         return jsonify({"error": "No se ha subido ningún archivo"}), 400

        #     file_url = gcs_upload_image(file_data, file_name)
        #     urls.append(file_url)
        #     # solicitud.rut = file_url - cancha_imgs= file.url
        #     # db.session.commit()
        # return jsonify({"message": "Archivo subido",
        #                 "urls" : urls}), 200
        sch = CanchaSchema()
        cancha_data = sch.load(data)
        nueva_cancha = Cancha(**cancha_data)

        db.session.add(nueva_cancha)
        db.session.commit()
        return jsonify({"message":"cancha subida exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@establecimiento_bp.route('/register_courts_img/<int:est_id>', methods = ['POST'])
def post_cancha_img(est_id):
    try:
        files = request.files.getlist('files') 
        urls = []
        for file in files:
            file_data = file.read()
            file_name = file.filename
            file_url = gcs_upload_image(file_data, file_name)
            print("URL: ", file_url)
            urls.append(file_url)
            # solicitud.rut = file_url - cancha_imgs= file.url
            # db.session.commit()
        print(urls)
        return jsonify({"message": "Archivo subido"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def validate_data_cancha(data):
    nombre = data.get('nombre')
   
    if not nombre:
        return jsonify({"error": "Debe incluir un nombre para la cancha"}), 400
    tipo = data.get('tipo')
    if not tipo:
        return jsonify({"error": "Debe incluir un tipo para la cancha"}), 400  
    capacidad =  data.get('capacidad')
    if not capacidad:
        return jsonify({"error": "Debe incluir capacidad para la cancha"}), 400 
    deescripcion = data.get('descripcion')
    if not deescripcion:
        return jsonify({"error": "Debe incluir descripcion para la cancha"}), 400 
    precio = data.get('precio')
    if not precio:
        return jsonify({"error": "Debe incluir precio para la cancha"}), 400 
    

    # horario = data.get('horario')
    # if not horario:
    #     return jsonify({"error": "Debe incluir horario para la cancha"}), 400 

    establecimiento = Establecimiento.query.filter_by(id_establecimiento = data.get('id_establecimiento')).first()
    if not establecimiento:
        return jsonify({"error": "El establecimiento no existe"}), 400 
    
    return jsonify({"message":"Data valida"}), 200

def validate_data_est(data):
    RUT = data.get('RUT')
    altitud = float(data.get('altitud'))
    longitud = float(data.get('longitud'))


    shapefile_path = os.path.join(current_app.root_path, 'static', 'Loca.shp')

    if not RUT:
        return False, 'ERROR: no hay RUT'
    
    if not altitud or not longitud: 
        return False, 'ERROR: no hay altitud y longitud'
    else:  
        valid_coor = is_in_bogota(altitud, longitud, shapefile_path )
        if not valid_coor:
            return valid_coor, "ERROR: Coordenadas fuera de bogota" 
    
    return True, "exito"


def is_in_bogota(altitude, longitude, shapefile_path):
    bogota_boundary = gpd.read_file(shapefile_path)
    point = Point(longitude, altitude)
    
    return any(bogota_boundary.contains(point))
