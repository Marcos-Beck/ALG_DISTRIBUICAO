import pandas as pd
import unicodedata
from . import terminal

#* = resumo de funcao ou grupo de funcoes
### = opcional

#* classificar as instituicoes de acordo com a solicitacao, ordem de inscricao e validade do CNPJ
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

    # verificar se todas as colunas existem 
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Validando colunas obrigatórias...')
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

    # calcular solicitacao total por instituicao
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Calculando solicitacao total por instituicao...')
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

    # identificar prioridade qtde 
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

    # extrair ordem de inscricao
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Extraindo ordem de inscrição...')
    dados['Ordem Inscrição'] = dados[
        coluna_beneficiario
        ].apply(extrair_ordem)

    # validar cnpj
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Validando CNPJs...')
    dados['CNPJ Válido'] = dados[
        coluna_cnpj
        ].apply(validar_cnpj)

    # classificar instituicoes
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Classificando instituições...')
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


#* classificar instituicoes de acordo com a regiao e localidade
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

    ### terminal.etapa('[ CLASSIFICAÇÃO ] Classificando localização das instituições...')

    # verificar colunas necessarias
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

    # normalizar nomes dos municipios
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

    # verificar municipios sem regiao
    if (
        regioes['_Municipio'].eq('').any()
        or regioes[coluna_regiao].isna().any()
    ):
        mensagem = 'ERRO: O cadastro regional possui municípios ou regiões vazios.'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # verificar se algum municipio pertence a mais de uma regiao
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

    # criar mapeamento municipio -> regiao
    mapa_regioes = (
        regioes.drop_duplicates(subset='_Municipio')
        .set_index('_Municipio')[coluna_regiao]
        .to_dict()
    )

    # identificar municipios nao cadastrados
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

    # adicionar regiao
    dados['Região'] = dados['_Municipio'].map(mapa_regioes)

    # identificar capital e interior
    capital_normalizada = normalizar_nome(capital)

    dados['Localidade'] = dados['_Municipio'].apply(
        lambda cidade: (
            'capital'
            if cidade == capital_normalizada
            else 'interior'
        )
    )

    # remover coluna auxiliar
    dados = dados.drop(columns=['_Municipio'])

    ### terminal.sucesso('[ CLASSIFICAÇÃO ] Classificação geográfica concluída. :D')

    return dados


#* organizar grupos geograficos
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

    ### terminal.etapa('[ CLASSIFICAÇÃO ] Organizando instituições por região...')

    # verificar colunas necessarias
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

    # verificar localidades validas
    localidades_validas = ['interior', 'capital']

    invalidas = dados.loc[
        ~dados[coluna_localidade].isin(localidades_validas),
        coluna_localidade
    ].drop_duplicates().tolist()

    if invalidas:
        mensagem = f'ERRO: Localidades inválidas: {invalidas}'
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # identificar a regiao onde esta a capital
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

    # organizar regioes do interior primeiro
    grupos = {}

    regioes = dados[coluna_regiao].drop_duplicates().tolist()

    regioes_interior = [
        regiao for regiao in regioes
        if regiao not in regioes_capital
    ]

    # adicionar a regiao da capital por ultimo
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

    ### terminal.sucesso('[ CLASSIFICAÇÃO ] Instituições organizadas por região.')

    return grupos


#* separar instituicoes por grupos de prioridade
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

    ### terminal.etapa('[ CLASSIFICAÇÃO ] Separando instituições por prioridade...')

    # verificar coluna necessaria 
    if coluna_prioridade not in dados.columns:
        mensagem = (
            f'ERRO: Coluna de prioridade ausente:' 
            f' {coluna_prioridade}'
        )
        terminal.erro(mensagem)
        raise ValueError(mensagem)

    # verificar prioridades invalidas ou ausentes 
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

    # grupos na ordem das prioridades 
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

    ### terminal.sucesso('[ CLASSIFICAÇÃO ] Instituições separadas por prioridade!')

    return grupos


#* separar instituicoes por prioridade e geografia
def preparar_grupos_geograficos(
    dados,
    prioridades,
    coluna_prioridade='Prioridade',
    coluna_regiao='Região',
    coluna_localidade='Localidade'
):
    """
    Separa as instituições por prioridade, região e localidade.

    Retorna uma estrutura hierárquica:
    região -> localidade -> prioridade -> DataFrame.
    """
    
    ### terminal.etapa('[ CLASSIFICAÇÃO ] Preparando grupos geográficos...')

    grupos_geograficos = {}

    # separa as instituições por prioridade
    grupos_prioridade = separar_prioridade(
        dados,
        prioridades,
        coluna_prioridade=coluna_prioridade
    )

    # organiza cada prioridade geograficamente
    for prioridade, instituicoes in grupos_prioridade.items():

        grupos_regiao = organizar_por_regiao(instituicoes)

        for regiao, dados_regiao in grupos_regiao.items():

            if regiao not in grupos_geograficos:
                grupos_geograficos[regiao] = {}

            # Separa capital e interior
            for localidade, dados_localidade in dados_regiao.groupby(
                coluna_localidade,
                sort=False
            ):

                if localidade not in grupos_geograficos[regiao]:
                    grupos_geograficos[regiao][localidade] = {}

                grupos_geograficos[regiao][localidade][prioridade] = (
                    dados_localidade
                )

    return grupos_geograficos