from app.models.Establecimiento import Establecimiento
from app.models.Cancha import Cancha
import geopandas as gpd
import os
import requests
from app import db
from shapely.geometry import Point
from flask import request, Blueprint, jsonify,current_app

establecimiento_bp = Blueprint('establecimiento', __name__)

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

#nombre
#tipo
#capacidad
#descripcion
#precio


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
