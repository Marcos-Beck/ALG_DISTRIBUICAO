import pandas as pd
from modules import distribuicao, classificacao, relatorio, terminal
from config.caixa_encantada import campanha as campanha, preparacao, categorias

#! armaneza informacoes para criação de relatorios:
# comparativo: demanda x estoque disponivel 
# estoque_final: estoque restante apos distribuicao
# resultados: resultados por prioridade

def main():

    terminal.titulo('ALGORITMO DE DISTRIBUIÇÃO')

    try:

        #* preparacao das bases
        terminal.etapa('CARREGANDO E PREPARANDO BASES...')

        inscricoes, regioes, arrecadacao = preparacao.carregar_bases()

        terminal.info(f'Número de registros de inscrição: {inscricoes.shape[0]}')
        terminal.info(f'Municipios inscritos: {inscricoes["Cidade"].nunique()}')
        terminal.info(f'Número de registros de arrecadação: {arrecadacao.shape[0]}')
        terminal.info(f'Municipios arrecadadores: {arrecadacao["Cidade"].nunique()}')

        classificados = preparacao.classificar_inscricoes(
            inscricoes,
            regioes
        )

        grupos_geograficos = preparacao.preparar_grupos_geograficos(
            classificados
        )


        #* preparacao da distribuicao
        terminal.etapa('PREPARANDO GRUPOS DE DISTRIBUIÇÃO...')

        grupos_distribuicao = distribuicao.preparar_grupos_distribuicao(
            grupos_geograficos=grupos_geograficos,
            categorias=categorias.CATEGORIAS
        )


        #* calculo da demanda
        terminal.etapa('CALCULANDO DEMANDA REGIONAL...')

        demanda_regional = distribuicao.calcular_demanda_regional(
            grupos_distribuicao=grupos_distribuicao,
            categorias=categorias.CATEGORIAS
        )


        #* preparacao do estoque
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


        #* consolidacao
        terminal.etapa('CONSOLIDANDO DEMANDA E ESTOQUE...')

        comparativo = distribuicao.comparar_solicitado_estoque(
            demanda_regional=demanda_regional,
            estoques_regionais=estoques_regionais
        )

        resumo = distribuicao.resumir_demanda_estoque(
            demanda_regional,
            estoques_regionais
        )


        #* execucao da distribuicao
        terminal.etapa('EXECUTANDO DISTRIBUIÇÃO...')

        resultado_final = distribuicao.distribuir_todas_prioridades(
            grupos_distribuicao,
            resumo['estoque'],
            categorias.CATEGORIAS
        )

        df_resultados = resultado_final['instituicoes']
        estoque_final = resultado_final['estoque_restante'] # 
        resultados = resultado_final['resultados_prioridade']


        #* exportacao
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

        terminal.erro(f'FALHA NA DISTRIBUIÇÃO: {erro} D:')
        raise


if __name__ == '__main__':
    main()