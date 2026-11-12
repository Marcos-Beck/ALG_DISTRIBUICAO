import re

# ordem de inscricao

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

# validacao cnpj

def validar_cnpj(cnpj):

    if cnpj is None:
        return False

    # Remover pontuação e espaços
    cnpj = re.sub(r'[^A-Za-z0-9]', '', str(cnpj)).upper()

    # Verificar tamanho
    if len(cnpj) != 14:
        return False

    # Rejeitar sequências repetidas
    if len(set(cnpj)) == 1:
        return False

    # Os dois últimos caracteres devem ser numéricos
    if not cnpj[-2:].isdigit():
        return False

    # Converter caracteres para valores numéricos
    valores = [ord(caractere) - 48 for caractere in cnpj]

    # Pesos dos dígitos verificadores
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Primeiro dígito verificador
    soma_1 = sum(
        valor * peso
        for valor, peso in zip(valores[:12], pesos_1)
    )

    resto_1 = soma_1 % 11
    digito_1 = 0 if resto_1 < 2 else 11 - resto_1

    if digito_1 != valores[12]:
        return False

    # Segundo dígito verificador
    soma_2 = sum(
        valor * peso
        for valor, peso in zip(valores[:13], pesos_2)
    )

    resto_2 = soma_2 % 11
    digito_2 = 0 if resto_2 < 2 else 11 - resto_2

    return digito_2 == valores[13]
