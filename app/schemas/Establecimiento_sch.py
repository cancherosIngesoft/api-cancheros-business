from marshmallow import fields, Schema
from marshmallow import Schema, fields

class EstablecimientoSchema(Schema):
    id_establecimiento = fields.Integer(dump_only=True)
    rut = fields.String()
    altitud = fields.Float()
    longitud = fields.Float()