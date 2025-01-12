from app import db

class Resenia(db.Model):
    id_resenia = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.String(200), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)

    id_autor = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='id_usuario'), 
        nullable=False
    )

    id_establecimiento = db.Column(
        db.Integer, 
        db.ForeignKey('establecimiento.id_establecimiento', name='id_establecimiento'), 
        nullable=False
    )

    autor = db.relationship('Usuario', back_populates='resenias')
    establecimiento = db.relationship('Establecimiento', back_populates='resenias')