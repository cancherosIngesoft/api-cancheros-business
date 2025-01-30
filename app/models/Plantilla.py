from app import db

plantilla = db.Table(
    'plantilla',
    db.Column('id_subequipo', db.Integer, db.ForeignKey('subequipo.id_subequipo'), primary_key=True),
    db.Column('id_miembro', db.Integer, db.ForeignKey('miembro_equipo.id_miembro'), primary_key=True)
)