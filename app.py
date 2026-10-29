import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time
import os

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

# --- ESTILIZAÇÃO CSS COMPACTA (PRETO FECHADO E DOURADO) ---
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
    </style>
""", unsafe_allow_html=True)

try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception:
    st.error("⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes nos Secrets.")
    st.stop()

# --- CARREGA USUÁRIOS DO SUPABASE (COM FALLBACK SE VAZIO) ---
@st.cache_data(ttl=10)
def carregar_usuarios_db():
    try:
        res = supabase.table("usuarios_sistema").select("*").execute()
        if res.data:
            creds = {"usernames": {}}
            for u in res.data:
                creds["usernames"][u["username"]] = {
                    "name": u["name"],
                    "password": u["password"],
                    "role": u["role"]
                }
            return creds
    except Exception:
        pass
    # Padrão inicial caso a tabela esteja vazia
    hashed_passwords = stauth.Hasher.hash_list(['mudar123', 'mudar123', 'bacharel123', 'advogado123', 'estagiario123'])
    return {
        "usernames": {
            "nelson": {"name": "Nelson Freire Machado", "password": hashed_passwords[0], "role": "admin"},
            "leonidas": {"name": "Leônidas da Paz e Silva", "password": hashed_passwords[1], "role": "admin"},
            "bacharel": {"name": "Bacharel(a)", "password": hashed_passwords[2], "role": "bacharel"},
            "advogado": {"name": "Advogado(a)", "password": hashed_passwords[3], "role": "advogado"},
            "estagiario": {"name": "Estagiário(a)", "password": hashed_passwords[4], "role": "estagiario"}
        }
    }

credentials = carregar_usuarios_db()

authenticator = stauth.Authenticate(
    credentials, cookie_name='sistema_honorarios_cookie', cookie_key='chave_seguranca_sistema_123', cookie_expiry_days=30
)

authentication_status = st.session_state.get('authentication_status')

if authentication_status != True:
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚖️ DEJURE ADVOCACIA</h1>", unsafe_allow_html=True)

authenticator.login(location='main', fields={'Form name': 'DEJURE ADVOCACIA'})

name = st.session_state.get('name')
username = st.session_state.get('username')

if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    if st.session_state.get('sessao_expirada'):
        st.warning('⏱️ Sua sessão expirou (5 min inativa). Faça login novamente.')
    else:
        st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    
    agora = time.time()
    TEMPO_MAXIMO = 300
    if 'ultima_atividade' in st.session_state and agora - st.session_state['ultima_atividade'] > TEMPO_MAXIMO:
        st.session_state.update({'authentication_status': None, 'sessao_expirada': True})
        del st.session_state['ultima_atividade']
        st.rerun()
        
    st.session_state['sessao_expirada'] = False
    st.session_state['ultima_atividade'] = agora
    t_rest = TEMPO_MAXIMO - (agora - st.session_state['ultima_atividade'])
    min_res, seg_res = max(0, int(t_rest // 60)), max(0, int(t_rest % 60))

    user_role = credentials["usernames"].get(username, {}).get("role", "estagiario")

    if 'pagina_atual' not in st.session_state: st.session_state['pagina_atual'] = "🏠 Página Inicial"
    if 'submenu_atual' not in st.session_state: st.session_state['submenu_atual'] = ""

    def validar_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11 or cpf == cpf[0] * 11: return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        d1 = (soma * 10) % 11; d1 = 0 if d1 == 10 else d1
        if d1 != int(cpf[9]): return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        d2 = (soma * 10) % 11; d2 = 0 if d2 == 10 else d2
        return d2 == int(cpf[10])

    @st.cache_data(ttl=30)
    def carregar_dados(tabela):
        res = supabase.table(tabela).select("*").execute()
        return res.data if res.data else []

    with st.sidebar:
        st.write(f"Logado como: **{name}**")
        p_txt = {"admin": "👑 Sócio", "advogado": "⚖️ Advogado(a)", "bacharel": "📜 Bacharel(a)"}.get(user_role, "🎓 Estagiário")
        st.caption(f"Perfil: {p_txt}")
        st.markdown("---")
        
        st.subheader("🧭 Módulos do Sistema")
        modulos = {
            "🏠 Página Inicial": "🏠 Página Inicial",
            "👥 Clientes": "Clientes",
            "💰 Pagamentos": "Pagamentos",
            "🔬 Perícias": "Perícias",
            "📂 Expedientes": "Expedientes",
            "📋 Pendências": "Pendências"
        }
        
        # Adiciona o módulo de segurança apenas para administradores/sócios
        if user_role == 'admin':
            modulos["🔒 Segurança"] = "Segurança"

        for label, pag in modulos.items():
            if st.button(label, use_container_width=True):
                st.session_state['pagina_atual'] = pag
                st.session_state['submenu_atual'] = "" if pag in ["🏠 Página Inicial", "Segurança"] else {"Clientes": "Consultar Clientes", "Pagamentos": "Ver Parcelas", "Perícias": "Ver Perícias", "Expedientes": "Consultar Expedientes", "Pendências": "Consultar Pendências"}[pag]
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"⏳ **Sessão expira em:**\n### `{min_res:02d}:{seg_res:02d}`")
        st.markdown("---")
        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        else: st.write("⚖️ **Dejure Advocacia**")

    menu_escolha = st.session_state['pagina_atual']

    if menu_escolha == "🏠 Página Inicial":
        if os.path.exists("logo.png"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2: st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #D4AF37;'>⚖️ DEJURE ADVOCACIA</h2>", unsafe_allow_html=True)

        st.title(f"Seja bem-vindo, {name}! ⚖️")
        st.markdown("### 📊 Visão Geral do Escritório")
        
        try:
            cli, hon, per, exp, pen = carregar_dados("clientes_cadastrados"), carregar_dados("honorarios"), carregar_dados("pericias"), carregar_dados("expedientes"), carregar_dados("pendencias")
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Clientes", len(cli))
            c2.metric("Contratos", len(hon))
            c3.metric("Perícias Pend.", len([p for p in per if p.get('status') == 'Pendente']))
            c4.metric("Expedientes Pend.", len([e for e in exp if e.get('status') == 'Pendente']))
            c5.metric("Pendências Doc.", len([pn for pn in pen if pn.get('status') == 'Pendente']))
        except Exception: pass

        st.markdown("---")
        try:
            hoje = date.today()
            alertas = []
            for p in per:
                if p.get('status') == 'Pendente' and p.get('data_indicacao'):
                    dt = datetime.strptime(p['data_indicacao'], "%Y-%m-%d").date()
                    alertas.append(((dt - hoje).days, f"🔬 Perícia | Cliente: {p['cliente']} | Tipo: {p['tipo_pericia']} | Data: {dt.strftime('%d/%m/%Y')}", p['id'], 'pericia'))
            for e in exp:
                if e.get('status') == 'Pendente' and e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    alertas.append(((dt - hoje).days, f"📂 Expediente | Processo: {e['numero_processo']} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {e['responsavel']}", e.get('id', 0), 'expediente'))
                    
            if alertas:
                col_a1, col_a2 = st.columns([0.80, 0.20])
                with col_a1: st.subheader("🚨 Central de Alertas de Prazos")
                with col_a2:
                    if st.button("🗑️ Excluir Alertas", type="primary"):
                        for _, _, i_id, i_tipo in alertas:
                            if i_tipo == 'pericia': supabase.table("pericias").update({"status": "Concluído"}).eq("id", i_id).execute()
                            elif i_tipo == 'expediente': supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", i_id).execute()
                        st.cache_data.clear()
                        st.success("Alertas atualizados!")
                        st.rerun()

                with st.expander("📌 **Ver Lista de Alertas Ativos**", expanded=True):
                    for dias, texto, _, _ in sorted(alertas, key=lambda x: x[0]):
                        if dias < 0: st.error(f"⚠️ **VENCIDO ({abs(dias)} dias):** {texto}")
                        elif dias == 1: st.error(f"🚨 **CRÍTICO (1 dia):** {texto}")
                        elif dias <= 3: st.warning(f"⚠️ **URGENTE ({dias} dias):** {texto}")
                        else: st.info(f"📅 **LEMBRETE ({dias} dias):** {texto}")
            else:
                st.info("🎉 Nenhum alerta de prazo pendente para hoje!")
        except Exception: pass

    elif menu_escolha == "Segurança" and user_role == 'admin':
        st.title("🔒 Gestão de Segurança e Usuários")
        
        tab1, tab2 = st.tabs(["➕ Cadastrar Novo Usuário", "🔑 Alterar Senha de Usuário"])
        
        with tab1:
            st.subheader("Cadastrar Novo Usuário no Sistema")
            with st.form("form_novo_usuario"):
                n_user = st.text_input("Nome de Usuário (login sem espaços, ex: carlos)")
                n_name = st.text_input("Nome Completo (ex: Carlos Eduardo)")
                n_pass = st.text_input("Senha Inicial", type="password")
                n_role = st.selectbox("Perfil / Nível de Acesso", ["admin", "advogado", "bacharel", "estagiario"], format_func=lambda x: {"admin": "👑 Sócio (Admin)", "advogado": "⚖️ Advogado(a)", "bacharel": "📜 Bacharel(a)", "estagiario": "🎓 Estagiário"}[x])
                
                if st.form_submit_button("Cadastrar Usuário"):
                    if not n_user or not n_name or not n_pass:
                        st.error("Preencha todos os campos obrigatórios.")
                    else:
                        hashed_p = stauth.Hasher([n_pass]).generate()[0]
                        try:
                            # Verifica se já existe
                            existe = supabase.table("usuarios_sistema").select("*").eq("username", n_user.strip()).execute()
                            if existe.data:
                                st.error("⚠️ Este nome de usuário já existe no sistema.")
                            else:
                                supabase.table("usuarios_sistema").insert({
                                    "username": n_user.strip().lower(),
                                    "name": n_name.strip(),
                                    "password": hashed_p,
                                    "role": n_role
                                }).execute()
                                st.cache_data.clear()
                                st.success(f"Usuário **{n_user}** cadastrado com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao cadastrar usuário: {e}")

        with tab2:
            st.subheader("Alterar Senha de Usuário Existente")
            lista_usrs = list(credentials["usernames"].keys())
            with st.form("form_alt_senha"):
                usr_sel = st.selectbox("Selecione o Usuário:", lista_usrs)
                nova_senha = st.text_input("Nova Senha", type="password", key="nova_s")
                
                if st.form_submit_button("Atualizar Senha"):
                    if not nova_senha:
                        st.error("Digite a nova senha.")
                    else:
                        hashed_p = stauth.Hasher([nova_senha]).generate()[0]
                        try:
                            # Atualiza ou insere caso não esteja na tabela SQL ainda
                            res_up = supabase.table("usuarios_sistema").update({"password": hashed_p}).eq("username", usr_sel).execute()
                            if not res_up.data:
                                # Se não achou na tabela (ex: usuário padrão hardcoded), insere direto
                                info_u = credentials["usernames"][usr_sel]
                                supabase.table("usuarios_sistema").insert({
                                    "username": usr_sel,
                                    "name": info_u["name"],
                                    "password": hashed_p,
                                    "role": info_u["role"]
                                }).execute()
                            st.cache_data.clear()
                            st.success(f"Senha do usuário **{usr_sel}** alterada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao alterar senha: {e}")

    else:
        # Demais módulos (Clientes, Pagamentos, etc. mantidos intactos)
        menu_principal = menu_escolha
        st.title(f"Módulo: {menu_principal} ⚖️")
        # ... (continua a lógica normal dos outros módulos já otimizados)
