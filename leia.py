import os
import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import uuid
from google.cloud import storage
from google.oauth2 import service_account
import datetime
from dotenv import load_dotenv
import hmac

#Cria variáveis do LeiaPix
presets = {
    "Horizontal": {"phaseX": 1.0, "phaseY": 0.0, "phaseZ": 0.0, "amplitudeX": 0.0, "amplitudeY": 0.25, "amplitudeZ": 0.25},
    "Wide Circle": {"phaseX": 1.0, "phaseY": 0.5, "phaseZ": 0.0, "amplitudeX": 0.0, "amplitudeY": 0.25, "amplitudeZ": 0.25},
    "Circle": {"phaseX": 1.0, "phaseY": 1.0, "phaseZ": 0.0, "amplitudeX": 0.25, "amplitudeY": 0.25, "amplitudeZ": 0.0},
    "Tall Circle": {"phaseX": 0.5, "phaseY": 1.0, "phaseZ": 0.0, "amplitudeX": 0.0, "amplitudeY": 0.25, "amplitudeZ": 0.25},
    "Vertical": {"phaseX": 0.0, "phaseY": 1.0, "phaseZ": 0.0, "amplitudeX": 0.0, "amplitudeY": 0.25, "amplitudeZ": 0.25,},
    "Perspective": {"phaseX": 1.0, "phaseY": 0.25, "phaseZ": 1.0, "amplitudeX": 0.0, "amplitudeY": 0.25, "amplitudeZ": 0.25}
}

# Credenciais Leia Pix
YOUR_CLIENT_ID = st.secrets["leia_pix"]["YOUR_CLIENT_ID"]
YOUR_CLIENT_SECRET = st.secrets["leia_pix"]["YOUR_CLIENT_SECRET"]

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
bucket_name = st.secrets["google_cloud"]['GOOGLE_CLOUD_BUCKET_NAME']

# URL para obter o token de acesso LeiaPix
IMMERSITYAI_LOGIN_OPENID_TOKEN_URL = (
  "https://auth.immersity.ai/auth/realms/immersity/protocol/openid-connect/token"
)

# Função para obter o token de acesso LeiaPix
def get_access_token():
    token_response = requests.post(
      IMMERSITYAI_LOGIN_OPENID_TOKEN_URL,
      data={
        "client_id": YOUR_CLIENT_ID,
        "client_secret": YOUR_CLIENT_SECRET,
        "grant_type": "client_credentials",
      },
    ).json()
    st.write(token_response)
    return token_response.get("access_token")

# Função para criar uma URL pré-assinada do Google Cloud Storage
def create_presigned_url_put(bucket_name, blob_name, expiration=datetime.timedelta(minutes=60)):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration, method='PUT')
    return url

def create_presigned_url_get(bucket_name, blob_name, expiration=datetime.timedelta(minutes=60)):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    url = blob.generate_signed_url(expiration=expiration, method='GET')
    return url

# Função para Fazer Upload da Imagem para o Google Cloud Storage
def upload_image_to_gcs(bucket_name, file_stream, file_name, content_type):
    """Faz o upload de uma imagem para o Google Cloud Storage e retorna a URL."""
    client = storage.Client(credentials=credentials)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    file_stream.seek(0)
    blob.upload_from_string(file_stream.read(), content_type=content_type)

    return blob.public_url

st.title('Animador de Imagens SpeckEAD 🐸')
st.caption('Desenvolvido por Emídio Souza para :orange[Kukac]')


#Começa com a checagem de usuário e senha
def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.form_submit_button("Começar a animar! 🎬", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 Usuário ou senha não encontrados!")
    return False


if not check_password():
    st.stop()

# Inicializa a seleção de presets no Streamlit
if 'selected_preset' not in st.session_state:
    st.session_state['selected_preset'] = list(presets.keys())[0]  # Define um valor padrão
if 'preset_values' not in st.session_state:
    st.session_state['preset_values'] = presets[list(presets.keys())[0]]

# Inicializa a aplicação Streamlit
col1, col2 = st.columns(2)

with col2:   
    # Interface para o usuário selecionar um desses presets como mencionado anteriormente.
    selected_preset = st.selectbox("Selecione uma pré-configuração:", list(presets.keys()))

    if st.session_state['preset_values'] != presets[selected_preset]:
        st.session_state['preset_values'] = presets[selected_preset]
    
    # Sliders usando valores do st.session_state
    convergence = st.slider('Convergence', min_value=-1.0, max_value=1.0, value=0.0, step=0.01)
    animationLength = st.slider('Animation Duration', min_value=0, max_value=6, value=6, step=1)
    amplitudeX = st.slider('Amplitude X', min_value=0.0, max_value=1.0, value=st.session_state['preset_values']["amplitudeX"], step=0.01)
    amplitudeY = st.slider('Amplitude Y', min_value=0.0, max_value=1.0, value=st.session_state['preset_values']["amplitudeY"], step=0.01)
    amplitudeZ = st.slider('Amplitude Z', min_value=0.0, max_value=1.0, value=st.session_state['preset_values']["amplitudeZ"], step=0.01)
    phaseX = st.slider('Phase X', min_value=0.0, max_value=0.75, value=st.session_state['preset_values']["phaseX"], step=0.25)
    phaseY = st.slider('Phase Y', min_value=0.0, max_value=0.75, value=st.session_state['preset_values']["phaseY"], step=0.25)
    phaseZ = st.slider('Phase Z', min_value=0.0, max_value=0.75, value=st.session_state['preset_values']["phaseZ"], step=0.25)

with col1:
    # Upload de arquivo
    uploaded_file = st.file_uploader("Escolha uma imagem para animar", type=["jpg", "png"])

    # Exibe a imagem carregada
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagem Original', use_column_width=True)

    if st.button("Animar Vídeo!🎬"):
        
        if uploaded_file is not None:
            with st.spinner('Wait for it...'):
                # Faz o upload da imagem para o Google Cloud Storage
                image_url = upload_image_to_gcs(
                    bucket_name, 
                    uploaded_file, 
                    uploaded_file.name, 
                    uploaded_file.type
                )
                # Obter o token de acesso LeiaPix
                access_token = get_access_token()
                st.write(access_token)
                

                if access_token:
                        # Gera URLs pré-assinadas para disparidade e animação
                        correlation_id_disparity = str(uuid.uuid4())
                        disparity_blob_name = f"disparity_{correlation_id_disparity}.jpg"
                        put_disparity_presigned_url = create_presigned_url_put(bucket_name, disparity_blob_name)


                    
                        # Faz a chamada para a API da LeiaPix para disparidade
                        disparity_response = requests.post(
                            "https://api.immersity.ai/api/v1/disparity",
                            headers={"Authorization": f"Bearer {access_token}"},
                            json={
                                "correlationId": correlation_id_disparity,
                                "inputImageUrl": image_url,  # Link para a imagem que você deseja obter disparidade
                                "resultPresignedUrl": put_disparity_presigned_url,
                            },
                            timeout=5 * 60,  # expira em 5 min
                        )

                        print(disparity_response.status_code, disparity_response.text)

                        if disparity_response.status_code == 201:
                            # Prepara os dados para enviar à API de animação
                            correlation_id_animation = str(uuid.uuid4())
                            animation_blob_name = f"disparity_{correlation_id_animation}.mp4"
                            # Aqui, você precisa adicionar a lógica para gerar a URL pré-assinada para animação

                            put_disparity_presigned_url = create_presigned_url_get(bucket_name, disparity_blob_name)
                            put_animation_presigned_url = create_presigned_url_put(bucket_name, animation_blob_name)


                            print(put_animation_presigned_url)

                            


                            # Faz a chamada para a API da LeiaPix para animação
                            animation_response = requests.post(
                                "https://api.immersity.ai/api/v1/animation",
                                headers={"Authorization": f"Bearer {access_token}"},
                                json={
                                    "correlationId": correlation_id_animation,
                                    "inputImageUrl": image_url,
                                    "inputDisparityUrl": put_disparity_presigned_url,  # URL pré-assinada da disparidade
                                    "resultPresignedUrl": put_animation_presigned_url,
                                    "convergence": convergence,  # Aqui estava o erro, deve ser dois pontos ':' e não igual '='
                                    "animationLength": animationLength,
                                    "phaseX": phaseX,
                                    "phaseY": phaseY,
                                    "phaseZ": phaseZ,
                                    "amplitudeX": amplitudeX,
                                    "amplitudeY": amplitudeY,
                                    "amplitudeZ": amplitudeZ
                                },
                                timeout=5 * 60,  # expira em 5 min
                            )
                            print(animation_response.status_code, animation_response.text)

                            
                            if animation_response.status_code == 201:
                                st.success('Imagem animada com sucesso!')
                                
                                # Aqui, você precisa adicionar a lógica para baixar e exibir a imagem animada a partir da URL pré-assinada
                                put_animation_presigned_url = create_presigned_url_get(bucket_name, animation_blob_name)
                                st.video(put_animation_presigned_url, format="video/mp4", start_time=0)
                            
                            else:
                                st.error("Erro ao animar a imagem")
                        else:
                            if disparity_response.status_code == 402:
                                st.error("Putz! 🙈 Nossos créditos acabaram!")
                            else:
                                st.error(f"{disparity_response.status_code}")
                else:
                    st.error("Erro ao obter o token de acesso")

