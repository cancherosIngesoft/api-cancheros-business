# from app.models.Horario_cancha import Horario_cancha
from app.models.Horario import Horario
from app.models.Cancha import Cancha
from app import db
from flask import request, Blueprint, jsonify
from app.schemas.schemas import HorarioSchema
from datetime import datetime


horarios_cancha_bp = Blueprint('horarios_cancha', __name__)

@horarios_cancha_bp.route('/set_horario_cancha', methods = ['POST'])
def set_horario():
    data = request.get_json()
    is_valid, error = validate_data(data)
    # if is_valid :
        # nuevo_hor = None
        # db.session.add(nuevo_hor)
        # db.session.commit()
        # TODO: el schema y modelos para horario cancha para subirlos
    return error



def validate_data(data):
    horario = Horario.query.filter_by(id_horario = data.get('id_horario')).first()
    cancha = Cancha.query.filter_by(id_cancha = data.get('id_cancha')).first()
    
    if horario and cancha:
        return True, "exito"
    
    return False, "ERROR: Horario y cancha deben existir previamnete"