from marshmallow import fields, Schema
from marshmallow import Schema, fields
 
class DuenioSchema(Schema):
    id_duenio = fields.Integer(dump_only=True)
    nombre = fields.String()
    apellido = fields.String() 