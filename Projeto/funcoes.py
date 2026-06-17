import streamlit as st

def limparTexto(valor):
    return str(valor).replace('"', "'").strip()

def extrairCidade(valor):
    valor = limparTexto(valor)

    if " - " in valor:
        return valor.split(" - ")[0].strip()
    
    return valor

def legenda():
    with st.expander("LEGENDAS", expanded=False):
        st.markdown("### Legenda dos Nós")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown("🔵 **Estado**")
        with col2: st.markdown("🟢 **Cidade**")
        with col3: st.markdown("🟡 **Usina**")
        with col4: st.markdown("🔴 **Combustível**")

        st.markdown("### Legenda das Arestas")
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown("🟢 **0 a 1 t/h** → Baixa emissão")
        with col2: st.markdown("🟠 **1 a 5 t/h** → Média emissão")
        with col3: st.markdown("🔴 **Acima de 5 t/h** → Alta emissão")

        st.markdown("""
            Informações sobre os modos de visualização:
            1. **Modos Genéricos/Agrupados (Ex: Estado ↔ Combustível):** Agrupam e somam os dados em categorias maiores. Eles combinam as informações para mostrar o cenário geral, evitando que os valores fiquem repetidos ou somados incorretamente nas linhas do gráfico.
            2. **Modos Específicos/Detalhados (Ex: Cidade ↔ Usina ↔ Combustível):** Mostram o caminho detalhado passo a passo, separando cada nível da estrutura, ideal para analisar uma usina ou localidade de forma isolada.

            Informações sobre os pesos das arestas (linhas):
            O valor indicado nas linhas mostra o total de emissão de CO₂ acumulado. Esse peso é calculado com base no tamanho da usina e no potencial de poluição do seu combustível, sendo somado gradativamente conforme o caminho avança por usinas, cidades ou estados.
        """)