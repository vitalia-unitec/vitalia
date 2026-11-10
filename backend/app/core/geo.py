from math import asin, cos, radians, sin, sqrt

RADIO_TIERRA_KM = 6371.0

# Un grado mide unos 111 km; usar 110 deja el rectángulo un poco más grande que el círculo
KM_POR_GRADO = 110.0


def distancia_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * RADIO_TIERRA_KM * asin(sqrt(a))


# Rectángulo que contiene al círculo de búsqueda: lat mínima, lat máxima, lng mínima, lng máxima
def rectangulo(lat: float, lng: float, radio_km: float) -> tuple[float, float, float, float]:
    grados_lat = radio_km / KM_POR_GRADO
    grados_lng = radio_km / (KM_POR_GRADO * max(cos(radians(lat)), 0.01))
    return lat - grados_lat, lat + grados_lat, lng - grados_lng, lng + grados_lng
