import time, streamlit as st
from functools import wraps

def wrapperExec(func):
    """Proxy composto que aplica:
        - tratamento de erros
        - validação de dados
        - medição de tempo
    """
    @wraps(func)
    def wrapper(dados, *args, **kwargs):
        if dados is None or not dados:
            st.warning("Por favor, carregue um arquivo JSON válido.")
            return
        try:
            inicio = time.time()
            result = func(dados, *args, **kwargs)
            fim = time.time()
            st.sidebar.caption(f"Tempo de execução: {fim - inicio:.4f}s")

            return result
        except Exception as e:
            st.error(f"Erro ao executar {func.__name__}: {e}")
    return wrapper