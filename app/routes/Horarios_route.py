from app.models.Horario import Horario
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.schemas.Horario_sch import HorarioSchema
from datetime import datetime


horarios_bp = Blueprint('horarios', __name__)

@horarios_bp.route('/set_horario', methods = ['POST'])
def set_horario():
    data = request.get_json()
    is_valid, error = validate_data_horario(data)
    schema = {}
    if is_valid: 
        horario_prev = Horario.query.filter_by(dia = data.get('dia'), hora_inicio =  data.get('hora_inicio'), hora_fin = data.get('hora_fin')).first()
        hor_sch = HorarioSchema()
        schema = hor_sch.dump(horario_prev)
        if horario_prev is None:
            nuevo_hor = Horario( dia = data.get('dia'), hora_inicio =  data.get('hora_inicio'), hora_fin = data.get('hora_fin'))           
            db.session.add(nuevo_hor)
            db.session.commit()
            schema = hor_sch.dump(nuevo_hor)
    
    return jsonify(schema) #error



@horarios_bp.route('/set_horario_cancha', methods = ['POST'])
def set_horario_cancha():
    data = request.get_json()
    is_valid, error = validate_data_hor_cancha(data)
    # if is_valid :
        # nuevo_hor = None
        # db.session.add(nuevo_hor)
        # db.session.commit()
        # TODO: el schema y modelos para horario cancha para subirlos
    return error



def validate_data_hor_cancha(data):
    horario = Horario.query.filter_by(id_horario = data.get('id_horario')).first()
    cancha = Cancha.query.filter_by(id_cancha = data.get('id_cancha')).first()
    
    if horario and cancha:
        return True, "exito"
    
    return False, "ERROR: Horario y cancha deben existir previamnete"

def validate_data_horario(data):
    hora_inicio_str = data.get('hora_inicio')  
    hora_fin_str = data.get('hora_fin')


    if not hora_inicio_str:
        return False, "ERROR: falta hora_inicio"
    
    if not hora_fin_str:
        return False, "ERROR: falta hora_fin"

    if not data.get('dia'):
        return False, "ERROR: falta dia"

    if len(hora_inicio_str) == 2:  
        hora_inicio_str = f"{hora_inicio_str}:00:00"

    if len(hora_fin_str) == 2:  
        hora_fin_str = f"{hora_fin_str}:00:00"

    if len(hora_inicio_str) == 4: 
        hora_inicio_str = f"{hora_inicio_str}:00"

    if len(hora_fin_str) == 4: 
        hora_fin_str = f"{hora_fin_str}:00"


    try:
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M:%S').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M:%S').time()
        if hora_inicio >= hora_fin:
            return False, "ERROR: la hora de inicio debe ser anterior a la hora de final"
        
    except ValueError:
        return False, "Error: La hora no es un formato de hora válido."

    
    return True, "exito"
    

def no_hay_horario(data):
    horario = Horario.query.filter_by(dia = data.get('dia'), hora_inicio =  data.get('hora_inicio'), hora_fin = data.get('hora_fin')).first()
    
    return horario is None
