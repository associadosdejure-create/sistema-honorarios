import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Controle de Honorários", layout="wide", page_icon="⚖️")

# --- CREDENCIAIS E PERFIS DE ACESSO ---
hashed_passwords = stauth.Hasher.hash_list(['mudar123', 'mudar123', 'bacharel123', 'advogado123', 'estagiario123'])

credentials = {
    "usernames": {
        "nelson": {
            "name": "Nelson Freire Machado",
            "password": hashed_passwords[0],
            "role": "admin"
        },
        "leonidas": {
            "name": "Leônidas da Paz e Silva",
            "password": hashed_passwords[1],
            "role": "admin"
        },
        "bacharel": {
            "name": "Bacharel(a)",
            "password": hashed_passwords[2],
            "role": "bacharel"
        },
        "advogado": {
            "name": "Advogado(a)",
            "password": hashed_passwords[3],
            "role": "advogado"
        },
        "estagiario": {
            "name": "Estagiário(a)",
            "password": hashed_passwords[4],
            "role": "estagiario"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='sistema_honorarios_cookie',
    cookie_key='chave_seguranca_sistema_123',
    cookie_expiry_days=30
)

# Renderiza o login alterando o título do formulário via dicionário 'fields'
authenticator.login(
    location='main', 
    fields={'Form name': 'DEJURE ADVOCACIA'}
)

authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

# --- CONTROLE DE FLUXO DA TELA ---
if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    
    user_role = credentials["usernames"][username]["role"]

    # --- CONEXÃO COM O SUPABASE ---
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # --- BARRA LATERAL (LOGO, LOGOUT E MENU) ---
    with st.sidebar:
        st.write(f"Logado como: **{name}**")
        
        if user_role == 'admin':
            perfil_txt = "👑 Sócio"
        elif user_role == 'advogado':
            perfil_txt = "⚖️ Advogado(a)"
        elif user_role == 'bacharel':
            perfil_txt = "📜 Bacharel(a)"
        else:
            perfil_txt = "🎓 Estagiário"
            
        st.caption(f"Perfil: {perfil_txt}")
        
        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.write("⚖️ **Dejure Advocacia**")
        
        st.markdown("---")
        menu = st.radio("Navegação", ["Cadastrar Honorário", "Ver Parcelas e Baixas"])

    # --- TELA PRINCIPAL ---
    st.title(f"Seja bem-vindo, {name}!")
    st.markdown("---")

    if menu == "Cadastrar Honorário":
        st.header("📝 Cadastrar Novo Pagamento Parcelado")
        
        with st.form("form_honorario"):
            cliente = st.text_input("Nome do Cliente")
            servico = st.text_input("Descrição do Serviço / Processo")
            valor_total = st.number
