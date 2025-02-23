from sqlalchemy import delete, select
from app.models.Equipo import Equipo
from app.models.Partido import Partido
from app.models.Usuario import Usuario
from app.models.Plantilla import plantilla
from app.schemas.Equipo_sch import ReturnClub, EquipoSchema
from app.models.Miembro_equipo import Miembro_equipo
from app import db
from flask import Blueprint, jsonify, request

from app.utils.utils import find_user_by_email, get_playersclub_info, is_captain_club


equipo_bp = Blueprint('equipos', __name__)


@equipo_bp.route('/usuario/clubes/<int:id_usuario>', methods = ['GET'])
def get_clubes_usuario(id_usuario):

    try: 
        ids_equipos =  db.session.query(Miembro_equipo.id_equipo).filter(Miembro_equipo.id_usuario == id_usuario).all()
        equipos = []
        for id_equipo, in ids_equipos:
            equipo = Equipo.query.filter(Equipo.id_equipo == id_equipo).first()
            equipo_info = EquipoSchema().dump(equipo)
            equipo_data = {
                **equipo_info,
                'numberPlayers' : count_number_members(id_equipo),
                'nameCapitan' : get_captain_name(id_equipo)
            }
            equipos.append( ReturnClub().dump( equipo_data)  )
        return equipos

    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@equipo_bp.route('/captain/delete_member', methods = ['DELETE'])
def captain_delete_member():
    try:
        data = request.get_json()
        id_equipo = data.get('idTeam')
        id_usuario = data.get('idUserToDelete')
        id_who_delete = data.get('idUserWhoDelete')

        if is_captain_club(id_who_delete, id_equipo):
            if id_usuario == id_who_delete:
                raise ValueError('El capitán no puede eliminarse así mismo, ve a salir del club') 
            delete_member(id_equipo, id_usuario)
            return jsonify({'message' : 'Usuario eliminado con exito'} ), 200
        else:
            raise ValueError('El usuario debe ser capitán para eliminar a otros miembros') 

    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@equipo_bp.route('/captain/add_members', methods = ['POST'])
def captain_add_members():
    try:
        data = request.get_json()
        id_equipo = data['idTeam']
        emails = data['emailsToAdd']
        id_who_delete = data['idUserWhoAdd']

        if is_captain_club(id_who_delete, id_equipo):

            for correo in emails:
                id_usuario = find_user_by_email(correo)
                if not id_usuario:
                    return
                if already_in_team(id_usuario, id_equipo):
                    raise ValueError('El jugador ya pertenece al club') 
                
                add_member(id_usuario, id_equipo )
                return jsonify({'message' : 'Usuario agregado con exito'} ), 200
        else:
            raise ValueError('El usuario debe ser capitán para agregar a otros miembros') 

    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@equipo_bp.route('/get_members/<int:id_team>', methods = ['GET'])
def get_members_club(id_team):
    try:
        miembros = members_club_info(id_team)
        miembros[1:] = sorted(miembros[1:], key=lambda x: x["name"])
        return miembros
    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@equipo_bp.route('delete_member', methods = ['DELETE'])
def user_delete_himself():
    try:
        data = request.get_json()
        id_equipo = data.get('idTeam')
        id_usuario = data.get('idUserToDelete')
        number_members = count_number_members(id_equipo)
        if number_members == 1: 
            raise ValueError('No puedes dejar a tu equipo sin miembros')
        
        if is_captain_club(id_equipo=id_equipo, id_capitan=id_usuario):
            new_captain = db.session.query(
            Miembro_equipo.id_usuario
            ).filter(Miembro_equipo.id_equipo== id_equipo, Miembro_equipo.id_usuario != id_usuario).first()

            db.session.query(Equipo).filter(Equipo.id_equipo == id_equipo).update({"id_capitan": new_captain[0]})

        delete_member(id_equipo=id_equipo, id_usuario=id_usuario)
        return jsonify({'message' : 'Usuario eliminado con exito'} ), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
def members_club_info(id_team):
    ids_usuarios = db.session.query(
    Miembro_equipo.id_usuario
    ).filter(Miembro_equipo.id_equipo== id_team).all()
    
    capitan = None
    index = 0 
    count =0 
    players = []
    for id_usuario, in ids_usuarios:
        schema = get_playersclub_info(id_team=id_team, id_usuario=id_usuario)
        players.append(schema)
        if schema.get('isCaptain'):
            capitan = schema
            index = count
        count += 1
    if count >= 0: # poner al capitan de primeras
        aux = players[0]
        players[0] = capitan
        players[index] = aux
        
    return players

def add_member(id_usuario, id_equipo):
    if id_usuario:
        nuevo_miembro = Miembro_equipo(
        id_usuario=id_usuario,  
        id_equipo=id_equipo
        )

        db.session.add(nuevo_miembro)
        db.session.commit()


def already_in_team(id_usuario, id_equipo): 
        already_in =  db.session.query(
        Miembro_equipo.id_miembro
        ).filter(Miembro_equipo.id_equipo== id_equipo,Miembro_equipo.id_usuario == id_usuario ).first()

        return already_in is not None

def delete_member(id_equipo, id_usuario):
    delete_from_plantilla(id_equipo, id_usuario)
    db.session.query(Miembro_equipo).filter(Miembro_equipo.id_equipo == id_equipo, Miembro_equipo.id_usuario == id_usuario).delete()
    db.session.commit()

def delete_from_plantilla(id_equipo, id_usuario):
    ids_subequipos = db.session.query(
        Partido.id_subequipoA,
        Partido.id_subequipoB
    ).filter(Equipo.id_equipo== id_equipo).all()

    for id_subequipoA, id_subequipoB in ids_subequipos:

        id_miembro_obj = db.session.query(
        Miembro_equipo.id_miembro
        ).filter(Miembro_equipo.id_equipo== id_equipo,Miembro_equipo.id_usuario == id_usuario ).first()

        id_miembro = None

        if id_miembro_obj:
            id_miembro = id_miembro_obj[0]

        stmt = delete(plantilla).where(
        ((plantilla.c.id_subequipo == id_subequipoA) | (plantilla.c.id_subequipo == id_subequipoB)) &
        (plantilla.c.id_miembro == id_miembro)
        )

        db.session.execute(stmt)
        db.session.commit()

def count_number_members(id_equipo):
    count = db.session.query(db.func.count()).filter(
    Miembro_equipo.id_equipo == id_equipo
    ).scalar()

    return count

def get_captain_name(id_equipo):
    capitan_nombre = (db.session.query(Usuario.nombre)
                      .join(Equipo, Equipo.id_capitan == Usuario.id_usuario)
                      .filter(Equipo.id_equipo == id_equipo).scalar())
    return capitan_nombre
