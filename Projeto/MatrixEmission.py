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
                potencia_bruta = float(str(row["MdaPotenciaOutorgadaKw"]).replace(".", "").replace(",", "."))
            except:
                potencia_bruta = 0.0
                
            fator_comb = fatoresCO2.get(limparTexto(row["NomFonteCombustivel"]), 0)
            emissao_calculada = round((potencia_bruta * fator_comb) / 1_000_000, 3)            
            dadosTabela.append({
                "Estado (UF)": limparTexto(row["SigUFPrincipal"]),
                "Cidade": extrairCidade(row["DscMuninicpios"]),
                "Usina": limparTexto(row["NomEmpreendimento"]),
                "Combustível": limparTexto(row["NomFonteCombustivel"]),
                "Potência Outorgada (kW)": potencia_bruta,
                "Fator de Emissão (gCO2/kWh)": fator_comb,
                "Emissão Potencial (t/h)": emissao_calculada
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
        options=colunasDisponiveis,
        default=["Estado (UF)", "Cidade", "Emissão Potencial (t/h)"]
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
    
    if len(g.nos) > 0:
        inicio = st.selectbox("Vértice inicial", sorted(g.nos.keys()), format_func=lambda x: g.labels.get(x, x))
        algoritmo = st.radio("Algoritmo", ["DFS", "BFS"])

        if st.button("Executar Busca"):
            resultado = g.dfs(inicio) if algoritmo == "DFS" else g.bfs(inicio)
            st.success(f"{len(resultado)} nós visitados")
            nomesVisitados = [g.labels.get(no_id, no_id) for no_id in resultado]
            st.write(nomesVisitados)
    
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