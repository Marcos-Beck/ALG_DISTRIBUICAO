from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] # raiz do projeto

DATA = ROOT / 'data' / 'CE'

# arquivos og

ARQ_INSCRICOES = DATA / 'Conjunto de Dados - CE 26.xlsx'

ARQ_ARRECADACOES = DATA / 'BASE_DADOS_CE_2025.xlsx'

ARQ_REGIAO = DATA / 'Regiao.csv'

# planilhas

PLAN_INSCRICOES = 'Inscrições'

PLAN_ARRECADACOES = 'Arrecadações'

# colunas

COL_INSC = [
    'Beneficiario',
    'Nome resp.',
    'Contato resp.',
    'Cidade',
    'CNPJ',

    'F 0-3',
    'F 4-7',
    'F 8-12',
    'M 0-3',
    'M 4-7',
    'M 8-12'
]

COL_ARRE = [
    'Cidade',
    'Órgão',

    'Fem 0-3',
    'Fem 4-7',
    'Fem 8+',
    'Masc 0-3',
    'Masc 4-7',
    'Masc 8+',
    'Uni 0-3',
    'Uni 4-7',
    'Uni 8+'
]

COL_REG = [
    'Região',
    'Município'
]