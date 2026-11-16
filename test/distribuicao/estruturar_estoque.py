
from modules import leitura, classificacao, distribuicao, terminal

from config.caixa_encantada import fontes, categorias

terminal.titulo('TESTE DE ESTRUTURAÇÃO DOS ESTOQUES')

try:

    # carregar arrecadacao
    arrecadacao = leitura.ler_excel(
        fontes.ARQ_ARRECADACOES,
        planilha=fontes.PLAN_ARRECADACOES,
        colunas=fontes.COL_ARRE
    )

    # preparar quantidades
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
        arrecadacao,
        colunas_estoque
    )

    # classificar geografia
    regioes = leitura.ler_csv(
        fontes.ARQ_REGIAO,
        colunas=fontes.COL_REG
    )

    arrecadacao = classificacao.classificar_geografia(
        dados=arrecadacao,
        coluna_cidade='Cidade',
        regioes=regioes,
        coluna_municipio='Município',
        coluna_regiao='Região',
        capital='Campo Grande'
    )

    # estruturar estoque
    estoques = distribuicao.estruturar_estoque(
        arrecadacao=arrecadacao,
        categorias=categorias.CATEGORIAS
    )

    # resultado
    for regiao, localidades in estoques.items():

        print(f'\nREGIÃO: {regiao}')

        for localidade, faixas in localidades.items():

            print(f'  LOCALIDADE: {localidade}')

            for faixa, generos in faixas.items():

                print(
                    f'    {faixa}: {generos}'
                )

    terminal.sucesso('Estruturação dos estoques concluída :D')

except Exception as erro:
    terminal.erro(f'Falha no teste: {erro}')
