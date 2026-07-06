from datetime import time
import unicodedata


TURNOS_HORARIOS = {
    "manana": (time(8, 0), time(12, 0)),
    "tarde": (time(14, 0), time(18, 0)),
}

DEPARTAMENTO_ALIASES = {
    "capital": "Ciudad",
    "ciudad": "Ciudad",
    "godoy cruz": "Godoy Cruz",
    "guaymallen": "Guaymallen",
    "las heras": "Las Heras",
    "lujan de cuyo": "Lujan de Cuyo",
    "maipu": "Maipu",
}


def parse_hora(valor) -> time:
    """
    Convierte valores de hora a datetime.time.

    Acepta:
    - enteros o floats: 9 -> 09:00
    - strings HH:MM: "09:30" -> 09:30
    - strings con hora sola: "9" -> 09:00
    """
    if isinstance(valor, time):
        return valor

    if isinstance(valor, (int, float)):
        hora = int(valor)
        minuto = int(round((float(valor) - hora) * 60))
        return time(hour=hora, minute=minuto)

    texto = str(valor).strip()

    if ":" in texto:
        partes = texto.split(":")
        return time(hour=int(partes[0]), minute=int(partes[1]))

    return time(hour=int(texto), minute=0)


def normalizar_texto(valor: str) -> str:
    """Normaliza espacios laterales en textos provenientes de CSV."""
    return str(valor).strip()


def sin_tildes(valor: str) -> str:
    """Devuelve el texto sin tildes ni diacríticos."""
    texto = normalizar_texto(valor)
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def normalizar_clave(valor: str) -> str:
    """Normaliza texto para usarlo como clave comparable."""
    return sin_tildes(valor).lower().strip()


def normalizar_dia(valor: str) -> str:
    """
    Normaliza días para comparar disponibilidad y cursos.

    Ejemplo:
    - "Sábado" -> "Sabado"
    - "Miércoles" -> "Miercoles"
    """
    return sin_tildes(valor).capitalize()


def normalizar_departamento(valor: str) -> str:
    """
    Normaliza departamentos para que coincidan con la matriz de distancias.

    En los datos hay equivalencias como:
    - Capital -> Ciudad
    - Maipú -> Maipu
    - Guaymallén -> Guaymallen
    """
    clave = normalizar_clave(valor)
    return DEPARTAMENTO_ALIASES.get(clave, sin_tildes(valor))


def turno_a_intervalo(turno: str) -> tuple[time, time]:
    """
    Convierte un turno textual en intervalo horario.

    Por ahora usamos la simplificación:
    - Mañana: 08:00 a 12:00
    - Tarde: 14:00 a 18:00
    """
    clave = normalizar_clave(turno)

    if clave not in TURNOS_HORARIOS:
        raise ValueError(f"Turno no reconocido: {turno}")

    return TURNOS_HORARIOS[clave]
