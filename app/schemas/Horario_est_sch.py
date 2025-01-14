from marshmallow import fields, Schema
from app.schemas.Establecimiento_sch import EstablecimientoSchema
from app.schemas.Horario_sch import HorarioSchema

class HorarioEstablecimientoSchema(Schema):
    horario = fields.Nested(HorarioSchema)
    establecimiento = fields.Nested(EstablecimientoSchema)