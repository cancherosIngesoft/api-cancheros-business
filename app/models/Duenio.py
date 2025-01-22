from app import db

class Duenio(db.Model):
    id_duenio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(80), nullable=False)

    establecimientos = db.relationship('Establecimiento', back_populates='duenio', cascade='all, delete-orphan')
