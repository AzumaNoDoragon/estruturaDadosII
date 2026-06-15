import streamlit as st, pandas as pd
import streamlit.components.v1 as components
from pyvis.network import Network
from collections import deque
from Projeto.Proxy import wrapperExec

def grafo(usinasOperacionais):
    def dfs(adj, inicio):
        visitados = []

        def visitar(no):
            visitados.append(no)
            for vizinho in adj.get(no, []):
                if vizinho not in visitados:
                    visitar(vizinho)
        visitar(inicio)

        return visitados

    def bfs(adj, inicio):
        visitados = []
        fila = deque([inicio])

        while fila:
            atual = fila.popleft()

            if atual in visitados:
                continue

            visitados.append(atual)

            for vizinho in adj.get(atual, []):
                if vizinho not in visitados:
                    fila.append(vizinho)

        return visitados
    
    def limparTexto(valor):
        return str(valor).replace('"', "'").strip()
    
    def extrairCidade(valor):
        valor = limparTexto(valor)

        if " - " in valor:
            return valor.split(" - ")[0].strip()
        
        return valor
    
    def adicionarAresta(arestas, origem, destino, peso):
        chave = tuple(sorted([origem, destino]))

        if chave not in arestas:
            arestas[chave] = peso
        else:
            arestas[chave] += peso

    def legenda():
        st.markdown("### Legenda dos Nós")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("🔵 **Estado**")
        with col2:
            st.markdown("🟢 **Cidade**")
        with col3:
            st.markdown("🟡 **Usina**")
        with col4:
            st.markdown("🔴 **Combustível**")

        st.markdown("### Legenda das Arestas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🟢 **0 a 1 t/h** → Baixa emissão")
        with col2:
            st.markdown("🟠 **1 a 5 t/h** → Média emissão")
        with col3:
            st.markdown("🔴 **Acima de 5 t/h** → Alta emissão")

    #Valores aproximados baseados em: IPCC, International Energy Agency e National Renewable Energy Laboratory (Pedi para o Gemini me ajudar com estes dados)
    fatoresCO2 = {
        "Potencial hidráulico": 24,
        "Gás de Alto Forno - CM": 1100,
        "Óleo Diesel": 778,
        "Bagaço de Cana de Açúcar": 18,
        "Gás Natural": 490,
        "Urânio": 12,
        "Licor Negro": 35,
        "Óleo Combustível": 840,
        "Calor de Processo - CM": 1000,
        "Outros Energéticos de Petróleo": 850,
        "Resíduos Florestais": 30,
        "Calor de Processo - GN": 490,
        "Carvão Mineral": 1001,
        "Gás de Refinaria": 650,
        "Biogás - RU": 230,
        "Cinética do vento": 11,
        "Lenha": 30,
        "Casca de Arroz": 25,
        "Radiação solar": 45,
        "Carvão Vegetal": 28,
        "Gás de Alto Forno - PE": 1100,
        "Gás de Alto Forno - Biomassa": 150,
        "Calor de Processo - OF": 840,
        "Biogás - RA": 180,
        "Capim Elefante": 20,
        "Óleos vegetais": 50,
        "Biogás-AGR": 150,
        "Resíduos Sólidos Urbanos - RU": 400,
        "Etanol": 38,
        "Carvão - RU": 600,
        "Biogás - Floresta": 120
    }

    legenda()

    listaCombustiveis = sorted(list(fatoresCO2.keys()))
    combustiveisSelecionados = st.multiselect(
        "Filtrar por tipos de combustível (deixe vazio para ver todos):",
        options=listaCombustiveis
    )

    if combustiveisSelecionados:
        usinasFiltradas = usinasOperacionais[usinasOperacionais['NomFonteCombustivel'].isin(combustiveisSelecionados)]
    else:
        usinasFiltradas = usinasOperacionais
    
    if usinasFiltradas.empty:
        st.warning("Nenhuma usina encontrada para o filtro selecionado.")
        return
    
    qtd = len(usinasFiltradas)
    qtdUsinas = st.slider(
            label = "Escolha a quantidade de usinas:",
            min_value = 0,
            max_value = qtd,
            value = 2, #min(50, qtd)
            step = 1
        )
    if qtdUsinas == 0:
        st.write("Precisa ter ao menos uma usina")
        return
    
    modo = st.selectbox(
        "Tipo de visualização",
        [
            "Estado ↔ Combustível",
            "Estado ↔ Cidade ↔ Combustível",
            "Cidade ↔ Usina ↔ Combustível",
            "Estado ↔ Usina ↔ Combustível",
            "Estado ↔ Cidade ↔ Usina ↔ Combustível"
        ]
    )
    
    usinasAleatorias = usinasFiltradas.sample(qtdUsinas, random_state=qtdUsinas)

    nos = {}
    arestas = {}
    emissaoCombustivel = {}
    for _, usina in usinasAleatorias.iterrows():
        uf = limparTexto(usina["SigUFPrincipal"])
        cidade = extrairCidade(usina["DscMuninicpios"])
        nomeUsina = limparTexto(usina["NomEmpreendimento"])
        combustivel = limparTexto(usina["NomFonteCombustivel"])

        try:
            potencia = str(usina["MdaPotenciaOutorgadaKw"]).replace(".", "").replace(",", ".")
            potencia = float(potencia)
        except:
            potencia = 0.0

        fator = fatoresCO2.get(combustivel, 0)
        emissao = round((potencia * fator) / 1_000_000, 3)

        if modo == "Estado ↔ Cidade ↔ Usina ↔ Combustível":
            nos[uf] = "estado"
            nos[cidade] = "cidade"
            nos[nomeUsina] = "usina"
            nos[combustivel] = "combustivel"
            adicionarAresta(arestas, uf, cidade, 0)
            adicionarAresta(arestas, cidade, nomeUsina, emissao)
            adicionarAresta(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Estado ↔ Usina ↔ Combustível":
            nos[uf] = "estado"
            nos[nomeUsina] = "usina"
            nos[combustivel] = "combustivel"
            adicionarAresta(arestas, uf, nomeUsina, emissao)
            adicionarAresta(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Cidade ↔ Usina ↔ Combustível":
            nos[cidade] = "cidade"
            nos[nomeUsina] = "usina"
            nos[combustivel] = "combustivel"
            adicionarAresta(arestas, cidade, nomeUsina, emissao)
            adicionarAresta(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Estado ↔ Cidade ↔ Combustível":
            nos[uf] = "estado"
            nos[cidade] = "cidade"
            nos[combustivel] = "combustivel"
            chave1 = (uf, cidade)
            chave2 = (cidade, combustivel)
            arestas[chave1] = 0
            emissaoCombustivel[chave2] = (
                emissaoCombustivel.get(chave2, 0)
                + emissao
            )
        elif modo == "Estado ↔ Combustível":
            nos[uf] = "estado"
            nos[combustivel] = "combustivel"
            chave = (uf, combustivel)
            emissaoCombustivel[chave] = (
                emissaoCombustivel.get(chave, 0)
                + emissao
            )
    if modo in (
        "Estado ↔ Combustível",
        "Estado ↔ Cidade ↔ Combustível"
    ):
        for (origem, combustivel), emissaoTotal in emissaoCombustivel.items():
            if modo == "Estado ↔ Combustível":
                nos[origem] = "estado"
            else:
                nos[origem] = "cidade"
            nos[combustivel] = "combustivel"

            adicionarAresta(
                arestas,
                origem,
                combustivel,
                round(emissaoTotal, 3)
            )
    
    st.subheader("Visualização da Rede de Distribuição e Emissões")

    net = Network(
        height="800px",
        width="100%",
        bgcolor="white"
    )

    #net.force_atlas_2based()

    for nome, tipo in nos.items():
        cor = {
            "estado": "#00B7FF",
            "cidade": "#00FF00",
            "usina": "#FFE600",
            "combustivel": "#FF0000"
        }[tipo]

        net.add_node(
            nome,
            label = nome if tipo in ("estado", "combustivel") else " ",
            title = nome,
            shape = "circle",
            color = cor,
            font={
                "size": 8 if tipo == "combustivel" else 12
            }
        )

    for (origem, destino), peso in arestas.items():
        if peso <= 1:
            cor = "green"
            largura = 1
        elif peso <= 5:
            cor = "orange"
            largura = 3
        else:
            cor = "red"
            largura = 5
        net.add_edge(
            origem,
            destino,
            label=f"{peso:.2f}",
            title=f"{peso:.2f} t/h",
            color=cor,
            width=largura
        )

    html = net.generate_html()

    components.html(
        html,
        height=800,
        scrolling=False,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nós", len(nos))
    with col2:
        st.metric("Arestas", len(arestas))
    st.dataframe(
        pd.DataFrame(
            [
                [origem, destino, peso]
                for (origem, destino), peso in arestas.items()
            ],
            columns=["Origem", "Destino", "Emissão (t/h)"]
        )
    )
    
    adj = {}
    for (origem, destino), peso in arestas.items():

        if origem not in adj:
            adj[origem] = []

        if destino not in adj:
            adj[destino] = []

        adj[origem].append(destino)
        adj[destino].append(origem)

    if len(nos) > 0:
        inicio = st.selectbox(
            "Vértice inicial",
            sorted(nos.keys())
        )

        algoritmo = st.radio(
            "Algoritmo",
            ["DFS", "BFS"]
        )

        if st.button("Executar Busca"):
            if algoritmo == "DFS":
                resultado = dfs(adj, inicio)
            else:
                resultado = bfs(adj, inicio)

            st.success(
                f"{len(resultado)} nós visitados"
            )

            st.write(
                resultado
            )
    
@wrapperExec
def main(dados):
    st.title("MatrixEmission")

    if dados is None:
        st.warning("Nenhuma informação encontrada, carregue outro arquivo no menu lateral.")
        return
    else:
        try:
            colunas = [campo["id"] for campo in dados["fields"]]
            df = pd.DataFrame(dados["records"], columns=colunas)
            usinasOperacionais = df[df['DscFaseUsina'] == 'Operação']
            grafo(usinasOperacionais)
        except Exception as e:
            st.error(f"Erro ao executar: {e}")