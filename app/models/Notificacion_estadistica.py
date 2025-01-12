from app import db

class Notificacion_estadistica(db.Model):
    id_noti_stats = db.Column(db.Integer, primary_key=True)

    id_capitan  = db.Column(
        db.Integer, 
        db.ForeignKey('usuario.id_usuario', name='capitan'), 
        nullable=False
    )

    id_partido  = db.Column(
        db.Integer, 
        db.ForeignKey('partido.id_partido', name='partido'), 
        nullable=False
    )

    capitan = db.relationship('Usuario', back_populates='notificaciones_estadistica') 
    partido = db.relationship('Partido', back_populates='notificaciones_estadistica')