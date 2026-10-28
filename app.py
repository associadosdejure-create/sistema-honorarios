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
                            supabase.table("clientes_cadastrados").insert({"nome": c_nome, "cpf_cnpj": c_doc, "telefone": c_tel, "email": c_email, "endereco": c_end, "cidade": c_cidade, "indicado_por": c_ind, "observacoes": c_obs}).execute()
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
                            supabase.table("clientes_cadastrados").update({"nome": e_nome, "cpf_cnpj": e_doc, "telefone": e_tel, "email": e_email, "endereco": e_end, "cidade": e_cidade, "indicado_por": e_ind, "observacoes": e_obs}).eq("id", c_obj['id']).execute()
                            st.cache_data.clear()
                            st.success("Cadastro atualizado com sucesso!")
                            st.rerun()
                        except Exception as e: st.error(f"Erro ao atualizar: {e}")
            else: st.info("Nenhum cliente disponível.")

    elif menu_principal == "Pagamentos":
        if submenu == "Cadastrar Contrato / Parcelas":
            st.header("📝 Cadastrar Novo Contrato Parcelado")
            lista_clientes_db = carregar_clientes()
            nomes_clientes = [c['nome'] for c in lista_clientes_db] if lista_clientes_db else []
