import pandas as pd
import streamlit as st

st.set_page_config(page_title="Média Ponderada", layout="centered")

# Título
st.title("Calculadora de Média Ponderada de Entradas")

# Descricao
st.markdown("Faça o upload de um arquivo `.xlsx` com as colunas **'Qtd.'**, **'Custo Gerencial'** e **'Dt.Entrada'** para calcular a média ponderada.")

# Upload
uploaded_file = st.file_uploader("📁 Selecione o arquivo Excel", type=["xlsx"])

# Estoque total
total_em_estoque = st.number_input("📦 Total disponível em estoque", min_value=1, value=182, step=1)

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        df["Qtd."] = pd.to_numeric(df["Qtd."].astype(str).str.replace(",", "."), errors="coerce")
        df["Custo Gerencial"] = pd.to_numeric(df["Custo Gerencial"].astype(str).str.replace(",", "."), errors="coerce")
        df = df.dropna(subset=["Qtd.", "Custo Gerencial"])

        df = df.sort_values(by="Dt.Entrada", ascending=False)

        quantidade_acumulada = 0
        soma_ponderada = 0
        soma_qtd = 0

        for _, row in df.iterrows():
            qtd_disponivel = row["Qtd."]
            custo = row["Custo Gerencial"]
            
            if quantidade_acumulada + qtd_disponivel <= total_em_estoque:
                soma_ponderada += custo * qtd_disponivel
                soma_qtd += qtd_disponivel
                quantidade_acumulada += qtd_disponivel
            else:
                qtd_restante = total_em_estoque - quantidade_acumulada
                soma_ponderada += custo * qtd_restante
                soma_qtd += qtd_restante
                break

        media_ponderada = soma_ponderada / soma_qtd if soma_qtd else 0

        st.success(f"Média Ponderada Calculada: **R$ {media_ponderada:.2f}**")
    
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando o upload de um arquivo...")
