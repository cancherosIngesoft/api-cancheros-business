from app import db
from sqlalchemy import Time

class Horario(db.Model):
    id_horario = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(Time, nullable=False)
    hora_fin = db.Column(Time, nullable=False)
    
