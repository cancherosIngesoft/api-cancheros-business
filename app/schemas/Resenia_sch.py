from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Establecimiento_sch import EstablecimientoSchema
from app.schemas.Usuario_sch import UsuarioSchema

class ReseniaSchema(Schema):
    id_resenia = fields.Integer(dump_only=True)
    autor = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])
    establecimiento = fields.Nested(EstablecimientoSchema)
    comentario = fields.String()
    calificacion = fields.Integer()
