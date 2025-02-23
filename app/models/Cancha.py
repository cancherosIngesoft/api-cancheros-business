from app import db

class Cancha(db.Model):
    id_cancha = db.Column(db.Integer, primary_key=True)
    capacidad = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(80), nullable=False)
    precio = db.Column(db.Numeric, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    imagen1 = db.Column(db.String(80), nullable=True)
    imagen2 = db.Column(db.String(80), nullable=True)
    imagen3 = db.Column(db.String(80), nullable=True)
    imagen4 = db.Column(db.String(80), nullable=True)
    imagen5 = db.Column(db.String(80), nullable=True)
    
    id_establecimiento = db.Column(
        db.Integer, 
        db.ForeignKey('establecimiento.id_establecimiento', name='id_establecimiento'), 
        nullable=False
    )


    establecimiento = db.relationship('Establecimiento', back_populates='canchas')
    reservas = db.relationship('Reserva', back_populates='cancha', cascade='all, delete-orphan')
