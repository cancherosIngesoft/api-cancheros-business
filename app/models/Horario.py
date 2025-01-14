from app import db

class Horario(db.Model):
    id_horario = db.Column(db.Integer, primary_key=True)
    dia = db.Column(db.String(20), nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    
