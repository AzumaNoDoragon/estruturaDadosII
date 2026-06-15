import time, streamlit as st
from functools import wraps

def tratarErro(func):
    """Trata erros"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"Erro ao executar {func.__name__}: {e}")
    return wrapper

def verifyData(func):
    """Valida os dados do Json"""
    @wraps(func)
    def wrapper(dados, *args, **kwargs):
        if dados is None or not dados:
            st.warning("Por favor, carregue um arquivo JSON válido.")
            return
        return func(dados, *args, **kwargs)
    return wrapper

def medirExec(func):
    """Mede o tempo de execução das funções"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        result = func(*args, **kwargs)
        fim = time.time()
        st.sidebar.caption(f"Tempo de execução: {fim - inicio:.4f}s")
        return result
    return wrapper

def wrapperExec(func):
    """Proxy composto que aplica:
    - tratamento de erros
    - validação de dados
    - medição de tempo
    """
    funcArmazenada = tratarErro(
        verifyData(
            medirExec(func)
        )
    )
    
    def wrapper(*args, **kwargs):
        return funcArmazenada(*args, **kwargs)
    return wrapper
