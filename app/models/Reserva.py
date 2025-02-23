from app import db

class Reserva(db.Model):
    id_reserva = db.Column(db.Integer, primary_key=True)
    hora_inicio = db.Column(db.DateTime, nullable=False)
    hora_fin = db.Column(db.DateTime, nullable=False)
    estado_procesado = db.Column(db.Boolean, nullable=False, default=False)
    id_referencia_pago = db.Column(db.String, nullable = True)

    id_host = db.Column(
        db.Integer, 
        db.ForeignKey('duenio.id_duenio', name='id_duenio'), 
        nullable=True
    )

    id_reservante = db.Column(
        db.Integer, 
        db.ForeignKey('reservante.id_reservante', name='id_reservante'), 
        nullable=True
    )

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
    host = db.relationship('Duenio', back_populates='reservas_host')
    partido = db.relationship('Partido', back_populates='reserva')
    notificaciones_reserva = db.relationship('Notificacion_reserva', back_populates='reserva', cascade='all, delete-orphan')
    reservante = db.relationship('Reservante', back_populates='reservas')