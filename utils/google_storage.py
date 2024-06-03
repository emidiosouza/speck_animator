from google.cloud import storage
from google.oauth2 import service_account
import streamlit as st
import datetime

#Carregar credenciais do Google Cloud
credentials = service_account.Credentials.from_service_account_info({
    'type': 'service_account',
    'project_id': st.secrets["google_cloud"]["project_id"],
    'private_key': st.secrets["google_cloud"]["private_key"],
    'client_email': st.secrets["google_cloud"]["client_email"],
    'client_id': st.secrets["google_cloud"]["client_id"],
    'auth_uri': st.secrets["google_cloud"]["auth_uri"],
    'token_uri': st.secrets["google_cloud"]["token_uri"],
    'auth_provider_x509_cert_url': st.secrets["google_cloud"]["auth_provider_x509_cert_url"],
    'client_x509_cert_url': st.secrets["google_cloud"]["client_x509_cert_url"]
})

# Função para criar uma URL pré-assinada do Google Cloud Storage
def create_presigned_url_put(blob_name, expiration=datetime.timedelta(minutes=60)):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(st.secrets["google_cloud"]['GOOGLE_CLOUD_BUCKET_NAME'])
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration, method='PUT')
    return url

def create_presigned_url_get(blob_name, expiration=datetime.timedelta(minutes=60)):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(st.secrets["google_cloud"]['GOOGLE_CLOUD_BUCKET_NAME'])
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration, method='GET')
    return url

# Função para Fazer Upload da Imagem para o Google Cloud Storage
def upload_image_to_gcs(file_stream, file_name, content_type):
    """Faz o upload de uma imagem para o Google Cloud Storage e retorna a URL."""
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(st.secrets["google_cloud"]['GOOGLE_CLOUD_BUCKET_NAME'])
    blob = bucket.blob(file_name)
    file_stream.seek(0)
    blob.upload_from_string(file_stream.read(), content_type=content_type)

    return blob.public_url