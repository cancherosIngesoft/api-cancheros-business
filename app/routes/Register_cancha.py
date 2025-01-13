from app.models.Establecimiento import Establecimiento
from app.models.Cancha import Cancha
from flask import request, Blueprint, jsonify

cancha_bp = Blueprint('cancha', __name__)

@cancha_bp.route('/register_courts', methods = ['GET', 'POST'])
def reg_cancha():
    return 'hola'