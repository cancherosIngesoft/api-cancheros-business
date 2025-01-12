from app import db

class Admin(db.Model):
    _tablename_ = 'admin'
    id_admin = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(80), nullable=False)
    contrasenia = db.Column(db.String(80), nullable=False)
    
    solicitudes = db.relationship(
        'Solicitud', 
        back_populates='admin', 
        cascade='all, delete-orphan'
    )
