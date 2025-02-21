from decimal import ROUND_HALF_UP, Decimal
import hashlib
import hmac
import json
from flask import Blueprint, current_app, jsonify, request
import requests

from app.models.Duenio import Duenio
from app.models.Reserva import Reserva
from app.routes.Reservas_route import update_status
from app import db


payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/webhook', methods = ['POST'])
def webhook():
    WEBHOOK_SECRET = current_app.config["SECRET_WEBHOOK"]
    MERCADO_PAGO_ACCESS_TOKEN = current_app.config["MERCADO_PAGO_ACCESS_TOKEN"]
    print("Procesado")
    try:
        xSignature = request.headers.get("x-signature")
        xRequestId = request.headers.get("x-request-id")

        if not xSignature:
            return jsonify({"error": "Firma no proporcionada"}), 400

        dataID = request.args.get('data.id')
        parts = xSignature.split(",")

        ts = None
        hash = None

        for part in parts:
            keyValue = part.split("=", 1)
            if len(keyValue) == 2:
                key = keyValue[0].strip()
                value = keyValue[1].strip()
                if key == "ts":
                    ts = value
                elif key == "v1":
                    hash = value


        manifest = f"id:{dataID};request-id:{xRequestId};ts:{ts};"
        hmac_obj = hmac.new(WEBHOOK_SECRET.encode(), msg=manifest.encode(), digestmod=hashlib.sha256)

        sha = hmac_obj.hexdigest()
        if not sha == hash:
            return jsonify({"error": "Firma inválida"}), 401

        data = request.json
        print(data)
        event_type = data.get('type')
        resource_id = data.get('data', {}).get('id')

        if event_type == 'payment':
            print(f"Pago recibido: {resource_id}")
            url = f"https://api.mercadopago.com/v1/payments/{resource_id}"
            headers = {
                "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"
            }
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                payment_details = response.json()
                items = payment_details.get("additional_info", {}).get("items", [])
                reserva_id = items[0].get("id")

                update_status(reserva_id, resource_id)
                calculate_commision(reserva_id)
        else:
            print(f"Evento no manejado: {event_type}")

        
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

def calculate_commision(id_reserva):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        cancha_price = reserva.cancha.precio
        comision = (
            ((cancha_price / Decimal('2') * Decimal('0.0329') + Decimal('952')) * Decimal('0.19')) 
            + (cancha_price * Decimal('0.05'))
        )
        comision = comision.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

        id_duenio = reserva.cancha.establecimiento.id_duenio
        duenio = Duenio.query.get(id_duenio)
        duenio.commission_amount = comision if not duenio.commission_amount else duenio.commission_amount + comision
        
        db.session.commit()
        return
    except Exception as e:
        db.session.rollback()
        print("Error:", e)