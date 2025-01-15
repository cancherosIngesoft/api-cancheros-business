from flask import Flask, current_app
from flask_mail import Mail, Message 
from flask import render_template_string

mail = Mail(current_app)

def send_auth_mail(name,email,password):


    html_content = render_template_string(open('templates/mail_credentials.html').read(), 
                                          nombre=name,
                                          email=email,
                                          password=password)

    
    message = Message(subject='CANCHEROS - Solicitud aprobada',
                  sender=current_app.config["MAIL_USERNAME"],
                  recipients=[email])
    
    message.html = html_content

    try:
        mail.send(message)
        return "Correo enviado con éxito!"
    except Exception as e:
        print(e)
        return f"Error al enviar el correo: {e}"
    
def send_rejected_mail(email,name,reason):


    html_content = render_template_string(open('templates/mail_rejected.html').read(), 
                                          name=name,
                                          email=email,
                                          reason=reason)

    message = Message(subject='CANCHEROS - Solicitud rechazada',
                  sender=current_app.config["MAIL_USERNAME"],
                  recipients=[email])
    
    message.html = html_content

    try:
        mail.send(message)
        return "Correo enviado con éxito!"
    except Exception as e:
        print(e)
        return f"Error al enviar el correo: {e}"
