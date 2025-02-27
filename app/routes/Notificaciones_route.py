from decimal import Decimal
from flask import request, Blueprint, jsonify,current_app
from sqlalchemy import func, select

from app.models.Duenio import Duenio
from app import db
from app.models.Equipo import Equipo
from app.models.Notificacion_estadistica import Notificacion_estadistica
from app.models.Partido import Partido
from app.models.Reserva import Reserva
from app.schemas.Noti_stats_sch import NotificacionEstadisticaSchema

notificaciones_bp = Blueprint('notificaciones', __name__)

noti_stats_schema = NotificacionEstadisticaSchema()

@notificaciones_bp.route('/notifications/check-reservations-finished', methods = ['PUT'])
def check_reservations_finished():
    try:

        stmt = (
            select(Reserva, Partido)
            .join(Partido, Reserva.id_partido == Partido.id_partido)
            .outerjoin(Notificacion_estadistica, Partido.id_partido == Notificacion_estadistica.id_partido)
            .where(
                Reserva.hora_fin < func.now().op("AT TIME ZONE")("America/Bogota"),
                Partido.goles_A.is_(None),
                Partido.goles_B.is_(None),
                Reserva.id_partido.isnot(None),
                Notificacion_estadistica.id_partido.is_(None)
            )
        )
        
        results = db.session.execute(stmt).scalars().all()
        notificaciones = []
        for reserva in results:
            try:
                id_capitan = reserva.reservante.id_capitan
                id_partido = reserva.id_partido
                notificaciones.append(Notificacion_estadistica(id_capitan=id_capitan,id_partido=id_partido))
            except Exception as e:
                print("Error:", e)

        db.session.add_all(notificaciones)
        db.session.commit()

        return jsonify({
            "message": "Exitoso"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

@notificaciones_bp.route('/notifications/stats/<int:id_captain>', methods = ['GET'])
def get_notifications_estadistica(id_captain):
    try:

        stmt = (
            select(Notificacion_estadistica, Reserva)
            .join(Partido, Notificacion_estadistica.id_partido == Partido.id_partido)
            .join(Equipo, Equipo.id_equipo == Partido.id_equipo)
            .join(Reserva, Reserva.id_partido == Partido.id_partido)
            .where(
                Equipo.id_capitan == id_captain
            )
        )

        results = db.session.execute(stmt).all()

        notificaciones = []
        for notificacion_estadistica, reserva in results:
            try:
                notificaciones.append({
                    "id_reserva": reserva.id_reserva,
                    **noti_stats_schema.dump(notificacion_estadistica)
                })
            except Exception as e:
                print("Error:", e)


        return notificaciones, 200
    
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
def delete_notification(id_capitan, id_partido):
    try:
        notification = Notificacion_estadistica.query.filter_by(
            id_capitan=id_capitan, 
            id_partido=id_partido).first()
        if not notification:
            return False
        db.session.delete(notification)
        return True
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)})