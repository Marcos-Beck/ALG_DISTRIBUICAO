from modules import distribuicao, classificacao, relatorio, terminal
from config.caixa_encantada import campanha as campanha, preparacao, categorias


def main():

    terminal.titulo('ALGORITMO DE DISTRIBUIÇÃO')

    try:

        # PREPARAÇÃO DAS BASES

        terminal.etapa('CARREGANDO E PREPARANDO BASES...')

        inscricoes, regioes, arrecadacao = preparacao.carregar_bases()

        classificados = preparacao.classificar_inscricoes(
            inscricoes,
            regioes
        )

        grupos_geograficos = preparacao.preparar_grupos_geograficos(
            classificados
        )


        # PREPARACAO DA DISTRIBUIÇÃO

        terminal.etapa('PREPARANDO GRUPOS DE DISTRIBUIÇÃO...')

        grupos_distribuicao = distribuicao.preparar_grupos_distribuicao(
            grupos_geograficos=grupos_geograficos,
            categorias=categorias.CATEGORIAS
        )


        # CALCULO DA DEMANDA/SOLICITADO

        terminal.etapa('CALCULANDO DEMANDA REGIONAL...')

        demanda_regional = distribuicao.calcular_demanda_regional(
            grupos_distribuicao=grupos_distribuicao,
            categorias=categorias.CATEGORIAS
        )


        # PREPARACAO DO ESTOQUE

        terminal.etapa('ESTRUTURANDO ESTOQUE...')

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


        # CONSOLIDACAO

        terminal.etapa('CONSOLIDANDO DEMANDA E ESTOQUE...')

        comparativo = distribuicao.comparar_solicitado_estoque(
            demanda_regional=demanda_regional,
            estoques_regionais=estoques_regionais
        )

        resumo = distribuicao.resumir_demanda_estoque(
            demanda_regional,
            estoques_regionais
        )


        # EXECUCAO DA DISTRIBUICAO

        terminal.etapa('EXECUTANDO DISTRIBUIÇÃO...')

        resultado_final = distribuicao.distribuir_todas_prioridades(
            grupos_distribuicao,
            resumo['estoque'],
            categorias.CATEGORIAS
        )

        df_resultados = resultado_final['instituicoes']
        estoque_final = resultado_final['estoque_restante']
        resultados = resultado_final['resultados_prioridade']


        # EXPORTACAO

        terminal.etapa('EXPORTANDO RESULTADOS...')

        arquivos = relatorio.exportar_resultados(
            dados=df_resultados,
            nome=campanha.NOME,
            ano=campanha.ANO
        )

        terminal.sucesso('DISTRIBUIÇÃO CONCLUÍDA! :D')

        print(f'Excel: {arquivos["excel"]}')
        print(f'CSV: {arquivos["csv"]}')

        return resultado_final


    except Exception as erro:

        terminal.erro(f'FALHA NA DISTRIBUIÇÃO: {erro}')
        raise


if __name__ == '__main__':
    main()
