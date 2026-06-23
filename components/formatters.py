from datetime import date, datetime


def data_para_date(valor):
    """Converte datas em texto para date. Aceita ISO e DD/MM/AAAA."""
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor).strip()

    if not texto or texto in ["-", "None", "null"]:
        return None

    # Remove horário quando vier junto.
    texto_base = texto.split("T")[0].split(" " )[0]

    formatos = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(texto_base, formato).date()
        except Exception:
            pass

    return None


def data_br(valor, padrao="-"):
    """Formata data para DD/MM/AAAA, sem alterar o valor salvo no banco."""
    data = data_para_date(valor)

    if data:
        return data.strftime("%d/%m/%Y")

    if valor is None:
        return padrao

    texto = str(valor).strip()
    return texto if texto else padrao


def data_iso(valor, padrao=""):
    """Normaliza data para AAAA-MM-DD quando necessário."""
    data = data_para_date(valor)

    if data:
        return data.strftime("%Y-%m-%d")

    return padrao
