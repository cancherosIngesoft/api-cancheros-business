from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Equipo_sch import EquipoSchema
from app.schemas.Subequipo_sch import SubequipoSchema

class PartidoSchema(Schema):
    id_partido = fields.Integer(dump_only=True)
    equipo = fields.Nested(EquipoSchema)
    subequipoA = fields.Nested(SubequipoSchema)
    subequipoB = fields.Nested(SubequipoSchema)
    goles_A = fields.Integer()
    goles_B = fields.Integer()

class ReturnPastMatches(Schema):
    idReservation = fields.Integer(data_key='idReservation')
    idField =  fields.Integer()
    hours = fields.Dict()  
    FieldType  = fields.String()
    businessDirection  = fields.String()
    businessName = fields.String()
    capacity  = fields.Integer()
    dateReservation = fields.Method('get_dateReserva')
    fieldImg = fields.String(allow_none= True)
    idBooker = fields.String()
    totalPrice = fields.Integer()
    geoGraphicalLocation = fields.Method('get_geoGraphicalLocation')
    isParticipating = fields.Boolean()
    teamAName = fields.String()
    teamBName = fields.String()
    score =  fields.List( fields.Dict )
    
    def get_geoGraphicalLocation(self,obj):
        return {
            'lat' : obj.get('lat'),
            'long' : obj.get('long')
        }
    
    def get_dateReserva(self,obj):
        horaInicio  = obj.get('hours').get('horaInicio')
        return  horaInicio[:10] 

