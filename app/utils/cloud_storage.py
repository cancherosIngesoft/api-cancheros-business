import io
import os
from google.cloud import storage
from flask import current_app, jsonify

BUCKET_NAME = "cancheros_bucket"
FOLDER_NAME = "rut"
FOLDER_IMG = "canchas"
FOLDER_CLUB = "clubes"
MAX_IMG_SIZE = 2 * 1024 * 1024  # Tamaño máximo en bytes (2 MB)

credentials_path = os.path.abspath("storage-credentials.json")
def upload_image(file):
    gcs_client = storage.Client()
    storage_bucket = gcs_client.get_bucket(BUCKET_NAME)
    blob = storage_bucket.blob(file.filename)

    content_type = file.content_type 

def upload_to_gcs(file_data, file_name):
    ENV = current_app.config["ENVIRONMENT"]
    
    client = None
    if(ENV == "LOCAL"):
        client = storage.Client.from_service_account_json(credentials_path)
    else:
        client = storage.Client()
    CHUNK_SIZE = 1024 * 1024 * 30

    object_name = f"{FOLDER_NAME}/{file_name}"
    bucket = client.get_bucket(BUCKET_NAME)

    # blob = bucket.blob(object_name, chunk_size=CHUNK_SIZE)
    # blob.upload_from_file(file_data, content_type='application/octet-stream')

    blob = bucket.blob(object_name)
    blob.upload_from_file(io.BytesIO(file_data), content_type='application/octet-stream')
    return blob.public_url

def gcs_upload_image(file_data, file_name):

    file_extension = file_name.split('.')[-1].lower()
    if file_extension not in ['jpg','png', 'jpeg']:
        return jsonify({"error": "extension de archivo no permitida"})

    # Verifica si el tamaño del archivo es válido
    if len(file_data) > MAX_IMG_SIZE:
        print("Entro tamaño")
        return jsonify({"error": "archivos muy pesados"})

    ENV = current_app.config["ENVIRONMENT"]   
    client = None
    if(ENV == "LOCAL"):
        client = storage.Client.from_service_account_json(credentials_path)
    else:
        client = storage.Client()
    
    object_name = f"{FOLDER_IMG}/{file_name}"
    bucket = client.get_bucket(BUCKET_NAME)
    blob =   bucket.blob(object_name)
    blob.upload_from_file(io.BytesIO(file_data), content_type='application/octet-stream')
    return blob.public_url


def gcs_upload_someIMG(file_data, file_name, folder_name):
    file_extension = file_name.split('.')[-1].lower()
    if file_extension not in ['jpg','png', 'jpeg']:
        return jsonify({"error": "extension de archivo no permitida"})

    # Verifica si el tamaño del archivo es válido
    if len(file_data) > MAX_IMG_SIZE:
        print("Entro tamaño")
        return jsonify({"error": "archivos muy pesados"})


    ENV = current_app.config["ENVIRONMENT"]   
    client = None
    if(ENV == "LOCAL"):
        client = storage.Client.from_service_account_json(credentials_path)
    else:
        client = storage.Client()
    
    object_name = f"{folder_name}/{file_name}"
    bucket = client.get_bucket(BUCKET_NAME)
    blob =   bucket.blob(object_name)
    blob.upload_from_file(io.BytesIO(file_data), content_type='application/octet-stream')
    return blob.public_url

def upload_file(chunk, file_name):
    if 'file_data' not in upload_file.__dict__:
        upload_file.file_data = io.BytesIO()
    upload_file.file_data.write(chunk)

    upload_file.file_data.seek(0)
    upload_to_gcs(upload_file.file_data,file_name)

