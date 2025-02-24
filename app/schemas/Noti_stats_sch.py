from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Partido_sch import PartidoSchema
from app.schemas.Usuario_sch import UsuarioSchema

class NotificacionEstadisticaSchema(Schema):
    id_noti_stats = fields.Integer(dump_only=True)
    partido = fields.Nested(PartidoSchema(only=(["equipo"])))
    # capitan = fields.Nested(UsuarioSchema,  exclude=["'es_capitan", "es_jugador", "es_aficionado"])