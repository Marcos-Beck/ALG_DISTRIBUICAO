import pandas as pd
from pathlib import Path
from . import terminal

#* = resumo de funcao ou grupo de funcoes
### = opcional

#* ler arquivos

# ler excel
def ler_excel(
    caminho, 
    planilha=0, 
    colunas=None, 
    **kwargs
    ):

    ### terminal.etapa(f'[ LEITURA ] Lendo planilha...')

    caminho = Path(caminho)

    dados = pd.read_excel(
        caminho,
        sheet_name=planilha,
        usecols=colunas,
        **kwargs
    )
    
    return dados

# ler csv
def ler_csv(
    caminho,
    nome_arquivo=None,
    colunas=None,
    separador=',',
    encoding='utf-8',
    **kwargs
):

    if nome_arquivo is None:
        nome_arquivo = Path(caminho).name

    ### terminal.etapa(f'[ LEITURA ] Lendo arquivo csv...')

    caminho = Path(caminho)

    dados = pd.read_csv(
        caminho,
        usecols=colunas,
        sep=separador,
        encoding=encoding,
        **kwargs
    )

    return dados


#* tratar dados

# converter para numerico
def numericos(
    dados,
    colunas,
    preencher_com=0,
    tipo='int'
):

    ### terminal.etapa(f'[ TRATAMENTO ] Convertendo colunas para numérico...')

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = pd.to_numeric(
            dados[coluna],
            errors='coerce'
        ).fillna(preencher_com)

        dados[coluna] = dados[coluna].astype(tipo)

    return dados

# preencher nulos e converter para string
def texto_vazio(
    dados,
    colunas,
    preencher_com='',
    tipo='str'
):

    ### terminal.etapa(f'[ TRATAMENTO ] Preenchendo nulos e convertendo para string...')

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = dados[coluna].fillna(preencher_com)

        dados[coluna] = dados[coluna].astype(tipo)

    return dados

# capitalizar texto
def capitalize_text(
    dados,
    colunas
):
    ### terminal.etapa(f'[ TRATAMENTO ] Capitalizando texto nas colunas...')

    dados = dados.copy()

    for coluna in colunas:

        dados[coluna] = dados[coluna].str.title()

    return dados