from app import db
from app.models.Miembro_equipo import Miembro_equipo
from app.models.Reservante import Reservante
from app.schemas.Reservante_sch import ReservanteSchema
from flask import jsonify


def insert_into_reservante(data):
    try:
        reservante_data = ReservanteSchema(exclude=["reservante", "nombre"]).load(data)
        nuevo_reservante = Reservante(**reservante_data)

        db.session.add(nuevo_reservante)
        db.session.commit()
        return jsonify({"id": nuevo_reservante.id_reservante}), 200

    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error en la base de datos: {str(e)}") 
    
def is_in_team(id_equipo,id_usuario):
    miembro = ( (
        db.session.query(Miembro_equipo.id_miembro)  # Seleccionar el campo id_miembro
        .filter(Miembro_equipo.id_usuario == id_usuario)  # Filtrar por id_usuario
        .filter(Miembro_equipo.id_equipo == id_equipo)  # Filtrar por id_equipo
        ).first())
    return not miembro is None
