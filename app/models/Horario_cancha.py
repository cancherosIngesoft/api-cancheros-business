from app import db


class Horario_cancha(db.Model):
    id_cancha = db.Column(db.Integer, db.ForeignKey('cancha.id_cancha'), primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horario.id_horario'), primary_key=True)

    # cancha = db.relationship('Cancha', back_populates='horarios')
    # horario = db.relationship('Horario', back_populates='canchas')
