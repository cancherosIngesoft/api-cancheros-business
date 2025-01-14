from app.models.Establecimiento import Establecimiento
import geopandas as gpd
import os
from app import db
from shapely.geometry import Point
from flask import request, Blueprint, jsonify,current_app

establecimiento_bp = Blueprint('establecimiento', __name__)

@establecimiento_bp.route('/register_est', methods = ['GET', 'POST'])
def reg_establecimiento():
    data = request.get_json()

    is_valid,error = validate_data(data)
    if(is_valid):
        nuevo_est = Establecimiento( RUT = data.get('RUT'), altitud =  data.get('altitud'), longitud= data.get('longitud'))
        db.session.add(nuevo_est)
        db.session.commit()
    return error



def validate_data(data):
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


