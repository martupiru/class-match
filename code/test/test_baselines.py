from classmatch.baselines import mejor_de_n_aleatorios, resolver_greedy, resolver_random
from classmatch.chromosome import OrdenCursos
from classmatch.data_loader import cargar_dataset
from classmatch.fitness import evaluar


def test_resolver_random_longitud_y_ids_validos():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = resolver_random(dataset, orden)

    assert len(cromosoma) == len(dataset.cursos)
    for senior_id, junior_id in cromosoma:
        assert senior_id is None or senior_id in dataset.profesores
        assert junior_id is None or junior_id in dataset.profesores


def test_mejor_de_n_aleatorios_es_reproducible_con_semilla():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    resultado_1 = mejor_de_n_aleatorios(dataset, orden, n_intentos=20, semilla=123)
    resultado_2 = mejor_de_n_aleatorios(dataset, orden, n_intentos=20, semilla=123)

    assert resultado_1.mejor_detalle.fitness_total == resultado_2.mejor_detalle.fitness_total


def test_mejor_de_n_aleatorios_mejora_o_iguala_con_mas_intentos():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    pocos_intentos = mejor_de_n_aleatorios(dataset, orden, n_intentos=1, semilla=1)
    muchos_intentos = mejor_de_n_aleatorios(dataset, orden, n_intentos=200, semilla=1)

    assert muchos_intentos.mejor_detalle.fitness_total <= pocos_intentos.mejor_detalle.fitness_total


def test_resolver_greedy_asigna_senior_a_todos_los_cursos():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = resolver_greedy(dataset, orden)

    assert len(cromosoma) == len(dataset.cursos)
    # Hay Seniors en el dataset de prueba, así que el greedy no debería
    # dejar ningún curso sin Senior asignado.
    for senior_id, _ in cromosoma:
        assert senior_id is not None


def test_resolver_greedy_le_gana_al_random_puro():
    import random

    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    detalle_greedy = evaluar(resolver_greedy(dataset, orden), dataset, orden)

    random.seed(7)
    detalle_random = evaluar(resolver_random(dataset, orden), dataset, orden)

    assert detalle_greedy.fitness_total < detalle_random.fitness_total