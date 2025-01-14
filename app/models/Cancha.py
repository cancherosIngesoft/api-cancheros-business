from app import db

class Cancha(db.Model):
    id_cancha = db.Column(db.Integer, primary_key=True)
    tamanio = db.Column(db.Integer, nullable=False)
    grama = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(80), nullable=False)
    precio = db.Column(db.Numeric, nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    
    id_establecimiento = db.Column(
        db.Integer, 
        db.ForeignKey('establecimiento.id_establecimiento', name='id_establecimiento'), 
        nullable=False
    )


    establecimiento = db.relationship('Establecimiento', back_populates='canchas')
    reservas = db.relationship('Reserva', back_populates='cancha', cascade='all, delete-orphan')
