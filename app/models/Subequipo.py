from app import db

class Subequipo(db.Model):
    id_subequipo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)

    id_equipo = db.Column(
        db.Integer, 
        db.ForeignKey('equipo.id_equipo', name='id_equipo'), 
        nullable=False
    )


    equipo = db.relationship('Equipo', back_populates='subequipos')
    partido_a = db.relationship('Partido', foreign_keys='Partido.id_subequipoA', back_populates='subequipoA', uselist=False)
    partido_b = db.relationship('Partido', foreign_keys='Partido.id_subequipoB', back_populates='subequipoB', uselist=False)