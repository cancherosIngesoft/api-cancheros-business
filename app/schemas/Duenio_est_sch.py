from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Establecimiento_sch import EstablecimientoSchema
from app.schemas.Duenio_sch import DuenioSchema

class DuenioEstablecimientoSchema(Schema):
    establecimiento = fields.Nested(EstablecimientoSchema)
    duenio = fields.Nested(DuenioSchema)