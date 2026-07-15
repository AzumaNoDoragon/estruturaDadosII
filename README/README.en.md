# MatrixEmission - CO₂ Emissions Analysis and Connectivity

MatrixEmission is a Python project that analyzes, models, and maps the CO₂ emission potential of operational power plants in Brazil. Using official data from ANEEL and estimates based on specialized literature (IPCC), the application organizes the information into a Graph structure and generates an interactive network visualization. It is the ideal tool for dynamically tracking, filtering, and understanding the environmental impact and geographical reach of the Brazilian energy matrix.
The project solves the problem of visualizing complex and tabular energy infrastructure data by applying Graph Theory concepts to connect States, Cities, Power Plants, and Fuels, enabling the analysis of dependencies and ecological impact reach in real time.

## Features

- **Graph-Based Modeling:** Structuring connections between States ↔ Cities ↔ Power Plants ↔ Fuels using optimized data structures.
- **Interactive Network Visualization:** Generating dynamic network graphs via the Pyvis library, allowing visual exploration of nodes and paths.
- **Traversal and Search Algorithms:** Implementation of Breadth-First Search (BFS) and Depth-First Search (DFS) for path traceability and impact reach within the network topology.
- **Emission Potential Calculation:** Theoretical estimation of CO₂ emission potential (t/h) based on the maximum granted/inspected power and specific emission factors per fuel type.
- **Dynamic Filters:** Advanced filtering by fuel types and data volume control through interactive sliders.
- **Intuitive Interface with Streamlit:** Complete web dashboard with JSON data upload menus, automated analytical reports, and dynamic legends.
- **Edge Weight Mapping:** Automatic visual classification of emission levels (Low, Medium, and High emission) through the colors and thicknesses of the graph's edges.
- **Proxy/Wrapper Design Pattern:** Integrated execution time monitoring, exception handling, and input data validation.

## Requirements

- Python 3.8 or higher
- Packages: `streamlit`, `pandas`, `pyvis`
- JSON containing official data extracted from the [ANEEL Open Data Portal](https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel/resource/11ec447d-698d-4ab8-977f-b424d5deee6a)

## How to run
### Online Mode (Streamlit Cloud)
1. Open the application link: [estruturadadosii.streamlit.app](https://estruturadadosii.streamlit.app/)
2. Click the **"Yes, get this app back up!"** button and wait for the server to spin up.
3. In the sidebar menu, upload a file containing the power plant list in JSON format (`relacaoUsinas.json`).
4. Interact with the filters, select the starting node, and explore the connectivity analysis generated on the screen.

### Local Mode (For modifications and testing)
1. Clone or download the repository.
2. Install the Python dependencies:
   ```bash
   pip install streamlit pandas pyvis
3. Run the main script using Streamlit:
   ```bash
   streamlit run main.py
4. Streamlit will automatically open your default browser to the local address. If it doesn't open, access the URL indicated in the terminal.
5. In the sidebar menu, upload a file containing the power plant list in JSON format (`relacaoUsinas.json`).
6. Interact with the filters, select the starting node, and explore the connectivity analysis generated on the screen.

> **Notes**
> - The CO₂ calculation is a theoretical estimate of the potential based on installed capacity and does not necessarily reflect continuous real measurements; it serves as a comparative impact metric.
> - The `Proxy.py` file acts by injecting a decorator (`@wrapperExec`) into the main functions to ensure robustness, intercepting format errors, and displaying the exact time the algorithm took to process the network.
> - Grouped visualization modes unify larger categories to avoid edge weight redundancy, while detailed modes open the complete topology step-by-step.

## File Structure

- `main.py`: Application entry script, responsible for the JSON upload sidebar menu and loading the visual module.
- `Projeto/MatrixEmission.py`: Main orchestrator for the dashboard logic, filters, graph assembly, and display of analytical responses.
- `Projeto/Class.py`: Definition of domain classes (Power Plant, City, State, Fuel) and implementation of the Graph structure with `dfs` and `bfs` search methods.
- `Projeto/fatoresCO2.py`: Dictionary containing the approximate theoretical CO₂ emission factors (based on IPCC, IEA, and NREL data) for each fuel type.
- `Projeto/funcoes.py`: Utility functions for cleaning and extracting strings, as well as rendering node and edge legends.
- `Projeto/Proxy.py`: Implementation of the structural design pattern for error handling, data validation, and real-time performance measurement.

## License

This project is distributed for educational and academic purposes. The electrical infrastructure data used belongs to and is managed by the Brazilian National Electric Energy Agency (ANEEL).