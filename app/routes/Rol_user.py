from app.models.Usuario import Usuario 
from app.models.Admin import Admin 
from app.models.Duenio import Duenio
from app import db
from flask import request, Blueprint, jsonify
from app.schemas.Admin_sch import  AdminSchema
from app.schemas.Duenio_sch import  DuenioSchema
from app.schemas.Usuario_sch import UsuarioSchema


usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/rol_user', methods = ['GET', 'POST'])
def log_usr():
    try: 
        data = request.get_json()
        email = data.get('correo')
        
        schema = get_rol(email)
        if not schema:
            exit  = post_usr(data)
            return exit
            
        return  schema 
    except Exception as e:
        return jsonify({"error": str(e)}), 500



def post_usr(data):
    nuevo_usr = Usuario( nombre = data.get('nombre'), correo =  data.get('correo'), es_capitan = False,es_jugador = False, es_aficionado = True )
    db.session.add(nuevo_usr)
    db.session.commit()
    return jsonify({"message": "Usuario creado con exito"}), 200 


def get_rol(email):
    schema = None
    usuario = Usuario.query.filter_by(correo=email).first()

    if not usuario:           
        duenio = Duenio.query.filter_by(correo=email).first()

        if not duenio: 
            admin =  Admin.query.filter_by(correo=email).first()          
  
            if admin:
                schema = AdminSchema().dump({
                'id_admin':admin.id_admin,
                'correo': admin.correo
                })
                schema['rol'] = "admin"
                schema['id'] = schema.pop('id_admin')
               
        else: 
            schema = DuenioSchema().dump(
            {
                'id_duenio':duenio.id_duenio,
                'nombre': duenio.nombre
            })   
            schema['rol'] = "duenio"
            schema['id'] = schema.pop('id_duenio')
            
            
    else:
        schema = UsuarioSchema().dump( {
        'id_usuario' : usuario.id_usuario,
        'nombre': usuario.nombre,
        'correo': usuario.correo,
        'es_capitan' : usuario.es_capitan,
        'es_jugador' : usuario.es_jugador,
        'es_aficionado' : usuario.es_aficionado
        })
        schema['id'] = schema.pop('id_usuario')
    
    return schema