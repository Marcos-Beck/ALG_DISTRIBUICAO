from modules import leitura, terminal, classificacao

terminal.titulo('INICIANDO ALGORITMO DE DISTRIBUIÇÃO...')

try:

    # etapa 1 - data 
    terminal.etapa('ETAPA 1 PROCESSANDO...')
    inscricoes, arrecadacao = leitura.carregar_bases() # carrega as bases (obvio)

    terminal.info(
        f'{len(inscricoes)} registros de inscrições e {inscricoes['Total'].sum()} total solicitado'
    )
    terminal.info(
        f'{len(arrecadacao)} registros de arrecadação e {arrecadacao['Total'].sum()} total arrecadado'
    )

    # etapa 2 - classificacao
    terminal.etapa('ETAPA 2 PROCESSANDO...')
    classificados = classificacao.classificar_pedidos(
        inscricoes
        )

    # resumo
    terminal.info(
        f'Prioridade 1: {len(classificados[classificados["Prioridade"] == 1])} pedidos'
    )
    terminal.info(
        f'Prioridade 2: {len(classificados[classificados["Prioridade"] == 2])} pedidos'
    )
    terminal.info(
        f'Prioridade 3: {len(classificados[classificados["Prioridade"] == 3])} pedidos'
    )

    terminal.sucesso('Processamento concluído! -3-')

except Exception as e:
    terminal.erro(
        f'Falha na execução D: {e}'
    )

# roda o diagnostico
# leitura.diagnostico(inscricoes, arrecadacao)

# mostra as 5 primeiras linhas da base classificada
#print(
#    classificados[
#        ['Beneficiario', 'Cidade', 'Total', 'Prioridade']
#    ].head(5).to_string(index=False)
#)