def distribuir_igualitario(instituicoes, estoque):
    """
    Distribui o estoque de forma igualitária progressiva.
    Instituicoes: lista de dicionarios contendo:
        nome: identificação da instituição
        solicitado: quantidade solicitada
        
    estoque: quantidade disponivel para distribuicao.
    """

    resultado = []

    # criar copia das inst com saldos 
    for indice, instituicao in enumerate(instituicoes):
        resultado.append({
            'indice': indice,
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

        # calcular quantidade a distribuir por instituicao
        distribuicao = estoque_restante // len(pendentes)

        if distribuicao == 0:
            distribuicao = 1  # garantir que pelo menos 1 seja distribuido

        for inst in pendentes:
            necessario = inst['solicitado'] - inst['atendido']
            atender = min(distribuicao, necessario)

            inst['atendido'] += atender
            estoque_restante -= atender

            if estoque_restante <= 0:
                break

        # distribuir sem ultrapassar a solicitacao
        for inst in pendentes:
            necessario = inst['solicitado'] - inst['atendido']
            if necessario > 0 and estoque_restante > 0:
                atender = min(necessario, estoque_restante)
                inst['atendido'] += atender
                estoque_restante -= atender

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


#! BLOCO DE TESTE RAPIDO
instituicoes = [
    {
        'nome': 'Instituição A',
        'solicitacao_fem': 50,
        'solicitacao_masc': 30
    },
    {
        'nome': 'Instituição B',
        'solicitacao_fem': 20,
        'solicitacao_masc': 40
    }
]

resultado = distribuir_faixa_etaria(
    instituicoes,
    estoque_fem=60,
    estoque_masc=50,
    estoque_uni=30
)

for item in resultado['instituicoes']:
    print(item)

print('Estoques restantes:', resultado['estoque_restante'])
