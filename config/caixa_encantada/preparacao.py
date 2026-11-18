from modules import leitura, classificacao
from config.caixa_encantada import fontes, categorias, regras
from config.caixa_encantada import config as campanha

# carregar e preparar as bases de dados do projeto
def carregar_bases():

    # carregar inscricoes
    inscricoes = leitura.ler_excel(
        fontes.ARQ_INSCRICOES,
        planilha=fontes.PLAN_INSCRICOES,
        colunas=fontes.COL_INSC
    )

    # carregar regioes
    regioes = leitura.ler_csv(
        fontes.ARQ_REGIAO,
        colunas=fontes.COL_REG
    )

    # carregar arrecadacoes
    arrecadacao = leitura.ler_excel(
        fontes.ARQ_ARRECADACOES,
        planilha=fontes.PLAN_ARRECADACOES,
        colunas=fontes.COL_ARRE
    )

    # identificar colunas numericas do estoque
    colunas_estoque = [
        categorias.CATEGORIAS[faixa][genero]['estoque']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    colunas_estoque += [
        categorias.CATEGORIAS[faixa]['unissex']
        for faixa in categorias.CATEGORIAS
    ]

    # tratar campos numericos
    arrecadacao = leitura.numericos(
        dados=arrecadacao,
        colunas=colunas_estoque
    )

    return inscricoes, regioes, arrecadacao

# classificar inscricoes e preparar grupos geograficos
def classificar_inscricoes(inscricoes, regioes):

    # identificar colunas de solicitacao
    colunas_solicitacao = [
        categorias.CATEGORIAS[faixa][genero]['demanda']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    # classificacao quantitativa
    classificados = classificacao.classificar_instituicoes(
        dados=inscricoes,
        colunas_solicitacao=colunas_solicitacao,
        prioridades=campanha.PRIORIDADES_QTDE,
        coluna_beneficiario='Beneficiario',
        coluna_cnpj='CNPJ',
        extrair_ordem=regras.extrair_ordem_insc,
        validar_cnpj=regras.validar_cnpj
    )

    # classificação geografica
    classificados = classificacao.classificar_geografia(
        dados=classificados,
        coluna_cidade='Cidade',
        regioes=regioes,
        coluna_municipio='Município',
        coluna_regiao='Região',
        capital=campanha.CAPITAL
    )

    return classificados

# preparar grupos geograficos
def preparar_grupos_geograficos(classificados):

    grupos_geograficos = classificacao.preparar_grupos_geograficos(
        dados=classificados,
        prioridades=campanha.PRIORIDADES_QTDE
    )

    return grupos_geograficos




