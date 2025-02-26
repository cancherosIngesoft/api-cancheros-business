from flask import Blueprint, jsonify, request
from sqlalchemy import delete, insert
from app import db
from app.models.Partido import Partido
from app.models.Reserva import Reserva
from app.models.Subequipo import Subequipo
from app.models.Usuario import Usuario
from app.models.Miembro_equipo import Miembro_equipo
from app.models.Plantilla import plantilla
from app.schemas.Subequipo_sch import SubequipoSchema
from app.utils.utils import is_in_team

Subequipo_schema = SubequipoSchema()
subequipo_bp = Blueprint('subequipos', __name__)

@subequipo_bp.route('/subequipos/reserva/<int:id_reserva>', methods = ['GET'])
def get_subequipos_reserva(id_reserva):
    try: 
        subequipos_info = (
        db.session.query(Partido.id_subequipoA, Partido.id_subequipoB, Partido.goles_A, Partido.goles_B)
        .join(Reserva, Reserva.id_partido == Partido.id_partido)
        .filter(Reserva.id_reserva == id_reserva)
        ).first()
        
        id_subA = subequipos_info[0]
        id_subB = subequipos_info[1]
        subequipoA_info = {
            'idTeam' : id_subA ,
            'nameTeam' : get_name_subteam(id_subA ),
            'members' : get_members_subteam(id_subA),
            'score' : subequipos_info[2]
        }

        subequipoB_info = {
            'idTeam' : id_subB ,
            'nameTeam' : get_name_subteam(id_subB ),
            'members' : get_members_subteam(id_subB),
            'score' : subequipos_info[3]
        }

        return {'teamA' : subequipoA_info, 'teamB' : subequipoB_info}
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400


@subequipo_bp.route('/subequipos/post_to_subequipo', methods = ['POST'])
def post_player_subequipo():
    try: 
        data = request.get_json()
        
        id_equipo = get_equipo_in_reserva(data.get('id_reservation'))

        is_subquipo_valido = subequipo_valido(id_reserva=data.get('id_reservation'), id_subequipo=data.get('id_subTeam'))

        if not is_subquipo_valido:
            raise Exception("El subequipo no pertenece a la reserva")
        
        in_team = is_in_team(id_equipo, data.get('id_user'))
        
        if not in_team:
            raise Exception("El usuaio no pertenece al equipo")

        id_miembro  = ( (
        db.session.query(Miembro_equipo.id_miembro)  # Seleccionar el campo id_miembro
        .filter(Miembro_equipo.id_usuario == data.get('id_user'))  # Filtrar por id_usuario
        .filter(Miembro_equipo.id_equipo == id_equipo)  # Filtrar por id_equipo
        ).first())[0]

        already_in_subteam = already_confirmed_in_subequipo(data.get('id_subTeam'), id_miembro= id_miembro)

        if already_in_subteam:
            raise Exception("Usuario ya confirmado en el subequipo")

        stmt = insert(plantilla).values(
            id_subequipo= data.get('id_subTeam'),  
            id_miembro=id_miembro   
        )

        
        with db.engine.connect() as connection:
            connection.execute(stmt)
            connection.commit()  
        return jsonify({"msg": 'agregado con exito'}), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@subequipo_bp.route('/subequipos/delete_from_subequipo', methods = ['DELETE'])
def delete_from_subequipo_endpoint():
    try:
        data = request.get_json()
        id_reserva =  data.get("id_reservation")
        id_usuario = data.get("id_user")
        
        id_equipo = get_equipo_in_reserva(id_reserva)
        id_miembro = get_miembro_from_user(id_equipo= id_equipo, id_usuario= id_usuario)

        ids_subequipos_reserva = get_subteams_in_reserva(id_reserva)

        in_any_subequipo = False
        for id_subequipo in ids_subequipos_reserva:
            in_any_subequipo = already_confirmed_in_subequipo(id_miembro= id_miembro, id_subequipo=id_subequipo) or in_any_subequipo
            delete_from_subequipo(id_subequipo=id_subequipo, id_miembro=id_miembro)
        
        if not in_any_subequipo:
            raise ValueError('El usuario no pertenecía a ningún subequipo de la reserva')
        
        return jsonify({"message": "Usuario elimiando con exito del subequipo"}), 200 
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400


def get_miembro_from_user(id_equipo, id_usuario):
    id_miembro = None
    id_miembro_query =  db.session.query(
            Miembro_equipo.id_miembro
        ).filter(Miembro_equipo.id_equipo == id_equipo, Miembro_equipo.id_usuario == id_usuario).first()

    if id_miembro_query:
        id_miembro = id_miembro_query[0]
    return id_miembro

def get_subteams_in_reserva(id_reserva):

    id_partido_query = db.session.query(
            Reserva.id_partido
        ).filter(Reserva.id_reserva == id_reserva).first()
    
    id_partido = None
    subteams = []
    if id_partido_query:
        id_partido = id_partido_query[0]
    
        ids_subequipos_query = db.session.query(
                Partido.id_subequipoA,
                Partido.id_subequipoB
            ).filter(Partido.id_partido == id_partido).first()
        
        subteams = list(ids_subequipos_query)
    return subteams

def get_equipo_in_reserva(id_reserva):
    id_equipo_query = db.session.query(
            Reserva.id_reservante
        ).filter(Reserva.id_reserva == id_reserva).first()
    
    id_equipo = None
    if id_equipo_query:
        id_equipo = id_equipo_query[0]
    return id_equipo

def delete_from_subequipo(id_subequipo, id_miembro):
    stmt = delete(plantilla).where(
    (plantilla.c.id_subequipo == id_subequipo) &
    (plantilla.c.id_miembro == id_miembro)
    )

    db.session.execute(stmt)
    db.session.commit()

def subequipo_valido(id_reserva, id_subequipo):
    ids_subequipos = get_subteams_in_reserva(id_reserva)
    return id_subequipo in ids_subequipos

def already_confirmed_in_subequipo(id_subequipo, id_miembro):
    in_plantilla = db.session.query(plantilla).filter(plantilla.c.id_subequipo == id_subequipo).filter(plantilla.c.id_miembro == id_miembro).first()
    return in_plantilla is not None


def get_name_subteam(id_subequipo):
    name = db.session.query(
            Subequipo.nombre
        ).filter(Subequipo.id_subequipo== id_subequipo).first()
    
    return name[0]

def get_members_subteam(id_subequipo):
    nombres_miembros  = (
    db.session.query(Usuario.nombre)
    .join(Miembro_equipo, Miembro_equipo.id_usuario == Usuario.id_usuario)
    .join(plantilla, Miembro_equipo.id_miembro == plantilla.c.id_miembro)
    .filter(plantilla.c.id_subequipo == id_subequipo)).all()

    return list(map(lambda x: x[0], nombres_miembros))



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


def delete_subequipo(id_subequipo):
    try:
        subequipoA = Subequipo.query.get(id_subequipo)
        if not subequipoA:
            return jsonify({"error": "Subequipo no encontrado"}), 404
        
        db.session.delete(subequipoA)
        db.session.commit()

        return jsonify({"message": "Subequipo eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

