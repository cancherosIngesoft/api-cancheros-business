from flask import Blueprint, jsonify, request
from app.models.Partido import Partido
from app.models.Reserva import Reserva
from app.routes.Subequipo_route import create_subequipo
from app import db
from app.schemas.Partido_sch import PartidoSchema

partido_schema = PartidoSchema()

partido_bp = Blueprint('partidos', __name__)


@partido_bp.route('/partido/add_marcador', methods = ['PATCH'])
def post_marcador():
    try: 
        data = request.get_json()

        id_paritdo = db.session.query(Reserva.id_partido).filter(Reserva.id_reserva == data.get('idReservation')).first()[0]

        goles_A = data.get('score')[0]

        goles_B = data.get('score')[1]

        db.session.query(Partido).filter(Partido.id_partido == id_paritdo).update({"goles_A": goles_A, "goles_B": goles_B})
        db.session.commit()

        return jsonify( {'message' : 'Marcador agregado con exito'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

def create_partido(data):
    id_equipo = data["id_equipo"]

    try:
        subequipo_A = create_subequipo({
            "nombre": "Equipo A"
        })
        subequipo_B = create_subequipo({
            "nombre": "Equipo B"
        })

        print(subequipo_A)
        nuevo_partido = Partido(
            id_equipo = id_equipo,
            id_subequipoA = subequipo_A[0]["id_subequipo"],
            id_subequipoB =subequipo_B[0]["id_subequipo"]
        )
        db.session.add(nuevo_partido)
        db.session.commit()

        return partido_schema.dump(nuevo_partido), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    


