from marshmallow import fields, Schema

# from app.schemas.Establecimiento_sch import EstablecimientoSchema

class CanchaSchema(Schema):
    id_cancha = fields.Integer(dump_only=True)
    tamanio = fields.Integer()
    grama = fields.String()
    precio = fields.Float()
    descripcion = fields.String
    nombre = fields.String