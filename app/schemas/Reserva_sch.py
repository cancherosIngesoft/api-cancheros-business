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


class ReservaSchemaReservante(ReservaSchema):
    reservante = fields.Nested(ReservanteSchema)


class ReservaSchemaPersonalized(Schema):
    id_reserva = fields.Integer(dump_only=True, data_key="idReservation")
    hours = fields.Method('get_horas')

    def get_horas(self, obj):
        return {
            "horaInicio": obj.hora_inicio.isoformat(),
            "horaFin": obj.hora_fin.isoformat()
        }