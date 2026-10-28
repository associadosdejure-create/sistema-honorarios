import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
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
    st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    user_role = credentials["usernames"][username]["role"]
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
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
        menu_principal = st.selectbox("Menu Principal", ["Pagamentos", "Perícias", "Expedientes", "Pendências"], key="menu_principal_selectbox")
        submenu = "" 
        if menu_principal == "Pagamentos":
            submenu = st.radio("Opções de Pagamentos", ["Cadastrar Cliente", "Ver Parcelas", "Baixar Parcela", "Excluir Contrato"], key="sub_pagamentos")
        elif menu_principal == "Perícias":
            submenu = st.radio("Opções de Perícias", ["Cadastrar Perícia", "Ver Perícias"], key="sub_pericias")
        elif menu_principal == "Expedientes":
            submenu = st.radio("Opções de Expedientes", ["Cadastrar Expediente", "Consultar Expedientes"], key="sub_expedientes")
        elif menu_principal == "Pendências":
            submenu = st.radio("Opções de Pendências", ["Cadastrar Pendência", "Consultar Pendências"], key="sub_pendencias")
    st.title(f"Seja bem-vindo, {name}!")
    st.markdown("---")
    try:
        res_alertas_p = supabase.table("pericias").select("*").eq("status", "Pendente").execute()
        res_alertas_e = supabase.table("expedientes").select("*").eq("status", "Pendente").execute()
        hoje = date.today()
        alertas_total = []
        if res_alertas_p.data:
            for p in res_alertas_p.data:
                if p.get('data_indicacao'):
                    dt = datetime.strptime(p['data_indicacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas_total.append((dias, f"🔬 **Perícia** | **Cliente:** {p['cliente']} | **Tipo:** {p['tipo_pericia']} | **Data:** {dt.strftime('%d/%m/%Y')}"))
        if res_alertas_e.data:
            for e in res_alertas_e.data:
                if e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas_total.append((dias, f"📂 **Expediente** | **Processo:** {e['numero_processo']} | **Cliente:** {e['cliente']} | **Prazo:** {dt.strftime('%d/%m/%Y')} | **Resp:** {e['responsavel']}"))
        if alertas_total:
            with st.expander("🚨 **CENTRAL DE ALERTAS DE PRAZOS**", expanded=True):
                for dias, texto in sorted(alertas_total, key=lambda x: x[0]):
                    if dias < 0:
                        st.error(f"⚠️ **VENCIDO ({abs(dias)} dias em atraso):** {texto}")
                    elif dias == 1:
                        st.error(f"🚨 **CRÍTICO (Falta 1 dia):** {texto}")
                    elif dias <= 3:
                        st.warning(f"⚠️ **URGENTE (Faltam {dias} dias):** {texto}")
                    elif dias <= 7:
                        st.info(f"📅 **LEMBRETE (Faltam {dias} dias):** {texto}")
            st.markdown("---")
    except Exception as e:
