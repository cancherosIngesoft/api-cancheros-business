from app import db

class Horario_establecimiento(db.Model):
    id_establecimiento = db.Column('id_establecimiento', db.Integer, db.ForeignKey('establecimiento.id_establecimiento'), primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horario.id_horario'), primary_key=True)

    # establecimiento= db.relationship('Establecimiento', back_populates='establecimientos')
    # horario = db.relationship('Horario', back_populates='canchas')