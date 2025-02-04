import unicodedata
import pytz
import requests
from sqlalchemy import and_, func, or_
from app.models.Equipo import Equipo
from app.models.Reserva import Reserva
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.models.Reservante import Reservante
from app.models.Usuario import Usuario
from app.routes.Horarios_route import verify_hour_court
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
        fin_semana = inicio_semana + timedelta(days=6)

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
            return jsonify({"error": "No existe el reservante"}), 200
        
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
        # db.session.flush()

        # nuevo_miembro = MiembroEquipo(id_usuario=3, id_equipo=nuevo_equipo.id_equipo)
        # db.session.add(nuevo_miembro)

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
    




