"""
fitness.py
Función de evaluación (fitness)

    fitness = distancia_total
            + penalizaciones_por_restricciones_incumplidas
            - recompensa_por_juniors_asignados

Es una función de MINIMIZACIÓN: menor fitness = mejor solución.

recibe un Cromosoma (lista de genes) y un Dataset, y devuelve un float. ga_engine.py lo registra en el toolbox
envuelto en una tupla (requisito de DEAP para creator.FitnessMin).
"""

from dataclasses import dataclass, field
from typing import Dict, List

from classmatch.chromosome import Cromosoma, OrdenCursos
from classmatch.data_loader import Dataset
from classmatch.models import Curso, NivelProfesor, Profesor

# Penalizaciones y recompensas (tabla del README_PASO_3.md, sección 5)
PENALIZACION_SIN_SENIOR = 1000
PENALIZACION_SENIOR_FUERA_DISPONIBILIDAD = 300
PENALIZACION_SENIOR_CONFLICTO_HORARIO = 300
PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD = 100
PENALIZACION_JUNIOR_CONFLICTO_HORARIO = 100
RECOMPENSA_JUNIOR_ASIGNADO = -20


@dataclass
class DetalleFitness:
    """Desglose del fitness para depuración y métricas """
    fitness_total: float = 0.0
    distancia_total: float = 0.0
    cursos_sin_senior: int = 0
    seniors_fuera_disponibilidad: int = 0
    seniors_en_conflicto: int = 0
    juniors_fuera_disponibilidad: int = 0
    juniors_en_conflicto: int = 0
    cursos_con_junior: int = 0


def _cursos_por_profesor(
    cromosoma: Cromosoma, orden: OrdenCursos, dataset: Dataset
) -> Dict[int, List[Curso]]:
    """Para cada profesor asignado (Senior o Junior), lista de cursos que
    le tocaron -> permite detectar conflictos de horario (mismo profesor,
    cursos incompatibles según Curso.conflictua_con)."""
    cursos_por_profesor: Dict[int, List[Curso]] = {}
    for i, (senior_id, junior_id) in enumerate(cromosoma):
        curso = orden.curso_en_posicion(dataset, i)
        for profesor_id in (senior_id, junior_id):
            if profesor_id is not None:
                cursos_por_profesor.setdefault(profesor_id, []).append(curso)
    return cursos_por_profesor


def _contar_conflictos_horario(cursos_por_profesor: Dict[int, List[Curso]]) -> Dict[int, int]:
    """Cuenta, por profesor, cuántos pares de cursos asignados están en
    conflicto entre sí (se solapan o son contiguos entre escuelas distintas)."""
    conflictos_por_profesor: Dict[int, int] = {}
    for profesor_id, cursos in cursos_por_profesor.items():
        conflictos = 0
        for i in range(len(cursos)):
            for j in range(i + 1, len(cursos)):
                if cursos[i].conflictua_con(cursos[j]):
                    conflictos += 1
        conflictos_por_profesor[profesor_id] = conflictos
    return conflictos_por_profesor


def evaluar(
    cromosoma: Cromosoma, dataset: Dataset, orden: OrdenCursos
) -> DetalleFitness:
    """Evalúa un cromosoma completo y devuelve el desglose de fitness."""
    detalle = DetalleFitness()
    cursos_por_profesor = _cursos_por_profesor(cromosoma, orden, dataset)
    conflictos_por_profesor = _contar_conflictos_horario(cursos_por_profesor)

    for i, (senior_id, junior_id) in enumerate(cromosoma):
        curso = orden.curso_en_posicion(dataset, i)

        # --- Restricción: curso debe tener Senior ---
        if senior_id is None:
            detalle.cursos_sin_senior += 1
            detalle.fitness_total += PENALIZACION_SIN_SENIOR
            continue  # sin Senior no tiene sentido seguir evaluando este gen

        senior = dataset.profesores[senior_id]

        if not senior.esta_disponible(curso.dia, curso.hora_inicio, curso.hora_fin):
            detalle.seniors_fuera_disponibilidad += 1
            detalle.fitness_total += PENALIZACION_SENIOR_FUERA_DISPONIBILIDAD

        detalle.distancia_total += dataset.distancia_profesor_curso(senior, curso)

        # --- Junior (opcional) ---
        if junior_id is not None:
            junior = dataset.profesores[junior_id]
            detalle.cursos_con_junior += 1
            detalle.fitness_total += RECOMPENSA_JUNIOR_ASIGNADO

            if not junior.esta_disponible(curso.dia, curso.hora_inicio, curso.hora_fin):
                detalle.juniors_fuera_disponibilidad += 1
                detalle.fitness_total += PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD

            detalle.distancia_total += dataset.distancia_profesor_curso(junior, curso)

    # --- Conflictos de horario (un profesor en 2 cursos incompatibles) ---
    # Se cuentan una sola vez por par en conflicto, distinguiendo si el
    # profesor actuó como Senior o Junior en ese par no es trivial porque
    # un mismo profesor podría, en teoría, aparecer con ambos roles en
    # cursos distintos; para la v1 aplicamos la penalización de Senior si
    # el profesor es Senior, y de Junior si es Junior (nivel es fijo).
    for profesor_id, n_conflictos in conflictos_por_profesor.items():
        if n_conflictos == 0:
            continue
        profesor = dataset.profesores[profesor_id]
        if profesor.es_senior():
            detalle.seniors_en_conflicto += n_conflictos
            detalle.fitness_total += PENALIZACION_SENIOR_CONFLICTO_HORARIO * n_conflictos
        else:
            detalle.juniors_en_conflicto += n_conflictos
            detalle.fitness_total += PENALIZACION_JUNIOR_CONFLICTO_HORARIO * n_conflictos

    detalle.fitness_total += detalle.distancia_total
    return detalle


def fitness_valor(cromosoma: Cromosoma, dataset: Dataset, orden: OrdenCursos) -> float:
    """Atajo que devuelve solo el valor numérico de fitness (lo que va a
    usar directamente DEAP)."""
    return evaluar(cromosoma, dataset, orden).fitness_total
