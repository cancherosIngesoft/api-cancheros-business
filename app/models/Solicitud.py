from .. import db

class Solicitud(db.Model):

    id_solicitud = db.Column(db.Integer, primary_key=True)
    tipo_doc_duenio = db.Column(db.String(20), nullable=False)
    doc_duenio = db.Column(db.Integer, nullable=False)
    fecha_nacimiento = db.Column(db.DateTime, nullable=False)
    nombre_duenio = db.Column(db.String(80), nullable=False)
    email_duenio = db.Column(db.String(80), nullable=False)
    tel_duenio = db.Column(db.Integer, nullable=False)
    nombre_est = db.Column(db.String(80), nullable=False)
    num_canchas = db.Column(db.Integer, nullable=False)
    rut = db.Column(db.String(20), nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    direccion = db.Column(db.String(120), nullable=False)
    ya_procesada = db.Column(db.Boolean, nullable=False)
    fecha_procesada = db.Column(db.DateTime, nullable=True)
    resultado = db.Column(db.Boolean, nullable=True)


    id_admin = db.Column(
        db.Integer, 
        db.ForeignKey('admin.id_admin', name='id_admin'), 
        nullable=True
    )

    
    admin = db.relationship(
        'Admin', 
        back_populates='solicitudes',
    )
