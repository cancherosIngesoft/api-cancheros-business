import json
from app import db
from app.models.Equipo import Equipo
from app.models.Usuario import Usuario
from app.schemas.Equipo_sch import EquipoSchema
from app.utils.cloud_storage import gcs_upload_someIMG, FOLDER_CLUB
from flask import request, Blueprint, jsonify,current_app

clubes_bp = Blueprint('clubes', __name__)

@clubes_bp.route('/is_able_to_create_club/<int:id_user>', methods = ['GET'])
def is_able_to_create_club(id_user):
    try:
        count_clubs = db.session.query(Equipo).filter_by(id_capitan=id_user).count()
        if count_clubs < 5:
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
        json_data = request.form['json']
        data = json.loads(json_data)
        file = request.files["file"]
        file_data = file.read()
        file_name = file.filename
        
        if not file:
            file_url = None
        else:
            file_url = gcs_upload_someIMG(file_data, file_name, FOLDER_CLUB)

        data['imagen'] = file_url
        data['id_capitan'] = id_user
        equipo_data = EquipoSchema().load(data)
        nuevo_equipo = Equipo(**equipo_data)

        db.session.add(nuevo_equipo)
        
        usuario.es_capitan = True
        usuario.es_jugador = True
        usuario.es_aficionado = False

        db.session.commit()
        
        
        return jsonify({"message":"equipo creado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
