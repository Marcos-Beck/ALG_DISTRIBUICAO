from pathlib import Path
import pandas as pd

from modules import terminal

#* = resumo de funcao ou grupo de funcoes
### = opcional

#* gerar tabelas de diagnostico para conferencia da distribuicao
def gerar_resumos_diagnostico(df_resultados, estoque_reserva, estoque_restante):
    """
    Gera DataFrames de diagnostico para conferencia de estoque,
    reserva obrigatoria, consumo por genero e atendimento por prioridade.
    """

    linhas_estoque = []
    for faixa, generos in estoque_reserva['bruto'].items():
        cons_f = int(df_resultados[f'Distribuido Fem {faixa}'].sum())
        cons_m = int(df_resultados[f'Distribuido Masc {faixa}'].sum())
        cons_u = int(
            df_resultados[f'Distribuido Unissex Fem {faixa}'].sum()
            + df_resultados[f'Distribuido Unissex Masc {faixa}'].sum()
        )
        consumos = {'feminino': cons_f, 'masculino': cons_m, 'unissex': cons_u}

        for genero in ['feminino', 'masculino', 'unissex']:
            bruto = int(generos[genero])
            reservado = int(estoque_reserva['reservado'][faixa][genero])
            disponivel = int(estoque_reserva['distribuivel'][faixa][genero])
            consumido = consumos[genero]
            restante = int(estoque_restante[faixa][genero])

            linhas_estoque.append({
                'Faixa': faixa,
                'Categoria': genero,
                'Arrecadado Bruto': bruto,
                'Reservado (15%)': reservado,
                'Disponivel Distribuicao (85%)': disponivel,
                'Consumido': consumido,
                'Restante Distribuivel': restante
            })

    df_estoque = pd.DataFrame(linhas_estoque)

    linhas_prioridade = []
    for prioridade, grupo in df_resultados.groupby('Prioridade', sort=True):
        solicitado = int(grupo['Solicitado Total'].sum())
        atendido = int(grupo['Atendido Total'].sum())
        falta = int(grupo['Falta Total'].sum())
        pct = round((atendido / solicitado) * 100, 2) if solicitado > 0 else 0.0

        linhas_prioridade.append({
            'Prioridade': prioridade,
            'Instituicoes': int(len(grupo)),
            'Solicitado Total': solicitado,
            'Atendido Total': atendido,
            'Falta Total': falta,
            'Percentual Atendimento (%)': pct
        })

    df_prioridades = pd.DataFrame(linhas_prioridade)

    tot_bruto = int(df_estoque['Arrecadado Bruto'].sum())
    tot_reservado = int(df_estoque['Reservado (15%)'].sum())
    tot_disponivel = int(df_estoque['Disponivel Distribuicao (85%)'].sum())
    tot_distribuido = int(df_resultados['Atendido Total'].sum())
    tot_restante = int(df_estoque['Restante Distribuivel'].sum())

    linhas_geral = [
        {'Indicador': 'Total Arrecadado (Bruto)', 'Valor': tot_bruto},
        {'Indicador': 'Total Reservado (15% - Intacto)', 'Valor': tot_reservado},
        {'Indicador': 'Total Disponivel para Distribuicao (85%)', 'Valor': tot_disponivel},
        {'Indicador': 'Total Distribuido', 'Valor': tot_distribuido},
        {'Indicador': 'Estoque Restante Distribuivel (Nao inclui reserva)', 'Valor': tot_restante},
    ]

    for _, row in df_prioridades.iterrows():
        prio = int(row['Prioridade'])
        linhas_geral.append({
            'Indicador': f'Demanda Total P{prio}',
            'Valor': int(row['Solicitado Total'])
        })
        linhas_geral.append({
            'Indicador': f'Quantidade Atendida P{prio}',
            'Valor': int(row['Atendido Total'])
        })

    df_geral = pd.DataFrame(linhas_geral)

    return {
        'Resumo_Geral': df_geral,
        'Resumo_Estoque': df_estoque,
        'Resumo_Prioridades': df_prioridades
    }


#* exportar resultados em excel e csv
def exportar_resultados(dados, nome, ano, nome_arquivo='distribuicao', resumos=None):
    """
    Exporta os resultados em Excel e CSV.

    Cria automaticamente uma pasta identificada pela campanha e ano.
    """

    ### terminal.etapa(f'[ RELATORIO ] Exportando resultados para Excel e CSV...')

    # diretorio principal do projeto
    raiz = Path(__file__).resolve().parents[1]

    # cria a pasta de resultados
    pasta_resultados = raiz / 'output' / f'{nome} {ano}'
    pasta_resultados.mkdir(parents=True, exist_ok=True)

    # caminho dos arquivos 
    caminho_excel = pasta_resultados / f'{nome_arquivo}.xlsx'
    caminho_csv = pasta_resultados / f'{nome_arquivo}.csv'

    # exportacao
    if resumos:
        with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
            dados.to_excel(writer, sheet_name='Distribuicao', index=False)
            for nome_aba, df_aba in resumos.items():
                df_aba.to_excel(writer, sheet_name=nome_aba[:31], index=False)
    else:
        dados.to_excel(
            caminho_excel,
            index=False
        )

    dados.to_csv(
        caminho_csv,
        index=False,
        sep=';',
        encoding='utf-8-sig'
        )

    return{
        'excel': caminho_excel,
        'csv': caminho_csv
    }