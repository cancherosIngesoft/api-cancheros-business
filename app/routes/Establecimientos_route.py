from collections import defaultdict
from datetime import datetime
import json
from sqlalchemy import func
from app.models.Establecimiento import Establecimiento
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.schemas.Canchas_sch import CanchaSchema, CanchaSchemaBusiness
from app.schemas.Horario_sch import HorarioSchema
from app.models.Cancha import Cancha
from app.utils.cloud_storage import gcs_upload_image, upload_to_gcs
from app.routes.Horarios_route import set_court_time
from app.utils.utils import delete_horario_cancha, get_cambios_in_horarios,  get_horarios_cancha
import geopandas as gpd
import os
import requests
from app import db
from shapely.geometry import Point
from flask import request, Blueprint, jsonify,current_app

from app.models.Resenia import Resenia
from app.schemas.Establecimiento_sch import EstablecimientoSchema, BusinessInfoSchema

establecimiento_bp = Blueprint('establecimiento', __name__)

ALLOWED_FILTERS = {
    "location": str,
    "max_price": float,
    "min_price": float,
    "field_type": str,
}


business_schema =  BusinessInfoSchema(exclude=[
    "canchas"],many=True)
business_schema_canchas =  BusinessInfoSchema(exclude=[
    "promedio_calificacion",
    "priceRange"])

def post_establecimiento(data):

        validate_data_est(data)
        
        establecimiento_data = EstablecimientoSchema().load(data)
        nuevo_est = Establecimiento(**establecimiento_data)
        db.session.add(nuevo_est)
        db.session.commit()


        return jsonify({"message": "establecimiento creado"}), 200


@establecimiento_bp.route('/register_courts/<int:id_owner>', methods = ['POST'])
def post_cancha(id_owner):
    try:

        json_data = request.form['json']
        data = json.loads(json_data)
        dataCancha = {key: data[key] for key in ['nombre', 'tipo', 'capacidad', 'descripcion', 'precio'] if key in data}
        dataSchedule = {key: data[key] for key in ['field_schedule'] if key in data}
        #dataCancha['id_duenio'] = id_owner
        msg,cod = validate_data_cancha(dataCancha, id_owner)
        if cod != 200:
            raise ValueError(f"Error en la validación: {msg.data}")
        establecimiento = Establecimiento.query.filter_by(id_duenio = id_owner).first()
        dataCancha['id_establecimiento'] = establecimiento.id_establecimiento
        files = request.files.getlist('files') 
        i = 1
        for file in files:
            file_data = file.read()
            extension = '.' + file.filename.split('.')[-1].lower()
            file_name = str(datetime.now().strftime('%Y-%m-%d%H0%M0%S0%f')[:-3]) + extension
            print(type(file_name), file_name, " xd")
            if not file:
                file_url = None
            else:
                file_url = gcs_upload_image(file_data, file_name)
            dataCancha[f'imagen{i}'] = file_url
            i+=1
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


@establecimiento_bp.route('/edit_courts/<int:id_cancha>', methods = ['PATCH'])
def edit_courts(id_cancha):
    try:
        data = request.get_json()
        dataCancha = {key: data[key] for key in ['nombre', 'tipo', 'capacidad', 'descripcion', 'precio'] if key in data}
        horarios_nuevos = data.get('field_schedule')
        horarios_antiguos = get_horarios_cancha(id_cancha)

        
        borrados, agregados = get_cambios_in_horarios(nuevos=horarios_nuevos, antiguos=horarios_antiguos)

        post_cambios_cancha(id_cancha=id_cancha, data=dataCancha)

        for horario in borrados:
            id_horario = horario.get("id_horario")
            delete_horario_cancha(id_horario, id_cancha)

        
        dataSchedule = {
            "field_schedule" : agregados,
            "id_court" : id_cancha
        }
        set_court_time(dataSchedule, id_cancha)

        
        return jsonify({"message" : "Cancha editada con exito"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500 


def post_cambios_cancha(id_cancha, data):
    db.session.query(Cancha).filter(Cancha.id_cancha == id_cancha).update(data)
    db.session.commit()


@establecimiento_bp.route('/get_courts/<int:id_owner>', methods = ['GET'])
def get_canchas(id_owner):
    try:
        establecimiento = Establecimiento.query.filter_by(id_duenio = id_owner).first()
        if not establecimiento:
            raise ValueError(f"No hay establecimiento asociado")
        canchas= Cancha.query.filter_by(id_establecimiento = establecimiento.id_establecimiento).all()
        if not canchas:
            return [], 200
        else:
            list_canchas = []
            for cancha in canchas:
                horarios = db.session.query(Horario.dia, Horario.hora_inicio, Horario.hora_fin).\
                join(Horario_cancha, Horario_cancha.id_horario == Horario.id_horario).\
                join(Cancha, Cancha.id_cancha == Horario_cancha.id_cancha).\
                filter(Cancha.id_cancha == cancha.id_cancha).all()

                cancha_schema = CanchaSchema(exclude=["id_establecimiento"]).dump(cancha)
                field_schedules = []
                for horario in horarios:
                    field_schedules.append(  HorarioSchema(exclude=['id_horario']).dump(horario)  )
                cancha_schema['field_schedule'] =  field_schedules
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
            query = query.filter(Cancha.capacidad == field_type)
        
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

@establecimiento_bp.route('/business/<int:business_id>', methods = ['GET'])
def get_establecimiento(business_id):
    try:

        establecimiento = Establecimiento.query.get(business_id)
        if not establecimiento:
            return jsonify({"error": "Establecimiento no encontrado"}), 404

        return business_schema_canchas.dump(establecimiento), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def validate_data_cancha(data, id_owner):
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

    establecimiento = Establecimiento.query.filter_by(id_duenio = id_owner).first()
    if not establecimiento:
        return jsonify({"error": "El usuario no tiene establecimiento asociado"}), 400 
    
    return jsonify({"message":"Data valida"}), 200

def validate_data_est(data):
    RUT = data.get('RUT')
    altitud = float(data.get('altitud'))
    longitud = float(data.get('longitud'))


    shapefile_path = os.path.join(current_app.root_path, 'static/geo_bogota', 'Loca.shp')

    if not RUT:
        raise Exception("no hay RUT")
    
    if not altitud or not longitud:    
        raise Exception("no hay latitud y longitud") 
    else:  
        valid_coor = is_in_bogota(altitud, longitud, shapefile_path )
        if not valid_coor:       
            raise Exception("Coordenadas fuera de bogota") 
    
    return jsonify({"mesaage": "Data valida"}), 200 


def is_in_bogota(altitude, longitude, shapefile_path):
    bogota_boundary = gpd.read_file(shapefile_path)
    point = Point(longitude, altitude)
    
    return any(bogota_boundary.contains(point))
