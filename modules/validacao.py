import pandas as pd
from . import terminal

# validar estrutura da base
def validar_df(dados, nome='DataFrame'):

    if not isinstance(dados, pd.DataFrame):
        mensagem = f'ERRO: {nome} não é um DataFrame válido.'
        terminal.erro(mensagem)
        raise TypeError(mensagem)

    if dados.empty:
        mensagem = f'ERRO: {nome} está vazio.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    return True

# validar colunas 
def validar_colunas(dados, colunas, nome='DataFrame'):

    validar_df(dados, nome)

    colunas_faltantes = set(colunas) - set(dados.columns)

    if colunas_faltantes:
        mensagem = f'ERRO: {nome} não contém as colunas obrigatórias: {colunas_faltantes}.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    return True

# valores ausentes 
def validar_nulos (dados, colunas, nome='DataFrame'):

    validar_df(dados, nome)

    colunas_nulas = [col for col in colunas if dados[col].isnull().any()]

    if colunas_nulas:
        mensagem = f'ERRO: {nome} contém valores nulos nas colunas: {colunas_nulas}.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    return True

# duplicados 
def validar_duplicados(dados, colunas, nome='DataFrame'):
    
    validar_df(dados, nome)

    duplicados = dados.duplicated(subset=colunas, keep=False)

    if duplicados.any():
        mensagem = f'ERRO: {nome} contém linhas duplicadas com base nas colunas: {colunas}.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    return True

# chave unica
def validar_chave_unica(dados, colunas, nome='DataFrame'):

    validar_df(dados, nome)

    if dados.duplicated(subset=colunas).any():
        mensagem = f'ERRO: {nome} não possui chave única com base nas colunas: {colunas}.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    return True


