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
        st.warning('⏱️ Sua sessão expirou (5 min inativa). Faça login novamente.')
    else:
        st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    
    agora = time.time()
    TEMPO_MAXIMO = 300  # 5 minutos em segundos

    if 'ultima_atividade' in st.session_state:
        tempo_decorrido = agora - st.session_state['ultima_atividade']
        if tempo_decorrido > TEMPO_MAXIMO:
            st.session_state['logout'] = True
            st.session_state['authentication_status'] = None
            st.session_state['sessao_expirada'] = True
            del st.session_state['ultima_atividade']
            st.rerun()
            
    st.session_state['sessao_expirada'] = False
    st.session_state['ultima_atividade'] = agora

    tempo_restante = TEMPO_MAXIMO - (agora - st.session_state['ultima_atividade'])
    minutos_restantes = max(0, int(tempo_restante // 60))
    segundos_restantes = max(0, int(tempo_restante % 60))

    user_role = credentials["usernames"].get(username, {}).get("role", "estagiario")
    
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase = create_client(url, key)
    except Exception:
        st.error("⚠️ ERRO CRÍTICO: Chaves do Supabase ausentes nos Secrets.")
        st.stop()

    with st.sidebar:
        st.write(f"Logado como: **{name}**")
        if user_role == 'admin': p_txt = "👑 Sócio"
        elif user_role == 'advogado': p_txt = "⚖️ Advogado(a)"
        elif user_role == 'bacharel': p_txt = "📜 Bacharel(a)"
        else: p_txt = "🎓 Estagiário"
            
        st.caption(f"Perfil: {p_txt}")
        
        st.markdown("---")
        st.markdown(f"⏳ **Sessão expira em:**\n### `{minutos_restantes:02d}:{segundos_restantes:02d}`")
        st.caption("*(Atualiza a cada clique / ação)*")
        st.markdown("---")

        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        try: st.image("logo.png", use_container_width=True)
        except Exception: st.write("⚖️ **Dejure Advocacia**")

    st.title(f"Seja bem-vindo, {name}! ⚖️")
    
    st.markdown("### 📌 Painel de Navegação")
    col1, col2 = st.columns(2)
    
    with col1:
        menu_principal = st.selectbox("1️⃣ Módulo Principal:", ["Pagamentos", "Perícias", "Expedientes", "Pendências"])
        
    with col2:
        submenu = ""
        if menu_principal == "Pagamentos":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Cliente", "Ver Parcelas", "Baixar Parcela", "Excluir Contrato"])
        elif menu_principal == "Perícias":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Perícia", "Ver Perícias"])
        elif menu_principal == "Expedientes":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Expediente", "Consultar Expedientes"])
        elif menu_principal == "Pendências":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Pendência", "Consultar Pendências"])

    st.markdown("---")

    try:
        res_p = supabase.table("pericias").select("*").eq("status", "Pendente").execute()
        res_e = supabase.table("expedientes").select("*").eq("status", "Pendente").execute()
        hoje = date.today()
        alertas = []
        
        if res_p.data:
            for p in res_p.data:
                if p.get('data_indicacao'):
                    dt = datetime.strptime(p['data_indicacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas.append((dias, f"🔬 Perícia | Cliente: {p['cliente']} | Tipo: {p['tipo_pericia']} | Data: {dt.strftime('%d/%m/%Y')}"))
                    
        if res_e.data:
            for e in res_e.data:
                if e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas.append((dias, f"📂 Expediente | Processo: {e['numero_processo']} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {e['responsavel']}"))
                    
        if alertas:
            with st.expander("🚨 **CENTRAL DE ALERTAS DE PRAZOS**", expanded=True):
                for dias, texto in sorted(alertas, key=lambda x: x[0]):
                    if dias < 0: st.error(f"⚠️ **VENCIDO ({abs(dias)} dias):** {texto}")
                    elif dias == 1: st.error(f"🚨 **CRÍTICO (1 dia):** {texto}")
                    elif dias <= 3: st.warning(f"⚠️ **URGENTE ({dias} dias):** {texto}")
                    elif dias <= 7: st.info(f"📅 **LEMBRETE ({dias} dias):** {texto}")
            st.markdown("---")
    except Exception:
        pass

    if menu_principal == "Pagamentos":
        if submenu == "Cadastrar Cliente":
            st.header("📝 Cadastrar Novo Cliente e Contrato")
            with st.form("form_honorario"):
                cliente = st.text_input("Nome do Cliente")
                servico = st.text_input("Descrição do Serviço / Processo")
                valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
                num_parcelas = st.number_input("Número de Parcelas", min_value=1, max_value=36, value=3)
                data_primeira = st.date_input("Data do 1º Vencimento", datetime.now())
                
                if st.form_submit_button("Cadastrar e Gerar Parcelas"):
                    if cliente and servico and valor_total > 0:
                        try:
                            res = supabase.table("honorarios").insert({"cliente": cliente, "servico": servico, "valor_total": float(valor_total)}).execute()
                            if res.data:
                                h_id = res.data[0]['id']
                                vp = valor_total / num_parcelas
                                for i in range(int(num_parcelas)):
                                    venc = (data_primeira + relativedelta(months=i)).strftime("%Y-%m-%d")
                                    sp = f"{i+1}/{int(num_parcelas)}"
                                    supabase.table("parcelas").insert({"honorario_id": h_id, "numero_parcela": sp, "valor": float(vp), "vencimento": venc, "status": "Pendente"}).execute()
                                st.success(f"Sucesso! Honorário de {cliente} cadastrado.")
                            else: st.error("Erro ao retornar dados.")
                        except Exception as e: st.error(f"Erro: {e}")
                    else: st.error("Preencha todos os campos.")
                        
        elif submenu == "Ver Parcelas":
            st.header("📋 Visualizar Parcelas")
            try:
                res_h = supabase.table("honorarios").select("*").execute()
                if res_h.data:
                    cdict = {f"{h['cliente']} — Serv: {h['servico']}": h['id'] for h in res_h.data}
                    cli_sel = st.selectbox("Selecione o Cliente:", options=list(cdict.keys()))
                    if cli_sel:
                        h_id = cdict[cli_sel]
                        st.markdown("---")
                        res_p = supabase.table("parcelas").select("*").eq("honorario_id", h_id).execute()
                        if res_p.data:
                            lista = [{"ID Parcela": p['id'], "Parcela": p['numero_parcela'], "Valor (R$)": f"R$ {p['valor']:.2f}", "Vencimento": datetime.strptime(p['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": p['status']} for p in res_p.data]
                            df_p = pd.DataFrame(lista)
                            def color_st(v):
                                if v == 'Pago': return 'color: #28a745; font-weight: bold;'
                                if v == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                                return ''
                            st.dataframe(df_p.style.map(color_st, subset=['Status']), use_container_width=True)
                        else: st.info("Sem parcelas.")
                else: st.info("Nenhum cliente.")
            except Exception as e: st.error(f"Erro: {e}")
                
        elif submenu == "Baixar Parcela":
            st.header("🔄 Dar Baixa em Parcela")
            try:
                res_h = supabase.table("honorarios").select("*").execute()
                if res_h.data:
                    cdict = {f"{h['cliente']} — Serv: {h['servico']}": h['id'] for h in res_h.data}
                    cli_sel = st.selectbox("Selecione o Cliente:", options=list(cdict.keys()), key="bx_cli")
                    if cli_sel:
                        h_id = cdict[cli_sel]
                        res_p = supabase.table("parcelas").select("*").eq("honorario_id", h_id).execute()
                        if res_p.data:
                            lista = [{"ID Parcela": p['id'], "Parcela": p['numero_parcela'], "Valor (R$)": f"R$ {p['valor']:.2f}", "Vencimento": datetime.strptime(p['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": p['status']} for p in res_p.data]
                            df_p = pd.DataFrame(lista)
                            def color_st(v):
                                if v == 'Pago': return 'color: #28a745; font-weight: bold;'
                                if v == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                                return ''
                            st.dataframe(df_p.style.map(color_st, subset=['Status']), use_container_width=True)
                            st.markdown("---")
                            id_bx = st.number_input("ID da Parcela para dar baixa:", min_value=1, step=1)
                            if st.button("Confirmar Baixa (Pago)", type="primary"):
                                supabase.table("parcelas").update({"status": "Pago"}).eq("id", id_bx).execute()
                                st.success(f"Parcela {id_bx} baixada!")
                                st.rerun()
                        else: st.info("Sem parcelas.")
                else: st.info("Sem clientes.")
            except Exception as e: st.error(f"Erro: {e}")
                
        elif submenu == "Excluir Contrato":
            st.header("🗑️ Exclusão de Contratos")
            if user_role == 'admin':
                try:
                    res_h = supabase.table("honorarios").select("*").execute()
                    if res_h.data:
                        cdict = {f"{h['cliente']} — Serv: {h['servico']}": h['id'] for h in res_h.data}
                        cli_sel = st.selectbox("Contrato a excluir:", options=list(cdict.keys()))
                        if cli_sel:
                            st.warning("⚠️ Atenção: Exclusão permanente.")
                            if st.button("Excluir Definitivamente", type="primary"):
                                supabase.table("honorarios").delete().eq("id", cdict[cli_sel]).execute()
                                st.success("Contrato excluído!")
                                st.rerun()
                    else: st.info("Sem contratos.")
                except Exception as e: st.error(f"Erro: {e}")
            else: st.error("🔒 Acesso Restrito aos administradores.")
                
    elif menu_principal == "Perícias":
        if submenu == "Cadastrar Perícia":
            st.header("🔬 Cadastrar Nova Perícia")
            with st.form("form_pericia"):
                cli_per = st.text_input("Nome do Cliente")
                tipo_per = st.text_input("Tipo de Perícia")
                juizo = st.text_input("Juízo / Vara")
                val_per = st.number_input("Honorário Pericial (R$)", min_value=0.0, format="%.2f")
                dt_per = st.date_input("Data da Perícia", datetime.now())
                
                if st.form_submit_button("Salvar Perícia"):
                    if cli_per and tipo_per:
                        try:
                            supabase.table("pericias").insert({"cliente": cli_per, "tipo_pericia": tipo_per, "juizo_vara": juizo, "honorario_pericial": float(val_per), "data_indicacao": dt_per.strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                            st.success("Perícia cadastrada!")
                        except Exception as e: st.error(f"Erro: {e}")
                    else: st.error("Preencha Cliente e Tipo.")
                        
        elif submenu == "Ver Perícias":
            st.header("📋 Lista de Perícias")
            try:
                res_p = supabase.table("pericias").select("*").execute()
                if res_p.data:
                    lista = [{"ID": i['id'], "Cliente": i['cliente'], "Tipo": i['tipo_pericia'], "Juízo": i.get('juizo_vara',''), "Valor": f"R$ {i.get('honorario_pericial',0):.2f}", "Data": datetime.strptime(i['data_indicacao'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": i.get('status','Pendente')} for i in res_p.data]
                    df_p = pd.DataFrame(lista)
                    def color_p(v):
                        if v in ['Pago', 'Concluído']: return 'color: #28a745; font-weight: bold;'
                        if v == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                        return ''
                    st.dataframe(df_p.style.map(color_p, subset=['Status']), use_container_width=True)
                else: st.info("Nenhuma perícia.")
            except Exception as e: st.error(f"Erro: {e}")
                
    elif menu_principal == "Expedientes":
        if submenu == "Cadastrar Expediente":
            st.header("📂 Cadastrar Novo Expediente")
            with st.form("form_expediente"):
                num_proc = st.text_input("Número do Processo")
                cli_exp = st.text_input("Nome do Cliente")
                desc_exp = st.text_input("Descrição / Objeto")
                dt_exp = st.date_input("Prazo Limite", datetime.now())
                resp_exp = st.text_input("Responsável")
                
                if st.form_submit_button("Cadastrar"):
                    if num_proc and cli_exp and resp_exp:
                        try:
                            supabase.table("expedientes").insert({"numero_processo": num_proc, "cliente": cli_exp, "descricao": desc_exp, "data_manifestacao": dt_exp.strftime("%Y-%m-%d"), "responsavel": resp_exp, "status": "Pendente"}).execute()
                            st.success("Expediente cadastrado!")
                        except Exception as e: st.error(f"Erro: {e}")
                    else: st.error("Preencha Processo, Cliente e Responsável.")
                        
        elif submenu == "Consultar Expedientes":
            st.header("📋 Consulta de Expedientes")
            try:
                res_e = supabase.table("expedientes").select("*").execute()
                if res_e.data:
                    lista = [{"ID": i['id'], "Processo": i['numero_processo'], "Cliente": i['cliente'], "Prazo": datetime.strptime(i['data_manifestacao'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": i.get('status','Pendente')} for i in res_e.data]
                    df_e = pd.DataFrame(lista)
                    def color_e(v):
                        if v in ['Protocolado', 'Concluído']: return 'color: #28a745; font-weight: bold;'
                        if v == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                        return ''
                    st.dataframe(df_e.style.map(color_e, subset=['Status']), use_container_width=True)
                    st.markdown("---")
                    id_bx_e = st.number_input("ID do Expediente concluído:", min_value=1, step=1)
                    if st.button("Marcar como Protocolado"):
                        supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", id_bx_e).execute()
                        st.success("Atualizado!")
                        st.rerun()
                else: st.info("Nenhum expediente.")
            except Exception as e: st.error(f"Erro: {e}")
                
    elif menu_principal == "Pendências":
        if submenu == "Cadastrar Pendência":
            st.header("📋 Cadastrar Pendência")
            with st.form("form_pendencia"):
                cli_pen = st.text_input("Nome do Cliente")
                proc_pen = st.text_input("Processo (Opcional)")
                d1 = st.checkbox("Procuração / RG / CPF")
                d2 = st.checkbox("Comprovante de Residência")
                d3 = st.checkbox("Laudos / Exames")
                d4 = st.text_input("Outro Documento")
                dt_sol = st.date_input("Data", datetime.now())
                
                if st.form_submit_button("Salvar Pendência"):
                    if cli_pen:
                        docs = []
                        if d1: docs.append("Procuração/Docs Pessoais")
                        if d2: docs.append("Comprovante de Residência")
                        if d3: docs.append("Laudos/Exames")
                        if d4.strip(): docs.append(d4.strip())
                        if docs:
                            try:
                                supabase.table("pendencias").insert({"cliente": cli_pen, "processo": proc_pen, "documento_devido": " | ".join(docs), "data_solicitacao": dt_sol.strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                                st.success("Pendência cadastrada!")
                            except Exception as e: st.error(f"Erro: {e}")
                        else: st.warning("Selecione ao menos um documento.")
                    else: st.error("Preencha o Nome do Cliente.")
                        
        elif submenu == "Consultar Pendências":
            st.header("📂 Consulta de Pendências")
            try:
                res_pen = supabase.table("pendencias").select("*").execute()
                if res_pen.data:
                    lista = [{"ID": i['id'], "Cliente": i['cliente'], "Documento": i['documento_devido'], "Status": i.get('status','Pendente')} for i in res_pen.data]
                    df_pen = pd.DataFrame(lista)
                    def color_pen(v):
                        if v == 'Entregue': return 'color: #28a745; font-weight: bold;'
                        if v == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                        return ''
                    st.dataframe(df_pen.style.map(color_pen, subset=['Status']), use_container_width=True)
                    st.markdown("---")
                    id_bx_p = st.number_input("ID da Pendência resolvida:", min_value=1, step=1)
                    if st.button("Marcar como Entregue"):
                        supabase.table("pendencias").update({"status": "Entregue"}).eq("id", id_bx_p).execute()
                        st.success("Baixa realizada!")
                        st.rerun()
                else: st.info("Sem pendências.")
            except Exception as e: st.error(f"Erro: {e}")
