from app import db

plantilla = db.Table(
    'plantilla',
    db.Column('id_subequipo', db.Integer, db.ForeignKey('subequipo.id_subequipo'), primary_key=True),
    db.Column('id_jugador', db.Integer, db.ForeignKey('usuario.id_usuario'), primary_key=True)
)