import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from modules import leitura, classificacao, distribuicao, terminal

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

    terminal.etapa('CONFERINDO DEMANDA X ESTOQUE...')

    for regiao, localidades in comparativo.items():

        for localidade, faixas in localidades.items():

            print(f'\n========== {regiao} / {localidade} ==========')

            for faixa, valores in faixas.items():

                print(
                    f"\n{faixa}:"
                    f"\n  Feminino: "
                    f"Demanda {valores['demanda_feminino']} | "
                    f"Estoque {valores['estoque_feminino']} | "
                    f"Déficit {valores['deficit_feminino']}"
                    f"\n  Masculino: "
                    f"Demanda {valores['demanda_masculino']} | "
                    f"Estoque {valores['estoque_masculino']} | "
                    f"Déficit {valores['deficit_masculino']}"
                    f"\n  Unissex disponível: {valores['estoque_unissex']}"
                )

    terminal.info(
        f'{len(comparativo)} regiões presentes no comparativo.'
    )

    terminal.sucesso('COMPARATIVO CONCLUÍDO! :D')

except Exception as erro:
     terminal.erro(f'Falha no teste: {erro}')
     
# debug: detail do erro
# except Exception as erro:
#     import traceback
#     traceback.print_exc()
#     terminal.erro(f'Falha no teste: {erro}')

