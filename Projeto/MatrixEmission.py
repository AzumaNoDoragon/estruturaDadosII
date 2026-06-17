import streamlit as st, pandas as pd
import streamlit.components.v1 as components
from pyvis.network import Network
# Minhas bibliotecas
from Projeto.Proxy import wrapperExec
from Projeto.Class import Combustivel, Cidade, Usina, Estado, Grafo
from Projeto.fatoresCO2 import fatoresCO2
from Projeto.funcoes import legenda, limparTexto, extrairCidade

def grafo(usinasOperacionais):
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
            value = min(50, qtd),
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

    estadosMapeados = {}
    listaUsinas = []
    for _, row in usinasAleatorias.iterrows():
        uf = limparTexto(row["SigUFPrincipal"])
        cidade = extrairCidade(row["DscMuninicpios"])
        nomeUsina = limparTexto(row["NomEmpreendimento"])
        combustivel = limparTexto(row["NomFonteCombustivel"])

        try:
            potencia = float(str(row["MdaPotenciaOutorgadaKw"]).replace(".", "").replace(",", "."))
        except:
            potencia = 0.0

        if uf not in estadosMapeados:
            estadosMapeados[uf] = Estado(uf)
        estadoObj = estadosMapeados[uf]

        if cidade not in estadoObj.cidades:
            estadoObj.cidades[cidade] = Cidade(cidade, estadoObj)
        cidadeObj = estadoObj.cidades[cidade]

        combustivelObj = Combustivel(combustivel, fatoresCO2.get(combustivel, 0))
        usinaObj = Usina(nomeUsina, potencia, combustivelObj, cidadeObj)

        if not any(u.id == usinaObj.id for u in cidadeObj.usinas):
            cidadeObj.usinas.append(usinaObj)
        listaUsinas.append(usinaObj)

    g = Grafo()
    for u in listaUsinas:
        c = u.cidade
        e = u.cidade.estado
        comb = u.combustivel

        if modo == "Estado ↔ Cidade ↔ Usina ↔ Combustível":
            g.adicionarNo(e.id, "estado", e.uf, f"Estado: {e.uf}\nEmissão Total: {e.emissaoTotal():.3f} t/h")
            g.adicionarNo(c.id, "cidade", c.nome, f"Cidade: {c.nome}\nEmissão Local: {c.emissaoTotal():.3f} t/h")
            g.adicionarNo(u.id, "usina", u.nome, f"Usina: {u.nome}\nEmissão Potencial: {u.emissao:.3f} t/h")
            g.adicionarNo(comb.id, "combustivel", comb.nome, f"Combustível: {comb.nome}\nFator IPCC: {comb.fator}")
            if (e.id, c.id) not in g.arestas:
                g.adicionarAresta(e.id, c.id, c.emissaoTotal())
            g.adicionarAresta(c.id, u.id, u.emissao)
            g.adicionarAresta(u.id, comb.id, u.emissao)
        elif modo == "Estado ↔ Usina ↔ Combustível":
            idU = f"{e.id}_{u.nome}"
            g.adicionarNo(e.id, "estado", e.uf, f"Estado: {e.uf}\nEmissão Total: {e.emissaoTotal():.3f} t/h")
            g.adicionarNo(idU, "usina", u.nome, f"Usina: {u.nome}\nEmissão Potencial: {u.emissao:.3f} t/h")
            g.adicionarNo(comb.id, "combustivel", comb.nome, f"Combustível: {comb.nome}\nFator IPCC: {comb.fator}")
            g.adicionarAresta(e.id, idU, u.emissao)
            g.adicionarAresta(idU, comb.id, u.emissao)
        elif modo == "Cidade ↔ Usina ↔ Combustível":
            g.adicionarNo(c.id, "cidade", c.nome, f"Cidade: {c.nome}\nEmissão Local: {c.emissaoTotal():.3f} t/h")
            g.adicionarNo(u.id, "usina", u.nome, f"Usina: {u.nome}\nEmissão Potencial: {u.emissao:.3f} t/h")
            g.adicionarNo(comb.id, "combustivel", comb.nome, f"Combustível: {comb.nome}\nFator IPCC: {comb.fator}")
            g.adicionarAresta(c.id, u.id, u.emissao)
            g.adicionarAresta(u.id, comb.id, u.emissao)
        elif modo == "Estado ↔ Cidade ↔ Combustível":
            g.adicionarNo(e.id, "estado", e.uf, f"Estado: {e.uf}\nEmissão Total: {e.emissaoTotal():.3f} t/h")
            g.adicionarNo(c.id, "cidade", c.nome, f"Cidade: {c.nome}\nEmissão Local: {c.emissaoTotal():.3f} t/h")
            g.adicionarNo(comb.id, "combustivel", comb.nome, f"Combustível: {comb.nome}\nFator IPCC: {comb.fator}")
            if (e.id, c.id) not in g.arestas:
                g.adicionarAresta(e.id, c.id, c.emissaoTotal())
            if (c.id, comb.id) not in g.arestas:
                g.adicionarAresta(c.id, comb.id, c.emissaoTotal())
        elif modo == "Estado ↔ Combustível":
            g.adicionarNo(e.id, "estado", e.uf, f"Estado: {e.uf}\nEmissão Total: {e.emissaoTotal():.3f} t/h")
            g.adicionarNo(comb.id, "combustivel", comb.nome, f"Combustível: {comb.nome}\nFator IPCC: {comb.fator}")
            if (e.id, comb.id) not in g.arestas:
                g.adicionarAresta(e.id, comb.id, e.emissaoTotal())
    
    st.subheader("Visualização da Rede de Distribuição e Emissões")
    net = Network(height="800px", width="100%", bgcolor="white")
    net.force_atlas_2based()

    for nome, tipo in g.nos.items():
        cor = {
            "estado": "#00B7FF",
            "cidade": "#00FF00",
            "usina": "#FFE600",
            "combustivel": "#FF0000"
        }[tipo]
        net.add_node(
            nome,
            label = g.labels[nome] if tipo in ("estado", "combustivel") else " ",
            title = g.tips[nome],
            shape = "circle",
            color = cor,
            font = {"size": 8 if tipo == "combustivel" else 12}
        )

    for (origem, destino), peso in g.arestas.items():
        if peso <= 1:
            cor, largura = "green", 1
        elif peso <= 5:
            cor, largura = "orange", 3
        else:
            cor, largura = "red", 5
        net.add_edge(
            origem,
            destino,
            label = f"{peso:.2f}",
            title = f"{peso:.2f} t/h",
            color = cor,
            width = largura
        )

    st.iframe(net.generate_html(), height=800)

    col1, col2 = st.columns(2)
    with col1: st.metric("Nós", len(g.nos))
    with col2: st.metric("Arestas", len(g.arestas))

    st.subheader("Painel Analítico")
    st.info("*Remova colunas como 'Usina' para ver o agrupamento e a soma automática por Cidade, Estado ou até mesmo Combustível.\n Obs.: Caso ocorra alguma inconsistência no carregamento dos dados após múltiplas seleções, basta remover os filtros ativos e adicioná-los novamente para atualizar a tabela.*")

    opc = st.checkbox("Clique aqui caso deseje verificar todos os dados, caso contrário, os dados abaixo serão apenas do grafo atual.")
    dadosTabela = []
    if opc:
        for _, row in usinasFiltradas.iterrows():
            try:
                potenciaBruta = float(str(row["MdaPotenciaOutorgadaKw"]).replace(".", "").replace(",", "."))
            except:
                potenciaBruta = 0.0
                
            fatorComb = fatoresCO2.get(limparTexto(row["NomFonteCombustivel"]), 0)
            emissaoCalculada = round((potenciaBruta * fatorComb) / 1_000_000, 3)            
            dadosTabela.append({
                "Estado (UF)": limparTexto(row["SigUFPrincipal"]),
                "Cidade": extrairCidade(row["DscMuninicpios"]),
                "Usina": limparTexto(row["NomEmpreendimento"]),
                "Combustível": limparTexto(row["NomFonteCombustivel"]),
                "Potência Outorgada (kW)": potenciaBruta,
                "Fator de Emissão (gCO2/kWh)": fatorComb,
                "Emissão Potencial (t/h)": emissaoCalculada
            })
    else:
        for u in listaUsinas:
            dadosTabela.append({
                "Estado (UF)": u.cidade.estado.uf,
                "Cidade": u.cidade.nome,
                "Usina": u.nome,
                "Combustível": u.combustivel.nome,
                "Potência Outorgada (kW)": u.potencia,
                "Fator de Emissão (gCO2/kWh)": u.combustivel.fator,
                "Emissão Potencial (t/h)": u.emissao
            })

    dfBruto = pd.DataFrame(dadosTabela)
    colunasDisponiveis = list(dfBruto.columns)
    colunasSelecionadas = st.multiselect(
        "Selecione quais detalhes deseja inspecionar na tabela:",
        options = colunasDisponiveis,
        default = colunasDisponiveis
    )

    if colunasSelecionadas:
        colunasChave = [c for c in colunasSelecionadas if c in ["Estado (UF)", "Cidade", "Usina", "Combustível", "Fator de Emissão (gCO2/kWh)"]]
        colunasValores = [c for c in colunasSelecionadas if c in ["Potência Outorgada (kW)", "Emissão Potencial (t/h)"]]
        if colunasChave:
            if colunasValores:
                dfExibir = dfBruto.groupby(colunasChave)[colunasValores].sum().reset_index()
            else:
                dfExibir = dfBruto[colunasChave].drop_duplicates()
            dfExibir = dfExibir.sort_values(by=colunasChave[0])
        else:
            dfExibir = pd.DataFrame([dfBruto[colunasValores].sum()])
        st.dataframe(dfExibir[colunasSelecionadas], width="stretch")
    else:
        st.info("Por favor, selecione pelo menos uma coluna acima para visualizar os dados.")

    with st.expander("Perguntas analíticas que o sistema responde", expanded=False):
        dados = not dfBruto.empty

        # Pergunta 1. Usina mais poluente
        maxPoluente = dfBruto["Emissão Potencial (t/h)"].idxmax() if dados else None
        usinaCritica = dfBruto.loc[maxPoluente]["Usina"] if maxPoluente is not None else "N/A"
        emissaoCritica = dfBruto["Emissão Potencial (t/h)"].max() if dados else 0.0
        st.markdown("""
            * **Nota de Escopo Dinâmico:** Os resultados apresentados abaixo são recalculados em tempo real de acordo com as suas ações. Caso o checkbox para verificar todos os dados esteja ativo, os cálculos abrangerão a base de dados completa da ANEEL; caso contrário, refletirão estritamente a amostra atual renderizada no grafo.
            ---
        """)
        st.markdown("""
            **1. Qual Usina representa o maior ponto crítico de emissão de CO₂ no cenário atual?**
            * **Resposta:** A usina **{usinaCritica}** destaca-se como o maior poluente, gerando individualmente um fluxo potencial de **{emissaoCritica:.3f} t/h** de CO₂.
            ---
        """)

        # Pergunta 2. Estado líder em emiss]oes na amostragem
        if dados:
            grupoEstado = dfBruto.groupby("Estado (UF)")["Emissão Potencial (t/h)"].sum()
            estadoLider = grupoEstado.idxmax()
            emissaoEstado = grupoEstado.max()
        else:
            estadoLider, emissaoEstado = "N/A", 0.0
        st.markdown(f"""
            **2. Qual Estado concentra o maior volume acumulado de emissões horárias com base nas usinas mapeadas?**
            * **Resposta:** O estado do **{estadoLider}** lidera o índice de emissões agregadas na amostragem atual, com um impacto de **{emissaoEstado:.3f} t/h** de CO₂.
            ---
        """)
        
        # Pergunta 3. Combustível com maior fator poluente
        if dados:
            grupoCombustivel = dfBruto.groupby("Combustível")["Fator de Emissão (gCO2/kWh)"].mean()
            combMaisPoluente = grupoCombustivel.idxmax()
            fatorPoluente = grupoCombustivel.max()
        else:
            combMaisPoluente, fatorPoluente = "N/A", 0.0
        st.markdown(f"""
            **3. Qual das fontes de combustível selecionadas possui o maior fator de emissão (potencial poluente por kWh)?**
            * **Resposta:** O combustível **{combMaisPoluente}** apresenta a menor eficiência ecológica, registando um fator de emissão médio de **{fatorPoluente} gCO₂/kWh**.
        """)
        st.write("---")

        # Pergunta 4. Rastreabilidade de Impacto
        st.write("Configuração da resposta 4")
        col1, col2 = st.columns(2)
        with col1:
            noInicialBusca = st.selectbox("Vértice inicial", sorted(g.nos.keys()), format_func=lambda x: g.labels.get(x, x))
        with col2:
            with st.expander("BFS/DFS"):
                st.info("""
                    Busca em Largura (BFS):
                    Explora primeiro os vértices mais próximos do nó inicial.

                    Busca em Profundidade (DFS):
                    Explora um caminho até o final antes de retroceder.
                """)
            algoritmo = st.radio("Algoritmo", ["DFS", "BFS"])
        if noInicialBusca:
            resultadoBusca = g.dfs(noInicialBusca) if algoritmo == "DFS" else g.bfs(noInicialBusca)
            nomesVisitados = [g.labels.get(noId, noId) for noId in resultadoBusca]
        else:
            resultadoBusca, nomesVisitados = [], []
        st.markdown(f"""
            **4. Aplicação do Algoritmo de Busca ({algoritmo}): Partindo do nó selecionado '{g.labels.get(noInicialBusca, noInicialBusca) if noInicialBusca else "N/A"}', qual é o caminho de dependência e alcance de impacto mapeado?**
            * **Resposta:** O algoritmo de varredura **{algoritmo}** processou a topologia em tempo real e descobriu que este ponto conecta-se diretamente com **{len(resultadoBusca)} elementos** na rede.
            * **Caminho de Rastreabilidade:** {nomesVisitados}
        """)
        st.write("---")
        
        # Pergunta 5. Análise de Conectividade
        totalEstados = dfBruto["Estado (UF)"].nunique() if dados else 0
        totalCidades = dfBruto["Cidade"].nunique() if dados else 0
        st.markdown(f"""
            **5. Qual é a abrangência geográfica e o impacto socioambiental do conjunto de usinas atualmente selecionado no filtro?**
            * **Resposta:** O cenário em análise espalha o seu impacto por **{totalEstados} Estado(s)** e **{totalCidades} Cidade(s)** diferentes, permitindo mapear a matriz poluente.
        """)

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