import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Média Ponderada", layout="centered")

st.title("Calculadora de Média Ponderada de Entradas")

st.markdown("Faça o upload de um arquivo `.txt` ou cole o conteúdo no formato `gridConsulta.fill([...])` para calcular a média ponderada.")

input_mode = st.radio("Como deseja fornecer os dados?", ("Upload de arquivo .txt", "Colar conteúdo manualmente"))

uploaded_file = None
pasted_text = ""

if input_mode == "Upload de arquivo .txt":
    uploaded_file = st.file_uploader("📁 Selecione o arquivo", type=["txt"])
else:
    pasted_text = st.text_area("Cole aqui o conteúdo do arquivo", height=300)

total_em_estoque = st.number_input("📦 Total disponível em estoque", min_value=1, value=1, step=1)

if (uploaded_file or pasted_text.strip()):
    try:
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
        else:
            content = pasted_text

        # Extrai todos os arrays de dentro do gridConsulta.fill([...])
        matches = re.findall(r"gridConsulta\.fill\(\[(.*?)\]\);", content, re.DOTALL)

        data = []
        for match in matches:
            # Pega apenas os conteúdos entre aspas simples ou duplas, ignorando vírgulas internas
            row = re.findall(r"'(.*?)'", match) or re.findall(r'"(.*?)"', match)

            # Limpa HTML e espaços
            row = [re.sub(r'<.*?>', '', item).strip() for item in row]

            if len(row) >= 18:
                data.append([row[0], row[4], row[17]])  # Dt.Entrada, Qtd., Custo Gerencial

        df = pd.DataFrame(data, columns=["Dt.Entrada", "Qtd.", "Custo Gerencial"])

        df["Dt.Entrada"] = pd.to_datetime(df["Dt.Entrada"], dayfirst=True, errors="coerce")
        df["Qtd."] = pd.to_numeric(df["Qtd."].str.replace(",", "."), errors="coerce")
        df["Custo Gerencial"] = pd.to_numeric(df["Custo Gerencial"].str.replace(",", "."), errors="coerce")

        df = df.dropna(subset=["Dt.Entrada", "Qtd.", "Custo Gerencial"])
        df = df.sort_values(by="Dt.Entrada", ascending=False)

        quantidade_acumulada = 0
        soma_ponderada = 0
        soma_qtd = 0

        for _, row in df.iterrows():
            qtd = row["Qtd."]
            custo = row["Custo Gerencial"]

            if quantidade_acumulada + qtd <= total_em_estoque:
                soma_ponderada += qtd * custo
                soma_qtd += qtd
                quantidade_acumulada += qtd
            else:
                qtd_restante = total_em_estoque - quantidade_acumulada
                soma_ponderada += qtd_restante * custo
                soma_qtd += qtd_restante
                break

        media_ponderada = soma_ponderada / soma_qtd if soma_qtd else 0

        st.success(f"Média Ponderada Calculada: **R$ {media_ponderada:.2f}**")

        with st.expander("Ver dados processados"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar os dados: {e}")
else:
    st.info("Aguardando dados para processar...")
