import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

import pandas as pd
from modules.classificacao import classificar_geografia, organizar_por_regiao

dados_teste = pd.DataFrame({
    'Cidade': [
        'Campo Grande',
        'Sidrolândia',
        'Dourados'
    ]
})

regioes = pd.read_csv('data/CE/Regiao.csv')

resultado = classificar_geografia(
    dados=dados_teste,
    coluna_cidade='Cidade',
    regioes=regioes,
    coluna_municipio='Município',
    coluna_regiao='Região',
    capital='Campo Grande'
)

print(resultado)

resultado = organizar_por_regiao(resultado)

for regiao, instituicoes in resultado.items():
    print(f'\nREGIÃO: {regiao}')
    print(instituicoes[['Cidade', 'Região', 'Localidade']])