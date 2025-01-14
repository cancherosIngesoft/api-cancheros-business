from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Partido_sch import PartidoSchema
from app.schemas.Usuario_sch import UsuarioSchema
from app.schemas.Reserva_sch import ReservaSchema

class NotificacionReservaSchema(Schema):
    id_noti_reserva = fields.Integer(dump_only=True)
    partido = fields.Nested(PartidoSchema(only=("equipo","goles_a","goles_b")))
    invitado = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])
    reserva = fields.Nested(ReservaSchema(only=("cancha", "reservante","hora_inicio","hora_fin")))
    es_aceptada = fields.Boolean()