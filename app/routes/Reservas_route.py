import unicodedata
import pytz
import requests
from sqlalchemy import and_, func, or_, cast, Date, select
from app.models.Miembro_equipo import Miembro_equipo
from app.models.Reserva import Reserva
from app.models.Establecimiento import Establecimiento
from app.models.Equipo import Equipo
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.models.Reservante import Reservante
from app.models.Usuario import Usuario
from app.routes.Horarios_route import verify_hour_court
from app.routes.Partido_route import create_partido
from app.schemas.Horario_sch import HorarioSchema
from app.schemas.Horario_cancha_sch import HorarioCanchaSchema
from datetime import datetime, time, timedelta
import locale

from app.schemas.Reserva_sch import ReservaSchema


reservas_bp = Blueprint('reservas', __name__)
reserva_schema = ReservaSchema(many=True, exclude=["cancha"])
reserva_schema_unique = ReservaSchema(exclude=["cancha"])

@reservas_bp.route('/reservations/court/<int:id_cancha>', methods = ['POST'])
def get_reservas_week(id_cancha):
    data = request.get_json()
    date = data["date"]

    try:
        inicio_semana = datetime.strptime(date, "%Y-%m-%d")
        fin_semana = inicio_semana + timedelta(days=7)

        fin_semana = fin_semana.replace(hour=23, minute=59, second=59)

        reservas = Reserva.query.filter(
            Reserva.id_cancha == id_cancha,
            Reserva.hora_inicio >= inicio_semana,
            Reserva.hora_fin <= fin_semana
        ).order_by(Reserva.hora_inicio).all()

     

        return reserva_schema.dump(reservas), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    


@reservas_bp.route('/booking', methods = ['POST'])
def create_reserva():
    data = request.get_json()

    try:
        is_team = data.get("isTeam")
        id_reservante = data.get("id_reservante")
        reservante = db.session.query(Reservante).filter_by(id_reservante=id_reservante).first()
        if not reservante:
            return jsonify({"error": "No existe el reservante"}), 404
        if is_team and not reservante.tipo_reservante == "equipo":
            return jsonify({"error": "El reservante no corresponde a un equipo"}), 404
        
        hora_inicio=data.get("hora_inicio")
        hora_fin=data.get("hora_fin")
        id_cancha=data.get("id_cancha")

        if not verify_hour_court(data):
            return jsonify({"error": "Este horario no esta disponible para esta cancha"}), 400
        nueva_hora_inicio = datetime.strptime(data.get("hora_inicio"), "%Y-%m-%d %H:%M:%S")
        nueva_hora_fin = datetime.strptime(data.get("hora_fin"), "%Y-%m-%d %H:%M:%S")
        
        reservas_solapadas = db.session.query(Reserva).filter(
            Reserva.id_cancha == id_cancha,
            or_(
                and_(
                    Reserva.hora_inicio <= hora_inicio, 
                    hora_inicio < Reserva.hora_fin
                ),
                and_(
                    Reserva.hora_inicio < hora_fin, 
                    hora_fin <= Reserva.hora_fin
                ),
                and_(
                    Reserva.hora_inicio >= hora_inicio, 
                    Reserva.hora_fin <= hora_fin
                )
            )
        ).all()

        if reservas_solapadas:
            return jsonify({"error": "La reserva se solapa con otra existente"}), 400

        nueva_reserva = Reserva(
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_reservante=id_reservante,
            id_cancha=id_cancha
        )
        db.session.add(nueva_reserva)

        if is_team:
            new_partido = create_partido({
                "id_equipo": id_reservante
            })
            id_partido = new_partido[0]["id_partido"]
            nueva_reserva.id_partido = id_partido
            print("Es un team", new_partido)


        db.session.commit()

        return reserva_schema_unique.dump(nueva_reserva), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
def update_status(id_reserva):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        reserva.estado_procesado = True
        db.session.commit()
        return
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

@reservas_bp.route('/reservations/active/<int:id_user>', methods = ['GET'])
def get_reservas_activas(id_user):
    try:

        reservas_individuales = get_reservas_reservante(id_user, in_team=False,activas= True)

        reservas_equipo = get_reservas_equipo_de_user(id_user, activas=True)
        return  jsonify(reservas_individuales + reservas_equipo)


    

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
@reservas_bp.route('/reservations/inactive/<int:id_user>', methods = ['GET'])
def get_reservas_inactivas(id_user):
    try:

        reservas_individuales = get_reservas_reservante(id_user, in_team=False,activas= False)

        reservas_equipo = get_reservas_equipo_de_user(id_user, False)
        return  jsonify(reservas_individuales + reservas_equipo)


    

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

def get_reservas_reservante(id_booker, in_team, activas):
        
        if activas:
            reservas = Reserva.query.filter(
                Reserva.id_reservante == id_booker,  
                Reserva.hora_inicio >= datetime.now()).all()
        else:
            reservas = Reserva.query.filter(
                Reserva.id_reservante == id_booker,  
                Reserva.hora_inicio < datetime.now()).all()
        
        reservas_activas = []
        for reserva in reservas:
            schema = {}
            idReservation = reserva.id_reserva
            dateReservation = reserva.hora_inicio.strftime("%Y-%m-%d")
            hours = { "horaInicio":reserva.hora_inicio, "horaFin" : reserva.hora_fin }
            
            cancha_info = db.session.query(
                    Cancha.imagen1,
                    Cancha.capacidad,
                    Cancha.tipo,
                    Cancha.precio,
                    Cancha.id_establecimiento
                ).filter(Cancha.id_cancha == reserva.id_cancha).first()
            
            
            capacity = cancha_info[1]
            field_type = cancha_info[2]
            fieldImg = cancha_info[0]

            diferencia_horas = (reserva.hora_fin - reserva.hora_inicio).total_seconds() / 3600
            totalPrice = diferencia_horas * float(cancha_info.precio)


            Business_info = db.session.query(
                    Establecimiento.nombre,
                    Establecimiento.direccion,
                ).filter(Establecimiento.id_establecimiento == cancha_info.id_establecimiento).first()

            businessDiretion = Business_info[1]
            businessName = Business_info[0]

            if in_team:
                teamName_query = db.session.query(Equipo.nombre ).filter_by(id_equipo = id_booker).first()
                schema['teamName'] = teamName_query[0]

            schema['idReservation'] = idReservation
            schema['dateReservation'] = dateReservation
            schema['hours'] = hours
            schema['inTeam'] = in_team
            schema['idBooker'] = id_booker
            schema['bussinesName'] = businessName
            schema['FieldType'] = field_type
            schema['capacity'] = capacity
            schema['bussinesDirection'] = businessDiretion
            schema['fieldImg'] = fieldImg
            schema['totalPrice'] = totalPrice

            reservas_activas.append(schema)

        return reservas_activas


def get_reservas_equipo_de_user(id_user, activas):
    
        ids_equipo = db.session.query(Miembro_equipo.id_equipo).filter_by(id_usuario=id_user).all()

        reservas_equipos = []
        for id_equipo in ids_equipo:
            reservas = get_reservas_reservante(id_equipo[0], in_team=True, activas=activas)
            reservas_equipos.extend(reservas)
        
        return reservas_equipos
