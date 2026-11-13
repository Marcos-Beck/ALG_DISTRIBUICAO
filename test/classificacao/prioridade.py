import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))



from modules import leitura, classificacao, terminal

from config.caixa_encantada import fontes, categorias, regras
from config.caixa_encantada.config import PRIORIDADES_QTDE


terminal.titulo('TESTE DE CLASSIFICAÇÃO POR PRIORIDADE')

try:

    # ETAPA 1 - CARREGAR INSCRIÇÕES
    terminal.etapa('CARREGANDO INSCRIÇÕES...')

    inscricoes = leitura.ler_excel(
        fontes.ARQ_INSCRICOES,
        planilha=fontes.PLAN_INSCRICOES,
        colunas=fontes.COL_INSC
    )

    terminal.info(
        f'{len(inscricoes)} inscrições carregadas.'
    )

    # ETAPA 2 - IDENTIFICAR COLUNAS DE DEMANDA
    colunas_solicitacao = [
        categorias.CATEGORIAS[faixa][genero]['demanda']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    # ETAPA 3 - CLASSIFICAR INSTITUIÇÕES
    terminal.etapa('CLASSIFICANDO INSTITUIÇÕES...')

    classificados = classificacao.classificar_instituicoes(
        dados=inscricoes,
        colunas_solicitacao=colunas_solicitacao,
        prioridades=PRIORIDADES_QTDE,
        coluna_beneficiario='Beneficiario',
        coluna_cnpj='CNPJ',
        extrair_ordem=regras.extrair_ordem_insc,
        validar_cnpj=regras.validar_cnpj
    )

    # ETAPA 4 - SEPARAR PRIORIDADES
    terminal.etapa('SEPARANDO PRIORIDADES...')

    grupos = classificacao.separar_prioridade(
        dados=classificados,
        coluna_prioridade='Prioridade',
        prioridades=PRIORIDADES_QTDE
    )

    # ETAPA 5 - EXIBIR RESULTADOS
    for prioridade, instituicoes in grupos.items():

        print(f'\n========== PRIORIDADE P{prioridade} ==========')

        print(
            instituicoes[
                ['Beneficiario', 'Solicitação Total', 'Prioridade']
            ].to_string(index=False)
        )

        terminal.info(
            f'Total de instituições: {len(instituicoes)}'
        )

    terminal.sucesso('TESTE CONCLUÍDO!')

except Exception as e:

    terminal.erro(f'Falha no teste: {e}')





