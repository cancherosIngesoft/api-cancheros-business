from marshmallow import fields, Schema

from app.schemas.Establecimiento_sch import EstablecimientoSchema

class CanchaSchema(Schema):
    id_cancha = fields.Integer(dump_only=True)
    id_establecimiento = fields.Integer()
    capacidad = fields.Integer()
    tipo = fields.String()
    establecimiento =  fields.Nested(EstablecimientoSchema)
    precio = fields.Float()
    descripcion = fields.String()
    nombre = fields.String()