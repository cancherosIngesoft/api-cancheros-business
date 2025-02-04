from app import db

class Partido(db.Model):
    id_partido = db.Column(db.Integer, primary_key=True)
    goles_A = db.Column(db.Integer, nullable=True)
    goles_B = db.Column(db.Integer, nullable=True)

    id_equipo = db.Column(
        db.Integer, 
        db.ForeignKey('equipo.id_equipo', name='id_equipo'), 
        nullable=False
    )

    id_subequipoA = db.Column(
        db.Integer, 
        db.ForeignKey('subequipo.id_subequipo', name='id_subequipoA'), 
        nullable=False
        )
    id_subequipoB = db.Column(
        db.Integer, 
        db.ForeignKey('subequipo.id_subequipo', name='id_subequipoB'), 
        nullable=False
    )

    subequipoA = db.relationship('Subequipo', foreign_keys=[id_subequipoA], back_populates='partido_a')
    subequipoB = db.relationship('Subequipo', foreign_keys=[id_subequipoB], back_populates='partido_b')
    equipo = db.relationship('Equipo', back_populates='partidos')
    reserva = db.relationship('Reserva', back_populates='partido', uselist=False, cascade='all, delete-orphan')
    notificaciones_reserva = db.relationship('Notificacion_reserva', back_populates='partido', cascade='all, delete-orphan')
    notificaciones_estadistica = db.relationship('Notificacion_estadistica', back_populates='partido', cascade='all, delete-orphan')


