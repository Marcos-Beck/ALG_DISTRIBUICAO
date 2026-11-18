import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from modules import leitura, classificacao, distribuicao, relatorio, terminal

from config.caixa_encantada import fontes, categorias, regras
from config.caixa_encantada import campanha as campanha

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

    arrecadacao = leitura.ler_excel(
        fontes.ARQ_ARRECADACOES,
        planilha=fontes.PLAN_ARRECADACOES,
        colunas=fontes.COL_ARRE
    )

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

    # ETAPA 6 - SEPARAR CAPITAL E INTERIOR

    terminal.etapa('SEPARANDO CAPITAL E INTERIOR...')

    grupos_geograficos = {}

    for prioridade, regioes_grupo in grupos_completos.items():

        for regiao, instituicoes in regioes_grupo.items():

            grupos_geograficos.setdefault(regiao, {})

            for localidade, grupo in instituicoes.groupby(
                'Localidade',
                sort=False
            ):

                grupos_geograficos[regiao].setdefault(
                    localidade,
                    {}
                )

                grupos_geograficos[regiao][localidade][prioridade] = (
                    grupo.copy()
                )

    grupos_geograficos_novo = classificacao.preparar_grupos_geograficos(
        dados=classificados,
        prioridades=campanha.PRIORIDADES_QTDE
    )

    # ETAPA 7 - PREPARAR GRUPOS PARA DISTRIBUIÇÃO

    terminal.etapa('PREPARANDO GRUPOS DE DISTRIBUIÇÃO...')

    grupos_distribuicao = distribuicao.preparar_grupos_distribuicao(
        grupos_geograficos=grupos_geograficos,
        categorias=categorias.CATEGORIAS
    )


    # ETAPA 9 - CALCULAR DEMANDA REGIONAL

    terminal.etapa('CALCULANDO DEMANDA REGIONAL...')

    demanda_regional = distribuicao.calcular_demanda_regional(
        grupos_distribuicao=grupos_distribuicao,
        categorias=categorias.CATEGORIAS
    )

    # for prioridade, regioes_demanda in demanda_regional.items():

    #     print(f'\n========== DEMANDA P{prioridade} ==========')

    #     for regiao, localidades in regioes_demanda.items():

    #         for localidade, faixas in localidades.items():

    #             print(f'\n{regiao} / {localidade}')

    #             for faixa, generos in faixas.items():

    #                 print(
    #                     f"  {faixa}: "
    #                     f"Feminino: {generos['feminino']} | "
    #                     f"Masculino: {generos['masculino']}"
    #                 )

# ETAPA 10 - PREPARAR ESTOQUE

    terminal.etapa('PREPARANDO ESTOQUE...')

    arrecadacao = classificacao.classificar_geografia(
        dados=arrecadacao,
        coluna_cidade='Cidade',
        regioes=regioes,
        coluna_municipio='Município',
        coluna_regiao='Região',
        capital=campanha.CAPITAL
    )

    estoques_regionais = distribuicao.estruturar_estoque(
        arrecadacao=arrecadacao,
        categorias=categorias.CATEGORIAS
    )

    terminal.sucesso('ESTOQUE PREPARADO!')

    # ETAPA 11 - COMPARAR DEMANDA E ESTOQUE

    terminal.etapa('COMPARANDO SOLICITADO E ESTOQUE...')

    comparativo = distribuicao.comparar_solicitado_estoque(
        demanda_regional=demanda_regional,
        estoques_regionais=estoques_regionais
    )

    # ETAPA 12 - CONFERIR COMPARATIVO

    # terminal.etapa('CONFERINDO DEMANDA X ESTOQUE...')

    # for regiao, localidades in comparativo.items():

    #     for localidade, faixas in localidades.items():

    #         print(f'\n========== {regiao} / {localidade} ==========')

    #         for faixa, valores in faixas.items():

    #             print(
    #                 f"\n{faixa}:"
    #                 f"\n  Feminino: "
    #                 f"Demanda {valores['demanda_feminino']} | "
    #                 f"Estoque {valores['estoque_feminino']} | "
    #                 f"Déficit {valores['deficit_feminino']}"
    #                 f"\n  Masculino: "
    #                 f"Demanda {valores['demanda_masculino']} | "
    #                 f"Estoque {valores['estoque_masculino']} | "
    #                 f"Déficit {valores['deficit_masculino']}"
    #                 f"\n  Unissex disponível: {valores['estoque_unissex']}"
    #             )

    # terminal.info(
    #     f'{len(comparativo)} regiões presentes no comparativo.'
    # )

    # terminal.sucesso('COMPARATIVO CONCLUÍDO! :D')

    # ETAPA 13 - CONSOLIDAR DEMANDA E ESTOQUE

    terminal.etapa('CONSOLIDANDO DEMANDA E ESTOQUE...')

    resumo = distribuicao.resumir_demanda_estoque(
        demanda_regional=demanda_regional,
        estoques_regionais=estoques_regionais
    )

    for prioridade, faixas in resumo['demanda'].items():

        print(f'\n========== DEMANDA P{prioridade} ==========')

        for faixa, generos in faixas.items():

            print(
                f"{faixa}: "
                f"Feminino: {generos['feminino']} | "
                f"Masculino: {generos['masculino']}"
            )

    print('\n========== ESTOQUE TOTAL ==========')

    for faixa, generos in resumo['estoque'].items():

        print(
            f"{faixa}: "
            f"Feminino: {generos['feminino']} | "
            f"Masculino: {generos['masculino']} | "
            f"Unissex: {generos['unissex']}"
        )

    terminal.sucesso('RESUMO CONSOLIDADO!')

    terminal.etapa('EXECUTANDO DISTRIBUIÇÃO DE TODAS AS PRIORIDADES...')

    resultado_final = distribuicao.distribuir_todas_prioridades(
        grupos_distribuicao=grupos_distribuicao,
        estoques=resumo['estoque'],
        categorias=categorias.CATEGORIAS
    )

    df_resultados = resultado_final['instituicoes']
    estoque_final = resultado_final['estoque_restante']
    resultados = resultado_final['resultados_prioridade']

    terminal.sucesso('DISTRIBUIÇÃO CONSOLIDADA!')

    terminal.info(
        f'Instituições: {len(df_resultados)}'
    )

    terminal.info(
        f'Colunas: {len(df_resultados.columns)}'
    )

    terminal.info(
        f'Solicitado: {df_resultados["Solicitado Total"].sum()}'
    )

    terminal.info(
        f'Atendido: {df_resultados["Atendido Total"].sum()}'
    )

    terminal.info(
        f'Faltante: {df_resultados["Falta Total"].sum()}'
    )


    terminal.sucesso('SIMULAÇÃO PRIORIDADE CONCLUÍDA!')

    for prioridade, resultado in resultados.items():

        solicitado = sum(
            inst['total_solicitado_fem'] + inst['total_solicitado_masc']
            for inst in resultado['instituicoes']
        )

        distribuido = sum(
            inst['total_distribuido']
            for inst in resultado['instituicoes']
        )

        falta = sum(
            inst['falta_total']
            for inst in resultado['instituicoes']
        )

        print(f'\n{prioridade}')
        print(f'Solicitado: {solicitado}')
        print(f'Distribuído: {distribuido}')
        print(f'Não atendido: {falta}')



    print('\n========== CONFERÊNCIA GLOBAL DE ESTOQUE ==========')

    for faixa, generos in resumo['estoque'].items():

        # Soma o consumo físico das três prioridades
        consumo_fem = sum(
            inst['faixas'][faixa]['especifico_fem']
            for resultado in resultados.values()
            for inst in resultado['instituicoes']
        )

        consumo_masc = sum(
            inst['faixas'][faixa]['especifico_masc']
            for resultado in resultados.values()
            for inst in resultado['instituicoes']
        )

        consumo_uni = sum(
            inst['faixas'][faixa]['unissex_fem']
            + inst['faixas'][faixa]['unissex_masc']
            for resultado in resultados.values()
            for inst in resultado['instituicoes']
        )

        estoque_final = resultado_final['estoque_restante'][faixa]

        print(f'\nFaixa {faixa}')

        print(
            f"Feminino | Inicial: {generos['feminino']} "
            f"| Consumido: {consumo_fem} "
            f"| Final: {estoque_final['feminino']}"
        )

        print(
            f"Masculino | Inicial: {generos['masculino']} "
            f"| Consumido: {consumo_masc} "
            f"| Final: {estoque_final['masculino']}"
        )

        print(
            f"Unissex | Inicial: {generos['unissex']} "
            f"| Consumido: {consumo_uni} "
            f"| Final: {estoque_final['unissex']}"
        )

    # ETAPA 14 - CONFERIR DATAFRAME FINAL
    terminal.etapa('CONFERINDO DATAFRAME FINAL...')

    terminal.info(
        f'Quantidade de instituições: {len(df_resultados)}'
    )

    terminal.info(
        f'Quantidade de colunas: {len(df_resultados.columns)}'
    )

    terminal.info(
        f'Instituições por prioridade:\n'
        f'{df_resultados["Prioridade"].value_counts().sort_index()}'
    )

    terminal.info(
        f'Valores nulos: {df_resultados.isna().sum().sum()}'
    )

    terminal.info(
        f'Registros duplicados: {df_resultados.duplicated().sum()}'
    )

    assert list(grupos_geograficos.keys()) == list(grupos_geograficos_novo.keys())

    for regiao in grupos_geograficos:

        assert list(grupos_geograficos[regiao].keys()) == list(
            grupos_geograficos_novo[regiao].keys()
        )

        for localidade in grupos_geograficos[regiao]:

            assert list(grupos_geograficos[regiao][localidade].keys()) == list(
                grupos_geograficos_novo[regiao][localidade].keys()
            )

            for prioridade in grupos_geograficos[regiao][localidade]:

                antigo = grupos_geograficos[regiao][localidade][prioridade]
                novo = grupos_geograficos_novo[regiao][localidade][prioridade]

                assert antigo.equals(novo)

    print('Teste de agrupamento geográfico aprovado!')

    print('Teste de agrupamento geográfico aprovado!')

#     # ETAPA 15 - EXPORTAR RESULTADOS
#     terminal.etapa('EXPORTANDO RESULTADOS...')

#     arquivos = relatorio.exportar_resultados(
#         dados=df_resultados,
#         nome=campanha.NOME,
#         ano=campanha.ANO
#     )

#     terminal.sucesso('ARQUIVOS EXPORTADOS! :D')

#     terminal.info(f'Excel: {arquivos["excel"]}')
#     terminal.info(f'CSV: {arquivos["csv"]}')

except Exception as erro:
    terminal.erro(f'Falha no teste: {erro}')
     
#  debug: detail do erro
# except Exception as erro:
#      import traceback
#      traceback.print_exc()
#      terminal.erro(f'Falha no teste: {erro}')

