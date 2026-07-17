"""
Experimento de escalabilidad para CLASSMATCH.

Con la configuración del AG fija (misma población y mismas generaciones),
se hace crecer el tamaño del problema mediante datasets sintéticos y se mide
cómo escalan el tiempo de cómputo y la calidad de las soluciones de:

- Algoritmo genético
- Greedy
- Random

"""

import csv
import time
from pathlib import Path
from typing import Optional

from classmatch.alg_genetico_model import construir_toolbox, ejecutar
from classmatch.baselines import mejor_de_n_aleatorios, resolver_greedy
from classmatch.chromosome import OrdenCursos
from classmatch.data_loader import Dataset, cargar_dataset
from classmatch.fitness import evaluar
from classmatch.models import (
    BloqueDisponibilidad,
    Curso,
    Escuela,
    Profesor,
)


# ---------------------------------------------------------------------------
# Configuración fija del experimento
# ---------------------------------------------------------------------------

TAMANO_POBLACION = 100
MAX_GENERACIONES = 60

# Se usa un valor muy alto para evitar la parada anticipada y mantener el
# mismo presupuesto computacional en todas las escalas.
GENERACIONES_SIN_MEJORA_LIMITE = 9999

EVALUACIONES_PRESUPUESTO = TAMANO_POBLACION * (MAX_GENERACIONES + 1)

# Factor 1 corresponde al tamaño original del dataset.
FACTORES_ESCALA = [1, 2, 4, 8, 16, 32]

# El generador es determinista, pero se mantienen varias semillas para el AG
# y para el baseline Random (1 a 10)
SEMILLAS = list(range(1, 11))

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
SALIDA_CSV = RESULTADOS_DIR / "escalabilidad.csv"


CAMPOS_CSV = [
    "metodo",
    "factor_escala",
    "n_profesores",
    "n_escuelas",
    "n_cursos",
    "semilla",
    "fitness_total",
    "fitness_por_curso",
    "distancia_total",
    "duracion_seg",
    "violaciones_duras",
    "violaciones_duras_por_curso",
    "cursos_sin_senior",
    "seniors_fuera_disponibilidad",
    "seniors_en_conflicto",
    "juniors_fuera_disponibilidad",
    "juniors_en_conflicto",
    "cursos_con_junior",
]


# ---------------------------------------------------------------------------
# Generación del dataset sintético
# ---------------------------------------------------------------------------

def _clonar_disponibilidad(
    profesor: Profesor,
) -> list[BloqueDisponibilidad]:
    """Devuelve una copia independiente de los bloques de disponibilidad."""
    return [
        BloqueDisponibilidad(
            dia=bloque.dia,
            hora_inicio=bloque.hora_inicio,
            hora_fin=bloque.hora_fin,
        )
        for bloque in profesor.disponibilidad
    ]


def generar_dataset_sintetico(
    dataset_base: Dataset,
    factor: int,
    semilla: Optional[int] = None,
) -> Dataset:
    """Replica profesores, escuelas y cursos por el mismo factor.

    La réplica conserva:

    - proporción entre Seniors y Juniors;
    - departamentos;
    - disponibilidad horaria;
    - días y horarios de los cursos;
    - relación entre cursos y escuelas;
    - matriz de distancias original.

    La semilla se acepta para conservar la interfaz del experimento, aunque
    esta versión del generador es determinista
    """
    if factor < 1:
        raise ValueError("El factor de escala debe ser mayor o igual a 1")

    _ = semilla

    profesores_originales = sorted(
        dataset_base.profesores.values(),
        key=lambda profesor: profesor.id,
    )
    escuelas_originales = sorted(
        dataset_base.escuelas.values(),
        key=lambda escuela: str(escuela.id),
    )
    cursos_originales = list(dataset_base.cursos.values())

    profesores: dict[int, Profesor] = {}
    escuelas: dict[str, Escuela] = {}
    cursos: dict[str, Curso] = {}

    siguiente_profesor_id = 1
    siguiente_curso_numero = 1

    for replica in range(1, factor + 1):
        equivalencias_escuelas: dict[str, str] = {}

        # Replicar escuelas.
        for escuela in escuelas_originales:
            nueva_escuela_id = f"{escuela.id}_S{replica}"
            equivalencias_escuelas[str(escuela.id)] = nueva_escuela_id

            escuelas[nueva_escuela_id] = Escuela(
                id=nueva_escuela_id,
                nombre=f"{escuela.nombre} [réplica {replica}]",
                departamento=escuela.departamento,
            )

        # Replicar profesores.
        for profesor in profesores_originales:
            profesores[siguiente_profesor_id] = Profesor(
                id=siguiente_profesor_id,
                nombre=f"{profesor.nombre} [réplica {replica}]",
                nivel=profesor.nivel,
                departamento=profesor.departamento,
                disponibilidad=_clonar_disponibilidad(profesor),
            )
            siguiente_profesor_id += 1

        # Replicar cursos y asociarlos con la escuela correspondiente
        # de la misma réplica.
        for curso in cursos_originales:
            nuevo_curso_id = f"C{siguiente_curso_numero}"

            cursos[nuevo_curso_id] = Curso(
                id=nuevo_curso_id,
                escuela_id=equivalencias_escuelas[str(curso.escuela_id)],
                dia=curso.dia,
                hora_inicio=curso.hora_inicio,
                hora_fin=curso.hora_fin,
            )

            siguiente_curso_numero += 1

    return Dataset(
        profesores=profesores,
        escuelas=escuelas,
        cursos=cursos,
        distancias=dataset_base.distancias,
    )


# ---------------------------------------------------------------------------
# Construcción de filas para el CSV
# ---------------------------------------------------------------------------

def _fila(
    metodo: str,
    factor: int,
    ds: Dataset,
    semilla: int,
    detalle,
    duracion: float,
) -> dict:
    n_cursos = len(ds.cursos)

    violaciones_duras = (
        detalle.cursos_sin_senior
        + detalle.seniors_fuera_disponibilidad
        + detalle.seniors_en_conflicto
    )

    return {
        "metodo": metodo,
        "factor_escala": factor,
        "n_profesores": len(ds.profesores),
        "n_escuelas": len(ds.escuelas),
        "n_cursos": n_cursos,
        "semilla": semilla,
        "fitness_total": detalle.fitness_total,
        "fitness_por_curso": round(detalle.fitness_total / n_cursos, 3),
        "distancia_total": detalle.distancia_total,
        "duracion_seg": round(duracion, 4),
        "violaciones_duras": violaciones_duras,
        "violaciones_duras_por_curso": round(
            violaciones_duras / n_cursos,
            6,
        ),
        "cursos_sin_senior": detalle.cursos_sin_senior,
        "seniors_fuera_disponibilidad": (
            detalle.seniors_fuera_disponibilidad
        ),
        "seniors_en_conflicto": detalle.seniors_en_conflicto,
        "juniors_fuera_disponibilidad": (
            detalle.juniors_fuera_disponibilidad
        ),
        "juniors_en_conflicto": detalle.juniors_en_conflicto,
        "cursos_con_junior": detalle.cursos_con_junior,
    }


# ---------------------------------------------------------------------------
# Experimento
# ---------------------------------------------------------------------------

def main() -> None:
    dataset_base = cargar_dataset()
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

    print(
        f"Config fija del AG: población={TAMANO_POBLACION}, "
        f"generaciones={MAX_GENERACIONES} "
        f"({EVALUACIONES_PRESUPUESTO} evaluaciones de presupuesto)\n"
    )

    filas: list[dict] = []
    inicio_total = time.perf_counter()

    for factor in FACTORES_ESCALA:
        for semilla in SEMILLAS:
            ds = generar_dataset_sintetico(
                dataset_base,
                factor,
                semilla=semilla,
            )
            orden = OrdenCursos.desde_dataset(ds)

            print(
                f"factor={factor:>3} semilla={semilla}  "
                f"({len(ds.profesores)} prof, "
                f"{len(ds.escuelas)} esc, "
                f"{len(ds.cursos)} cursos)"
            )

            # -------------------------------------------------------------
            # Algoritmo genético
            # -------------------------------------------------------------
            toolbox = construir_toolbox(ds, orden)

            inicio = time.perf_counter()
            resultado = ejecutar(
                toolbox,
                tamano_poblacion=TAMANO_POBLACION,
                max_generaciones=MAX_GENERACIONES,
                generaciones_sin_mejora_limite=(
                    GENERACIONES_SIN_MEJORA_LIMITE
                ),
                semilla=semilla,
                verbose=False,
            )
            duracion_ga = time.perf_counter() - inicio

            detalle_ga = evaluar(
                resultado.hall_of_fame[0],
                ds,
                orden,
            )

            filas.append(
                _fila(
                    "genetico",
                    factor,
                    ds,
                    semilla,
                    detalle_ga,
                    duracion_ga,
                )
            )

            print(
                f"   genetico  {duracion_ga:>7.2f}s  "
                f"fitness/curso="
                f"{detalle_ga.fitness_total / len(ds.cursos):.1f}"
            )

            # -------------------------------------------------------------
            # Greedy
            # -------------------------------------------------------------
            inicio = time.perf_counter()
            cromosoma_greedy = resolver_greedy(ds, orden)
            duracion_greedy = time.perf_counter() - inicio

            detalle_greedy = evaluar(
                cromosoma_greedy,
                ds,
                orden,
            )

            filas.append(
                _fila(
                    "greedy",
                    factor,
                    ds,
                    semilla,
                    detalle_greedy,
                    duracion_greedy,
                )
            )

            print(
                f"   greedy    {duracion_greedy:>7.2f}s  "
                f"fitness/curso="
                f"{detalle_greedy.fitness_total / len(ds.cursos):.1f}"
            )

            # -------------------------------------------------------------
            # Random
            # -------------------------------------------------------------
            inicio = time.perf_counter()

            resultado_random = mejor_de_n_aleatorios(
                ds,
                orden,
                n_intentos=EVALUACIONES_PRESUPUESTO,
                semilla=semilla,
            )

            duracion_random = time.perf_counter() - inicio

            filas.append(
                _fila(
                    "random",
                    factor,
                    ds,
                    semilla,
                    resultado_random.mejor_detalle,
                    duracion_random,
                )
            )

            print(
                f"   random    {duracion_random:>7.2f}s  "
                f"fitness/curso="
                f"{resultado_random.mejor_detalle.fitness_total / len(ds.cursos):.1f}"
            )

    with SALIDA_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as archivo:
        writer = csv.DictWriter(
            archivo,
            fieldnames=CAMPOS_CSV,
        )
        writer.writeheader()
        writer.writerows(filas)

    duracion_total = time.perf_counter() - inicio_total

    print(
        f"\nListo. {len(filas)} filas en {duracion_total:.1f}s. "
        f"Resultados en: {SALIDA_CSV}"
    )
    print(
        "Para los gráficos: "
        "python -m classmatch.graficos_escalabilidad"
    )


if __name__ == "__main__":
    main()
