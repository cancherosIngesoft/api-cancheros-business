from marshmallow import fields, Schema


class CanchaSchema(Schema):
    id_cancha = fields.Integer(dump_only=True)
    id_establecimiento = fields.Integer()
    capacidad = fields.Integer()
    tipo = fields.String()
    precio = fields.Float()
    descripcion = fields.String()
    nombre = fields.String()
    imagen1 = fields.String(allow_none=True)
    imagen2 = fields.String(allow_none=True)
    imagen3 = fields.String(allow_none=True)
    imagen4 = fields.String(allow_none=True)
    imagen5 = fields.String(allow_none=True)

    
class CanchaReservaInfo(Schema):
    imagen1 = fields.String(allow_none=True, data_key='fieldImg')
    capacidad  = fields.Integer(data_key='capacity')
    tipo  = fields.String(data_key='FieldType')
    precio = fields.Float()
    id_establecimiento = fields.Integer()

class CanchaSchemaBusiness(CanchaSchema):
    from app.schemas.Establecimiento_sch import EstablecimientoSchema
    establecimiento =  fields.Nested(EstablecimientoSchema)