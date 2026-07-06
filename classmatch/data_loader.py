from pathlib import Path
from typing import Dict, List

import pandas as pd

from classmatch.models import (
    BloqueDisponibilidad,
    ClassMatchData,
    Curso,
    Escuela,
    NivelProfesor,
    Profesor,
)
from classmatch.utils import (
    normalizar_departamento,
    normalizar_dia,
    normalizar_texto,
    parse_hora,
    turno_a_intervalo,
)


def _leer_csv(path: str | Path) -> pd.DataFrame:
    """
    Lee CSV detectando separador automáticamente.

    Esto permite combinar archivos separados por ';' y por ','.
    """
    return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")


def _parse_nivel(valor: str) -> NivelProfesor:
    texto = normalizar_texto(valor).upper()

    if texto == "SENIOR":
        return NivelProfesor.SENIOR
    if texto == "JUNIOR":
        return NivelProfesor.JUNIOR

    raise ValueError(f"Nivel de profesor no reconocido: {valor}")


def cargar_disponibilidades(path: str | Path) -> Dict[str, List[BloqueDisponibilidad]]:
    """
    Lee disponibilidad.csv con columnas:
    id_profesor,dia,turno

    Los turnos se convierten a intervalos horarios usando utils.turno_a_intervalo().
    """
    df = _leer_csv(path)
    disponibilidades: Dict[str, List[BloqueDisponibilidad]] = {}

    for _, row in df.iterrows():
        profesor_id = normalizar_texto(row["id_profesor"])
        hora_inicio, hora_fin = turno_a_intervalo(row["turno"])

        bloque = BloqueDisponibilidad(
            dia=normalizar_dia(row["dia"]),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )

        disponibilidades.setdefault(profesor_id, []).append(bloque)

    return disponibilidades


def cargar_profesores(
    profesores_path: str | Path,
    disponibilidad_path: str | Path,
) -> Dict[str, Profesor]:
    """
    Lee profesores.csv con columnas:
    id_profesor,nombre,departamento,nivel,anos_experiencia,max_escuelas,distancia_max_km
    """
    df = _leer_csv(profesores_path)
    disponibilidades = cargar_disponibilidades(disponibilidad_path)

    profesores: Dict[str, Profesor] = {}

    for _, row in df.iterrows():
        profesor_id = normalizar_texto(row["id_profesor"])

        profesor = Profesor(
            id=profesor_id,
            nombre=normalizar_texto(row["nombre"]),
            nivel=_parse_nivel(row["nivel"]),
            departamento=normalizar_departamento(row["departamento"]),
            disponibilidad=disponibilidades.get(profesor_id, []),
            anos_experiencia=int(row["anos_experiencia"]),
            max_escuelas=int(row["max_escuelas"]),
            distancia_max_km=float(str(row["distancia_max_km"]).replace(",", ".")),
        )

        profesores[profesor.id] = profesor

    return profesores


def cargar_escuelas(path: str | Path) -> Dict[str, Escuela]:
    """
    Lee escuelas.csv con columnas:
    id;nombre;zona

    Nota:
    En el modelo usamos 'departamento', pero en tu CSV la columna se llama 'zona'.
    """
    df = _leer_csv(path)

    escuelas: Dict[str, Escuela] = {}

    for _, row in df.iterrows():
        escuela = Escuela(
            id=normalizar_texto(row["id"]),
            nombre=normalizar_texto(row["nombre"]),
            departamento=normalizar_departamento(row["zona"]),
        )
        escuelas[escuela.id] = escuela

    return escuelas


def cargar_cursos(path: str | Path) -> Dict[str, Curso]:
    """
    Lee cursos.csv con columnas:
    Cursos;Escuela;Dia;Inicio;Fin
    """
    df = _leer_csv(path)

    cursos: Dict[str, Curso] = {}

    for _, row in df.iterrows():
        curso = Curso(
            id=normalizar_texto(row["Cursos"]),
            escuela_id=normalizar_texto(row["Escuela"]),
            dia=normalizar_dia(row["Dia"]),
            hora_inicio=parse_hora(row["Inicio"]),
            hora_fin=parse_hora(row["Fin"]),
        )
        cursos[curso.id] = curso

    return cursos


def cargar_dataset(data_dir: str | Path) -> ClassMatchData:
    """
    Carga el dataset completo desde data/processed.

    Espera encontrar:
    - profesores.csv
    - disponibilidad.csv
    - escuelas.csv
    - cursos.csv
    """
    data_dir = Path(data_dir)

    return ClassMatchData(
        profesores=cargar_profesores(
            data_dir / "profesores.csv",
            data_dir / "disponibilidad.csv",
        ),
        escuelas=cargar_escuelas(data_dir / "escuelas.csv"),
        cursos=cargar_cursos(data_dir / "cursos.csv"),
    )
