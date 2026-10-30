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
    
    /* Força todas as tabelas a quebrarem o texto e se ajustarem sem cortar */
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
                "oab": "",
                "data_nascimento": None,
                "destaque_mes": False
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
                    "observacoes_pessoais": u.get("observacoes_pessoais", ""),
                    "destaque_mes": u.get("destaque_mes", False)
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
        pass  
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
            if user_foto:
                st.image(user_foto, use_container_width=True) # Foto no formato retangular original
            else:
                st.markdown("<h1 style='text-align: center; margin: 0;'>👤</h1>", unsafe_allow_html=True)

        st.write(f"Logado como: **{name}**")
        p_txt = {"admin": "👑 Sócio", "advogado": "⚖️ Advogado(a)", "bacharel": "📜 Bacharel(a)"}.get(user_role, "🎓 Estagiário")
        st.caption(f"Perfil: {p_txt}")
        
        # BOTÃO SAIR LOGO ABAIXO DO PERFIL DO USUÁRIO
        if st.button("🚪 Sair", use_container_width=True):
            registrar_auditoria(username, "Logout", "Acesso", f"Usuário {name} ({username}) efetuou logout do sistema.")
            st.session_state.update({'authentication_status': None, 'login_registrado': False})
            st.rerun()

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
            "🧑‍⚖️ Equipe Dejure": "Equipe Dejure",
            "🔒 Segurança": "Segurança"
        }
        
        if user_role == 'admin':
            modulos["🛡️ Auditoria"] = "Auditoria"

        for label, pag in modulos.items():
            if st.button(label, use_container_width=True):
                st.session_state['pagina_atual'] = pag
                st.session_state['submenu_atual'] = "" if pag == "🏠 Página Inicial" else {
                    "Clientes": "Consultar Clientes", 
                    "Pagamentos": "Ver Parcelas", 
                    "Perícias": "Ver Perícias", 
                    "Expedientes": "Consultar Expedientes", 
                    "Expedientes TRF": "Consultar Expedientes TRF",
                    "Pendências": "Consultar Pendências",
                    "Equipe Dejure": "Nossa Equipe",
                    "Segurança": "Meu Perfil",
                    "Auditoria": "Ver Logs"
                }.get(pag, "")
                limpar_flags_cadastro()
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"⏳ **Sessão expira em:**\n### `{min_res:02d}:{seg_res:02d}`")
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

                with tab_per:
                    renderizar_lista_alerta(alertas_pericias, "pericias")
                with tab_exp:
                    renderizar_lista_alerta(alertas_expedientes, "expedientes")
                with tab_trf:
                    renderizar_lista_alerta(alertas_expedientes_trf, "expedientes_trf")
                with tab_pag:
                    renderizar_lista_alerta(alertas_pagamentos, "pagamentos")
            else:
                st.info("🎉 Nenhum alerta de prazo ou pagamento pendente para hoje!")
        except Exception as e: 
            st.error(f"Erro ao carregar central de alertas: {e}")
    
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
            if user_role == 'admin':
                acoes.insert(4, "Excluir Cliente")
        elif menu_principal == "Pagamentos":
            acoes = ["Ver Parcelas", "Cadastrar Contrato", "Editar Contrato"]
            if user_role == 'admin':
                acoes = ["Ver Parcelas", "Cadastrar Contrato", "Baixar Parcela", "Extrato de Repasses", "Relatório por Período", "Editar Contrato", "Excluir Contrato"]
        elif menu_principal == "Perícias":
            acoes = ["Ver Perícias", "Cadastrar Perícia", "Importar Excel", "Editar Perícia"]
            if user_role == 'admin':
                acoes.append("Excluir Perícia")
        elif menu_principal == "Expedientes":
            acoes = ["Consultar Expedientes", "Cadastrar Expediente", "Importar Excel", "Editar Expediente"]
            if user_role == 'admin':
                acoes.append("Excluir Expediente")
        elif menu_principal == "Expedientes TRF":
            acoes = ["Consultar Expedientes TRF", "Cadastrar Expediente TRF", "Importar Excel", "Editar Expediente TRF"]
            if user_role == 'admin':
                acoes.append("Excluir Expediente TRF")
        elif menu_principal == "Pendências":
            acoes = ["Consultar Pendências", "Cadastrar Pendência", "Importar Excel", "Editar Pendência"]
            if user_role == 'admin':
                acoes.append("Excluir Pendência")
        elif menu_principal == "Equipe Dejure":
            acoes = ["Nossa Equipe"]
        elif menu_principal == "Segurança":
            acoes = ["Meu Perfil", "Alterar Senha"]
            if user_role == 'admin':
                acoes = ["Meu Perfil", "Gerenciar Usuários", "Cadastrar Novo Usuário", "Alterar Senha"]
        else:
            acoes = []

        if not st.session_state['submenu_atual'] or st.session_state['submenu_atual'] not in acoes:
            if acoes:
                st.session_state['submenu_atual'] = acoes[0]

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

        # --- PROCESSAMENTO DOS MÓDULOS ---
        
        if menu_principal == "Equipe Dejure":
            if sub == "Nossa Equipe":
                st.header("🧑‍⚖️ Equipe Dejure")
                st.caption("Conheça os profissionais que fazem parte do nosso escritório.")
                
                usuarios_equipe = []
                for uname, uinfo in credentials["usernames"].items():
                    if uname != "master" and uinfo.get("name"):
                        u_copy = uinfo.copy()
                        u_copy["username"] = uname
                        usuarios_equipe.append(u_copy)
                
                if not usuarios_equipe:
                    st.info("Nenhum membro da equipe encontrado.")
                else:
                    if user_role == 'admin':
                        with st.expander("⭐ Definir Destaque do Mês (Apenas Administrador)"):
                            opcoes_destaque = {"Nenhum Destaque / Remover": ""}
                            for u in usuarios_equipe:
                                opcoes_destaque[u['name']] = u['username']
                            
                            sel_destaque = st.selectbox("Selecione o Colaborador:", list(opcoes_destaque.keys()))
                            
                            if st.button("Salvar Destaque", type="primary"):
                                try:
                                    supabase.table("usuarios_sistema").update({"destaque_mes": False}).neq("username", "master").execute()
                                    user_selecionado = opcoes_destaque[sel_destaque]
                                    if user_selecionado:
                                        supabase.table("usuarios_sistema").update({"destaque_mes": True}).eq("username", user_selecionado).execute()
                                        registrar_auditoria(username, "Destaque do Mês", "Equipe", f"Destaque definido para: {sel_destaque}")
                                    
                                    st.cache_data.clear()
                                    st.success("Destaque atualizado com sucesso! Recarregando...")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar: {e}")
                    
                    st.markdown("---")
                    
                    destaque = next((u for u in usuarios_equipe if u.get("destaque_mes")), None)
                    outros = [u for u in usuarios_equipe if not u.get("destaque_mes")]

                    if destaque:
                        col_d1, col_d2, col_d3 = st.columns([1, 2, 1])
                        with col_d2:
                            with st.container(border=True):
                                st.markdown("<h3 style='text-align: center; color: #0A0A0A; background-color: #D4AF37; margin-top: 0; padding: 10px; border-radius: 5px;'>🏆 DESTAQUE DO MÊS 🏆</h3>", unsafe_allow_html=True)
                                
                                foto = destaque.get("foto_url")
                                if foto:
                                    st.markdown(f"""
                                        <div style='width: 100%; height: 320px; overflow: hidden; border-radius: 5px; margin-bottom: 15px;'>
                                            <img src='{foto}' style='width: 100%; height: 100%; object-fit: cover;'>
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='width: 100%; height: 320px; display: flex; align-items: center; justify-content: center; background-color: #1A1A1A; border-radius: 5px; margin-bottom: 15px;'><h1 style='margin:0; font-size: 5em;'>👤</h1></div>", unsafe_allow_html=True)
                                
                                st.markdown(f"<h2 style='text-align: center; color: #E0E0E0; margin-bottom: 5px;'>{destaque.get('name')}</h2>", unsafe_allow_html=True)
                                
                                if destaque.get("oab"):
                                    st.markdown(f"<p style='text-align: center; font-size: 1.1em; margin-bottom: 0;'>OAB: {destaque.get('oab')}</p>", unsafe_allow_html=True)
                                
                                # Aniversário formatado
                                if destaque.get("data_nascimento"):
                                    try:
                                        dt_obj = datetime.strptime(destaque.get("data_nascimento"), "%Y-%m-%d")
                                        st.markdown(f"<p style='text-align: center; font-size: 1.1em; margin-bottom: 0; color: #D4AF37;'>🎂 Aniversário: {dt_obj.strftime('%d/%m')}</p>", unsafe_allow_html=True)
                                    except: pass
                                
                                if destaque.get("observacoes_pessoais"):
                                    st.write("")
                                    st.info(destaque.get("observacoes_pessoais"))
                        
                        st.markdown("---")

                    if outros:
                        if destaque:
                            st.subheader("👥 Demais Integrantes da Equipe")
                            
                        cols = st.columns(4)
                        for i, u in enumerate(outros):
                            col = cols[i % 4]
                            with col:
                                with st.container(border=True):
                                    foto = u.get("foto_url")
                                    if foto:
                                        st.markdown(f"""
                                            <div style='width: 100%; height: 220px; overflow: hidden; border-radius: 5px; margin-bottom: 10px;'>
                                                <img src='{foto}' style='width: 100%; height: 100%; object-fit: cover;'>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div style='width: 100%; height: 220px; display: flex; align-items: center; justify-content: center; background-color: #1A1A1A; border-radius: 5px; margin-bottom: 10px;'><h1 style='margin:0; font-size: 4em;'>👤</h1></div>", unsafe_allow_html=True)
                                    
                                    st.markdown(f"<h4 style='text-align: center; color: #D4AF37; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{u.get('name')}</h4>", unsafe_allow_html=True)
                                    
                                    if u.get("oab"):
                                        st.markdown(f"<p style='text-align: center; font-size: 0.9em; margin-bottom: 5px;'>OAB: {u.get('oab')}</p>", unsafe_allow_html=True)
                                        
                                    # Aniversário na grade
                                    if u.get("data_nascimento"):
                                        try:
                                            dt_obj = datetime.strptime(u.get("data_nascimento"), "%Y-%m-%d")
                                            st.markdown(f"<p style='text-align: center; font-size: 0.9em; margin-bottom: 5px; color: #D4AF37;'>🎂 Aniversário: {dt_obj.strftime('%d/%m')}</p>", unsafe_allow_html=True)
                                        except: pass
                                    
                                    if u.get("observacoes_pessoais"):
                                        st.write("")
                                        with st.expander("Ver perfil detalhado"):
                                            st.write(u.get("observacoes_pessoais"))

        elif menu_principal == "Segurança":
            if sub == "Meu Perfil":
                st.header("👤 Meu Perfil de Usuário")
                st.caption(f"Gerencie suas informações pessoais e envie sua foto de perfil diretamente do seu computador ou celular ({username}).")
                
                col_pf1, col_pf2 = st.columns([1, 2])
                
                with col_pf1:
                    if user_info.get("foto_url"):
                        st.markdown(f"""
                            <div style='width: 100%; max-width: 300px; margin: 0 auto; height: 300px; border-radius: 10px; overflow: hidden; border: 2px solid #333;'>
                                <img src='{user_info.get("foto_url")}' style='width: 100%; height: 100%; object-fit: cover;'>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("Sem foto cadastrada.")
                
                with col_pf2:
                    with st.form("form_meu_perfil"):
                        p_nome = st.text_input("Nome Completo", value=user_info.get("name", ""))
                        p_tel = st.text_input("Telefone de Contato", value=user_info.get("telefone", ""))
                        p_oab = st.text_input("Registro OAB / Identificação Profissional", value=user_info.get("oab", ""))
                        
                        # Processando Data de Nascimento atual
                        dt_nasc_atual = user_info.get("data_nascimento")
                        if dt_nasc_atual:
                            try:
                                val_data = datetime.strptime(dt_nasc_atual, "%Y-%m-%d").date()
                            except:
                                val_data = None
                        else:
                            val_data = None
                        
                        p_nasc = st.date_input("Data de Nascimento", value=val_data, min_value=date(1920, 1, 1), max_value=date.today(), format="DD/MM/YYYY")
                        
                        file_foto = st.file_uploader("Escolher Foto do Computador ou Celular (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
                        
                        p_obs = st.text_area("Observações Pessoais (Minicurrículo, Gostos, etc.)", value=user_info.get("observacoes_pessoais", ""))
                        
                        if st.form_submit_button("Salvar Alterações no Perfil", type="primary"):
                            if username == "master":
                                st.warning("A conta Master de emergência não altera perfil no banco.")
                            else:
                                try:
                                    foto_final = user_info.get("foto_url")
                                    if file_foto is not None:
                                        foto_final = converter_imagem_base64(file_foto)
                                    
                                    # Pega a data formatada, ou None se estiver vazia
                                    str_nasc = p_nasc.strftime("%Y-%m-%d") if p_nasc else None

                                    supabase.table("usuarios_sistema").update({
                                        "nome_completo": p_nome,
                                        "name": p_nome,
                                        "telefone": p_tel,
                                        "oab": p_oab,
                                        "data_nascimento": str_nasc,
                                        "foto_url": foto_final,
                                        "observacoes_pessoais": p_obs
                                    }).eq("username", username).execute()
                                    
                                    registrar_auditoria(username, "Atualizar Perfil", "Segurança", "Dados de perfil (incluindo nascimento e foto) atualizados.")
                                    st.cache_data.clear()
                                    st.success("✅ Perfil atualizado com sucesso!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar perfil no banco de dados: {e}")

            elif sub == "Alterar Senha":
                st.header("🔐 Alterar Minha Senha")
                st.caption(f"Alterando senha para o usuário atual: **{username}**")
                with st.form("form_alt_senha"):
                    nova_senha = st.text_input("Nova Senha", type="password")
                    conf_senha = st.text_input("Confirmar Nova Senha", type="password")
                    if st.form_submit_button("Atualizar Minha Senha"):
                        if not nova_senha or nova_senha != conf_senha:
                            st.error("As senhas não coincidem ou estão vazias.")
                        elif username == 'master':
                            st.error("A conta Master de emergência não pode ser alterada.")
                        else:
                            novo_hash = gerar_hash(nova_senha)
                            try:
                                supabase.table("usuarios_sistema").update({"senha_hash": novo_hash, "password": novo_hash}).eq("username", username).execute()
                                registrar_auditoria(username, "Alterar Senha", "Segurança", f"Usuário {username} alterou a própria senha.")
                                st.cache_data.clear()
                                st.success("✅ Senha alterada com sucesso na nuvem! Faça login novamente com a nova senha.")
                            except Exception as e:
                                st.error(f"Erro ao atualizar senha no banco: {e}")

            elif sub == "Cadastrar Novo Usuário" and user_role == 'admin':
                st.header("➕ Cadastrar Novo Usuário no Sistema")
                with st.form("form_cad_user", clear_on_submit=True):
                    new_user = st.text_input("Nome de Usuário (login sem espaços, ex: joao)")
                    new_name = st.text_input("Nome Completo")
                    new_pass = st.text_input("Senha Inicial", type="password")
                    
                    perfis_opcoes = {
                        "👑 Sócio / Administrador": "admin",
                        "⚖️ Advogado(a)": "advogado",
                        "📜 Bacharel(a)": "bacharel",
                        "🎓 Estagiário(a)": "estagiario"
                    }
                    sel_perfil_label = st.selectbox("Perfil de Acesso", list(perfis_opcoes.keys()))
                    new_role = perfis_opcoes[sel_perfil_label]
                    
                    if st.form_submit_button("Cadastrar Usuário"):
                        if not new_user or not new_name or not new_pass:
                            st.error("Preencha todos os campos obrigatórios.")
                        else:
                            senha_hash = gerar_hash(new_pass)
                            try:
                                try:
                                    supabase.table("usuarios_sistema").insert({
                                        "username": new_user.strip().lower(),
                                        "nome_completo": new_name,
                                        "name": new_name,
                                        "senha_hash": senha_hash,
                                        "password": senha_hash,
                                        "role": new_role,
                                        "trocar_senha": True
                                    }).execute()
                                except Exception:
                                    supabase.table("usuarios_sistema").insert({
                                        "username": new_user.strip().lower(),
                                        "nome_completo": new_name,
                                        "name": new_name,
                                        "senha_hash": senha_hash,
                                        "password": senha_hash,
                                        "role": new_role
                                    }).execute()
                                    
                                registrar_auditoria(username, "Cadastrar Usuário", "Segurança", f"Novo usuário criado: {new_user} ({new_role})")
                                st.cache_data.clear()
                                st.session_state['cad_user_sucesso'] = True
                            except Exception as e:
                                st.error(f"Erro ao cadastrar usuário (verifique se o login já existe na tabela): {e}")

                if st.session_state.get('cad_user_sucesso'):
                    st.success("🎉 Usuário cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Usuário", key="btn_novo_user", type="primary", use_container_width=True):
                            st.session_state['cad_user_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_user", use_container_width=True):
                            st.session_state['cad_user_sucesso'] = False
                            st.session_state['submenu_atual'] = "Gerenciar Usuários"
                            st.rerun()

            elif sub == "Gerenciar Usuários" and user_role == 'admin':
                st.header("🛡️ Gerenciamento de Usuários Ativos")
                try:
                    res_users = supabase.table("usuarios_sistema").select("*").execute()
                    if res_users.data:
                        df_u = pd.DataFrame(res_users.data)
                        colunas_visiveis = [c for c in ['id', 'username', 'nome_completo', 'name', 'role', 'trocar_senha', 'telefone', 'oab'] if c in df_u.columns]
                        st.dataframe(df_u[colunas_visiveis], use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        st.subheader("🗑️ Excluir Usuário (Para resetar)")
                        udict = {f"{u['username']} (ID: {u['id']})": u['id'] for u in res_users.data}
                        if udict:
                            sel_del = st.selectbox("Selecione o usuário:", list(udict.keys()))
                            if st.checkbox("Confirmo a exclusão permanente deste usuário.") and st.button("EXCLUIR USUÁRIO SELECIONADO", type="primary"):
                                uid_del = udict[sel_del]
                                supabase.table("usuarios_sistema").delete().eq("id", uid_del).execute()
                                registrar_auditoria(username, "Excluir Usuário", "Segurança", f"Usuário ID {uid_del} excluído.")
                                st.cache_data.clear()
                                st.success("Usuário excluído com sucesso!")
                                st.rerun()
                        else:
                            st.info("Nenhum usuário no banco.")
                    else:
                        st.info("O banco de dados de usuários está vazio. Use a aba 'Cadastrar Novo Usuário' para adicionar seu login oficial.")
                except Exception as e:
                    st.error(f"Erro ao carregar usuários: {e}")

        elif menu_principal == "Clientes":
            if sub == "Cadastrar Cliente":
                st.header("👤 Cadastro Completo de Cliente")
                with st.form("fc_cli", clear_on_submit=True):
                    n, doc, tel, email, end, cid, gov, ind, obs = st.text_input("Nome *"), st.text_input("CPF/CNPJ"), st.text_input("Telefone"), st.text_input("E-mail"), st.text_input("Endereço"), st.text_input("Cidade/UF"), st.text_input("Senha Gov.br"), st.text_input("Indicado Por"), st.text_area("Observações")
                    
                    col_b_cad, col_b_vol = st.columns(2)
                    with col_b_cad:
                        salvar_cli = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_b_vol:
                        voltar_cli = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_cli:
                        if not n: st.error("O campo Nome é obrigatório.")
                        else:
                            doc_l = ''.join(filter(str.isdigit, str(doc)))
                            if len(doc_l) == 11 and not validar_cpf(doc_l): st.error("CPF Inválido!")
                            else:
                                supabase.table("clientes_cadastrados").insert({"nome": n, "cpf_cnpj": doc, "telefone": tel, "email": email, "endereco": end, "cidade": cid, "senha_gov": gov, "indicado_por": ind, "observacoes": obs}).execute()
                                registrar_auditoria(username, "Cadastrar Cliente", "Clientes", f"Cliente: {n}")
                                st.cache_data.clear()
                                st.session_state['cad_cli_sucesso'] = True
                                st.rerun()
                    if voltar_cli:
                        st.session_state['submenu_atual'] = "Consultar Clientes"
                        st.rerun()

                if st.session_state.get('cad_cli_sucesso'):
                    st.success("🎉 Cliente cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Cliente", key="btn_novo_cli", type="primary", use_container_width=True):
                            st.session_state['cad_cli_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Base de Clientes", key="btn_vol_cli", use_container_width=True):
                            st.session_state['cad_cli_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Clientes"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Clientes via Planilha Excel")
                st.caption("O arquivo deve conter as colunas: nome, cpf_cnpj, telefone, email, endereco, cidade, senha_gov, indicado_por, observacoes")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_cli")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("clientes_cadastrados", file_up)
            elif sub == "Consultar Clientes":
                st.header("📋 Base de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res: 
                    df_cli = pd.DataFrame(res)
                    st.dataframe(df_cli, use_container_width=True, hide_index=True)
                else: st.info("Nenhum cliente cadastrado.")
            elif sub == "Editar Cliente":
                st.header("✏️ Editar Cliente")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    cdict = {f"ID: {c['id']} — {c['nome']}": c for c in res}
                    sel = st.selectbox("Cliente:", list(cdict.keys()))
                    obj = cdict[sel]
                    with st.form("fe_cli"):
                        en, edoc, etel, eemail, eend, ecid, egov, eind, eobs = st.text_input("Nome", value=obj.get('nome','')), st.text_input("CPF/CNPJ", value=obj.get('cpf_cnpj','')), st.text_input("Telefone", value=obj.get('telefone','')), st.text_input("E-mail", value=obj.get('email','')), st.text_input("Endereço", value=obj.get('endereco','')), st.text_input("Cidade", value=obj.get('cidade','')), st.text_input("Gov.br", value=obj.get('senha_gov','')), st.text_input("Indicação", value=obj.get('indicado_por','')), st.text_area("Obs", value=obj.get('observacoes',''))
                        
                        col_e1, col_e2 = st.columns(2)
                        with col_e1:
                            atualizar_cli = st.form_submit_button("Atualizar", type="primary", use_container_width=True)
                        with col_e2:
                            voltar_ed_cli = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if atualizar_cli:
                            supabase.table("clientes_cadastrados").update({"nome": en, "cpf_cnpj": edoc, "telefone": etel, "email": eemail, "endereco": eend, "cidade": ecid, "senha_gov": egov, "indicado_por": eind, "observacoes": eobs}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Cliente", "Clientes", f"ID: {obj['id']} - {en}")
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                        if voltar_ed_cli:
                            st.session_state['submenu_atual'] = "Consultar Clientes"
                            st.rerun()
                else: st.info("Nenhum cliente.")
            elif sub == "Excluir Cliente" and user_role == 'admin':
                st.header("🗑️ Excluir Cliente")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    cdict = {f"ID: {c['id']} — {c['nome']}": c['id'] for c in res}
                    sel = st.selectbox("Cliente:", list(cdict.keys()))
                    if st.checkbox("Confirmo exclusão permanente deste cliente.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("clientes_cadastrados").delete().eq("id", cdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Cliente", "Clientes", f"ID: {cdict[sel]}")
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()
                    
                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de toda a base de clientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os registros de clientes do sistema."):
                        if st.button("🔥 EXCLUIR TODOS OS CLIENTES", type="primary"):
                            supabase.table("clientes_cadastrados").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS CLIENTES", "Clientes", "Exclusão em massa executada.")
                            st.cache_data.clear(); st.success("Todos os registros foram excluídos com sucesso!"); st.rerun()
                else: st.info("Nenhum cliente cadastrado.")
            elif sub == "Exportar Base (Backup)":
                st.header("📥 Backup de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    registrar_auditoria(username, "Backup Clientes", "Clientes", "Download da base realizado.")
                    st.download_button("Baixar CSV", data=pd.DataFrame(res).to_csv(index=False).encode('utf-8'), file_name=f"clientes_{date.today()}.csv", mime="text/csv", type="primary")
                else: st.info("Sem dados.")

        elif menu_principal == "Pagamentos":
            if sub == "Cadastrar Contrato":
                st.header("📝 Novo Contrato e Parcelamento")
                cli_db = carregar_dados("clientes_cadastrados")
                nomes = [c['nome'] for c in cli_db]
                with st.form("fc_hon", clear_on_submit=True):
                    cli_op = st.selectbox("Cliente:", ["Outro"] + nomes) if nomes else "Outro"
                    cli = st.text_input("Nome") if cli_op == "Outro" else cli_op
                    serv = st.text_input("Serviço")
                    vtot = st.number_input("Valor Total do Contrato (R$)", min_value=0.0, step=100.0)
                    
                    col_e1, col_e2 = st.columns(2)
                    with col_e1:
                        v_entrada = st.number_input("Valor de Entrada (R$)", min_value=0.0, step=50.0, value=0.0)
                    with col_e2:
                        npar = st.number_input("Quantidade de Parcelas (Restante)", min_value=1, max_value=36, value=3)
                    
                    dt1 = st.date_input("Vencimento da 1ª Parcela (ou Entrada)", datetime.now())
                    
                    col_b_h1, col_b_h2 = st.columns(2)
                    with col_b_h1:
                        salvar_hon = st.form_submit_button("Gerar Contrato e Parcelas", type="primary", use_container_width=True)
                    with col_b_h2:
                        voltar_hon = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_hon:
                        if not cli or not serv or vtot <= 0:
                            st.error("Preencha o cliente, o serviço e um valor total válido.")
                        elif v_entrada > vtot:
                            st.error("O valor da entrada não pode ser maior que o valor total do contrato.")
                        else:
                            res = supabase.table("honorarios").insert({"cliente": cli, "servico": serv, "valor_total": float(vtot)}).execute()
                            if res.data:
                                h_id = res.data[0]['id']
                                saldo_restante = vtot - v_entrada
                                
                                if v_entrada > 0:
                                    supabase.table("parcelas").insert({
                                        "honorario_id": h_id, 
                                        "numero_parcela": "Entrada", 
                                        "valor": float(v_entrada), 
                                        "vencimento": dt1.strftime("%Y-%m-%d"), 
                                        "status": "Pendente"
                                    }).execute()
                                    data_primeira_parcela = dt1 + relativedelta(months=1)
                                else:
                                    data_primeira_parcela = dt1

                                if npar > 0 and saldo_restante > 0:
                                    vp = saldo_restante / npar
                                    for i in range(int(npar)):
                                        venc = (data_primeira_parcela + relativedelta(months=i)).strftime("%Y-%m-%d")
                                        supabase.table("parcelas").insert({
                                            "honorario_id": h_id, 
                                            "numero_parcela": f"{i+1}/{int(npar)}", 
                                            "valor": float(vp), 
                                            "vencimento": venc, 
                                            "status": "Pendente"
                                        }).execute()

                                registrar_auditoria(username, "Cadastrar Contrato com Entrada", "Pagamentos", f"Cliente: {cli} - Total: R$ {vtot}")
                                st.cache_data.clear()
                                st.session_state['cad_hon_sucesso'] = True
                                st.rerun()
                    if voltar_hon:
                        st.session_state['submenu_atual'] = "Ver Parcelas"
                        st.rerun()

                if st.session_state.get('cad_hon_sucesso'):
                    st.success("🎉 Contrato e parcelas gerados com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Contrato", key="btn_novo_hon", type="primary", use_container_width=True):
                            st.session_state['cad_hon_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Parcelas", key="btn_vol_hon", use_container_width=True):
                            st.session_state['cad_hon_sucesso'] = False
                            st.session_state['submenu_atual'] = "Ver Parcelas"
                            st.rerun()

            elif sub == "Ver Parcelas":
                st.header("📋 Visualizar Parcelas")
                res_h = carregar_dados("honorarios")
                if res_h:
                    cdict = {f"{h['cliente']} — {h['servico']} (Total: R$ {h.get('valor_total', 0)})": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(cdict.keys()))
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel]).execute()
                    if res_p.data: 
                        df_p = pd.DataFrame(res_p.data)
                        if 'status' in df_p.columns:
                            st.dataframe(df_p.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                        else:
                            st.dataframe(df_p, use_container_width=True, hide_index=True)
                    else: st.info("Sem parcelas.")
                else: st.info("Sem contratos.")

            elif sub == "Baixar Parcela" and user_role == 'admin':
                st.header("💰 Baixar Parcela e Calcular Rateio")
                
                res_h = carregar_dados("honorarios")
                if not res_h:
                    st.info("Nenhum contrato cadastrado.")
                else:
                    cdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel_contrato = st.selectbox("1. Selecione o Contrato:", list(cdict.keys()))
                    
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel_contrato]).eq("status", "Pendente").execute()
                    if not res_p.data:
                        st.success("✅ Este contrato não possui parcelas pendentes.")
                    else:
                        parcelas_pendentes = {f"Parcela: {p['numero_parcela']} — R$ {p['valor']} (Venc: {p['vencimento']})": p for p in res_p.data}
                        sel_parcela_str = st.selectbox("2. Selecione a Parcela a Baixar:", list(parcelas_pendentes.keys()))
                        parcela_obj = parcelas_pendentes[sel_parcela_str]
                        valor_bruto = float(parcela_obj['valor'])
                        
                        st.markdown("---")
                        
                        lista_usuarios = []
                        for u in credentials['usernames'].values():
                            nome_u = u.get('name', '')
                            papel_u = u.get('role', 'estagiario')
                            if nome_u:
                                lista_usuarios.append({"nome": nome_u, "papel": papel_u})
                        
                        nomes_opcoes = [u['nome'] for u in lista_usuarios]

                        is_entrada = (parcela_obj['numero_parcela'] == "Entrada")
                        
                        if is_entrada:
                            st.subheader("⚙️ Regra de Entrada (Com Prospecção)")
                            st.info("O sistema detectou que esta é a **Entrada** do contrato. A regra completa será aplicada (prospectador, 5% colaboradores e operador).")
                            
                            col_r1, col_r2 = st.columns(2)
                            with col_r1:
                                prosp_name = st.selectbox("👤 Prospectador:", ["Nenhum / Sem Prospectador", "Prospectador Externo"] + nomes_opcoes)
                            with col_r2:
                                resp_name = st.selectbox("⚖️ Operador (Trabalhou no Processo):", nomes_opcoes)
                            
                            val_prosp_input = 0.0
                            if prosp_name not in ["Nenhum / Sem Prospectador", resp_name]:
                                val_prosp_input = st.number_input("💵 Valor de Captação deliberado (R$):", min_value=0.0, step=10.0, max_value=valor_bruto)
                            elif prosp_name == resp_name:
                                st.warning("📌 **Acúmulo Detectado:** O Prospectador e Operador são os mesmos. A comissão incidirá direto no bruto.")

                            resp_role = "estagiario"
                            for u in lista_usuarios:
                                if u['nome'] == resp_name:
                                    resp_role = u['papel']
                                    break
                                    
                        else:
                            st.subheader("⚙️ Regra de Parcela Normal (Sem Prospecção)")
                            st.info("O sistema detectou que esta é uma **Parcela Normal**. A prospecção e os 5% não se aplicam aqui. O valor será dividido apenas entre o Operador e os Sócios.")
                            
                            resp_name = st.selectbox("⚖️ Operador (Trabalhou no Processo):", nomes_opcoes)
                            val_op_input = st.number_input("💵 Valor do Operador avaliado no ato (R$):", min_value=0.0, max_value=valor_bruto, step=50.0)

                        # --- CÁLCULO E PROVA REAL EM TEMPO REAL ---
                        val_prospectador = 0.0
                        val_operador = 0.0
                        fundo_colab = 0.0
                        val_leonidas = 0.0
                        val_nelson = 0.0
                        
                        if is_entrada:
                            saldo = valor_bruto
                            regra_aplicada = "Entrada"
                            
                            if prosp_name == resp_name:
                                regra_aplicada = "Entrada (Acúmulo)"
                                taxa = 0.60 if resp_role in ['admin', 'advogado'] else 0.40
                                val_operador = round(valor_bruto * taxa, 2)
                                val_prospectador = val_operador
                                saldo -= val_operador
                                
                                if valor_bruto > 1000.0:
                                    fundo_colab = round(saldo * 0.05, 2)
                                    saldo -= fundo_colab
                                    
                                val_leonidas = round(saldo * 0.60, 2)
                                val_nelson = round(saldo * 0.40, 2)
                                
                            else:
                                if prosp_name != "Nenhum / Sem Prospectador":
                                    val_prospectador = round(val_prosp_input, 2)
                                
                                saldo -= val_prospectador
                                
                                if saldo > 1000.0:
                                    fundo_colab = round(saldo * 0.05, 2)
                                    saldo -= fundo_colab
                                    
                                taxa_op = 0.25 if resp_role in ['admin', 'advogado'] else (0.15 if resp_role == 'bacharel' else 0.10)
                                val_operador = round(saldo * taxa_op, 2)
                                saldo -= val_operador
                                
                                val_leonidas = round(saldo * 0.60, 2)
                                val_nelson = round(saldo * 0.40, 2)
                        else:
                            regra_aplicada = "Parcela Normal"
                            prosp_name = "N/A"
                            val_operador = round(val_op_input, 2)
                            saldo_socios = valor_bruto - val_operador
                            val_leonidas = round(saldo_socios * 0.60, 2)
                            val_nelson = round(saldo_socios * 0.40, 2)

                        # Ajuste de resíduo de centavos no sócio majoritário para fechar prova 100%
                        val_prosp_efetivo = 0.0 if "Acúmulo" in regra_aplicada else (val_prospectador if is_entrada and prosp_name != "Nenhum / Sem Prospectador" else 0.0)
                        soma_distribuida = round(val_prosp_efetivo + val_operador + fundo_colab + val_leonidas + val_nelson, 2)
                        diferenca = round(valor_bruto - soma_distribuida, 2)

                        if diferenca != 0:
                            val_leonidas = round(val_leonidas + diferenca, 2)
                            soma_distribuida = round(val_prosp_efetivo + val_operador + fundo_colab + val_leonidas + val_nelson, 2)
                            diferenca = round(valor_bruto - soma_distribuida, 2)

                        # --- PAINEL VISUAL DE PROVA REAL ---
                        st.markdown("#### 🧮 Prova Real do Rateio (Validação Entrada vs Saída)")
                        col_pr1, col_pr2, col_pr3 = st.columns(3)
                        col_pr1.metric("Recurso Bruto de Entrada", f"R$ {valor_bruto:.2f}")
                        col_pr2.metric("Soma Total Distribuída", f"R$ {soma_distribuida:.2f}")
                        
                        if diferenca == 0:
                            col_pr3.success("✅ **PROVA OK!**\nSoma 100% idêntica ao valor de entrada.")
                        else:
                            col_pr3.error(f"⚠️ **DIVERGÊNCIA:** Δ R$ {diferenca:.2f}")

                        with st.expander("🔍 Detalhamento dos Valores da Prova Real", expanded=True):
                            det_cols = st.columns(5)
                            det_cols[0].write(f"**Prospectador:**\nR$ {val_prosp_efetivo:.2f}")
                            det_cols[1].write(f"**Operador:**\nR$ {val_operador:.2f}")
                            det_cols[2].write(f"**Fundo Colab.:**\nR$ {fundo_colab:.2f}")
                            det_cols[3].write(f"**Leônidas (60%):**\nR$ {val_leonidas:.2f}")
                            det_cols[4].write(f"**Nelson (40%):**\nR$ {val_nelson:.2f}")

                        if st.button("Confirmar Baixa e Gerar Repasse", type="primary"):
                            repasse_dict = {
                                "parcela_id": parcela_obj['id'],
                                "contrato": sel_contrato,
                                "regra": regra_aplicada,
                                "valor_bruto": round(valor_bruto, 2),
                                "prospectador": prosp_name,
                                "valor_prospectador": round(val_prospectador, 2),
                                "operador": resp_name,
                                "papel_operador": resp_role if is_entrada else "N/A",
                                "valor_operador": round(val_operador, 2),
                                "fundo_colab": round(fundo_colab, 2),
                                "leonidas": round(val_leonidas, 2),
                                "nelson": round(val_nelson, 2),
                                "soma_distribuida": round(soma_distribuida, 2),
                                "prova_real_ok": True if diferenca == 0 else False,
                                "data_baixa": date.today().strftime("%Y-%m-%d")
                            }
                            json_repasse = json.dumps(repasse_dict, ensure_ascii=False)
                            
                            try:
                                supabase.table("parcelas").update({"status": "Pago"}).eq("id", parcela_obj['id']).execute()
                                registrar_auditoria(username, "Baixa e Rateio", "Repasses", json_repasse)
                                st.cache_data.clear()
                                st.success("✅ Parcela baixada e repasse validado com sucesso! Consulte o Extrato de Repasses.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao processar baixa: {e}")

            elif sub == "Extrato de Repasses" and user_role == 'admin':
                st.header("📊 Extrato Geral de Repasses (Fee Splitting)")
                st.caption("Visão financeira completa sobre a divisão de honorários das parcelas baixadas com Prova Real Auditada.")
                
                try:
                    res_rep = supabase.table("logs_auditoria").select("*").eq("modulo", "Repasses").order("data_hora", desc=True).execute()
                    if not res_rep.data:
                        st.info("Nenhum repasse registrado ainda.")
                    else:
                        linhas = []
                        total_bruto_acum = 0.0
                        total_dist_acum = 0.0
                        provas_validas = 0
                        total_registros = 0

                        for log in res_rep.data:
                            try:
                                r = json.loads(log['detalhes'])
                                val_bruto = float(r.get('valor_bruto', 0))
                                val_prosp_exib = float(r.get('valor_prospectador', 0))
                                val_op_exib = float(r.get('valor_operador', 0))
                                fundo_exib = float(r.get('fundo_colab', 0))
                                leo_exib = float(r.get('leonidas', 0))
                                nel_exib = float(r.get('nelson', 0))
                                
                                if "Acúmulo" in r.get('regra', ''):
                                    val_prosp_efetivo = 0.0
                                else:
                                    val_prosp_efetivo = val_prosp_exib if r.get('prospectador') not in ["Nenhum / Sem Prospectador", "N/A", ""] else 0.0

                                soma_dist = round(val_prosp_efetivo + val_op_exib + fundo_exib + leo_exib + nel_exib, 2)
                                dif = round(val_bruto - soma_dist, 2)
                                is_ok = (abs(dif) < 0.01)

                                total_registros += 1
                                if is_ok: provas_validas += 1
                                total_bruto_acum += val_bruto
                                total_dist_acum += soma_dist

                                linhas.append({
                                    "Data": datetime.strptime(log['data_hora'][:10], "%Y-%m-%d").strftime("%d/%m/%Y"),
                                    "Tipo Regra": r.get('regra', 'N/D'),
                                    "Contrato": r.get('contrato', '').split(' — ')[0],
                                    "Valor Bruto": f"R$ {val_bruto:.2f}",
                                    "Fundo Colab.": f"R$ {fundo_exib:.2f}",
                                    "Prospectador": r.get('prospectador', ''),
                                    "Val. Prospector": f"R$ {val_prosp_exib if 'Acúmulo' not in r.get('regra','') else 0.0:.2f}",
                                    "Operador": r.get('operador', ''),
                                    "Val. Operador": f"R$ {val_op_exib:.2f}",
                                    "Leônidas (60%)": f"R$ {leo_exib:.2f}",
                                    "Nelson (40%)": f"R$ {nel_exib:.2f}",
                                    "Soma Distribuída": f"R$ {soma_dist:.2f}",
                                    "Prova Real": "✅ 100% Batido" if is_ok else f"⚠️ Δ R$ {dif:.2f}"
                                })
                            except Exception:
                                pass
                        
                        if linhas:
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Total Entrado (Bruto)", f"R$ {total_bruto_acum:.2f}")
                            m2.metric("Total Repassado (Soma)", f"R$ {total_dist_acum:.2f}")
                            pct_audit = (provas_validas / total_registros * 100) if total_registros > 0 else 100
                            m3.metric("Auditoria Prova Real", f"{pct_audit:.0f}% OK ({provas_validas}/{total_registros})")

                            st.markdown("---")
                            df_rep = pd.DataFrame(linhas)
                            st.dataframe(df_rep, use_container_width=True, hide_index=True)
                            
                            st.download_button(
                                label="📥 Exportar Extrato Com Prova Real (CSV)",
                                data=df_rep.to_csv(index=False).encode('utf-8'),
                                file_name=f"extrato_repasses_provareal_{date.today()}.csv",
                                mime="text/csv",
                                type="primary"
                            )
                        else:
                            st.info("Nenhum dado formatado para exibição.")
                except Exception as e:
                    st.error(f"Erro ao carregar extratos: {e}")

            elif sub == "Relatório por Período" and user_role == 'admin':
                st.header("📅 Relatório Financeiro de Pagamentos por Período")
                st.caption("Gere balancetes e relatórios detalhados de entradas e divisões de honorários com base no intervalo de datas desejado.")
                
                hoje_dt = date.today()
                primeiro_dia_mes = hoje_dt.replace(day=1)

                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    dt_inicio = st.date_input("Data Inicial", value=primeiro_dia_mes)
                with col_f2:
                    dt_fim = st.date_input("Data Final", value=hoje_dt)
                with col_f3:
                    lista_usuarios_rel = ["Todos os Colaboradores / Sócios"]
                    for u in credentials['usernames'].values():
                        n_user = u.get('name', '')
                        if n_user and n_user not in lista_usuarios_rel:
                            lista_usuarios_rel.append(n_user)
                    filtro_pessoa = st.selectbox("Filtrar por Pessoa:", lista_usuarios_rel)

                if dt_inicio > dt_fim:
                    st.error("A Data Inicial não pode ser posterior à Data Final.")
                else:
                    try:
                        res_rep = supabase.table("logs_auditoria").select("*").eq("modulo", "Repasses").order("data_hora", desc=True).execute()
                        if not res_rep.data:
                            st.info("Nenhum registro de repasse encontrado no banco de dados.")
                        else:
                            linhas_relatorio = []
                            
                            sum_bruto = 0.0
                            sum_prosp = 0.0
                            sum_op = 0.0
                            sum_fundo = 0.0
                            sum_leonidas = 0.0
                            sum_nelson = 0.0
                            sum_distribuido = 0.0
                            count_provas_ok = 0

                            for log in res_rep.data:
                                try:
                                    r = json.loads(log['detalhes'])
                                    dt_baixa_str = r.get('data_baixa', log['data_hora'][:10])
                                    dt_baixa_obj = datetime.strptime(dt_baixa_str, "%Y-%m-%d").date()

                                    # Filtro por período
                                    if dt_inicio <= dt_baixa_obj <= dt_fim:
                                        prosp = r.get('prospectador', '')
                                        op = r.get('operador', '')
                                        
                                        # Filtro por pessoa (caso selecionado)
                                        if filtro_pessoa != "Todos os Colaboradores / Sócios":
                                            if filtro_pessoa not in [prosp, op, "Leônidas", "Nelson"]:
                                                continue

                                        v_bruto = float(r.get('valor_bruto', 0))
                                        v_prosp_raw = float(r.get('valor_prospectador', 0))
                                        v_op = float(r.get('valor_operador', 0))
                                        v_fundo = float(r.get('fundo_colab', 0))
                                        v_leo = float(r.get('leonidas', 0))
                                        v_nel = float(r.get('nelson', 0))

                                        v_prosp_efetivo = 0.0 if "Acúmulo" in r.get('regra', '') else (v_prosp_raw if prosp not in ["Nenhum / Sem Prospectador", "N/A", ""] else 0.0)
                                        soma_d = round(v_prosp_efetivo + v_op + v_fundo + v_leo + v_nel, 2)
                                        is_ok = abs(v_bruto - soma_d) < 0.01

                                        if is_ok: count_provas_ok += 1
                                        sum_bruto += v_bruto
                                        sum_prosp += v_prosp_efetivo
                                        sum_op += v_op
                                        sum_fundo += v_fundo
                                        sum_leonidas += v_leo
                                        sum_nelson += v_nel
                                        sum_distribuido += soma_d

                                        linhas_relatorio.append({
                                            "Data Baixa": dt_baixa_obj.strftime("%d/%m/%Y"),
                                            "Contrato / Cliente": r.get('contrato', '').split(' — ')[0],
                                            "Regra Aplicada": r.get('regra', 'N/D'),
                                            "Valor Bruto": f"R$ {v_bruto:.2f}",
                                            "Prospectador": f"{prosp} (R$ {v_prosp_efetivo:.2f})" if v_prosp_efetivo > 0 else (prosp if prosp else "-"),
                                            "Operador": f"{op} (R$ {v_op:.2f})",
                                            "Fundo Colab. (5%)": f"R$ {v_fundo:.2f}",
                                            "Leônidas (60%)": f"R$ {v_leo:.2f}",
                                            "Nelson (40%)": f"R$ {v_nel:.2f}",
                                            "Total Distribuído": f"R$ {soma_d:.2f}",
                                            "Prova Real": "✅ 100% Batido" if is_ok else "⚠️ Divergente"
                                        })
                                except Exception:
                                    pass

                            st.markdown("---")
                            st.subheader(f"📊 Resumo Financeiro do Período ({dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')})")
                            
                            c_rel1, c_rel2, c_rel3, c_rel4 = st.columns(4)
                            c_rel1.metric("Faturamento Bruto Entrado", f"R$ {sum_bruto:.2f}")
                            c_rel2.metric("Total Sócios (60/40)", f"R$ {(sum_leonidas + sum_nelson):.2f}")
                            c_rel3.metric("Total Operadores & Prospectores", f"R$ {(sum_op + sum_prosp):.2f}")
                            c_rel4.metric("Fundo Colaboradores (5%)", f"R$ {sum_fundo:.2f}")

                            with st.expander("👑 Divisão Detalhada dos Sócios no Período", expanded=True):
                                c_s1, c_s2, c_s3 = st.columns(3)
                                c_s1.metric("Leônidas (60%)", f"R$ {sum_leonidas:.2f}")
                                c_s2.metric("Nelson (40%)", f"R$ {sum_nelson:.2f}")
                                total_rel_regs = len(linhas_relatorio)
                                pct_rel_ok = (count_provas_ok / total_rel_regs * 100) if total_rel_regs > 0 else 100
                                c_s3.metric("Validação de Prova Real", f"{pct_rel_ok:.0f}% OK ({count_provas_ok}/{total_rel_regs})")

                            st.markdown("---")
                            st.subheader("📝 Lista Detalhada dos Pagamentos Processados")
                            
                            if linhas_relatorio:
                                df_rel = pd.DataFrame(linhas_relatorio)
                                st.dataframe(df_rel, use_container_width=True, hide_index=True)
                                
                                nome_arquivo = f"relatorio_pagamentos_{dt_inicio.strftime('%Y%m%d')}_a_{dt_fim.strftime('%Y%m%d')}.csv"
                                st.download_button(
                                    label="📥 Baixar Relatório Completo (CSV)",
                                    data=df_rel.to_csv(index=False).encode('utf-8'),
                                    file_name=nome_arquivo,
                                    mime="text/csv",
                                    type="primary"
                                )
                            else:
                                st.warning("Nenhum registro de pagamento encontrado para os filtros selecionados.")
                    except Exception as e:
                        st.error(f"Erro ao carregar relatório por período: {e}")

            elif sub == "Editar Contrato":
                st.header("✏️ Editar Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"ID: {h['id']} | {h['cliente']}": h for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    obj = hdict[sel]
                    with st.form("fe_hon"):
                        ec, es, ev = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Serviço", value=obj.get('servico','')), st.number_input("Valor", value=float(obj.get('valor_total',0)))
                        
                        col_eh1, col_eh2 = st.columns(2)
                        with col_eh1:
                            salvar_ed_hon = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_eh2:
                            voltar_ed_hon = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_hon:
                            supabase.table("honorarios").update({"cliente": ec, "servico": es, "valor_total": float(ev)}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Contrato", "Pagamentos", f"ID: {obj['id']}")
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                        if voltar_ed_hon:
                            st.session_state['submenu_atual'] = "Ver Parcelas"
                            st.rerun()
            elif sub == "Excluir Contrato" and user_role == 'admin':
                st.header("🗑️ Excluir Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    if st.checkbox("Confirmo exclusão do contrato selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("honorarios").delete().eq("id", hdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Contrato", "Pagamentos", f"ID: {hdict[sel]}")
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os contratos e parcelas.")
                    if st.checkbox("Confirmo a exclusão de TODOS os contratos e parcelas cadastradas."):
                        if st.button("🔥 EXCLUIR TODOS OS CONTRATOS E PARCELAS", type="primary"):
                            supabase.table("parcelas").delete().neq("id", 0).execute()
                            supabase.table("honorarios").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS CONTRATOS", "Pagamentos", "Exclusão em massa.")
                            st.cache_data.clear(); st.success("Todos os contratos e parcelas foram excluídos!"); st.rerun()
                else: st.info("Sem contratos cadastrados.")

        elif menu_principal == "Perícias":
            if sub == "Cadastrar Perícia":
                st.header("🔬 Nova Perícia")
                with st.form("fc_per", clear_on_submit=True):
                    cpf = st.text_input("CPF")
                    nome = st.text_input("Nome *")
                    local_pm = st.text_input("Local PM")
                    dt_pm = st.date_input("Data PM", datetime.now())
                    hora_pm = st.text_input("Hora PM (ex: 14:30)")
                    local_ps = st.text_input("Local PM")
                    dt_ps = st.date_input("Data PS", datetime.now())
                    hora_ps = st.text_input("Hora PS (ex: 15:30)")
                    senha_inss = st.text_input("Senha INSS")
                    elaborador = st.text_input("Elaborador")
                    
                    col_bp1, col_bp2 = st.columns(2)
                    with col_bp1:
                        salvar_per = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_bp2:
                        voltar_per = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_per:
                        if not nome:
                            st.error("O campo Nome é obrigatório.")
                        else:
                            supabase.table("pericias").insert({
                                "cpf": cpf,
                                "nome": nome,
                                "local_pm": local_pm,
                                "data_pm": dt_pm.strftime("%Y-%m-%d"),
                                "hora_pm": hora_pm,
                                "local_ps": local_ps,
                                "data_ps": dt_ps.strftime("%Y-%m-%d"),
                                "hora_ps": hora_ps,
                                "senha_inss": senha_inss,
                                "elaborador": elaborador,
                                "status": "Pendente"
                            }).execute()
                            registrar_auditoria(username, "Cadastrar Perícia", "Perícias", f"Nome: {nome}")
                            st.cache_data.clear()
                            st.session_state['cad_per_sucesso'] = True
                            st.rerun()
                    if voltar_per:
                        st.session_state['submenu_atual'] = "Ver Perícias"
                        st.rerun()

                if st.session_state.get('cad_per_sucesso'):
                    st.success("🎉 Perícia cadastrada com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Nova Perícia", key="btn_novo_per", type="primary", use_container_width=True):
                            st.session_state['cad_per_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_per", use_container_width=True):
                            st.session_state['cad_per_sucesso'] = False
                            st.session_state['submenu_atual'] = "Ver Perícias"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Perícias via Excel")
                st.caption("O arquivo deve conter exatamente as colunas: cpf, nome, local_pm, data_pm, hora_pm, local_ps, data_ps, hora_ps, senha_inss, elaborador, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_per")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("pericias", file_up)

            elif sub == "Ver Perícias":
                st.header("📋 Lista de Perícias")
                res = carregar_dados("pericias")
                if res: 
                    df_per = pd.DataFrame(res)
                    ordem_desejada = ['cpf', 'nome', 'local_pm', 'data_pm', 'hora_pm', 'local_ps', 'data_ps', 'hora_ps', 'senha_inss', 'elaborador', 'status']
                    colunas_existentes = [c for c in ordem_desejada if c in df_per.columns]
                    outras_colunas = [c for c in df_per.columns if c not in ordem_desejada and c != 'id']
                    df_per = df_per[['id'] + colunas_existentes + outras_colunas]

                    if 'status' in df_per.columns:
                        st.dataframe(df_per.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_per, use_container_width=True, hide_index=True)
                else: 
                    st.info("Sem perícias cadastradas.")

            elif sub == "Editar Perícia":
                st.header("✏️ Editar Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i.get('nome', 'Sem Nome')}": i for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    obj = pdict[sel]
                    with st.form("fe_per"):
                        ecpf = st.text_input("CPF", value=obj.get('cpf',''))
                        enome = st.text_input("Nome", value=obj.get('nome',''))
                        elocal_pm = st.text_input("Local PM", value=obj.get('local_pm',''))
                        
                        dt_pm_val = datetime.now().date()
                        if obj.get('data_pm'):
                            try:
                                dt_pm_val = datetime.strptime(obj.get('data_pm'), "%Y-%m-%d").date()
                            except:
                                pass
                        edt_pm = st.date_input("Data PM", value=dt_pm_val)
                        ehora_pm = st.text_input("Hora PM", value=obj.get('hora_pm',''))

                        elocal_ps = st.text_input("Local PS", value=obj.get('local_ps',''))
                        dt_ps_val = datetime.now().date()
                        if obj.get('data_ps'):
                            try:
                                dt_ps_val = datetime.strptime(obj.get('data_ps'), "%Y-%m-%d").date()
                            except:
                                pass
                        edt_ps = st.date_input("Data PS", value=dt_ps_val)
                        ehora_ps = st.text_input("Hora PS", value=obj.get('hora_ps',''))

                        esenhainss = st.text_input("Senha INSS", value=obj.get('senha_inss',''))
                        eelab = st.text_input("Elaborador", value=obj.get('elaborador',''))
                        est_op = st.selectbox("Status", ["Pendente", "Em Andamento", "Concluído", "Pago"], index=["Pendente", "Em Andamento", "Concluído", "Pago"].index(obj.get('status', 'Pendente')) if obj.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Concluído", "Pago"] else 0)
                        
                        col_ep1, col_ep2 = st.columns(2)
                        with col_ep1:
                            salvar_ed_per = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)
                        with col_ep2:
                            voltar_ed_per = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_per:
                            supabase.table("pericias").update({
                                "cpf": ecpf,
                                "nome": enome,
                                "local_pm": elocal_pm,
                                "data_pm": edt_pm.strftime("%Y-%m-%d"),
                                "hora_pm": ehora_pm,
                                "local_ps": elocal_ps,
                                "data_ps": edt_ps.strftime("%Y-%m-%d"),
                                "hora_ps": ehora_ps,
                                "senha_inss": esenhainss,
                                "elaborador": eelab,
                                "status": est_op
                            }).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Perícia", "Perícias", f"ID: {obj['id']}")
                            st.cache_data.clear()
                            st.success("Perícia atualizada com sucesso!")
                            st.rerun()
                        if voltar_ed_per:
                            st.session_state['submenu_atual'] = "Ver Perícias"
                            st.rerun()
                else: 
                    st.info("Sem perícias para editar.")

            elif sub == "Excluir Perícia" and user_role == 'admin':
                st.header("🗑️ Excluir Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i.get('nome', 'Sem Nome')}": i['id'] for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da perícia selecionada.") and st.button("EXCLUIR SELECIONADA", type="primary"):
                        supabase.table("pericias").delete().eq("id", pdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Perícia", "Perícias", f"ID: {pdict[sel]}")
                        st.cache_data.clear()
                        st.success("Perícia excluída!")
                        st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODAS as perícias.")
                    if st.checkbox("Confirmo a exclusão de TODAS as perícias cadastradas."):
                        if st.button("🔥 EXCLUIR TODAS AS PERÍCIAS", type="primary"):
                            supabase.table("pericias").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODAS AS PERÍCIAS", "Perícias", "Exclusão em massa.")
                            st.cache_data.clear()
                            st.success("Todas as perícias foram excluídas!")
                            st.rerun()
                else: 
                    st.info("Sem perícias cadastradas.")

        elif menu_principal == "Expedientes":
            if sub == "Cadastrar Expediente":
                st.header("📂 Novo Expediente")
                with st.form("fc_exp", clear_on_submit=True):
                    proc, cli, desc, dt, resp = st.text_input("Processo"), st.text_input("Cliente"), st.text_input("Descrição"), st.date_input("Prazo", datetime.now()), st.text_input("Responsável")
                    
                    col_bx1, col_bx2 = st.columns(2)
                    with col_bx1:
                        salvar_exp = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_bx2:
                        voltar_exp = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_exp:
                        supabase.table("expedientes").insert({"numero_processo": proc, "cliente": cli, "descricao": desc, "data_manifestacao": dt.strftime("%Y-%m-%d"), "responsavel": resp, "status": "Pendente"}).execute()
                        registrar_auditoria(username, "Cadastrar Expediente", "Expedientes", f"Processo: {proc}")
                        st.cache_data.clear()
                        st.session_state['cad_exp_sucesso'] = True
                        st.rerun()
                    if voltar_exp:
                        st.session_state['submenu_atual'] = "Consultar Expedientes"
                        st.rerun()

                if st.session_state.get('cad_exp_sucesso'):
                    st.success("🎉 Expediente cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Expediente", key="btn_novo_exp", type="primary", use_container_width=True):
                            st.session_state['cad_exp_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_exp", use_container_width=True):
                            st.session_state['cad_exp_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Expedientes"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Expedientes via Excel")
                st.caption("O arquivo deve conter as colunas: numero_processo, cliente, descricao, data_manifestacao (AAAA-MM-DD), responsavel, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_exp")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("expedientes", file_up)
            elif sub == "Consultar Expedientes":
                st.header("📋 Expedientes & Gestão Rápida de Status")
                res = carregar_dados("expedientes")
                if res:
                    df_exp = pd.DataFrame(res)
                    if 'status' in df_exp.columns:
                        st.dataframe(df_exp.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_exp, use_container_width=True, hide_index=True)
                    
                    st.markdown("---")
                    st.subheader("⚡ Atualização Rápida de Status")
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} ({i.get('status', 'Pendente')})": i for i in res}
                    sel_exp = st.selectbox("Selecione o Expediente:", list(edict.keys()), key="sel_up_exp")
                    obj_exp = edict[sel_exp]
                    
                    novo_status_exp = st.selectbox("Novo Status:", ["Pendente", "Em Andamento", "Manifestado"], index=["Pendente", "Em Andamento", "Manifestado"].index(obj_exp.get('status', 'Pendente')) if obj_exp.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Manifestado"] else 0, key="st_exp_val")
                    
                    if st.button("Atualizar Status do Expediente", type="primary"):
                        supabase.table("expedientes").update({"status": novo_status_exp}).eq("id", obj_exp['id']).execute()
                        registrar_auditoria(username, "Atualizar Status", "Expedientes", f"Processo ID {obj_exp['id']} para {novo_status_exp}")
                        st.cache_data.clear()
                        st.success("Status atualizado com sucesso!")
                        st.rerun()
                else: st.info("Sem expedientes cadastrados.")
            elif sub == "Editar Expediente":
                st.header("✏️ Editar Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    obj = edict[sel]
                    with st.form("fe_exp"):
                        ep, ec, ed, er, es = st.text_input("Processo", value=obj.get('numero_processo','')), st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Descrição", value=obj.get('descricao','')), st.text_input("Responsável", value=obj.get('responsavel','')), st.selectbox("Status", ["Pendente", "Em Andamento", "Manifestado"])
                        
                        col_eed1, col_eed2 = st.columns(2)
                        with col_eed1:
                            salvar_ed_exp = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_eed2:
                            voltar_ed_exp = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_exp:
                            supabase.table("expedientes").update({"numero_processo": ep, "cliente": ec, "descricao": ed, "responsavel": er, "status": es}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Expediente", "Expedientes", f"ID: {obj['id']}")
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                        if voltar_ed_exp:
                            st.session_state['submenu_atual'] = "Consultar Expedientes"
                            st.rerun()
            elif sub == "Excluir Expediente" and user_role == 'admin':
                st.header("🗑️ Excluir Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i['id'] for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    if st.checkbox("Confirmo exclusão do expediente selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("expedientes").delete().eq("id", edict[sel]).execute()
                        registrar_auditoria(username, "Excluir Expediente", "Expedientes", f"ID: {edict[sel]}")
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os expedientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os expedientes cadastrados."):
                        if st.button("🔥 EXCLUIR TODOS OS EXPEDIENTES", type="primary"):
                            supabase.table("expedientes").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS EXPEDIENTES", "Expedientes", "Exclusão em massa.")
                            st.cache_data.clear(); st.success("Todos os expedientes foram excluídos!"); st.rerun()
                else: st.info("Sem expedientes cadastrados.")

        elif menu_principal == "Expedientes TRF":
            if sub == "Cadastrar Expediente TRF":
                st.header("⚖️ Novo Expediente TRF")
                with st.form("fc_exp_trf", clear_on_submit=True):
                    proc, cli, desc, dt, resp = st.text_input("Processo"), st.text_input("Cliente"), st.text_input("Descrição"), st.date_input("Prazo", datetime.now()), st.text_input("Responsável")
                    
                    col_btrf1, col_btrf2 = st.columns(2)
                    with col_btrf1:
                        salvar_trf = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_btrf2:
                        voltar_trf = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_trf:
                        supabase.table("expedientes_trf").insert({"numero_processo": proc, "cliente": cli, "descricao": desc, "data_manifestacao": dt.strftime("%Y-%m-%d"), "responsavel": resp, "status": "Pendente"}).execute()
                        registrar_auditoria(username, "Cadastrar Expediente TRF", "Expedientes TRF", f"Processo: {proc}")
                        st.cache_data.clear()
                        st.session_state['cad_trf_sucesso'] = True
                        st.rerun()
                    if voltar_trf:
                        st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                        st.rerun()

                if st.session_state.get('cad_trf_sucesso'):
                    st.success("🎉 Expediente TRF cadastrado com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Novo Expediente TRF", key="btn_novo_trf", type="primary", use_container_width=True):
                            st.session_state['cad_trf_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_trf", use_container_width=True):
                            st.session_state['cad_trf_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Expedientes TRF via Excel")
                st.caption("O arquivo deve conter as colunas: numero_processo, cliente, descricao, data_manifestacao (AAAA-MM-DD), responsavel, status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_trf")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("expedientes_trf", file_up)
            elif sub == "Consultar Expedientes TRF":
                st.header("📋 Expedientes TRF & Gestão Rápida de Status")
                res = carregar_dados("expedientes_trf")
                if res:
                    df_trf = pd.DataFrame(res)
                    if 'status' in df_trf.columns:
                        st.dataframe(df_trf.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_trf, use_container_width=True, hide_index=True)

                    st.markdown("---")
                    st.subheader("⚡ Atualização Rápida de Status")
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} ({i.get('status', 'Pendente')})": i for i in res}
                    sel_trf = st.selectbox("Selecione o Expediente TRF:", list(edict.keys()), key="sel_up_trf")
                    obj_trf = edict[sel_trf]
                    
                    novo_status_trf = st.selectbox("Novo Status:", ["Pendente", "Em Andamento", "Manifestado"], index=["Pendente", "Em Andamento", "Manifestado"].index(obj_trf.get('status', 'Pendente')) if obj_trf.get('status', 'Pendente') in ["Pendente", "Em Andamento", "Manifestado"] else 0, key="st_trf_val")
                    
                    if st.button("Atualizar Status do Expediente TRF", type="primary"):
                        supabase.table("expedientes_trf").update({"status": novo_status_trf}).eq("id", obj_trf['id']).execute()
                        registrar_auditoria(username, "Atualizar Status TRF", "Expedientes TRF", f"Processo ID {obj_trf['id']} para {novo_status_trf}")
                        st.cache_data.clear()
                        st.success("Status atualizado com sucesso!")
                        st.rerun()
                else: st.info("Sem expedientes TRF cadastrados.")
            elif sub == "Editar Expediente TRF":
                st.header("✏️ Editar Expediente TRF")
                res = carregar_dados("expedientes_trf")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i for i in res}
                    sel = st.selectbox("Expediente TRF:", list(edict.keys()))
                    obj = edict[sel]
                    with st.form("fe_exp_trf"):
                        ep, ec, ed, er, es = st.text_input("Processo", value=obj.get('numero_processo','')), st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Descrição", value=obj.get('descricao','')), st.text_input("Responsável", value=obj.get('responsavel','')), st.selectbox("Status", ["Pendente", "Em Andamento", "Manifestado"])
                        
                        col_edtrf1, col_edtrf2 = st.columns(2)
                        with col_edtrf1:
                            salvar_ed_trf = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_edtrf2:
                            voltar_ed_trf = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_trf:
                            supabase.table("expedientes_trf").update({"numero_processo": ep, "cliente": ec, "descricao": ed, "responsavel": er, "status": es}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Expediente TRF", "Expedientes TRF", f"ID: {obj['id']}")
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                        if voltar_ed_trf:
                            st.session_state['submenu_atual'] = "Consultar Expedientes TRF"
                            st.rerun()
                else: st.info("Sem expedientes TRF.")
            elif sub == "Excluir Expediente TRF" and user_role == 'admin':
                st.header("🗑️ Excluir Expediente TRF")
                res = carregar_dados("expedientes_trf")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i['id'] for i in res}
                    sel = st.selectbox("Expediente TRF:", list(edict.keys()))
                    if st.checkbox("Confirmo exclusão do expediente TRF selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("expedientes_trf").delete().eq("id", edict[sel]).execute()
                        registrar_auditoria(username, "Excluir Expediente TRF", "Expedientes TRF", f"ID: {edict[sel]}")
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os expedientes TRF.")
                    if st.checkbox("Confirmo a exclusão de TODOS os expedientes TRF cadastrados."):
                        if st.button("🔥 EXCLUIR TODOS OS EXPEDIENTES TRF", type="primary"):
                            supabase.table("expedientes_trf").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODOS OS EXPEDIENTES TRF", "Expedientes TRF", "Exclusão em massa.")
                            st.cache_data.clear(); st.success("Todas as expedientes TRF foram excluídos!"); st.rerun()
                else: st.info("Sem expedientes TRF cadastrados.")

        elif menu_principal == "Pendências":
            if sub == "Cadastrar Pendência":
                st.header("📋 Nova Pendência")
                with st.form("fc_pen", clear_on_submit=True):
                    cli, proc = st.text_input("Cliente"), st.text_input("Processo")
                    d1, d2, d3 = st.checkbox("Procuração / RG / CPF"), st.checkbox("Comprovante Residência"), st.checkbox("Laudos / Exames")
                    d4 = st.text_input("Outro")
                    
                    col_bpen1, col_bpen2 = st.columns(2)
                    with col_bpen1:
                        salvar_pen = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                    with col_bpen2:
                        voltar_pen = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                    if salvar_pen:
                        docs = [d for d, b in zip(["Procuração/Docs", "Comp. Residência", "Laudos/Exames"], [d1, d2, d3]) if b]
                        if d4.strip(): docs.append(d4.strip())
                        if cli and docs:
                            supabase.table("pendencias").insert({"cliente": cli, "processo": proc, "documento_devido": " | ".join(docs), "data_solicitacao": date.today().strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                            registrar_auditoria(username, "Cadastrar Pendência", "Pendências", f"Cliente: {cli}")
                            st.cache_data.clear()
                            st.session_state['cad_pen_sucesso'] = True
                            st.rerun()
                        else: st.warning("Preencha o cliente e selecione ao menos um documento.")
                    if voltar_pen:
                        st.session_state['submenu_atual'] = "Consultar Pendências"
                        st.rerun()

                if st.session_state.get('cad_pen_sucesso'):
                    st.success("🎉 Pendência cadastrada com sucesso!")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ Cadastrar Nova Pendência", key="btn_novo_pen", type="primary", use_container_width=True):
                            st.session_state['cad_pen_sucesso'] = False
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Voltar para Lista", key="btn_vol_pen", use_container_width=True):
                            st.session_state['cad_pen_sucesso'] = False
                            st.session_state['submenu_atual'] = "Consultar Pendências"
                            st.rerun()

            elif sub == "Importar Excel":
                st.header("📥 Importar Pendências via Excel")
                st.caption("O arquivo deve conter as colunas: cliente, processo, documento_devido, data_solicitacao (AAAA-MM-DD), status")
                file_up = st.file_uploader("Envie a planilha (.xlsx ou .csv)", type=["xlsx", "csv"], key="up_pen")
                if file_up and st.button("Confirmar Importação", type="primary"):
                    importar_excel_para_supabase("pendencias", file_up)
            elif sub == "Consultar Pendências":
                st.header("📂 Pendências")
                res = carregar_dados("pendencias")
                if res:
                    df_pen = pd.DataFrame(res)
                    if 'status' in df_pen.columns:
                        st.dataframe(df_pen.style.map(colorir_status, subset=['status']), use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(df_pen, use_container_width=True, hide_index=True)

                    pid = st.number_input("ID da Pendência entregue:", min_value=1, step=1)
                    if st.button("Marcar como Entregue"):
                        supabase.table("pendencias").update({"status": "Entregue"}).eq("id", pid).execute()
                        registrar_auditoria(username, "Marcar Entregue", "Pendências", f"Pendência ID: {pid}")
                        st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                else: st.info("Sem pendências.")
            elif sub == "Editar Pendência":
                st.header("✏️ Editar Pendência")
                res = carregar_dados("pendencias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i for i in res}
                    sel = st.selectbox("Pendência:", list(pdict.keys()))
                    obj = pdict[sel]
                    with st.form("fe_pen"):
                        ec, ep, ed = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Processo", value=obj.get('processo','')), st.text_input("Documentos", value=obj.get('documento_devido',''))
                        
                        col_edpen1, col_edpen2 = st.columns(2)
                        with col_edpen1:
                            salvar_ed_pen = st.form_submit_button("Salvar", type="primary", use_container_width=True)
                        with col_edpen2:
                            voltar_ed_pen = st.form_submit_button("⬅️ Voltar", use_container_width=True)

                        if salvar_ed_pen:
                            supabase.table("pendencias").update({"cliente": ec, "processo": ep, "documento_devido": ed}).eq("id", obj['id']).execute()
                            registrar_auditoria(username, "Editar Pendência", "Pendências", f"ID: {obj['id']}")
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                        if voltar_ed_pen:
                            st.session_state['submenu_atual'] = "Consultar Pendências"
                            st.rerun()
            elif sub == "Excluir Pendência" and user_role == 'admin':
                st.header("🗑️ Excluir Pendência")
                res = carregar_dados("pendencias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i['id'] for i in res}
                    sel = st.selectbox("Pendência:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da pendência selecionada.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("pendencias").delete().eq("id", pdict[sel]).execute()
                        registrar_auditoria(username, "Excluir Pendência", "Pendências", f"ID: {pdict[sel]}")
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS as pendências.")
                    if st.checkbox("Confirmo a exclusão de TODOS as pendências cadastradas."):
                        if st.button("🔥 EXCLUIR TODOS AS PENDÊNCIAS", type="primary"):
                            supabase.table("pendencias").delete().neq("id", 0).execute()
                            registrar_auditoria(username, "EXCLUIR TODAS AS PENDÊNCIAS", "Pendências", "Exclusão em massa.")
                            st.cache_data.clear(); st.success("Todas as pendências foram excluídas!"); st.rerun()
                else: st.info("Sem pendências cadastradas.")
