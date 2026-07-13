"""
baselines.py
Algoritmos de comparación (baselines) para CLASSMATCH: random y greedy.

Sirven como punto de referencia para medir qué tan bien resuelve el
algoritmo genético el problema, comparando contra:

- Random y Greedy
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
# GREEDY (sin ningún criterio relacionado a la función de fitness)
# ---------------------------------------------------------------------------


def resolver_greedy(dataset: Dataset, orden: OrdenCursos) -> Cromosoma:
    """Greedy "a mano", con el único chequeo que cualquier scheduler real
    haría sin pensarlo (disponibilidad horaria general del profesor), pero
    sin ninguna otra optimización relacionada a fitness.py
    """
    seniors = dataset.profesores_por_nivel(NivelProfesor.SENIOR)
    juniors = dataset.profesores_por_nivel(NivelProfesor.JUNIOR)

    carga: Dict[int, int] = {p.id: 0 for p in seniors + juniors}

    def _disponibles(candidatos: List[Profesor], curso: Curso) -> List[Profesor]:
        return [
            p for p in candidatos
            if p.esta_disponible(curso.dia, curso.hora_inicio, curso.hora_fin)
        ]

    def _menos_cargado(candidatos: List[Profesor]) -> Optional[Profesor]:
        if not candidatos:
            return None
        return min(candidatos, key=lambda p: (carga[p.id], p.id))

    cromosoma: Cromosoma = []
    for i in range(len(orden)):
        curso = orden.curso_en_posicion(dataset, i)

        senior = _menos_cargado(_disponibles(seniors, curso))
        senior_id = senior.id if senior is not None else None
        if senior is not None:
            carga[senior.id] += 1

        junior = _menos_cargado(_disponibles(juniors, curso))
        junior_id = junior.id if junior is not None else None
        if junior is not None:
            carga[junior.id] += 1

        cromosoma.append((senior_id, junior_id))

    return cromosoma