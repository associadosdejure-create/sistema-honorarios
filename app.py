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
    
    try:
        supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception:
        st.error("⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes nos Secrets.")
        st.stop()

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

    @st.cache_data(ttl=300)
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
        for label, pag in modulos.items():
            if st.button(label, use_container_width=True):
                st.session_state['pagina_atual'] = pag
                st.session_state['submenu_atual'] = "" if pag == "🏠 Página Inicial" else {"Clientes": "Consultar Clientes", "Pagamentos": "Ver Parcelas", "Perícias": "Ver Perícias", "Expedientes": "Consultar Expedientes", "Pendências": "Consultar Pendências"}[pag]
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
    else:
        menu_principal = menu_escolha
        st.title(f"Módulo: {menu_principal} ⚖️")

        acoes_dict = {
            "Clientes": ["Consultar Clientes", "Cadastrar Cliente", "Editar Cliente", "Excluir Cliente", "Exportar Base (Backup)"],
            "Pagamentos": ["Ver Parcelas", "Cadastrar Contrato / Parcelas", "Baixar Parcela", "Editar Contrato", "Excluir Contrato"],
            "Perícias": ["Ver Perícias", "Cadastrar Perícia", "Editar Perícia", "Excluir Perícia"],
            "Expedientes": ["Consultar Expedientes", "Cadastrar Expediente", "Editar Expediente", "Excluir Expediente"],
            "Pendências": ["Consultar Pendências", "Cadastrar Pendência", "Editar Pendência", "Excluir Pendência"]
        }
        acoes = acoes_dict.get(menu_principal, [])

        if not st.session_state['submenu_atual'] or st.session_state['submenu_atual'] not in acoes:
            st.session_state['submenu_atual'] = acoes[0]

        cols = st.columns(len(acoes))
        for idx, acao in enumerate(acoes):
            with cols[idx]:
                if st.button(acao, use_container_width=True, type="primary" if st.session_state['submenu_atual'] == acao else "secondary"):
                    st.session_state['submenu_atual'] = acao
                    st.rerun()

        st.markdown("---")
        sub = st.session_state['submenu_atual']

        # --- PROCESSAMENTO DOS MÓDULOS ---
        if menu_principal == "Clientes":
            if sub == "Cadastrar Cliente":
                st.header("👤 Cadastro Completo de Cliente")
                with st.form("fc_cli"):
                    n, doc, tel, email, end, cid, gov, ind, obs = st.text_input("Nome *"), st.text_input("CPF/CNPJ"), st.text_input("Telefone"), st.text_input("E-mail"), st.text_input("Endereço"), st.text_input("Cidade/UF"), st.text_input("Senha Gov.br"), st.text_input("Indicado Por"), st.text_area("Observações")
                    if st.form_submit_button("Salvar"):
                        if not n: st.error("O campo Nome é obrigatório.")
                        else:
                            doc_l = ''.join(filter(str.isdigit, str(doc)))
                            if len(doc_l) == 11 and not validar_cpf(doc_l): st.error("CPF Inválido!")
                            else:
                                supabase.table("clientes_cadastrados").insert({"nome": n, "cpf_cnpj": doc, "telefone": tel, "email": email, "endereco": end, "cidade": cid, "senha_gov": gov, "indicado_por": ind, "observacoes": obs}).execute()
                                st.cache_data.clear(); st.success("Cliente cadastrado!")
            elif sub == "Consultar Clientes":
                st.header("📋 Base de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
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
                        if st.form_submit_button("Atualizar"):
                            supabase.table("clientes_cadastrados").update({"nome": en, "cpf_cnpj": edoc, "telefone": etel, "email": eemail, "endereco": eend, "cidade": ecid, "senha_gov": egov, "indicado_por": eind, "observacoes": eobs}).eq("id", obj['id']).execute()
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                else: st.info("Nenhum cliente.")
            elif sub == "Excluir Cliente" and user_role == 'admin':
                st.header("🗑️ Excluir Cliente")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    cdict = {f"ID: {c['id']} — {c['nome']}": c['id'] for c in res}
                    sel = st.selectbox("Cliente:", list(cdict.keys()))
                    if st.checkbox("Confirmo exclusão permanente deste cliente.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("clientes_cadastrados").delete().eq("id", cdict[sel]).execute()
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()
                    
                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de toda a base de clientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os registros de clientes do sistema."):
                        if st.button("🔥 EXCLUIR TODOS OS CLIENTES", type="primary"):
                            supabase.table("clientes_cadastrados").delete().neq("id", 0).execute()
                            st.cache_data.clear(); st.success("Todos os registros foram excluídos com sucesso!"); st.rerun()
                else: st.info("Nenhum cliente cadastrado.")
            elif sub == "Exportar Base (Backup)":
                st.header("📥 Backup de Clientes")
                res = carregar_dados("clientes_cadastrados")
                if res:
                    st.download_button("Baixar CSV", data=pd.DataFrame(res).to_csv(index=False).encode('utf-8'), file_name=f"clientes_{date.today()}.csv", mime="text/csv", type="primary")
                else: st.info("Sem dados.")

        elif menu_principal == "Pagamentos":
            if sub == "Cadastrar Contrato / Parcelas":
                st.header("📝 Novo Contrato")
                cli_db = carregar_dados("clientes_cadastrados")
                nomes = [c['nome'] for c in cli_db]
                with st.form("fc_hon"):
                    cli_op = st.selectbox("Cliente:", ["Outro"] + nomes) if nomes else "Outro"
                    cli = st.text_input("Nome") if cli_op == "Outro" else cli_op
                    serv, vtot, npar, dt1 = st.text_input("Serviço"), st.number_input("Valor Total", min_value=0.0), st.number_input("Parcelas", min_value=1, max_value=36, value=3), st.date_input("1º Vencimento", datetime.now())
                    if st.form_submit_button("Gerar"):
                        if cli and serv and vtot > 0:
                            res = supabase.table("honorarios").insert({"cliente": cli, "servico": serv, "valor_total": float(vtot)}).execute()
                            if res.data:
                                h_id = res.data[0]['id']
                                vp = vtot / npar
                                for i in range(int(npar)):
                                    venc = (dt1 + relativedelta(months=i)).strftime("%Y-%m-%d")
                                    supabase.table("parcelas").insert({"honorario_id": h_id, "numero_parcela": f"{i+1}/{int(npar)}", "valor": float(vp), "vencimento": venc, "status": "Pendente"}).execute()
                                st.cache_data.clear(); st.success("Contrato cadastrado!")
            elif sub == "Ver Parcelas":
                st.header("📋 Visualizar Parcelas")
                res_h = carregar_dados("honorarios")
                if res_h:
                    cdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(cdict.keys()))
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel]).execute()
                    if res_p.data: st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)
                    else: st.info("Sem parcelas.")
                else: st.info("Sem contratos.")
            elif sub == "Baixar Parcela":
                st.header("🔄 Baixar Parcela")
                res_h = carregar_dados("honorarios")
                if res_h:
                    cdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(cdict.keys()))
                    res_p = supabase.table("parcelas").select("*").eq("honorario_id", cdict[sel]).execute()
                    if res_p.data:
                        st.dataframe(pd.DataFrame(res_p.data), use_container_width=True)
                        pid = st.number_input("ID da Parcela:", min_value=1, step=1)
                        if st.button("Confirmar Baixa", type="primary"):
                            supabase.table("parcelas").update({"status": "Pago"}).eq("id", pid).execute()
                            st.cache_data.clear(); st.success("Baixado!"); st.rerun()
            elif sub == "Editar Contrato":
                st.header("✏️ Editar Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"ID: {h['id']} | {h['cliente']}": h for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    obj = hdict[sel]
                    with st.form("fe_hon"):
                        ec, es, ev = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Serviço", value=obj.get('servico','')), st.number_input("Valor", value=float(obj.get('valor_total',0)))
                        if st.form_submit_button("Salvar"):
                            supabase.table("honorarios").update({"cliente": ec, "servico": es, "valor_total": float(ev)}).eq("id", obj['id']).execute()
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
            elif sub == "Excluir Contrato" and user_role == 'admin':
                st.header("🗑️ Excluir Contrato")
                res_h = carregar_dados("honorarios")
                if res_h:
                    hdict = {f"{h['cliente']} — {h['servico']}": h['id'] for h in res_h}
                    sel = st.selectbox("Contrato:", list(hdict.keys()))
                    if st.checkbox("Confirmo exclusão do contrato selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("honorarios").delete().eq("id", hdict[sel]).execute()
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os contratos e parcelas.")
                    if st.checkbox("Confirmo a exclusão de TODOS os contratos e parcelas cadastradas."):
                        if st.button("🔥 EXCLUIR TODOS OS CONTRATOS E PARCELAS", type="primary"):
                            supabase.table("parcelas").delete().neq("id", 0).execute()
                            supabase.table("honorarios").delete().neq("id", 0).execute()
                            st.cache_data.clear(); st.success("Todos os contratos e parcelas foram excluídos!"); st.rerun()
                else: st.info("Sem contratos cadastrados.")

        elif menu_principal == "Perícias":
            if sub == "Cadastrar Perícia":
                st.header("🔬 Nova Perícia")
                with st.form("fc_per"):
                    cli, tipo, juizo, val, dt = st.text_input("Cliente"), st.text_input("Tipo"), st.text_input("Juízo"), st.number_input("Valor", min_value=0.0), st.date_input("Data", datetime.now())
                    if st.form_submit_button("Salvar"):
                        supabase.table("pericias").insert({"cliente": cli, "tipo_pericia": tipo, "juizo_vara": juizo, "honorario_pericial": float(val), "data_indicacao": dt.strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                        st.cache_data.clear(); st.success("Cadastrado!")
            elif sub == "Ver Perícias":
                st.header("📋 Lista de Perícias")
                res = carregar_dados("pericias")
                if res: st.dataframe(pd.DataFrame(res), use_container_width=True)
                else: st.info("Sem perícias.")
            elif sub == "Editar Perícia":
                st.header("✏️ Editar Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    obj = pdict[sel]
                    with st.form("fe_per"):
                        ec, et, ej, ev, st_op = st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Tipo", value=obj.get('tipo_pericia','')), st.text_input("Juízo", value=obj.get('juizo_vara','')), st.number_input("Valor", value=float(obj.get('honorario_pericial',0))), st.selectbox("Status", ["Pendente", "Concluído", "Pago"])
                        if st.form_submit_button("Salvar"):
                            supabase.table("pericias").update({"cliente": ec, "tipo_pericia": et, "juizo_vara": ej, "honorario_pericial": float(ev), "status": st_op}).eq("id", obj['id']).execute()
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
            elif sub == "Excluir Perícia":
                st.header("🗑️ Excluir Perícia")
                res = carregar_dados("pericias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i['id'] for i in res}
                    sel = st.selectbox("Perícia:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da perícia selecionada.") and st.button("EXCLUIR SELECIONADA", type="primary"):
                        supabase.table("pericias").delete().eq("id", pdict[sel]).execute()
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODAS as perícias.")
                    if st.checkbox("Confirmo a exclusão de TODAS as perícias cadastradas."):
                        if st.button("🔥 EXCLUIR TODAS AS PERÍCIAS", type="primary"):
                            supabase.table("pericias").delete().neq("id", 0).execute()
                            st.cache_data.clear(); st.success("Todas as perícias foram excluídas!"); st.rerun()
                else: st.info("Sem perícias cadastradas.")

        elif menu_principal == "Expedientes":
            if sub == "Cadastrar Expediente":
                st.header("📂 Novo Expediente")
                with st.form("fc_exp"):
                    proc, cli, desc, dt, resp = st.text_input("Processo"), st.text_input("Cliente"), st.text_input("Descrição"), st.date_input("Prazo", datetime.now()), st.text_input("Responsável")
                    if st.form_submit_button("Salvar"):
                        supabase.table("expedientes").insert({"numero_processo": proc, "cliente": cli, "descricao": desc, "data_manifestacao": dt.strftime("%Y-%m-%d"), "responsavel": resp, "status": "Pendente"}).execute()
                        st.cache_data.clear(); st.success("Cadastrado!")
            elif sub == "Consultar Expedientes":
                st.header("📋 Expedientes")
                res = carregar_dados("expedientes")
                if res:
                    st.dataframe(pd.DataFrame(res), use_container_width=True)
                    eid = st.number_input("ID para Protocolar:", min_value=1, step=1)
                    if st.button("Marcar como Protocolado"):
                        supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", eid).execute()
                        st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
                else: st.info("Sem expedientes.")
            elif sub == "Editar Expediente":
                st.header("✏️ Editar Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    obj = edict[sel]
                    with st.form("fe_exp"):
                        ep, ec, ed, er = st.text_input("Processo", value=obj.get('numero_processo','')), st.text_input("Cliente", value=obj.get('cliente','')), st.text_input("Descrição", value=obj.get('descricao','')), st.text_input("Responsável", value=obj.get('responsavel',''))
                        if st.form_submit_button("Salvar"):
                            supabase.table("expedientes").update({"numero_processo": ep, "cliente": ec, "descricao": ed, "responsavel": er}).eq("id", obj['id']).execute()
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
            elif sub == "Excluir Expediente":
                st.header("🗑️ Excluir Expediente")
                res = carregar_dados("expedientes")
                if res:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']}": i['id'] for i in res}
                    sel = st.selectbox("Expediente:", list(edict.keys()))
                    if st.checkbox("Confirmo exclusão do expediente selecionado.") and st.button("EXCLUIR SELECIONADO", type="primary"):
                        supabase.table("expedientes").delete().eq("id", edict[sel]).execute()
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODOS os expedientes.")
                    if st.checkbox("Confirmo a exclusão de TODOS os expedientes cadastrados."):
                        if st.button("🔥 EXCLUIR TODOS OS EXPEDIENTES", type="primary"):
                            supabase.table("expedientes").delete().neq("id", 0).execute()
                            st.cache_data.clear(); st.success("Todos os expedientes foram excluídos!"); st.rerun()
                else: st.info("Sem expedientes cadastrados.")

        elif menu_principal == "Pendências":
            if sub == "Cadastrar Pendência":
                st.header("📋 Nova Pendência")
                with st.form("fc_pen"):
                    cli, proc = st.text_input("Cliente"), st.text_input("Processo")
                    d1, d2, d3 = st.checkbox("Procuração / RG / CPF"), st.checkbox("Comprovante Residência"), st.checkbox("Laudos / Exames")
                    d4 = st.text_input("Outro")
                    if st.form_submit_button("Salvar"):
                        docs = [d for d, b in zip(["Procuração/Docs", "Comp. Residência", "Laudos/Exames"], [d1, d2, d3]) if b]
                        if d4.strip(): docs.append(d4.strip())
                        if cli and docs:
                            supabase.table("pendencias").insert({"cliente": cli, "processo": proc, "documento_devido": " | ".join(docs), "data_solicitacao": date.today().strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                            st.cache_data.clear(); st.success("Salvo!")
                        else: st.warning("Preencha o cliente e selecione ao menos um documento.")
            elif sub == "Consultar Pendências":
                st.header("📂 Pendências")
                res = carregar_dados("pendencias")
                if res:
                    st.dataframe(pd.DataFrame(res), use_container_width=True)
                    pid = st.number_input("ID da Pendência entregue:", min_value=1, step=1)
                    if st.button("Marcar como Entregue"):
                        supabase.table("pendencias").update({"status": "Entregue"}).eq("id", pid).execute()
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
                        if st.form_submit_button("Salvar"):
                            supabase.table("pendencias").update({"cliente": ec, "processo": ep, "documento_devido": ed}).eq("id", obj['id']).execute()
                            st.cache_data.clear(); st.success("Atualizado!"); st.rerun()
            elif sub == "Excluir Pendência":
                st.header("🗑️ Excluir Pendência")
                res = carregar_dados("pendencias")
                if res:
                    pdict = {f"ID: {i['id']} | {i['cliente']}": i['id'] for i in res}
                    sel = st.selectbox("Pendência:", list(pdict.keys()))
                    if st.checkbox("Confirmo exclusão da pendência selecionada.") and st.button("EXCLUIR SELECIONADA", type="primary"):
                        supabase.table("pendencias").delete().eq("id", pdict[sel]).execute()
                        st.cache_data.clear(); st.success("Excluído!"); st.rerun()

                    st.markdown("---")
                    st.warning("⚠️ **ÁREA CRÍTICA:** Exclusão em massa de TODAS as pendências.")
                    if st.checkbox("Confirmo a exclusão de TODAS as pendências cadastradas."):
                        if st.button("🔥 EXCLUIR TODAS AS PENDÊNCIAS", type="primary"):
                            supabase.table("pendencias").delete().neq("id", 0).execute()
                            st.cache_data.clear(); st.success("Todas as pendências foram excluídas!"); st.rerun()
                else: st.info("Sem pendências cadastradas.")
