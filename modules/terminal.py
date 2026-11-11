
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)


# configuracoes visuais

CORES = {
    'INFO': Fore.CYAN,
    'TITULO': Fore.BLACK + Style.BRIGHT,
    'SUCCESS': Fore.WHITE,
    'STEP': Fore.YELLOW,
    'ERROR': Fore.BLACK
}

FUNDOS = {
    'INFO': Back.RESET,
    'TITULO': Back.WHITE,
    'SUCCESS': Back.GREEN,
    'STEP': Back.RESET,
    'ERROR': Back.RED
}


# funcao de log principal

def log(tipo, mensagem):

    horario = datetime.now().strftime("%H:%M:%S")

    cor = CORES.get(tipo, Fore.WHITE)
    fundo = FUNDOS.get(tipo, Back.RESET)

    print(
        f"{cor}{fundo}"
        f"[{horario}] [{tipo:^7}] {mensagem}"
        f"{Style.RESET_ALL}"
    )


# atalhos

def info(mensagem):
    log('INFO', mensagem)

def titulo(mensagem):
    log('TITULO', mensagem)

def sucesso(mensagem):
    log('SUCCESS', mensagem)

def etapa(mensagem):
    log('STEP', mensagem)

def erro(mensagem):
    log('ERROR', mensagem)


# elementos vis

def titulo(mensagem):
    print(Fore.CYAN + Style.BRIGHT + '=' * 55)
    print(f'{mensagem.upper()}')
    print('=' * 55)


def separador():
    print(Fore.LIGHTBLACK_EX + "-" * 55)


def progresso(atual, total, mensagem):

    porcentagem = (atual / total) * 100 if total else 0

    log(
        'INFO',
        f'[{porcentagem:5.1f}%] {mensagem}'
    )
