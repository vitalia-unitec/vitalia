from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.errors import AppError, Conflicto, NoEncontrado, SinPermiso
from app.core.fotos import borrar_foto, guardar_foto, url_publica
from app.core.geo import distancia_km
from app.core.paginacion import Paginacion
from app.core.tiempo import ahora_local
from app.modules.categorias import repository as categorias_repository
from app.modules.clinicas import repository
from app.modules.clinicas.filtros import FiltrosBusqueda
from app.modules.clinicas.horario import estado_apertura
from app.modules.clinicas.models import (
    Clinica,
    ClinicaTipo,
    FotoClinica,
    Horario,
    ServicioClinica,
)
from app.modules.clinicas.schemas import (
    ClinicaDetalleSalida,
    ClinicaEntrada,
    ClinicaNegocioSalida,
    ClinicaResumenSalida,
    FotoSalida,
    HorariosEntrada,
    ServicioEntrada,
)
from app.modules.usuarios.models import Usuario

MAX_SERVICIOS = 50
MAX_FOTOS = 10
FOTOS_EN_DETALLE = 5


# Armar la respuesta de una clínica
def armar_fotos(fotos: list[FotoClinica]) -> list[dict]:
    return [FotoSalida(id=f.id, url=url_publica(f.ruta), orden=f.orden).a_json() for f in fotos]


def _datos_resumen(clinica: Clinica, lat: float | None, lng: float | None) -> dict:
    estado = estado_apertura(clinica.horarios, clinica.urgencias_24h, ahora_local())
    distancia = None
    if lat is not None and lng is not None:
        distancia = round(distancia_km(lat, lng, clinica.lat, clinica.lng), 1)

    return {
        "id": clinica.id,
        "nombre": clinica.nombre,
        "tipos": clinica.tipos,
        "calificacion": round(clinica.calificacion_prom, 1)
        if clinica.calificacion_prom is not None
        else None,
        "total_resenas": clinica.total_resenas,
        "distancia_km": distancia,
        "abierto": estado.abierto,
        "cierra_a": estado.cierra_a,
        "abre_a": estado.abre_a,
        "urgencias_24h": clinica.urgencias_24h,
        "verificada": clinica.verificada,
        "foto_principal": url_publica(clinica.fotos[0].ruta) if clinica.fotos else None,
        "servicios_destacados": [s.nombre for s in clinica.servicios[:3]],
        "lat": clinica.lat,
        "lng": clinica.lng,
    }


def armar_resumen(clinica: Clinica, lat: float | None = None, lng: float | None = None) -> dict:
    return ClinicaResumenSalida.model_validate(_datos_resumen(clinica, lat, lng)).a_json()


def armar_detalle(
    clinica: Clinica,
    lat: float | None = None,
    lng: float | None = None,
    para_negocio: bool = False,
) -> dict:
    datos = {
        **_datos_resumen(clinica, lat, lng),
        "descripcion": clinica.descripcion,
        "direccion": {
            "calle": clinica.calle,
            "colonia": clinica.colonia,
            "alcaldia_municipio": clinica.alcaldia_municipio,
            "ciudad": clinica.ciudad,
            "estado": clinica.estado,
            "codigo_postal": clinica.codigo_postal,
        },
        "telefono": clinica.telefono,
        "whatsapp": clinica.whatsapp,
        "sitio_web": clinica.sitio_web,
        "horarios": clinica.horarios,
        "fotos": armar_fotos(clinica.fotos[:FOTOS_EN_DETALLE]),
        "servicios": clinica.servicios,
    }

    if para_negocio:
        return ClinicaNegocioSalida.model_validate({**datos, "activa": clinica.activa}).a_json()
    return ClinicaDetalleSalida.model_validate(datos).a_json()


# Búsqueda pública
def _por_calificacion(clinica: Clinica) -> tuple:
    sin_calificacion = clinica.calificacion_prom is None
    return (sin_calificacion, -(clinica.calificacion_prom or 0), -clinica.total_resenas, clinica.id)


def _por_resenas(clinica: Clinica) -> tuple:
    return (-clinica.total_resenas, -(clinica.calificacion_prom or 0), clinica.id)


def _esta_abierta(clinica: Clinica) -> bool:
    return estado_apertura(clinica.horarios, clinica.urgencias_24h, ahora_local()).abierto


def buscar(db: Session, filtros: FiltrosBusqueda, pag: Paginacion) -> tuple[list[dict], int]:
    clinicas = repository.buscar_activas(db, filtros)

    distancias = {}
    if filtros.tiene_ubicacion:
        distancias = {c.id: distancia_km(filtros.lat, filtros.lng, c.lat, c.lng) for c in clinicas}
        clinicas = [c for c in clinicas if distancias[c.id] <= filtros.radio_km]
    if filtros.abierto_ahora:
        clinicas = [c for c in clinicas if _esta_abierta(c)]

    if filtros.orden == "distancia":
        clinicas.sort(key=lambda c: (distancias[c.id], c.id))
    elif filtros.orden == "resenas":
        clinicas.sort(key=_por_resenas)
    else:
        clinicas.sort(key=_por_calificacion)

    pagina = clinicas[pag.desde : pag.desde + pag.por_pagina]
    return [armar_resumen(c, filtros.lat, filtros.lng) for c in pagina], len(clinicas)


# Consultas públicas
def obtener_publica(db: Session, clinica_id: int) -> Clinica:
    clinica = repository.obtener(db, clinica_id)
    if clinica is None or not clinica.activa:
        raise NoEncontrado("La clínica no existe")
    return clinica


# Panel de negocio
def obtener_propia(db: Session, clinica_id: int, usuario: Usuario) -> Clinica:
    clinica = repository.obtener(db, clinica_id)
    if clinica is None:
        raise NoEncontrado("La clínica no existe")
    if clinica.propietario_id != usuario.id:
        raise SinPermiso("Esta clínica no es tuya")
    return clinica


def _aplicar_datos(clinica: Clinica, datos: ClinicaEntrada) -> None:
    clinica.nombre = datos.nombre
    clinica.descripcion = datos.descripcion
    clinica.calle = datos.direccion.calle
    clinica.colonia = datos.direccion.colonia
    clinica.alcaldia_municipio = datos.direccion.alcaldia_municipio
    clinica.ciudad = datos.direccion.ciudad
    clinica.estado = datos.direccion.estado
    clinica.codigo_postal = datos.direccion.codigo_postal
    clinica.lat = datos.lat
    clinica.lng = datos.lng
    clinica.telefono = datos.telefono
    clinica.whatsapp = datos.whatsapp
    clinica.sitio_web = str(datos.sitio_web) if datos.sitio_web else None
    clinica.urgencias_24h = datos.urgencias_24h

    nuevos = set(datos.tipos)
    clinica.tipos_rel = [t for t in clinica.tipos_rel if t.tipo in nuevos]
    actuales = set(clinica.tipos)
    for tipo in datos.tipos:
        if tipo not in actuales:
            clinica.tipos_rel.append(ClinicaTipo(tipo=tipo))


def crear(db: Session, usuario: Usuario, datos: ClinicaEntrada) -> Clinica:
    clinica = Clinica(propietario_id=usuario.id)
    _aplicar_datos(clinica, datos)
    repository.guardar(db, clinica)
    return clinica


def editar(db: Session, clinica: Clinica, datos: ClinicaEntrada) -> Clinica:
    _aplicar_datos(clinica, datos)
    repository.guardar(db, clinica)
    return clinica


def dar_de_baja(db: Session, clinica: Clinica) -> None:
    clinica.activa = False
    repository.guardar(db, clinica)


def reemplazar_horarios(db: Session, clinica: Clinica, datos: HorariosEntrada) -> list[Horario]:
    clinica.horarios = [
        Horario(dia_semana=h.dia_semana, abre=h.abre, cierra=h.cierra) for h in datos.horarios
    ]
    repository.guardar(db, clinica)
    return clinica.horarios


def _revisar_categoria(db: Session, categoria_id: int) -> None:
    if categorias_repository.buscar_por_id(db, categoria_id) is None:
        raise AppError("VALIDACION", "La categoría no existe", 400)


def _buscar_servicio(clinica: Clinica, servicio_id: int) -> ServicioClinica:
    for servicio in clinica.servicios:
        if servicio.id == servicio_id:
            return servicio
    raise NoEncontrado("El servicio no existe en esta clínica")


def agregar_servicio(db: Session, clinica: Clinica, datos: ServicioEntrada) -> ServicioClinica:
    if len(clinica.servicios) >= MAX_SERVICIOS:
        raise Conflicto(f"Una clínica puede tener máximo {MAX_SERVICIOS} servicios")
    _revisar_categoria(db, datos.categoria_id)

    servicio = ServicioClinica(clinica_id=clinica.id, **datos.model_dump())
    repository.guardar(db, servicio)
    db.refresh(clinica)
    return servicio


def editar_servicio(
    db: Session, clinica: Clinica, servicio_id: int, datos: ServicioEntrada
) -> ServicioClinica:
    servicio = _buscar_servicio(clinica, servicio_id)
    _revisar_categoria(db, datos.categoria_id)

    for campo, valor in datos.model_dump().items():
        setattr(servicio, campo, valor)
    repository.guardar(db, servicio)
    return servicio


def borrar_servicio(db: Session, clinica: Clinica, servicio_id: int) -> None:
    servicio = _buscar_servicio(clinica, servicio_id)
    clinica.servicios.remove(servicio)
    db.commit()


# Fotos
def _renumerar(clinica: Clinica) -> None:
    for posicion, foto in enumerate(clinica.fotos, start=1):
        foto.orden = posicion


def agregar_foto(db: Session, clinica: Clinica, archivo: UploadFile) -> FotoClinica:
    if len(clinica.fotos) >= MAX_FOTOS:
        raise Conflicto(f"Una clínica puede tener máximo {MAX_FOTOS} fotos")

    ruta = guardar_foto(archivo, "clinicas")
    foto = FotoClinica(ruta=ruta, orden=len(clinica.fotos) + 1)
    clinica.fotos.append(foto)
    try:
        db.commit()
    except Exception:
        db.rollback()
        borrar_foto(ruta)
        raise
    db.refresh(foto)
    return foto


def reordenar_fotos(db: Session, clinica: Clinica, ids: list[int]) -> list[FotoClinica]:
    por_id = {foto.id: foto for foto in clinica.fotos}
    if len(set(ids)) != len(ids) or set(ids) != set(por_id):
        raise AppError("VALIDACION", "Envía una vez el id de cada foto de la clínica", 400)

    for posicion, foto_id in enumerate(ids, start=1):
        por_id[foto_id].orden = posicion
    db.commit()
    db.refresh(clinica)
    return clinica.fotos


def borrar_foto_de_clinica(db: Session, clinica: Clinica, foto_id: int) -> None:
    foto = next((f for f in clinica.fotos if f.id == foto_id), None)
    if foto is None:
        raise NoEncontrado("La foto no existe en esta clínica")

    ruta = foto.ruta
    clinica.fotos.remove(foto)
    _renumerar(clinica)
    db.commit()
    borrar_foto(ruta)
