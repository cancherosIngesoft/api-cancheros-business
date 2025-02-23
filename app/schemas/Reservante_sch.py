from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Usuario_sch import UsuarioSchema
from app.schemas.Equipo_sch import EquipoSchema


class ReservanteSchema(Schema):
    id_reservante = fields.Integer(dump_only=True)
    tipo_reservante = fields.String()
    nombre = fields.Method("get_nombre")
    reservante = fields.Method('get_reservante_detalle')

    def get_nombre(self, obj):
        return obj.nombre

    def get_reservante_detalle(self, obj):

        if obj.tipo_reservante == 'usuario' and obj.id_reservante:

            return UsuarioSchema(only=("id_usuario","nombre")).dump(
                {'id_usuario': obj.id_reservante, 
                 'nombre': obj.nombre, 
                #  'rol':obj.rol
                 }
            )
        elif obj.tipo_reservante  == 'equipo' and obj.id_reservante:
       
            return EquipoSchema(only=("id_equipo","nombre","capitan")).dump(
                {'id_equipo': obj.id_reservante, 
                 'nombre': obj.nombre, 
                 'capitan':obj.capitan #TODO: que muestre la info del capitan anidado
                 }
                )