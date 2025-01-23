import requests
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.schemas.Horario_sch import HorarioSchema
from app.schemas.Horario_cancha_sch import HorarioCanchaSchema
from datetime import datetime


horarios_bp = Blueprint('horarios', __name__)

@horarios_bp.route('/set_time', methods = ['POST'])
def set_time():
    data = request.get_json()
    msg, cod = validate_data_time(data)
    schema = {}
    if cod != 200: 
         raise ValueError(f"Error en la validación Horario: {msg.data}")
    horario_prev = Horario.query.filter_by(dia = data.get('day'), hora_inicio =  data.get('startTime'), hora_fin = data.get('endTime')).first()
    hor_sch = HorarioSchema()
    schema = hor_sch.dump(horario_prev)
    if horario_prev is None:
        nuevo_hor = Horario( dia = data.get('day'), hora_inicio =  data.get('startTime'), hora_fin = data.get('endTime'))           
        db.session.add(nuevo_hor)
        db.session.commit()
        schema = hor_sch.dump(nuevo_hor)
    
    return jsonify(schema) 



#@horarios_bp.route('/set_court_time/<int:cancha_id>', methods = ['POST'])
def set_court_time(data, cancha_id):
    #data = request.get_json()
    data['id_court'] = cancha_id
    print('id cancha: ', cancha_id)
    msg, cod = validate_data_court_time(data)
    if cod != 200 :
        raise ValueError(f"Error en la validación HorarioCancha: {msg.data}")
    schedule_list = data.get('field_schedule')
    url = "http://localhost:8080/api/set_time" 
    try:
        for schedule in schedule_list:   
            response = requests.post(url, json=schedule)
            horario = response.json()
            id_time = horario.get('id_horario')
            if no_court_time(cancha_id, id_time):
                nuevo_hor = Horario_cancha(id_cancha = cancha_id, id_horario = id_time)
                db.session.add(nuevo_hor)
                db.session.commit()
        return jsonify({"msg": "Horarios subidos correctamente" }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def validate_data_court_time(data):
    required_keys = {"field_schedule", "id_court"}

    if not required_keys.issubset(data):
        return jsonify({"error": "Missing required keys"}), 400
    
    cancha = Cancha.query.filter_by(id_cancha = data.get('id_court')).first()
    
    if cancha:
        return jsonify({"message":"Horario cancha valido"}), 200
    return jsonify({"error": "Cancha deben existir previamente"}), 400

def validate_data_time(data):
    hora_inicio_str = data.get('startTime')  
    hora_fin_str = data.get('endTime')


    if not hora_inicio_str:
        return jsonify({"error": "falta hora_inicio"}), 400
    
    if not hora_fin_str:
        return jsonify({"error": "falta hora_fin"}), 400

    if not data.get('day'):
        return jsonify({"error": "falta el dia"}), 400

    if len(hora_inicio_str) == 2:  
        hora_inicio_str = f"{hora_inicio_str}:00:00"

    if len(hora_fin_str) == 2:  
        hora_fin_str = f"{hora_fin_str}:00:00"


    try:
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
        if hora_inicio >= hora_fin:
            return jsonify({"error": "falta hora_inicio debe ser anterior a la hora_fin"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
    return jsonify({"message":"Horario valido"}), 200
    

def no_hay_horario(data):
    horario = Horario.query.filter_by(dia = data.get('day'), hora_inicio =  data.get('startTime'), hora_fin = data.get('endTime')).first()
    
    return horario is None

def no_court_time(id_court, id_time):
    court_time = Horario_cancha.query.filter_by(id_cancha = id_court, id_horario = id_time).first()
    return court_time is None