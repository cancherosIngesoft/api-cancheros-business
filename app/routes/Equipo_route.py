from app.models.Equipo import Equipo
from app.models.Usuario import Usuario
from app.schemas.Equipo_sch import ReturnClub, EquipoSchema
from app.models.Miembro_equipo import Miembro_equipo
from app import db
from flask import Blueprint, jsonify


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
            print('1', equipo_info)
            print(equipo_data)
            equipos.append( ReturnClub().dump( equipo_data)  )
        return equipos

    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
    
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
