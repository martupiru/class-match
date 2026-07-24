# Proyecto Final - Algoritmo evolutivo para la asignación de horarios y escuelas 
## Integrantes: Laricchia Aida (13251) y Nahman Martina (13685)

### 1. Introducción
La asignación de docentes a cursos es una tarea que debe contemplar múltiples restricciones, como la disponibilidad horaria de los profesores, su nivel de experiencia y la ubicación geográfica de las instituciones. Cuando la cantidad de cursos y docentes aumenta, realizar esta planificación manualmente se vuelve un proceso complejo, propenso a errores y poco eficiente.

En este trabajo se aborda este problema mediante el desarrollo de CLASSMATCH, un sistema que utiliza un algoritmo genético para generar asignaciones de docentes que respeten las restricciones definidas y minimicen la distancia total recorrida por los profesores. Cada curso debe contar obligatoriamente con un docente Senior y cuando es posible, se asigna además un docente Junior, favoreciendo el acompañamiento y la capacitación dentro de la institución.

La implementación fue desarrollada en Python utilizando la biblioteca DEAP (Distributed Evolutionary Algorithms in Python), la cual proporciona herramientas para la creación de algoritmos evolutivos mediante operadores de selección, cruza y mutación.

Para construir un escenario de prueba representativo se diseñó un conjunto de datos compuesto por docentes, cursos, escuelas, disponibilidades horarias y una matriz de distancias entre departamentos de la provincia de Mendoza. Además, se realizó una encuesta a docentes con el objetivo de relevar información sobre su disponibilidad, ubicación y experiencia, permitiendo definir un caso de estudio basado en datos cercanos a una situación real.

Con el fin de evaluar el desempeño de la propuesta, el algoritmo genético fue comparado con dos algoritmos de referencia: un algoritmo Greedy y un algoritmo de asignación aleatoria (Random). La comparación se realizó mediante diferentes métricas, entre ellas la distancia total recorrida, el cumplimiento de las restricciones y el tiempo de ejecución.

### 2. Marco teórico
#### 2.1 Problemas de optimización combinatoria
Los problemas de optimización combinatoria consisten en encontrar la mejor solución posible dentro de un conjunto muy grande de alternativas. Cada solución representa una combinación distinta de decisiones y es evaluada mediante una función objetivo que determina su calidad. En la práctica, estos problemas suelen incorporar además un conjunto de restricciones que limitan las soluciones válidas, por lo que no todas las combinaciones posibles pueden considerarse aceptables.

Este tipo de problemas aparece con frecuencia en áreas como la planificación de horarios (timetabling), la asignación de recursos, la logística, el diseño de rutas, la programación de tareas y la distribución de personal. Una característica común es que el número de soluciones posibles crece de manera exponencial conforme aumenta el tamaño del problema, fenómeno conocido como explosión combinatoria. Como consecuencia, evaluar todas las alternativas mediante búsqueda exhaustiva resulta impracticable incluso para instancias de tamaño moderado.

Frente a esta dificultad, es habitual recurrir a métodos aproximados capaces de explorar eficientemente el espacio de búsqueda y obtener soluciones de buena calidad en tiempos razonables. Entre estos métodos se encuentran las metaheurísticas, dentro de las cuales los algoritmos evolutivos constituyen una de las alternativas más utilizadas.
#### 2.2 Algoritmos evolutivos
Los algoritmos evolutivos son una familia de técnicas de optimización inspiradas en los principios de la evolución biológica y la selección natural. Su funcionamiento parte de una población de soluciones candidatas que evoluciona iterativamente mediante mecanismos similares a los observados en la naturaleza, favoreciendo la supervivencia de los individuos con mayor aptitud.

En cada generación, las soluciones son evaluadas utilizando una función de aptitud (fitness), que mide qué tan adecuadamente resuelven el problema planteado. A partir de esta evaluación, los individuos con mejor desempeño tienen mayor probabilidad de participar en la generación de nuevos descendientes, mientras que otros son descartados. De esta manera, la población tiende a mejorar progresivamente a lo largo de las generaciones.

Una de las principales ventajas de los algoritmos evolutivos es que no requieren conocer propiedades matemáticas particulares de la función objetivo, como continuidad o derivabilidad. Esto permite aplicarlos sobre problemas complejos donde intervienen múltiples restricciones, funciones no lineales o espacios de búsqueda muy extensos.

Dentro de esta familia existen distintos enfoques, entre ellos los algoritmos genéticos, las estrategias evolutivas (Evolution Strategies), la programación evolutiva (Evolutionary Programming) y la programación genética (Genetic Programming). Aunque todos comparten los mismos principios generales, difieren principalmente en la forma de representar las soluciones y en los operadores utilizados durante el proceso evolutivo.
#### 2.3 Algoritmos genéticos
Los algoritmos genéticos constituyen uno de los métodos más difundidos dentro de los algoritmos evolutivos. Fueron propuestos por John Holland en la década de 1970 y se basan en la idea de simular el proceso de evolución de una población de individuos con el objetivo de encontrar soluciones cada vez mejores para un problema de optimización.

Cada individuo representa una posible solución y se codifica mediante un cromosoma, compuesto por un conjunto de genes. La interpretación de estos genes depende del problema abordado; sin embargo, todos los individuos de una población utilizan la misma representación para que puedan combinarse entre sí durante el proceso evolutivo.

El funcionamiento de un algoritmo genético puede resumirse en las siguientes etapas:
1. **Inicialización:** Se genera una población inicial de soluciones, normalmente de manera aleatoria, procurando mantener una adecuada diversidad.
2. **Evaluación**: Cada individuo es evaluado mediante una función de aptitud (fitness), que asigna un valor numérico representando la calidad de la solución.
3. **Selección:** Se eligen los individuos que participarán en la reproducción. Las soluciones con mejor fitness poseen una mayor probabilidad de ser seleccionadas, favoreciendo la transmisión de sus características a las generaciones siguientes.
4. **Cruzamiento (Crossover):** Dos individuos intercambian parte de sus genes para producir nuevos descendientes que combinan características de ambos padres.
5. **Mutación:** Se introducen pequeñas modificaciones aleatorias sobre algunos genes con el objetivo de mantener la diversidad genética de la población y evitar la convergencia prematura hacia óptimos locales.
6. **Reemplazo** Los nuevos individuos conforman la siguiente generación, repitiéndose el proceso hasta alcanzar un criterio de finalización previamente establecido.

En muchos algoritmos genéticos también se incorpora una estrategia denominada **elitismo**, que consiste en preservar una parte de las mejores soluciones encontradas en cada generación para asegurar que no se pierdan durante el proceso evolutivo. Esta técnica suele mejorar la estabilidad de la búsqueda y acelerar la convergencia hacia soluciones de mayor calidad.

Gracias a la combinación de exploración, proporcionada principalmente por la mutación y explotación, impulsada por la selección y el cruzamiento, los algoritmos genéticos logran recorrer eficientemente espacios de búsqueda muy grandes sin necesidad de evaluar todas las soluciones posibles.

#### 2.4 Justificación del algoritmo seleccionado
El problema abordado en este trabajo presenta características que dificultan la aplicación de métodos exactos de optimización. La gran cantidad de combinaciones posibles, sumada a la existencia de múltiples restricciones que deben cumplirse simultáneamente, genera un espacio de búsqueda cuyo tamaño crece rápidamente a medida que aumenta el número de docentes y cursos.

En este contexto, los algoritmos genéticos representan una alternativa adecuada debido a su capacidad para obtener soluciones de alta calidad mediante procesos de búsqueda aproximada. A diferencia de otras técnicas, permiten incorporar restricciones complejas directamente dentro de la función de evaluación y adaptarse fácilmente a modificaciones en el problema sin alterar la estructura general del algoritmo.

### 3.Diseño experimental
#### 3.1 Descripción del problema
El problema considerado consiste en asignar un conjunto de docentes a los cursos ofrecidos por distintas instituciones educativas, procurando obtener una planificación que minimice el costo total de la asignación y respete las restricciones definidas para el sistema.

Cada curso requiere obligatoriamente la presencia de un docente Senior responsable y, cuando las condiciones lo permiten, puede incorporarse además un docente Junior con el objetivo de favorecer su formación y acompañamiento pedagógico. Asimismo, las asignaciones deben respetar la disponibilidad horaria declarada por cada profesor y evitar que un mismo docente sea asignado simultáneamente a dos cursos con horarios superpuestos.

Desde el punto de vista de la optimización, cada asignación completa representa una solución candidata. El espacio de búsqueda está formado por todas las combinaciones posibles de docentes para todos los cursos, cuyo tamaño aumenta rápidamente al incrementarse la cantidad de profesores o cursos disponibles. Debido a esta explosión combinatoria, resulta poco factible evaluar exhaustivamente todas las alternativas, por lo que se optó por una estrategia basada en algoritmos genéticos.
#### 3.2 Obtención del conjunto de datos
Para evaluar el algoritmo se construyó un conjunto de datos que representa un escenario simplificado de asignación docente. La información utilizada proviene de dos fuentes principales.

Por un lado, se diseñó y distribuyó una encuesta dirigida a docentes con el propósito de relevar información relevante para el problema. Entre los datos recopilados se incluyeron el departamento de residencia, la disponibilidad horaria durante la semana y el nivel de experiencia de cada profesor (Senior o Junior). Esta información permitió construir un escenario basado en datos cercanos a una situación real.

Por otro lado, se definieron manualmente las instituciones educativas y los cursos que conforman el caso de estudio, especificando para cada curso la escuela donde se dicta, el día y turno correspondiente. Además, se elaboró una matriz de distancias entre los departamentos de la provincia de Mendoza, utilizada para estimar el costo de traslado asociado a cada asignación.

El conjunto de datos final quedó organizado en distintos archivos CSV, cada uno especializado en una parte del problema, facilitando tanto su mantenimiento como la carga automática por parte del sistema.

#### 3.3 Prepocesamiento de datos
Antes de ser utilizados por el algoritmo, los datos fueron sometidos a una etapa de procesamiento y normalización.

Las respuestas obtenidas mediante la encuesta fueron revisadas para eliminar inconsistencias y unificar criterios de escritura, especialmente en los nombres de departamentos, días de la semana y turnos horarios. Posteriormente se transformaron en archivos CSV independientes que representan docentes, disponibilidades y demás entidades del problema.

Durante la carga del sistema, estos archivos son procesados para construir las estructuras de datos utilizadas por el algoritmo genético. Esta separación entre datos originales y datos procesados facilita la reutilización del sistema con nuevos conjuntos de información sin necesidad de modificar la implementación.

#### 3.4 Representación de las soluciones
Cada individuo de la población representa una asignación completa de docentes a todos los cursos disponibles.

La representación elegida consiste en un cromosoma formado por una secuencia de genes, donde cada gen corresponde a un curso específico e indica los docentes asignados para dictarlo. De esta manera, un individuo codifica completamente una posible planificación.

Esta representación permite que los operadores de cruzamiento y mutación actúen directamente sobre las asignaciones, generando nuevas combinaciones de docentes a medida que evoluciona la población. Además, mantiene una correspondencia directa entre la estructura del cromosoma y el problema de asignación, simplificando tanto la implementación como la evaluación de cada solución.

#### 3.5 Función fitness
La calidad de cada individuo se evalúa mediante una función de fitness diseñada como un problema de minimización.

Esta función combina distintos criterios mediante una suma de costos y penalizaciones. En primer lugar, se calcula la distancia total recorrida por los docentes entre su departamento de residencia y la institución donde dictan clases. Sobre este valor se agregan penalizaciones cuando una asignación incumple alguna de las restricciones definidas para el problema, tales como incompatibilidades horarias o asignaciones fuera de la disponibilidad declarada por un docente.

Finalmente, la función incorpora una pequeña recompensa para aquellas soluciones que logran integrar docentes Junior sin afectar el cumplimiento de las restricciones principales. De esta manera, el algoritmo favorece asignaciones que no solo sean eficientes desde el punto de vista logístico, sino que también promuevan el acompañamiento entre docentes con distintos niveles de experiencia.

El diseño de esta función permite evaluar simultáneamente todos los aspectos relevantes del problema mediante un único valor numérico, utilizado por el algoritmo para comparar individuos durante el proceso evolutivo.

**Penalizaciones de la función:**
PENALIZACION_SIN_SENIOR = 1000
PENALIZACION_SENIOR_FUERA_DISPONIBILIDAD = 300
PENALIZACION_SENIOR_CONFLICTO_HORARIO = 300
PENALIZACION_JUNIOR_FUERA_DISPONIBILIDAD = 100
PENALIZACION_JUNIOR_CONFLICTO_HORARIO = 100
RECOMPENSA_JUNIOR_ASIGNADO = -20


#### 3.6 Algoritmos de referencia
Con el objetivo de analizar el desempeño del algoritmo genético, se implementaron dos algoritmos de referencia que sirven como línea base para la comparación.

El primero corresponde a un algoritmo de asignación aleatoria (Random), que genera soluciones seleccionando docentes al azar para cada curso. Aunque este enfoque no incorpora ningún criterio de optimización, resulta útil para establecer un punto de referencia mínimo sobre la calidad de las soluciones obtenidas.

El segundo algoritmo implementa una estrategia voraz (Greedy), asignando docentes siguiendo un criterio local basado en la carga horaria acumulada. Si bien este método busca construir soluciones de manera más informada que la asignación aleatoria, sus decisiones se toman considerando únicamente información local, sin evaluar el impacto global sobre la planificación completa. Además, este algoritmo fue seleccionado como línea base porque representa una estrategia similar a la utilizada habitualmente en la planificación manual de cursos, donde las asignaciones suelen realizarse priorizando la disponibilidad horaria de los docentes y la cobertura inmediata de cada curso, sin aplicar un proceso de optimización global que considere simultáneamente todas las restricciones y el costo total de la planificación. 

Ambos algoritmos fueron evaluados utilizando la misma función de fitness empleada por el algoritmo genético, permitiendo realizar comparaciones objetivas bajo idénticos criterios.

#### 3.7 Configuración algortimo genético
La implementación del algoritmo genético fue desarrollada utilizando la biblioteca DEAP, la cual proporciona una infraestructura flexible para definir individuos, operadores genéticos y mecanismos de selección.

La población inicial se genera aleatoriamente y evoluciona mediante un proceso iterativo compuesto por selección por torneo, cruzamiento en dos puntos y mutación sobre los genes del cromosoma. Además, se incorporó una estrategia de elitismo para preservar las mejores soluciones obtenidas en cada generación, evitando su pérdida durante el proceso evolutivo.

Como criterio de finalización se estableció un número máximo de generaciones junto con un mecanismo de corte por estancamiento, que interrumpe la ejecución cuando no se observan mejoras significativas en el fitness durante varias generaciones consecutivas.

#### 3.8 Experimentos realizados
Para validar el comportamiento del algoritmo se realizaron tres tipos de experimentos.

En primer lugar, se comparó el algoritmo genético con los algoritmos de referencia utilizando el mismo conjunto de datos y un presupuesto equivalente de evaluaciones.

Posteriormente, se efectuó un barrido de parámetros variando el tamaño de la población, la cantidad de generaciones y distintas semillas aleatorias. El objetivo de este experimento fue analizar la influencia de estos parámetros sobre la calidad de las soluciones obtenidas y la estabilidad del algoritmo.

Finalmente, se llevó a cabo un experimento de escalabilidad utilizando conjuntos de datos sintéticos de tamaño creciente. Este análisis permitió observar cómo evolucionan tanto el tiempo de ejecución como la calidad de las soluciones a medida que aumenta la complejidad del problema.

#### 3.9 Métricas de evaluación
La evaluación de los algoritmos se realizó utilizando como principal indicador el valor de la función de fitness, ya que esta resume en un único valor la calidad de cada solución considerando simultáneamente todos los objetivos y restricciones del problema.

La función de fitness combina la distancia total recorrida por los docentes con un conjunto de penalizaciones asociadas al incumplimiento de restricciones, como asignaciones fuera de la disponibilidad horaria, conflictos de horarios o incumplimiento de los requisitos de experiencia. Asimismo, incorpora una recompensa cuando la asignación incluye docentes Junior acompañados por un docente Senior, promoviendo el objetivo de capacitación planteado para el problema.

De esta manera, un menor valor de fitness representa una mejor solución, ya que implica una planificación con menores costos de traslado y un mayor grado de cumplimiento de las restricciones establecidas.

Además del fitness, durante los experimentos también se registró el tiempo de ejecución de cada algoritmo, permitiendo comparar no solo la calidad de las soluciones obtenidas sino también la eficiencia computacional de cada enfoque.

Finalmente, los resultados del algoritmo genético fueron comparados con los obtenidos mediante los algoritmos de referencia Random y Greedy, analizando la evolución del fitness y el valor final alcanzado en cada caso.

#### 3.10 Resultados
##### 3.10.1 Barrido de parámetros
![2_heatmap_parametros](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos/2_heatmap_parametros.png)
*Figura 1: Fitness promedio final del AG (8 semillas) para cada combinación de población y generaciones evaluada.*


![4_comparacion_metodos](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos/4_comparacion_metodos.png)
*Figura 2: Fitness final del algoritmo genético (mejor configuración), Greedy y Random. Las barras de error representan el desvío entre semillas*

![5_metricas_secundarias](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos/5_metricas_secundarias.png)
*Figura 3: Distancia total recorrida y cumplimiento de restricciones (conflictos horarios, disponibilidad, cobertura de Junior) para cada método*

##### 3.10.2 Experimento de escalabilidad
![02_fitness_por_curso](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos_escalabilidad/02_fitness_por_curso.png)
*Figura 4: Fitness promedio por curso en función de la cantidad de cursos del dataset sintético (factores de escala 1 a 32), para el algoritmo genético (población=100, generaciones=60 fijos), Greedy y Random. Barras de error: desvío entre 10 semillas*

![03_violaciones_por_curso](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos_escalabilidad/03_violaciones_por_curso.png)
*Figura 5: Violaciones obligatorias promedio por curso (cursos sin Senior, Seniors fuera de disponibilidad y Seniors en conflicto horario) en función de la cantidad de cursos, para los tres métodos*

![04_composicion_violaciones](https://github.com/martupiru/class-match/blob/main/code/resultados/graficos_escalabilidad/04_composicion_violaciones.png)
*Figura 6: Composición del total de violaciones por tipo, en la escala máxima evaluada (704 cursos), para cada método*

### 4.Análisis de resultados

///acá se hará el análisis de los resultados
