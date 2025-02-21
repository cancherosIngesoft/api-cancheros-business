from marshmallow import fields, Schema
from marshmallow import Schema, fields

from app.schemas.Canchas_sch import CanchaSchema
from app.schemas.Solicitud_sch import CoordinatesSchema

class EstablecimientoSchema(Schema):
    id_establecimiento = fields.Integer(dump_only=True)
    id_duenio = fields.Integer()
    nombre = fields.String()
    localidad = fields.String()
    RUT = fields.String()
    altitud = fields.Float()
    longitud = fields.Float()
    direccion = fields.String()
    telefono = fields.String() 

class BusinessInfoSchema(Schema):
    id_establecimiento = fields.Integer(dump_only=True, data_key="id")
    nombre = fields.String(data_key="name")
    geoReference =  fields.Method("get_georeference")
    promedio_calificacion = fields.String(data_key="calification")
    priceRange = fields.Method("get_price_range")
    canchas = fields.Nested(CanchaSchema, many=True)

    def get_price_range(self, obj):
        return [obj.min_price, obj.max_price]
    
    def get_georeference(self, obj):
        return {
            "lat": obj.altitud,
            "lon": obj.longitud
        }

class BusinessReservaInfo(Schema):
    direccion  = fields.String(data_key='businessDirection')
    nombre  = fields.String(data_key='businessName') 
    altitud = fields.Float(data_key='lat', required = False)
    longitud = fields.Float(data_key='long', required = False)