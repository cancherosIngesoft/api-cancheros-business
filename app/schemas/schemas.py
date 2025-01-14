from marshmallow import fields, Schema
from marshmallow import Schema, fields


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

    
class UsuarioSchema(Schema):
    id_usuario = fields.Integer(dump_only=True)
    nombre = fields.String()
    correo = fields.String()
    es_capitan = fields.Boolean()
    es_jugador = fields.Boolean()
    es_aficionado = fields.Boolean()
    rol = fields.Method('get_rol_usuario')

    def get_rol_usuario(self, obj):
        rol = ''
        if obj['es_capitan']:
            rol = 'capitan'
        elif obj['es_jugador']:
            rol = 'jugador'
        else:
            rol = 'aficionado'
        return rol
 
class DuenioSchema(Schema):
    id_duenio = fields.Integer(dump_only=True)
    nombre = fields.String()
    apellido = fields.String() 
 

class EstablecimientoSchema(Schema):
    id_establecimiento = fields.Integer(dump_only=True)
    rut = fields.String()
    altitud = fields.Float()
    longitud = fields.Float()


class CanchaSchema(Schema):
    id_cancha = fields.Integer(dump_only=True)
    tamanio = fields.Integer()
    grama = fields.String()
    establecimiento =  fields.Nested(EstablecimientoSchema)

class HorarioSchema(Schema):
    id_horario = fields.Integer(dump_only=True)
    dia = fields.String()
    hora_inicio = fields.Integer()
    hora_fin = fields.Integer()


class HorarioEstablecimientoSchema(Schema):
    horario = fields.Nested(HorarioSchema)
    establecimiento = fields.Nested(EstablecimientoSchema)


class DuenioEstablecimientoSchema(Schema):
    establecimiento = fields.Nested(EstablecimientoSchema)
    duenio = fields.Nested(DuenioSchema)


class ReporteSchema(Schema):
    id_reporte = fields.Integer(dump_only=True)
    establecimiento = fields.Nested(EstablecimientoSchema)
    horas_alquiladas = fields.Integer()
    dinero_generado = fields.Integer()


class ReseniaSchema(Schema):
    id_resenia = fields.Integer(dump_only=True)
    autor = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])
    establecimiento = fields.Nested(EstablecimientoSchema)
    comentario = fields.String()
    calificacion = fields.Integer()


class EquipoSchema(Schema):
    id_equipo = fields.Integer(dump_only=True)
    capitan = fields.Nested(UsuarioSchema(only=('id_usuario','nombre','correo')))
    nombre = fields.String()


class SubequipoSchema(Schema):
    id_subequipo = fields.Integer(dump_only=True)
    equipo = fields.Nested(EquipoSchema)
    nombre = fields.String()


class PartidoSchema(Schema):
    id_partido = fields.Integer(dump_only=True)
    equipo = fields.Nested(EquipoSchema)
    subequipoa = fields.Nested(SubequipoSchema)
    subequipob = fields.Nested(SubequipoSchema)
    goles_a = fields.Integer()
    goles_b = fields.Integer()


class ReservaSchema(Schema):
    id_reserva = fields.Integer(dump_only=True)
    cancha = fields.Nested(CanchaSchema)
    partido = fields.Nested(PartidoSchema(only=("equipo","goles_a","goles_b")))
    reservante = fields.Nested(ReservanteSchema)
    hora_inicio = fields.DateTime()
    hora_fin = fields.DateTime()


class PlantillaSchema(Schema):
    equipo = fields.Nested(EquipoSchema)
    jugador = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])


class NotificacionEstadisticaSchema(Schema):
    id_noti_stats = fields.Integer(dump_only=True)
    partido = fields.Nested(PartidoSchema(only=(["equipo"])))
    capitan = fields.Nested(UsuarioSchema,  exclude=["'es_capitan", "es_jugador", "es_aficionado"])


class NotificacionReservaSchema(Schema):
    id_noti_reserva = fields.Integer(dump_only=True)
    partido = fields.Nested(PartidoSchema(only=("equipo","goles_a","goles_b")))
    invitado = fields.Nested(UsuarioSchema, exclude=["'es_capitan", "es_jugador", "es_aficionado"])
    reserva = fields.Nested(ReservaSchema(only=("cancha", "reservante","hora_inicio","hora_fin")))
    es_aceptada = fields.Boolean()


class AdminSchema(Schema):
    id_admin = fields.Integer(dump_only=True)
    correo = fields.String()


class SolicitudSchema(Schema):
    id_solicitud = fields.Integer(dump_only=True, data_key="id")
    admin = fields.Nested(AdminSchema)
    tipo_doc_duenio = fields.String(data_key="documentType")
    doc_duenio = fields.Integer(data_key="documentNumber")
    fecha_nacimiento = fields.DateTime(data_key="birthDate")
    nombre_duenio = fields.String(data_key="name")
    email_duenio = fields.String(data_key="email")
    tel_duenio = fields.Integer(data_key="phone")
    nombre_est = fields.String(data_key="businessName")
    num_canchas = fields.Integer()
    rut = fields.String()
    localidad = fields.String()
    direccion = fields.String(data_key="address")
    resultado = fields.Boolean()
    fecha_procesada = fields.DateTime()


