import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))


from modules import leitura, classificacao, distribuicao, terminal

from config.caixa_encantada import fontes, categorias
from config.caixa_encantada import config as campanha


terminal.titulo('TESTE DE PREPARAÇÃO DA ARRECADAÇÃO')

try:

    # ETAPA 1 - CARREGAR BASES
    terminal.etapa('CARREGANDO ARRECADAÇÃO E REGIÕES...')

    arrecadacao = leitura.ler_excel(
        fontes.ARQ_ARRECADACOES,
        planilha=fontes.PLAN_ARRECADACOES,  
        colunas=fontes.COL_ARRE
    )

    regioes = leitura.ler_csv(
        fontes.ARQ_REGIAO,
        colunas=fontes.COL_REG
    )

    terminal.info(
        f'{len(arrecadacao)} registros de arrecadação carregados.'
    )

    # ETAPA 2 - TRATAR QUANTIDADES
    terminal.etapa('TRATANDO QUANTIDADES...')

    colunas_estoque = [
        categorias.CATEGORIAS[faixa][genero]['estoque']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    colunas_estoque += [
        categorias.CATEGORIAS[faixa]['unissex']
        for faixa in categorias.CATEGORIAS
    ]

    arrecadacao = leitura.numericos(
        dados=arrecadacao,
        colunas=colunas_estoque
    )

    terminal.sucesso('Quantidades tratadas.')

    # ETAPA 3 - CLASSIFICAR GEOGRAFIA
    terminal.etapa('CLASSIFICANDO GEOGRAFIA...')

    arrecadacao = classificacao.classificar_geografia(
        dados=arrecadacao,
        coluna_cidade='Cidade',
        regioes=regioes,
        coluna_municipio='Município',
        coluna_regiao='Região',
        capital=campanha.CAPITAL
    )

    # ETAPA 4 - ESTRUTURAR ESTOQUE

    terminal.etapa('ESTRUTURANDO ESTOQUE...')

    estoques_regionais = distribuicao.estruturar_estoque(
        arrecadacao=arrecadacao,
        categorias=categorias.CATEGORIAS
    )
    
    terminal.etapa('CONFERINDO ESTOQUE ESTRUTURADO...')

    for regiao, localidades in estoques_regionais.items():

        for localidade, faixas in localidades.items():

            total = sum(
                valores['feminino']
                + valores['masculino']
                + valores['unissex']
                for valores in faixas.values()
            )

            terminal.info(
                f'{regiao} / {localidade}: {total} brinquedos'
            )
    # ETAPA 5 - CONFERIR RESULTADOS
    terminal.etapa('CONFERINDO ESTOQUES...')

    print('\n========== REGISTROS PREPARADOS ==========')

    print(
        arrecadacao[
            ['Cidade', 'Órgão', 'Região', 'Localidade']
            + colunas_estoque
        ].head(10).to_string(index=False)
    )

    print('\n========== ESTOQUE POR REGIÃO E LOCALIDADE ==========')

    resumo = arrecadacao.groupby(
        ['Região', 'Localidade']
    )[colunas_estoque].sum()

    print(resumo.to_string())

    terminal.sucesso('PREPARAÇÃO DA ARRECADAÇÃO CONCLUÍDA!')

except Exception as e:

    terminal.erro(f'Falha no teste: {e}')
