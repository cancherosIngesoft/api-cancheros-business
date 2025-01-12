from app import db

class Reservante(db.Model):
    id_reservante = db.Column(db.Integer, primary_key=True)
    tipo_reservante = db.Column(db.String(80), nullable=False)