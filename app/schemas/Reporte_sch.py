from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Establecimiento_sch import EstablecimientoSchema

class ReporteSchema(Schema):
    id_reporte = fields.Integer(dump_only=True)
    establecimiento = fields.Nested(EstablecimientoSchema)
    horas_alquiladas = fields.Integer()
    dinero_generado = fields.Integer()