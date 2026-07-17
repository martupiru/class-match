"""
Lee los CSV canónicos de data/processed/ y construye un objeto `Dataset`
central: diccionarios {id: objeto} para profesores/escuelas/cursos, más la
matriz de distancias
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
from classmatch.utils import (
    extraer_numero_id,
    hora_entera_a_time,
    normalizar_departamento,
    normalizar_dia,
    turno_a_horario,
)

import pandas as pd

from classmatch.distance_matrix import DistanceMatrix, cargar_distancias
from classmatch.models import (
    BloqueDisponibilidad,
    Curso,
    Escuela,
    NivelProfesor,
    Profesor,
)

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


@dataclass
class Dataset:
    """Repositorio central: todo lo que el algoritmo necesita para operar"""
    profesores: Dict[int, Profesor]
    escuelas: Dict[str, Escuela]
    cursos: Dict[str, Curso]
    distancias: DistanceMatrix  # departamentos ya en su forma canónica

    def profesores_por_nivel(self, nivel: NivelProfesor) -> List[Profesor]:
        return [p for p in self.profesores.values() if p.nivel == nivel]

    def distancia(self, depto_a: str, depto_b: str) -> float:
        return self.distancias.get(depto_a, depto_b)

    def distancia_profesor_curso(self, profesor: Profesor, curso: Curso) -> float:
        escuela = self.escuelas[curso.escuela_id]
        return self.distancia(profesor.departamento, escuela.departamento)

    def resumen(self) -> str:
        n_senior = len(self.profesores_por_nivel(NivelProfesor.SENIOR))
        n_junior = len(self.profesores_por_nivel(NivelProfesor.JUNIOR))
        return (
            f"Dataset: {len(self.profesores)} profesores "
            f"({n_senior} Senior, {n_junior} Junior), "
            f"{len(self.escuelas)} escuelas, {len(self.cursos)} cursos, "
            f"{len(self.distancias.departamentos())} departamentos"
        )


def _parsear_nivel(valor: str) -> NivelProfesor:
    """Convierte el texto de la columna 'nivel' de profesores.csv al Enum
    NivelProfesor"""
    texto = valor.strip()
    for candidato in (texto, texto.upper(), texto.capitalize(), texto.lower()):
        try:
            return NivelProfesor(candidato)
        except ValueError:
            continue
    valores_validos = [n.value for n in NivelProfesor]
    raise ValueError(
        f"Nivel de profesor no reconocido: '{valor}'. Valores válidos: {valores_validos}"
    )


def cargar_dataset(processed_dir: Path = PROCESSED_DIR) -> Dataset:
    profesores_df = pd.read_csv(processed_dir / "profesores.csv")
    disponibilidad_df = pd.read_csv(processed_dir / "disponibilidad.csv")
    escuelas_df = pd.read_csv(processed_dir / "escuelas.csv", sep=";")
    cursos_df = pd.read_csv(processed_dir / "cursos.csv", sep=";")
    distancias = cargar_distancias(processed_dir / "distancias.csv")

    disponibilidad_por_profesor: Dict[int, List[BloqueDisponibilidad]] = {}
    for _, fila in disponibilidad_df.iterrows():
        id_profesor = int(fila["id_profesor"])

        hora_inicio, hora_fin = turno_a_horario(fila["turno"])

        bloque = BloqueDisponibilidad(
            dia=normalizar_dia(fila["dia"]),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )

        disponibilidad_por_profesor.setdefault(id_profesor, []).append(bloque)

    profesores = {
        int(fila["id_profesor"]): Profesor(
            id=int(fila["id_profesor"]),
            nombre=fila["nombre"],
            nivel=_parsear_nivel(fila["nivel"]),
            departamento=normalizar_departamento(fila["departamento"]),
            disponibilidad=disponibilidad_por_profesor.get(int(fila["id_profesor"]), []),
        )
        for _, fila in profesores_df.iterrows()
    }

    escuelas = {
        str(fila["id"]): Escuela(
            id=str(fila["id"]),
            nombre=fila["nombre"],
            departamento=normalizar_departamento(fila["zona"]),
        )
        for _, fila in escuelas_df.iterrows()
    }

    cursos = {
        str(fila["Cursos"]): Curso(
            id=str(fila["Cursos"]),
            escuela_id=str(fila["Escuela"]),
            dia=normalizar_dia(fila["Dia"]),
            hora_inicio=hora_entera_a_time(fila["Inicio"]),
            hora_fin=hora_entera_a_time(fila["Fin"]),
        )
        for _, fila in cursos_df.iterrows()
    }

    return Dataset(
        profesores=profesores, escuelas=escuelas, cursos=cursos, distancias=distancias
    )


if __name__ == "__main__":
    ds = cargar_dataset()
    print(ds.resumen())