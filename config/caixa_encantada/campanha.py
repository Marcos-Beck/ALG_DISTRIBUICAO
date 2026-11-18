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
        'max': 200
    },

    2: {
        'min': 201,
        'max': 260
    },

    3: {
        'min': 261,
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

