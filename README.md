# CLASS-MATCH: Algoritmo evolutivo para la asignación de profesores a cursos

Proyecto realizado para la materia de Inteligencia Artificial 

Integrantes: Laricchia Aida y Nahman Martina

---

El objetivo de este proyecto es implementar un algoritmo evolutivo, utilizando el framework **DEAP**, que asigne profesores a los cursos de una red de escuelas/talleres minimizando las distancias de traslado y respetando la disponibilidad horaria y el nivel de experiencia de cada docente. En particular, se exige que todo curso tenga un profesor **Senior** a cargo, y que los profesores **Junior** solo puedan dictar clases acompañados de un Senior.

Cada individuo (cromosoma) representa una asignación completa: un gen por curso, con el par `(senior_id, junior_id)` asignado a ese curso. La calidad de una asignación se mide con una función de fitness que suma la distancia total recorrida por los profesores y penaliza el incumplimiento de restricciones (cursos sin Senior, profesores fuera de su disponibilidad horaria, conflictos de horario entre cursos de un mismo profesor), premiando levemente la incorporación de Juniors.

El algoritmo genético se compara contra dos algoritmos de referencia (baselines):
- **Random**: mejor solución entre N asignaciones generadas al azar.
- **Greedy**: asigna a cada curso el profesor disponible con menor carga horaria actual.

---

## Requisitos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <https://github.com/martupiru/class-match>
   cd code
   ```
2. Crear y activar un entorno virtual:
   ```bash
   python -m venv env
   env\Scripts\activate      # Windows
   source env/bin/activate   # Linux/Mac
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para correr el algoritmo genético sobre el dataset real y ver el resultado en consola:
```bash
python -m classmatch.main
```
Esto carga el dataset desde `data/processed/`, ejecuta el algoritmo genético y muestra en pantalla el resumen del dataset, el detalle del fitness de la mejor solución encontrada (distancia total, cursos sin Senior, conflictos de horario, etc.) y las asignaciones finales por curso.

Otros scripts disponibles:

- **Comparación contra baselines** (una corrida, mismo presupuesto de evaluaciones):
  ```bash
  python -m classmatch.comp_baselines
  ```
- **Barrido de parámetros** (población × generaciones × semillas), guarda resultados en `resultados/`:
  ```bash
  python -m classmatch.experimento_parametros
  python -m classmatch.graficos_experimentos
  ```
- **Experimento de escalabilidad** (crece el tamaño del problema con datasets sintéticos y mide tiempo/calidad):
  ```bash
  python -m classmatch.scalability
  python -m classmatch.graf_scalability
  ```

Para correr la suite de tests:
```bash
pytest
```

## Estructura del proyecto

- `classmatch/main.py`: punto de entrada; carga el dataset, corre el algoritmo genético y muestra la mejor solución.
- `classmatch/models.py`: entidades de dominio (`Profesor`, `Escuela`, `Curso`, `BloqueDisponibilidad`) y reglas de negocio (disponibilidad, conflictos de horario).
- `classmatch/data_loader.py`: lee los CSV de `data/processed/` y construye el `Dataset` central usado por el resto del sistema.
- `classmatch/distance_matrix.py`: carga y consulta la matriz de distancias entre departamentos.
- `classmatch/chromosome.py`: representación del individuo (cromosoma), generación de individuos aleatorios y decodificación a asignaciones.
- `classmatch/fitness.py`: función de evaluación (distancia + penalizaciones por restricciones incumplidas).
- `classmatch/alg_genetico_model.py`: integración con DEAP (selección por torneo, cruce en dos puntos, mutación por gen, elitismo, corte por estancamiento).
- `classmatch/baselines.py`: algoritmos de comparación Random y Greedy.
- `classmatch/comp_baselines.py`: corre y compara AG vs. Random vs. Greedy con el mismo presupuesto de evaluaciones.
- `classmatch/experimento_parametros.py` / `graficos_experimentos.py`: barrido de parámetros del AG y generación de gráficos de convergencia y comparación.
- `classmatch/scalability.py` / `graf_scalability.py`: experimento de escalabilidad con datasets sintéticos de tamaño creciente.
- `classmatch/utils.py`: funciones auxiliares de parseo y normalización de datos.
- `data/raw/`: planillas originales (respuestas de encuesta a profesores, datos de escuelas/cursos/distancias).
- `data/processed/`: CSV canónicos que consume el sistema (`profesores.csv`, `disponibilidad.csv`, `escuelas.csv`, `cursos.csv`, `distancias.csv`).
- `resultados/`: CSV y gráficos generados por los experimentos de parámetros y escalabilidad.
- `test/`: suite de tests unitarios (pytest) para modelos, carga de datos, cromosomas, fitness, baselines y escalabilidad.

## Documentación

La documentación completa del proyecto, explicación de los algoritmos, parámetros utilizados, análisis de resultados y posibles mejoras, se encuentra en el archivo [proyecto_final.md](proyecto_final.md)