from pathlib import Path

from modules import terminal

#* = resumo de funcao ou grupo de funcoes
### = opcional

#* exportar resultados em excel e csv
def exportar_resultados(dados, nome, ano, nome_arquivo='distribuicao'):
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