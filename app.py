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
        except Exception:
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
                submitted = st.form_submit_button("Cadastrar e Gerar Parcelas")
                
                if submitted:
                    if cliente and servico and valor_total > 0:
                        try:
                            res = supabase.table("honorarios").insert({"cliente": cliente, "servico": servico, "valor_total": float(valor_total)}).execute()
                            if not res.data:
                                st.error("Erro: O Supabase não retornou os dados.")
                            else:
                                h_id = res.data[0]['id']
                                valor_parcela = valor_total / num_parcelas
                                for i in range(int(num_parcelas)):
                                    venc = (data_primeira + relativedelta(months=i)).strftime("%Y-%m-%d")
                                    supabase.table("parcelas").insert({"honorario_id": h_id, "numero_parcela": f"{i+1}/{int(num_parcelas)}", "valor": float(valor_parcela), "vencimento": venc, "status": "Pendente"}).execute()
                                st.success(f"Sucesso! Honorário de {cliente} cadastrado.")
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                    else:
                        st.error("Preencha todos os campos.")
                        
        elif submenu == "Ver Parcelas":
            st.header("📋 Visualizar Parcelas")
            try:
                res_honorarios = supabase.table("honorarios").select("*").execute()
                if res_honorarios.data:
                    clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']}": h['id'] for h in res_honorarios.data}
                    cli_sel = st.selectbox("Selecione o Cliente:", options=list(clientes_dict.keys()))
                    if cli_sel:
                        h_id = clientes_dict[cli_sel]
                        st.markdown("---")
                        res_parcelas = supabase.table("parcelas").select("*").eq("honorario_id", h_id).execute()
                        if res_parcelas.data:
                            lista = [{"ID Parcela": p['id'], "Parcela": p['numero_parcela'], "Valor (R$)": f"R$ {p['valor']:.2f}", "Vencimento": datetime.strptime(p['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": p['status']} for p in res_parcelas.data]
                            df_p = pd.DataFrame(lista)
                            def colorir_status(val):
                                if val == 'Pago': return 'color: #28a745; font-weight: bold;'
                                elif val == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                                return ''
                            st.dataframe(df_p.style.map(colorir_status, subset=['Status']), use_container_width=True)
                        else:
                            st.info("Este contrato não possui parcelas.")
                else:
                    st.info("Nenhum cliente cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")
                
        elif submenu == "Baixar Parcela":
            st.header("🔄 Dar Baixa em Parcela")
            try:
                res_honorarios = supabase.table("honorarios").select("*").execute()
                if res_honorarios.data:
                    clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']}": h['id'] for h in res_honorarios.data}
                    cli_sel = st.selectbox("Selecione o Cliente:", options=list(clientes_dict.keys()), key="baixa_cli")
                    if cli_sel:
                        h_id = clientes_dict[cli_sel]
                        res_parcelas = supabase.table("parcelas").select("*").eq("honorario_id", h_id).execute()
                        if res_parcelas.data:
                            lista = [{"ID Parcela": p['id'], "Parcela": p['numero_parcela'], "Valor (R$)": f"R$ {p['valor']:.2f}", "Vencimento": datetime.strptime(p['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"), "Status": p['status']} for p in res_parcelas.data]
                            df_p = pd.DataFrame(lista)
                            def colorir_status(val):
                                if val == 'Pago': return 'color: #28a745; font-weight: bold;'
                                elif val == 'Pendente': return 'color: #dc3545; font-weight: bold;'
                                return ''
                            st.dataframe(df_p.style.map(colorir_status, subset=['Status']), use_container_width=True)
                            st.markdown("---")
                            id_baixa = st.number_input("ID da Parcela para dar baixa:", min_value=1, step=1)
                            if st.button("Confirmar Baixa (Pago)", type="primary"):
                                supabase.table("parcelas").update({"status": "Pago"}).eq("id", id_baixa).execute()
                                st.success(f"Parcela {id_baixa} baixada!")
                                st.rerun()
                        else:
                            st.info("Sem parcelas.")
                else:
                    st.info("Sem clientes.")
            except Exception as e:
                st.error(f"Erro: {e}")
                
        elif submenu == "Excluir Contrato":
            st.header("🗑️ Exclusão de Contratos")
            if user_role == 'admin':
                try:
                    res_honorarios = supabase.table("honorarios").select("*").execute()
                    if res_honorarios.data:
                        clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']}": h['id'] for h in res_honorarios.data}
                        cli_sel = st.selectbox("Contrato a excluir:", options=list(clientes_dict.keys()))
                        if cli_sel:
                            st.warning("⚠️ Atenção: Exclusão permanente.")
                            if st.button("Excluir Definitivamente", type="primary"):
                                supabase.table("honorarios").delete().eq("id", clientes_dict[cli_sel]).execute()
                                st.success("Contrato excluído!")
                                st.rerun()
                    else:
                        st.info("Sem contratos.")
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.error("🔒 Acesso Restrito aos administradores.")
                
    elif menu_principal == "Perícias":
        if submenu == "Cadastrar Perícia":
            st.header("🔬 Cadastrar Nova Perícia")
            with st.form("form_pericia"):
                cli_pericia = st.text_input("Nome do Cliente")
                tipo_pericia = st.text_input("Tipo de Perícia")
                juizo_vara = st.text_input("Juízo / Vara")
                honorario_pericial = st.number_input("Honorário Pericial (R$)", min_value=0.0, format="%.2f")
                data_indicacao = st.date_input("Data da Perícia", datetime.now())
                if st.form_submit_button("Salvar Perícia"):
                    if cli_pericia and tipo_pericia:
                        try:
                            supabase.table("pericias").insert({"cliente": cli_pericia, "tipo_pericia": tipo_pericia, "juizo_vara": juizo_vara, "honorario_pericial": float(honorario_pericial), "data_indicacao": data_indicacao.strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                            st.success("Perícia cadastrada!")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.error("Preencha Cliente e Tipo.")
                        
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
                else:
                    st.info("Nenhuma perícia.")
            except Exception as e:
                st.error(f"Erro: {e}")
                
    elif menu_principal == "Expedientes":
        if submenu == "Cadastrar Expediente":
            st.header("📂 Cadastrar Novo Expediente")
            with st.form("form_expediente"):
                num_processo = st.text_input("Número do Processo")
                cliente_exp = st.text_input("Nome do Cliente")
                descricao_exp = st.text_input("Descrição / Objeto")
                data_manifestacao = st.date_input("Prazo Limite", datetime.now())
                responsavel_exp = st.text_input("Responsável")
                if st.form_submit_button("Cadastrar"):
                    if num_processo and cliente_exp and responsavel_exp:
                        try:
                            supabase.table("expedientes").insert({"numero_processo": num_processo, "cliente": cliente_exp, "descricao": descricao_exp, "data_manifestacao": data_manifestacao.strftime("%Y-%m-%d"), "responsavel": responsavel_exp, "status": "Pendente"}).execute()
                            st.success("Expediente cadastrado!")
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.error("Preencha Processo, Cliente e Responsável.")
                        
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
                    id_baixa = st.number_input("ID do Expediente concluído:", min_value=1, step=1)
                    if st.button("Marcar como Protocolado"):
                        supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", id_baixa).execute()
                        st.success("Atualizado!")
                        st.rerun()
                else:
                    st.info("Nenhum expediente.")
            except Exception as e:
                st.error(f"Erro: {e}")
                
    elif menu_principal == "Pendências":
        if submenu == "Cadastrar Pendência":
            st.header("📋 Cadastrar Pendência")
            with st.form("form_pendencia"):
                cliente_pend = st.text_input("Nome do Cliente")
                processo_pend = st.text_input("Processo (Opcional)")
                doc_1 = st.checkbox("Procuração / RG / CPF")
                doc_2 = st.checkbox("Comprovante de Residência")
                doc_3 = st.checkbox("Laudos / Exames")
                doc_4 = st.text_input("Outro Documento")
                data_sol = st.date_input("Data", datetime.now())
                
                if st.form_submit_button("Salvar Pendência"):
                    if cliente_pend:
                        docs = []
                        if doc_1: docs.append("Procuração/Docs Pessoais")
                        if doc_2: docs.append("Comprovante de Residência")
                        if doc_3: docs.append("Laudos/Exames")
                        if doc_4.strip(): docs.append(doc_4.strip())
                        if docs:
                            try:
                                supabase.table("pendencias").insert({"cliente": cliente_pend, "processo": processo_pend, "documento_devido": " | ".join(docs), "data_solicitacao": data_sol.strftime("%Y-%m-%d"), "status": "Pendente"}).execute()
                                st.success("Pendência cadastrada!")
                            except Exception as e:
                                st.error(f"Erro: {e}")
                        else:
                            st.warning("Selecione ao menos um documento.")
                    else:
                        st.error("Preencha o Nome do Cliente.")
                        
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
                    id_baixa = st.number_input("ID da Pendência resolvida:", min_value=1, step=1)
                    if st.button("Marcar como Entregue"):
                        supabase.table("pendencias").update({"status": "Entregue"}).eq("id", id_baixa).execute()
                        st.success("Baixa realizada!")
                        st.rerun()
                else:
                    st.info("Sem pendências.")
            except Exception as e:
                st.error(f"Erro: {e}")
