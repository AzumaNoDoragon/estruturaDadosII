import random, streamlit as st, pandas as pd
from Projeto.Proxy import wrapperExec

class Vertice:
    def __init__(self, nome):
        self.nome = nome
        self.arestas = []
    
    def adicionarArestaUnidirecional(self, novoVertice, peso):
        self.arestas.append((novoVertice, peso))
    
    def adicionarArestasBidirecional(self, novoVertice, peso):
        self.adicionarArestaUnidirecional(novoVertice, peso)
        novoVertice.adicionarArestaUnidirecional(self, peso)

    def apagarAresta(self, vertice):
        for(verticeConectado, distancia) in self.arestas:
            if verticeConectado == vertice:
                self.arestas.remove((verticeConectado, distancia))
                verticeConectado.apagarAresta(self)
                break
    
    def __str__(self):
        return self.nome

def grafo(usinasOperacionais):
    def limparTexto(valor):
        return str(valor).replace('"', "'").strip()
    
    def extrairCidade(valor):
        valor = limparTexto(valor)

        if " - " in valor:
            return valor.split(" - ")[0].strip()
        
        return valor
    
    def corEmissao(peso):
        if peso > 5.0: return "red", "Alta"
        if peso > 1.0: return "orange", "Média"
        else: return "green", "Baixa"
    
    def adicionarArestar(arestas, origem, destino, peso):
        chave = tuple(sorted([origem, destino]))

        if chave not in arestas:
            arestas[chave] = peso
        else:
            arestas[chave] += peso

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
    
    modo = st.selectbox(
        "Tipo de visualização",
        [
            "Estado ↔ Cidade ↔ Usina ↔ Combustível",
            "Estado ↔ Usina ↔ Combustível",
            "Cidade ↔ Usina ↔ Combustível",
            "Estado ↔ Combustível"
        ]
    )
    
    usinasAleatorias = usinasFiltradas.sample(qtdUsinas, random_state=42)

    nos = {}
    arestas = {}
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
            adicionarArestar(arestas, uf, cidade, 0)
            adicionarArestar(arestas, cidade, nomeUsina, emissao)
            adicionarArestar(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Estado ↔ Usina ↔ Combustível":
            nos[uf] = "estado"
            nos[nomeUsina] = "usina"
            nos[combustivel] = "combustivel"
            adicionarArestar(arestas, uf, nomeUsina, emissao)
            adicionarArestar(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Cidade ↔ Usina ↔ Combustível":
            nos[cidade] = "cidade"
            nos[nomeUsina] = "usina"
            nos[combustivel] = "combustivel"
            adicionarArestar(arestas, cidade, nomeUsina, emissao)
            adicionarArestar(arestas, nomeUsina, combustivel, emissao)
        elif modo == "Estado ↔ Combustível":
            nos[uf] = "estado"
            nos[combustivel] = "combustivel"
            adicionarArestar(arestas, uf, combustivel, emissao)
    
    dot_code = "graph G {\n"
    dot_code += "  rankdir=LR;\n"
    dot_code += "  overlap=false;\n"
    dot_code += "  splines=true;\n"
    dot_code += "  layout=dot;\n"
    dot_code += "  nodesep=0.5;\n"
    dot_code += "  ranksep=1.5;\n"
    
    for nome, tipo in nos.items():
        if tipo == "estado":
            dot_code += f'  "{nome}" [shape=circle, style=filled, fillcolor=lightblue];\n'
        elif tipo == "cidade":
            dot_code += f'  "{nome}" [shape=circle, style=filled, fillcolor=lightgreen];\n'
        elif tipo == "usina":
            dot_code += f'  "{nome}" [shape=circle, style=filled, fillcolor=lightgray];\n'
        elif tipo == "combustivel":
            dot_code += f'  "{nome}" [shape=circle, style=filled, fillcolor=khaki];\n'
    
    for (origem, destino), peso in arestas.items():
        cor, nivel = corEmissao(peso)
        label = f"{peso} t/h"

        dot_code += (
            f'  "{origem}" -- "{destino}" '
            f'[label="{label}", color="{cor}", penwidth={1}, fontcolor="{cor}"];\n'
        )

    dot_code += "}"

    st.subheader("Visualização da Rede de Distribuição e Emissões")
    st.graphviz_chart(dot_code, use_container_width=True)
    
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