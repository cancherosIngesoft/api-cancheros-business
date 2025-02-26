from decimal import Decimal
from flask import request, Blueprint, jsonify,current_app
from sqlalchemy import func, select

from app import db
from app.models.Cancha import Cancha
from app.models.Equipo import Equipo
from app.models.Establecimiento import Establecimiento
from app.models.Notificacion_estadistica import Notificacion_estadistica
from app.models.Partido import Partido
from app.models.Resenia import Resenia
from app.models.Reserva import Reserva
from app.models.Reservante import Reservante
from app.models.Usuario import Usuario
from app.routes.Reservas_route import get_reservas_equipo_de_user, get_reservas_reservante
from app.schemas.Resenia_sch import ReseniaSchema
from app.schemas.Reserva_sch import ReservaSchema


resenias_bp = Blueprint('resenias', __name__)
reserva_schema_unique = ReservaSchema(only=["hora_inicio", "hora_fin", "partido"])
resenia_schema = ReseniaSchema()

def get_pending_califications(id_user):
    try:

        #Reservas individuales
        stmt_individual = (
            select(Reservante, Establecimiento)
            .join(Reserva, Reserva.id_reservante == Reservante.id_reservante)
            .join(Cancha, Reserva.id_cancha == Cancha.id_cancha)
            .join(Establecimiento, Establecimiento.id_establecimiento == Cancha.id_establecimiento)
            .outerjoin(Resenia, 
                (Resenia.id_autor == Reservante.id_reservante) & 
                (Resenia.id_establecimiento == Establecimiento.id_establecimiento)
            )
            .where(
                Reserva.hora_fin < func.now().op("AT TIME ZONE")("America/Bogota"),
                Reserva.id_reservante == id_user,
                Resenia.id_resenia.is_(None) 
            )
            .distinct()
        )

        #Reservas por equipo
        stmt_team = (
            select(Reservante, Establecimiento)
            .join(Reserva, Reserva.id_reservante == Reservante.id_reservante)
            .join(Partido, Reserva.id_partido == Partido.id_partido)
            .join(Equipo, Equipo.id_equipo == Partido.id_equipo)
            .join(Cancha, Reserva.id_cancha == Cancha.id_cancha)
            .join(Establecimiento, Establecimiento.id_establecimiento == Cancha.id_establecimiento)
            .outerjoin(Resenia, 
                (Resenia.id_autor == Equipo.id_capitan) & 
                (Resenia.id_establecimiento == Establecimiento.id_establecimiento)
            )
            .where(
                Reserva.hora_fin < func.now().op("AT TIME ZONE")("America/Bogota"),
                Equipo.id_capitan == id_user,
                Resenia.id_resenia.is_(None)
            )
            .distinct()
        )
        
        results_individual = db.session.execute(stmt_individual).all()
        results_team = db.session.execute(stmt_team).all()
        pending_califications = []
        for reservante, establecimiento in results_individual:
            try:
                pending_califications.append({
                    # "id_reservante": reservante.id_reservante,
                    "id_user": id_user,
                    "id_establecimiento": establecimiento.id_establecimiento,
                    # "isTeam": False,
                })
            except Exception as e:
                print("Error:", e)

        for reservante, establecimiento in results_team:
            try:
                pending_califications.append({
                    # "id_reservante": reservante.id_reservante,
                    "id_user": id_user,
                    "id_establecimiento": establecimiento.id_establecimiento,
                    # "isTeam": True,
                })
                print(reservante)
                print(establecimiento)
            except Exception as e:
                print("Error:", e)

        return pending_califications
    
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@resenias_bp.route('/calification', methods = ['POST'])
def post_calification():
    data = request.get_json()
    id_user = data.get("id_autor")
    id_establecimiento = data.get("id_establecimiento")
    try:

        reservas_individual_done = get_reservas_reservante(id_booker=id_user, in_team=False, activas=False)
        reservas_team_done = get_reservas_equipo_de_user(id_user, False)
        all_reservas = reservas_individual_done + reservas_team_done
        flag_existe = any(reserva["businessId"] == id_establecimiento for reserva in all_reservas) 

        if not flag_existe:
            return jsonify({
                "message": "El usuario no puede calificar en este establecimiento"
            }), 400
        print(data)
        resenia = Resenia(**data)
        db.session.add(resenia)
        db.session.commit()

        return resenia_schema.dump(resenia), 200
    
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@resenias_bp.route('/califications/pending/<int:id_user>', methods = ['GET'])
def check_reservations_finished(id_user):
    try:
        pending_califications = get_pending_califications(id_user)
        return jsonify(pending_califications), 200

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
