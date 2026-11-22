import re


#* ordem de inscricao
def extrair_ordem_insc(beneficiario):

    if not isinstance(beneficiario, str):
        return None

    resultado = re.match(
        r'^\s*(\d+)\s*[-–]\s*',
        beneficiario
    )

    if resultado:
        return int(resultado.group(1))

    return None


#* validacao cnpj
def validar_cnpj(cnpj):

    if cnpj is None:
        return False

    # remover pontuacao e espacos
    cnpj = re.sub(r'[^A-Za-z0-9]', '', str(cnpj)).upper()

    # verificar tamanho
    if len(cnpj) != 14:
        return False

    # rejeitar sequencias repetidas
    if len(set(cnpj)) == 1:
        return False

    # os dois ultimos caracteres devem ser numericos
    if not cnpj[-2:].isdigit():
        return False

    # converter caracteres para valores numericos
    valores = [ord(caractere) - 48 for caractere in cnpj]

    # pesos dos digitos verificadores
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # primeiro digito verificador
    soma_1 = sum(
        valor * peso
        for valor, peso in zip(valores[:12], pesos_1)
    )

    resto_1 = soma_1 % 11
    digito_1 = 0 if resto_1 < 2 else 11 - resto_1

    if digito_1 != valores[12]:
        return False

    # segundo digito verificador
    soma_2 = sum(
        valor * peso
        for valor, peso in zip(valores[:13], pesos_2)
    )

    resto_2 = soma_2 % 11
    digito_2 = 0 if resto_2 < 2 else 11 - resto_2

    return digito_2 == valores[13]