from marshmallow import fields, Schema
from marshmallow import Schema, fields

class AdminSchema(Schema):
    id_admin = fields.Integer(dump_only=True)
    correo = fields.String()
