import pandas as pd
from . import terminal

def classificar_instituicoes(
        dados,
        colunas_solicitacao,
        prioridades,
        coluna_beneficiario,
        coluna_cnpj,
        extrair_ordem,
        validar_cnpj,
):
    dados = dados.copy()

    # 1 verificar se todas as colunas existem 
    terminal.info('Validando colunas obrigatórias...')
    colunas_obg = (
        colunas_solicitacao 
        + [coluna_beneficiario, coluna_cnpj]
    )

    faltantes = [
        coluna for coluna in colunas_obg 
        if coluna not in dados.columns
    ]

    if faltantes:
        mensagem = f'ERRO: Colunas obrigatórias ausentes: {faltantes}'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 2 calcular solicitacao total por instituicao
    terminal.info('Calculando solicitacao total por instituicao...')
    solicitacao = dados[colunas_solicitacao].apply(
        pd.to_numeric,
        errors='coerce'
    )

    invalidos = (
        dados[colunas_solicitacao].notna()
        & solicitacao.isna()
    )

    if invalidos.any().any():
        mensagem = (
            f'ERRO: Valores inválidos encontrados nas colunas de solicitação: '
            f'{dados.loc[invalidos.any(axis=1), coluna_beneficiario].tolist()}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    dados['Solicitação Total'] = solicitacao.fillna(0).sum(axis=1)

    # 3 identificar prioridade qtde 
    def identificar_prioridade(total):
        for prioridade, limites in sorted(prioridades.items()):
            min_val = limites['min']
            max_val = limites['max']

            if (min_val is None or total >= min_val) and (max_val is None or total <= max_val):
                return prioridade

        return None

    dados['Prioridade'] = dados['Solicitação Total'].apply(
        identificar_prioridade
        )

    # 4 extrair ordem de inscricao
    terminal.info('Extraindo ordem de inscrição...')
    dados['Ordem Inscrição'] = dados[
        coluna_beneficiario
        ].apply(extrair_ordem)

    # 5 validar cnpj
    terminal.info('Validando CNPJs...')
    dados['CNPJ Válido'] = dados[
        coluna_cnpj
        ].apply(validar_cnpj)

    # 6 classificar instituicoes
    terminal.info('Classificando instituições...')
    dados = dados.sort_values(
        by=[
            'Prioridade',
            'Ordem Inscrição',
            'CNPJ Válido'
        ],
        ascending=[True, True, False],
        na_position='last',
        kind='mergesort'
    )
    
    return dados.reset_index(drop=True)
    


