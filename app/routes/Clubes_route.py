import json
from app import db
from app.models.Equipo import Equipo
from app.models.Reservante import Reservante
from app.models.Usuario import Usuario
from app.schemas.Equipo_sch import EquipoSchema
from app.utils.cloud_storage import gcs_upload_someIMG, FOLDER_CLUB
from app.utils.utils import insert_into_reservante
from flask import request, Blueprint, jsonify,current_app

clubes_bp = Blueprint('clubes', __name__)

#@clubes_bp.route('/is_able_to_create_club/<int:id_user>', methods = ['GET'])
def is_able_to_create_club(id_user):
    try:
        count_clubs = db.session.query(Equipo).filter_by(id_capitan=id_user).count()
        if count_clubs < 6:
            response = {'able' : True }
        else:
            response = {'able' : False }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clubes_bp.route('/create_club/<int:id_user>', methods = ['POST'])
def create_club(id_user):
    try:

        usuario = db.session.query(Usuario).filter(Usuario.id_usuario == id_user).first()
        if not usuario:
            raise ValueError('Usuario no existente')
        msg, _ = is_able_to_create_club(usuario.id_usuario)
        if not msg.get_json().get('able'): 
            raise ValueError('Usuario con más de 5 equipos')
        json_data = request.form['json']
        data = json.loads(json_data)
        file = request.files["file"]
        file_data = file.read()
        file_name = file.filename
        
        if not file:
            file_url = None
        else:
            file_url = gcs_upload_someIMG(file_data, file_name, FOLDER_CLUB)

        print(file_url)
        data['imagen'] = file_url
        data['id_capitan'] = id_user

        response_insert_reservante, _ = insert_into_reservante( {"tipo_reservante" : "equipo"} )
        id_reservante= response_insert_reservante.get_json().get('id') 

        try:
            equipo_data = EquipoSchema().load(data)
            nuevo_equipo = Equipo(id_equipo=id_reservante,**equipo_data)
            db.session.add(nuevo_equipo)     
            usuario.es_capitan = True
            usuario.es_jugador = True
            usuario.es_aficionado = False
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            db.session.query(Reservante).filter(Reservante.id_reservante == id_reservante).delete()
            db.session.commit()
            return jsonify({"error": str(e)}), 500
        
        
        
        return jsonify({"message":"equipo creado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@clubes_bp.route('/get_captain/<int:id_user>', methods = ['GET'])
def get_captain(id_user):
    try:
        usuario = db.session.query(Usuario).filter(Usuario.id_usuario == id_user).first()
        if not usuario:
            raise ValueError('Usuario no existente')
        
        equipos = Equipo.query.filter_by(id_capitan=id_user).all()

        clubes = []

        for equipo in equipos:
            equipo_schema = EquipoSchema(exclude=["id_capitan"]).dump(equipo)
            clubes.append(equipo_schema)
        
        return jsonify({"clubes":clubes}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
