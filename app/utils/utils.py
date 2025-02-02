from app import db
from app.models.Reservante import Reservante
from app.schemas.Reservante_sch import ReservanteSchema
from flask import jsonify


def insert_into_reservante(data):
    try:
        reservante_data = ReservanteSchema(exclude=["reservante"]).load(data)
        nuevo_reservante = Reservante(**reservante_data)

        db.session.add(nuevo_reservante)
        db.session.commit()
        return jsonify({"id": nuevo_reservante.id_reservante}), 200

    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error en la base de datos: {str(e)}") 
