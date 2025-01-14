from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Equipo_sch import EquipoSchema

class SubequipoSchema(Schema):
    id_subequipo = fields.Integer(dump_only=True)
    equipo = fields.Nested(EquipoSchema)
    nombre = fields.String()