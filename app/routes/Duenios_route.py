
from decimal import Decimal
from flask import request, Blueprint, jsonify,current_app

from app.models.Duenio import Duenio
from app import db
from app.routes.Reservas_route import calcular_reporte_financiero

duenios_bp = Blueprint('duenios', __name__)


@duenios_bp.route('/owner/debt/<int:id_owner>', methods = ['GET'])
def get_comission_amount(id_owner):
    try:
        owner = Duenio.query.get(id_owner)
        if not owner:
            return jsonify({"error": "Duenio de cancha no encontrado"}), 404
        
        report_financial = calcular_reporte_financiero(id_owner)
        comission_amount = owner.commission_amount if not owner.commission_amount else float(owner.commission_amount)
        return jsonify({
            "commission_amount": comission_amount,
            "total_profit": report_financial["total_profit"]
        }), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

def update_comission(id_host):
    try:
        host = Duenio.query.get(id_host)
        if not host:
            return jsonify({"error": "Host de cancha no encontrado"}), 404

        host.commission_amount = 0
        db.session.commit()
        return
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400