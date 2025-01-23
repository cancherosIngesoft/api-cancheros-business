import json
from sqlalchemy import func
from app.models.Establecimiento import Establecimiento
from app.schemas.Canchas_sch import CanchaSchema
from app.models.Cancha import Cancha
from app.utils.cloud_storage import gcs_upload_image, upload_to_gcs
from app.routes.Horarios_route import set_court_time
import geopandas as gpd
import os
import requests
from app import db
from shapely.geometry import Point
from flask import request, Blueprint, jsonify,current_app

from app.models.Resenia import Resenia
from app.schemas.Establecimiento_sch import BusinessInfoSchema

establecimiento_bp = Blueprint('establecimiento', __name__)

ALLOWED_FILTERS = {
    "location": str,
    "max_price": float,
    "min_price": float,
    "field_type": str,
}


business_schema =  BusinessInfoSchema(many=True)

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
        json_data = request.form['json']
        data = json.loads(json_data)
        dataCancha = {key: data[key] for key in ['nombre', 'tipo', 'capacidad', 'descripcion', 'precio'] if key in data}
        dataSchedule = {key: data[key] for key in ['field_schedule'] if key in data}
        dataCancha['id_establecimiento'] = est_id
        msg,cod = validate_data_cancha(dataCancha)
        if cod != 200:
            raise ValueError(f"Error en la validación: {msg.data}")
        files = request.files.getlist('files') 
        i = 1
        for file in files:
            file_data = file.read()
            file_name = file.filename
            
            if not file:
                file_url = None
            else:
                file_url = gcs_upload_image(file_data, file_name)
            dataCancha[f'imagen{i}'] = file_url
            i+=1
        print(dataCancha)
        sch = CanchaSchema()
        cancha_data = sch.load(dataCancha)
        nueva_cancha = Cancha(**cancha_data)

        db.session.add(nueva_cancha)
        db.session.commit()
        try:
            set_court_time(dataSchedule, nueva_cancha.id_cancha)
        except Exception as e:
            db.session.rollback()  
            db.session.delete(nueva_cancha)
            db.session.commit()
            return jsonify({"error": f"Error al configurar los horarios de la cancha: {str(e)}"}), 500  
        return jsonify({"message":"cancha subida exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@establecimiento_bp.route('/get_courts/<int:est_id>', methods = ['GET'])
def get_canchas(est_id):
    try:
        canchas= Cancha.query.filter_by(id_establecimiento = est_id).all()
        if not canchas:
            return jsonify({"error": "No hay canchas registradas"}), 500
        else:
            list_canchas = []
            for cancha in canchas:
                cancha_schema = CanchaSchema().dump(cancha)
                list_canchas.append(cancha_schema)
            return jsonify({"courts": list_canchas}), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@establecimiento_bp.route('/business', methods = ['GET'])
def get_establecimientos():
    filters_venues = request.args
    print(filters_venues)
    try:
        filters = parse_filters(filters_venues, ALLOWED_FILTERS)
        

        location = filters.get("location")
        max_price = filters.get("max_price")
        min_price = filters.get("min_price")
        field_type = filters.get("field_type")

        query = db.session.query(
            Establecimiento.id_establecimiento.label('id_establecimiento'),
            Establecimiento.nombre, Establecimiento.altitud, Establecimiento.longitud,
            func.coalesce(func.avg(Resenia.calificacion), None).label('promedio_calificacion'),
            func.max(Cancha.precio).label('max_price'),
            func.min(Cancha.precio).label('min_price')
        ).outerjoin(
            Resenia, Establecimiento.id_establecimiento == Resenia.id_establecimiento
        ).join(
            Cancha, Establecimiento.id_establecimiento == Cancha.id_establecimiento
        )

        
        if location:
            query = query.filter(Establecimiento.localidad.ilike(f'%{location}%'))

        # Filtros para canchas

        if max_price is not None and min_price is not None:
            query = query.filter(Cancha.precio.between(min_price, max_price))
            
        elif max_price is not None:
            query = query.filter(Cancha.precio <= max_price)
        elif min_price is not None:
            query = query.filter(Cancha.precio >= min_price)

        if field_type:
            query = query.filter(Cancha.tamanio == field_type)
        
        query = query.group_by(
            Establecimiento.id_establecimiento
        )
        establecimientos = query.all()



        return business_schema.dump(establecimientos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def parse_filters(filters, allowed_filters):
    parsed_filters = {}
    
    for key, value in filters.items():
        if key not in allowed_filters:
            raise ValueError(f"Filtro '{key}' invalido.")
        try:
            parsed_filters[key] = allowed_filters[key](value)   
        except ValueError:
            print("Error")
            raise ValueError(f"Invalid value for filter '{key}': {value}")
    return parsed_filters


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
