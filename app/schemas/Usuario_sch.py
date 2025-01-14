from marshmallow import fields, Schema
from marshmallow import Schema, fields


class UsuarioSchema(Schema):
    id_usuario = fields.Integer(dump_only=True)
    nombre = fields.String()
    correo = fields.String()
    es_capitan = fields.Boolean()
    es_jugador = fields.Boolean()
    es_aficionado = fields.Boolean()
    rol = fields.Method('get_rol_usuario')

    def get_rol_usuario(self, obj):
        rol = ''
        if obj['es_capitan']:
            rol = 'capitan'
        elif obj['es_jugador']:
            rol = 'jugador'
        else:
            rol = 'aficionado'
        return rol
 