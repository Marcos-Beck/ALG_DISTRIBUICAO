import argparse # recebe configuracoes e parametros pelo terminal
import fnmatch # compara nomes de arquivos com padroes
import os 
import sys # obtem informacoes do py que esta rodando
import subprocess 
import threading # executa funcoes em paralelo
import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from modules import terminal

# configuracoes

PASTAS_IGNORADAS = {
    '.git',
    '__pycache__',
    '.venv',
    'env',
    'venv',
    'build',
    'dist',
    '.pytest_cache'
}

processo = None # armazenar o processo do py que esta rodando

bloqueio_processo = threading.Lock() # impede que o processo seja reiniciado enquanto ele esta rodando

timer_reinicio = None # temporizador para guardar o tempo de espera antes de reiniciar o processo

encerrando = threading.Event() # sinaliza que o processo esta sendo encerrado

# FUNCOES AUX 

def limpar_terminal():
    '''
    Limpa o terminal.
    '''
    os.system('cls' if os.name == 'nt' else 'clear') # funciona no win, linux e mac :D

def caminho_ignorado(caminho, raiz, padroes, excecoes=None):
    '''
    Verifica se o caminho deve ser ignorado.
    '''
    caminho = Path(caminho)
    excecoes = excecoes or []

    try:
        relativo = caminho.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        relativo = caminho.resolve().as_posix()

    partes = Path(relativo).parts
    nome = caminho.name.lower()
    relativo = relativo.lower()

    # 1 verifica excecoes (tem prioridade sobre regras de ignorar)
    for padrao in excecoes:

        padrao = padrao.lower()

        if (
            fnmatch.fnmatch(relativo, padrao)
            or fnmatch.fnmatch(nome, padrao)
            or any(
                fnmatch.fnmatch(parte.lower(), padrao)
                for parte in partes
            )
        ):
            return False

    # 2 ignora pastas padrao
    if any(
        parte.lower() in PASTAS_IGNORADAS
        for parte in partes
    ):
        return True

    # 3 verifica padroes adc de ignorar
    for padrao in padroes:

        padrao = padrao.lower()

        if (
            fnmatch.fnmatch(relativo, padrao)
            or fnmatch.fnmatch(nome, padrao)
            or any(
                fnmatch.fnmatch(parte.lower(), padrao)
                for parte in partes
            )
        ):
            return True

    return False

# SELECAO DO ARQUIVO

def listar_arquivos(raiz):
    '''
    Lista todos os arquivos .py na raiz e subpastas, ignorando pastas e arquivos especificados.
    '''
    arquivos = []

    for pasta, subpastas, nomes in os.walk(raiz):

        # evita entrar em pastas ignoradas
        subpastas[:] = [
            nome for nome in subpastas
            if nome.lower() not in PASTAS_IGNORADAS
        ]

        for nome in nomes:

            if nome.lower().endswith('.py'):
                arquivos.append(Path(pasta) / nome)

    return sorted(arquivos)

def selecionar_arquivo(raiz, informado=None):
    '''
    Seleciona o arquivo .py a ser executado.
    '''
    # caso informado pelo comando
    if informado:

        arquivo = Path(informado)

        if not arquivo.is_absolute():
            arquivo = raiz / arquivo

        arquivo = arquivo.resolve()

    else:

        arquivos = listar_arquivos(raiz)

        if not arquivos:
            raise FileNotFoundError(
                terminal.erro('Nenhum arquivo .py encontrado na raiz e subpastas.')
                )
        terminal.etapa('Arquivos disponíveis:')

        for indice, arquivo in enumerate(arquivos, start=1):

            try: 
                nome = arquivo.relative_to(raiz)
            except ValueError:
                nome = arquivo

            terminal.info(f'[{indice}] {nome}')

        while True:

            escolha = input('\nSelecione o arquivo: ').strip()

            if escolha.isdigit():
                indice = int(escolha) - 1

                if 0 <= indice < len(arquivos):
                    arquivo = arquivos[indice]
                    break

                terminal.erro('Opção inválida.')

            else:

                arquivo = Path(escolha.strip('"').strip("'"))

                if not arquivo.is_absolute():
                    arquivo = raiz / arquivo

                arquivo = arquivo.resolve()

                if arquivo.is_file():
                    break

                terminal.erro('Arquivo não encontrado.')

    if not arquivo.exists():
        raise FileNotFoundError(
            terminal.erro(f'Arquivo não encontrado: {arquivo}')
        )

    if arquivo.suffix.lower() != '.py':
        raise ValueError(
            terminal.erro(f'Arquivo selecionado não é um arquivo .py: {arquivo}')
        )
    return arquivo

# EXECUCAO

