import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Conexão com o Supabase usando as chaves secretas
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Controle de Honorários", layout="wide", page_icon="⚖️")

st.title("⚖️ Controle de Honorários do Escritório")

# Menu na barra lateral
menu = st.sidebar.radio("Navegação", ["Cadastrar Honorário", "Ver Parcelas e Baixas"])

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
                # 1. Salva no banco o contrato geral
                res = supabase.table("honorarios").insert({
                    "cliente": cliente, 
                    "servico": servico, 
                    "valor_total": valor_total
                }).execute()
                
                h_id = res.data[0]['id']
                valor_parcela = valor_total / num_parcelas
                
                # 2. Gera e salva cada parcela individualmente
                for i in range(int(num_parcelas)):
                    vencimento = data_primeira + relativedelta(months=i)
                    supabase.table("parcelas").insert({
                        "honorario_id": h_id,
                        "numero_parcela": f"{i+1}/{int(num_parcelas)}",
                        "valor": valor_parcela,
                        "vencimento": vencimento.strftime("%Y-%m-%d"),
                        "status": "Pendente"
                    }).execute()
                
                st.success(f"Sucesso! Honorário de {cliente} cadastrado em {int(num_parcelas)}x de R$ {valor_parcela:.2f}")
            else:
                st.error("Por favor, preencha todos os campos corretamente.")

elif menu == "Ver Parcelas e Baixas":
    st.header("📋 Gestão de Parcelas")
    
    # Busca todas as parcelas e os dados do cliente
    res = supabase.table("parcelas").select("*, honorarios(cliente, servico)").execute()
    
    if res.data:
        lista_dados = []
        for item in res.data:
            lista_dados.append({
                "ID": item['id'],
                "Cliente": item['honorarios']['cliente'],
                "Serviço": item['honorarios']['servico'],
                "Parcela": item['numero_parcela'],
                "Valor (R$)": f"R$ {item['valor']:.2f}",
                "Vencimento": datetime.strptime(item['vencimento'], "%Y-%m-%d").strftime("%d/%m/%Y"),
                "Status": item['status']
            })
        
        df = pd.DataFrame(lista_dados)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("🔄 Dar baixa em parcela")
        id_baixa = st.number_input("Digite o ID da parcela paga:", min_value=1, step=1)
        if st.button("Marcar como Pago"):
            supabase.table("parcelas").update({"status": "Pago"}).eq("id", id_baixa).execute()
            st.success("Status atualizado com sucesso!")
            st.rerun()
    else:
        st.info("Nenhuma parcela cadastrada até o momento.")
