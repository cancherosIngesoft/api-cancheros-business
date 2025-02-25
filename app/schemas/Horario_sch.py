from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Establecimiento_sch import EstablecimientoSchema

class HorarioSchema(Schema):
    id_horario = fields.Integer(dump_only=True)
    dia = fields.String()
    hora_inicio = fields.String()
    hora_fin = fields.String()

class HorarioReturn(Schema):
    id_horario = fields.Integer(dump_only=True)
    dia = fields.String(data_key = "day")
    hora_inicio = fields.String(data_key = "startTime")
    hora_fin = fields.String(data_key = "endTime")
