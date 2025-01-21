from sqlalchemy import func
from app.models.Establecimiento import Establecimiento
from app.models.Cancha import Cancha
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
def reg_establecimiento():
    data = request.get_json()

    is_valid,error = validate_data_est(data)
    if(is_valid):
        nuevo_est = Establecimiento( RUT = data.get('RUT'), altitud =  data.get('altitud'), longitud= data.get('longitud'))
        db.session.add(nuevo_est)
        db.session.commit()
    return error

@establecimiento_bp.route('/register_courts', methods = ['POST'])
def reg_cancha():
    data = request.get_json()
    #response_horario = requests.post('http://localhost:8080/api/set_horario', json=data['horario']).json()
    is_valid, error = validate_data_cancha(data)
    
    # si response horario = {} entonces horario no valido
    if is_valid:
        nueva_cancha = Cancha( id_establecimiento = data.get('id_establecimiento'),tamanio =  data.get('tamanio'), grama = data.get('grama') , descripcion = data.get('descripcion'), nombre = data.get('nombre'), precio = data.get('precio'))
        db.session.add(nueva_cancha)
        db.session.commit()


    return "exito" #response_horario.json()

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
    tipo = data.get('tipo')
    capacidad =  data.get('capacidad')
    deescripcion = data.get('descripcion')
    precio = data.get('precio')
    horario = data.get('horario')


    # if not nombre:
    #     return False, "ERROR: nombre nulo"  

    # if not tipo:
    #     return False, "ERROR: tipo nulo"  
    
    # if not capacidad:
    #     return False, "ERROR: capacidad nulo"  
    
    # if not deescripcion:
    #     return False, "ERROR: descripcion nulo"  
    
    # if not precio:
    #     return False, "ERROR: precio nulo"   
    
    # if not horario:
    #     return False, "ERROR: horario  nulo"  
    
    # establecimiento = Establecimiento.query.filter_by(id_establecimiento = data.get('id_establecimiento')).first()

    # if not establecimiento: 
    #     return False, "ERROR: No existe el establecimiento asociado" 
    return True, "Exito"

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
