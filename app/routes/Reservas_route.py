import unicodedata
import pytz
import requests
from sqlalchemy import func
from app.models.Equipo import Equipo
from app.models.Reserva import Reserva
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.models.Reservante import Reservante
from app.models.Usuario import Usuario
from app.schemas.Horario_sch import HorarioSchema
from app.schemas.Horario_cancha_sch import HorarioCanchaSchema
from datetime import datetime, time, timedelta
import locale


reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/booking', methods = ['POST'])
def create_reserva():
    data = request.get_json()

    try:
        is_team = data.get("isTeam")
        id_reservante = data.get("id_reservante")
        reservante = db.session.query(Reservante).filter_by(id_reservante=id_reservante).first()
        if not reservante:
            if is_team:
                equipo = db.session.query(Equipo).filter_by(id_equipo=id_reservante).first()
                if not equipo:
                    return jsonify({"Error": "El equipo no existe"}), 400
            else:
                usuario = db.session.query(Usuario).filter_by(id_usuario=id_reservante).first()
                if not usuario:
                    return jsonify({"Error": "El usuario no existe"}), 400

            tipo_reservante = 'usuario' if not is_team else 'equipo'
            nuevo_reservante = Reservante(id_reservante=id_reservante, tipo_reservante=tipo_reservante)
            db.session.add(nuevo_reservante)
            db.session.commit()

        nueva_reserva = Reserva(
            hora_inicio=data.get("hora_inicio"),
            hora_fin=data.get("hora_fin"),
            id_reservante=id_reservante,
            id_cancha=data.get("id_cancha")
        )
        db.session.add(nueva_reserva)
        # db.session.flush()

        # nuevo_miembro = MiembroEquipo(id_usuario=3, id_equipo=nuevo_equipo.id_equipo)
        # db.session.add(nuevo_miembro)

        db.session.commit()

        return jsonify({"message": "Exitoso"}), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    




