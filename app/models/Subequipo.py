from app import db

class Subequipo(db.Model):
    id_subequipo = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    
    partido_a = db.relationship('Partido', foreign_keys='Partido.id_subequipoA', back_populates='subequipoA', uselist=False)
    partido_b = db.relationship('Partido', foreign_keys='Partido.id_subequipoB', back_populates='subequipoB', uselist=False)