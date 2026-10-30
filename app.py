import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
import os
import bcrypt
import json
import base64

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0A0A0A !important; }
    [data-testid="stSidebar"], [data-testid="stExpander"], [data-testid="stForm"] {
        background-color: #121212 !important; border: 1px solid #222222 !important;
    }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p { color: #E0E0E0 !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .stButton > button[kind="primary"] {
        background-color: #D4AF37 !important; color: #0A0A0A !important; font-weight: bold; border: none;
    }
    .stButton > button[kind="primary"]:hover { background-color: #C5A028 !important; color: #000000 !important; }
    .stButton > button { background-color: #1F1F1F !important; color: #E0E0E0 !important; border: 1px solid #333333 !important; }
    .stButton > button:hover { background-color: #2D2D2D !important; color: #D4AF37 !important; border-color: #D4AF37 !important; }
    [data-testid="stMetricValue"] { color: #D4AF37 !important; }
    input, select, textarea { background-color: #1A1A1A !important; color: #FFFFFF !important; border-color: #333333 !important; }
    
    [data-testid="stDataFrame"] div[data-baseweb="table"] tr,
    [data-testid="stDataFrame"] table, 
    [data-testid="stTable"] {
        width: 100% !important;
    }
    [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td,
    [data-testid="stTable"] th, [data-testid="stTable"] td {
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
    </style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes nos Secrets.")
    st.stop()

def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def converter_imagem_base64(file) -> str:
    encoded = base64.b64encode(file.read()).decode()
    mime_type = file.type
    return f"data:{mime_type};base64,{encoded}"

def registrar_auditoria(usuario, acao, modulo, detalhes=""):
    try:
        supabase.table("logs_auditoria").insert({
            "usuario": usuario,
            "acao": acao,
            "modulo": modulo,
            "detalhes": detalhes
        }).execute()
    except Exception:
        pass

def limpar_flags_cadastro():
    for k in ['cad_cli_sucesso', 'cad_hon_sucesso', 'cad_per_sucesso', 'cad_exp_sucesso', 'cad_trf_sucesso', 'cad_pen_sucesso', 'cad_user_sucesso']:
        st.session_state[k] = False

def carregar_usuarios_db():
    senha_padrao_hash = gerar_hash('mudar123')
    cred_dict = {
        "usernames": {
            "master": {
                "name": "Administrador Master",
                "password": senha_padrao_hash,
                "role": "admin",
                "trocar_senha": False,
                "foto_url": None,
                "telefone": "",
                "oab": ""
            }
        }
    }
    
    try:
        res = supabase.table("usuarios_sistema").select("*").execute()
        if res.data:
            for u in res.data:
                uname = str(u.get("username", "")).strip().lower()
                if not uname: continue
                
                senha_db = str(u.get("senha_hash", u.get("password", ""))).strip()
                if senha_db and not senha_db.startswith("$2"):
                    senha_db = gerar_hash(senha_db)

                cred_dict["usernames"][uname] = {
                    "name": str(u.get("nome_completo", u.get("name", "Usuário"))),
                    "password": senha_db,
                    "role": str(u.get("role", "estagiario")),
                    "trocar_senha": u.get("trocar_senha", True) if "trocar_senha" in u else True,
                    "foto_url": u.get("foto_url", None),
                    "telefone": u.get("telefone", ""),
                    "oab": u.get("oab", ""),
                    "observacoes_pessoais": u.get("observacoes_pessoais", "")
                }
    except Exception:
        pass
        
    return cred_dict

credentials = carregar_usuarios_db()

authenticator = stauth.Authenticate(
    credentials, 
    cookie_name='sistema_dejure_cookie_v13', 
    cookie_key='chave_seguranca_dejure_2026_v13', 
    cookie_expiry_days=30
)

authentication_status = st.session_state.get('authentication_status')

if authentication_status != True:
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚖️ DEJURE ADVOCACIA</h1>", unsafe_allow_html=True)

try:
    authenticator.login(location='main')
except Exception:
    authenticator.login('main')

name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status == True and not st.session_state.get('login_registrado', False):
    registrar_auditoria(username, "Login", "Acesso", f"Usuário {name} ({username}) efetuou login no sistema.")
    st.session_state['login_registrado'] = True

if authentication_status == False:
    st.error('❌ Usuário ou senha incorretos.')
elif authentication_status == None:
    if st.session_state.get('sessao_expirada'):
        st.warning('⏱️ Sua sessão expirou (5 min inativa). Faça login novamente.')
elif authentication_status == True:
    agora = time.time()
    TEMPO_MAXIMO = 300
    if 'ultima_atividade' in st.session_state and agora - st.session_state['ultima_atividade'] > TEMPO_MAXIMO:
        registrar_auditoria(username, "Logout (Inatividade)", "Acesso", f"Sessão de {username} expirou por inatividade.")
        st.session_state.update({'authentication_status': None, 'sessao_expirada': True, 'login_registrado': False})
        del st.session_state['ultima_atividade']
        st.rerun()
        
    st.session_state['sessao_expirada'] = False
    st.session_state['ultima_atividade'] = agora
    t_rest = TEMPO_MAXIMO - (agora - st.session_state['ultima_atividade'])
    min_res, seg_res = max(0, int(t_rest // 60)), max(0, int(t_rest % 60))

    user_info = credentials["usernames"].get(username, {})
    user_role = user_info.get("role", "estagiario")
    
    precisa_trocar_senha = user_info.get("trocar_senha", False) if username != "master" else False

    if precisa_trocar_senha:
        st.markdown("<h2 style='text-align: center; color: #D4AF37;'>🔒 PRIMEIRO ACESSO DETECTADO</h2>", unsafe_allow_html=True)
        st.warning(f"Olá, **{name}**! Por razões de segurança do escritório, você deve cadastrar uma nova senha pessoal antes de acessar o sistema.")
        
        col_pa1, col_pa2, col_pa3 = st.columns([1, 2, 1])
        with col_pa2:
            with st.form("form_primeiro_acesso"):
                nova_s = st.text_input("Nova Senha Pessoal", type="password")
                conf_s = st.text_input("Confirme a Nova Senha", type="password")
                
                if st.form_submit_button("Atualizar Senha e Entrar", type="primary"):
                    if not nova_s or nova_s != conf_s:
                        st.error("As senhas não coincidem ou estão em branco.")
                    elif nova_s == "mudar123":
                        st.error("A nova senha não pode ser igual à senha padrão ('mudar123'). Escolha uma senha segura.")
                    else:
                        hash_novo = gerar_hash(nova_s)
                        try:
                            supabase.table("usuarios_sistema").update({
                                "senha_hash": hash_novo,
                                "password": hash_novo,
                                "trocar_senha": False
                            }).eq("username", username).execute()
                            
                            registrar_auditoria(username, "Troca de Senha Obrigatória", "Segurança", "Senha alterada com sucesso no primeiro acesso.")
                            st.cache_data.clear()
                            st.success("🎉 Senha alterada com sucesso! Liberando acesso ao sistema...")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar senha no banco: {e}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⬅️ Sair / Voltar para a Tela de Login", use_container_width=True):
                registrar_auditoria(username, "Logout (Primeiro Acesso)", "Acesso", f"Usuário {username} optou por sair na tela de primeiro acesso.")
                st.session_state.update({
                    'authentication_status': None,
                    'login_registrado': False,
                    'name': None,
                    'username': None
                })
                if 'ultima_atividade' in st.session_state:
                    del st.session_state['ultima_atividade']
                st.rerun()
        st.stop()
