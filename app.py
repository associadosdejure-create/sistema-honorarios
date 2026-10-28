import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

hashed_passwords = stauth.Hasher.hash_list(['mudar123', 'mudar123', 'bacharel123', 'advogado123', 'estagiario123'])

credentials = {
    "usernames": {
        "nelson": {"name": "Nelson Freire Machado", "password": hashed_passwords[0], "role": "admin"},
        "leonidas": {"name": "Leônidas da Paz e Silva", "password": hashed_passwords[1], "role": "admin"},
        "bacharel": {"name": "Bacharel(a)", "password": hashed_passwords[2], "role": "bacharel"},
        "advogado": {"name": "Advogado(a)", "password": hashed_passwords[3], "role": "advogado"},
        "estagiario": {"name": "Estagiário(a)", "password": hashed_passwords[4], "role": "estagiario"}
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='sistema_honorarios_cookie',
    cookie_key='chave_seguranca_sistema_123',
    cookie_expiry_days=30
)

authenticator.login(location='main', fields={'Form name': 'DEJURE ADVOCACIA'})

authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    if st.session_state.get('sessao_expirada'):
        st.warning('⏱️ Sua sessão expirou por inatividade (10 minutos). Por favor, faça login novamente.')
    else:
        st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    
    # ---------------------------------------------------------
    # CONTROLE DE INATIVIDADE (10 MINUTOS)
    # ---------------------------------------------------------
    agora = time.time()
    if 'ultima_atividade' in st.session_state:
        if agora - st.session_state['ultima_atividade'] > 600:
            st.session_state['logout'] = True
            st.session_state['authentication_status'] = None
            st.session_state['sessao_expirada'] = True
            del st.session_state['ultima_atividade']
            st.rerun()
            
    st.session_state['sessao_expirada'] = False
    st.session_state['ultima_atividade'] = agora

    user_role = credentials["usernames"].get(username, {}).get("role", "estagiario")
    
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)
    except Exception as e:
        st.error("⚠️ ERRO CRÍTICO: As chaves do Supabase não foram configuradas nos Secrets do Streamlit Cloud.")
        st.stop()

    # Barra lateral apenas para o Perfil e botão de Sair
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
        except Exception:
            st.write("⚖️ **Dejure Advocacia**")

    st.title(f"Seja bem-vindo, {name}! ⚖️")
    
    # ---------------------------------------------------------
    # MENUS MOVIDOS PARA O CENTRO DA TELA (NUNCA VÃO SUMIR)
    # ---------------------------------------------------------
    st.markdown("### 📌 Painel de Navegação")
    col1, col2 = st.columns(2)
    
    with col1:
        menu_principal = st.selectbox(
            "1️⃣ Selecione o Módulo Principal:", 
            ["Pagamentos", "Perícias", "Expedientes", "Pendências"]
        )
        
    with col2:
        if menu_principal == "Pagamentos":
            submenu = st.selectbox("2️⃣ Selecione a Ação:", ["Cadastrar Cliente", "Ver Parcelas", "Baixar Parcela", "Excluir Contrato"])
        elif menu_principal == "Perícias":
            submenu = st.selectbox("2️⃣ Selecione a
