from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Equipo_sch import EquipoSchema
from app.schemas.Subequipo_sch import SubequipoSchema

class PartidoSchema(Schema):
    id_partido = fields.Integer(dump_only=True)
    equipo = fields.Nested(EquipoSchema)
    subequipoA = fields.Nested(SubequipoSchema)
    subequipoB = fields.Nested(SubequipoSchema)
    goles_A = fields.Integer()
    goles_B = fields.Integer()

