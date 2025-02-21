from app import db

class Duenio(db.Model):
    id_duenio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(80), nullable=False)
    tipo_doc = db.Column(db.String(80))
    documento = db.Column(db.Integer, nullable=True  )
    telefono = db.Column(db.String(80), nullable=True )
    fecha_nacimiento = db.Column(db.DateTime, nullable=True)
    commission_amount = db.Column(db.Numeric, nullable=True)

    establecimiento = db.relationship('Establecimiento', back_populates='duenio', cascade='all, delete-orphan')
    reservas_host = db.relationship('Reserva', back_populates='host', cascade='all, delete-orphan')
