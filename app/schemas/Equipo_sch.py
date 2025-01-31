from marshmallow import fields, Schema
from marshmallow import Schema, fields

class EquipoSchema(Schema):
    id_equipo = fields.Integer(dump_only=True)
    id_capitan = fields.Integer()
    nombre = fields.String()
    imagen = fields.String()
    descripcion = fields.String()

class CapitanEquipoSchema(EquipoSchema):
    from app.schemas.Usuario_sch import UsuarioSchema
    capitan = fields.Nested(UsuarioSchema(only=('id_usuario','nombre','correo')))
