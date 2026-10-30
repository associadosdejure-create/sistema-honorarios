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
import io

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

# --- ESTILIZAÇÃO CSS (PRETO, DOURADO E TABELAS COM TEXTO EXPANDIDO) ---
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
except Exception as e:
    st.error(f"⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes ou inválidas. Detalhe: {e}")
    st.stop()

def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def converter_imagem_base64(file) -> str:
    encoded = base64.b64encode(file.read()).decode()
    mime_type = file.type
    return f"data:{mime_type};base64,{encoded}"

def exibir_imagem_base64(foto_url, width=120):
    if not foto_url or not isinstance(foto_url, str):
        return False
    try:
        if foto_url.startswith("data:"):
            header, encoded = foto_url.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            st.image(io.BytesIO(image_bytes), width=width)
            return True
        else:
            st.image(foto_url, width=width)
            return True
    except Exception:
        return False

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
                "oab": "",
                "data_nascimento": None,
                "observacoes_pessoais": ""
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
                    "data_nascimento": u.get("data_nascimento", None),
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
else:
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
                            try:
                                supabase.table("usuarios_sistema").update({
                                    "senha_hash": hash_novo,
                                    "password": hash_novo,
                                    "trocar_senha": False
                                }).eq("username", username).execute()
                            except Exception:
                                supabase.table("usuarios_sistema").update({
                                    "senha_hash": hash_novo,
                                    "password": hash_novo
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

    if 'pagina_atual' not in st.session_state: st.session_state['pagina_atual'] = "🏠 Página Inicial"
    if 'submenu_atual' not in st.session_state: st.session_state['submenu_atual'] = ""
    
    if 'ocultar_vencidos' not in st.session_state: st.session_state['ocultar_vencidos'] = set()
    if 'ocultar_urgentes' not in st.session_state: st.session_state['ocultar_urgentes'] = set()
    if 'ocultar_lembretes' not in st.session_state: st.session_state['ocultar_lembretes'] = set()

    def validar_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11 or cpf == cpf[0] * 11: return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        d1 = (soma * 10) % 11; d1 = 0 if d1 == 10 else d1
        if d1 != int(cpf[9]): return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        d2 = (soma * 10) % 11; d2 = 0 if d2 == 10 else d2
        return d2 == int(cpf[10])

    @st.cache_data(ttl=300)
    def carregar_dados(tabela):
        res = supabase.table(tabela).select("*").execute()
        return res.data if res.data else []

    def importar_excel_para_supabase(tabela, arquivo):
        try:
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)
            
            df = df.loc[:, ~df.columns.str.contains('^Unnamed', na=False)]
            df = df.dropna(how='all', axis=1)
            df.columns = df.columns.str.strip().str.lower()
            
            df = df.where(pd.notnull(df), "")
            df = df.fillna("")
            
            for col in df.columns:
                if 'data' in col.lower() or 'vencimento' in col.lower():
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                    df[col] = df[col].replace(['NaT', 'nan', 'NAT', 'NaN', 'None', ''], None)
                elif 'hora' in col.lower():
                    df[col] = df[col].apply(lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else (str(x) if x != "" else None))

            dados = df.to_dict(orient="records")
            dadosLimpos = [{k: (v if pd.notnull(v) and v != "" else None) for k, v in registro.items()} for registro in dados]

            supabase.table(tabela).insert(dadosLimpos).execute()
            registrar_auditoria(username, "Importação Excel", tabela, f"{len(dadosLimpos)} registros importados.")
            st.cache_data.clear()
            st.success(f"🎉 {len(dadosLimpos)} registros importados com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"⚠️ Erro ao importar planilha: {e}")

    def colorir_status(val):
        if str(val).lower() == 'pendente':
            return 'color: #FF4B4B; font-weight: bold;'
        elif str(val).lower() in ['manifestado', 'concluído', 'pago', 'entregue']:
            return 'color: #00CC96; font-weight: bold;'
        elif str(val).lower() == 'em andamento':
            return 'color: #FFA15A; font-weight: bold;'
        return ''

    with st.sidebar:
        user_foto = user_info.get("foto_url", None)
        col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
        with col_f2:
            if not exibir_imagem_base64(user_foto, width=100):
                st.markdown("<h1 style='text-align: center; margin: 0;'>👤</h1>", unsafe_allow_html=True)

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
            "⚖️ Expedientes TRF": "Expedientes TRF",
            "📋 Pendências": "Pendências",
            "🌟 Equipe Dejure": "Equipe Dejure",
            "🔒 Segurança": "Segurança"
        }
        
        if user_role == 'admin':
            modulos["🛡️ Auditoria"] = "Auditoria"

        for label, pag in modulos.items():
            if st.button(label, use_container_width=True):
                st.session_state['pagina_atual'] = pag
                st.session_state['submenu_atual'] = "" if pag in ["🏠 Página Inicial", "🌟 Equipe Dejure"] else {
                    "Clientes": "Consultar Clientes", 
                    "Pagamentos": "Ver Parcelas", 
                    "Perícias": "Ver Perícias", 
                    "Expedientes": "Consultar Expedientes", 
                    "Expedientes TRF": "Consultar Expedientes TRF",
                    "Pendências": "Consultar Pendências",
                    "Segurança": "Meu Perfil",
                    "Auditoria": "Ver Logs"
                }.get(pag, "")
                limpar_flags_cadastro()
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"⏳ **Sessão expira em:**\n### `{min_res:02d}:{seg_res:02d}`")
        st.markdown("---")
        
        if st.button("Sair", use_container_width=True):
            registrar_auditoria(username, "Logout", "Acesso", f"Usuário {name} ({username}) efetuou logout do sistema.")
            st.session_state.update({'authentication_status': None, 'login_registrado': False})
            st.rerun()

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

        st.markdown(f"### Seja bem-vindo, {name}! ⚖️")

        try:
            res_users_nasc = supabase.table("usuarios_sistema").select("nome_completo, name, data_nascimento").execute()
            if res_users_nasc.data:
                hoje_str = date.today().strftime("%m-%d")
                aniversariantes_hoje = []
                for u in res_users_nasc.data:
                    dt_n = u.get("data_nascimento")
                    if dt_n and len(dt_n) >= 10:
                        if dt_n[5:] == hoje_str:
                            aniversariantes_hoje.append(u.get("nome_completo", u.get("name", "Colaborador")))
                
                if aniversariantes_hoje:
                    nomes_aniv = " e ".join(aniversariantes_hoje)
                    st.success(f"🥳 **PARABÉNS DA EQUIPE DEJURE!** Hoje é o aniversário de **{nomes_aniv}**! 🎂 Desejamos muito sucesso, felicidades e realizações!")
        except Exception:
            pass

        st.markdown("### 📊 Visão Geral do Escritório")
        
        try:
            cli, hon, per, exp, exp_trf, pen = carregar_dados("clientes_cadastrados"), carregar_dados("honorarios"), carregar_dados("pericias"), carregar_dados("expedientes"), carregar_dados("expedientes_trf"), carregar_dados("pendencias")
            parcelas_db = carregar_dados("parcelas")
            
            per_pendentes_com_data = 0
            for p in per:
                if p.get('status') == 'Pendente' and (p.get('data_pm') or p.get('data_ps')):
                    per_pendentes_com_data += 1

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Clientes", len(cli))
            c2.metric("Contratos", len(hon))
            c3.metric("Perícias Pend.", per_pendentes_com_data)
            c4.metric("Expedientes Pend.", len([e for e in exp if e.get('status') == 'Pendente' and e.get('data_manifestacao')]))
            c5.metric("Exp. TRF Pend.", len([et for et in exp_trf if et.get('status') == 'Pendente' and et.get('data_manifestacao')]))
            c6.metric("Parcelas Pend.", len([pc for pc in parcelas_db if pc.get('status') == 'Pendente' and pc.get('vencimento')]))
        except Exception: pass

        st.markdown("---")
        try:
            hoje = date.today()
            alertas_pericias = []
            alertas_expedientes = []
            alertas_expedientes_trf = []
            alertas_pagamentos = []

            for p in per:
                if p.get('status') == 'Pendente':
                    if p.get('data_pm'):
                        dt = datetime.strptime(p['data_pm'], "%Y-%m-%d").date()
                        dias_restantes = (dt - hoje).days
                        if dias_restantes >= -5:
                            uid = f"per_{p['id']}_pm"
                            alertas_pericias.append((dias_restantes, f"🔬 Perícia Médica | Nome: {p.get('nome', 'N/D')} | Data PM: {dt.strftime('%d/%m/%Y')}", uid, 'pericia'))
                    if p.get('data_ps'):
                        dt = datetime.strptime(p['data_ps'], "%Y-%m-%d").date()
                        dias_restantes = (dt - hoje).days
                        if dias_restantes >= -5:
                            uid = f"per_{p['id']}_ps"
                            alertas_pericias.append((dias_restantes, f"🔬 Perícia Social | Nome: {p.get('nome', 'N/D')} | Data PS: {dt.strftime('%d/%m/%Y')}", uid, 'pericia'))

            for e in exp:
                if e.get('status') == 'Pendente' and e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    uid = f"exp_{e.get('id', 0)}"
                    alertas_expedientes.append(((dt - hoje).days, f"📂 Processo: {e['numero_processo']} | Cliente: {e.get('cliente', 'N/D')} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {e['responsavel']}", uid, 'expediente'))

            for et in exp_trf:
                if et.get('status') == 'Pendente' and et.get('data_manifestacao'):
                    dt = datetime.strptime(et['data_manifestacao'], "%Y-%m-%d").date()
                    uid = f"trf_{et.get('id', 0)}"
                    alertas_expedientes_trf.append(((dt - hoje).days, f"⚖️ Processo: {et['numero_processo']} | Cliente: {et.get('cliente', 'N/D')} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {et['responsavel']}", uid, 'expediente_trf'))

            for pc in parcelas_db:
                if pc.get('status') == 'Pendente' and pc.get('vencimento'):
                    dt = datetime.strptime(pc['vencimento'], "%Y-%m-%d").date()
                    uid = f"pag_{pc.get('id', 0)}"
                    alertas_pagamentos.append(((dt - hoje).days, f"💰 Parcela {pc.get('numero_parcela')} | Vencimento: {dt.strftime('%d/%m/%Y')} | Valor: R$ {pc.get('valor', 0):.2f}", uid, 'pagamento'))

            total_alertas = len(alertas_pericias) + len(alertas_expedientes) + len(alertas_expedientes_trf) + len(alertas_pagamentos)

            if total_alertas > 0:
                st.subheader("🚨 Central de Alertas de Prazos e Vencimentos")
                tab_per, tab_exp, tab_trf, tab_pag = st.tabs(["🔬 Perícias", "📂 Expedientes", "⚖️ Expedientes TRF", "💰 Pagamentos"])

                def renderizar_lista_alerta(lista_alertas, nome_cat):
                    lista_visivel = [
                        item for item in lista_alertas 
                        if item[2] not in st.session_state['ocultar_vencidos'] 
                        and item[2] not in st.session_state['ocultar_urgentes'] 
                        and item[2] not in st.session_state['ocultar_lembretes']
                    ]

                    if not lista_visivel:
                        st.info("Nenhum alerta pendente visível nesta categoria.")
                        return

                    if user_role == 'admin':
                        st.markdown(f"##### ⚡ Limpeza Visual (Apenas Tela)")
                        col_b1, col_b2, col_b3 = st.columns(3)
                        
                        with col_b1:
                            if st.button(f"🔴 Ocultar Vencidos", key=f"btn_venc_{nome_cat}"):
                                for item in lista_alertas:
                                    if item[0] < 0:
                                        st.session_state['ocultar_vencidos'].add(item[2])
                                st.rerun()

                        with col_b2:
                            if st.button(f"🟠 Ocultar Críticos/Urgentes", key=f"btn_urg_{nome_cat}"):
                                for item in lista_alertas:
                                    if 0 <= item[0] <= 3:
                                        st.session_state['ocultar_urgentes'].add(item[2])
                                st.rerun()

                        with col_b3:
                            if st.button(f"🟢 Ocultar Lembretes", key=f"btn_lemb_{nome_cat}"):
                                for item in lista_alertas:
                                    if item[0] > 3:
                                        st.session_state['ocultar_lembretes'].add(item[2])
                                st.rerun()
                        st.markdown("---")

                    for dias, texto, uid, _ in sorted(lista_visivel, key=lambda x: x[0]):
                        if dias < 0: st.error(f"⚠️ **VENCIDO ({abs(dias)} dias):** {texto}")
                        elif dias == 1: st.error(f"🚨 **CRÍTICO (1 dia):** {texto}")
                        elif dias <= 3: st.warning(f"⚠️ **URGENTE ({dias} dias):** {texto}")
                        else: st.info(f"📅 **LEMBRETE ({dias} dias):** {texto}")

                with tab_per: renderizar_lista_alerta(alertas_pericias, "pericias")
                with tab_exp: renderizar_lista_alerta(alertas_expedientes, "expedientes")
                with tab_trf: renderizar_lista_alerta(alertas_expedientes_trf, "expedientes_trf")
                with tab_pag: renderizar_lista_alerta(alertas_pagamentos, "pagamentos")
            else:
                st.info("🎉 Nenhum alerta de prazo ou pagamento pendente para hoje!")
        except Exception as e: 
            st.error(f"Erro ao carregar central de alertas: {e}")
    
    elif menu_escolha == "🌟 Equipe Dejure":
        st.title("🌟 Galeria da Equipe Dejure")
        st.caption("Conheça os profissionais que compõem o nosso escritório e celebre os aniversariantes.")
        
        try:
            res_usuarios = supabase.table("usuarios_sistema").select("*").execute()
            lista_colabs = res_usuarios.data if res_usuarios.data else []
            
            with st.expander("🛠️ Diagnóstico do Módulo Equipe Dejure", expanded=False):
                st.write(f"Total de registros na tabela `usuarios_sistema`: **{len(lista_colabs)}**")
                if lista_colabs: st.json(lista_colabs)
                else: st.warning("A tabela retornou vazia.")

            if not lista_colabs:
                st.warning("⚠️ Nenhum colaborador encontrado na tabela `usuarios_sistema` do Supabase.")
            else:
                st.markdown("### 🏆 Colaborador(a) em Destaque do Mês")
                colabs_validos = [u for u in lista_colabs if str(u.get('username', '')).strip().lower() != 'master']
                
                if colabs_validos:
                    if user_role == 'admin':
                        nomes_c = [c.get('nome_completo', c.get('name', '')) for c in colabs_validos]
                        destaque_atual = st.selectbox("Selecione o Colaborador do Mês em Destaque:", nomes_c, index=0, key="sel_colab_mes")
                    else:
                        destaque_atual = colabs_validos[0].get('nome_completo', colabs_validos[0].get('name', ''))

                    obj_destaque = next((c for c in colabs_validos if c.get('nome_completo') == destaque_atual or c.get('name') == destaque_atual), colabs_validos[0])
                    
                    col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                    with col_d2:
                        st.markdown("""
                            <div style="background: linear-gradient(135deg, #1F1F1F, #121212); padding: 20px; border-radius: 15px; border: 2px solid #D4AF37; text-align: center; box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3);">
                        """, unsafe_allow_html=True)
                        
                        foto_dest = obj_destaque.get('foto_url')
                        if not exibir_imagem_base64(foto_dest, width=140):
                            st.markdown("<h1 style='font-size: 60px; margin: 0;'>⭐</h1>", unsafe_allow_html=True)
                        
                        st.markdown(f"<h3 style='color: #D4AF37; margin-top: 10px;'>{obj_destaque.get('nome_completo', obj_destaque.get('name', ''))}</h3>", unsafe_allow_html=True)
                        papel_d = {"admin": "👑 Sócio Administrador", "advogado": "⚖️ Advogado(a)", "bacharel": "📜 Bacharel(a)"}.get(obj_destaque.get('role'), "🎓 Estagiário(a)")
                        st.markdown(f"<p style='color: #E0E0E0; font-weight: bold;'>{papel_d}</p>", unsafe_allow_html=True)
                        if obj_destaque.get('oab'):
                            st.markdown(f"<p style='color: #A0A0A0; font-size: 14px;'>OAB: {obj_destaque.get('oab')}</p>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 🖼️ Galeria de Profissionais")
                
                cols_galeria = st.columns(3)
                for idx, colab in enumerate(lista_colabs):
                    col_atual = cols_galeria[idx % 3]
                    with col_atual:
                        st.markdown("""
                            <div style="background-color: #161616; padding: 15px; border-radius: 10px; border: 1px solid #333333; text-align: center; margin-bottom: 15px; min-height: 280px;">
                        """, unsafe_allow_html=True)
                        
                        f_url = colab.get('foto_url')
                        if not exibir_imagem_base64(f_url, width=110):
                            st.markdown("<h1 style='font-size: 50px; margin: 0;'>👤</h1>", unsafe_allow_html=True)
                        
                        nome_c = colab.get('nome_completo', colab.get('name', ''))
                        cargo_c = {"admin": "👑 Sócio", "advogado": "⚖️ Advogado(a)", "bacharel": "📜 Bacharel(a)"}.get(colab.get('role'), "🎓 Estagiário(a)")
                        
                        st.markdown(f"<h4 style='color: #D4AF37; margin: 10px 0 5px 0;'>{nome_c}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #CCCCCC; font-size: 13px; margin: 0;'>{cargo_c}</p>", unsafe_allow_html=True)
                        
                        if colab.get('oab'):
                            st.markdown(f"<p style='color: #999999; font-size: 12px; margin: 2px 0;'>OAB: {colab.get('oab')}</p>", unsafe_allow_html=True)
                        
                        if colab.get('telefone'):
                            st.markdown(f"<p style='color: #999999; font-size: 12px; margin: 2px 0;'>📞 {colab.get('telefone')}</p>", unsafe_allow_html=True)
                        
                        dt_nasc = colab.get('data_nascimento')
                        if dt_nasc:
                            try:
                                dt_obj = datetime.strptime(dt_nasc, "%Y-%m-%d")
                                st.markdown(f"<p style='color: #00CC96; font-size: 12px; margin-top: 5px;'>🎂 Aniversário: <strong>{dt_obj.strftime('%d/%m')}</strong></p>", unsafe_allow_html=True)
                            except:
                                pass
                        
                        st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao carregar a galeria da equipe: {e}")

    elif menu_escolha == "Auditoria" and user_role == 'admin':
        st.title("🛡️ Central de Auditoria do Sistema")
        st.caption("Acompanhe as ações gerais do sistema e os registros de acesso dos usuários.")
        
        tab_geral, tab_acessos = st.tabs(["🛡️ Auditoria Geral", "🔑 Logs de Acesso (Login / Logout)"])
        
        with tab_geral:
            st.subheader("Histórico de Ações Gerais")
            if st.button("🔥 ZERAR LOGS GERAIS", key="btn_zerar_geral"):
                try:
                    supabase.table("logs_auditoria").delete().neq("id", 0).execute()
                    st.success("Logs gerais zerados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            try:
                res_logs = supabase.table("logs_auditoria").select("*").neq("modulo", "Acesso").order("data_hora", desc=True).limit(100).execute()
                if res_logs.data:
                    df_logs = pd.DataFrame(res_logs.data)
                    st.dataframe(df_logs, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de auditoria geral encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar logs gerais: {e}")

        with tab_acessos:
            st.subheader("Histórico de Entradas e Saídas (Login / Logout)")
            if st.button("🔥 ZERAR LOGS DE ACESSO", key="btn_zerar_acesso"):
                try:
                    supabase.table("logs_auditoria").delete().eq("modulo", "Acesso").execute()
                    st.success("Logs de acesso zerados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

            try:
                res_acessos = supabase.table("logs_auditoria").select("*").eq("modulo", "Acesso").order("data_hora", desc=True).limit(100).execute()
                if res_acessos.data:
                    df_acessos = pd.DataFrame(res_acessos.data)
                    st.dataframe(df_acessos, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum registro de acesso encontrado.")
            except Exception as e:
                st.error(f"Erro ao carregar logs de acesso: {e}")

    else:
        menu_principal = menu_escolha
        st.title(f"Módulo: {menu_principal} ⚖️")

        if menu_principal == "Clientes":
            acoes = ["Consultar Clientes", "Cadastrar Cliente", "Importar Excel", "Editar Cliente", "Exportar Base (Backup)"]
            if user_role == 'admin': acoes.insert(4, "Excluir Cliente")
        elif menu_principal == "Pagamentos":
            acoes = ["Ver Parcelas", "Cadastrar Contrato", "Editar Contrato"]
            if user_role == 'admin': acoes = ["Ver Parcelas", "Cadastrar Contrato", "Baixar Parcela", "Extrato de Repasses", "Relatório por Período", "Editar Contrato", "Excluir Contrato"]
        elif menu_principal == "Perícias":
            acoes = ["Ver Perícias", "Cadastrar Perícia", "Importar Excel", "Editar Perícia"]
            if user_role == 'admin': acoes.append("Excluir Perícia")
        elif menu_principal == "Expedientes":
            acoes = ["Consultar Expedientes", "Cadastrar Expediente", "Importar Excel", "Editar Expediente"]
            if user_role == 'admin': acoes.append("Excluir Expediente")
        elif menu_principal == "Expedientes TRF":
            acoes = ["Consultar Expedientes TRF", "Cadastrar Expediente TRF", "Importar Excel", "Editar Expediente TRF"]
            if user_role == 'admin': acoes.append("Excluir Expediente TRF")
        elif menu_principal == "Pendências":
            acoes = ["Consultar Pendências", "Cadastrar Pendência", "Importar Excel", "Editar Pendência"]
            if user_role == 'admin': acoes.append("Excluir Pendência")
        elif menu_principal == "Segurança":
            acoes = ["Meu Perfil", "Alterar Senha"]
            if user_role == 'admin': acoes = ["Meu Perfil", "Gerenciar Usuários", "Cadastrar Novo Usuário", "Alterar Senha"]
        else:
            acoes = []

        if not st.session_state['submenu_atual'] or st.session_state['submenu_atual'] not in acoes:
            if acoes: st.session_state['submenu_atual'] = acoes[0]

        if acoes:
            cols = st.columns(len(acoes))
            for idx, acao in enumerate(acoes):
                with cols[idx]:
                    if st.button(acao, use_container_width=True, type="primary" if st.session_state['submenu_atual'] == acao else "secondary"):
                        st.session_state['submenu_atual'] = acao
                        limpar_flags_cadastro()
                        st.rerun()

        st.markdown("---")
        sub = st.session_state['submenu_atual']

        # --- PROCESSAMENTO DOS MÓDULOS RESTAURADOS ---
        if menu_principal == "Segurança":
            if sub == "Meu Perfil":
                st.header("👤 Meu Perfil de Usuário")
                col_pf1, col_pf2 = st.columns([1, 2])
                with col_pf1:
                    if not exibir_imagem_base64(user_info.get("foto_url"), width=200): st.info("Sem foto cadastrada.")
                with col_pf2:
                    with st.form("form_meu_perfil"):
                        p_nome = st.text_input("Nome Completo", value=user_info.get("name", ""))
                        p_tel = st.text_input("Telefone de Contato", value=user_info.get("telefone", ""))
                        p_oab = st.text_input("Registro OAB", value=user_info.get("oab", ""))
                        dt_nasc_val = date(1990, 1, 1)
                        if user_info.get("data_nascimento"):
                            try: dt_nasc_val = datetime.strptime(user_info.get("data_nascimento"), "%Y-%m-%d").date()
                            except: pass
                        p_nasc = st.date_input("Data de Nascimento", value=dt_nasc_val)
                        file_foto = st.file_uploader("Escolher Foto (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
                        p_obs = st.text_area("Observações Pessoais", value=user_info.get("observacoes_pessoais", ""))
                        if st.form_submit_button("Salvar Alterações no Perfil", type="primary"):
                            if username == "master": st.warning("A conta Master de emergência não altera perfil no banco.")
                            else:
                                try:
                                    foto_final = user_info.get("foto_url")
                                    if file_foto is not None: foto_final = converter_imagem_base64(file_foto)
                                    supabase.table("usuarios_sistema").update({
                                        "nome_completo": p_nome, "name": p_nome, "telefone": p_tel, "oab": p_oab,
                                        "data_nascimento": p_nasc.strftime("%Y-%m-%d"), "foto_url": foto_final, "observacoes_pessoais": p_obs
                                    }).eq("username", username).execute()
                                    registrar_auditoria(username, "Atualizar Perfil", "Segurança", "Perfil atualizado.")
                                    st.cache_data.clear(); st.success("✅ Perfil atualizado!"); time.sleep(1); st.rerun()
                                except Exception as e: st.error(f"Erro ao salvar: {e}")
            elif sub == "Alterar Senha":
                st.header("🔐 Alterar Minha Senha")
                with st.form("form_alt_senha"):
                    nova_senha = st.text_input("Nova Senha", type="password")
                    conf_senha = st.text_input("Confirmar Nova Senha", type="password")
                    if st.form_submit_button("Atualizar Minha Senha"):
                        if not nova_senha or nova_senha != conf_senha: st.error("As senhas não coincidem ou estão vazias.")
                        elif username == 'master': st.error("A conta Master não pode ser alterada.")
                        else:
                            novo_hash = gerar_hash(nova_senha)
                            supabase.table("usuarios_sistema").update({"senha_hash": novo_hash, "password": novo_hash}).eq("username", username).execute()
                            registrar_auditoria(username, "Alterar Senha", "Segurança", "Senha alterada.")
                            st.cache_data.clear(); st.success("✅ Senha alterada com sucesso!")
            elif sub == "Cadastrar Novo Usuário" and user_role == 'admin':
                st.header("➕ Cadastrar Novo Usuário")
                with st.form("form_cad_user", clear_on_submit=True):
                    new_user = st.text_input("Nome de Usuário (login)")
                    new_name = st.text_input("Nome Completo")
                    new_pass = st.text_input("Senha Inicial", type="password")
                    perfis_opcoes = {"👑 Sócio / Administrador": "admin", "⚖️ Advogado(a)": "advogado", "📜 Bacharel(a)": "bacharel", "🎓 Estagiário(a)": "estagiario"}
                    new_role = perfis_opcoes[st.selectbox("Perfil de Acesso", list(perfis_opcoes.keys()))]
                    if st.form_submit_button("Cadastrar Usuário"):
                        if not new_user or not new_name or not new_pass: st.error("Preencha todos os campos.")
                        else:
                            senha_hash = gerar_hash(new_pass)
                            supabase.table("usuarios_sistema").insert({"username": new_user.strip().lower(), "nome_completo": new_name, "name": new_name, "senha_hash": senha_hash, "password": senha_hash, "role": new_role, "trocar_senha": True}).execute()
                            registrar_auditoria(username, "Cadastrar Usuário", "Segurança", f"Usuário criado: {new_user}")
                            st.cache_data.clear(); st.success("🎉 Usuário cadastrado com sucesso!")
            elif sub == "Gerenciar Usuários" and user_role == 'admin':
                st.header("🛡️ Gerenciamento de Usuários Ativos")
                res_users = supabase.table("usuarios_sistema").select("*").execute()
                if res_users.data:
                    df_u = pd.DataFrame(res_users.data)
                    st.dataframe(df_u[[c for c in ['id', 'username', 'nome_completo', 'role', 'telefone', 'oab'] if c in df_u.columns]], use_container_width=True, hide_index=True)

        elif menu_principal == "Clientes":
            if sub == "Cadastrar Cliente":
                st.header("👤 Cadastro de Cliente")
                with st.form("fc_cli", clear_on_submit=True):
                    n, doc, tel, email, end, cid, gov, ind, obs = st.text_input("Nome *"), st.text_input("CPF/CNPJ"), st.text_input("Telefone"), st.text_input("E-mail"), st.text_input("Endereço"), st.text_input("Cidade/UF"), st.text_input("Senha Gov.br"), st.text_input("Indicado Por"), st.text_area("Observações")
                    if st.form_submit_button("Salvar"):
                        if not n: st.error("Nome obrigatório.")
                        else:
                            supabase.table("clientes_cadastrados").insert({"nome": n, "cpf_cnpj": doc, "telefone": tel, "email": email, "endereco": end, "cidade": cid, "senha_gov": gov, "indicado_por": ind, "observacoes": obs}).execute()
                            registrar_auditoria(username, "Cadastrar Cliente", "Clientes", f"Cliente: {n}")
                            st.cache_data.clear(); st.success("🎉 Cliente cadastrado!")
            elif sub == "Consultar Clientes":
                st.header("📋 Base de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else: st.info("Nenhum cliente cadastrado.")
            elif sub == "Importar Excel":
                st.header("📥 Importar Clientes via Planilha")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_cli")
                if file_up and st.button("Confirmar", type="primary"): importar_excel_para_supabase("clientes_cadastrados", file_up)

        elif menu_principal == "Pagamentos":
            if sub == "Ver Parcelas":
                st.header("📋 Visualizar Parcelas")
                res_h = carregar_dados("honorarios")
                if res_h:
                    cdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(cdict.keys()))
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel]).execute()
                    if res_p.data: st.dataframe(pd.DataFrame(res_p.data), use_container_width=True, hide_index=True)
                    else: st.info("Sem parcelas.")
                else: st.info("Sem contratos.")
            elif sub == "Cadastrar Contrato":
                st.header("📝 Novo Contrato")
                cli_db = carregar_dados("clientes_cadastrados")
                nomes = [c['nome'] for c in cli_db]
                with st.form("fc_hon", clear_on_submit=True):
                    cli = st.selectbox("Cliente:", ["Outro"] + nomes) if nomes else "Outro"
                    c_nome = st.text_input("Nome do Cliente") if cli == "Outro" else cli
                    serv = st.text_input("Serviço")
                    vtot = st.number_input("Valor Total (R$)", min_value=0.0, step=100.0)
                    if st.form_submit_button("Gerar Contrato"):
                        supabase.table("honorarios").insert({"cliente": c_nome, "servico": serv, "valor_total": float(vtot)}).execute()
                        st.cache_data.clear(); st.success("🎉 Contrato gerado!")

        elif menu_principal == "Perícias":
            if sub == "Ver Perícias":
                st.header("📋 Lista de Perícias")
                res = carregar_dados("pericias")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else: st.info("Sem perícias.")
            elif sub == "Cadastrar Perícia":
                st.header("🔬 Nova Perícia")
                with st.form("fc_per", clear_on_submit=True):
                    nome = st.text_input("Nome *")
                    if st.form_submit_button("Salvar"):
                        if nome:
                            supabase.table("pericias").insert({"nome": nome, "status": "Pendente"}).execute()
                            st.cache_data.clear(); st.success("Perícia cadastrada!")

        elif menu_principal == "Expedientes":
            if sub == "Consultar Expedientes":
                st.header("📂 Expedientes")
                res = carregar_dados("expedientes")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else: st.info("Sem expedientes.")

        elif menu_principal == "Expedientes TRF":
            if sub == "Consultar Expedientes TRF":
                st.header("⚖️ Expedientes TRF")
                res = carregar_dados("expedientes_trf")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else: st.info("Sem expedientes TRF.")

        elif menu_principal == "Pendências":
            if sub == "Consultar Pendências":
                st.header("📋 Pendências")
                res = carregar_dados("pendencias")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
                else: st.info("Sem pendências.")
