from datetime import time

from classmatch.models import BloqueDisponibilidad, Curso, NivelProfesor, Profesor


def test_bloque_contiene_horario_completo():
    bloque = BloqueDisponibilidad("Lunes", time(8, 0), time(12, 0))

    assert bloque.contiene("Lunes", time(9, 0), time(11, 0))


def test_bloque_no_contiene_si_el_dia_es_distinto():
    bloque = BloqueDisponibilidad("Lunes", time(8, 0), time(12, 0))

    assert not bloque.contiene("Martes", time(9, 0), time(11, 0))


def test_profesor_esta_disponible_para_curso():
    curso = Curso("C1", "E1", "Lunes", time(9, 0), time(12, 0))
    profesor = Profesor(
        id="P1",
        nombre="Ana",
        nivel=NivelProfesor.SENIOR,
        departamento="Ciudad",
        disponibilidad=[
            BloqueDisponibilidad("Lunes", time(8, 0), time(13, 0)),
        ],
    )

    assert profesor.esta_disponible_para(curso)


def test_cursos_solapados():
    c1 = Curso("C1", "E1", "Sabado", time(9, 0), time(12, 0))
    c2 = Curso("C2", "E1", "Sabado", time(10, 0), time(13, 0))

    assert c1.se_solapa_con(c2)


def test_cursos_contiguos_no_solapan():
    c1 = Curso("C1", "E1", "Sabado", time(9, 0), time(12, 0))
    c2 = Curso("C2", "E1", "Sabado", time(12, 0), time(13, 0))

    assert not c1.se_solapa_con(c2)


def test_cursos_en_distinto_dia_no_solapan():
    c1 = Curso("C1", "E1", "Sabado", time(9, 0), time(12, 0))
    c2 = Curso("C2", "E1", "Viernes", time(9, 0), time(12, 0))

    assert not c1.se_solapa_con(c2)
