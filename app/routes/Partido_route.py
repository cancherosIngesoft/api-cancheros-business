from flask import jsonify
from app.models.Partido import Partido
from app.routes.Subequipo_route import create_subequipo
from app import db
from app.schemas.Partido_sch import PartidoSchema

partido_schema = PartidoSchema()

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