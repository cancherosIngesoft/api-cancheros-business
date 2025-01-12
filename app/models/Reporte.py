from app import db

class Reporte(db.Model):
    id_reporte = db.Column(db.Integer, primary_key=True)
    horas_alquiladas = db.Column(db.Integer, nullable=False)
    dinero_generado = db.Column(db.Integer, nullable=False)

    id_establecimito = db.Column(
        db.Integer, 
        db.ForeignKey('establecimiento.id_establecimiento', name='id_establecimiento'), 
        nullable=False
    )


    establecimiento = db.relationship('Establecimiento', back_populates='reportes')
