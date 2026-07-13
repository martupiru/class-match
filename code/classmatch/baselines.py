"""
baselines.py
Algoritmos de comparación (baselines) para CLASSMATCH: random y greedy.

Sirven como punto de referencia para medir qué tan bien resuelve el
algoritmo genético el problema, comparando contra:

- Random: soluciones generadas completamente al azar, sin ninguna
  heurística
- Greedy: Recorre los cursos uno por unoy para cada uno asigna al profesor de MENOR COSTO usando exactamente
  las mismas penalizaciones que fitness.py (distancia + disponibilidad +
  conflictos de horario). Es el "baseline serio": una solución razonable
  sin búsqueda poblacional, para ver cuánto aporta realmente el AG
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from classmatch.chromosome import Cromosoma, Gen, OrdenCursos
from classmatch.data_loader import Dataset
from classmatch.fitness import (
    DetalleFitness,
    PENALIZACION_JUNIOR_CONFLICTO_HORARIO,
    PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD,
    PENALIZACION_SENIOR_CONFLICTO_HORARIO,
    PENALIZACION_SENIOR_FUERA_DISPONIBILIDAD,
    RECOMPENSA_JUNIOR_ASIGNADO,
    evaluar,
)
from classmatch.models import Curso, NivelProfesor, Profesor

# ---------------------------------------------------------------------------
# RANDOM
# ---------------------------------------------------------------------------


def _gen_aleatorio_puro(
    curso: Curso, seniors: List[Profesor], juniors: List[Profesor]
) -> Gen:
    """Gen totalmente al azar: no mira disponibilidad ni conflictos, a
    diferencia de generar_gen_aleatorio() (usado para poblar el AG, que sí
    intenta priorizar disponibilidad). Es el "peor caso" honesto contra el
    que se compara el algoritmo genético."""
    senior = random.choice(seniors) if seniors else None
    junior = random.choice(juniors) if juniors and random.random() < 0.5 else None
    return (senior.id if senior else None, junior.id if junior else None)


def resolver_random(dataset: Dataset, orden: OrdenCursos) -> Cromosoma:
    """Una única solución completamente al azar"""
    seniors = dataset.profesores_por_nivel(NivelProfesor.SENIOR)
    juniors = dataset.profesores_por_nivel(NivelProfesor.JUNIOR)
    return [
        _gen_aleatorio_puro(orden.curso_en_posicion(dataset, i), seniors, juniors)
        for i in range(len(orden))
    ]


@dataclass
class ResultadoRandom:
    mejor_cromosoma: Cromosoma
    mejor_detalle: DetalleFitness
    intentos: int


def mejor_de_n_aleatorios(
    dataset: Dataset,
    orden: OrdenCursos,
    n_intentos: int,
    semilla: Optional[int] = None,
) -> ResultadoRandom:
    """Genera `n_intentos` soluciones al azar y devuelve la mejor.

    Para que la comparación contra el AG sea justa en "presupuesto
    computacional", conviene usar n_intentos = tamano_poblacion *
    (generaciones_ejecutadas + 1), es decir, la misma cantidad de
    evaluaciones de fitness que hizo el AG.
    """
    if semilla is not None:
        random.seed(semilla)

    mejor_cromosoma: Optional[Cromosoma] = None
    mejor_detalle: Optional[DetalleFitness] = None

    for _ in range(n_intentos):
        cromosoma = resolver_random(dataset, orden)
        detalle = evaluar(cromosoma, dataset, orden)
        if mejor_detalle is None or detalle.fitness_total < mejor_detalle.fitness_total:
            mejor_cromosoma = cromosoma
            mejor_detalle = detalle

    return ResultadoRandom(
        mejor_cromosoma=mejor_cromosoma, mejor_detalle=mejor_detalle, intentos=n_intentos
    )


# ---------------------------------------------------------------------------
# GREEDY
# ---------------------------------------------------------------------------

# Estado local del greedy: profesor_id -> cursos que ya se le asignaron
# en ESTA solución (se va llenando a medida que se construye, a diferencia
# del AG que evalúa conflictos recién al final sobre el cromosoma completo).
EstadoAsignaciones = Dict[int, List[Curso]]


def _tiene_conflicto(profesor_id: int, curso: Curso, asignados: EstadoAsignaciones) -> bool:
    return any(curso.conflictua_con(otro) for otro in asignados.get(profesor_id, []))


def _costo_candidato(
    profesor: Profesor,
    curso: Curso,
    dataset: Dataset,
    asignados: EstadoAsignaciones,
    penalizacion_disponibilidad: float,
    penalizacion_conflicto: float,
) -> float:
    """Costo de asignar a `profesor` a `curso`, con las MISMAS
    penalizaciones que usa fitness.py, para que el greedy optimice
    localmente la misma función objetivo que el AG optimiza globalmente."""
    costo = dataset.distancia_profesor_curso(profesor, curso)

    if not profesor.esta_disponible(curso.dia, curso.hora_inicio, curso.hora_fin):
        costo += penalizacion_disponibilidad

    if _tiene_conflicto(profesor.id, curso, asignados):
        costo += penalizacion_conflicto

    return costo


def _elegir_mejor(
    candidatos: List[Profesor],
    curso: Curso,
    dataset: Dataset,
    asignados: EstadoAsignaciones,
    penalizacion_disponibilidad: float,
    penalizacion_conflicto: float,
) -> Optional[Profesor]:
    if not candidatos:
        return None
    return min(
        candidatos,
        key=lambda p: _costo_candidato(
            p, curso, dataset, asignados, penalizacion_disponibilidad, penalizacion_conflicto
        ),
    )


def resolver_greedy(dataset: Dataset, orden: OrdenCursos) -> Cromosoma:
    """Heurística constructiva golosa: recorre los cursos en orden y, para
    cada uno, asigna primero el Senior de menor costo. Después evalúa si
    conviene sumarle un Junior: lo asigna solo si el beneficio neto
    (recompensa por asignar Junior menos el costo que agrega) es
    positivo, igual que premia/castiga el fitness del AG.
    """
    seniors = dataset.profesores_por_nivel(NivelProfesor.SENIOR)
    juniors = dataset.profesores_por_nivel(NivelProfesor.JUNIOR)
    asignados: EstadoAsignaciones = {}

    cromosoma: Cromosoma = []

    for i in range(len(orden)):
        curso = orden.curso_en_posicion(dataset, i)

        senior = _elegir_mejor(
            seniors,
            curso,
            dataset,
            asignados,
            PENALIZACION_SENIOR_FUERA_DISPONIBILIDAD,
            PENALIZACION_SENIOR_CONFLICTO_HORARIO,
        )
        senior_id = senior.id if senior is not None else None
        if senior is not None:
            asignados.setdefault(senior.id, []).append(curso)

        junior_id = None
        mejor_junior = _elegir_mejor(
            juniors,
            curso,
            dataset,
            asignados,
            PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD,
            PENALIZACION_JUNIOR_CONFLICTO_HORARIO,
        )
        if mejor_junior is not None:
            costo_junior = _costo_candidato(
                mejor_junior,
                curso,
                dataset,
                asignados,
                PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD,
                PENALIZACION_JUNIOR_CONFLICTO_HORARIO,
            )
            beneficio_neto = costo_junior + RECOMPENSA_JUNIOR_ASIGNADO
            if beneficio_neto < 0:
                junior_id = mejor_junior.id
                asignados.setdefault(mejor_junior.id, []).append(curso)

        cromosoma.append((senior_id, junior_id))

    return cromosoma