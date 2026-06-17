from collections import deque

class Grafo:
    def __init__(self):
        self.nos = {}
        self.labels = {}
        self.tips = {}
        self.arestas = {}
        self.adj = {}
    
    def adicionarNo(self, idNo, tipo, label, tip):
        self.nos[idNo] = tipo
        self.labels[idNo] = label
        self.tips[idNo] = tip
    
    def adicionarAresta(self, origem, destino, peso):
        chave = (origem, destino)
        if chave not in self.arestas:
            self.arestas[chave] = peso
        else:
            self.arestas[chave] += peso
        
        if origem not in self.adj:
            self.adj[origem] = []
        if destino not in self.adj:
            self.adj[destino] = []
        self.adj[origem].append(destino)
        self.adj[destino].append(origem)
    
    def dfs(self, inicio):
        visitados = []
        def visitar(no):
            visitados.append(no)
            for vizinho in self.adj.get(no, []):
                if vizinho not in visitados:
                    visitar(vizinho)
        visitar(inicio)
        return visitados
    
    def bfs(self, inicio):
        visitados = []
        fila = deque([inicio])
        while fila:
            atual = fila.popleft()
            if atual in visitados: continue
            visitados.append(atual)
            for vizinho in self.adj.get(atual, []):
                if vizinho not in visitados:
                    fila.append(vizinho)
        return visitados

class Combustivel:
    def __init__(self, nome, fator):
        self.nome = nome
        self.fator = fator
        self.id = nome

class Usina:
    def __init__(self, nome, potencia, combustivel, cidadeObj):
        self.nome = nome 
        self.potencia = potencia 
        self.combustivel = combustivel 
        self.cidade = cidadeObj 
        self.id = f"{cidadeObj.id}_{nome}"

        self.emissao = round((self.potencia * combustivel.fator) / 1_000_000, 3)

class Cidade:
    def __init__(self, nome, estadoObj):
        self.nome = nome
        self.estado = estadoObj
        self.usinas = []
        self.id = f"{estadoObj.id}_{nome}"

    def emissaoTotal(self):
        return round(sum(u.emissao for u in self.usinas), 3)

class Estado:
    def __init__(self, uf):
        self.uf = uf
        self.id = uf
        self.cidades = {}

    def emissaoTotal(self):
        return round(sum(c.emissaoTotal() for c in self.cidades.values()), 3)