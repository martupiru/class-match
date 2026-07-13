"""
comparar_baselines.py
Corre el algoritmo genetico, el greedy y el random sobre el mismo dataset
y con la misma semilla y compara los resultados en una tabla.

Uso:
    python -m classmatch.comparar_baselines
"""

from classmatch.alg_genetico_model import construir_toolbox, ejecutar
from classmatch.baselines import mejor_de_n_aleatorios, resolver_greedy
from classmatch.chromosome import OrdenCursos
from classmatch.data_loader import cargar_dataset
from classmatch.fitness import evaluar

# Misma config que main.py
TAMANO_POBLACION = 20
MAX_GENERACIONES = 10
SEMILLA = 42


def _imprimir_fila(nombre: str, detalle, extra: str = ""):
    print(
        f"{nombre:<12} fitness={detalle.fitness_total:>10.1f}  "
        f"distancia={detalle.distancia_total:>7.1f}  "
        f"sin_senior={detalle.cursos_sin_senior:>2}  "
        f"conflictos_sr={detalle.seniors_en_conflicto:>2}  "
        f"sr_fuera_disp={detalle.seniors_fuera_disponibilidad:>2}  "
        f"jr_fuera_disp={detalle.juniors_fuera_disponibilidad:>2}  "
        f"con_junior={detalle.cursos_con_junior:>2}"
        f"{extra}"
    )


def main():
    dataset = cargar_dataset()
    print(dataset.resumen())
    orden = OrdenCursos.desde_dataset(dataset)

    # --- Genético ---
    toolbox = construir_toolbox(dataset, orden)
    resultado_ga = ejecutar(
        toolbox,
        tamano_poblacion=TAMANO_POBLACION,
        max_generaciones=MAX_GENERACIONES,
        generaciones_sin_mejora_limite=5,
        semilla=SEMILLA,
        verbose=False,
    )
    mejor_ga = resultado_ga.hall_of_fame[0]
    detalle_ga = evaluar(mejor_ga, dataset, orden)
    evaluaciones_ga = TAMANO_POBLACION * (resultado_ga.generaciones_ejecutadas + 1)

    # --- Random (mismo presupuesto de evaluaciones que el AG) ---
    resultado_random = mejor_de_n_aleatorios(
        dataset, orden, n_intentos=evaluaciones_ga, semilla=SEMILLA
    )

    # --- Greedy ---
    cromosoma_greedy= resolver_greedy(dataset, orden)
    detalle_greedy = evaluar(cromosoma_greedy, dataset, orden)

    print(f"\nComparación (presupuesto = {evaluaciones_ga} evaluaciones para GA y random):\n")
    _imprimir_fila("Genético", detalle_ga, f"  ({resultado_ga.generaciones_ejecutadas} gen.)")
    _imprimir_fila(
    "Greedy",
    detalle_greedy,
    "  (solo disponibilidad)"
    )
    _imprimir_fila(
        "Random", resultado_random.mejor_detalle, f"  ({resultado_random.intentos} intentos)"
    )


if __name__ == "__main__":
    main()