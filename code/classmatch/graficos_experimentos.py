"""

Genera los gráficos del barrido de parámetros y de la
comparación de las 3 implementaciones (Genético, Greedy, Random), a
partir de los CSV producidos por experimento_parametros.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo guardar a archivo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
BARRIDO_CSV = RESULTADOS_DIR / "barrido_parametros.csv"
CONVERGENCIA_CSV = RESULTADOS_DIR / "convergencia.csv"
GRAFICOS_DIR = RESULTADOS_DIR / "graficos"

COLOR_GA = "#2E7D32"
COLOR_GREEDY = "#F9A825"
COLOR_RANDOM = "#C62828"


def _cargar_datos():
    barrido = pd.read_csv(BARRIDO_CSV)
    convergencia = pd.read_csv(CONVERGENCIA_CSV)
    return barrido, convergencia


# ---------------------------------------------------------------------------
# 1. Curvas de convergencia del AG, una línea por tamaño de población
# ---------------------------------------------------------------------------
def graficar_convergencia_por_poblacion(convergencia: pd.DataFrame):
    generaciones_max = convergencia["generaciones_config"].max()
    datos = convergencia[convergencia["generaciones_config"] == generaciones_max]

    fig, ax = plt.subplots(figsize=(9, 6))
    poblaciones = sorted(datos["poblacion"].unique())
    colores = plt.cm.viridis(np.linspace(0.15, 0.85, len(poblaciones)))

    for poblacion, color in zip(poblaciones, colores):
        sub = datos[datos["poblacion"] == poblacion]
        agrupado = sub.groupby("generacion")["min_fitness"].agg(["mean", "std"])
        ax.plot(
            agrupado.index, agrupado["mean"],
            label=f"población={poblacion}", color=color, linewidth=2,
        )
        ax.fill_between(
            agrupado.index,
            agrupado["mean"] - agrupado["std"].fillna(0),
            agrupado["mean"] + agrupado["std"].fillna(0),
            color=color, alpha=0.15,
        )

    ax.set_xlabel("Generación")
    ax.set_ylabel("Fitness (mínimo de la población)")
    ax.set_title(
        f"Convergencia del AG por tamaño de población\n"
        f"(config de {generaciones_max} generaciones, media ± std entre semillas)"
    )
    ax.legend(title="Población")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Heatmap: fitness promedio final por (población, generaciones)
# ---------------------------------------------------------------------------
def graficar_heatmap_parametros(barrido: pd.DataFrame):
    ga = barrido[barrido["metodo"] == "genetico"]
    tabla = ga.pivot_table(
        index="poblacion", columns="generaciones_config", values="fitness_total", aggfunc="mean"
    ).sort_index(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(tabla.values, cmap="viridis", aspect="auto")

    ax.set_xticks(range(len(tabla.columns)))
    ax.set_xticklabels(tabla.columns)
    ax.set_yticks(range(len(tabla.index)))
    ax.set_yticklabels(tabla.index)
    ax.set_xlabel("Generaciones")
    ax.set_ylabel("Población")
    ax.set_title("Fitness promedio final del AG por configuración\n(más oscuro = mejor)")

    for i in range(tabla.shape[0]):
        for j in range(tabla.shape[1]):
            valor = tabla.values[i, j]
            ax.text(
                j, i, f"{valor:.0f}", ha="center", va="center",
                color="white" if valor < tabla.values.mean() else "black", fontsize=10,
            )

    fig.colorbar(im, ax=ax, label="Fitness promedio (menor = mejor)")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Boxplots: dispersión del fitness final por población, un panel por
#    cantidad de generaciones
# ---------------------------------------------------------------------------
def graficar_boxplots_por_generaciones(barrido: pd.DataFrame):
    ga = barrido[barrido["metodo"] == "genetico"]
    generaciones = sorted(ga["generaciones_config"].unique())

    fig, axes = plt.subplots(1, len(generaciones), figsize=(4 * len(generaciones), 5), sharey=True)
    if len(generaciones) == 1:
        axes = [axes]

    for ax, gen in zip(axes, generaciones):
        sub = ga[ga["generaciones_config"] == gen]
        poblaciones = sorted(sub["poblacion"].unique())
        datos = [sub[sub["poblacion"] == p]["fitness_total"].values for p in poblaciones]
        ax.boxplot(datos, tick_labels=poblaciones)
        ax.set_title(f"{gen} generaciones")
        ax.set_xlabel("Población")
        ax.grid(alpha=0.3, axis="y")

    axes[0].set_ylabel("Fitness final")
    fig.suptitle("Dispersión del fitness final entre semillas, por configuración")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 4. Comparación final: mejor config del AG vs Greedy vs Random
# ---------------------------------------------------------------------------
def graficar_comparacion_metodos(barrido: pd.DataFrame):
    ga = barrido[barrido["metodo"] == "genetico"]
    mejor_config = (
        ga.groupby(["poblacion", "generaciones_config"])["fitness_total"].mean().idxmin()
    )
    poblacion_mejor, generaciones_mejor = int(mejor_config[0]), int(mejor_config[1])
    ga_mejor = ga[
        (ga["poblacion"] == poblacion_mejor) & (ga["generaciones_config"] == generaciones_mejor)
    ]["fitness_total"]

    greedy_valor = barrido[barrido["metodo"] == "greedy"]["fitness_total"].iloc[0]
    random_valores = barrido[barrido["metodo"] == "random"]["fitness_total"]

    nombres = [
        f"Genético\n(pob={poblacion_mejor}, gen={generaciones_mejor})",
        "Greedy",
        "Random",
    ]
    medias = [ga_mejor.mean(), greedy_valor, random_valores.mean()]
    errores = [ga_mejor.std(), 0, random_valores.std()]
    colores = [COLOR_GA, COLOR_GREEDY, COLOR_RANDOM]

    fig, ax = plt.subplots(figsize=(7, 6))
    barras = ax.bar(nombres, medias, yerr=errores, capsize=8, color=colores, alpha=0.85)
    for barra, media in zip(barras, medias):
        ax.text(
            barra.get_x() + barra.get_width() / 2, media, f"{media:.0f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold",
        )

    ax.set_ylabel("Fitness final (menor = mejor)")
    ax.set_title("Comparación de las 3 implementaciones\n(mejor config del AG, barras de error = desvío entre semillas)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 5. Métricas secundarias por método (distancia, cursos con junior, etc.)
# ---------------------------------------------------------------------------
def graficar_metricas_secundarias(barrido: pd.DataFrame):
    ga = barrido[barrido["metodo"] == "genetico"]
    mejor_config = (
        ga.groupby(["poblacion", "generaciones_config"])["fitness_total"].mean().idxmin()
    )
    poblacion_mejor, generaciones_mejor = int(mejor_config[0]), int(mejor_config[1])
    ga_mejor = ga[
        (ga["poblacion"] == poblacion_mejor) & (ga["generaciones_config"] == generaciones_mejor)
    ]
    greedy_fila = barrido[barrido["metodo"] == "greedy"]
    random_filas = barrido[barrido["metodo"] == "random"]

    metricas_conteo = [
        "seniors_en_conflicto",
        "seniors_fuera_disponibilidad",
        "juniors_en_conflicto",
        "juniors_fuera_disponibilidad",
        "cursos_con_junior",
    ]
    etiquetas_conteo = [
        "Seniors en\nconflicto",
        "Seniors fuera\ndisponibilidad",
        "Juniors en\nconflicto",
        "Juniors fuera\ndisponibilidad",
        "Cursos con\njunior",
    ]

    fig, (ax_dist, ax_conteo) = plt.subplots(1, 2, figsize=(13, 6), gridspec_kw={"width_ratios": [1, 2.5]})

    # --- Panel 1: distancia total (escala propia, en km) ---
    valores_dist = [
        ga_mejor["distancia_total"].mean(),
        greedy_fila["distancia_total"].mean(),
        random_filas["distancia_total"].mean(),
    ]
    ax_dist.bar(["Genético", "Greedy", "Random"], valores_dist,
                color=[COLOR_GA, COLOR_GREEDY, COLOR_RANDOM], alpha=0.85)
    ax_dist.set_ylabel("Distancia total (km)")
    ax_dist.set_title("Distancia total")
    ax_dist.grid(alpha=0.3, axis="y")

    # --- Panel 2: métricas de conteo (violaciones de restricciones, etc.) ---
    valores_ga = [ga_mejor[m].mean() for m in metricas_conteo]
    valores_greedy = [greedy_fila[m].mean() for m in metricas_conteo]
    valores_random = [random_filas[m].mean() for m in metricas_conteo]

    x = np.arange(len(metricas_conteo))
    ancho = 0.25
    ax_conteo.bar(x - ancho, valores_ga, ancho, label="Genético", color=COLOR_GA, alpha=0.85)
    ax_conteo.bar(x, valores_greedy, ancho, label="Greedy", color=COLOR_GREEDY, alpha=0.85)
    ax_conteo.bar(x + ancho, valores_random, ancho, label="Random", color=COLOR_RANDOM, alpha=0.85)
    ax_conteo.set_xticks(x)
    ax_conteo.set_xticklabels(etiquetas_conteo)
    ax_conteo.set_ylabel("Valor promedio")
    ax_conteo.set_title("Restricciones y cobertura de juniors")
    ax_conteo.legend()
    ax_conteo.grid(alpha=0.3, axis="y")

    fig.suptitle(
        f"Métricas secundarias por método "
        f"(AG: pob={poblacion_mejor}, gen={generaciones_mejor})"
    )
    fig.tight_layout()
    return fig


def main():
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    barrido, convergencia = _cargar_datos()

    figuras = {
        "1_convergencia_por_poblacion.png": graficar_convergencia_por_poblacion(convergencia),
        "2_heatmap_parametros.png": graficar_heatmap_parametros(barrido),
        "3_boxplots_por_generaciones.png": graficar_boxplots_por_generaciones(barrido),
        "4_comparacion_metodos.png": graficar_comparacion_metodos(barrido),
        "5_metricas_secundarias.png": graficar_metricas_secundarias(barrido),
    }

    for nombre, fig in figuras.items():
        ruta = GRAFICOS_DIR / nombre
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"Guardado: {ruta}")


if __name__ == "__main__":
    main()