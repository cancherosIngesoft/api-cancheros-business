from marshmallow import fields, Schema
from app.schemas.Canchas_sch import CanchaSchema
from app.schemas.Horario_sch import HorarioSchema

class HorarioEstablecimientoSchema(Schema):
    horario = fields.Nested(HorarioSchema)
    cancha = fields.Nested(CanchaSchema)