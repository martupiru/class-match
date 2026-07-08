from classmatch.data_loader import cargar_dataset


def test_cargar_dataset():
    dataset = cargar_dataset()

    assert dataset is not None
    assert hasattr(dataset, "profesores")
    assert hasattr(dataset, "escuelas")
    assert hasattr(dataset, "cursos")

    assert len(dataset.profesores) > 0
    assert len(dataset.escuelas) > 0
    assert len(dataset.cursos) > 0