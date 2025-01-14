from marshmallow import fields, Schema
from flask import current_app
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


import os

shapefile_path = os.path.join(current_app.root_path, 'static', 'Loca.shp')

# Verifica si el archivo existe
if not os.path.exists(shapefile_path):
    raise FileNotFoundError(f"El archivo no existe en la ruta: {shapefile_path}")
