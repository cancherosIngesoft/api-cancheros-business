from marshmallow import fields, Schema
from marshmallow import Schema, fields
 
class DuenioSchema(Schema):
    id_duenio = fields.Integer(dump_only=True)
    nombre = fields.String()
    correo = fields.String()
    apellido = fields.String() 
    tipo_doc = fields.String() 
    documento = fields.Integer()
    telefono = fields.String() 
    fecha_nacimiento = fields.DateTime()