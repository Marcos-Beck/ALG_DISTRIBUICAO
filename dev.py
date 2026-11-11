import subprocess # executa outros programas a partir do py
import sys # fornece acesso a variáveis e funções específicas do interpretador py
import threading # fornece suporte a threads (execução paralela de código)
import time # fornece funções para manipulação de tempo e datas
import os # fornece funções para interagir com o sistema operacional

from watchdog.observers import Observer # modulo externo monitora alterações em arquivos e diretórios tipo nodemon
from watchdog.events import FileSystemEventHandler # modulo externo manipula eventos de sistema de arquivos
from modules import terminal

processo = None # variável global para armazenar o processo em execução
ultimo_evento = 0 # variável global para armazenar o timestamp do último evento de modificação

def clear_console(): # função para limpar o console
    if os.name == 'nt': 
        os.system('cls')
    else: 
        os.system('clear')


def executar():
    global processo

    if processo:
        processo.terminate() # termina o processo em execução
        processo.wait() # aguarda o término do processo

    clear_console()

    terminal.info('Iniciando programa :) ...')

    processo = subprocess.Popen([
        sys.executable,
        'main.py'  # script que será executado #! fazer ser selecionado no terminal dps se possivel
    ])


class ReloadHandler(FileSystemEventHandler): # classe que manipula eventos de sistema de arquivos

    def on_modified(self, event):
        global ultimo_evento

        if event.is_directory: # ignora eventos de diretório
            return

        if not event.src_path.endswith('.py'): # ignora eventos de arquivos que não são .py
            return

        agora = time.time() # evita múltiplos eventos repetidos em sequência

        if agora - ultimo_evento < 1: # se o tempo desde o último evento for menor que 1 segundo, ignora
            return

        ultimo_evento = agora
        terminal.sucesso('Arquivo Alterado! Reiniciando...')
        executar()


observer = Observer() # cria um observador para monitorar alterações em arquivos e diretórios

observer.schedule(
    ReloadHandler(),
    path='.',
    recursive=True
    ) # agenda o observador para monitorar alterações no diretório atual e em subdiretórios

observer.start() 

executar()

try:
    threading.Event().wait() # aguarda indefinidamente até que o programa seja interrompido
except KeyboardInterrupt:
    terminal.erro('Programa interrompido D:\n')
    observer.stop() # para o observador quando o programa é interrompido
    if processo:
        processo.terminate()
        processo.wait() # aguarda o término do processo em execução

    
