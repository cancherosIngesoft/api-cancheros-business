from marshmallow import fields, Schema
from marshmallow import Schema, fields
from app.schemas.Admin_sch import AdminSchema

class LegalDocumentsSchema(Schema):
    name = fields.String(required=True)
    url = fields.String(required=True)

class CoordinatesSchema(Schema):
    lat = fields.String(data_key="latitud") 
    lng = fields.String(data_key="longitud") 


class PersonalInfoSchema(Schema):
    documentType = fields.String(data_key="tipo_doc_duenio")
    documentNumber = fields.String(data_key="doc_duenio")
    birthDate = fields.String(data_key="fecha_nacimiento")
    name = fields.String(data_key="nombre_duenio")
    lastName = fields.String(data_key="apellido_duenio")  
    email = fields.String(data_key="email_duenio")
    phone = fields.String(data_key="tel_duenio")


class BusinessInfoSchema(Schema):
    name = fields.String(data_key="nombre_est")
    courtCount = fields.Integer(data_key="num_canchas")
    courtTypes = fields.String(data_key="num_canchas")  # TODO: Esto no se guarda en la BD
    phone = fields.String(data_key="tel_est")  
    legalDocuments = fields.Nested(LegalDocumentsSchema, required=False)


class LocationInfoSchema(Schema):
    locality = fields.String(data_key="localidad")
    address = fields.String(data_key="direccion")
    coordinates = fields.Nested(CoordinatesSchema, required = False)
    

class SolicitudSchema(Schema):
    id_solicitud = fields.Integer(dump_only=True, data_key="id")
    personalInfo = fields.Nested(PersonalInfoSchema)
    businessInfo = fields.Nested(BusinessInfoSchema)
    locationInfo = fields.Nested(LocationInfoSchema)

class SolicitudBaseSchema(Schema):
    id_solicitud = fields.Integer(dump_only=True, data_key="id")
    admin = fields.Nested(AdminSchema)
    tipo_doc_duenio = fields.String()
    doc_duenio = fields.Integer()
    fecha_nacimiento = fields.DateTime()
    nombre_duenio = fields.String()
    email_duenio = fields.String()
    tel_duenio = fields.Integer()
    nombre_est = fields.String()
    num_canchas = fields.Integer()
    rut = fields.String()
    localidad = fields.String()
    direccion = fields.String()
    resultado = fields.Boolean()
    fecha_procesada = fields.DateTime()
    longitud = fields.String()
    apellido_duenio = fields.String()
    latitud = fields.String()
    tel_est = fields.String()

data = {
    "id": 1,
    "tipo_doc_duenio": "CC",
    "doc_duenio": "123456789",
    "fecha_nacimiento": "1990-01-01",
    "nombre_duenio": "Juan",
    "email_duenio": "juan@example.com",
    "tel_duenio": "555-1234",
    "nombre_est": "Mi Empresa",
    "num_canchas": 5,
    "RUT": "https://example.com/rut.pdf",
    "localidad": "Chapinero",
    "direccion": "Calle 123",
    "latitud": 4.65,
    "longitud": -74.05
}