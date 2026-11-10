import pandas as pd
import pathlib as pl
from modules import dicionario 

# caminho dos arquivos

BASE = pl.Path(__file__).resolve().parent.parent
DATA = BASE / 'data'

ARQ_INSC = DATA / 'Conjunto de Dados - CE 26.xlsx'
ARQ_ARRE = DATA / 'BASE_DADOS_CE_2025.xlsx'

def carregar_bases():

    print('\nCarregando bases de dados...\n')

    # inscricoes
    colunas_inscricao = (
        dicionario.INSCRICOES['str'] 
        + dicionario.INSCRICOES['int']
    )

    # arrecadacao
    colunas_arrecadacao = (
        dicionario.ARRECADACAO['str']
        + dicionario.ARRECADACAO['int']
    )

    # ler planilhas

    inscricoes = pd.read_excel(
        ARQ_INSC,
        sheet_name='Inscrições',
        usecols=colunas_inscricao
    )
    arrecadacao = pd.read_excel(
        ARQ_ARRE,
        sheet_name='Arrecadações',
        usecols=colunas_arrecadacao
    )

    print('\nBases carregadas com sucesso! :)\n')

    # tratar quantidades

    for coluna in dicionario.INSCRICOES['int']:
        inscricoes[coluna] = pd.to_numeric(
            inscricoes[coluna],
            errors='coerce'
            ).fillna(0).astype(int)

    for coluna in dicionario.ARRECADACAO['int']:
        arrecadacao[coluna] = pd.to_numeric(
            arrecadacao[coluna],
            errors='coerce'
            ).fillna(0).astype(int)

    # demanda por insticao
    inscricoes['Total'] = (
        inscricoes[dicionario.INSCRICOES['int']].sum(axis=1)
        )

    # arrecadacao por reg (cidade + orgao)
    arrecadacao['Total'] = (
    arrecadacao[dicionario.ARRECADACAO['int']].sum(axis=1)
        )

    return inscricoes, arrecadacao

def diagnostico(inscricoes, arrecadacao):
    print('\nDiagnóstico das bases de dados:\n')

    print('\n------------INSCRIÇÕES------------\n')
    print(f'Registros: {len(inscricoes)}')
    print(f'\nPré-Visualização:\n {inscricoes.head()}')
    print(f'\nNulos:\n {inscricoes.isnull().sum()}') # TEM que retornar 0, caso contrario erro no tratamento
    print(f'\nDescrição:\n {inscricoes.describe()}')
    print(f'\n Colunas:\n {inscricoes.columns.tolist()}')

    print('\n------------ARRECADACAO------------\n')
    print(f'Registros: {len(arrecadacao)}')
    print(f'\nPré-Visualização:\n {arrecadacao.head()}')
    print(f'\nNulos:\n {arrecadacao.isnull().sum()}') # TEM que retornar 0, caso contrario erro no tratamento
    print(f'\nDescrição:\n {arrecadacao.describe()}')
    print(f'\nColunas:\n {arrecadacao.columns.tolist()}')
