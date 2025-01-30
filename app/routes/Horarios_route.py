import unicodedata
import pytz
import requests
from sqlalchemy import func
from app.models.Reserva import Reserva
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.schemas.Horario_sch import HorarioSchema
from app.schemas.Horario_cancha_sch import HorarioCanchaSchema
from datetime import datetime, time, timedelta
import locale


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

@horarios_bp.route('/available/court/<int:id_cancha>', methods = ['POST'])
def get_available_hours(id_cancha):
    data = request.get_json()
    date = data["date"]
    dias_semana = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miercoles",
        "Thursday": "Jueves", "Friday": "Viernes",
        "Saturday": "Sabado", "Sunday": "Domingo"
    }

    fecha_dt = datetime.strptime(date, "%Y-%m-%d")
    dia_semana = dias_semana[fecha_dt.strftime("%A")]

    horarios_disponibles = (
        db.session.query(
            Horario_cancha.id_cancha,
            Horario.hora_inicio,
            Horario.hora_fin
        )
        .join(Horario, Horario_cancha.id_horario == Horario.id_horario)
        .filter(Horario_cancha.id_cancha == id_cancha)
        .filter(Horario.dia.ilike(dia_semana))
        .all()
    )

    reservas_ocupadas = (
        db.session.query(
            Reserva.hora_inicio,
            Reserva.hora_fin
        )
        .filter(Reserva.id_cancha == id_cancha)
        .filter(func.date(Reserva.hora_inicio) == date)
        .all()
    )

    if len(horarios_disponibles) == 0 :
        return jsonify({"message": f"Esta cancha no tiene horarios habilitados para el dia {dia_semana}"}), 400

    franjas_disponibles = []
    fecha_base = datetime.strptime(date, "%Y-%m-%d")
    reservas = [(
        datetime.strptime(reserva.hora_inicio, "%Y-%m-%d %H:%M:%S"),
        datetime.strptime(reserva.hora_fin, "%Y-%m-%d %H:%M:%S")
    ) for reserva in reservas_ocupadas]

    for horario in horarios_disponibles:
        inicio = datetime.combine(fecha_base, horario.hora_inicio)
        fin = datetime.combine(fecha_base, horario.hora_fin)
        
        while inicio + timedelta(hours=1) <= fin:
            fin_current = inicio + timedelta(hours=1)

            flag_solapa = any(
                (reserva_inicio < fin_current and reserva_fin > inicio)
                for reserva_inicio, reserva_fin in reservas
            )

            if not flag_solapa:
                franjas_disponibles.append({
                    "hora_inicio": inicio.strftime('%H:%M:%S'),
                    "hora_fin": fin_current.strftime('%H:%M:%S')
                })

            inicio = fin_current


    return jsonify(franjas_disponibles), 200

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