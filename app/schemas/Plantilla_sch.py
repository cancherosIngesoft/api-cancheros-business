from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Equipo_sch import EquipoSchema
from app.schemas.Usuario_sch import UsuarioSchema


class PlantillaSchema(Schema):
    equipo = fields.Nested(EquipoSchema)
    jugador = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])