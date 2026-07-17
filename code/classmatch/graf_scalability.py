"""
Genera los gráficos del experimento de escalabilidad, a partir de
resultados/escalabilidad.csv (producido por experimento_escalabilidad.py).

No vuelve a correr nada: solo lee el CSV y grafica. Si cambiaste los
factores de escala o las semillas, corré antes:
    python -m classmatch.experimento_escalabilidad

Uso:
    python -m classmatch.graficos_escalabilidad
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sin ventana: solo guardar a archivo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTADOS_DIR = Path(__file__).resolve().parent.parent / "resultados"
ESCALABILIDAD_CSV = RESULTADOS_DIR / "escalabilidad.csv"
GRAFICOS_DIR = RESULTADOS_DIR / "graficos"

COLOR_GA = "#2E7D32"
COLOR_GREEDY = "#F9A825"
COLOR_RANDOM = "#C62828"
COLORES_METODO = {"genetico": COLOR_GA, "greedy": COLOR_GREEDY, "random": COLOR_RANDOM}
ETIQUETAS_METODO = {"genetico": "Genético", "greedy": "Greedy", "random": "Random"}
METODOS = ["genetico", "greedy", "random"]


def _cargar_datos() -> pd.DataFrame:
    return pd.read_csv(ESCALABILIDAD_CSV)


# ---------------------------------------------------------------------------
# 1. Tiempo de ejecución vs tamaño del problema (log-log), con la
#    pendiente estimada (orden polinómico aproximado) por método
# ---------------------------------------------------------------------------
def graficar_tiempo_vs_tamano(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 7))

    for metodo in METODOS:
        sub = df[df["metodo"] == metodo]
        agrupado = sub.groupby("n_cursos")["duracion_seg"].agg(["mean", "std"]).reset_index()
        # Evitamos duraciones 0 (greedy a escala chica puede redondear a
        # 0.0000s) para que el log-log no rompa; les ponemos un piso chico.
        medias = agrupado["mean"].clip(lower=1e-4)

        ax.plot(
            agrupado["n_cursos"], medias, "o-",
            label=ETIQUETAS_METODO[metodo], color=COLORES_METODO[metodo], linewidth=2,
        )

        # Pendiente en log-log = orden polinómico aproximado (tiempo ~ n^pendiente)
        log_n = np.log(agrupado["n_cursos"])
        log_t = np.log(medias)
        pendiente, _ = np.polyfit(log_n, log_t, 1)
        ax.annotate(
            f"{ETIQUETAS_METODO[metodo]}: pendiente ≈ {pendiente:.2f}",
            xy=(agrupado["n_cursos"].iloc[-1], medias.iloc[-1]),
            xytext=(5, 0), textcoords="offset points",
            color=COLORES_METODO[metodo], fontsize=9, fontweight="bold",
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Cantidad de cursos (tamaño del problema, escala log)")
    ax.set_ylabel("Tiempo de ejecución (s, escala log)")
    ax.set_title(
        "Tiempo de ejecución vs. tamaño del problema\n"
        "(presupuesto de evaluaciones fijo; pendiente ≈ orden de crecimiento)"
    )
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 2. Calidad de la solución (fitness por curso) vs tamaño del problema
# ---------------------------------------------------------------------------
def graficar_calidad_vs_tamano(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))

    for metodo in METODOS:
        sub = df[df["metodo"] == metodo]
        agrupado = sub.groupby("n_cursos")["fitness_por_curso"].agg(["mean", "std"]).reset_index()
        ax.errorbar(
            agrupado["n_cursos"], agrupado["mean"], yerr=agrupado["std"].fillna(0),
            marker="o", capsize=4, label=ETIQUETAS_METODO[metodo],
            color=COLORES_METODO[metodo], linewidth=2,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Cantidad de cursos (tamaño del problema, escala log)")
    ax.set_ylabel("Fitness promedio por curso (menor = mejor)")
    ax.set_title(
        "Calidad de la solución vs. tamaño del problema\n"
        "(con presupuesto de evaluaciones FIJO en todas las escalas)"
    )
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 3. Boxplots: distribución del TIEMPO por factor de escala, un panel
#    por método (mismo eje Y en los 3, para comparar de un vistazo)
# ---------------------------------------------------------------------------
def graficar_boxplots_tiempo(df: pd.DataFrame):
    factores = sorted(df["factor_escala"].unique())

    fig, axes = plt.subplots(1, len(METODOS), figsize=(5 * len(METODOS), 5.5), sharey=False)

    for ax, metodo in zip(axes, METODOS):
        sub = df[df["metodo"] == metodo]
        datos = [sub[sub["factor_escala"] == f]["duracion_seg"].values for f in factores]
        caja = ax.boxplot(datos, tick_labels=factores, patch_artist=True)
        for parche in caja["boxes"]:
            parche.set_facecolor(COLORES_METODO[metodo])
            parche.set_alpha(0.6)
        ax.set_title(ETIQUETAS_METODO[metodo])
        ax.set_xlabel("Factor de escala")
        ax.grid(alpha=0.3, axis="y")

    axes[0].set_ylabel("Tiempo de ejecución (s)")
    fig.suptitle("Dispersión del tiempo de ejecución entre semillas, por tamaño de problema")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 4. Boxplots: distribución del FITNESS POR CURSO por factor de escala,
#    un panel por método
# ---------------------------------------------------------------------------
def graficar_boxplots_calidad(df: pd.DataFrame):
    factores = sorted(df["factor_escala"].unique())

    fig, axes = plt.subplots(1, len(METODOS), figsize=(5 * len(METODOS), 5.5), sharey=True)

    for ax, metodo in zip(axes, METODOS):
        sub = df[df["metodo"] == metodo]
        datos = [sub[sub["factor_escala"] == f]["fitness_por_curso"].values for f in factores]
        caja = ax.boxplot(datos, tick_labels=factores, patch_artist=True)
        for parche in caja["boxes"]:
            parche.set_facecolor(COLORES_METODO[metodo])
            parche.set_alpha(0.6)
        ax.set_title(ETIQUETAS_METODO[metodo])
        ax.set_xlabel("Factor de escala")
        ax.grid(alpha=0.3, axis="y")

    axes[0].set_ylabel("Fitness por curso (menor = mejor)")
    fig.suptitle("Dispersión de la calidad de solución entre semillas, por tamaño de problema")
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# 5. Boxplot del TIEMPO por factor de escala, UNO POR MÉTODO Y POR
#    ARCHIVO (a diferencia del gráfico 3, que junta los 3 paneles en una
#    sola imagen): cada método con su propia escala, pensados para
#    mostrarse/exportarse por separado.
# ---------------------------------------------------------------------------
def graficar_boxplot_tiempo_individual(df: pd.DataFrame, metodo: str):
    factores = sorted(df["factor_escala"].unique())
    sub = df[df["metodo"] == metodo]
    datos = [sub[sub["factor_escala"] == f]["duracion_seg"].values for f in factores]

    fig, ax = plt.subplots(figsize=(7, 6))
    caja = ax.boxplot(datos, tick_labels=factores, patch_artist=True, widths=0.6)
    for parche in caja["boxes"]:
        parche.set_facecolor(COLORES_METODO[metodo])
        parche.set_alpha(0.7)
    for mediana in caja["medians"]:
        mediana.set_color("black")

    ax.set_xlabel("Factor de escala")
    ax.set_ylabel("Tiempo de ejecución (s)")
    ax.set_title(f"Tiempo de ejecución — {ETIQUETAS_METODO[metodo]}\n(cajas y bigotes, escala propia)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    return fig


def main():
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    df = _cargar_datos()

    figuras = {
        "6_tiempo_vs_tamano_loglog.png": graficar_tiempo_vs_tamano(df),
        "7_calidad_vs_tamano.png": graficar_calidad_vs_tamano(df),
        "8_boxplots_tiempo_por_factor.png": graficar_boxplots_tiempo(df),
        "9_boxplots_calidad_por_factor.png": graficar_boxplots_calidad(df),
        "10_boxplot_tiempo_genetico.png": graficar_boxplot_tiempo_individual(df, "genetico"),
        "11_boxplot_tiempo_greedy.png": graficar_boxplot_tiempo_individual(df, "greedy"),
        "12_boxplot_tiempo_random.png": graficar_boxplot_tiempo_individual(df, "random"),
    }

    for nombre, fig in figuras.items():
        ruta = GRAFICOS_DIR / nombre
        fig.savefig(ruta, dpi=150)
        plt.close(fig)
        print(f"Guardado: {ruta}")


if __name__ == "__main__":
    main()