import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Controle de Honorários", layout="wide", page_icon="⚖️")

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

# Renderiza o login na tela principal
authenticator.login(location='main')

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

    # --- BARRA LATERAL (LOGO, LOGOUT E MENU) ---
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
        
        # Botão de logout oficial da biblioteca
        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.write("⚖️ **Dejure Advocacia**")
        
        st.markdown("---")
        menu = st.radio("Navegação", ["Cadastrar Honorário", "Ver Parcelas e Baixas"])

    # --- TELA PRINCIPAL ---
    st.title(f"Seja bem-vindo, {name}!")
    st.markdown("---")

    if menu == "Cadastrar Honorário":
        st.header("📝 Cadastrar Novo Pagamento Parcelado")
        
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

    elif menu == "Ver Parcelas e Baixas":
        st.header("📋 Gestão de Parcelas e Contratos")
        
        try:
            res = supabase.table("parcelas").select("*, honorarios(id, cliente, servico)").execute()
            if res.data:
                lista_dados = []
                for item in res.data:
                    cli = item.get('honorarios') or {}
                    lista_dados.append({
                        "ID Parcela": item['id'],
                        "ID Honorário": cli.get('id'),
                        "Cliente": cli.get('cliente', 'N/D'),
                        "Serviço": cli.get('servico', 'N/D'),
                        "Parcela": item['numero_parcela'],
                        "Valor (R$)": f"R$ {item['valor']:.2f}",
                        "Vencimento": datetime.strptime(item['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                        "Status": item['status']
                    })
                
                df = pd.DataFrame(lista_dados)
                
                # --- FUNÇÃO DE ESTILO PARA A TABELA ---
                def colorir_status(val):
                    if val == 'Pago':
                        return 'color: #28a745; font-weight: bold;'  # Verde
                    elif val == 'Pendente':
                        return 'color: #dc3545; font-weight: bold;'  # Vermelho
                    return ''

                # Aplica o estilo na coluna 'Status'
                df_estilizado = df.style.map(colorir_status, subset=['Status'])
                
                # Exibe a tabela formatada
                st.dataframe(df_estilizado, use_container_width=True)
                
                st.markdown("---")
                
                # --- CONTROLE DE PERMISSÕES NA TELA DE GESTÃO ---
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔄 Dar baixa em parcela")
                    id_baixa = st.number_input("Digite o ID da parcela paga:", min_value=1, step=1, key="input_baixa")
                    if st.button("Marcar como Pago"):
                        supabase.table("parcelas").update({"status": "Pago"}).eq("id", id_baixa).execute()
                        st.success("Status atualizado com sucesso!")
                        st.rerun()
                
                with col2:
                    st.subheader("🗑️ Excluir Contrato Inteiro")
                    if user_role == 'admin':
                        st.caption("Remove o contrato e todas as suas parcelas.")
                        id_excluir = st.number_input("Digite o ID do Honorário a excluir:", min_value=1, step=1, key="input_excluir")
                        if st.button("Excluir Contrato", type="primary"):
                            supabase.table("honorarios").delete().eq("id", id_excluir).execute()
                            st.success("Contrato e parcelas excluídos com sucesso!")
                            st.rerun()
                    else:
                        st.info("🔒 Área de exclusão restrita aos sócios administradores.")
            else:
                st.info("Nenhuma parcela cadastrada até o momento.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
