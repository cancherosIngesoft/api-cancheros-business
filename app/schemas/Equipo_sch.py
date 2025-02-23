from marshmallow import fields, Schema

class EquipoSchema(Schema):
    id_equipo = fields.Integer(dump_only=True)
    id_capitan = fields.Integer()
    nombre = fields.String()
    imagen = fields.String(allow_none= True)
    descripcion = fields.String(allow_none=True)


class ReturnClub(Schema):
    from app.schemas.Usuario_sch import UsuarioSchema
    id_equipo = fields.Integer(dump_only=True, data_key = 'idTeam')
    id_capitan = fields.Integer(data_key = 'idCaptain')
    nombre = fields.String(data_key = 'teamName')
    imagen = fields.String(allow_none= True, data_key= 'icon')
    descripcion = fields.String(allow_none=True, data_key='description')
    nameCapitan = fields.String()
    numberPlayers = fields.Integer()

class CapitanEquipoSchema(EquipoSchema):
    from app.schemas.Usuario_sch import UsuarioSchema
    capitan = fields.Nested(UsuarioSchema(only=('id_usuario','nombre','correo')))


class ReturnPlayersClub(Schema):
    idPlayer = fields.String()
    name = fields.String()
    isCaptain = fields.Boolean()

