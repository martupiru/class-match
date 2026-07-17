"""
Utilidades de normalización de texto para reconciliar inconsistencias entre
las distintas fuentes de datos (encuesta, escuelas, cursos, distancias)
"""

import re
import unicodedata
from datetime import time


def _sin_acentos(texto: str) -> str:
    """Remueve tildes/diacríticos para comparar de forma robusta"""
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def _clave(texto: str) -> str:
    """Clave de comparación: sin tildes, minúscula, sin espacios extra"""
    return _sin_acentos(texto).strip().lower()


# Forma canónica (con tilde correcta) que va a quedar en todos los CSV
# generados y en los objetos del dominio. "Ciudad" se mapea a "Capital"
# por confirmación del usuario (son el mismo departamento)
_DEPARTAMENTOS_CANONICOS = [
    "Capital",
    "Godoy Cruz",
    "Guaymallén",
    "Las Heras",
    "Luján de Cuyo",
    "Maipú",
]
_MAPA_DEPARTAMENTOS = {_clave(d): d for d in _DEPARTAMENTOS_CANONICOS}
_MAPA_DEPARTAMENTOS[_clave("Ciudad")] = "Capital"


def normalizar_departamento(texto: str) -> str:
    """Convierte cualquier variante de un departamento a su forma canónica

    Lanza ValueError si el departamento no es reconocido, para no dejar
    pasar silenciosamente un error de tipeo en los datos de origen.
    """
    clave = _clave(texto)
    if clave not in _MAPA_DEPARTAMENTOS:
        raise ValueError(
            f"Departamento no reconocido: '{texto}'. "
            f"Departamentos válidos: {_DEPARTAMENTOS_CANONICOS} (+ 'Ciudad' -> Capital)"
        )
    return _MAPA_DEPARTAMENTOS[clave]


_DIAS_CANONICOS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_MAPA_DIAS = {_clave(d): d for d in _DIAS_CANONICOS}


def normalizar_dia(texto: str) -> str:
    """Convierte cualquier variante de un dia de la semana a su forma canonica."""
    clave = _clave(texto)
    if clave not in _MAPA_DIAS:
        raise ValueError(f"Día no reconocido: '{texto}'. Días válidos: {_DIAS_CANONICOS}")
    return _MAPA_DIAS[clave]


def extraer_numero_id(codigo: str) -> int:
    """Extrae la parte numérica de un identificador alfanumérico tipo
    'E3', 'C17', 'P01' -> 3, 17, 1.
    Lanza ValueError si no se encuentra ningún número en el id
    """
    match = re.search(r"\d+", codigo)
    if not match:
        raise ValueError(f"No se pudo extraer un número del id: '{codigo}'")
    return int(match.group())

def hora_entera_a_time(hora) -> time:
    """Convierte una hora entera (ej. 9, 14) tal como viene en cursos.csv
    ('Inicio'/'Fin') a un objeto time en punto (ej. time(9, 0), time(14, 0)).
    Lanza ValueError si el valor no es una hora válida (0-23).
    """
    try:
        hora_int = int(hora)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Hora inválida: '{hora}'. Se esperaba un entero (0-23)") from exc

    if not 0 <= hora_int <= 23:
        raise ValueError(f"Hora fuera de rango: '{hora}'. Debe estar entre 0 y 23")

    return time(hora_int, 0)


def turno_a_horario(turno: str) -> tuple[time, time]:
    """Convierte un turno textual a un rango horario."""
    clave = _clave(turno)

    if clave == "manana":
        return time(8, 0), time(12, 0)

    if clave == "tarde":
        return time(14, 0), time(18, 0)

    if clave == "noche":
        return time(18, 0), time(22, 0)

    raise ValueError(f"Turno no reconocido: '{turno}'. Turnos válidos: mañana, tarde, noche")