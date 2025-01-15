from .. import db

class Solicitud(db.Model):

    id_solicitud = db.Column(db.Integer, primary_key=True)
    tipo_doc_duenio = db.Column(db.String(20), nullable=False)
    doc_duenio = db.Column(db.Integer, nullable=False)
    fecha_nacimiento = db.Column(db.DateTime, nullable=False)
    nombre_duenio = db.Column(db.String(80), nullable=False)
    apellido_duenio = db.Column(db.String(80), nullable=False)
    email_duenio = db.Column(db.String(80), nullable=False)
    tel_duenio = db.Column(db.String, nullable=False)
    tel_est = db.Column(db.String, nullable=False)
    nombre_est = db.Column(db.String(80), nullable=False)
    num_canchas = db.Column(db.Integer, nullable=False)
    rut = db.Column(db.String(200), nullable=True)
    localidad = db.Column(db.String(80), nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    latitud= db.Column(db.String, nullable=False)
    longitud = db.Column(db.String, nullable=False)
    comentario_rechazo= db.Column(db.String(300), nullable=True)
    ya_procesada = db.Column(db.Boolean, nullable=False)
    fecha_procesada = db.Column(db.DateTime, nullable=True)
    resultado = db.Column(db.Boolean, nullable=True)


    def get_personal_info(self):
        return {
            "documentType": self.tipo_doc_duenio,
            "documentNumber": self.doc_duenio,
            "birthDate": self.fecha_nacimiento,
            "name": self.nombre_duenio + " " +  self.apellido_duenio,
            "lastName": self.nombre_duenio,  # Aún sin apellido en la BD
            "email": self.email_duenio,
            "phone": self.tel_duenio
        }

    def get_business_info(self):
        return {
            "name": self.nombre_est,
            "courtCount": self.num_canchas,
            "courtTypes": self.num_canchas,  # No guardado en la BD
            "phone": self.tel_duenio,  # No guardado en la BD
            "legalDocuments": {
                "name": "RUT",
                "url": self.rut
            }
        }

    def get_location_info(self):
        return {
            "locality": self.localidad,
            "address": self.direccion,
            "coordinates": {
                #"lat": self.altitud, # No se guarda en la BD
                #"lng": self.longitud # No se guarda em la BD
            }
        }

    id_admin = db.Column(
        db.Integer, 
        db.ForeignKey('admin.id_admin', name='id_admin'), 
        nullable=True
    )

    
    admin = db.relationship(
        'Admin', 
        back_populates='solicitudes',
    )
