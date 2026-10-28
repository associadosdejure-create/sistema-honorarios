import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Controle DEJURE ADVOCACIA", layout="wide", page_icon="⚖️")

# --- CREDENCIAIS E PERFIS DE ACESSO ---
hashed_passwords = stauth.Hasher.hash_list(['mudar123', 'mudar123', 'bacharel123', 'advogado123', 'estagiario123'])

credentials = {
    "usernames": {
        "nelson": {
            "name": "Nelson Freire Machado",
            "password": hashed_passwords[0],
            "role": "admin"
        },
        "leonidas": {
            "name": "Leônidas da Paz e Silva",
            "password": hashed_passwords[1],
            "role": "admin"
        },
        "bacharel": {
            "name": "Bacharel(a)",
            "password": hashed_passwords[2],
            "role": "bacharel"
        },
        "advogado": {
            "name": "Advogado(a)",
            "password": hashed_passwords[3],
            "role": "advogado"
        },
        "estagiario": {
            "name": "Estagiário(a)",
            "password": hashed_passwords[4],
            "role": "estagiario"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    cookie_name='sistema_honorarios_cookie',
    cookie_key='chave_seguranca_sistema_123',
    cookie_expiry_days=30
)

authenticator.login(
    location='main', 
    fields={'Form name': 'DEJURE ADVOCACIA'}
)

authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

# --- CONTROLE DE FLUXO DA TELA ---
if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    st.warning('Por favor, digite seu usuário e senha para acessar o sistema.')
elif authentication_status == True:
    
    user_role = credentials["usernames"][username]["role"]

    # --- CONEXÃO COM O SUPABASE ---
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # --- BARRA LATERAL (LOGO, LOGOUT E MENUS / SUBMENUS) ---
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
        
        # --- ESTRUTURA DE MENUS E SUBMENUS ---
        menu_principal = st.selectbox("Menu Principal", ["Pagamentos", "Perícias", "Expedientes", "Pendências"])
        
        if menu_principal == "Pagamentos":
            submenu = st.radio(
                "Opções de Pagamentos", 
                ["Cadastrar Cliente", "Ver Parcelas", "Baixar Parcela", "Excluir Contrato"]
            )
        elif menu_principal == "Perícias":
            submenu = st.radio(
                "Opções de Perícias", 
                ["Cadastrar Perícia", "Ver Perícias"]
            )
        elif menu_principal == "Expedientes":
            submenu = st.radio(
                "Opções de Expedientes", 
                ["Cadastrar Expediente", "Consultar Expedientes"]
            )
        elif menu_principal == "Pendências":
            submenu = st.radio(
                "Opções de Pendências", 
                ["Cadastrar Pendência", "Consultar Pendências"]
            )

    # --- TELA PRINCIPAL ---
    st.title(f"Seja bem-vindo, {name}!")
    st.markdown("---")

    # ==========================================
    # VERIFICAÇÃO AUTOMÁTICA DE ALERTAS (PERÍCIAS E EXPEDIENTES)
    # ==========================================
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
            with st.expander("🚨 **CENTRAL DE ALERTAS DE PRAZOS (PERÍCIAS E EXPEDIENTES)**", expanded=True):
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
        pass

    # ==========================================
    # SEÇÃO: PAGAMENTOS
    # ==========================================
    if menu_principal == "Pagamentos":
        
        if submenu == "Cadastrar Cliente":
            st.header("📝 Cadastrar Novo Cliente e Contrato Parcelado")
            
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
                            res = supabase.table("honorarios").insert({
                                "cliente": cliente, 
                                "servico": servico, 
                                "valor_total": float(valor_total)
                            }).execute()
                            
                            if not res.data:
                                st.error("Erro: O Supabase não retornou os dados inseridos.")
                            else:
                                h_id = res.data[0]['id']
                                valor_parcela = valor_total / num_parcelas
                                
                                for i in range(int(num_parcelas)):
                                    vencimento = data_primeira + relativedelta(months=i)
                                    supabase.table("parcelas").insert({
                                        "honorario_id": h_id,
                                        "numero_parcela": f"{i+1}/{int(num_parcelas)}",
                                        "valor": float(valor_parcela),
                                        "vencimento": vencimento.strftime("%Y-%m-%d"),
                                        "status": "Pendente"
                                    }).execute()
                                
                                st.success(f"Sucesso! Honorário de {cliente} cadastrado em {int(num_parcelas)}x de R$ {valor_parcela:.2f}")
                        except Exception as e:
                            st.error(f"Erro detalhado ao salvar no banco: {e}")
                    else:
                        st.error("Por favor, preencha todos os campos corretamente.")

        elif submenu == "Ver Parcelas":
            st.header("📋 Visualizar Parcelas por Cliente")
            
            try:
                res_honorarios = supabase.table("honorarios").select("*").execute()
                
                if res_honorarios.data:
                    clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']} (ID Contrato: {h['id']})": h['id'] for h in res_honorarios.data}
                    
                    cliente_selecionado_txt = st.selectbox("Selecione o Cliente:", options=list(clientes_dict.keys()))
                    
                    if cliente_selecionado_txt:
                        contrato_id_escolhido = clientes_dict[cliente_selecionado_txt]
                        
                        st.markdown("---")
                        res_parcelas = supabase.table("parcelas").select("*").eq("honorario_id", contrato_id_escolhido).execute()
                        
                        if res_parcelas.data:
                            lista_parcelas = []
                            for item in res_parcelas.data:
                                lista_parcelas.append({
                                    "ID Parcela": item['id'],
                                    "Parcela": item['numero_parcela'],
                                    "Valor (R$)": f"R$ {item['valor']:.2f}",
                                    "Vencimento": datetime.strptime(item['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                                    "Status": item['status']
                                })
                            
                            df_p = pd.DataFrame(lista_parcelas)
                            
                            def colorir_status(val):
                                if val == 'Pago':
                                    return 'color: #28a745; font-weight: bold;'
                                elif val == 'Pendente':
                                    return 'color: #dc3545; font-weight: bold;'
                                return ''

                            df_estilizado = df_p.style.map(colorir_status, subset=['Status'])
                            st.dataframe(df_estilizado, use_container_width=True)
                        else:
                            st.info("Este contrato não possui parcelas cadastradas.")
                else:
                    st.info("Nenhum cliente cadastrado até o momento.")
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")

        elif submenu == "Baixar Parcela":
            st.header("🔄 Dar Baixa em Parcela (Marcar como Paga)")
            
            try:
                res_honorarios = supabase.table("honorarios").select("*").execute()
                
                if res_honorarios.data:
                    clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']} (ID Contrato: {h['id']})": h['id'] for h in res_honorarios.data}
                    cliente_selecionado_txt = st.selectbox("Selecione o Cliente:", options=list(clientes_dict.keys()), key="select_baixa_cli")
                    
                    if cliente_selecionado_txt:
                        contrato_id_escolhido = clientes_dict[cliente_selecionado_txt]
                        res_parcelas = supabase.table("parcelas").select("*").eq("honorario_id", contrato_id_escolhido).execute()
                        
                        if res_parcelas.data:
                            lista_parcelas = []
                            for item in res_parcelas.data:
                                lista_parcelas.append({
                                    "ID Parcela": item['id'],
                                    "Parcela": item['numero_parcela'],
                                    "Valor (R$)": f"R$ {item['valor']:.2f}",
                                    "Vencimento": datetime.strptime(item['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                                    "Status": item['status']
                                })
                            
                            df_p = pd.DataFrame(lista_parcelas)
                            def colorir_status(val):
                                if val == 'Pago':
                                    return 'color: #28a745; font-weight: bold;'
                                elif val == 'Pendente':
                                    return 'color: #dc3545; font-weight: bold;'
                                return ''
                            
                            st.dataframe(df_p.style.map(colorir_status, subset=['Status']), use_container_width=True)
                            st.markdown("---")
                            
                            id_baixa = st.number_input("Digite o **ID da Parcela** que deseja dar baixa:", min_value=1, step=1)
                            if st.button("Confirmar Baixa (Marcar como Pago)", type="primary"):
                                supabase.table("parcelas").update({"status": "Pago"}).eq("id", id_baixa).execute()
                                st.success(f"Parcela ID {id_baixa} atualizada para **Pago** com sucesso!")
                                st.rerun()
                        else:
                            st.info("Este contrato não possui parcelas.")
                else:
                    st.info("Nenhum cliente cadastrado.")
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")

        elif submenu == "Excluir Contrato":
            st.header("🗑️ Exclusão de Contratos")
            
            if user_role == 'admin':
                try:
                    res_honorarios = supabase.table("honorarios").select("*").execute()
                    
                    if res_honorarios.data:
                        clientes_dict = {f"{h['cliente']} — Serviço: {h['servico']} (ID Contrato: {h['id']})": h['id'] for h in res_honorarios.data}
                        cliente_selecionado_txt = st.selectbox("Selecione o Contrato a excluir:", options=list(clientes_dict.keys()), key="select_excluir_cli")
                        
                        if cliente_selecionado_txt:
                            contrato_id_escolhido = clientes_dict[cliente_selecionado_txt]
                            
                            st.warning("⚠️ Atenção: A exclusão de um contrato remove permanentemente o registro e todas as suas parcelas associadas.")
                            
                            if st.button("Excluir Definitivamente", type="primary"):
                                supabase.table("honorarios").delete().eq("id", contrato_id_escolhido).execute()
                                st.success("Contrato e parcelas excluídos com sucesso!")
                                st.rerun()
                    else:
                        st.info("Nenhum contrato cadastrado para exclusão.")
                except Exception as e:
                    st.error(f"Erro ao carregar dados: {e}")
            else:
                st.error("🔒 Acesso Restrito. Apenas os sócios administradores possuem permissão para excluir contratos.")

    # ==========================================
    # SEÇÃO: PERÍCIAS
    # ==========================================
    elif menu_principal == "Perícias":
        
        if submenu == "Cadastrar Perícia":
            st.header("🔬 Cadastrar Nova Perícia")
            
            with st.form("form_pericia"):
                cli_pericia = st.text_input("Nome do Parte / Cliente")
                tipo_pericia = st.text_input("Tipo de Perícia (Ex: Médica, Engenharia, Contábil)")
                juizo_vara = st.text_input("Juízo / Vara / Processo")
                honorario_pericial = st.number_input("Valor do Honorário Pericial (R$)", min_value=0.0, format="%.2f")
                data_indicacao = st.date_input("Data da Perícia / Audiência", datetime.now())
                
                submitted_pericia = st.form_submit_button("Salvar Perícia")
                
                if submitted_pericia:
                    if cli_pericia and tipo_pericia:
                        try:
                            res_p = supabase.table("pericias").insert({
                                "cliente": cli_pericia,
                                "tipo_pericia": tipo_pericia,
                                "juizo_vara": juizo_vara,
                                "honorario_pericial": float(honorario_pericial),
                                "data_indicacao": data_indicacao.strftime("%Y-%m-%d"),
                                "status": "Pendente"
                            }).execute()
                            
                            if res_p.data:
                                st.success(f"Perícia de {cli_pericia} cadastrada com sucesso!")
                            else:
                                st.error("Erro ao salvar perícia no Supabase.")
                        except Exception as e:
                            st.error(f"Erro detalhado: {e}")
                    else:
                        st.error("Por favor, preencha pelo menos o Cliente e o Tipo de Perícia.")

        elif submenu == "Ver Perícias":
            st.header("📋 Lista de Perícias Cadastradas")
            
            try:
                res_pericias = supabase.table("pericias").select("*").execute()
                
                if res_pericias.data:
                    lista_pericias = []
                    for item in res_pericias.data:
                        lista_pericias.append({
                            "ID": item['id'],
                            "Cliente": item['cliente'],
                            "Tipo": item['tipo_pericia'],
                            "Juízo/Vara": item.get('juizo_vara', 'N/D'),
                            "Honorário (R$)": f"R$ {item.get('honorario_pericial', 0):.2f}",
                            "Data da Perícia": datetime.strptime(item['data_indicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if item.get('data_indicacao') else 'N/D',
                            "Status": item.get('status', 'Pendente')
                        })
                    
                    df_pericias = pd.DataFrame(lista_pericias)
                    
                    def colorir_status_pericia(val):
                        if val == 'Pago' or val == 'Concluído':
                            return 'color: #28a745; font-weight: bold;'
                        elif val == 'Pendente':
                            return 'color: #dc3545; font-weight: bold;'
                        return ''

                    df_p_estilizado = df_pericias.style.map(colorir_status_pericia, subset=['Status'])
                    st.dataframe(df_p_estilizado, use_container_width=True)
                else:
                    st.info("Nenhuma perícia cadastrada até o momento.")
            except Exception as e:
                st.error(f"Erro ao carregar dados das perícias: {e}")

    # ==========================================
    # SEÇÃO: EXPEDIENTES
    # ==========================================
    elif menu_principal == "Expedientes":
        
        if submenu == "Cadastrar Expediente":
            st.header("📂 Cadastrar Novo Expediente / Prazo")
            
            with st.form("form_expediente"):
                num_processo = st.text_input("Número do Processo")
                cliente_exp = st.text_input("Nome do Cliente")
                descricao_exp = st.text_input("Descrição / Objeto (Ex: Contestação, Apelação)")
                data_manifestacao = st.date_input("Data da Manifestação / Prazo Limite", datetime.now())
                responsavel_exp = st.text_input("Responsável (Ex: Dr. Nelson, Dr. Leônidas)")
                
                submitted_exp = st.form_submit_button("Cadastrar Expediente")
                
                if submitted_exp:
                    if num_processo and cliente_exp and responsavel_exp:
                        try:
                            res_e = supabase.table("expedientes").insert({
                                "numero_processo": num_processo,
                                "cliente": cliente_exp,
                                "descricao": descricao_exp,
                                "data_manifestacao": data_manifestacao.strftime("%Y-%m-%d"),
                                "responsavel": responsavel_exp,
                                "status": "Pendente"
                            }).execute()
                            
                            if res_e.data:
                                st.success(f"Expediente do processo {num_processo} cadastrado com sucesso!")
                            else:
                                st.error("Erro ao salvar expediente no Supabase.")
                        except Exception as e:
                            st.error(f"Erro detalhado: {e}")
                    else:
                        st.error("Por favor, preencha pelo menos o Número do Processo, o Cliente e o Responsável.")

        elif submenu == "Consultar Expedientes":
            st.header("📋 Consulta de Expedientes e Prazos")
            
            try:
                res_expedientes = supabase.table("expedientes").select("*").execute()
                
                if res_expedientes.data:
                    lista_exp = []
                    for item in res_expedientes.data:
                        lista_exp.append({
                            "ID": item['id'],
                            "Processo": item['numero_processo'],
                            "Cliente": item['cliente'],
                            "Descrição": item.get('descricao', 'N/D'),
                            "Data Manifestação": datetime.strptime(item['data_manifestacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if item.get('data_manifestacao') else 'N/D',
                            "Responsável": item['responsavel'],
                            "Status": item.get('status', 'Pendente')
                        })
                    
                    df_exp = pd.DataFrame(lista_exp)
                    
                    def colorir_status_exp(val):
                        if val == 'Protocolado' or val == 'Concluído':
                            return 'color: #28a745; font-weight: bold;'
                        elif val == 'Pendente':
                            return 'color: #dc3545; font-weight: bold;'
                        return ''

                    df_e_estilizado = df_exp.style.map(colorir_status_exp, subset=['Status'])
                    st.dataframe(df_e_estilizado, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("🔄 Dar Baixa / Concluir Expediente")
                    id_baixa_exp = st.number_input("Digite o ID do Expediente protocolado/concluído:", min_value=1, step=1, key="input_baixa_exp")
                    if st.button("Marcar como Protocolado / Concluído"):
                        supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", id_baixa_exp).execute()
                        st.success(f"Expediente ID {id_baixa_exp} atualizado para **Protocolado** com sucesso!")
                        st.rerun()
                else:
                    st.info("Nenhum expediente cadastrado até o momento.")
            except Exception as e:
                st.error(f"Erro ao carregar dados dos expedientes: {e}")

    # ==========================================
    # SEÇÃO: PENDÊNCIAS DE CLIENTES
    # ==========================================
    elif menu_principal == "Pendências":
        
        if submenu == "Cadastrar Pendência":
            st.header("📋 Cadastrar Pendência de Documentação")
            
            with st.form("form_pendencia"):
                cliente_pend = st.text_input("Nome do Cliente")
                processo_pend = st.text_input("Número do Processo (Opcional)")
                documento_devido = st.text_input("Documento Devido (Ex: Procuração assinada, RG/CPF, Comprovante de Residência, Laudo Médico)")
                data_solicitacao = st.date_input("Data da Solicitação", datetime.now())
                
                submitted_pend = st.form_submit_button("Salvar Pendência")
                
                if submitted_pend:
                    if cliente_pend and documento_devido:
                        try:
                            res_pen = supabase.table("pendencias").insert({
                                "cliente": cliente_pend,
                                "processo": processo_pend,
                                "documento_devido": documento_devido,
                                "data_solicitacao": data_solicitacao.strftime("%Y-%m-%d"),
                                "status": "Pendente"
                            }).execute()
                            
                            if res_pen.data:
                                st.success(f"Pendência de documento cadastrada para o cliente {cliente_pend}!")
                            else:
                                st.error("Erro ao salvar pendência no Supabase.")
                        except Exception as e:
                            st.error(f"Erro detalhado: {e}")
                    else:
                        st.error("Por favor, preencha pelo menos o Nome do Cliente e o Documento Devido.")

        elif submenu == "Consultar Pendências":
            st.header("📂 Consulta de Pendências de Documentação")
            
            try:
                res_pendencias = supabase.table("pendencias").select("*").execute()
                
                if res_pendencias.data:
                    lista_pend = []
                    for item in res_pendencias.data:
                        lista_pend.append({
                            "ID": item['id'],
                            "Cliente": item['cliente'],
                            "Processo": item.get('processo', 'N/D'),
                            "Documento Devido": item['documento_devido'],
                            "Solicitação": datetime.strptime(item['data_solicitacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if item.get('data_solicitacao') else 'N/D',
                            "Status": item.get('status', 'Pendente')
                        })
                    
                    df_pend = pd.DataFrame(lista_pend)
                    
                    def colorir_status_pend(val):
                        if val == 'Entregue' or val == 'Concluído':
                            return 'color: #28a745; font-weight: bold;'
                        elif val == 'Pendente':
                            return 'color: #dc3545; font-weight: bold;'
                        return ''

                    df_pen_estilizado = df_pend.style.map(colorir_status_pend, subset=['Status'])
                    st.dataframe(df_pen_estilizado, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("✅ Dar Baixa em Documento Entregue")
                    id_baixa_pen = st.number_input("Digite o ID da Pendência resolvida:", min_value=1, step=1, key="input_baixa_pen")
                    if st.button("Marcar como Entregue"):
                        supabase.table("pendencias").update({"status": "Entregue"}.eq("id", id_baixa_pen).execute()
                        st.success(f"Pendência ID {id_baixa_pen} atualizada para **Entregue** com sucesso!")
                        st.rerun()
                else:
                    st.info("Nenhuma pendência de documento cadastrada até o momento.")
            except Exception as e:
                st.error(f"Erro ao carregar dados das pendências: {e}")
