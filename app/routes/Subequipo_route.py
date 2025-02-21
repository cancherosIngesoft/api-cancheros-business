from flask import Blueprint, jsonify, request
from sqlalchemy import insert
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
        
        info_partido = ((
        db.session.query(Partido.id_equipo, Partido.id_partido)  
        .join(Reserva, Reserva.id_partido == Partido.id_partido)  
        .filter(Reserva.id_reserva == data.get('id_reservation'))  
        ).first())

        id_equipo = info_partido[0]
        id_partido = info_partido[1]

        is_subquipo_valido = subequipo_valido(id_partido= id_partido, id_subequipo=data.get('id_subTeam'))

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


def subequipo_valido(id_partido, id_subequipo):
    ids_subequipos = db.session.query(Partido.id_subequipoA, Partido.id_subequipoB).filter(Partido.id_partido == id_partido).first()
    id_subA = ids_subequipos[0]
    id_subB = ids_subequipos[1]
    return id_subequipo == id_subA or id_subequipo == id_subB

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

