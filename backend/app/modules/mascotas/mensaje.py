from urllib.parse import quote

LADA_MEXICO = "52"


# Texto de la edad: "3 años", "1 año y 2 meses", "4 meses"
def describir_edad(anios: int | None, meses: int | None) -> str | None:
    partes = []
    if anios:
        partes.append(f"{anios} año" if anios == 1 else f"{anios} años")
    if meses:
        partes.append(f"{meses} mes" if meses == 1 else f"{meses} meses")
    if not partes:
        return None
    return " y ".join(partes)


def armar_texto(
    clinica: str,
    nombre: str,
    especie: str,
    sexo: str,
    raza: str | None = None,
    edad_anios: int | None = None,
    edad_meses: int | None = None,
    color: str | None = None,
) -> str:
    datos = [nombre, f"{especie} {sexo}"]
    if raza:
        datos.append(raza)
    edad = describir_edad(edad_anios, edad_meses)
    if edad:
        datos.append(edad)
    if color:
        datos.append(f"color {color.lower()}")

    return (
        f"Hola, {clinica}. Los encontré en Vitalia. "
        f"Quiero información para mi mascota: {', '.join(datos)}."
    )


# Número para wa.me: solo dígitos y con lada de país
def numero_internacional(whatsapp: str) -> str:
    return LADA_MEXICO + whatsapp if len(whatsapp) == 10 else whatsapp


def armar_url(whatsapp: str, texto: str) -> str:
    return f"https://wa.me/{numero_internacional(whatsapp)}?text={quote(texto, safe='')}"
