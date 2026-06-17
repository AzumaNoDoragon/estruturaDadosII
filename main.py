import streamlit as st
import json
from Projeto.MatrixEmission import main

st.sidebar.title("Menu de Upload")

dados = None
uploadedFile = st.sidebar.file_uploader("Envie o arquivo JSON", type=["json"])
if uploadedFile:
    try:
        dados = json.load(uploadedFile)
        st.sidebar.success("Arquivo carregado com sucesso!")
        main(dados)
    except Exception as e:
        st.error(f"Erro ao executar: {e}")
else:
    st.info("Faça upload de um JSON para continuar.")