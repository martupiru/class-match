from pathlib import Path
from datetime import time

from classmatch.data_loader import (
    cargar_cursos,
    cargar_dataset,
    cargar_disponibilidades,
    cargar_escuelas,
    cargar_profesores,
)
from classmatch.distance_matrix import cargar_distancias
from classmatch.models import NivelProfesor


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "processed"


def test_cargar_escuelas():
    escuelas = cargar_escuelas(DATA_DIR / "escuelas.csv")

    assert len(escuelas) == 4
    assert escuelas["E1"].nombre == "Rainbow"
    assert escuelas["E1"].departamento == "Godoy Cruz"
    assert escuelas["E3"].departamento == "Ciudad"


def test_cargar_cursos():
    cursos = cargar_cursos(DATA_DIR / "cursos.csv")

    assert len(cursos) == 22
    assert cursos["C1"].escuela_id == "E1"
    assert cursos["C1"].dia == "Sabado"
    assert cursos["C1"].hora_inicio == time(9, 0)
    assert cursos["C1"].hora_fin == time(12, 0)
    assert cursos["C7"].dia == "Miercoles"


def test_cargar_disponibilidades():
    disponibilidades = cargar_disponibilidades(DATA_DIR / "disponibilidad.csv")

    assert len(disponibilidades) == 15
    assert disponibilidades["1"][0].dia == "Lunes"
    assert disponibilidades["1"][0].hora_inicio == time(8, 0)
    assert disponibilidades["1"][0].hora_fin == time(12, 0)


def test_cargar_profesores():
    profesores = cargar_profesores(
        DATA_DIR / "profesores.csv",
        DATA_DIR / "disponibilidad.csv",
    )

    assert len(profesores) == 16
    assert profesores["1"].nombre == "Mateo Nahman"
    assert profesores["1"].nivel == NivelProfesor.JUNIOR
    assert profesores["1"].departamento == "Maipu"
    assert profesores["3"].nivel == NivelProfesor.SENIOR
    assert profesores["9"].departamento == "Ciudad"


def test_profesor_disponible_para_curso_con_dias_normalizados():
    dataset = cargar_dataset(DATA_DIR)

    profesor = dataset.profesores["1"]
    curso = dataset.cursos["C1"]

    assert curso.dia == "Sabado"
    assert profesor.esta_disponible_para(curso)


def test_cargar_dataset_completo():
    dataset = cargar_dataset(DATA_DIR)

    assert len(dataset.profesores) == 16
    assert len(dataset.escuelas) == 4
    assert len(dataset.cursos) == 22


def test_cargar_distancias():
    distancias = cargar_distancias(DATA_DIR / "distancias.csv")

    assert distancias.get("Ciudad", "Godoy Cruz") == 5.5
    assert distancias.get("Godoy Cruz", "Maipu") == 8.5
