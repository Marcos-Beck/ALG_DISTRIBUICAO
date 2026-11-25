import math
import pandas as pd
from . import terminal

#* = resumo de funcao ou grupo de funcoes
### = opcional

#* adequar o df de instituicoes para utilizar funcoes de distribuicao
def preparar_instituicoes(
    dados,
    categorias,
    coluna_beneficiario='Beneficiario'
):
    """
    Converte o DataFrame de instituições para a estrutura
    utilizada pelas funções de distribuição.
    """

    # validar coluna de identificacao
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

                valor = pd.to_numeric(
                    linha[coluna],
                    errors='raise'
                )

                instituicao['solicitado'][faixa][genero] = (
                    int(valor) if pd.notna(valor) else 0
                )

        instituicoes.append(instituicao)

    return instituicoes


#* consolidar a demanda preservando as informacoes geograficas e de ordem de inscricao
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

    ### terminal.etapa(f'[ DISTRIBUICAO ] Preparando grupos de distribuicao por prioridade...')

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

                    # preserva criterios de classificacao
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


#* calcular a demanda por prioridade, região, localidade e faixa etária
def calcular_demanda_regional(
    grupos_distribuicao,
    categorias
):
    """
    Calcula a demanda por prioridade, região, localidade
    e faixa etária, separando feminino e masculino.

    Não altera instituições nem estoques.
    """

    ### terminal.etapa('[ DISTRIBUICAO ] Calculando demanda regional por prioridade...')

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


#* estruturar o estoque geograficamente + faixa etaria e genero
def estruturar_estoque(
        arrecadacao,
        categorias,
        coluna_regiao='Região',
        coluna_localidade='Localidade',
):
    """
    Estrutura os estoques por região, localidade, faixa eteria e genero.

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
    ### terminal.etapa('[ DISTRIBUICAO ] Estruturando estoque geograficamente...')

    # validar colunas geograficas
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

    # identificar colunas estoque
    colunas_estoque = []

    for faixa, generos in categorias.items():
        for genero in ['feminino', 'masculino']:
            coluna = generos[genero]['estoque']
            colunas_estoque.append(coluna)

        coluna_uni = generos['unissex']
        colunas_estoque.append(coluna_uni)

    # remover duplicacoes
    colunas_estoque = list(dict.fromkeys(colunas_estoque))

    # validar colunas estoque
    for coluna in colunas_estoque:
        if coluna not in arrecadacao.columns:
            raise ValueError(
                f'Coluna de estoque não encontrada: {coluna}'
            )

    # criar copia p/ nao modificar a base og
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

    # agrupar por região e localidade
    agrupados = dados.groupby(
        [coluna_regiao, coluna_localidade],
        sort=False
    )[colunas_estoque].sum()

    # montar estrutura final
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


#* distribuir o estoque de forma igualitária
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


#* distribuir unissex proporcionalmente
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


def distribuir_unissex_insti(instituicoes, dist_unissex_fem, dist_unissex_masc):
    """
    Distribui as parcelas unissex entre as instituições,
    respeitando a demanda restante de cada gênero.
    """

    resultado = []

    for indice, item in enumerate(instituicoes):
        resultado.append({
            'indice': indice,
            'nome': item['nome'],
            'dist_unissex_fem': 0,
            'dist_unissex_masc': 0
        })

    # distribuir parcela feminina
    distribuicao_fem, _ = distribuir_igualitario(
        [
            {'nome': indice, 'solicitado': item['demanda_fem']}
            for indice, item in enumerate(instituicoes)
        ],
        dist_unissex_fem
    )

    for indice, item in enumerate(distribuicao_fem):
        resultado[item['nome']]['dist_unissex_fem'] = item['atendido']

    # distribuir parcela masculina
    distribuicao_masc, _ = distribuir_igualitario(
        [
            {'nome': indice, 'solicitado': item['demanda_masc']}
            for indice, item in enumerate(instituicoes)
        ],
        dist_unissex_masc
    )

    for indice, item in enumerate(distribuicao_masc):
        resultado[item['nome']]['dist_unissex_masc'] = item['atendido']

    return resultado


#* distribuir por faixa etária
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

    # preparar registros
    for instituicao in instituicoes:
        resultado.append({
            'nome': instituicao['nome'],
            'solicitacao_fem': instituicao['solicitacao_fem'],
            'solicitacao_masc': instituicao['solicitacao_masc'],
            'dist_especifico_fem': 0,
            'dist_especifico_masc': 0,
            'dist_unissex_fem': 0,
            'dist_unissex_masc': 0
        })

    # distribuir estoque feminino especifico distribuido
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
        resultado[item['nome']]['dist_especifico_fem'] = item['atendido']

    # distribuir estoque masculino especifico distribuido
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
        resultado[item['nome']]['dist_especifico_masc'] = item['atendido']

    # calcular demandas restantes por instituicao
    solicitacoes_restantes = [
        {
            'nome': item['nome'],
            'demanda_fem': max(
                0, item['solicitacao_fem'] - item['dist_especifico_fem']
            ),
            'demanda_masc': max(
                0, item['solicitacao_masc'] - item['dist_especifico_masc']
            )
        }
        for item in resultado
    ]

    # calcular demanda restante total
    falta_fem = sum(
        item['demanda_fem'] for item in solicitacoes_restantes
    )

    falta_masc = sum(
        item['demanda_masc'] for item in solicitacoes_restantes
    )

    # dividir estoque unissex proporcionalmente
    dist_unissex_fem, dist_unissex_masc, estoque_uni_restante = (
        distribuir_unissex(
            falta_fem,
            falta_masc,
            estoque_uni
        )
    )

    # distribuir as parcelas unissex entre as instituicoes
    distribuicao_uni = distribuir_unissex_insti(
        solicitacoes_restantes,
        dist_unissex_fem,
        dist_unissex_masc
    )

    # registrar quantidades recebidas
    for item in distribuicao_uni:
        resultado[item['indice']]['dist_unissex_fem'] = item['dist_unissex_fem']
        resultado[item['indice']]['dist_unissex_masc'] = item['dist_unissex_masc']

    # calcular totais
    for item in resultado:
        item['total_fem'] = (
            item['dist_especifico_fem'] + item['dist_unissex_fem']
        )

        item['total_masc'] = (
            item['dist_especifico_masc'] + item['dist_unissex_masc']
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



#* distribuir estoque para todas as faixas etarias
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


#* calcular peso da penalizacao gradual
def calcular_peso_penalizacao(solicitado, penalizacao=None):
    """
    Calcula o peso proporcional de uma instituicao conforme seu volume
    total solicitado e os parametros configuraveis de penalizacao.
    """

    if not penalizacao or not penalizacao.get('ativa', True):
        return 1.0

    inicio = penalizacao.get('inicio', 0)
    limite = penalizacao.get('limite', inicio)
    intensidade = penalizacao.get('intensidade', 0.0)

    if solicitado <= inicio:
        return 1.0

    if limite <= inicio or solicitado >= limite:
        return max(0.0, 1.0 - intensidade)

    fracao = (solicitado - inicio) / (limite - inicio)
    return max(0.0, 1.0 - intensidade * fracao)


#* alocar estoque de forma proporcional ponderada com redistribuicao de cotas
def alocar_proporcional_ponderado(demandas, estoque, pesos=None):
    """
    Distribui um estoque inteiro proporcionalmente as demandas restantes
    multiplicadas pelos pesos, redistribuindo excedentes quando alguma
    instituicao atinge o teto da sua solicitacao.
    """

    n = len(demandas)
    if n == 0 or estoque <= 0:
        return [0] * n, estoque

    if pesos is None:
        pesos = [1.0] * n

    alocado = [0] * n
    restante = int(estoque)

    while restante > 0:
        ativas = [
            i for i in range(n)
            if (demandas[i] - alocado[i]) > 0 and pesos[i] > 0
        ]

        if not ativas:
            break

        soma_ponderada = sum(
            (demandas[i] - alocado[i]) * pesos[i]
            for i in ativas
        )

        if soma_ponderada <= 0:
            break

        cotas = {
            i: restante * ((demandas[i] - alocado[i]) * pesos[i]) / soma_ponderada
            for i in ativas
        }

        # se alguma cota atingir ou superar a demanda restante, fixa no teto e redistribui o saldo
        saturadas = [
            i for i in ativas
            if cotas[i] >= (demandas[i] - alocado[i])
        ]

        if saturadas:
            for i in saturadas:
                ganho = demandas[i] - alocado[i]
                alocado[i] += ganho
                restante -= ganho
            continue

        pisos = {i: int(math.floor(cotas[i])) for i in ativas}
        for i in ativas:
            alocado[i] += pisos[i]
            restante -= pisos[i]

        if restante > 0:
            ordenados = sorted(
                ativas,
                key=lambda i: (-(cotas[i] - pisos[i]), i)
            )
            for i in ordenados[:restante]:
                alocado[i] += 1
                restante -= 1

    return alocado, restante


#* distribuir parcela unissex em uma faixa com metodo igualitario ou ponderado
def _distribuir_unissex_em_faixa(falta_fem, falta_masc, estoque_uni, pesos=None):
    """
    Divide o estoque unissex entre demandas feminina e masculina restantes
    e distribui entre as instituicoes sem consumo duplo.
    """

    n = len(falta_fem)
    if estoque_uni <= 0 or n == 0:
        return [0] * n, [0] * n, estoque_uni

    if pesos is None:
        tot_ff = sum(falta_fem)
        tot_fm = sum(falta_masc)
    else:
        tot_ff = sum(falta_fem[i] for i in range(n) if pesos[i] > 0)
        tot_fm = sum(falta_masc[i] for i in range(n) if pesos[i] > 0)

    if tot_ff + tot_fm <= 0:
        return [0] * n, [0] * n, estoque_uni

    parcela_fem, parcela_masc, estoque_uni_restante = distribuir_unissex(
        tot_ff,
        tot_fm,
        estoque_uni
    )

    if pesos is None:
        dist_f, _ = distribuir_igualitario(
            [{'nome': i, 'solicitado': falta_fem[i]} for i in range(n)],
            parcela_fem
        )
        dist_m, _ = distribuir_igualitario(
            [{'nome': i, 'solicitado': falta_masc[i]} for i in range(n)],
            parcela_masc
        )
        al_uf = [item['atendido'] for item in dist_f]
        al_um = [item['atendido'] for item in dist_m]
    else:
        al_uf, _ = alocar_proporcional_ponderado(falta_fem, parcela_fem, pesos)
        al_um, _ = alocar_proporcional_ponderado(falta_masc, parcela_masc, pesos)

    return al_uf, al_um, estoque_uni_restante


#* aplicar rodada igualitaria por faixa sobre demandas-alvo
def _aplicar_rodada_igualitaria_faixas(instituicoes, alvos, estoque_atual, atendido_inst):
    """
    Executa uma rodada igualitaria em todas as faixas sobre alvos definidos,
    atualizando estoque_atual e atendido_inst no local.
    """

    for faixa in estoque_atual:
        dem_f = [alvos[i][faixa]['feminino'] for i in range(len(instituicoes))]
        dem_m = [alvos[i][faixa]['masculino'] for i in range(len(instituicoes))]

        if sum(dem_f) + sum(dem_m) == 0:
            continue

        res_f, estoque_atual[faixa]['feminino'] = distribuir_igualitario(
            [{'nome': i, 'solicitado': dem_f[i]} for i in range(len(instituicoes))],
            estoque_atual[faixa]['feminino']
        )
        res_m, estoque_atual[faixa]['masculino'] = distribuir_igualitario(
            [{'nome': i, 'solicitado': dem_m[i]} for i in range(len(instituicoes))],
            estoque_atual[faixa]['masculino']
        )

        al_f = [item['atendido'] for item in res_f]
        al_m = [item['atendido'] for item in res_m]

        falta_f = [dem_f[i] - al_f[i] for i in range(len(instituicoes))]
        falta_m = [dem_m[i] - al_m[i] for i in range(len(instituicoes))]

        al_uf, al_um, estoque_atual[faixa]['unissex'] = _distribuir_unissex_em_faixa(
            falta_f,
            falta_m,
            estoque_atual[faixa]['unissex']
        )

        for i in range(len(instituicoes)):
            atendido_inst[i][faixa]['dist_especifico_fem'] += al_f[i]
            atendido_inst[i][faixa]['dist_especifico_masc'] += al_m[i]
            atendido_inst[i][faixa]['dist_unissex_fem'] += al_uf[i]
            atendido_inst[i][faixa]['dist_unissex_masc'] += al_um[i]


#* distribuir prioridade com meta minima progressiva e proporcionalidade ponderada
def distribuir_prioridade_proporcional(
    instituicoes,
    estoques,
    minimo=None,
    penalizacao=None
):
    """
    Executa a distribuicao de um grupo de prioridade com meta minima
    progressiva opcional e distribuicao proporcional ponderada pela
    penalizacao configurada.
    """

    estoque_atual = {
        faixa: valores.copy()
        for faixa, valores in estoques.items()
    }

    faixas_lista = list(estoque_atual.keys())
    buckets = [(faixa, genero) for faixa in faixas_lista for genero in ('feminino', 'masculino')]

    atendido_inst = [
        {
            faixa: {
                'dist_especifico_fem': 0,
                'dist_especifico_masc': 0,
                'dist_unissex_fem': 0,
                'dist_unissex_masc': 0
            }
            for faixa in faixas_lista
        }
        for _ in instituicoes
    ]

    totais_solicitados = [
        sum(
            inst['solicitado'][faixa][genero]
            for faixa in faixas_lista
            for genero in ('feminino', 'masculino')
        )
        for inst in instituicoes
    ]

    pesos = [
        calcular_peso_penalizacao(total, penalizacao)
        for total in totais_solicitados
    ]

    # sub-etapa A: meta minima progressiva (passe 1 por perfil e passe 2 de compensacao)
    if minimo and minimo.get('ativo', False) and minimo.get('quantidade', 0) > 0:
        qtd_minima = int(minimo['quantidade'])

        alvos_p1 = []
        for idx, inst in enumerate(instituicoes):
            dem_flat = [inst['solicitado'][faixa][genero] for (faixa, genero) in buckets]
            alvo_total = min(qtd_minima, totais_solicitados[idx])
            m_flat, _ = alocar_proporcional_ponderado(dem_flat, alvo_total)
            alvo_dict = {}
            for b_idx, (faixa, genero) in enumerate(buckets):
                alvo_dict.setdefault(faixa, {})[genero] = m_flat[b_idx]
            alvos_p1.append(alvo_dict)

        _aplicar_rodada_igualitaria_faixas(instituicoes, alvos_p1, estoque_atual, atendido_inst)

        # passe 2: aproxima instituicoes abaixo da meta usando apenas faixas com saldo disponivel
        alvos_p2 = []
        for idx, inst in enumerate(instituicoes):
            ja_recebido = sum(
                atendido_inst[idx][faixa]['dist_especifico_fem']
                + atendido_inst[idx][faixa]['dist_especifico_masc']
                + atendido_inst[idx][faixa]['dist_unissex_fem']
                + atendido_inst[idx][faixa]['dist_unissex_masc']
                for faixa in faixas_lista
            )
            gap = max(0, min(qtd_minima, totais_solicitados[idx]) - ja_recebido)
            dem_disp = []
            for (faixa, genero) in buckets:
                suf = 'fem' if genero == 'feminino' else 'masc'
                ja_fg = (
                    atendido_inst[idx][faixa][f'dist_especifico_{suf}']
                    + atendido_inst[idx][faixa][f'dist_unissex_{suf}']
                )
                rest_fg = max(0, inst['solicitado'][faixa][genero] - ja_fg)
                tem_estoque = (estoque_atual[faixa][genero] + estoque_atual[faixa]['unissex']) > 0
                dem_disp.append(rest_fg if tem_estoque else 0)

            m2_flat, _ = alocar_proporcional_ponderado(dem_disp, min(gap, sum(dem_disp)))
            alvo_dict = {}
            for b_idx, (faixa, genero) in enumerate(buckets):
                alvo_dict.setdefault(faixa, {})[genero] = m2_flat[b_idx]
            alvos_p2.append(alvo_dict)

        _aplicar_rodada_igualitaria_faixas(instituicoes, alvos_p2, estoque_atual, atendido_inst)

    # sub-etapa B: distribuicao proporcional ponderada do saldo restante
    for faixa in faixas_lista:
        rest_f = [
            inst['solicitado'][faixa]['feminino']
            - atendido_inst[i][faixa]['dist_especifico_fem']
            - atendido_inst[i][faixa]['dist_unissex_fem']
            for i, inst in enumerate(instituicoes)
        ]
        rest_m = [
            inst['solicitado'][faixa]['masculino']
            - atendido_inst[i][faixa]['dist_especifico_masc']
            - atendido_inst[i][faixa]['dist_unissex_masc']
            for i, inst in enumerate(instituicoes)
        ]

        al_f, estoque_atual[faixa]['feminino'] = alocar_proporcional_ponderado(
            rest_f, estoque_atual[faixa]['feminino'], pesos
        )
        al_m, estoque_atual[faixa]['masculino'] = alocar_proporcional_ponderado(
            rest_m, estoque_atual[faixa]['masculino'], pesos
        )

        falta_f = [rest_f[i] - al_f[i] for i in range(len(instituicoes))]
        falta_m = [rest_m[i] - al_m[i] for i in range(len(instituicoes))]

        al_uf, al_um, estoque_atual[faixa]['unissex'] = _distribuir_unissex_em_faixa(
            falta_f,
            falta_m,
            estoque_atual[faixa]['unissex'],
            pesos=pesos
        )

        for i in range(len(instituicoes)):
            atendido_inst[i][faixa]['dist_especifico_fem'] += al_f[i]
            atendido_inst[i][faixa]['dist_especifico_masc'] += al_m[i]
            atendido_inst[i][faixa]['dist_unissex_fem'] += al_uf[i]
            atendido_inst[i][faixa]['dist_unissex_masc'] += al_um[i]

    # montar estrutura de retorno compativel com distribuir_todas_faixas
    resultado = []
    for idx, inst in enumerate(instituicoes):
        faixas_res = {}
        for faixa in faixas_lista:
            sol_f = inst['solicitado'][faixa]['feminino']
            sol_m = inst['solicitado'][faixa]['masculino']
            dados_f = atendido_inst[idx][faixa]

            tot_f = dados_f['dist_especifico_fem'] + dados_f['dist_unissex_fem']
            tot_m = dados_f['dist_especifico_masc'] + dados_f['dist_unissex_masc']

            faixas_res[faixa] = {
                'solicitacao_fem': sol_f,
                'solicitacao_masc': sol_m,
                'dist_especifico_fem': dados_f['dist_especifico_fem'],
                'dist_especifico_masc': dados_f['dist_especifico_masc'],
                'dist_unissex_fem': dados_f['dist_unissex_fem'],
                'dist_unissex_masc': dados_f['dist_unissex_masc'],
                'total_fem': tot_f,
                'total_masc': tot_m,
                'total_distribuido': tot_f + tot_m,
                'falta_fem': sol_f - tot_f,
                'falta_masc': sol_m - tot_m
            }

        tot_sol_f = sum(f['solicitacao_fem'] for f in faixas_res.values())
        tot_sol_m = sum(f['solicitacao_masc'] for f in faixas_res.values())
        tot_at_f = sum(f['total_fem'] for f in faixas_res.values())
        tot_at_m = sum(f['total_masc'] for f in faixas_res.values())
        falta_tot = sum(f['falta_fem'] + f['falta_masc'] for f in faixas_res.values())

        resultado.append({
            'nome': inst['nome'],
            'faixas': faixas_res,
            'peso_penalizacao': pesos[idx],
            'total_solicitado_fem': tot_sol_f,
            'total_solicitado_masc': tot_sol_m,
            'total_fem': tot_at_f,
            'total_masc': tot_at_m,
            'total_distribuido': tot_at_f + tot_at_m,
            'falta_total': falta_tot
        })

    return {
        'instituicoes': resultado,
        'estoque_restante': estoque_atual
    }


#* preparar df final distribuido para todas as prioridades
def distribuir_todas_prioridades(
    grupos_distribuicao,
    estoques,
    categorias,
    minimo=None,
    penalizacao=None,
    prioridades_proporcionais=None
):
    """
    Executa a distribuição de todas as prioridades em sequência
    e retorna um DataFrame consolidado com os resultados.
    """
    ### terminal.etapa('[ DISTRIBUICAO ] Distribuindo todas as prioridades...')

    # Ordena as prioridades numericamente
    prioridades = sorted(
        grupos_distribuicao,
        key=lambda prioridade: int(
            ''.join(
                caractere
                for caractere in str(prioridade)
                if caractere.isdigit()
            )
        )
    )

    estoque_atual = {
        faixa: valores.copy()
        for faixa, valores in estoques.items()
    }

    registros = []
    resultados_prioridade = {}

    for prioridade in prioridades:

        instituicoes_originais = grupos_distribuicao[prioridade]

        usar_proporcional = (
            prioridades_proporcionais is not None
            and prioridade in prioridades_proporcionais
        )

        # executa a distribuicao da prioridade atual
        if usar_proporcional:
            resultado = distribuir_prioridade_proporcional(
                instituicoes=instituicoes_originais,
                estoques=estoque_atual,
                minimo=minimo,
                penalizacao=penalizacao
            )
        else:
            resultado = distribuir_todas_faixas(
                instituicoes=instituicoes_originais,
                estoques=estoque_atual
            )

        resultados_prioridade[prioridade] = resultado

        # atualiza o estoque para a proxima prioridade
        estoque_atual = resultado['estoque_restante']

        instituicoes_distribuidas = resultado['instituicoes']

        if len(instituicoes_originais) != len(instituicoes_distribuidas):
            raise ValueError(
                f'Divergência na quantidade de instituições '
                f'da prioridade {prioridade}.'
            )

        # consolida os dados de cada instituicao
        for original, distribuicao in zip(
            instituicoes_originais,
            instituicoes_distribuidas
        ):

            if original['nome'] != distribuicao['nome']:
                raise ValueError(
                    f'Divergência entre instituição original '
                    f'e distribuída na prioridade {prioridade}.'
                )

            registro = {
                'Prioridade': original['prioridade'],
                'Região': original['regiao'],
                'Localidade': original['localidade'],
                'Instituição': original['nome'],
                'Ordem Inscrição': original['ordem_inscricao'],
                'CNPJ Válido': original['cnpj_valido']
            }

            total_solicitado = 0
            total_atendido = 0
            total_faltante = 0

            for faixa in categorias:

                solicitado = original['solicitado'][faixa]
                distribuido = distribuicao['faixas'][faixa]

                solicitado_fem = solicitado['feminino']
                solicitado_masc = solicitado['masculino']

                atendido_fem = distribuido['total_fem']
                atendido_masc = distribuido['total_masc']

                falta_fem = distribuido['falta_fem']
                falta_masc = distribuido['falta_masc']

                registro.update({
                    # solicitacao original
                    f'Solicitado Fem {faixa}': solicitado_fem,
                    f'Solicitado Masc {faixa}': solicitado_masc,

                    # origem do estoque utilizado
                    f'Distribuido Fem {faixa}':
                        distribuido['dist_especifico_fem'],

                    f'Distribuido Masc {faixa}':
                        distribuido['dist_especifico_masc'],

                    f'Distribuido Unissex Fem {faixa}':
                        distribuido['dist_unissex_fem'],

                    f'Distribuido Unissex Masc {faixa}':
                        distribuido['dist_unissex_masc'],

                    # atendimento final
                    f'Atendido Fem {faixa}': atendido_fem,
                    f'Atendido Masc {faixa}': atendido_masc,

                    # demanda nao atendida
                    f'Falta Fem {faixa}': falta_fem,
                    f'Falta Masc {faixa}': falta_masc,

                    # totais por faixa
                    f'Solicitado Total {faixa}':
                        solicitado_fem + solicitado_masc,

                    f'Atendido Total {faixa}':
                        atendido_fem + atendido_masc,

                    f'Falta Total {faixa}':
                        falta_fem + falta_masc
                })

                total_solicitado += solicitado_fem + solicitado_masc
                total_atendido += atendido_fem + atendido_masc
                total_faltante += falta_fem + falta_masc

            percentual_atendimento = (
                round((total_atendido / total_solicitado) * 100, 2)
                if total_solicitado > 0
                else 0.0
            )
            peso_aplicado = round(
                distribuicao.get('peso_penalizacao', 1.0),
                4
            )

            registro.update({
                'Solicitado Total': total_solicitado,
                'Atendido Total': total_atendido,
                'Falta Total': total_faltante,
                'Percentual Atendimento': percentual_atendimento,
                'Peso Penalizacao': peso_aplicado
            })

            registros.append(registro)

    df_resultados = pd.DataFrame(registros)

    return {
        'instituicoes': df_resultados,
        'estoque_restante': estoque_atual,
        'resultados_prioridade': resultados_prioridade
    }


#* comparar a demanda solicitada com o estoque disponivel
def comparar_solicitado_estoque(demanda_regional, estoques_regionais):
    """
    Compara a demanda solicitada total por prioridade com o estoque disponível por região, localidade, faixa etária e gênero.
    Retorna um dicionário com a estrutura:
    {
        'Região': {
            'Localidade': {
                'Faixa Etária': {
                    'demanda_feminino': int,
                    'demanda_masculino': int,
                    'estoque_feminino': int,
                    'estoque_masculino': int,
                    'estoque_unissex': int,
                    'deficit_feminino': int,
                    'deficit_masculino': int
                }
            }
        }
    }
    """

    ### terminal.etapa('[ DISTRIBUICAO ] Comparando demanda solicitada com estoque disponivel...')

    # consolida a demanda de todas as prioridades
    demanda_total = {}

    for prioridade, regioes in demanda_regional.items():

        for regiao, localidades in regioes.items():

            for localidade, faixas in localidades.items():

                demanda_total.setdefault(regiao, {})
                demanda_total[regiao].setdefault(localidade, {})

                for faixa, generos in faixas.items():

                    demanda_total[regiao][localidade].setdefault(
                        faixa,
                        {'feminino': 0, 'masculino': 0}
                    )

                    demanda_total[regiao][localidade][faixa]['feminino'] += (
                        generos['feminino']
                    )

                    demanda_total[regiao][localidade][faixa]['masculino'] += (
                        generos['masculino']
                    )

    resultado = {}

    regioes = dict.fromkeys(
        list(demanda_total) + list(estoques_regionais)
    )

    for regiao in regioes:

        resultado[regiao] = {}

        localidades = dict.fromkeys(
            list(demanda_total.get(regiao, {}))
            + list(estoques_regionais.get(regiao, {}))
        )

        for localidade in localidades:

            resultado[regiao][localidade] = {}

            faixas = dict.fromkeys(
                list(demanda_total.get(regiao, {}).get(localidade, {}))
                + list(estoques_regionais.get(regiao, {}).get(localidade, {}))
            )

            for faixa in faixas:

                demanda = demanda_total.get(
                    regiao, {}
                ).get(localidade, {}).get(faixa, {})

                estoque = estoques_regionais.get(
                    regiao, {}
                ).get(localidade, {}).get(faixa, {})

                demanda_fem = demanda.get('feminino', 0)
                demanda_masc = demanda.get('masculino', 0)

                estoque_fem = estoque.get('feminino', 0)
                estoque_masc = estoque.get('masculino', 0)
                estoque_uni = estoque.get('unissex', 0)

                resultado[regiao][localidade][faixa] = {
                    'demanda_feminino': demanda_fem,
                    'demanda_masculino': demanda_masc,
                    'estoque_feminino': estoque_fem,
                    'estoque_masculino': estoque_masc,
                    'estoque_unissex': estoque_uni,
                    'deficit_feminino': max(0, demanda_fem - estoque_fem),
                    'deficit_masculino': max(0, demanda_masc - estoque_masc)
                }

    return resultado


#* resumir a demanda e o estoque total por faixa etaria e genero
def resumir_demanda_estoque(demanda_regional, estoques_regionais):
    """
    Consolida a demanda por prioridade e o estoque total disponível,
    agrupando os valores por faixa etária e gênero.

    Retorna um dicionário com a demanda de cada prioridade e o
    estoque feminino, masculino e unissex disponível no estado.
    """

    ### terminal.etapa('[ DISTRIBUICAO ] Resumindo demanda e estoque total por faixa etaria e genero...')

    resumo = {
        'demanda': {},
        'estoque': {}
    }

    # consolidar demanda por prioridade
    for prioridade, regioes in demanda_regional.items():

        resumo['demanda'][prioridade] = {}

        for localidades in regioes.values():

            for faixas in localidades.values():

                for faixa, generos in faixas.items():

                    resumo['demanda'][prioridade].setdefault(
                        faixa,
                        {'feminino': 0, 'masculino': 0}
                    )

                    resumo['demanda'][prioridade][faixa]['feminino'] += (
                        generos['feminino']
                    )

                    resumo['demanda'][prioridade][faixa]['masculino'] += (
                        generos['masculino']
                    )

    # consolidar estoque de todas as regioes
    for localidades in estoques_regionais.values():

        for faixas in localidades.values():

            for faixa, generos in faixas.items():

                resumo['estoque'].setdefault(
                    faixa,
                    {
                        'feminino': 0,
                        'masculino': 0,
                        'unissex': 0
                    }
                )

                for genero in ['feminino', 'masculino', 'unissex']:

                    resumo['estoque'][faixa][genero] += generos[genero]

    return resumo


#* separar reserva obrigatoria de estoque por faixa etaria e genero
def separar_reserva_estoque(
    estoques,
    percentual=0.15,
    ativa=True,
    arredondamento='cima'
):
    """
    Calcula a reserva obrigatoria de estoque por faixa etaria e genero
    (incluindo unissex), retornando bruto, reservado e distribuivel.
    """

    if not ativa or percentual <= 0:
        bruto = {
            faixa: {genero: int(qtd) for genero, qtd in generos.items()}
            for faixa, generos in estoques.items()
        }
        reservado = {
            faixa: {genero: 0 for genero in generos}
            for faixa, generos in estoques.items()
        }
        distribuivel = {
            faixa: {genero: int(qtd) for genero, qtd in generos.items()}
            for faixa, generos in estoques.items()
        }
        return {
            'bruto': bruto,
            'reservado': reservado,
            'distribuivel': distribuivel
        }

    bruto = {}
    reservado = {}
    distribuivel = {}

    for faixa, generos in estoques.items():
        bruto[faixa] = {}
        reservado[faixa] = {}
        distribuivel[faixa] = {}

        for genero, quantidade in generos.items():
            total = int(quantidade)

            if arredondamento == 'cima':
                qtd_reservada = math.ceil(total * percentual)
            else:
                qtd_reservada = math.floor(total * percentual)

            # garante que a reserva nao ultrapasse o estoque bruto nem fique negativa
            qtd_reservada = max(0, min(total, qtd_reservada))
            qtd_distribuivel = total - qtd_reservada

            bruto[faixa][genero] = total
            reservado[faixa][genero] = qtd_reservada
            distribuivel[faixa][genero] = qtd_distribuivel

    return {
        'bruto': bruto,
        'reservado': reservado,
        'distribuivel': distribuivel
    }