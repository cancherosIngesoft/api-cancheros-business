from datetime import datetime
from sqlalchemy import select
from app import db
from app.models.Cancha import Cancha
from app.models.Equipo import Equipo
from app.models.Establecimiento import Establecimiento
from app.models.Miembro_equipo import Miembro_equipo
from app.models.Partido import Partido
from app.models.Plantilla import plantilla
from app.models.Reserva import Reserva
from app.models.Reservante import Reservante
from app.models.Subequipo import Subequipo
from app.models.Usuario import Usuario
from app.schemas.Canchas_sch import CanchaReservaInfo
from app.schemas.Equipo_sch import ReturnPlayersClub
from app.schemas.Establecimiento_sch import BusinessReservaInfo
from app.schemas.Partido_sch import ReturnPastMatches
from app.schemas.Reserva_sch import ReservaSchemaPersonalized, TeamReservationReturn
from app.schemas.Reservante_sch import ReservanteSchema
from flask import jsonify


def insert_into_reservante(data):
    try:
        reservante_data = ReservanteSchema(exclude=["reservante", "nombre"]).load(data)
        nuevo_reservante = Reservante(**reservante_data)

        db.session.add(nuevo_reservante)
        db.session.commit()
        return jsonify({"id": nuevo_reservante.id_reservante}), 200

    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Error en la base de datos: {str(e)}") 
    

def date_to_int(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d"))

def counting_sort(arr, exp, key_func):
    n = len(arr)
    output = [0] * n
    count = [0] * 10  

    for item in arr:
        index = (key_func(item) // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        item = arr[i]
        index = (key_func(item) // exp) % 10
        output[count[index] - 1] = item
        count[index] -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr, key_func):
    if not arr:
        return

    max_val = max(key_func(item) for item in arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort(arr, exp, key_func)
        exp *= 10

def order_matches(matches):
    print('id1 ', id(matches))
    radix_sort(matches, key_func=lambda x: date_to_int(x["dateReservation"]))
    print('id2 ', id(matches))
    return matches

def past_matches(id_equipo, id_user):
    try: 
        reservas = Reserva.query.filter(
                    Reserva.id_reservante == id_equipo,  
                    Reserva.hora_inicio < datetime.now()).all()
        reservas_activas = []
        for reserva in reservas:
            reserva_data = retrieve_reserva_info(reserva= reserva, id_equipo= id_equipo, id_user=id_user)
            score_data = get_score_partido_info(reserva.id_partido)
            match_data = {
                **reserva_data,
                "score" : score_data
            }

            print("score", score_data)
            past_match = ReturnPastMatches().dump(match_data)
            reservas_activas.append(past_match)
            
        return reservas_activas
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"Error": str(e)}), 400

def get_score_partido_info(id_partido):
    partido_info = db.session.query(
            Partido.id_subequipoA,
            Partido.id_subequipoB,
            Partido.goles_A,
            Partido.goles_B
        ).filter(Partido.id_partido == id_partido).first()
    
    ids_subequipos = [partido_info[0], partido_info[1]]
    goles = [partido_info[2], partido_info[3]]
    score = []
    if goles[0] is not None and goles[1] is not None:
        i = 0
        for id_subequipo in ids_subequipos:
            subequipo_nombre = db.session.query(
                Subequipo.nombre
            ).filter(Subequipo.id_subequipo == id_subequipo).first()

            schema = { 
                'teamName' : subequipo_nombre[0],
                'teamId' : id_subequipo,
                'score' : goles[i]
            }
            i += 1
            score.append(schema)

    return score

def is_in_team(id_equipo,id_usuario):
    miembro = ( (
        db.session.query(Miembro_equipo.id_miembro)  # Seleccionar el campo id_miembro
        .filter(Miembro_equipo.id_usuario == id_usuario)  # Filtrar por id_usuario
        .filter(Miembro_equipo.id_equipo == id_equipo)  # Filtrar por id_equipo
        ).first())
    return not miembro is None


def retrieve_reserva_info(reserva, id_equipo, id_user):
    schema = TeamReservationReturn()
    reserva_info = ReservaSchemaPersonalized().dump(reserva)
    #print('res', reserva_info)
    cancha_info =  get_cancha_information_reserva(reserva.id_cancha)
    #print('hola', cancha_info)

    diferencia_horas = (reserva.hora_fin - reserva.hora_inicio).total_seconds() / 3600
    totalPrice = diferencia_horas * float(cancha_info.get('precio'))

    Business_info = get_bussines_information_reserva(cancha_info.get('id_establecimiento'))

    subequipos_info = get_subequipo_information_reserva(reserva.id_partido)

    is_participating  = get_is_participating(id_partido= reserva.id_partido,id_user=id_user )

    teamCaptain_query = db.session.query(Equipo.id_capitan ).filter_by(id_equipo = id_equipo).first()            

    reserva_individual_data = {
        **reserva_info,
        **cancha_info,
        **Business_info,
        **subequipos_info,
        'totalPrice' : totalPrice,
        'idBooker' : teamCaptain_query[0],
        'isParticipating' : is_participating
    }


    return schema.dump(reserva_individual_data)   

def get_cancha_information_reserva(id_cancha):
    cancha_info = db.session.query(
            Cancha.imagen1,
            Cancha.capacidad,
            Cancha.tipo,
            Cancha.precio,
            Cancha.id_establecimiento
        ).filter(Cancha.id_cancha == id_cancha).first()
    
    schema = CanchaReservaInfo()
    return schema.dump(cancha_info)

def get_is_participating(id_partido, id_user):
    ids_subequipos = db.session.query(
            Partido.id_subequipoA,
            Partido.id_subequipoB
        ).filter(Partido.id_partido == id_partido).first()
    
    is_participating = False

    for id_subequipo in ids_subequipos:
        query = select(plantilla.c.id_subequipo, plantilla.c.id_miembro).where(
        (plantilla.c.id_subequipo == id_subequipo) &
        (plantilla.c.id_miembro == id_user)
        )
        result = db.session.execute(query).fetchone()
        is_in_subequipo = result is not None

        is_participating = is_participating or is_in_subequipo

    return is_participating


def get_bussines_information_reserva(id_establecimiento):
    Business_info = db.session.query(
                    Establecimiento.nombre,
                    Establecimiento.direccion,
                    Establecimiento.altitud,
                    Establecimiento.longitud
                ).filter(Establecimiento.id_establecimiento == id_establecimiento).first()
    schema = BusinessReservaInfo()
    return schema.dump(Business_info)



def get_subequipo_information_reserva(id_partido):
    ids_subequipos = db.session.query(
            Partido.id_subequipoA,
            Partido.id_subequipoB
        ).filter(Partido.id_partido == id_partido).first()
    subequipos_info = {}
    claves = ['teamAName',  'teamBName']
    i = 0
    for id_subequipo in ids_subequipos:
        subequipo_nombre = db.session.query(
            Subequipo.nombre
        ).filter(Subequipo.id_subequipo == id_subequipo).first()
        subequipos_info[ claves[i] ] = subequipo_nombre[0]
        i += 1

    return subequipos_info 

def find_user_by_email(email):
    id_user = db.session.query(
            Usuario.id_usuario,
        ).filter(Usuario.correo== email).first()
    
    if id_user:
        return id_user[0]
    else:
        return None

def is_captain_club(id_capitan, id_equipo):
    id_real_cap = db.session.query(
        Equipo.id_capitan
    ).filter(Equipo.id_equipo== id_equipo).first()

    if id_real_cap:
        return id_real_cap[0] == id_capitan
    return False



def get_playersclub_info(id_usuario, id_team):
    name =  db.session.query(
        Usuario.nombre
        ).filter(Usuario.id_usuario== id_usuario).first()
    
    data = {
        "idPlayer": id_usuario, 
        "name" : name[0], 
        "isCaptain": is_captain_club(id_capitan=id_usuario, id_equipo=id_team)
        }
    
    return ReturnPlayersClub().dump(data)