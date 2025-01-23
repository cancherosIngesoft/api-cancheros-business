from marshmallow import fields, Schema
from marshmallow import Schema, fields

from app.schemas.Canchas_sch import CanchaSchema
from app.schemas.Solicitud_sch import CoordinatesSchema

class EstablecimientoSchema(Schema):
    id_establecimiento = fields.Integer(dump_only=True)
    rut = fields.String()
    altitud = fields.Float()
    longitud = fields.Float()


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
    