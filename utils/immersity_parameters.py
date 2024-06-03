import streamlit as st
import requests
# Credenciais Leia Pix
YOUR_CLIENT_ID = st.secrets["leia_pix"]["YOUR_CLIENT_ID"]
YOUR_CLIENT_SECRET = st.secrets["leia_pix"]["YOUR_CLIENT_SECRET"]


# Função para obter o token de acesso LeiaPix
def get_access_token():
    # URL para obter o token de acesso LeiaPix
    IMMERSITYAI_LOGIN_OPENID_TOKEN_URL = (
    "https://auth.immersity.ai/auth/realms/immersity/protocol/openid-connect/token"
    )
    token_response = requests.post(
      IMMERSITYAI_LOGIN_OPENID_TOKEN_URL,
      data={
        "client_id": YOUR_CLIENT_ID,
        "client_secret": YOUR_CLIENT_SECRET,
        "grant_type": "client_credentials",
      },
    ).json()
    return token_response.get("access_token")

def immersity_parameters():
    #Cria variáveis do LeiaPix
    presets = {
        "Horizontal": {"convergence" :0.0, "animationLength" : 6.0, "phaseX": 0.0, "phaseY": 0.0, "phaseZ": 0.0, "amplitudeX": 0.75, "amplitudeY": 0.0, "amplitudeZ": 0.0},
        "Wide Circle": {"convergence" :0.0, "animationLength" : 6.0,"phaseX": 0.75, "phaseY": 0.0, "phaseZ": 0.0, "amplitudeX": 1.0, "amplitudeY": 0.0, "amplitudeZ": 0.75},
        "Circle": {"convergence" :0.0, "animationLength" : 6.0,"phaseX": 1.0, "phaseY": 1.0, "phaseZ": 0.0, "amplitudeX": 0.50, "amplitudeY": 0.50, "amplitudeZ": 0.0},
        "Tall Circle": {"convergence" :0.0, "animationLength" : 6.0,"phaseX": 0.0, "phaseY": 0.75, "phaseZ": 0.50, "amplitudeX": 0.0, "amplitudeY": 0.50, "amplitudeZ": 0.50},
        "Vertical": {"convergence" :0.0, "animationLength" : 6.0,"phaseX": 0.0, "phaseY": 0.0, "phaseZ": 0.0, "amplitudeX": 0.0, "amplitudeY": 0.75, "amplitudeZ": 0.00},
        "Perspective": {"convergence" :0.0, "animationLength" : 6.0,"phaseX": 1.0, "phaseY": 0.25, "phaseZ": 1.0, "amplitudeX": 0.25, "amplitudeY": 0.25, "amplitudeZ": 0.50}
    }
    if 'selected_preset' not in st.session_state:   
        st.session_state['selected_preset'] = list(presets.keys())[0]
    if 'current_state' not in st.session_state:   
        st.session_state['current_state'] = presets[st.session_state['selected_preset']]

    

    # Função para definir os presets no estado da sessão
    def def_preset():
        st.session_state['current_state'] = presets[st.session_state['selected_preset']]
        for key, value in st.session_state['current_state'].items():
            st.session_state[key] = value

    # Interface para o usuário selecionar um preset
    st.selectbox(
        "Selecione uma pré-configuração:", 
        presets, 
        key='selected_preset', 
        on_change=def_preset
    )

    # Inicializar os sliders no estado da sessão, se necessário
    for key in ['convergence','animationLength','amplitudeX', 'amplitudeY', 'amplitudeZ', 'phaseX', 'phaseY', 'phaseZ']:
        if key not in st.session_state:
            st.session_state[key] = st.session_state['current_state'][key]
        else:
            st.session_state['current_state'][key] = st.session_state[key]

    # Sliders usando valores do st.session_state
    st.slider(
        'Convergence', 
        min_value=-1.0, 
        max_value=1.0, 
        value = st.session_state['current_state']['convergence'],
        step=0.01,
        key='convergence'
    )

    animationLength = st.slider(
        'Animation Duration', 
        min_value=0.0, 
        max_value=10.0, 
        value=st.session_state['current_state']["animationLength"], 
        step=1.0,
        key="animationLength"
    )

    amplitudeX = st.slider(
        'Amplitude X', 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state['current_state']["amplitudeX"], 
        step=0.01, 
        key="amplitudeX"
    )

    amplitudeY = st.slider(
        'Amplitude Y', 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state['current_state']["amplitudeY"], 
        step=0.01, 
        key="amplitudeY",
        args=("amplitudeY", st.session_state["amplitudeY"])
    )

    amplitudeZ = st.slider(
        'Amplitude Z', 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state['current_state']["amplitudeZ"], 
        step=0.01, 
        key="amplitudeZ",
        args=("amplitudeZ", st.session_state["amplitudeZ"])
    )

    phaseX = st.slider(
        'Phase X', 
        min_value=0.0, 
        max_value=0.75, 
        value=st.session_state['current_state']["phaseX"], 
        step=0.25, 
        key="phaseX",
        args=("phaseX", st.session_state["phaseX"])
    )

    phaseY = st.slider(
        'Phase Y', 
        min_value=0.0, 
        max_value=0.75, 
        value=st.session_state['current_state']["phaseY"], 
        step=0.25, 
        key="phaseY",
        args=("phaseY", st.session_state["phaseY"])
    )

    phaseZ = st.slider(
        'Phase Z', 
        min_value=0.0, 
        max_value=0.75, 
        value=st.session_state['current_state']["phaseZ"], 
        step=0.25, 
        key="phaseZ",
        args=("phaseZ", st.session_state["phaseZ"])
    )