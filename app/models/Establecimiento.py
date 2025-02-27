from app import db

class Establecimiento(db.Model):
    id_establecimiento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=True)
    RUT = db.Column(db.String(), nullable=False)
    altitud = db.Column(db.String(80), nullable=False)
    longitud = db.Column(db.String(80), nullable=False)
    localidad = db.Column(db.String(80), nullable=False)
    direccion = db.Column(db.String(80), nullable=True)
    telefono = db.Column(db.String(15), nullable=True)

    id_duenio = db.Column(
        db.Integer, 
        db.ForeignKey('duenio.id_duenio', name='id_duenio'), 
        nullable=True
    )

    duenio = db.relationship('Duenio', back_populates='establecimiento')
    canchas = db.relationship('Cancha', back_populates='establecimiento', cascade='all, delete-orphan')
    resenias = db.relationship('Resenia', back_populates='establecimiento', cascade='all, delete-orphan')
    reportes = db.relationship('Reporte', back_populates='establecimiento', cascade='all, delete-orphan')