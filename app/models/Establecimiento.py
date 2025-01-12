from app import db

class Establecimiento(db.Model):
    id_establecimiento = db.Column(db.Integer, primary_key=True)
    RUT = db.Column(db.String(80), nullable=False)
    altitud = db.Column(db.String(80), nullable=False)
    longitud = db.Column(db.String(80), nullable=False)

    canchas = db.relationship('Cancha', back_populates='establecimiento', cascade='all, delete-orphan')
    resenias = db.relationship('Resenia', back_populates='establecimiento', cascade='all, delete-orphan')
    reportes = db.relationship('Reporte', back_populates='establecimiento', cascade='all, delete-orphan')