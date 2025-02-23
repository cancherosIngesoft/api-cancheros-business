from decimal import Decimal
from flask import request, Blueprint, jsonify,current_app
from sqlalchemy import func, select

from app.models.Duenio import Duenio
from app import db
from app.models.Notificacion_estadistica import Notificacion_estadistica
from app.models.Partido import Partido
from app.models.Reserva import Reserva
from app.routes.Reservas_route import calcular_reporte_financiero

notificaciones_bp = Blueprint('notificaciones', __name__)


@notificaciones_bp.route('/notifications/check-reservations-finished', methods = ['PUT'])
def check_reservations_finished():
    try:

        stmt = (
            select(Reserva, Partido)
            .join(Partido, Reserva.id_partido == Partido.id_partido)
            .outerjoin(Notificacion_estadistica, Partido.id_partido == Notificacion_estadistica.id_partido)
            .where(
                Reserva.hora_fin < func.now().op("AT TIME ZONE")("America/Bogota"),
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