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


        #* reserva obrigatoria de estoque
        terminal.etapa('CALCULANDO RESERVA OBRIGATÓRIA DE ESTOQUE...')

        estoque_reserva = distribuicao.separar_reserva_estoque(
            estoques=resumo['estoque'],
            percentual=campanha.RESERVA['percentual'],
            ativa=campanha.RESERVA['ativa'],
            arredondamento=campanha.RESERVA['arredondamento']
        )

        total_bruto = sum(
            sum(generos.values())
            for generos in estoque_reserva['bruto'].values()
        )
        total_reservado = sum(
            sum(generos.values())
            for generos in estoque_reserva['reservado'].values()
        )
        total_distribuivel = sum(
            sum(generos.values())
            for generos in estoque_reserva['distribuivel'].values()
        )

        terminal.info(f'Estoque bruto arrecadado: {total_bruto}')
        terminal.info(f'Estoque reservado ({campanha.RESERVA["percentual"] * 100:.0f}%): {total_reservado}')
        terminal.info(f'Estoque disponivel para distribuicao: {total_distribuivel}')


        #* execucao da distribuicao
        terminal.etapa('EXECUTANDO DISTRIBUIÇÃO...')

        resultado_final = distribuicao.distribuir_todas_prioridades(
            grupos_distribuicao,
            estoque_reserva['distribuivel'],
            categorias.CATEGORIAS,
            minimo=campanha.MINIMO_ATENDIMENTO,
            penalizacao=campanha.PENALIZACAO,
            prioridades_proporcionais=campanha.MINIMO_ATENDIMENTO.get('prioridades', [])
        )

        df_resultados = resultado_final['instituicoes']
        estoque_final = resultado_final['estoque_restante']
        resultados = resultado_final['resultados_prioridade']

        total_distribuido = int(df_resultados['Atendido Total'].sum())
        total_restante_distribuivel = sum(
            sum(generos.values())
            for generos in estoque_final.values()
        )

        terminal.info(f'Total distribuido: {total_distribuido}')
        terminal.info(f'Estoque restante distribuivel (nao inclui reserva): {total_restante_distribuivel}')
        terminal.info(f'Reserva intacta: {total_reservado}')

        resultado_final['reserva'] = estoque_reserva

        resumos_diagnostico = relatorio.gerar_resumos_diagnostico(
            df_resultados=df_resultados,
            estoque_reserva=estoque_reserva,
            estoque_restante=estoque_final
        )
        resultado_final['resumos'] = resumos_diagnostico

        for _, row in resumos_diagnostico['Resumo_Prioridades'].iterrows():
            terminal.info(
                f'P{int(row["Prioridade"])}: {int(row["Instituicoes"])} inst | '
                f'Demanda: {int(row["Solicitado Total"])} | '
                f'Atendido: {int(row["Atendido Total"])} ({row["Percentual Atendimento (%)"]:.2f}%)'
            )


        #* exportacao
        terminal.etapa('EXPORTANDO RESULTADOS...')

        arquivos = relatorio.exportar_resultados(
            dados=df_resultados,
            nome=campanha.NOME,
            ano=campanha.ANO,
            resumos=resumos_diagnostico
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