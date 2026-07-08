"""
chromosome.py
Representación del individuo (cromosoma) para CLASSMATCH

Cada individuo es una lista de genes, un gen por curso, en el mismo orden
en que los cursos están cargados en el Dataset. Cada gen es una tupla
(senior_id, junior_id) donde junior_id puede ser None.

"""

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from classmatch.data_loader import Dataset
from classmatch.models import Curso, NivelProfesor, Profesor
from classmatch.utils import extraer_numero_id

Gen = Tuple[int, Optional[int]]  # (senior_id, junior_id_o_None)
Cromosoma = List[Gen]


@dataclass
class OrdenCursos:
    """Fija el orden curso <-> posición del cromosoma, una sola vez por
    Dataset, para que todo el resto del código (fitness, mutación, etc.)
    use siempre el mismo mapeo índice -> curso."""
    curso_ids: List[str]  # curso_ids[i] = id del curso en la posición i

    @classmethod
    def desde_dataset(cls, dataset: Dataset) -> "OrdenCursos":
        # Los ids son strings tipo "C1", "C10", "C2"; se ordenan por su
        # parte numérica para que queden en orden natural (C1, C2, ..., C22)
        # en vez del orden lexicográfico por defecto.
        return cls(curso_ids=sorted(dataset.cursos.keys(), key=extraer_numero_id))

    def curso_en_posicion(self, dataset: Dataset, posicion: int) -> Curso:
        return dataset.cursos[self.curso_ids[posicion]]

    def __len__(self) -> int:
        return len(self.curso_ids)


def generar_gen_aleatorio(
    curso: Curso,
    seniors: List[Profesor],
    juniors: List[Profesor],
    prob_incluir_junior: float = 0.7,
    priorizar_disponibilidad: bool = True,
) -> Gen:
    """Genera un gen (senior_id, junior_id) para un curso dado.

    Si `priorizar_disponibilidad` es True, intenta elegir entre los
    profesores que SÍ están disponibles para ese horario (mejora la
    calidad de la población inicial). Si ninguno está disponible, elige
    de todos modos al azar entre todos —individuos inválidos son
    aceptables, el fitness los penaliza
    """

    def elegir(candidatos: List[Profesor]) -> Optional[Profesor]:
        if not candidatos:
            return None
        if priorizar_disponibilidad:
            disponibles = [
                p for p in candidatos
                if p.esta_disponible(curso.dia, curso.hora_inicio, curso.hora_fin)
            ]
            if disponibles:
                return random.choice(disponibles)
        return random.choice(candidatos)

    senior = elegir(seniors)
    senior_id = senior.id if senior is not None else None

    junior_id = None
    if random.random() < prob_incluir_junior:
        junior = elegir(juniors)
        junior_id = junior.id if junior is not None else None

    return (senior_id, junior_id)


def generar_cromosoma_aleatorio(
    dataset: Dataset,
    orden: OrdenCursos,
    prob_incluir_junior: float = 0.7,
    priorizar_disponibilidad: bool = True,
) -> Cromosoma:
    """Genera un individuo completo: un gen aleatorio por cada curso."""
    seniors = dataset.profesores_por_nivel(NivelProfesor.SENIOR)
    juniors = dataset.profesores_por_nivel(NivelProfesor.JUNIOR)

    return [
        generar_gen_aleatorio(
            curso=orden.curso_en_posicion(dataset, i),
            seniors=seniors,
            juniors=juniors,
            prob_incluir_junior=prob_incluir_junior,
            priorizar_disponibilidad=priorizar_disponibilidad,
        )
        for i in range(len(orden))
    ]


def decodificar(
    cromosoma: Cromosoma, dataset: Dataset, orden: OrdenCursos
) -> Dict[int, Gen]:
    """Convierte el cromosoma (genotipo, lista posicional) en un diccionario
    {curso_id: (senior_id, junior_id)} (fenotipo, más fácil de interpretar
    para reportes o depuración)."""
    return {
        orden.curso_ids[i]: gen
        for i, gen in enumerate(cromosoma)
    }