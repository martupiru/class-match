"""
experimento_parametros.py
Punto 9 del cronograma: barrido de parámetros del algoritmo genético.

Corre el AG con distintas combinaciones de (tamaño de población, cantidad
de generaciones), cada una repetida con varias semillas distintas (el AG
es estocástico: una sola corrida por config no alcanza para concluir
nada), y guarda todos los resultados en dos CSV para analizar después
(punto 10) con pandas/Excel, o generar gráficos con
graficos_experimentos.py:

- resultados/barrido_parametros.csv: una fila por corrida completa
  (AG, greedy o random), con el fitness final y su desglose.
- resultados/convergencia.csv: una fila por generación de cada corrida
  del AG (mínimo y promedio de fitness de la población), para poder
  graficar curvas de convergencia.

También corre el greedy y un random con el mismo presupuesto que la
config MÁS GRANDE del barrido, para tener las líneas de referencia en el
mismo archivo.

Uso:
    python -m classmatch.experimento_parametros
"""

import csv
import itertools
import time
from pathlib import Path

from classmatch.alg_genetico_model import construir_toolbox, ejecutar
from classmatch.baselines import mejor_de_n_aleatorios, resolver_greedy
from classmatch.chromosome import OrdenCursos
from classmatch.data_loader import cargar_dataset
from classmatch.fitness import evaluar

# --- Grid de configuraciones a probar ---
POBLACIONES = [20, 50, 100, 200]
GENERACIONES = [10, 30, 60, 150]
SEMILLAS = [1, 2, 3, 4, 5, 6, 7, 8]

# Corte por estancamiento deshabilitado a propósito: para el barrido nos
# interesa ver el efecto de max_generaciones tal cual, no que el AG corte
# antes por su cuenta.
GENERACIONES_SIN_MEJORA_LIMITE = 9999

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
SALIDA_CSV = RESULTADOS_DIR / "barrido_parametros.csv"
SALIDA_CONVERGENCIA_CSV = RESULTADOS_DIR / "convergencia.csv"

CAMPOS_CSV = [
    "metodo",
    "poblacion",
    "generaciones_config",
    "generaciones_ejecutadas",
    "semilla",
    "fitness_total",
    "distancia_total",
    "cursos_sin_senior",
    "seniors_fuera_disponibilidad",
    "seniors_en_conflicto",
    "juniors_fuera_disponibilidad",
    "juniors_en_conflicto",
    "cursos_con_junior",
    "duracion_seg",
]

CAMPOS_CONVERGENCIA_CSV = [
    "poblacion",
    "generaciones_config",
    "semilla",
    "generacion",
    "min_fitness",
    "avg_fitness",
]


def _fila_desde_detalle(metodo, poblacion, generaciones_config, generaciones_ejecutadas,
                         semilla, detalle, duracion):
    return {
        "metodo": metodo,
        "poblacion": poblacion,
        "generaciones_config": generaciones_config,
        "generaciones_ejecutadas": generaciones_ejecutadas,
        "semilla": semilla,
        "fitness_total": detalle.fitness_total,
        "distancia_total": detalle.distancia_total,
        "cursos_sin_senior": detalle.cursos_sin_senior,
        "seniors_fuera_disponibilidad": detalle.seniors_fuera_disponibilidad,
        "seniors_en_conflicto": detalle.seniors_en_conflicto,
        "juniors_fuera_disponibilidad": detalle.juniors_fuera_disponibilidad,
        "juniors_en_conflicto": detalle.juniors_en_conflicto,
        "cursos_con_junior": detalle.cursos_con_junior,
        "duracion_seg": round(duracion, 4),
    }


def main():
    dataset = cargar_dataset()
    orden = OrdenCursos.desde_dataset(dataset)

    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)

    combinaciones = list(itertools.product(POBLACIONES, GENERACIONES, SEMILLAS))
    total = len(combinaciones)
    print(dataset.resumen())
    print(
        f"Corriendo {total} combinaciones del AG "
        f"({len(POBLACIONES)} poblaciones x {len(GENERACIONES)} generaciones x "
        f"{len(SEMILLAS)} semillas)...\n"
    )

    filas = []
    filas_convergencia = []
    inicio_total = time.perf_counter()

    # --- Barrido del AG ---
    for i, (poblacion, generaciones, semilla) in enumerate(combinaciones, start=1):
        toolbox = construir_toolbox(dataset, orden)

        inicio = time.perf_counter()
        resultado = ejecutar(
            toolbox,
            tamano_poblacion=poblacion,
            max_generaciones=generaciones,
            generaciones_sin_mejora_limite=GENERACIONES_SIN_MEJORA_LIMITE,
            semilla=semilla,
            verbose=False,
        )
        duracion = time.perf_counter() - inicio

        mejor = resultado.hall_of_fame[0]
        detalle = evaluar(mejor, dataset, orden)

        filas.append(_fila_desde_detalle(
            "genetico", poblacion, generaciones, resultado.generaciones_ejecutadas,
            semilla, detalle, duracion,
        ))

        for registro in resultado.logbook:
            filas_convergencia.append({
                "poblacion": poblacion,
                "generaciones_config": generaciones,
                "semilla": semilla,
                "generacion": registro["gen"],
                "min_fitness": registro["min"],
                "avg_fitness": registro["avg"],
            })

        if i % 10 == 0 or i == total:
            print(
                f"[{i}/{total}] pob={poblacion:>3} gen={generaciones:>3} semilla={semilla} "
                f"-> fitness={detalle.fitness_total:>10.1f}  ({duracion:.2f}s)"
            )

    # --- Referencias: greedy y random, con el presupuesto de la config más grande ---
    poblacion_max = max(POBLACIONES)
    generaciones_max = max(GENERACIONES)
    evaluaciones_max = poblacion_max * (generaciones_max + 1)

    cromosoma_greedy = resolver_greedy(dataset, orden)
    detalle_greedy = evaluar(cromosoma_greedy, dataset, orden)
    filas.append(_fila_desde_detalle(
        "greedy", None, None, None, None, detalle_greedy, 0.0
    ))

    for semilla in SEMILLAS:
        inicio = time.perf_counter()
        resultado_random = mejor_de_n_aleatorios(
            dataset, orden, n_intentos=evaluaciones_max, semilla=semilla
        )
        duracion = time.perf_counter() - inicio
        filas.append(_fila_desde_detalle(
            "random", None, None, None, semilla, resultado_random.mejor_detalle, duracion
        ))

    with open(SALIDA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        writer.writeheader()
        writer.writerows(filas)

    with open(SALIDA_CONVERGENCIA_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_CONVERGENCIA_CSV)
        writer.writeheader()
        writer.writerows(filas_convergencia)

    duracion_total = time.perf_counter() - inicio_total
    print(
        f"\nListo. {len(filas)} filas en {SALIDA_CSV.name}, "
        f"{len(filas_convergencia)} filas en {SALIDA_CONVERGENCIA_CSV.name}. "
        f"Total: {duracion_total:.1f}s."
    )

    _imprimir_resumen(filas)
    print("\nPara los gráficos: python -m classmatch.graficos_experimentos")


def _imprimir_resumen(filas):
    """Promedio y desvío de fitness por configuración (poblacion, generaciones),
    ordenado de mejor a peor, para tener una primera lectura sin abrir el CSV."""
    import pandas as pd

    df = pd.DataFrame(filas)
    ga = df[df["metodo"] == "genetico"]

    resumen = (
        ga.groupby(["poblacion", "generaciones_config"])["fitness_total"]
        .agg(["mean", "std", "min", "max"])
        .round(1)
        .sort_values("mean")
    )

    print("\nResumen del AG por configuración (ordenado de mejor a peor fitness promedio):")
    print(resumen)

    greedy_fitness = df[df["metodo"] == "greedy"]["fitness_total"].iloc[0]
    random_fitness = df[df["metodo"] == "random"]["fitness_total"].mean()
    print(f"\nGreedy (referencia, determinístico): {greedy_fitness:.1f}")
    print(f"Random (promedio, {len(SEMILLAS)} semillas, mismo presupuesto que la config más grande): {random_fitness:.1f}")


if __name__ == "__main__":
    main()