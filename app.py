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
        if agora - st.session_state['ultima_atividade'] > TEMPO_MAXIMO:
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

    # --- FUNÇÕES DE CACHE ---
    @st.cache_data(ttl=30)
    def carregar_clientes():
        res = supabase.table("clientes_cadastrados").select("*").execute()
        return res.data if res.data else []

    @st.cache_data(ttl=30)
    def carregar_honorarios():
        res = supabase.table("honorarios").select("*").execute()
        return res.data if res.data else []

    @st.cache_data(ttl=30)
    def carregar_pericias():
        res = supabase.table("pericias").select("*").execute()
        return res.data if res.data else []

    @st.cache_data(ttl=30)
    def carregar_expedientes():
        res = supabase.table("expedientes").select("*").execute()
        return res.data if res.data else []

    @st.cache_data(ttl=30)
    def carregar_pendencias():
        res = supabase.table("pendencias").select("*").execute()
        return res.data if res.data else []

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
        menu_principal = st.selectbox("1️⃣ Módulo Principal:", ["Clientes", "Pagamentos", "Perícias", "Expedientes", "Pendências"])
        
    with col2:
        submenu = ""
        if menu_principal == "Clientes":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Cliente", "Consultar Clientes", "Editar Cliente"])
        elif menu_principal == "Pagamentos":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Contrato / Parcelas", "Ver Parcelas", "Baixar Parcela", "Editar Contrato", "Excluir Contrato"])
        elif menu_principal == "Perícias":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Perícia", "Ver Perícias", "Editar Perícia", "Excluir Perícia"])
        elif menu_principal == "Expedientes":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Expediente", "Consultar Expedientes", "Editar Expediente", "Excluir Expediente"])
        elif menu_principal == "Pendências":
            submenu = st.selectbox("2️⃣ Ação:", ["Cadastrar Pendência", "Consultar Pendências", "Editar Pendência", "Excluir Pendência"])

    st.markdown("---")

    # --- CENTRAL DE ALERTAS ---
    try:
        lista_per = carregar_pericias()
        lista_exp = carregar_expedientes()
        hoje = date.today()
        alertas = []
        
        for p in lista_per:
            if p.get('status') == 'Pendente' and p.get('data_indicacao'):
                dt = datetime.strptime(p['data_indicacao'], "%Y-%m-%d").date()
                dias = (dt - hoje).days
                alertas.append((dias, f"🔬 Perícia | Cliente: {p['cliente']} | Tipo: {p['tipo_pericia']} | Data: {dt.strftime('%d/%m/%Y')}"))
                
        for e in lista_exp:
            if e.get('status') == 'Pendente' and e.get('data_manifestacao'):
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

    # ---------------------------------------------------------
    # MÓDULO CLIENTES
    # ---------------------------------------------------------
    if menu_principal == "Clientes":
        if submenu == "Cadastrar Cliente":
            st.header("👤 Cadastro Completo de Cliente")
            with st.form("form_cad_cliente"):
                c_nome = st.text_input("Nome Completo / Razão Social *")
                c_doc = st.text_input("CPF ou CNPJ")
                c_tel = st.text_input("Telefone / WhatsApp")
                c_email = st.text_input("E-mail")
                c_end = st.text_input("Endereço Completo (Rua, Nº, Bairro)")
                c_cidade = st.text_input("Cidade / UF")
                c_ind = st.text_input("Quem Indicou?")
                c_obs = st.text_area("Observações Importantes")
                
                if st.form_submit_button("Salvar Cadastro do Cliente"):
                    if c_nome:
                        try:
                            dados_cliente = {
                                "nome": c_nome, "cpf_cnpj": c_doc, "telefone": c_tel, "email": c_email,
                                "endereco": c_end, "cidade": c_cidade, "indicado_por": c_ind, "observacoes": c_obs
                            }
                            supabase.table("clientes_cadastrados").insert(dados_cliente).execute()
                            st.cache_data.clear()
                            st.success(f"Cliente **{c_nome}** cadastrado com sucesso!")
                        except Exception as e: st.error(f"Erro ao salvar: {e}")
                    else: st.error("O campo 'Nome' é obrigatório.")

        elif submenu == "Consultar Clientes":
            st.header("📋 Base de Clientes Cadastrados")
            try:
                res_cli = carregar_clientes()
                if res_cli:
                    lista_c = [{"ID": c['id'], "Nome": c['nome'], "Telefone": c.get('telefone', ''), "E-mail": c.get('email', ''), "Cidade": c.get('cidade', ''), "Indicado Por": c.get('indicado_por', '')} for c in res_cli]
                    st.dataframe(pd.DataFrame(lista_c), use_container_width=True)
                else: st.info("Nenhum cliente cadastrado.")
            except Exception as e: st.error(f"Erro: {e}")

        elif submenu == "Editar Cliente":
            st.header("✏️ Editar Cadastro de Cliente")
            res_cli = carregar_clientes()
            if res_cli:
                cdict = {f"ID: {c['id']} — {c['nome']}": c for c in res_cli}
                c_sel_txt = st.selectbox("Selecione o Cliente para Editar:", options=list(cdict.keys()))
                c_obj = cdict[c_sel_txt]
                
                with st.form("form_edit_cliente"):
                    e_nome = st.text_input("Nome Completo / Razão Social", value=c_obj.get('nome', ''))
                    e_doc = st.text_input("CPF ou CNPJ", value=c_obj.get('cpf_cnpj', ''))
                    e_tel = st.text_input("Telefone / WhatsApp", value=c_obj.get('telefone', ''))
                    e_email = st.text_input("E-mail", value=c_obj.get('email', ''))
                    e_end = st.text_input("Endereço Completo", value=c_obj.get('endereco', ''))
                    e_cidade = st.text_input("Cidade / UF", value=c_obj.get('cidade', ''))
                    e_ind = st.text_input("Quem Indicou?", value=c_obj.get('indicado_por', ''))
                    e_obs = st.text_area("Observações", value=c_obj.get('observacoes', ''))
                    
                    if st.form_submit_button("Salvar Alterações"):
                        try:
                            supabase.table("clientes_cadastrados").update({
                                "nome": e_nome, "cpf_cnpj": e_doc, "telefone": e_tel, "email": e_email,
                                "endereco": e_end, "cidade": e_cidade, "indicado_por": e_ind, "observacoes": e_obs
                            }).eq("id", c_obj['id']).execute()
                            st.cache_data.clear()
                            st.success("Cadastro do cliente atualizado com sucesso!")
                            st.rerun()
                        except Exception as e: st.error(f"Erro ao atualizar: {e}")
            else: st.info("Nenhum cliente disponível para edição.")

    # ---------------------------------------------------------
    # MÓDULO PAGAMENTOS
    # ---------------------------------------------------------
    elif menu_principal == "Pagamentos":
        if submenu == "Cadastrar Contrato / Parcelas":
            st.header("📝 Cadastrar Novo Contrato Parcelado")
            lista_clientes_db = carregar_clientes()
            nomes_clientes = [c['nome'] for c in lista_clientes_db] if lista_clientes_db else []
            
            with st.form("form_honorario"):
                cliente_opcao = st.selectbox("Cliente:", ["Outro (Digitar manualmente)"] + nomes_clientes) if nomes_clientes else "Outro (Digitar manualmente)"
                cliente = st.text_input("Nome do Cliente") if cliente_opcao == "Outro (Digitar manualmente)" else cliente_opcao
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
                                    supabase.table("parcelas").insert({"honorario_id": h_id, "numero_parcela": f"{i+1}/{int(num_parcelas)}", "valor": float(vp), "vencimento": venc, "status": "Pendente"}).execute()
                                st.cache_data.clear()
                                st.success(f"Contrato de {cliente} cadastrado!")
                        except Exception as e: st.error(f"Erro: {e}")
                    else: st.error("Preencha todos os campos.")
                        
        elif submenu == "Ver Parcelas":
            st.header("📋 Visualizar Parcelas")
            try:
                res_h = carregar_honorarios()
                if res_h:
                    cdict = {f"{h['cliente']} — Serv: {h['servico']}": h['id'] for h in res_h}
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
                else: st.info("Nenhum contrato.")
            except Exception as e: st.error(f"Erro: {e}")
                
        elif submenu == "Baixar Parcela":
            st.header("🔄 Dar Baixa em Parcela")
            try:
                res_h = carregar_honorarios()
                if res_h:
                    cdict = {f"{h['cliente']} — Serv: {h['servico']}": h['id'] for h in res_h}
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
                                st.cache_data.clear()
                                st.success(f"Parcela {id_bx} baixada!")
                                st.rerun()
                        else: st.info("Sem parcelas.")
                else: st.info("Sem contratos.")
            except Exception as e: st.error(f"Erro: {e}")

        elif submenu == "Editar Contrato":
            st.header("✏️ Editar Contrato / Honorário")
            res_h = carregar_honorarios()
            if res_h:
                hdict = {f"ID: {h['id']} | Cliente: {h['cliente']} — Serv: {h['servico']}": h for h in res_h}
                h_sel = st.selectbox("Selecione o Contrato para Editar:", options=list(hdict.keys()))
                h_obj = hdict[h_sel]
                
                with st.form("form_edit_honorario"):
                    eh_cli = st.text_input("Nome do Cliente", value=h_obj.get('cliente', ''))
                    eh_serv = st.text_input("Descrição do Serviço", value=h_obj.get('servico', ''))
                    eh_val = st.number_input("Valor Total (R$)", min_value=0.0, value=float(h_obj.get('valor_total', 0.0)), format="%.2f")
                    
                    if st.form_submit_button("Salvar Alterações do Contrato"):
                        try:
                            supabase.table("honorarios").update({
                                "cliente": eh_cli, "servico": eh_serv, "valor_total": float(eh_val)
                            }).eq("id", h_obj['id']).execute()
                            st.cache_data.clear()
                            st.success("Contrato atualizado com sucesso!")
                            st.rerun()
                        except Exception as e: st.error(f"Erro ao atualizar: {e}")
            else: st.info("Nenhum contrato cadastrado.")
                
        elif submenu == "Excluir Contrato":
            st.header("🗑️ Exclusão de Contratos e Honorários")
            if user_role == 'admin':
                try:
                    res_h = carregar_honorarios()
                    if res_h:
                        cdict = {f"{h['cliente']} — Serv: {h['servico']} (ID: {h['id']})": h['id'] for h in res_h}
                        cli_sel = st.selectbox("Selecione o Contrato a excluir:", options=list(cdict.keys()))
                        if cli_sel:
                            st.warning("⚠️ Atenção: A exclusão remove permanentemente o contrato e todas as parcelas associadas.")
                            confirmar_exc = st.checkbox("Confirmo que deseja excluir permanentemente este contrato.")
                            if confirmar_exc:
                                if st.button("🚨 EXCLUIR DEFINITIVAMENTE", type="primary"):
                                    supabase.table("honorarios").delete().eq("id", cdict[cli_sel]).execute()
                                    st.cache_data.clear()
                                    st.success("Contrato excluído com sucesso!")
                                    st.rerun()
                    else: st.info("Sem contratos.")
                except Exception as e: st.error(f"Erro: {e}")
            else: st.error("🔒 Acesso Restrito aos administradores.")
                
    # ---------------------------------------------------------
    # MÓDULO PERÍCIAS
    # ---------------------------------------------------------
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
                            st.cache_data.clear()
                            st.success("Perícia cadastrada!")
                        except Exception as e: st.error(f"Erro: {e}")
                    else: st.error("Preencha Cliente e Tipo.")
                        
        elif submenu == "Ver Perícias":
            st.header("📋 Lista de Perícias")
            try:
                res_p = carregar_pericias()
                if res_p:
                    lista = [{"ID": i['id'], "Cliente": i['cliente'], "Tipo": i['tipo_pericia'], "
