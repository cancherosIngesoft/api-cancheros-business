from marshmallow import fields, Schema
from schemas import *


objeto = {
    'es_capitan': True,
    'es_jugador': False,
    'es_aficionado': False
}
schema = UsuarioSchema().dump( {
        'id_usuario' : 1,
        'nombre': 'pepo',
        'correo':'correocreible',
        'es_capitan' : True,
        'es_jugador' : False,
        'es_aficionado' : False
    })



print(schema)  # Salida: 3000 (5000 - 2000) 