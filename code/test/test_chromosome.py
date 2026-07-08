from classmatch.data_loader import cargar_dataset
from classmatch.chromosome import OrdenCursos, generar_cromosoma_aleatorio, decodificar


def test_generar_cromosoma_aleatorio():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = generar_cromosoma_aleatorio(dataset, orden)

    assert len(cromosoma) == len(dataset.cursos)

    for senior_id, junior_id in cromosoma:
        assert senior_id is None or senior_id in dataset.profesores
        assert junior_id is None or junior_id in dataset.profesores


def test_decodificar_cromosoma():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    cromosoma = generar_cromosoma_aleatorio(dataset, orden)
    asignaciones = decodificar(cromosoma, dataset, orden)

    assert len(asignaciones) == len(dataset.cursos)
    assert set(asignaciones.keys()) == set(dataset.cursos.keys())