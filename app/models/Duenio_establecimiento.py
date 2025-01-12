from app import db

duenio_establecimiento = db.Table(
    'duenio_establecimiento',
    db.Column('id_establecimiento', db.Integer, db.ForeignKey('establecimiento.id_establecimiento'), primary_key=True),
    db.Column('id_duenio', db.Integer, db.ForeignKey('duenio.id_duenio'), primary_key=True)
)