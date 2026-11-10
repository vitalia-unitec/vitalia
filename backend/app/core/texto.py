import unicodedata


# Minúsculas y sin acentos, para comparar texto escrito de distintas formas
def normalizar(texto: str | None) -> str:
    if not texto:
        return ""
    separado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in separado if unicodedata.category(c) != "Mn").lower()
