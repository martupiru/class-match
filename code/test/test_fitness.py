from classmatch.data_loader import cargar_dataset
from classmatch.chromosome import OrdenCursos, generar_cromosoma_aleatorio
from classmatch.fitness import evaluar, fitness_valor


def test_fitness_devuelve_numero():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = generar_cromosoma_aleatorio(dataset, orden)

    valor = fitness_valor(cromosoma, dataset, orden)

    assert isinstance(valor, float)
    assert valor >= 0 or valor < 0


def test_evaluar_devuelve_detalle():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = generar_cromosoma_aleatorio(dataset, orden)
    detalle = evaluar(cromosoma, dataset, orden)

    assert hasattr(detalle, "fitness_total")
    assert hasattr(detalle, "distancia_total")
    assert hasattr(detalle, "cursos_sin_senior")