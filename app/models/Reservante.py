from app import db
from app.models.Equipo import Equipo
from app.models.Usuario import Usuario

class Reservante(db.Model):
    id_reservante = db.Column(db.Integer, primary_key=True)
    tipo_reservante = db.Column(db.Enum('usuario', 'equipo', name='tipo_reservante'))


    reservas = db.relationship('Reserva', back_populates='reservante', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'reservante',
        'polymorphic_on': tipo_reservante
    }
