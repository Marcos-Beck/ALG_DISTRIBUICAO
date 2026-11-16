import pandas as pd

def preparar_instituicoes(
    dados,
    categorias,
    coluna_beneficiario='Beneficiario'
):
    """
    Converte o DataFrame de instituições para a estrutura
    utilizada pelas funções de distribuição.
    """

    # Validar coluna de identificação
    if coluna_beneficiario not in dados.columns:
        raise ValueError(
            f'Coluna não encontrada: {coluna_beneficiario}'
        )

    instituicoes = []

    for _, linha in dados.iterrows():

        instituicao = {
            'nome': linha[coluna_beneficiario],
            'solicitado': {}
        }

        for faixa, generos in categorias.items(): # percorre todas as faixas e generos

            instituicao['solicitado'][faixa] = {}

            for genero in ['feminino', 'masculino']:

                coluna = generos[genero]['demanda'] # pega a coluna de demanda correspondente

                if coluna not in dados.columns:
                    raise ValueError(
                        f'Coluna de solicitação não encontrada: {coluna}'
                    )

                valor = pd.to_numeric(  # garantir que o valor seja numm
                    linha[coluna],
                    errors='raise'
                )

                instituicao['solicitado'][faixa][genero] = (
                    int(valor) if pd.notna(valor) else 0
                )

        instituicoes.append(instituicao)

    return instituicoes


def preparar_grupos_distribuicao(
    grupos_geograficos,
    categorias,
    coluna_ordem='Ordem Inscrição',
    coluna_cnpj_valido='CNPJ Válido'
):
    """
    Reúne instituições de todas as regiões por prioridade,
    preservando região, localidade e ordem de classificação.
    """

    grupos = {}
    sequencia = 0

    for regiao, localidades in grupos_geograficos.items():

        for localidade, prioridades in localidades.items():

            for prioridade, dados in prioridades.items():

                preparados = preparar_instituicoes(
                    dados=dados,
                    categorias=categorias
                )

                for (_, linha), instituicao in zip(
                    dados.iterrows(),
                    preparados
                ):

                    instituicao['regiao'] = regiao
                    instituicao['localidade'] = localidade
                    instituicao['prioridade'] = prioridade

                    # ´preserva criterios de classificacao
                    ordem = linha.get(coluna_ordem, None)
                    cnpj_valido = linha.get(
                        coluna_cnpj_valido,
                        False
                    )

                    instituicao['ordem_inscricao'] = ordem

                    instituicao['cnpj_valido'] = (
                        bool(cnpj_valido)
                        if pd.notna(cnpj_valido)
                        else False
                    ) # garante que seja bool mesmo se vier como string

                    instituicao['_sequencia'] = sequencia
                    sequencia += 1

                    grupos.setdefault(prioridade, [])
                    grupos[prioridade].append(instituicao)

    # reorganizar prioridade respeitando a classificacao original
    for prioridade, instituicoes in grupos.items():

        instituicoes.sort(
            key=lambda item: (
                (
                    float('inf')
                    if pd.isna(item['ordem_inscricao'])
                    else item['ordem_inscricao']
                ),
                not item['cnpj_valido'],
                item['_sequencia']
            ) # ordem de classificacao: ordem_inscricao, cnpj_valido, sequencia
        )

        for instituicao in instituicoes:
            instituicao.pop('_sequencia')

    return grupos


def calcular_demanda_regional(
    grupos_distribuicao,
    categorias
):
    """
    Calcula a demanda por prioridade, região, localidade
    e faixa etária, separando feminino e masculino.

    Não altera instituições nem estoques.
    """

    demanda = {}

    for prioridade, instituicoes in grupos_distribuicao.items():

        demanda[prioridade] = {}

        for instituicao in instituicoes:

            regiao = instituicao['regiao']
            localidade = instituicao['localidade']

            demanda[prioridade].setdefault(regiao, {})
            demanda[prioridade][regiao].setdefault(
                localidade,
                {}
            )

            for faixa in categorias:

                grupo = demanda[prioridade][regiao][localidade]

                grupo.setdefault(
                    faixa,
                    {
                        'feminino': 0,
                        'masculino': 0
                    }
                )

                solicitado = instituicao['solicitado'][faixa]

                grupo[faixa]['feminino'] += solicitado['feminino']
                grupo[faixa]['masculino'] += solicitado['masculino']

    return demanda


def estruturar_estoque(
        arrecadacao,
        categorias,
        coluna_regiao='Região',
        coluna_localidade='Localidade',
):
    """
    Estrutura os estoques por região, localidade, faixa etária e gênero.

    Retorna:
        {
            'Região': {
                'interior': {
                    '0-3': {
                        'feminino': 100,
                        'masculino': 80,
                        'unissex': 50
                    }
                }
            }
        }
    """

    # 1 validar colunas geograficas
    colunas_geograficas = [coluna_regiao, coluna_localidade]

    for coluna in colunas_geograficas:
        if coluna not in arrecadacao.columns:
            raise ValueError(
                f'Coluna obrigatória "{coluna}" não encontrada.'
                )

        if arrecadacao[coluna].isna().any():
            raise ValueError(
                f'Coluna obrigatória "{coluna}" contém valores nulos.'
                )

    # 2 identificar colunas estoque
    colunas_estoque = []

    for faixa, generos in categorias.items():
        for genero in ['feminino', 'masculino']:
            coluna = generos[genero]['estoque']
            colunas_estoque.append(coluna)

        coluna_uni = generos['unissex']
        colunas_estoque.append(coluna_uni)

    # remover duplicacoes
    colunas_estoque = list(dict.fromkeys(colunas_estoque))

    # 3 validar colunas estoque
    for coluna in colunas_estoque:
        if coluna not in arrecadacao.columns:
            raise ValueError(
                f'Coluna de estoque não encontrada: {coluna}'
            )

    # 4 criar copia p/ nao modificar a base og
    dados = arrecadacao.copy()

    # garantir num
    for coluna in colunas_estoque:
        try:
            dados[coluna] = pd.to_numeric(
                dados[coluna],
                errors='raise'
            ).fillna(0)
        except (ValueError, TypeError):
            raise ValueError(
                f'Valores inválidos encontrados na coluna: {coluna}'
            )

    # 5 agrupar por região e localidade
    agrupados = dados.groupby(
        [coluna_regiao, coluna_localidade],
        sort=False
    )[colunas_estoque].sum()

    # 6 montar estrutura final
    estoques = {}

    for (regiao, localidade), valores in agrupados.iterrows():

        estoques.setdefault(regiao, {})
        estoques[regiao].setdefault(localidade, {})

        for faixa, generos in categorias.items():

            estoques[regiao][localidade][faixa] = {
                'feminino': int(
                    valores[generos['feminino']['estoque']]
                ),
                'masculino': int(
                    valores[generos['masculino']['estoque']]
                ),
                'unissex': int(
                    valores[generos['unissex']]
                )
            }

    return estoques


def distribuir_igualitario(instituicoes, estoque):
    """
    Distribui o estoque de forma igualitária progressiva.

    Todas as instituições recebem uma parcela antes
    de qualquer instituição receber complementação.

    Instituicoes: lista de dicionarios contendo:
        nome: identificação da instituição
        solicitado: quantidade solicitada

    estoque: quantidade disponível para distribuição.
    """

    resultado = []

    for instituicao in instituicoes:
        resultado.append({
            'nome': instituicao['nome'],
            'solicitado': instituicao['solicitado'],
            'atendido': 0
        })

    estoque_restante = estoque

    # enquanto houver estoque e solicitacao pendente
    while estoque_restante > 0:

        # filtrar instituicoes com solicitacao pendente
        pendentes = [
            inst for inst in resultado
            if inst['atendido'] < inst['solicitado']
        ]

        if not pendentes:
            break  # todas as solicitacoes atendidas

        # calcular parcela igualitaria para instituicoes pendentes
        parcela = estoque_restante // len(pendentes)

        # se não houver unidades suficientes para todos distribui uma unidade por vez seguindo a ordem recebida.
        if parcela == 0:
            parcela = 1

        for inst in pendentes:

            necessario = inst['solicitado'] - inst['atendido']
            atender = min(parcela, necessario, estoque_restante)

            inst['atendido'] += atender
            estoque_restante -= atender

            if estoque_restante <= 0:
                break

    return resultado, estoque_restante

# #! BLOCO DE TESTE RAPIDO
# instituicoes = [
#     {'nome': 'Instituição A', 'solicitado': 56},
#     {'nome': 'Instituição B', 'solicitado': 81}
# ]

# resultado, sobra = distribuir_igualitario(
#     instituicoes,
#     estoque=100
# )

# print(resultado)
# print('Estoque restante:', sobra)


def distribuir_unissex (solicitado_fem, solicitado_masc, estoque):
    """
    Distribui o estoque unissex PROPORCIONALMENTE entre as demandas feminina e masculina.
    """
    total_solicitado = solicitado_fem + solicitado_masc

    if estoque <= 0 or total_solicitado <= 0:
        return 0, 0, estoque  # nada a distribuir

    estoque_utilizado = min(estoque, total_solicitado)

    # calcular proporcao de cada demanda
    fem = (
        estoque_utilizado * solicitado_fem 
    ) // total_solicitado

    masc = (
        estoque_utilizado * solicitado_masc 
    ) // total_solicitado

    # distribuir o restante (se houver) para evitar perda de estoque
    restante = estoque_utilizado - fem - masc

    if restante > 0:
        if solicitado_fem - fem >= solicitado_masc - masc:
            fem += 1
        else:
            masc += 1

    estoque_restante = estoque - estoque_utilizado

    return fem, masc, estoque_restante


def distribuir_unissex_insti(instituicoes, unissex_fem, unissex_masc):
    """
    Distribui as parcelas unissex entre as instituições,
    respeitando a demanda restante de cada gênero.
    """

    resultado = []

    for indice, item in enumerate(instituicoes):
        resultado.append({
            'indice': indice,
            'nome': item['nome'],
            'unissex_fem': 0,
            'unissex_masc': 0
        })

    # Distribuir parcela feminina
    distribuicao_fem, _ = distribuir_igualitario(
        [
            {'nome': indice, 'solicitado': item['demanda_fem']}
            for indice, item in enumerate(instituicoes)
        ],
        unissex_fem
    )

    for indice, item in enumerate(distribuicao_fem):
        resultado[item['nome']]['unissex_fem'] = item['atendido']

    # Distribuir parcela masculina
    distribuicao_masc, _ = distribuir_igualitario(
        [
            {'nome': indice, 'solicitado': item['demanda_masc']}
            for indice, item in enumerate(instituicoes)
        ],
        unissex_masc
    )

    for indice, item in enumerate(distribuicao_masc):
        resultado[item['nome']]['unissex_masc'] = item['atendido']

    return resultado


# #! BLOCO DE TESTE RAPIDO
# fem, masc, restante = distribuir_unissex(
#     solicitado_fem=50,
#     solicitado_masc=50,
#     estoque=100)

# print(f"Feminino: {fem}, Masculino: {masc}, Restante: {restante}")



def distribuir_faixa_etaria(
    instituicoes,
    estoque_fem,
    estoque_masc,
    estoque_uni
):
    """
    Distribui os estoques feminino, masculino e unissex
    para uma faixa etária.
    """

    resultado = []

    # Preparar registros
    for instituicao in instituicoes:
        resultado.append({
            'nome': instituicao['nome'],
            'solicitacao_fem': instituicao['solicitacao_fem'],
            'solicitacao_masc': instituicao['solicitacao_masc'],
            'especifico_fem': 0,
            'especifico_masc': 0,
            'unissex_fem': 0,
            'unissex_masc': 0
        })

    # Distribuir estoque feminino específico
    distribuicao_fem, estoque_fem_restante = distribuir_igualitario(
        [
            {
                'nome': indice,
                'solicitado': item['solicitacao_fem']
            }
            for indice, item in enumerate(resultado)
        ],
        estoque_fem
    )

    for item in distribuicao_fem:
        resultado[item['nome']]['especifico_fem'] = item['atendido']

    # Distribuir estoque masculino específico
    distribuicao_masc, estoque_masc_restante = distribuir_igualitario(
        [
            {
                'nome': indice,
                'solicitado': item['solicitacao_masc']
            }
            for indice, item in enumerate(resultado)
        ],
        estoque_masc
    )

    for item in distribuicao_masc:
        resultado[item['nome']]['especifico_masc'] = item['atendido']

    # Calcular demandas restantes por instituição
    solicitacoes_restantes = [
        {
            'nome': item['nome'],
            'demanda_fem': max(
                0, item['solicitacao_fem'] - item['especifico_fem']
            ),
            'demanda_masc': max(
                0, item['solicitacao_masc'] - item['especifico_masc']
            )
        }
        for item in resultado
    ]

    # Calcular demanda restante total
    falta_fem = sum(
        item['demanda_fem'] for item in solicitacoes_restantes
    )

    falta_masc = sum(
        item['demanda_masc'] for item in solicitacoes_restantes
    )

    # Dividir estoque unissex proporcionalmente
    unissex_fem, unissex_masc, estoque_uni_restante = (
        distribuir_unissex(
            falta_fem,
            falta_masc,
            estoque_uni
        )
    )

    # Distribuir as parcelas unissex entre as instituições
    distribuicao_uni = distribuir_unissex_insti(
        solicitacoes_restantes,
        unissex_fem,
        unissex_masc
    )

    # Registrar quantidades recebidas
    for item in distribuicao_uni:
        resultado[item['indice']]['unissex_fem'] = item['unissex_fem']
        resultado[item['indice']]['unissex_masc'] = item['unissex_masc']

    # Calcular totais
    for item in resultado:
        item['total_fem'] = (
            item['especifico_fem'] + item['unissex_fem']
        )

        item['total_masc'] = (
            item['especifico_masc'] + item['unissex_masc']
        )

        item['total_distribuido'] = (
            item['total_fem'] + item['total_masc']
        )

        item['falta_fem'] = (
            item['solicitacao_fem'] - item['total_fem']
        )

        item['falta_masc'] = (
            item['solicitacao_masc'] - item['total_masc']
        )

    return {
        'instituicoes': resultado,
        'estoque_restante': {
            'feminino': estoque_fem_restante,
            'masculino': estoque_masc_restante,
            'unissex': estoque_uni_restante
        }
    }


# #! BLOCO DE TESTE RAPIDO
# instituicoes = [
#     {
#         'nome': 'Instituição A',
#         'solicitacao_fem': 50,
#         'solicitacao_masc': 30
#     },
#     {
#         'nome': 'Instituição B',
#         'solicitacao_fem': 20,
#         'solicitacao_masc': 40
#     }
# ]

# resultado = distribuir_faixa_etaria(
#     instituicoes,
#     estoque_fem=60,
#     estoque_masc=50,
#     estoque_uni=30
# )

# for item in resultado['instituicoes']:
#     print(item)

# print('Estoques restantes:', resultado['estoque_restante'])

def distribuir_todas_faixas(instituicoes, estoques):
    """
    Distribui os estoques para todas as faixas etárias.
    Executa distribuir_faixa_etaria() individualmente para cada faixa e reune os resultados.
    """
    resultado = []

    # prepara o resultado de cada instituicao
    for instituicao in instituicoes:
        resultado.append({
            'nome': instituicao['nome'],
            'faixas': {}
        })
    estoque_restante = {}

    # percorre todas as faixas 
    for faixa, estoque in estoques.items():

        # prepara as solicitacoes da faixa atual 
        solicitacoes = [
            {
                'nome': indice,
                'solicitacao_fem': instituicao['solicitado'][faixa]['feminino'],
                'solicitacao_masc': instituicao['solicitado'][faixa]['masculino']
            }
            for indice, instituicao in enumerate(instituicoes)
        ]

        # executa a distribuicao 
        distribuicao = distribuir_faixa_etaria(
            solicitacoes,
            estoque_fem=estoque['feminino'],
            estoque_masc=estoque['masculino'],
            estoque_uni=estoque['unissex']
        )

        # guarda o resultado de cada instituicao
        for item in distribuicao['instituicoes']:
            indice = item['nome']

            dados_faixa = item.copy()
            dados_faixa.pop('nome')

            resultado[indice]['faixas'][faixa] = dados_faixa

        # guarda o estoque restante da faixa
        estoque_restante[faixa] = distribuicao['estoque_restante']

    # calcula os totais de todas as faixas 
    for instituicao in resultado:

        faixas = instituicao['faixas']

        instituicao['total_solicitado_fem'] = sum(
            faixa['solicitacao_fem'] 
            for faixa in faixas.values()
        )

        instituicao['total_solicitado_masc'] = sum(
            faixa['solicitacao_masc']
            for faixa in faixas.values()
        )

        instituicao['total_fem'] = sum(
            faixa['total_fem']
            for faixa in faixas.values()
        )

        instituicao['total_masc'] = sum(
            faixa['total_masc']
            for faixa in faixas.values()
        )

        instituicao['total_distribuido'] = (
            instituicao['total_fem'] +
            instituicao['total_masc']
        )

        instituicao['falta_total'] = sum(
            item['falta_fem'] + item['falta_masc']
            for item in faixas.values()
        )

    return {
        'instituicoes': resultado,
        'estoque_restante': estoque_restante
    }

