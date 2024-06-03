
import streamlit as st
import requests
from PIL import Image
import uuid
from utils import *

st.title('Animador de Imagens SpeckEAD 🐸')
st.caption('Desenvolvido por Emídio Souza para :orange[Kukac]')

if not check_password():
    st.stop()

# Inicializa a aplicação Streamlit
col1, col2 = st.columns(2)

with col2:
    immersity_parameters()
    st.write("Valores atuais:", st.session_state['current_state'])

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
                    uploaded_file, 
                    uploaded_file.name, 
                    uploaded_file.type
                )
                # Obter o token de acesso LeiaPix
                access_token = get_access_token()

                if access_token:
                        # Gera URLs pré-assinadas para disparidade e animação
                        correlation_id_disparity = str(uuid.uuid4())
                        disparity_blob_name = f"disparity_{correlation_id_disparity}.jpg"
                        put_disparity_presigned_url = create_presigned_url_put(disparity_blob_name)

                        print(f"Google Disparity URL: {put_disparity_presigned_url}")

                        # Faz a chamada para a API da LeiaPix para disparidade
                        disparity_response = requests.post(
                            "https://api.immersity.ai/api/v1/disparity",
                            headers={
                                "accept": "application/json",
                                "content-type": "application/json",
                                "Authorization": f"Bearer {access_token}"
                                },  # Acquired in previous step
                            json={
                                "correlationId": correlation_id_disparity,
                                "inputImageUrl": image_url,  # Link to the image you want to get disparity for
                                "resultPresignedUrl": put_disparity_presigned_url,  # Presigned URL with HTTP PUT permission.
                            },
                            timeout=5*60,  # expires in 5 min
                        )

                        print(disparity_response.status_code, disparity_response.text)

                        if disparity_response.status_code == 201:
                            # Prepara os dados para enviar à API de animação
                            correlation_id_animation = str(uuid.uuid4())
                            animation_blob_name = f"disparity_{correlation_id_animation}.mp4"
                            # Aqui, você precisa adicionar a lógica para gerar a URL pré-assinada para animação

                            put_disparity_presigned_url = create_presigned_url_get(disparity_blob_name)
                            put_animation_presigned_url = create_presigned_url_put(animation_blob_name)
                            
                            # Faz a chamada para a API da LeiaPix para animação
                            animation_response = requests.post(
                                "https://api.immersity.ai/api/v1/animation",
                                headers={"Authorization": f"Bearer {access_token}"},
                                json={
                                    "correlationId": correlation_id_animation,
                                    "inputImageUrl": image_url,
                                    "inputDisparityUrl": put_disparity_presigned_url,  # URL pré-assinada da disparidade
                                    "resultPresignedUrl": put_animation_presigned_url,
                                    "convergence": st.session_state['current_state']['convergence'],  # Aqui estava o erro, deve ser dois pontos ':' e não igual '='
                                    "animationLength": st.session_state['current_state']['animationLength'],
                                    "phaseX": st.session_state['current_state']['phaseX'],
                                    "phaseY": st.session_state['current_state']['phaseY'],
                                    "phaseZ": st.session_state['current_state']['phaseZ'],
                                    "amplitudeX": st.session_state['current_state']['amplitudeX'],
                                    "amplitudeY": st.session_state['current_state']['amplitudeY'],
                                    "amplitudeZ": st.session_state['current_state']['amplitudeZ']
                                },
                                timeout=5 * 60,  # expira em 5 min
                            )
                            print(animation_response.status_code, animation_response.text)

                            
                            if animation_response.status_code == 201:
                                st.success('Imagem animada com sucesso!')
                                put_animation_presigned_url = create_presigned_url_get(animation_blob_name)
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

