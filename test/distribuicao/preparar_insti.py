
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from modules import leitura, classificacao, distribuicao, terminal

from config.caixa_encantada import fontes, categorias, regras
from config.caixa_encantada import config as campanha

terminal.titulo('TESTE DE PREPARAÇÃO DAS INSTITUIÇÕES')

try:

    inscricoes = leitura.ler_excel(
        fontes.ARQ_INSCRICOES,
        planilha=fontes.PLAN_INSCRICOES,
        colunas=fontes.COL_INSC
    )

    colunas_solicitacao = [
        categorias.CATEGORIAS[faixa][genero]['demanda']
        for faixa in categorias.CATEGORIAS
        for genero in ['feminino', 'masculino']
    ]

    classificados = classificacao.classificar_instituicoes(
        dados=inscricoes,
        colunas_solicitacao=colunas_solicitacao,
        prioridades=campanha.PRIORIDADES_QTDE,
        coluna_beneficiario='Beneficiario',
        coluna_cnpj='CNPJ',
        extrair_ordem=regras.extrair_ordem_insc,
        validar_cnpj=regras.validar_cnpj
    )

    # selecionar apenas p1
    prioridade = classificados[
        classificados['Prioridade'] == 1
    ].copy()

    # preparar estrutura
    resultado = distribuicao.preparar_instituicoes(
        dados=prioridade,
        categorias=categorias.CATEGORIAS
    )

    # conferir algumas instituições
    for instituicao in resultado[:3]:
        print(instituicao)

    terminal.sucesso(
        f'{len(resultado)} instituições preparadas!'
    )

except Exception as e:
    terminal.erro(f'Falha no teste: {e}')
