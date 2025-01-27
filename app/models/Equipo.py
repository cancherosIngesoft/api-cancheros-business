from app import db

class Equipo(db.Model):
    id_equipo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)

    id_capitan = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='id_capitan'), 
        nullable=False
    )

    # plantillas = db.relationship('Plantilla', back_populates='equipo', cascade='all, delete-orphan')
    subequipos = db.relationship('Subequipo', back_populates='equipo', cascade='all, delete-orphan')
    capitan = db.relationship('Usuario', back_populates='equipos')
    partido = db.relationship('Partido', back_populates='equipo', uselist=False, cascade='all, delete-orphan')
    participantes = db.relationship('Participante', back_populates='equipo', cascade='all, delete-orphan')