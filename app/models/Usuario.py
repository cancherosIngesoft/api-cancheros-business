from app import db

class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(80), nullable=False)
    es_capitan = db.Column(db.Boolean, nullable=False)
    es_jugador = db.Column(db.Boolean, nullable=False)
    es_aficionado = db.Column(db.Boolean, nullable=False)

    resenias = db.relationship('Resenia', back_populates='autor', cascade='all, delete-orphan')
    equipos = db.relationship('Equipo', back_populates='capitan', cascade='all, delete-orphan')
    notificaciones_reserva = db.relationship('Notificacion_reserva', back_populates='invitado', cascade='all, delete-orphan')
    notificaciones_estadistica = db.relationship('Notificacion_estadistica', back_populates='capitan', cascade='all, delete-orphan')