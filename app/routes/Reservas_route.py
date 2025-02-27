import unicodedata
import pandas as pd
import pytz
import requests
from datetime import datetime
from sqlalchemy import and_, func, or_, cast, Date, select
from app.models.Duenio import Duenio
from app.models.Horario import Horario
from app.models.Horario_cancha import Horario_cancha
from app.models.Plantilla import plantilla
from app.models.Miembro_equipo import Miembro_equipo
from app.models.Establecimiento import Establecimiento
from app.models.Reserva import Reserva
from app.models.Establecimiento import Establecimiento
from app.models.Equipo import Equipo
from app.models.Cancha import Cancha
from app.models.Partido import Partido
from app import db
from flask import request, Blueprint, jsonify
from app.models.Reservante import Reservante
from app.models.Subequipo import Subequipo
from app.models.Usuario import Usuario
from app.routes.Horarios_route import verify_hour_court
from app.routes.Partido_route import create_partido, delete_partido
from app.routes.Subequipo_route import delete_subequipo
from app.schemas.Horario_sch import HorarioSchema
from app.schemas.Establecimiento_sch import BusinessReservaInfo
from app.schemas.Canchas_sch import CanchaReservaInfo
from app.schemas.Horario_cancha_sch import HorarioCanchaSchema
from datetime import datetime, time, timedelta
import locale

from app.schemas.Reserva_sch import ReservaSchema, ReservaSchemaPersonalized, ReservaSchemaReservante, ReservationExtended, IndividualReservationReturn, TeamReservationReturn
from app.utils.utils import calculate_comission_court, get_bussines_information_reserva, get_cancha_information_reserva, is_in_team, retrieve_reserva_info


reservas_bp = Blueprint('reservas', __name__)
reserva_schema = ReservaSchema(many=True, exclude=["cancha"])
reserva_schema_unique = ReservaSchema(exclude=["cancha"])

reserva_schema_cancha = ReservaSchemaReservante(many=True)
reserva_schema_personalized = ReservaSchemaPersonalized(many=True)


@reservas_bp.route('/reservations/financial-report/business/<int:id_duenio>', methods = ['GET'])
def get_financial_report(id_duenio):
    id_court = request.args.get('id_court')
    month = request.args.get('month')
    year = request.args.get('year')

    resultado = calcular_reporte_financiero(id_duenio, id_court, month, year)

    if "error" in resultado:
        return jsonify({"error": resultado["error"]}), 400

    return jsonify(resultado), 200


def calcular_reporte_financiero(id_duenio, id_court=None, month=None, year=None):
    try:

        filtro_cancha = True if id_court is None else (Reserva.id_cancha == id_court)
        filtro_cancha_horarios = True if id_court is None else (Cancha.id_cancha == id_court)

        filtro_fecha = True
        if month and year:
            filtro_fecha = db.extract('month', Reserva.hora_inicio) == month
            filtro_fecha &= db.extract('year', Reserva.hora_inicio) == year

        reservas = Reserva.query.join(Cancha).join(Establecimiento).filter(
            Establecimiento.id_duenio == id_duenio,
            filtro_cancha,
            filtro_fecha
        ).all()

        df = pd.DataFrame([
            {
                "id_cancha": r.id_cancha,
                "hora_inicio": r.hora_inicio,
                "hora_fin": r.hora_fin,
                "precio": r.cancha.precio
            } 
            for r in reservas
        ])


        df["hora_inicio"] = pd.to_datetime(df["hora_inicio"])
        df["hora_fin"] = pd.to_datetime(df["hora_fin"])

        df["horas_reservadas"] = (df["hora_fin"] - df["hora_inicio"]).dt.total_seconds() / 3600

        df["precio"] = df["precio"].astype(float)
        df["precio_total"] = df["horas_reservadas"] * df["precio"]
        total_horas_reservadas = df["horas_reservadas"].sum()

        total_canchas = Cancha.query.join(Establecimiento).filter(
            Establecimiento.id_duenio == id_duenio
        ).count()

        horarios = (
            db.session.query(Horario.dia, Horario.hora_inicio, Horario.hora_fin, Cancha.id_cancha)
            .join(Horario_cancha, Horario.id_horario == Horario_cancha.id_horario)
            .join(Cancha, Horario_cancha.id_cancha == Cancha.id_cancha)
            .join(Establecimiento, Cancha.id_establecimiento == Establecimiento.id_establecimiento)
            .filter(
                Establecimiento.id_duenio == id_duenio,
                filtro_cancha_horarios
            )
            .all()
        )

        df_horarios = pd.DataFrame([
            {
                "id_cancha": h.id_cancha,
                "dia": h.dia,
                "hora_inicio": h.hora_inicio,
                "hora_fin": h.hora_fin
            } 
            for h in horarios
        ])

        df_horarios["hora_inicio"] = pd.to_datetime(df_horarios["hora_inicio"], format="%H:%M:%S").dt.hour
        df_horarios["hora_fin"] = pd.to_datetime(df_horarios["hora_fin"], format="%H:%M:%S").dt.hour

        df_horarios["horas_disponibles"] = df_horarios["hora_fin"] - df_horarios["hora_inicio"]

        fecha_min = df["hora_inicio"].min().date()
        fecha_max = df["hora_fin"].max().date()
        dias_consultados = (fecha_max - fecha_min).days + 1

        total_horas_disponibles = df_horarios["horas_disponibles"].sum() * dias_consultados / 7

        #Calculo final del porcentaje de uso
        porcentaje_uso = (total_horas_reservadas / total_horas_disponibles) * 100 if total_horas_disponibles > 0 else 0
        total_ingresos = df["precio_total"].sum()

        return {
            "use_porcentage": porcentaje_uso,
            "total_profit": total_ingresos
        }

    except Exception as e:
        return jsonify({"Error": str(e)}), 400

@reservas_bp.route('/reservations/business/<int:id_duenio>', methods = ['GET'])
def get_reservas_week_establecimiento(id_duenio):
    week = request.args.get('week_day')
    month = request.args.get('month')
    year = request.args.get('year') 

    try:

        filtro_month = True
        if month and year:
            filtro_month = db.extract('month', Reserva.hora_inicio) == month
            filtro_month &= db.extract('year', Reserva.hora_inicio) == year

        filtro_semana = True
        if week:
            inicio_semana = datetime.strptime(week, "%Y-%m-%d")
            fin_semana = inicio_semana + timedelta(days=7)
            fin_semana = fin_semana.replace(hour=23, minute=59, second=59)
            filtro_semana = (Reserva.hora_inicio >= inicio_semana) & (Reserva.hora_fin <= fin_semana)

        reservas = (
            Reserva.query
            .join(Cancha, Reserva.id_cancha == Cancha.id_cancha)
            .join(Establecimiento, Cancha.id_establecimiento == Establecimiento.id_establecimiento)
            .filter(
                Establecimiento.id_duenio == id_duenio,
                filtro_semana,
                filtro_month
                # Reserva.hora_inicio >= inicio_semana,  
                # Reserva.hora_fin <= fin_semana,
            )
            .order_by(Reserva.hora_inicio)
            .all()
        )

        return reserva_schema_personalized.dump(reservas), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    

    
@reservas_bp.route('/reservations/court/<int:id_cancha>', methods = ['GET'])
def get_reservas_week(id_cancha):
    week = request.args.get('week_day')

    try:
        reservas = None
        if not week:
            reservas = Reserva.query.filter(
                Reserva.id_cancha == id_cancha
            ).order_by(Reserva.hora_inicio)
        else:

            inicio_semana = datetime.strptime(week, "%Y-%m-%d")
            fin_semana = inicio_semana + timedelta(days=7)

            fin_semana = fin_semana.replace(hour=23, minute=59, second=59)

            reservas = Reserva.query.filter(
                Reserva.id_cancha == id_cancha,
                Reserva.hora_inicio >= inicio_semana,
                Reserva.hora_fin <= fin_semana
            ).order_by(Reserva.hora_inicio).all()

     

        return reserva_schema.dump(reservas), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 400
    
@reservas_bp.route('/reservation/<int:id_reservation>', methods = ['GET'])
def get_reserva(id_reservation):

    try:
        reserva = Reserva.query.get(id_reservation)
        return reserva_schema_unique.dump(reserva), 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 400


def delete_reservation(reserva):
    try:
        cancha_price = reserva.cancha.precio
        comision = calculate_comission_court(cancha_price)
        id_owner = reserva.cancha.establecimiento.id_duenio
        
        db.session.delete(reserva)
        if reserva.partido:
            partido = reserva.partido
            delete_partido(partido.id_partido)
            if partido.id_subequipoA:
                delete_subequipo(partido.id_subequipoA)
            if partido.id_subequipoB:
                delete_subequipo(partido.id_subequipoB)

        if reserva.estado_procesado:
            duenio = Duenio.query.get(id_owner)
            duenio.commission_amount =  duenio.commission_amount - comision
        
        db.session.commit()

        return True

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return False
    
@reservas_bp.route('/reservation/reference/<string:id_payment>', methods = ['DELETE'])
def delete_reservation_by_payment(id_payment):
    try:
        reserva = Reserva.query.filter_by(id_referencia_pago=id_payment).first()
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if delete_reservation(reserva):
            return jsonify({"message": "Reserva eliminada exitosamente"}), 200
        else:
            return jsonify({"error": "Ocurrió un error al eliminar la reserva"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@reservas_bp.route('/reservation/<string:id_reservation>', methods = ['DELETE'])
def delete_reservation_by_id(id_reservation):
    try:
        reserva = Reserva.query.get(id_reservation)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if delete_reservation(reserva):
            return jsonify({"message": "Reserva eliminada exitosamente"}), 200
        else:
            return jsonify({"error": "Ocurrió un error al eliminar la reserva"}), 500

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@reservas_bp.route('/booking', methods = ['POST'])
def create_reserva():
    data = request.get_json()
    try:
        is_team = data.get("isTeam")
        id_host = data.get("id_host")
        id_reservante = data.get("id_reservante")
        reservante = db.session.query(Reservante).filter_by(id_reservante=id_reservante).first()
        
        if not id_host:
            if not reservante:
                return jsonify({"error": "No existe el reservante"}), 404
        else:
            admin = db.session.query(Duenio).filter_by(id_duenio=id_host).first()
            if not admin:
                return jsonify({"error": "No existe el host"}), 404
        if is_team and not reservante.tipo_reservante == "equipo":
            return jsonify({"error": "El reservante no corresponde a un equipo"}), 404

        hora_inicio=data.get("hora_inicio")
        hora_fin=data.get("hora_fin")
        id_cancha=data.get("id_cancha")

        if not verify_hour_court(data):
            return jsonify({"error": "Este horario no esta disponible para esta cancha"}), 400
        nueva_hora_inicio = datetime.strptime(data.get("hora_inicio"), "%Y-%m-%d %H:%M:%S")
        nueva_hora_fin = datetime.strptime(data.get("hora_fin"), "%Y-%m-%d %H:%M:%S")
        
        reservas_solapadas = check_reservas_solapadas(id_cancha, hora_inicio, hora_fin)
        if reservas_solapadas:
            return jsonify({"error": "La reserva se solapa con otra existente"}), 400

        nueva_reserva = Reserva(
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            id_reservante=id_reservante if not id_host else None,
            id_cancha=id_cancha,
            id_host=id_host if id_host else None
        )
        db.session.add(nueva_reserva)

        if is_team:
            new_partido = create_partido({
                "id_equipo": id_reservante
            })
            id_partido = new_partido[0]["id_partido"]
            nueva_reserva.id_partido = id_partido
            print("Es un team", new_partido)


        db.session.commit()

        return reserva_schema_unique.dump(nueva_reserva), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@reservas_bp.route('/booking/reschedule/<int:id_reservation>', methods = ['PUT'])
def reschedule_reserva(id_reservation):
    data = request.get_json()

    try:
        reserva = Reserva.query.get(id_reservation)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        nueva_hora_inicio=data.get("hora_inicio")
        nueva_hora_fin=data.get("hora_fin")
        id_cancha = reserva.id_cancha
        data["id_cancha"] = id_cancha

        print(data)

        if not verify_hour_court(data):
            return jsonify({"error": "Este horario no esta disponible para esta cancha"}), 400
        
        reservas_solapadas = check_reservas_solapadas(id_cancha, nueva_hora_inicio, nueva_hora_fin)
        if reservas_solapadas:
            return jsonify({"error": "La reserva se solapa con otra existente"}), 400

        reserva.hora_inicio = nueva_hora_inicio
        reserva.hora_fin = nueva_hora_fin
        db.session.commit()

        return reserva_schema_unique.dump(reserva), 200
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

def check_reservas_solapadas(id_cancha, hora_inicio, hora_fin):
    reservas_solapadas = db.session.query(Reserva).filter(
            Reserva.id_cancha == id_cancha,
            or_(
                and_(
                    Reserva.hora_inicio <= hora_inicio, 
                    hora_inicio < Reserva.hora_fin
                ),
                and_(
                    Reserva.hora_inicio < hora_fin, 
                    hora_fin <= Reserva.hora_fin
                ),
                and_(
                    Reserva.hora_inicio >= hora_inicio, 
                    Reserva.hora_fin <= hora_fin
                )
            )
        ).all()
    
    return reservas_solapadas
    
def delete_reservation_by_id_reserva(id_reserva):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        db.session.delete(reserva)
        db.session.commit()

        return jsonify({"message": "Reserva eliminada exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    
    
def update_status(id_reserva, id_referencia):
    try:
        reserva = Reserva.query.get(id_reserva)
        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        reserva.estado_procesado = True
        reserva.id_referencia_pago = id_referencia
        db.session.commit()
        return
    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    

@reservas_bp.route('/reservations/active/<int:id_user>', methods = ['GET'])
def get_reservas_activas(id_user):
    try:

        reservas_individuales = get_reservas_reservante(id_user, in_team=False,activas= True)

        reservas_equipo = get_reservas_equipo_de_user(id_user, activas=True)
        return  jsonify(reservas_individuales + reservas_equipo)

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
@reservas_bp.route('/reservations/inactive/<int:id_user>', methods = ['GET'])
def get_reservas_inactivas(id_user):
    try:

        reservas_individuales = get_reservas_reservante(id_user, in_team=False,activas= False)

        reservas_equipo = get_reservas_equipo_de_user(id_user, False)
        return  jsonify(reservas_individuales + reservas_equipo)

    except Exception as e:
        db.session.rollback()
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

@reservas_bp.route('/reservations/active/club/<int:id_equipo>/<int:id_user>', methods = ['GET'])
def get_reservas_activas_equipo(id_equipo, id_user):
    try:
        in_team = is_in_team(id_equipo, id_user)
        if(in_team):
            return reservas_activas_equipo(id_equipo=id_equipo, id_user=id_user)
        else:
            raise Exception("El usuaio no pertenece al equipo")
 
    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400
    
def reservas_activas_equipo(id_equipo, id_user):

    try: 
        reservas = Reserva.query.filter(
                    Reserva.id_reservante == id_equipo,  
                    Reserva.hora_inicio >= datetime.now()).all()
        reservas_activas = []
        for reserva in reservas:
            reserva_individual = retrieve_reserva_info(reserva= reserva, id_equipo= id_equipo, id_user=id_user)
            reservas_activas.append(reserva_individual)
            
        return reservas_activas
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400     

    

def get_reservas_reservante(id_booker, in_team, activas):
        
        if activas:
            reservas = Reserva.query.filter(
                Reserva.id_reservante == id_booker,  
                Reserva.hora_inicio >= datetime.now()).all()
        else:
            reservas = Reserva.query.filter(
                Reserva.id_reservante == id_booker,  
                Reserva.hora_inicio < datetime.now()).all()
        
        reservas_activas = []
        for reserva in reservas:
            schema = IndividualReservationReturn()
            reserva_info = ReservaSchemaPersonalized().dump(reserva)
            cancha_info =  get_cancha_information_reserva(reserva.id_cancha)

            diferencia_horas = (reserva.hora_fin - reserva.hora_inicio).total_seconds() / 3600
            totalPrice = diferencia_horas * float(cancha_info.get('precio'))

            Business_info = get_bussines_information_reserva(cancha_info.get('id_establecimiento'))

            reserva_individual_data = {
                **reserva_info,
                **cancha_info,
                **Business_info,
                'totalPrice' : totalPrice,
                'idBooker' : id_booker,
                'inTeam' : in_team
            }

            #print('data', reserva_individual_data)
            if in_team:
                teamName_query = db.session.query(Equipo.nombre ).filter_by(id_equipo = id_booker).first()
                reserva_individual_data['teamName'] = teamName_query[0]
                teamCaptain_query = db.session.query(Equipo.id_capitan ).filter_by(id_equipo = id_booker).first()
                reserva_individual_data['idBooker'] = teamCaptain_query[0]
            
            
            reserva_individual = schema.dump(reserva_individual_data)      

            reservas_activas.append(reserva_individual)

        return reservas_activas

    

def get_reservas_equipo_de_user(id_user, activas):
    
        ids_equipo = db.session.query(Miembro_equipo.id_equipo).filter_by(id_usuario=id_user).all()

        reservas_equipos = []
        for id_equipo in ids_equipo:
            print('id', id_equipo[0])
            reservas = get_reservas_reservante(id_equipo[0], in_team=True, activas=activas)
            reservas_equipos.extend(reservas)
        
        return reservas_equipos
