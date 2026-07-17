"""
Integración con DEAP para CLASSMATCH.

- Representación: lista de genes (senior_id, junior_id) por curso.
- Selección: torneo, tamaño 3.
- Cruzamiento: dos puntos, prob. 0.8.
- Mutación: por gen (4 acciones posibles), prob. individuo 0.2, prob. gen 0.1.
- Reemplazo: elitismo (2 individuos).
- Parada: máx. 100 generaciones o 20 generaciones sin mejora.

"""

import random
from dataclasses import dataclass
from typing import Optional

from deap import base, creator, tools

from classmatch.chromosome import (
    Cromosoma,
    OrdenCursos,
    generar_cromosoma_aleatorio,
)
from classmatch.data_loader import Dataset
from classmatch.fitness import fitness_valor
from classmatch.models import NivelProfesor

# --- Parámetros iniciales ---
TAMANO_POBLACION = 100
MAX_GENERACIONES = 100
TAMANO_TORNEO = 3
PROB_CRUZAMIENTO = 0.8
PROB_MUTACION_INDIVIDUO = 0.2
PROB_MUTACION_GEN = 0.1
CANTIDAD_ELITES = 2
GENERACIONES_SIN_MEJORA_LIMITE = 20


def _registrar_creators():
    """DEAP `creator.create` falla si se llama dos veces con el mismo
    nombre (ej. al correr tests repetidamente en el mismo proceso). Se
    protege con hasattr para que este módulo sea importable/reejecutable
    sin efectos secundarios molestos."""
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)


def _mutar_individuo(individuo, dataset: Dataset, indpb: float):
    """Mutación por gen: para cada curso, con probabilidad indpb, aplica
    una de las 4 acciones definidas:
    cambiar Senior, cambiar Junior, agregar Junior, quitar Junior"""
    seniors = dataset.profesores_por_nivel(NivelProfesor.SENIOR)
    juniors = dataset.profesores_por_nivel(NivelProfesor.JUNIOR)

    for i in range(len(individuo)):
        if random.random() >= indpb:
            continue
        senior_id, junior_id = individuo[i]
        acciones_posibles = ["cambiar_senior", "quitar_junior"]
        if junior_id is not None:
            acciones_posibles.append("cambiar_junior")
        else:
            acciones_posibles.append("agregar_junior")
        accion = random.choice(acciones_posibles)

        if accion == "cambiar_senior" and seniors:
            senior_id = random.choice(seniors).id
        elif accion == "cambiar_junior" and juniors:
            junior_id = random.choice(juniors).id
        elif accion == "agregar_junior" and juniors:
            junior_id = random.choice(juniors).id
        elif accion == "quitar_junior":
            junior_id = None

        individuo[i] = (senior_id, junior_id)

    return (individuo,)


def construir_toolbox(dataset: Dataset, orden: OrdenCursos) -> base.Toolbox:
    """Arma el toolbox de DEAP registrando todos los operadores según el
    diseño conceptual"""
    _registrar_creators()
    toolbox = base.Toolbox()

    toolbox.register(
        "individual",
        tools.initIterate,
        creator.Individual,
        lambda: generar_cromosoma_aleatorio(dataset, orden),
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register(
        "evaluate",
        lambda ind: (fitness_valor(ind, dataset, orden),),
    )
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register(
        "mutate", _mutar_individuo, dataset=dataset, indpb=PROB_MUTACION_GEN
    )
    toolbox.register("select", tools.selTournament, tournsize=TAMANO_TORNEO)

    return toolbox


@dataclass
class ResultadoGA:
    poblacion_final: list
    hall_of_fame: tools.HallOfFame
    logbook: tools.Logbook
    generaciones_ejecutadas: int


def ejecutar(
    toolbox: base.Toolbox,
    tamano_poblacion: int = TAMANO_POBLACION,
    max_generaciones: int = MAX_GENERACIONES,
    prob_cruzamiento: float = PROB_CRUZAMIENTO,
    prob_mutacion_individuo: float = PROB_MUTACION_INDIVIDUO,
    cantidad_elites: int = CANTIDAD_ELITES,
    generaciones_sin_mejora_limite: int = GENERACIONES_SIN_MEJORA_LIMITE,
    semilla: Optional[int] = None,
    verbose: bool = True,
) -> ResultadoGA:
    """Ciclo evolutivo generacional con elitismo explicito.

    No se usa algorithms.eaSimple de DEAP porque no soporta elitismo
    nativo. Se implementa un loop manual, estándar en la literatura de AGs: selección + cruce + mutación sobre
    (pop - elites), y los elites se copian directo a la siguiente
    generación sin modificar
    """
    if semilla is not None:
        random.seed(semilla)

    poblacion = toolbox.population(n=tamano_poblacion)

    fitnesses = map(toolbox.evaluate, poblacion)
    for ind, fit in zip(poblacion, fitnesses):
        ind.fitness.values = fit

    hof = tools.HallOfFame(cantidad_elites)
    hof.update(poblacion)

    stats = tools.Statistics(lambda ind: ind.fitness.values[0])
    stats.register("min", min)
    stats.register("avg", lambda xs: sum(xs) / len(xs))
    logbook = tools.Logbook()
    logbook.header = ["gen", "min", "avg"]

    mejor_historico = min(ind.fitness.values[0] for ind in poblacion)
    generaciones_sin_mejora = 0
    generacion = 0

    record = stats.compile(poblacion)
    logbook.record(gen=generacion, **record)
    if verbose:
        print(logbook.stream)

    for generacion in range(1, max_generaciones + 1):
        elites = list(map(toolbox.clone, tools.selBest(poblacion, cantidad_elites)))

        descendencia = toolbox.select(poblacion, tamano_poblacion - cantidad_elites)
        descendencia = list(map(toolbox.clone, descendencia))

        for hijo1, hijo2 in zip(descendencia[::2], descendencia[1::2]):
            if random.random() < prob_cruzamiento:
                toolbox.mate(hijo1, hijo2)
                del hijo1.fitness.values
                del hijo2.fitness.values

        for mutante in descendencia:
            if random.random() < prob_mutacion_individuo:
                toolbox.mutate(mutante)
                del mutante.fitness.values

        invalidos = [ind for ind in descendencia if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalidos)
        for ind, fit in zip(invalidos, fitnesses):
            ind.fitness.values = fit

        poblacion[:] = descendencia + elites
        hof.update(poblacion)

        record = stats.compile(poblacion)
        logbook.record(gen=generacion, **record)
        if verbose:
            print(logbook.stream)

        mejor_actual = min(ind.fitness.values[0] for ind in poblacion)
        if mejor_actual < mejor_historico:
            mejor_historico = mejor_actual
            generaciones_sin_mejora = 0
        else:
            generaciones_sin_mejora += 1

        if generaciones_sin_mejora >= generaciones_sin_mejora_limite:
            if verbose:
                print(
                    f"Parada anticipada: {generaciones_sin_mejora} "
                    f"generaciones sin mejora (límite={generaciones_sin_mejora_limite})"
                )
            break

    return ResultadoGA(
        poblacion_final=poblacion,
        hall_of_fame=hof,
        logbook=logbook,
        generaciones_ejecutadas=generacion,
    )
