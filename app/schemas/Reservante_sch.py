from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Usuario_sch import UsuarioSchema
from app.schemas.Equipo_sch import EquipoSchema


class ReservanteSchema(Schema):
    id_reservante = fields.Integer(dump_only=True)
    tipo_reservante = fields.String()
    reservante = fields.Method('get_reservante_detalle')


    def get_reservante_detalle(self, obj):
        if obj['tipo_reservante'] == 'usuario' and obj.get('id_usuario'):

            return UsuarioSchema().dump(
                {'id_usuario': obj['id_usuario'], 
                 'nombre': obj['nombre'], 
                 'rol':obj['rol']
                 }
            )
        elif obj['tipo_reservante'] == 'equipo' and obj.get('id_equipo'):
       
            return EquipoSchema().dump(
                {'id_equipo': obj['id_equipo'], 
                 'nombre': obj['nombre'], 
                 'capitan':obj['capitan'] #TODO: que muestre la info del capitan anidado
                 }
                )