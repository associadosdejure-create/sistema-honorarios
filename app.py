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

    # --- INICIALIZAÇÃO DE ESTADOS DE NAVEGAÇÃO ---
    if 'pagina_atual' not in st.session_state:
        st.session_state['pagina_atual'] = "🏠 Página Inicial"

    if 'submenu_atual' not in st.session_state:
        st.session_state['submenu_atual'] = ""

    # --- FUNÇÃO DE VALIDAÇÃO DE CPF ---
    def validar_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        if digito1 == 10: digito1 = 0
        if digito1 != int(cpf[9]): return False
        
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        if digito2 == 10: digito2 = 0
        if digito2 != int(cpf[10]): return False
        return True

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
        
        # --- MENU PRINCIPAL EM LINKS (SIDEBAR) ---
        st.subheader("🧭 Módulos do Sistema")
        
        if st.button("🏠 Página Inicial", use_container_width=True):
            st.session_state['pagina_atual'] = "🏠 Página Inicial"
            st.session_state['submenu_atual'] = ""
            st.rerun()
        if st.button("👥 Clientes", use_container_width=True):
            st.session_state['pagina_atual'] = "Clientes"
            st.session_state['submenu_atual'] = "Consultar Clientes"
            st.rerun()
        if st.button("💰 Pagamentos", use_container_width=True):
            st.session_state['pagina_atual'] = "Pagamentos"
            st.session_state['submenu_atual'] = "Ver Parcelas"
            st.rerun()
        if st.button("🔬 Perícias", use_container_width=True):
            st.session_state['pagina_atual'] = "Perícias"
            st.session_state['submenu_atual'] = "Ver Perícias"
            st.rerun()
        if st.button("📂 Expedientes", use_container_width=True):
            st.session_state['pagina_atual'] = "Expedientes"
            st.session_state['submenu_atual'] = "Consultar Expedientes"
            st.rerun()
        if st.button("📋 Pendências", use_container_width=True):
            st.session_state['pagina_atual'] = "Pendências"
            st.session_state['submenu_atual'] = "Consultar Pendências"
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"⏳ **Sessão expira em:**\n### `{minutos_restantes:02d}:{segundos_restantes:02d}`")
        st.caption("*(Atualiza a cada clique / ação)*")
        st.markdown("---")

        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        try: st.image("logo.png", use_container_width=True)
        except Exception: st.write("⚖️ **Dejure Advocacia**")

    menu_escolha = st.session_state['pagina_atual']

    # ==========================================
    # PÁGINA INICIAL (DASHBOARD ANTECEDENTE)
    # ==========================================
    if menu_escolha == "🏠 Página Inicial":
        st.title(f"Seja bem-vindo, {name}! ⚖️")
        st.markdown("### 📊 Visão Geral do Escritório")
        
        try:
            total_cli = len(carregar_clientes())
            total_hon = len(carregar_honorarios())
            total_per = len([p for p in carregar_pericias() if p.get('status') == 'Pendente'])
            total_exp = len([e for e in carregar_expedientes() if e.get('status') == 'Pendente'])
            total_pen = len([pn for pn in carregar_pendencias() if pn.get('status') == 'Pendente'])
            
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            col_m1.metric("Clientes", total_cli)
            col_m2.metric("Contratos", total_hon)
            col_m3.metric("Perícias Pend.", total_per)
            col_m4.metric("Expedientes Pend.", total_exp)
            col_m5.metric("Pendências Doc.", total_pen)
        except Exception:
            pass

        st.markdown("---")

        try:
            lista_per = carregar_pericias()
            lista_exp = carregar_expedientes()
            hoje = date.today()
            alertas = []
            
            for p in lista_per:
                if p.get('status') == 'Pendente' and p.get('data_indicacao'):
                    dt = datetime.strptime(p['data_indicacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas.append((dias, f"🔬 Perícia | Cliente: {p['cliente']} | Tipo: {p['tipo_pericia']} | Data: {dt.strftime('%d/%m/%Y')}", p['id'], 'pericia'))
                    
            for e in lista_exp:
                if e.get('status') == 'Pendente' and e.get('data_manifestacao'):
                    dt = datetime.strptime(e['data_manifestacao'], "%Y-%m-%d").date()
                    dias = (dt - hoje).days
                    alertas.append((dias, f"📂 Expediente | Processo: {e['numero_processo']} | Prazo: {dt.strftime('%d/%m/%Y')} | Resp: {e['responsavel']}", e['id'], 'expediente'))
                    
            if alertas:
                col_alerta_1, col_alerta_2 = st.columns([0.80, 0.20])
                with col_alerta_1:
                    st.subheader("🚨 Central de Alertas de Prazos")
                with col_alerta_2:
                    if st.button("🗑️ Excluir Alertas", type="primary"):
                        for _, _, item_id, tipo in alertas:
                            if tipo == 'pericia':
                                supabase.table("pericias").update({"status": "Concluído"}).eq("id", item_id).execute()
                            elif tipo == 'expediente':
                                supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", item_id).execute()
                        st.cache_data.clear()
                        st.success("Alertas excluídos/baixados com sucesso!")
                        st.rerun()

                with st.expander("📌 **Ver Lista de Alertas Ativos**", expanded=True):
                    for dias, texto, _, _ in sorted(alertas, key=lambda x: x[0]):
                        if dias < 0: st.error(f"⚠️ **VENCIDO ({abs(dias)} dias):** {texto}")
                        elif dias == 1: st.error(f"🚨 **CRÍTICO (1 dia):** {texto}")
                        elif dias <= 3: st.warning(f"⚠️ **URGENTE ({dias} dias):** {texto}")
                        elif dias <= 7: st.info(f"📅 **LEMBRETE ({dias} dias):** {texto}")
            else:
                st.info("🎉 Nenhum alerta de prazo pendente para hoje!")
        except Exception:
            pass

        st.markdown("---")
        st.info("💡 **Dica:** Utilize os botões do menu lateral esquerdo para acessar e gerenciar os módulos.")

    # ==========================================
    # MÓDULOS DE NAVEGAÇÃO PRINCIPAL (EM LINKS)
    # ==========================================
    else:
        menu_principal = menu_escolha
        st.title(f"Módulo: {menu_principal} ⚖️")

        # --- SUBMENUS EM FORMATO DE LINKS (BOTÕES HORIZONTAIS) ---
        if menu_principal == "Clientes":
            acoes = ["Consultar Clientes", "Cadastrar Cliente", "Editar Cliente", "Excluir Cliente", "Exportar Base (Backup)"]
        elif menu_principal == "Pagamentos":
            acoes = ["Ver Parcelas", "Cadastrar Contrato / Parcelas", "Baixar Parcela", "Editar Contrato", "Excluir Contrato"]
        elif menu_principal == "Perícias":
            acoes = ["Ver Perícias", "Cadastrar Perícia", "Editar Perícia", "Excluir Perícia"]
        elif menu_principal == "Expedientes":
            acoes = ["Consultar Expedientes", "Cadastrar Expediente", "Editar Expediente", "Excluir Expediente"]
        elif menu_principal == "Pendências":
            acoes = ["Consultar Pendências", "Cadastrar Pendência", "Editar Pendência", "Excluir Pendência"]

        if not st.session_state['submenu_atual'] or st.session_state['submenu_atual'] not in acoes:
            st.session_state['submenu_atual'] = acoes[0]

        # Exibe os links de ações na parte superior do módulo
        cols = st.columns(len(acoes))
        for idx, acao in enumerate(acoes):
            with cols[idx]:
                tipo_btn = "primary" if st.session_state['submenu_atual'] == acao else "secondary"
                if st.button(acao, use_container_width=True, type=tipo_btn):
                    st.session_state['submenu_atual'] = acao
                    st.rerun()

        st.markdown("---")
        submenu = st.session_state['submenu_atual']

        # --- LÓGICA DE CADA SUBMENU ---
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
                    c_gov = st.text_input("Senha Gov.br")
                    c_ind = st.text_input("Quem Indicou?")
                    c_obs = st.text_area("Observações Importantes")
                    
                    if st.form_submit_button("Salvar Cadastro do Cliente"):
                        if not c_nome:
                            st.error("O campo 'Nome Completo / Razão Social' é obrigatório.")
                        else:
                            doc_limpo = ''.join(filter(str.isdigit, str(c_doc)))
                            if len(doc_limpo) == 11 and not validar_cpf(doc_limpo):
                                st.error("⚠️ **CPF INVÁLIDO!** O número digitado não corresponde a um CPF válido. Verifique os dígitos.")
                            else:
                                try:
                                    supabase.table("clientes_cadastrados").insert({
                                        "nome": c_nome, "cpf_cnpj": c_doc, "telefone": c_tel, 
                                        "email": c_email, "endereco": c_end, "cidade": c_cidade, 
                                        "senha_gov": c_gov, "indicado_por": c_ind, "observacoes": c_obs
                                    }).execute()
                                    st.cache_data.clear()
                                    st.success(f"Cliente **{c_nome}** cadastrado com sucesso!")
                                except Exception as e: st.error(f"Erro ao salvar: {e}")

            elif submenu == "Consultar Clientes":
                st.header("📋 Base de Clientes Cadastrados")
                try:
                    res_cli = carregar_clientes()
                    if res_cli:
                        lista_c = [{
                            "ID": c['id'], "Nome": c['nome'], "CPF/CNPJ": c.get('cpf_cnpj', ''), 
                            "Telefone": c.get('telefone', ''), "E-mail": c.get('email', ''), 
                            "Cidade": c.get('cidade', ''), "Senha Gov": c.get('senha_gov', ''), 
                            "Indicado Por": c.get('indicado_por', '')
                        } for c in res_cli]
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
                        e_gov = st.text_input("Senha Gov.br", value=c_obj.get('senha_gov', ''))
                        e_ind = st.text_input("Quem Indicou?", value=c_obj.get('indicado_por', ''))
                        e_obs = st.text_area("Observações", value=c_obj.get('observacoes', ''))
                        
                        if st.form_submit_button("Salvar Alterações"):
                            doc_limpo = ''.join(filter(str.isdigit, str(e_doc)))
                            if len(doc_limpo) == 11 and not validar_cpf(doc_limpo):
                                st.error("⚠️ **CPF INVÁLIDO!** O número digitado não corresponde a um CPF válido.")
                            else:
                                try:
                                    supabase.table("clientes_cadastrados").update({
                                        "nome": e_nome, "cpf_cnpj": e_doc, "telefone": e_tel, 
                                        "email": e_email, "endereco": e_end, "cidade": e_cidade, 
                                        "senha_gov": e_gov, "indicado_por": e_ind, "observacoes": e_obs
                                    }).eq("id", c_obj['id']).execute()
                                    st.cache_data.clear()
                                    st.success("Cadastro atualizado com sucesso!")
                                    st.rerun()
                                except Exception as e: st.error(f"Erro ao atualizar: {e}")
                else: st.info("Nenhum cliente disponível.")

            elif submenu == "Excluir Cliente":
                st.header("🗑️ Exclusão de Clientes")
                if user_role == 'admin':
                    try:
                        res_cli = carregar_clientes()
                        if res_cli:
                            cdict = {f"ID: {c['id']} — {c['nome']}": c['id'] for c in res_cli}
                            c_sel = st.selectbox("Selecione o Cliente a excluir:", options=list(cdict.keys()))
                            if c_sel:
                                st.warning("⚠️ Atenção: A exclusão deste cliente do cadastro geral é irreversível.")
                                conf_cli = st.checkbox("Confirmo que desejo excluir permanentemente este cliente.")
                                if conf_cli:
                                    if st.button("🚨 EXCLUIR CLIENTE", type="primary"):
                                        supabase.table("clientes_cadastrados").delete().eq("id", cdict[c_sel]).execute()
                                        st.cache_data.clear()
                                        st.success("Cliente excluído com sucesso!")
                                        st.rerun()
                        else: st.info("Nenhum cliente cadastrado.")
                    except Exception as e: st.error(f"Erro: {e}")
                else: st.error("🔒 Acesso Restrito aos administradores.")

            elif submenu == "Exportar Base (Backup)":
                st.header("📥 Exportar Base de Dados de Clientes")
                st.write("Clique no botão abaixo para baixar todos os clientes cadastrados em formato de planilha (CSV):")
                try:
                    res_cli = carregar_clientes()
                    if res_cli:
                        df_export = pd.DataFrame(res_cli)
                        csv_data = df_export.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Baixar Planilha de Clientes (CSV)",
                            data=csv_data,
                            file_name=f"clientes_dejure_{date.today().strftime('%Y-%m-%d')}.csv",
                            mime="text/csv",
                            type="primary"
                        )
                    else:
                        st.info("Nenhum cliente cadastrado para exportar.")
                except Exception as e:
                    st.error(f"Erro ao gerar exportação: {e}")

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
                                st.dataframe(pd.DataFrame(lista), use_container_width=True)
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
                                st.dataframe(pd.DataFrame(lista), use_container_width=True)
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
                        
                        if st.form_submit_button("Salvar Alterações"):
                            try:
                                supabase.table("honorarios").update({"cliente": eh_cli, "servico": eh_serv, "valor_total": float(eh_val)}).eq("id", h_obj['id']).execute()
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
                                confirmar_exc = st.checkbox("Confirmo que desejo excluir permanentemente este contrato.")
                                if confirmar_exc:
                                    if st.button("🚨 EXCLUIR DEFINITIVAMENTE", type="primary"):
                                        supabase.table("honorarios").delete().eq("id", cdict[cli_sel]).execute()
                                        st.cache_data.clear()
                                        st.success("Contrato excluído com sucesso!")
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
                                st.cache_data.clear()
                                st.success("Perícia cadastrada!")
                            except Exception as e: st.error(f"Erro: {e}")
                        else: st.error("Preencha Cliente e Tipo.")
                            
            elif submenu == "Ver Perícias":
                st.header("📋 Lista de Perícias")
                try:
                    res_p = carregar_pericias()
                    if res_p:
                        lista = []
                        for i in res_p:
                            dt_fmt = datetime.strptime(i['data_indicacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if i.get('data_indicacao') else ""
                            lista.append({"ID": i['id'], "Cliente": i['cliente'], "Tipo": i['tipo_pericia'], "Juízo": i.get('juizo_vara',''), "Valor": f"R$ {i.get('honorario_pericial',0):.2f}", "Data": dt_fmt, "Status": i.get('status','Pendente')})
                        st.dataframe(pd.DataFrame(lista), use_container_width=True)
                    else: st.info("Nenhuma perícia.")
                except Exception as e: st.error(f"Erro: {e}")

            elif submenu == "Editar Perícia":
                st.header("✏️ Editar Perícia")
                res_p = carregar_pericias()
                if res_p:
                    pdict = {f"ID: {i['id']} | Cliente: {i['cliente']} | Tipo: {i['tipo_pericia']}": i for i in res_p}
                    p_sel = st.selectbox("Selecione a Perícia para Editar:", options=list(pdict.keys()))
                    p_obj = pdict[p_sel]
                    
                    with st.form("form_edit_pericia"):
                        ep_cli = st.text_input("Nome do Cliente", value=p_obj.get('cliente', ''))
                        ep_tipo = st.text_input("Tipo de Perícia", value=p_obj.get('tipo_pericia', ''))
                        ep_juizo = st.text_input("Juízo / Vara", value=p_obj.get('juizo_vara', ''))
                        ep_val = st.number_input("Honorário Pericial (R$)", min_value=0.0, value=float(p_obj.get('honorario_pericial', 0.0)), format="%.2f")
                        
                        dt_atual = datetime.strptime(p_obj['data_indicacao'], "%Y-%m-%d").date() if p_obj.get('data_indicacao') else date.today()
                        ep_dt = st.date_input("Data da Perícia", value=dt_atual)
                        ep_status = st.selectbox("Status", ["Pendente", "Concluído", "Pago"], index=0 if p_obj.get('status') == 'Pendente' else 1)
                        
                        if st.form_submit_button("Salvar Alterações"):
                            try:
                                supabase.table("pericias").update({"cliente": ep_cli, "tipo_pericia": ep_tipo, "juizo_vara": ep_juizo, "honorario_pericial": float(ep_val), "data_indicacao": ep_dt.strftime("%Y-%m-%d"), "status": ep_status}).eq("id", p_obj['id']).execute()
                                st.cache_data.clear()
                                st.success("Perícia atualizada com sucesso!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro ao atualizar: {e}")
                else: st.info("Nenhuma perícia cadastrada.")

            elif submenu == "Excluir Perícia":
                st.header("🗑️ Exclusão de Perícias")
                try:
                    res_p = carregar_pericias()
                    if res_p:
                        pdict = {f"ID: {i['id']} | Cliente: {i['cliente']} | Tipo: {i['tipo_pericia']}": i['id'] for i in res_p}
                        p_sel = st.selectbox("Selecione a Perícia a excluir:", options=list(pdict.keys()))
                        if p_sel:
                            st.warning("⚠️ Atenção: A exclusão desta perícia é irreversível.")
                            conf_p = st.checkbox("Confirmo que desejo excluir esta perícia.")
                            if conf_p:
                                if st.button("🚨 EXCLUIR PERÍCIA", type="primary"):
                                    supabase.table("pericias").delete().eq("id", pdict[p_sel]).execute()
                                    st.cache_data.clear()
                                    st.success("Perícia excluída com sucesso!")
                                    st.rerun()
                    else: st.info("Nenhuma perícia cadastrada.")
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
                                st.cache_data.clear()
                                st.success("Expediente cadastrado!")
                            except Exception as e: st.error(f"Erro: {e}")
                        else: st.error("Preencha Processo, Cliente e Responsável.")
                            
            elif submenu == "Consultar Expedientes":
                st.header("📋 Consulta de Expedientes")
                try:
                    res_e = carregar_expedientes()
                    if res_e:
                        lista = []
                        for i in res_e:
                            dt_fmt = datetime.strptime(i['data_manifestacao'], "%Y-%m-%d").strftime("%d/%m/%Y") if i.get('data_manifestacao') else ""
                            lista.append({"ID": i['id'], "Processo": i['numero_processo'], "Cliente": i['cliente'], "Prazo": dt_fmt, "Status": i.get('status','Pendente')})
                        st.dataframe(pd.DataFrame(lista), use_container_width=True)
                        st.markdown("---")
                        id_bx_e = st.number_input("ID do Expediente concluído:", min_value=1, step=1)
                        if st.button("Marcar como Protocolado"):
                            supabase.table("expedientes").update({"status": "Protocolado"}).eq("id", id_bx_e).execute()
                            st.cache_data.clear()
                            st.success("Atualizado!")
                            st.rerun()
                    else: st.info("Nenhum expediente.")
                except Exception as e: st.error(f"Erro: {e}")

            elif submenu == "Editar Expediente":
                st.header("✏️ Editar Expediente / Prazo")
                res_e = carregar_expedientes()
                if res_e:
                    edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} | Cliente: {i['cliente']}": i for i in res_e}
                    e_sel = st.selectbox("Selecione o Expediente para Editar:", options=list(edict.keys()))
                    e_obj = edict[e_sel]
                    
                    with st.form("form_edit_expediente"):
                        ee_proc = st.text_input("Número do Processo", value=e_obj.get('numero_processo', ''))
                        ee_cli = st.text_input("Nome do Cliente", value=e_obj.get('cliente', ''))
                        ee_desc = st.text_input("Descrição / Objeto", value=e_obj.get('descricao', ''))
                        
                        dt_atual_e = datetime.strptime(e_obj['data_manifestacao'], "%Y-%m-%d").date() if e_obj.get('data_manifestacao') else date.today()
                        ee_dt = st.date_input("Prazo Limite", value=dt_atual_e)
                        ee_resp = st.text_input("Responsável", value=e_obj.get('responsavel', ''))
                        ee_status = st.selectbox("Status", ["Pendente", "Protocolado", "Concluído"], index=0 if e_obj.get('status') == 'Pendente' else 1)
                        
                        if st.form_submit_button("Salvar Alterações"):
                            try:
                                supabase.table("expedientes").update({"numero_processo": ee_proc, "cliente": ee_cli, "descricao": ee_desc, "data_manifestacao": ee_dt.strftime("%Y-%m-%d"), "responsavel": ee_resp, "status": ee_status}).eq("id", e_obj['id']).execute()
                                st.cache_data.clear()
                                st.success("Expediente atualizado com sucesso!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro ao atualizar: {e}")
                else: st.info("Nenhum expediente cadastrado.")

            elif submenu == "Excluir Expediente":
                st.header("🗑️ Exclusão de Expedientes")
                try:
                    res_e = carregar_expedientes()
                    if res_e:
                        edict = {f"ID: {i['id']} | Proc: {i['numero_processo']} | Cliente: {i['cliente']}": i['id'] for i in res_e}
                        e_sel = st.selectbox("Selecione o Expediente a excluir:", options=list(edict.keys()))
                        if e_sel:
                            st.warning("⚠️ Atenção: A exclusão deste expediente é irreversível.")
                            conf_e = st.checkbox("Confirmo que desejo excluir este expediente.")
                            if conf_e:
                                if st.button("🚨 EXCLUIR EXPEDIENTE", type="primary"):
                                    supabase.table("expedientes").delete().eq("id", edict[e_sel]).execute()
                                    st.cache_data.clear()
                                    st.success("Expediente excluído com sucesso!")
                                    st.rerun()
                    else: st.info("Nenhum expediente cadastrado.")
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
                                    st.cache_data.clear()
                                    st.success("Pendência cadastrada!")
                                except Exception as e: st.error(f"Erro: {e}")
                            else: st.warning("Selecione ao menos um documento.")
                        else: st.error("Preencha o Nome do Cliente.")
                            
            elif submenu == "Consultar Pendências":
                st.header("📂 Consulta de Pendências")
                try:
                    res_pen = carregar_pendencias()
                    if res_pen:
                        lista = [{"ID": i['id'], "Cliente": i['cliente'], "Documento": i['documento_devido'], "Status": i.get('status','Pendente')} for i in res_pen]
                        st.dataframe(pd.DataFrame(lista), use_container_width=True)
                        st.markdown("---")
                        id_bx_p = st.number_input("ID da Pendência resolvida:", min_value=1, step=1)
                        if st.button("Marcar como Entregue"):
                            supabase.table("pendencias").update({"status": "Entregue"}).eq("id", id_bx_p).execute()
                            st.cache_data.clear()
                            st.success("Baixa realizada!")
                            st.rerun()
                    else: st.info("Sem pendências.")
                except Exception as e: st.error(f"Erro: {e}")

            elif submenu == "Editar Pendência":
                st.header("✏️ Editar Pendência de Documento")
                res_pen = carregar_pendencias()
                if res_pen:
                    pdict = {f"ID: {i['id']} | Cliente: {i['cliente']} | Doc: {i['documento_devido']}": i for i in res_pen}
                    p_sel = st.selectbox("Selecione a Pendência para Editar:", options=list(pdict.keys()))
                    p_obj = pdict[p_sel]
                    
                    with st.form("form_edit_pendencia"):
                        ep_cli = st.text_input("Nome do Cliente", value=p_obj.get('cliente', ''))
                        ep_proc = st.text_input("Processo", value=p_obj.get('processo', ''))
                        ep_docs = st.text_input("Documento(s) Devido(s)", value=p_obj.get('documento_devido', ''))
                        ep_status = st.selectbox("Status", ["Pendente", "Entregue"], index=0 if p_obj.get('status') == 'Pendente' else 1)
                        
                        if st.form_submit_button("Salvar Alterações"):
                            try:
                                supabase.table("pendencias").update({"cliente": ep_cli, "processo": ep_proc, "documento_devido": ep_docs, "status": ep_status}).eq("id", p_obj['id']).execute()
                                st.cache_data.clear()
                                st.success("Pendência atualizada com sucesso!")
                                st.rerun()
                            except Exception as e: st.error(f"Erro ao atualizar: {e}")
                else: st.info("Nenhuma pendência cadastrada.")

            elif submenu == "Excluir Pendência":
                st.header("🗑️ Exclusão de Pendências")
                try:
                    res_pen = carregar_pendencias()
                    if res_pen:
                        pdict = {f"ID: {i['id']} | Cliente: {i['cliente']} | Doc: {i['documento_devido']}": i['id'] for i in res_pen}
                        p_sel = st.selectbox("Selecione a Pendência a excluir:", options=list(pdict.keys()))
                        if p_sel:
                            st.warning("⚠️ Atenção: A exclusão desta pendência é irreversível.")
                            conf_pen = st.checkbox("Confirmo que desejo excluir esta pendência.")
                            if conf_pen:
                                if st.button("🚨 EXCLUIR PENDÊNCIA", type="primary"):
                                    supabase.table("pendencias").delete().eq("id", pdict[p_sel]).execute()
                                    st.cache_data.clear()
                                    st.success("Pendência excluída com sucesso!")
                                    st.rerun()
                    else: st.info("Nenhuma pendência cadastrada.")
                except Exception as e: st.error(f"Erro: {e}")
