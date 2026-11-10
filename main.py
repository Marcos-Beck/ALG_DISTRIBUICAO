from modules import leitura
from modules import terminal

# carrega as bases
inscricoes, arrecadacao = leitura.carregar_bases()

# roda o diagnostico
leitura.diagnostico(inscricoes, arrecadacao)

terminal.sucesso('Processamento concluído! :D')