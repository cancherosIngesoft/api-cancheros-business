from app import db

class Duenio(db.Model):
    id_duenio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(80), nullable=False)
    #tipo_doc = db.Column(db.String(80))
    #documento = db.Column(db.Integer, nullable=True  )
    #telefono = tipo_doc = db.Column(db.String(80), nullable=True )
    #fecha_nacimiento = db.Column(db.DateTime, nullable=True)

    establecimiento = db.relationship('Establecimiento', back_populates='duenio', cascade='all, delete-orphan')
