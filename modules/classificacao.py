import pandas as pd
import unicodedata
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


def classificar_geografia(
    dados,
    coluna_cidade,
    regioes,
    coluna_municipio,
    coluna_regiao,
    capital
):
    """
    Identifica a região e a localidade de cada instituição.

    Localidade:
        capital: município definido como capital.
        interior: demais municípios cadastrados.
    """

    dados = dados.copy()
    regioes = regioes.copy()

    terminal.etapa('Classificando localização das instituições...')

    # 1. Verificar colunas necessárias
    colunas_dados = [coluna_cidade]
    colunas_regioes = [coluna_municipio, coluna_regiao]

    faltantes_dados = [
        coluna for coluna in colunas_dados
        if coluna not in dados.columns
    ]

    faltantes_regioes = [
        coluna for coluna in colunas_regioes
        if coluna not in regioes.columns
    ]

    if faltantes_dados or faltantes_regioes:
        mensagem = (
            f'ERRO: Colunas ausentes. '
            f'Dados: {faltantes_dados}. '
            f'Regiões: {faltantes_regioes}.'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 2. Normalizar nomes dos municípios
    def normalizar_nome(valor):
        if pd.isna(valor):
            return ''

        valor = unicodedata.normalize('NFKD', str(valor))
        valor = ''.join(
            caractere for caractere in valor
            if not unicodedata.combining(caractere)
        )

        return valor.strip().casefold()

    dados['_Municipio'] = dados[coluna_cidade].apply(
        normalizar_nome
    )

    regioes['_Municipio'] = regioes[coluna_municipio].apply(
        normalizar_nome
    )

    # 3. Verificar municípios sem região
    if (
        regioes['_Municipio'].eq('').any()
        or regioes[coluna_regiao].isna().any()
    ):
        mensagem = 'ERRO: O cadastro regional possui municípios ou regiões vazios.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 4. Verificar se algum município pertence a mais de uma região
    conflitos = (
        regioes.groupby('_Municipio')[coluna_regiao]
        .nunique()
    )

    conflitos = conflitos[conflitos > 1]

    if not conflitos.empty:
        mensagem = (
            'ERRO: Municípios cadastrados em mais de uma região: '
            f'{conflitos.index.tolist()}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 5. Criar mapeamento município -> região
    mapa_regioes = (
        regioes.drop_duplicates(subset='_Municipio')
        .set_index('_Municipio')[coluna_regiao]
        .to_dict()
    )

    # 6. Identificar municípios não cadastrados
    municipios_nao_encontrados = dados.loc[
        ~dados['_Municipio'].isin(mapa_regioes),
        coluna_cidade
    ].drop_duplicates().tolist()

    if municipios_nao_encontrados:
        mensagem = (
            'ERRO: Municípios não encontrados no cadastro regional: '
            f'{municipios_nao_encontrados}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 7. Adicionar região
    dados['Região'] = dados['_Municipio'].map(mapa_regioes)

    # 8. Identificar capital e interior
    capital_normalizada = normalizar_nome(capital)

    dados['Localidade'] = dados['_Municipio'].apply(
        lambda cidade: (
            'capital'
            if cidade == capital_normalizada
            else 'interior'
        )
    )

    # 9. Remover coluna auxiliar
    dados = dados.drop(columns=['_Municipio'])

    terminal.sucesso('Classificação geográfica concluída. :D')

    return dados



def organizar_por_regiao(
    dados,
    coluna_regiao='Região',
    coluna_localidade='Localidade'
):
    """
    Organiza as instituições por região.

    Regiões do interior são processadas primeiro.
    A região que contém a capital é processada por último.

    Dentro de cada região, instituições do interior
    aparecem antes das instituições da capital.
    """

    dados = dados.copy()

    terminal.etapa('Organizando instituições por região...')

    # 1. Verificar colunas necessárias
    colunas_obrigatorias = [
        coluna_regiao,
        coluna_localidade
    ]

    faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in dados.columns
    ]

    if faltantes:
        mensagem = f'ERRO: Colunas ausentes: {faltantes}'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 2. Verificar localidades válidas
    localidades_validas = ['interior', 'capital']

    invalidas = dados.loc[
        ~dados[coluna_localidade].isin(localidades_validas),
        coluna_localidade
    ].drop_duplicates().tolist()

    if invalidas:
        mensagem = f'ERRO: Localidades inválidas: {invalidas}'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 3. Identificar a região onde está a capital
    regioes_capital = dados.loc[
        dados[coluna_localidade] == 'capital',
        coluna_regiao
    ].drop_duplicates().tolist()

    if len(regioes_capital) > 1:
        mensagem = (
            'ERRO: Foram encontradas instituições da capital '
            f'em mais de uma região: {regioes_capital}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 4. Organizar regiões do interior primeiro
    grupos = {}

    regioes = dados[coluna_regiao].drop_duplicates().tolist()

    regioes_interior = [
        regiao for regiao in regioes
        if regiao not in regioes_capital
    ]

    # Adicionar a região da capital por último
    regioes_ordenadas = regioes_interior + regioes_capital

    for regiao in regioes_ordenadas:

        instituicoes = dados[
            dados[coluna_regiao] == regiao
        ]

        interior = instituicoes[
            instituicoes[coluna_localidade] == 'interior'
        ]

        capital = instituicoes[
            instituicoes[coluna_localidade] == 'capital'
        ]

        grupos[regiao] = pd.concat(
            [interior, capital]
        ).reset_index(drop=True)

    terminal.sucesso('Instituições organizadas por região.')

    return grupos

def separar_prioridade(
        dados, 
        prioridades,
        coluna_prioridade='Prioridade'
):
    """
    Separa as instituições em grupos de acordo com a prioridade.
    Retorna um dicionário contendo um DataFrame para cada prioridade.
    """

    dados = dados.copy()

    terminal.etapa('Separando instituições por prioridade...')

    # 1 verificar coluna necessária 
    if coluna_prioridade not in dados.columns:
        mensagem = (
            f'ERRO: Coluna de prioridade ausente:' 
            f' {coluna_prioridade}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 2 verificar prioridades invalidas ou ausentes 
    prioridades_validas = list(prioridades.keys())

    invalidas = dados.loc[
        ~dados[coluna_prioridade].isin(prioridades_validas),
        coluna_prioridade
    ].unique().tolist()

    if invalidas:
        mensagem = (
            f'ERRO: Prioridades inválidas ou ausentes:'
            f'{invalidas}.'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # 3 grupos na ordem das prioridades 
    grupos = {}

    for prioridade in sorted(prioridades_validas):

        instituicoes = dados[
            dados[coluna_prioridade] == prioridade
        ].copy()

        grupos[prioridade] = instituicoes.reset_index(drop=True)

        terminal.info(
            f'Prioridade {prioridade}:'
            f' {len(instituicoes)} instituições.'
        )

    terminal.sucesso('Instituições separadas por prioridade!')

    return grupos