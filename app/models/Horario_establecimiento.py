from app import db

horario_establecimiento = db.Table(
    'horario_establecimiento',
    db.Column('id_horario', db.Integer, db.ForeignKey('horario.id_horario'), primary_key=True),
    db.Column('id_establecimiento', db.Integer, db.ForeignKey('establecimiento.id_establecimiento'), primary_key=True)
)