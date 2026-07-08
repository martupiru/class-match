# CLASSMATCH
Proyecto "class match" - Laricchia Aida y Nahman Martina

# Diseño conceptual del algoritmo y selección de parámetros iniciales

## Objetivo de esta etapa

Esta etapa corresponde al punto 3 del plan de actividades del proyecto CLASSMATCH:

> Diseño conceptual del algoritmo y selección de parámetros iniciales.  
> Determinar los operadores genéticos, criterios de selección y otros parámetros importantes del algoritmo evolutivo.

El objetivo de este documento es justificar, a nivel conceptual, cómo se modelará el algoritmo genético que será utilizado para resolver el problema de asignación de profesores a cursos en distintas escuelas.

En esta etapa no se implementa todavía el algoritmo completo en DEAP. Primero se definen las decisiones principales de diseño: representación del individuo, función de fitness, operadores genéticos, estrategia de selección, reemplazo, condición de parada y parámetros iniciales.

---

## 1. Justificación del uso de un algoritmo genético

El problema CLASSMATCH consiste en asignar profesores a cursos considerando restricciones horarias, disponibilidad, niveles docentes y distancia aproximada entre departamentos. A medida que aumenta la cantidad de cursos, profesores y escuelas, la cantidad de combinaciones posibles crece rápidamente.

Por este motivo, se propone utilizar un algoritmo genético, ya que este tipo de técnica permite trabajar con poblaciones de soluciones candidatas y mejorarlas progresivamente a través de selección, cruzamiento y mutación.

Sabemos que los algoritmos genéticos son técnicas de búsqueda local inspiradas en la selección natural y la evolución de las especies. Estos algoritmos parten de una población inicial, evalúan la aptitud de los individuos mediante una función de fitness, seleccionan los más aptos y generan nuevas soluciones mediante operadores evolutivos.

En CLASSMATCH cada individuo representa una asignación completa de profesores a cursos. El algoritmo busca mejorar esas asignaciones para cumplir las restricciones obligatorias y optimizar los objetivos deseados.

---

## 2. Representación del individuo

Cada individuo de la población representa una solución completa al problema.

Como cada curso requiere exactamente un profesor Senior y opcionalmente un profesor Junior, se define que cada gen del cromosoma representa la asignación de profesores para un curso.

La estructura conceptual de un gen será:

```text
(senior_id, junior_id)
```

Donde:

- `senior_id` identifica al profesor Senior asignado al curso.
- `junior_id` identifica al profesor Junior asignado al curso y puede tomar el valor `None` cuando el curso no tiene Junior asignado.

Ejemplo de individuo:

```text
[
  ("P1", "P11"),
  ("P3", None),
  ("P5", "P14"),
  ("P2", "P12")
]
```

En este ejemplo el primer curso tiene asignado al Senior `P1` y al Junior `P11`, el segundo curso tiene solamente Senior y así sucesivamente.

Si el dataset tiene 22 cursos, entonces cada individuo tendrá 22 genes. El orden de los genes coincide con el orden de los cursos cargados desde el dataset.

Esta representación se elige porque es directa y fácil de interpretar: cada posición del cromosoma corresponde a una decisión concreta de asignación.

---

## 3. Genotipo y fenotipo

El genotipo es la representación interna que manipula el algoritmo genético. En CLASSMATCH, el genotipo será una lista de pares `(senior_id, junior_id)`.

El fenotipo es la interpretación real de ese genotipo dentro del problema. La asignación concreta de profesores a cursos considerando escuela, día, horario, disponibilidad y distancia.

Ejemplo:

```text
Genotipo:
("P1", "P11")

Fenotipo:
Curso C1, dictado en la Escuela E1, asignado al Senior P1 y al Junior P11.
```

Esta distinción es importante porque el algoritmo modifica el genotipo, pero la calidad de la solución se evalúa observando el fenotipo.

---

## 4. Población inicial

La población inicial estará formada por individuos generados aleatoriamente.

Para cada curso se seleccionará:

1. un profesor Senior al azar
2. opcionalmente, un profesor Junior al azar o `None` en caso de que no se asigne Junior.

Para mejorar la calidad inicial de las soluciones, la generación puede priorizar profesores que estén disponibles para el día y horario del curso. Sin embargo, se permitirá que existan individuos con conflictos, ya que la función de fitness será la encargada de penalizar las soluciones inválidas.

Esta decisión permite mantener diversidad en la población sin exigir que todos los individuos iniciales sean perfectamente válidos.

---

## 5. Función de fitness

La función de fitness mide la calidad de cada individuo.

En CLASSMATCH, la función de fitness debe contemplar:

1. cumplimiento de restricciones obligatorias
2. minimización de distancia total
3. maximización de cursos con Junior asignado.

Se propone utilizar una función de minimización. Por lo tanto, una solución será mejor cuanto **menor** sea su valor de fitness.

La estructura conceptual será:

```text
fitness = distancia_total
        + penalizaciones_por_restricciones_incumplidas
        - recompensa_por_juniors_asignados
```

Las restricciones obligatorias tendrán penalizaciones altas, porque una solución que incumple disponibilidad o solapamientos no debería considerarse buena aunque tenga poca distancia.

Penalizaciones iniciales propuestas:

| Situación | Penalización |
|---|---:|
| Curso sin profesor Senior | +10000 |
| Profesor Senior fuera de disponibilidad | +9000 |
| Profesor Senior asignado a cursos simultáneos | +9000 |
| Profesor Junior fuera de disponibilidad | +3000 |
| Profesor Junior asignado a cursos simultáneos | +3000 |
| Junior asignado correctamente | -300 |

La distancia total se calcula a partir de la matriz de distancias entre departamentos. Para cada asignación se suma la distancia entre el departamento de residencia del profesor y el departamento de la escuela donde se dicta el curso.

---

## 6. Selección de padres

Se utilizará selección por torneo.

En este método se eligen `k` individuos al azar de la población y se selecciona el mejor de ese grupo según su fitness. Esta estrategia es simple, eficiente y permite controlar la presión selectiva modificando el tamaño del torneo.

Parámetro inicial propuesto:

```text
Tipo de selección: torneo
Tamaño del torneo: 3
```

Se elige torneo de tamaño 3 porque representa un equilibrio inicial: favorece a los mejores individuos, pero sin eliminar demasiado rápido la diversidad de la población.

---

## 7. Operador de cruzamiento

Se utilizará cruzamiento de dos puntos.

Este operador toma dos individuos padres, selecciona dos posiciones del cromosoma e intercambia el segmento comprendido entre esos puntos.

Ejemplo conceptual:

```text
Padre A:
[A1, A2, A3, A4, A5, A6]

Padre B:
[B1, B2, B3, B4, B5, B6]

Cruce entre posiciones 2 y 4:

Hijo 1:
[A1, A2, B3, B4, A5, A6]

Hijo 2:
[B1, B2, A3, A4, B5, B6]
```

En CLASSMATCH, cada gen representa la asignación de un curso. Por lo tanto, el cruzamiento permite combinar bloques de asignaciones provenientes de distintos padres.

Parámetro inicial propuesto:

```text
Probabilidad de cruzamiento: 0.8
```

Se elige una probabilidad alta porque el cruzamiento será el principal mecanismo para combinar asignaciones parciales buenas.

---

## 8. Operador de mutación

La mutación introduce variabilidad en la población y ayuda a evitar que el algoritmo quede atrapado en óptimos locales.

En CLASSMATCH, la mutación se aplicará sobre genes individuales. Para un curso determinado, la mutación podrá realizar alguna de estas acciones:

1. cambiar el profesor Senior asignado
2. cambiar el profesor Junior asignado
3. agregar un Junior si el curso no tenía
4. quitar el Junior asignado.

Parámetros iniciales propuestos:

```text
Probabilidad de mutación del individuo: 0.2
Probabilidad de mutación por gen: 0.1
```

Esto significa que no todos los individuos mutarán en cada generación y cuando un individuo mute solo algunos genes serán modificados.

---

## 9. Reemplazo y elitismo

Para formar la siguiente generación se utilizará elitismo.

El elitismo consiste en conservar una pequeña cantidad de los mejores individuos de la generación actual y copiarlos directamente a la siguiente generación. Esto evita perder la mejor solución encontrada por efecto del cruzamiento o de la mutación.

Parámetro inicial propuesto:

```text
Cantidad de individuos élite: 2
```

Se elige un número bajo de élites para conservar buenas soluciones sin reducir demasiado la diversidad de la población.

---

## 10. Condición de parada

El algoritmo se detendrá cuando se alcance una cantidad máxima de generaciones o cuando no se observe mejora durante varias generaciones consecutivas.

Parámetros iniciales propuestos:

```text
Cantidad máxima de generaciones: 100
Parada anticipada: 20 generaciones sin mejora
```

La cantidad fija de generaciones permite controlar el tiempo de ejecución mientras que la parada anticipada evita continuar ejecutando el algoritmo cuando la población ya no mejora significativamente.

---

## 11. Parámetros iniciales propuestos

| Parámetro | Valor inicial |
|---|---:|
| Tamaño de población | 100 individuos |
| Cantidad máxima de generaciones | 100 |
| Selección | Torneo |
| Tamaño del torneo | 3 |
| Cruzamiento | Dos puntos |
| Probabilidad de cruzamiento | 0.8 |
| Mutación | Cambio aleatorio de asignaciones |
| Probabilidad de mutación del individuo | 0.2 |
| Probabilidad de mutación por gen | 0.1 |
| Reemplazo | Elitismo |
| Cantidad de élites | 2 |
| Criterio principal | Minimizar fitness |
| Parada anticipada | 20 generaciones sin mejora |

Estos valores serán utilizados como configuración inicial. En etapas posteriores podrán ajustarse experimentalmente comparando la calidad de las soluciones obtenidas, el tiempo de ejecución y la estabilidad del algoritmo.

---

## 12. Métricas a registrar

Durante la ejecución del algoritmo se registrarán métricas para analizar su comportamiento:

| Métrica | Objetivo |
|---|---|
| Mejor fitness por generación | Observar la mejora de la mejor solución |
| Fitness promedio por generación | Analizar la evolución general de la población |
| Distancia total de la mejor solución | Evaluar el objetivo de minimización de traslados |
| Cantidad de cursos con Junior | Medir el cumplimiento del objetivo secundario |
| Cantidad de conflictos horarios | Controlar restricciones obligatorias |
| Cantidad de asignaciones fuera de disponibilidad | Controlar factibilidad |
| Tiempo de ejecución | Comparar configuraciones |

Estas métricas permitirán evaluar si el algoritmo mejora con el paso de las generaciones y si logra encontrar soluciones válidas.

---

## 13. Consideración sobre optimización multiobjetivo

El problema CLASSMATCH tiene más de un objetivo: minimizar distancias, maximizar la cantidad de Juniors asignados y cumplir restricciones. En una versión avanzada, podría abordarse como un problema multiobjetivo utilizando enfoques como Pareto o NSGA-II.

Sin embargo, para la primera implementación se utilizará una función de fitness compuesta con penalizaciones y recompensas. Esta decisión reduce la complejidad inicial del proyecto y permite construir una primera versión funcional del algoritmo.

Una vez obtenida una versión base, se podrá evaluar la posibilidad de implementar una variante multiobjetivo.

---

## 14. Decisión final de diseño

Para la primera versión de CLASSMATCH se implementará un algoritmo genético clásico con:

- representación directa por curso
- selección por torneo
- cruzamiento de dos puntos
- mutación por gen
- función fitness de minimización con penalizaciones
- elitismo
- parada por cantidad de generaciones y por ausencia de mejora

---
