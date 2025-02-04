from flask import jsonify
from app import db
from app.models.Subequipo import Subequipo
from app.schemas.Subequipo_sch import SubequipoSchema

Subequipo_schema = SubequipoSchema()

def create_subequipo(data):
    nombre = data["nombre"]

    try:
        nuevo_subequipo = Subequipo(
            nombre = nombre
        )
        db.session.add(nuevo_subequipo)
        db.session.commit()

        return Subequipo_schema.dump(nuevo_subequipo), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    