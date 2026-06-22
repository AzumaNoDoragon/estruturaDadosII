# MatrixEmission - Análise e Conectividade de Emissões de CO₂

MatrixEmission é um projeto em Python que analisa, modela e mapeia o potencial de emissão de CO₂ das usinas elétricas operacionais no Brasil. Utilizando dados oficiais da ANEEL e estimativas baseadas em literatura especializada (IPCC), a aplicação organiza as informações em uma estrutura de Grafos e gera uma visualização interativa em rede. É a ferramenta ideal para rastrear, filtrar e compreender o impacto ambiental e a abrangência geográfica da matriz energética brasileira de forma dinâmica.
O projeto resolve o problema de visualização de dados complexos e tabulares de infraestrutura energética, aplicando conceitos de Teoria dos Grafos para conectar Estados, Cidades, Usinas e Combustíveis, permitindo a análise de dependência e alcance de impacto ecológico em tempo real.

## Funcionalidades

- **Modelagem Baseada em Grafos:** Estruturação das conexões entre Estados ↔ Cidades ↔ Usinas ↔ Combustíveis utilizando estruturas de dados otimizadas.
- **Visualização Interativa em Rede:** Geração de gráficos dinâmicos de rede via biblioteca Pyvis, permitindo explorar visualmente os nós e caminhos.
- **Algoritmos de Varredura e Busca:** Implementação de busca em largura (BFS) e busca em profundidade (DFS) para rastreabilidade de caminhos e alcance de impactos na topologia da rede.
- **Cálculo de Potencial de Emissão:** Estimativa teórica do potencial de emissão de CO₂ (t/h) baseada na potência máxima outorgada/fiscalizada e fatores de emissão específicos por combustível.
- **Filtros Dinâmicos:** Filtragem avançada por tipos de combustível e controle de volume de dados por meio de sliders interativos.
- **Interface Intuitiva com Streamlit:** Painel web completo com menus de upload de dados JSON, relatórios analíticos automáticos e legendas dinâmicas.
- **Mapeamento de Pesos nas Arestas:** Classificação visual automática do nível de emissão (Baixa, Média e Alta emissão) através das cores e espessuras das linhas do grafo.
- **Padrão de Projeto Proxy/Wrapper:** Monitoramento integrado de tempo de execução, tratamento de exceções e validação dos dados de entrada.

## Requisitos

- Python 3.8 ou superior
- Pacotes: `streamlit`, `pandas`, `pyvis`
- JSON com os dados oficiais extraídos do [Portal de Dados Abertos da ANEEL](https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel/resource/11ec447d-698d-4ab8-977f-b424d5deee6a)

## Como executar
### Modo Online (Streamlit Cloud)
1. 1. Abra o link da aplicação: [estruturadadosii.streamlit.app](https://estruturadadosii.streamlit.app/)
2. Clique no botão **"Yes, get this app back up!"** e espere o servidor subir.
3. No menu lateral, faça o upload de um arquivo contendo a relação de usinas em formato JSON (relacaoUsinas.json).
4. Interaja com os filtros, selecione o nó inicial e explore a análise de conectividade gerada na tela.

### Modo Local (Para modificações e testes)
1. Clone ou baixe o repositório.
2. Instale as dependências Python:
   ```bash
   pip install streamlit pandas pyvis
3. Execute o script principal utilizando o Streamlit:
    ```bash
   streamlit run main.py
4. O Streamlit abrirá automaticamente o seu navegador padrão no endereço local. Caso não abra, acesse a URL indicada no terminal.
5. No menu lateral, faça o upload de um arquivo contendo a relação de usinas em formato JSON (relacaoUsinas.json).
6. Interaja com os filtros, selecione o nó inicial e explore a análise de conectividade gerada na tela.

> **Notas**
> - O cálculo de CO₂ é uma estimativa teórica do potencial baseado na potência instalada e não reflete necessariamente medições reais contínuas, servindo como uma métrica comparativa de impacto.
> - O arquivo Proxy.py atua injetando um decorator (@wrapperExec) nas funções principais para garantir robustez, interceptando erros de formato e exibindo o tempo exato que o algoritmo levou para processar a rede.
> - Modos de visualização agrupados unificam categorias maiores para evitar redundância de pesos, enquanto modos detalhados abrem a topologia completa passo a passo.

## Estrutura dos arquivos

- `main.py`: Script de entrada da aplicação, responsável pelo menu lateral de upload JSON e carregamento do módulo visual.
- `Projeto/MatrixEmission.py`: Orquestrador principal da lógica do painel, filtros, montagem do grafo e exibição das respostas analíticas.
- `Projeto/Class.py`: Definição das classes de domínio (Usina, Cidade, Estado, Combustivel) e implementação da estrutura de Grafo com os métodos de busca dfs e bfs.
- `Projeto/fatoresCO2.py`: Dicionário contendo os fatores de emissão teóricos de CO₂ aproximados (baseados em dados do IPCC, IEA e NREL) para cada tipo de combustível.
- `Projeto/funcoes.py`: Funções utilitárias para limpeza e extração de strings, além da renderização das legendas de nós e arestas.
- `Projeto/Proxy.py`: Implementação do padrão de projeto estrutural para tratamento de erros, validação de dados e medição de desempenho em tempo real.

## Licença

Este projeto é distribuído para fins educacionais e acadêmicos. Os dados de infraestrutura elétrica utilizados pertencem e são geridos pela Agência Nacional de Energia Elétrica (ANEEL).