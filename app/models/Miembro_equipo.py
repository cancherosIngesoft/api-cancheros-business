from app import db

class Miembro_equipo(db.Model):
    id_miembro = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='id_usuario'), 
        nullable=False
    )
    id_equipo = db.Column(
        db.Integer, 
        db.ForeignKey('equipo.id_equipo', name='id_equipo'), 
        nullable=False
    )


    equipo = db.relationship('Equipo', back_populates='participantes')
    usuario = db.relationship('Usuario', back_populates='miembros')
    
   


