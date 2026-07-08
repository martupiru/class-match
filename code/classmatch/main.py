from classmatch.data_loader import cargar_dataset
from classmatch.chromosome import OrdenCursos, decodificar
from classmatch.fitness import evaluar
from classmatch.alg_genetico_model import construir_toolbox, ejecutar


def main():
    dataset = cargar_dataset()
    print(dataset.resumen())

    orden = OrdenCursos.desde_dataset(dataset)

    toolbox = construir_toolbox(dataset, orden)

    resultado = ejecutar(
        toolbox,
        tamano_poblacion=20,
        max_generaciones=10,
        generaciones_sin_mejora_limite=5,
        semilla=42,
        verbose=True,
    )

    mejor = resultado.hall_of_fame[0]
    detalle = evaluar(mejor, dataset, orden)
    asignaciones = decodificar(mejor, dataset, orden)

    print("\nMejor solución:")
    print("Fitness:", detalle.fitness_total)
    print("Distancia total:", detalle.distancia_total)
    print("Cursos sin senior:", detalle.cursos_sin_senior)
    print("Seniors fuera disponibilidad:", detalle.seniors_fuera_disponibilidad)
    print("Seniors en conflicto:", detalle.seniors_en_conflicto)
    print("Juniors fuera disponibilidad:", detalle.juniors_fuera_disponibilidad)
    print("Juniors en conflicto:", detalle.juniors_en_conflicto)
    print("Cursos con junior:", detalle.cursos_con_junior)

    print("\nAsignaciones:")
    for curso_id, gen in asignaciones.items():
        senior_id, junior_id = gen
        print(f"Curso {curso_id}: Senior={senior_id}, Junior={junior_id}")


if __name__ == "__main__":
    main()