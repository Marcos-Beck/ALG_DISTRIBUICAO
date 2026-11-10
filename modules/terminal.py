
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)


# configuracoes visuais

CORES = {
    "INFO": Fore.CYAN,
    "SUCCESS": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "DEBUG": Fore.MAGENTA,
    "STEP": Fore.BLUE
}

FUNDOS = {
    "INFO": Back.RESET,
    "SUCCESS": Back.GREEN,
    "WARNING": Back.YELLOW,
    "ERROR": Back.RED,
    "DEBUG": Back.MAGENTA,
    "STEP": Back.BLUE
}


# funcao de log principal

def log(tipo, mensagem):

    horario = datetime.now().strftime("%H:%M:%S")
    cor = CORES.get(tipo, Fore.WHITE)

    print(
        f"{Fore.LIGHTBLACK_EX}[{horario}] "
        f"{cor}[{tipo:^7}] "
        f"{Style.RESET_ALL}{mensagem}"
    )


# atalhos

def info(mensagem):
    log("INFO", mensagem)


def sucesso(mensagem):
    log("SUCCESS", mensagem)


def aviso(mensagem):
    log("WARNING", mensagem)


def erro(mensagem):
    log("ERROR", mensagem)


# elementos vis

def titulo(mensagem):

    print()
    print(Fore.CYAN + Style.BRIGHT + "=" * 55)
    print(f" {mensagem.upper()}")
    print("=" * 55)


def separador():
    print(Fore.LIGHTBLACK_EX + "-" * 55)


def progresso(atual, total, mensagem):

    porcentagem = (atual / total) * 100 if total else 0

    log(
        "INFO",
        f"[{porcentagem:5.1f}%] {mensagem}"
    )
