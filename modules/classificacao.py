from modules import terminal

def classificar_pedidos(inscricoes):
    terminal.etapa('Classsificando pedidos por quantidades...')

    # preservar base og
    classificados = inscricoes.copy()

    terminal.etapa('Calculando prioridades...')

    # definir prioridade 
    def definir_prioridade(quantidade):

        if quantidade <= 200:
            return 1

        elif quantidade <= 260:
            return 2

        else:
            return 3

    classificados['Prioridade'] = (
        classificados['Total']
        .apply(definir_prioridade)
    )

    # ordem por prioridade e total
    classificados = classificados.sort_values(
        by=['Prioridade', 'Total'],
        ascending=[True, False],
        kind='stable'
    ).reset_index(drop=True)

    terminal.sucesso('Classificação concluída! :)')

    return classificados