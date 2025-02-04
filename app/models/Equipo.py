from app import db

class Equipo(db.Model):
    # id_equipo = db.Column(db.Integer, primary_key=True)
    id_equipo = db.Column(
        db.Integer, 
        db.ForeignKey('reservante.id_reservante', name='fk_equipo_reservante'), 
        primary_key=True
    )
    nombre = db.Column(db.String(80), nullable=False)
    imagen = db.Column(db.String(), nullable=True)
    descripcion = db.Column(db.String(80), nullable=True)

    id_capitan = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='id_capitan'), 
        nullable=False
    )

    # plantillas = db.relationship('Plantilla', back_populates='equipo', cascade='all, delete-orphan')
    subequipos = db.relationship('Subequipo', back_populates='equipo', cascade='all, delete-orphan')
    # capitan = db.relationship('Usuario', back_populates='equipos')
    partido = db.relationship('Partido', back_populates='equipo', uselist=False, cascade='all, delete-orphan')
    participantes = db.relationship('Miembro_equipo', back_populates='equipo', cascade='all, delete-orphan')

    reservante = db.relationship(
        "Reservante",
        primaryjoin="and_(Equipo.id_equipo == foreign(Reservante.id_reservante), Reservante.tipo_reservante == 'equipo')",
        uselist=False
    )

    __mapper_args__ = {
        'polymorphic_identity': 'equipo',
    }