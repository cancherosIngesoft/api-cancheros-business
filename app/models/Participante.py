from app import db

class Participante(db.Model):
    id_participante = db.Column(db.Integer, primary_key=True)
    id_equipo = db.Column(
        db.Integer, 
        db.ForeignKey('equipo.id_equipo', name='id_equipo'), 
        nullable=False
    )


    equipo = db.relationship('Equipo', back_populates='participantes') 
   


