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

bloqueio_timer = threading.Lock() # impede que o temporizador seja reiniciado enquanto ele esta rodando

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

def parar_processo():
    '''
    Encerra o processo anterior com segurança.
    '''
    global processo

    if processo is None:
        return

    if processo.poll() is None:  # processo ainda esta rodando

        terminal.info('Encerrando processo anterior...')

        processo.terminate()  # envia sinal de terminacao

        try:
            processo.wait(timeout=5)  # espera o processo encerrar

        except subprocess.TimeoutExpired:
            terminal.info('Processo não encerrou, forçando encerramento...')
            processo.kill()  # força o encerramento
            processo.wait()  # espera o processo encerrar

    processo = None  # reseta o processo para None

def executar(arquivo,raiz):
    '''
    Executa ou reinicia o arquivo selecionado.
    '''
    global processo

    with bloqueio_processo:  # garante que apenas um processo seja iniciado por vez

        if encerrando.is_set():
            return  # se o processo esta sendo encerrado nao inicia outro

        parar_processo()  # encerra o processo anterior
        limpar_terminal()  # limpa o terminal antes de iniciar o novo processo

        terminal.info(f'Executando: {arquivo.name}')

        # inclui a raiz do projeto no caminho de importacao para facilitar imports de modulos em subpastas
        ambiente = os.environ.copy()

        pythonpath_atual = ambiente.get('PYTHONPATH', '')

        ambiente['PYTHONPATH'] = (
            str(raiz) 
            + (os.pathsep + pythonpath_atual if pythonpath_atual else '')
        )

        try:

            processo = subprocess.Popen(
                [
                    sys.executable,  # caminho do interpretador python que esta rodando este script
                    str(arquivo)  # caminho do arquivo .py a ser executado
                ],
                cwd=str(raiz),  # define a raiz do projeto como diretorio de trabalho
                env=ambiente,  # define o ambiente com a raiz do projeto no PYTHON
            )

        except OSError as erro:

            processo = None 
            terminal.erro(f'Falha ao executar o processo: {erro}')

# CONTROLE DE REINICIO 

def agendar_reinicio(arquivo, raiz, debounce):
    '''
    Aguarda um tempo após a última modificação, evita multiplos reinicios
    '''

    global timer_reinicio

    with bloqueio_timer:  # garante que apenas um temporizador seja iniciado por vez

        if encerrando.is_set():
            return  # se o processo esta sendo encerrado nao agenda reinicio

        if timer_reinicio is not None:
            timer_reinicio.cancel()  # cancela o temporizador anterior

        timer_reinicio = threading.Timer(
            debounce, 
            executar, 
            args=(arquivo, raiz)
            )

        timer_reinicio.daemon = True  # garante que o temporizador nao bloqueie a finalizacao do script
        timer_reinicio.start()  # inicia o temporizador

def reiniciar(arquivo,raiz):
    '''
    Executa novamente o arquivo selecionado
    '''
    global timer_reinicio

    with bloqueio_timer:  # garante que apenas um temporizador seja iniciado por vez

        if encerrando.is_set():
            return  # se o processo esta sendo encerrado nao reinicia

        terminal.sucesso('Arquivo alterado! Reiniciando...')

        executar(arquivo, raiz)  # reinicia o processo imediatamente

# MONITORAMENTO 

class ReloadHandler(FileSystemEventHandler):
    '''
    Manipulador de eventos para monitorar alterações em arquivos.
    '''

    def __init__(self, raiz, padroes, arquivo, debounce):
        super().__init__()

        self.raiz = raiz
        self.padroes = padroes
        self.arquivo = arquivo
        self.debounce = debounce

    def verificar_evento(self, event):
        '''
        Verifica se o evento é relevante para o reload.
        '''
        if event.is_directory:
            return  # ignora eventos de diretório

        caminhos = [event.src_path]

        # considera tambem o destino em alteracoes de renomear

        if hasattr(event, 'dest_path'):
            caminhos.append(event.dest_path)

        for caminho in caminhos:

            caminho = Path(caminho)

            if caminho.suffix.lower() != '.py':
                continue  # ignora arquivos que nao sao .py

            if caminho_ignorado(
                caminho,
                self.raiz,
                self.padroes
            ):
                continue  # ignora arquivos que estao em pastas ignoradas ou que correspondem a padroes de ignorar

            agendar_reinicio(
                self.arquivo,
                self.raiz,
                self.debounce
            )

            return

    def on_modified(self, event):
        self.verificar_evento(event)

    def on_created(self, event):
        self.verificar_evento(event)

    def on_moved(self, event):
        self.verificar_evento(event)

    def on_deleted(self, event):
        self.verificar_evento(event)

# INICIALIZACAO
