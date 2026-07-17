from classmatch.chromosome import OrdenCursos
from classmatch.data_loader import cargar_dataset
from classmatch.scalability import ScalabilityConfig, run_experiment, scale_dataset, summarize


def test_scale_dataset_preserves_proportions_and_references():
    base = cargar_dataset()
    scaled = scale_dataset(base, 3)

    assert len(scaled.profesores) == 3 * len(base.profesores)
    assert len(scaled.escuelas) == 3 * len(base.escuelas)
    assert len(scaled.cursos) == 3 * len(base.cursos)
    assert all(course.escuela_id in scaled.escuelas for course in scaled.cursos.values())
    assert len(OrdenCursos.desde_dataset(scaled)) == len(scaled.cursos)

    base_seniors = sum(p.es_senior() for p in base.profesores.values())
    scaled_seniors = sum(p.es_senior() for p in scaled.profesores.values())
    assert scaled_seniors == 3 * base_seniors


def test_small_scalability_experiment_produces_all_methods():
    base = cargar_dataset()
    config = ScalabilityConfig(
        factors=(1,),
        seeds=(7,),
        population=4,
        generations=1,
        include_random=True,
    )
    records = run_experiment(base, config)
    assert {record.method for record in records} == {"Genetico", "Greedy", "Random"}
    assert all(record.courses == len(base.cursos) for record in records)
    assert len(summarize(records)) == 3
