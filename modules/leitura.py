import pandas as pd
from pathlib import Path


# ler arquivos

def ler_excel(caminho, planilha=0, colunas=None, **kwargs):

    caminho = Path(caminho)

    dados = pd.read_excel(
        caminho,
        sheet_name=planilha,
        usecols=colunas,
        **kwargs
    )

    return dados


def ler_csv(
    caminho,
    colunas=None,
    separador=',',
    encoding='utf-8',
    **kwargs
):

    caminho = Path(caminho)

    dados = pd.read_csv(
        caminho,
        usecols=colunas,
        sep=separador,
        encoding=encoding,
        **kwargs
    )

    return dados


# tratar dados

def numericos(
    dados,
    colunas,
    preencher_com=0,
    tipo='int'
):

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors='coerce'
        ).fillna(preencher_com)

        dados[coluna] = dados[coluna].astype(tipo)

    return dados

def texto_vazio(
    dados,
    colunas,
    preencher_com='',
    tipo='str'
):

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = dados[coluna].fillna(preencher_com)

        dados[coluna] = dados[coluna].astype(tipo)

    return dados

def capitalize_text(
    dados,
    colunas
):

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = dados[coluna].str.title()

    return dados



