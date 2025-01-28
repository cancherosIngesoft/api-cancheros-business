from app import db

class Reserva(db.Model):
    id_reserva = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.String(80), nullable=False)
    hora_fin = db.Column(db.String(80), nullable=False)

    id_cancha = db.Column(
        db.Integer, 
        db.ForeignKey('cancha.id_cancha', name='id_cancha'), 
        nullable=False
    )

    id_partido = db.Column(
        db.Integer, 
        db.ForeignKey('partido.id_partido', name='id_partido'), 
        nullable=True
    )


    cancha = db.relationship('Cancha', back_populates='reservas')
    partido = db.relationship('Partido', back_populates='reserva')
    notificaciones_reserva = db.relationship('Notificacion_reserva', back_populates='reserva', cascade='all, delete-orphan')