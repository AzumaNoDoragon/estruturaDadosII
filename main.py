import streamlit as st
import json

st.sidebar.title("Menu de Upload")

dados = None
uploaded_file = st.sidebar.file_uploader("Envie o arquivo JSON", type=["json"])
if uploaded_file:
    try:
        dados = json.load(uploaded_file)
        st.sidebar.success("Arquivo carregado com sucesso!")
        import Projeto.MatrixEmission
        Projeto.MatrixEmission.main(dados)
    except Exception as e:
        st.error(f"Erro ao executar: {e}")
else:
    st.info("Faça upload de um JSON para continuar.")