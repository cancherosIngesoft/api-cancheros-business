from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Equipo_sch import EquipoSchema

class SubequipoSchema(Schema):
    id_subequipo = fields.Integer(dump_only=True, data_key = 'idTeam')
    nombre = fields.String(data_key='teamName')

class TeamReturn(Schema):
    idTeam = fields.Integer(dump_only=True)
    teamName = fields.String( )
    members = fields.List( fields.String())
    score = fields.Integer(allow_none = True)

