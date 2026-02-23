def verificar_senha(senha):
    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False
    tem_especial = False

    for c in senha:
        if c.isupper():
            tem_maiuscula = True
        elif c.islower():
            tem_minuscula = True
        elif c.isdigit():
            tem_numero = True
        else:
            tem_especial = True

    if tem_maiuscula and tem_minuscula and tem_numero and tem_especial:
        return True
    else:
        return False