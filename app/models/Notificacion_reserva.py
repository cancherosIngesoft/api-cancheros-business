from app import db

class Notificacion_reserva(db.Model):
    id_noti_reserva = db.Column(db.Integer, primary_key=True)
    es_aceptada = db.Column(db.Boolean, nullable=False)

    id_invitado = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='invitado'), 
        nullable=False
    )

    id_partido = db.Column(
        db.Integer, 
        db.ForeignKey('partido.id_partido', name='partido'), 
        nullable=False
    )

    id_reserva = db.Column(
        db.Integer, 
        db.ForeignKey('reserva.id_reserva', name='reserva'), 
        nullable=False
    )

    invitado = db.relationship('Usuario', back_populates='notificaciones_reserva')
    partido = db.relationship('Partido', back_populates='notificaciones_reserva')
    reserva = db.relationship('Reserva', back_populates='notificaciones_reserva')