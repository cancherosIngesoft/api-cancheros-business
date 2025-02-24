from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Canchas_sch import CanchaSchema
from app.schemas.Partido_sch import PartidoSchema
from app.schemas.Reservante_sch import ReservanteSchema

class ReservaSchema(Schema):
    id_reserva = fields.Integer(dump_only=True)
    cancha = fields.Nested(CanchaSchema)
    partido = fields.Nested(PartidoSchema(only=("equipo","goles_A","goles_B", "subequipoA", "subequipoB")))
    reservante = fields.Nested(ReservanteSchema(exclude=(["reservante"])))
    hora_inicio = fields.DateTime()
    hora_fin = fields.DateTime()
    estado_procesado = fields.Boolean()
    id_referencia_pago = fields.String()


class ReservaSchemaReservante(ReservaSchema):
    reservante = fields.Nested(ReservanteSchema)


class ReservaSchemaPersonalized(Schema):
    id_reserva = fields.Integer(dump_only=True, data_key="idReservation")
    hours = fields.Method('get_horas')
    id_cancha = fields.Integer(required = False, data_key="idField")
    id_referencia_pago = fields.String()

    def get_horas(self, obj):
        return {
            "horaInicio": obj.hora_inicio.isoformat(),
            "horaFin": obj.hora_fin.isoformat()
        }
    

class ReservationExtended(Schema):
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
    id_referencia_pago = fields.String()
    
    def get_dateReserva(self,obj):
        horaInicio  = obj.get('hours').get('horaInicio')
        return  horaInicio[:10] 

class IndividualReservationReturn(ReservationExtended):
    inTeam = fields.Boolean()
    teamName = fields.String(allow_none=True)

class TeamReservationReturn(ReservationExtended):
    geoGraphicalLocation = fields.Method('get_geoGraphicalLocation')
    isParticipating = fields.Boolean()
    teamAName = fields.String()
    teamBName = fields.String()
    id_referencia_pago = fields.String()
    
    def get_geoGraphicalLocation(self,obj):
        return {
            'lat' : obj.get('lat'),
            'long' : obj.get('long')
        }