import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from modules.distribuicao import distribuir_igualitario

instituicoes = [
    {'nome': 'Instituição A', 'solicitado': 1},
    {'nome': 'Instituição B', 'solicitado': 100},
    {'nome': 'Instituição C', 'solicitado': 100}
]

resultado, restante = distribuir_igualitario(
    instituicoes,
    100
)

print(resultado)
print('Estoque restante:', restante)