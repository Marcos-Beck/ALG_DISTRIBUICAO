import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from modules import leitura, classificacao, terminal

from config.caixa_encantada import fontes, categorias, regras
from config.caixa_encantada import config as campanha

terminal.titulo('TESTE DE INTEGRAÇÃO: PRIORIDADE E GEOGRAFIA')

try:

    # ETAPA 1 - CARREGAR BASES
    terminal.etapa('CARREGANDO BASES...')

    inscricoes = leitura.ler_excel(
        fontes.ARQ_INSCRICOES,
        planilha=fontes.PLAN_INSCRICOES,
        colunas=fontes.COL_INSC
    )

    regioes = leitura.ler_csv(
        fontes.ARQ_REGIAO,
        colunas=fontes.COL_REG
    )

    # ETAPA 2 - CLASSIFICAR INSTITUIÇÕES
    terminal.etapa('CLASSIFICANDO INSTITUIÇÕES...')

    colunas_solicitacao = [
        categorias.CATEGORIAS[faixa][genero]['demanda']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    classificados = classificacao.classificar_instituicoes(
        dados=inscricoes,
        colunas_solicitacao=colunas_solicitacao,
        prioridades=campanha.PRIORIDADES_QTDE,
        coluna_beneficiario='Beneficiario',
        coluna_cnpj='CNPJ',
        extrair_ordem=regras.extrair_ordem_insc,
        validar_cnpj=regras.validar_cnpj
    )

    # ETAPA 3 - CLASSIFICAR GEOGRAFIA
    terminal.etapa('CLASSIFICANDO GEOGRAFIA...')

    classificados = classificacao.classificar_geografia(
        dados=classificados,
        coluna_cidade='Cidade',
        regioes=regioes,
        coluna_municipio='Município',
        coluna_regiao='Região',
        capital=campanha.CAPITAL
    )

    # ETAPA 4 - SEPARAR PRIORIDADES
    terminal.etapa('SEPARANDO PRIORIDADES...')

    grupos_prioridade = classificacao.separar_prioridade(
        dados=classificados,
        coluna_prioridade='Prioridade',
        prioridades=campanha.PRIORIDADES_QTDE
    )

    # ETAPA 5 - ORGANIZAR POR REGIÃO
    terminal.etapa('ORGANIZANDO POR REGIÃO...')

    grupos_completos = {}

    for prioridade, instituicoes in grupos_prioridade.items():

        grupos_completos[prioridade] = (
            classificacao.organizar_por_regiao(instituicoes)
        )

    # ETAPA 6 - RESUMO
    for prioridade, regioes_grupo in grupos_completos.items():

        print(f'\n========== PRIORIDADE P{prioridade} ==========')

        for regiao, instituicoes in regioes_grupo.items():

            print(f'\nREGIÃO: {regiao}')

            print(
                instituicoes[
                    ['Beneficiario', 'Cidade', 'Solicitação Total',
                     'Prioridade', 'Localidade']
                ].to_string(index=False)
            )

            terminal.info(
                f'{len(instituicoes)} instituições'
            )

    terminal.sucesso('INTEGRAÇÃO CONCLUÍDA!')

except Exception as e:

    terminal.erro(f'Falha no teste: {e}')
