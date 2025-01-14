
from app.models.Cancha import Cancha
from app.models.Establecimiento import Establecimiento
from flask import request, Blueprint, jsonify
from app import db
import requests

cancha_bp = Blueprint('cancha', __name__)

@cancha_bp.route('/register_courts', methods = ['POST'])
def reg_cancha():
    data = request.get_json()
    response_horario = requests.post('http://localhost:8080/api/set_horario', json=data['horario']).json()
    is_valid, error = validate_data(data)
    
    # si response horario = {} entonces horario no valido
    if is_valid:
        nueva_cancha = Cancha( tamanio =  data.get('capacidad'), grama = data.get('tipo') )
        db.session.add(nueva_cancha)
        db.session.commit()


    return response_horario.json()

#nombre
#tipo
#capacidad
#descripcion
#precio


def validate_data(data):
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