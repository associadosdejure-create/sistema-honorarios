import streamlit as st
import streamlit_authenticator as stauth
from supabase import create_client
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Controle de Honorários", layout="wide", page_icon="⚖️")

# --- CREDENCIAIS DE ACESSO (LOGIN) ---
# Você pode alterar os nomes de usuário e as senhas (as senhas abaixo estão em texto puro para facilitar, depois podemos criptografar se desejar)
names = ['Administrador', 'Advogado(a)']
usernames = ['admin', 'advogado']
passwords = ['123456', 'senha123'] # Mude para as senhas que preferir

# Configuração do sistema de login
authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    cookie_name='sistema_honorarios_cookie',
    key='sua_chave_secreta_aqui',
    cookie_expiry_days=30
)

# Renderiza a tela de login
name, authentication_status, username = authenticator.login('Login - Sistema de Honorários', 'main')

if authentication_status == False:
    st.error('Usuário ou senha incorretos')
elif authentication_status == None:
    st.warning('Por favor, digite seu usuário e senha')
elif authentication_status == True:
    
    # --- CONEXÃO COM O SUPABASE ---
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)

    # --- BARRA LATERAL (LOGO, LOGOUT E MENU) ---
    with st.sidebar:
        st.write(f"Bem-vindo(a), **{name}**")
        authenticator.logout('Sair', 'sidebar')
        st.markdown("---")
        
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.write("⚖️ **Escritório de Advocacia**")
        
        st.markdown("---")
        menu = st.radio("Navegação", ["Cadastrar Honorário", "Ver Parcelas e Baixas"])

    # --- TELA PRINCIPAL ---
    st.title("⚖️ Controle de Honorários do Escritório")

    if menu == "Cadastrar Honorário":
        st.header("📝 Cadastrar Novo Contrato Parcelado")
        
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
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                
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
                    st.caption("Remove o contrato e todas as suas parcelas.")
                    id_excluir = st.number_input("Digite o ID do Honorário a excluir:", min_value=1, step=1, key="input_excluir")
                    if st.button("Excluir Contrato", type="primary"):
                        supabase.table("honorarios").delete().eq("id", id_excluir).execute()
                        st.success("Contrato e parcelas excluídos com sucesso!")
                        st.rerun()
            else:
                st.info("Nenhuma parcela cadastrada até o momento.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
