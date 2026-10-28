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

# ==========================================
# CONTROLE DE INATIVIDADE (10 MINUTOS)
# ==========================================
if st.session_state.get('authentication_status') == True:
    if 'ultima_atividade' in st.session_state:
        # 600 segundos = 10 minutos
        if time.time() - st.session_state['ultima_atividade'] > 600:
            # Expira a sessão
            st.session_state['authentication_status'] = None
            st.session_state['logout'] = True
            st.session_state['sessao_expirada'] = True
            del st.session_state['ultima_atividade']
            
            # Tenta apagar o cookie armazenado no navegador
            if hasattr(authenticator, 'cookie_manager'):
                try:
                    authenticator.cookie_manager.delete(authenticator.cookie_name)
                except Exception:
                    pass
                    
            # Reinicia a página para forçar o login
            st.rerun()
            
    # Se não expirou, atualiza a última atividade para o momento do clique
    st.session_state['ultima_atividade'] = time.time()


authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    # Mostra mensagem personalizada caso a sessão tenha caído por inatividade
    if st.session_state.get('sessao_expirada'):
        st.error('⏱️ Sua sessão expirou devido a 10 minutos de inatividade. Por favor, faça login novamente.')
        st.session_state
