# identificacoes 

NOME = 'Caixa Encantada'
ANO = 2026

# config geo

CAPITAL = 'Campo Grande'

# ordem de processamento

ORDEM_GEO = [
    'Interior',
    'Capital'
]

# prioridades quantitativas 

PRIORIDADES_QTDE = {

    1: {
        'min': 0,
        'max': 210
    },

    2: {
        'min': 211,
        'max': None
    }

}

# estrategia de distribuicao

DISTRIBUICAO = {

    # todas as insti recebem uma parcela antes da etapa de complementacao 
    'metodo': 'igualitario_progressivo',

    # estoque regional utilizado antes do geral
    'estoque_regional': True,

    # estoque geral utilizado apos regional
    'estoque_geral': True,

    # permitir atendimento parcial 
    'atendimento_parcial': True

}

# reserva obrigatoria de estoque

RESERVA = {
    'ativa': True,
    'percentual': 0.15,
    'arredondamento': 'cima'
}

# meta minima progressiva de atendimento

MINIMO_ATENDIMENTO = {
    'ativo': True,
    'quantidade': 210,
    'prioridades': [2]
}

# penalizacao gradual de solicitacoes elevadas

PENALIZACAO = {
    'ativa': True,
    'inicio': 700,
    'limite': 1200,
    'intensidade': 1.0
}