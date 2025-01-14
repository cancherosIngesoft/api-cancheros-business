from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Usuario_sch import UsuarioSchema

class EquipoSchema(Schema):
    id_equipo = fields.Integer(dump_only=True)
    capitan = fields.Nested(UsuarioSchema(only=('id_usuario','nombre','correo')))
    nombre = fields.String()