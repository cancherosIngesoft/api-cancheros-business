import io
import os
from google.cloud import storage
from flask import current_app

BUCKET_NAME = "cancheros_bucket"
FOLDER_NAME = "rut"

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
        client = storage.Client().from_service_account_json(credentials_path)
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

def upload_file(chunk, file_name):
    if 'file_data' not in upload_file.__dict__:
        upload_file.file_data = io.BytesIO()
    upload_file.file_data.write(chunk)

    upload_file.file_data.seek(0)
    upload_to_gcs(upload_file.file_data,file_name)

