"""Figuras del informe/presentación. Siguen las guías de formato de la cátedra:
- ejes con leyendas en PALABRAS y unidades SI (mm, mm/s) entre paréntesis (GuiaPresentaciones 1.8);
- tamaño de fuente grande (≥ 20) similar al del texto de la diapositiva (1.8);
- datos promedio marcados con símbolo y barra de error; las rectas solo como guía para el ojo (2.4.6);
- escala logarítmica cuando los datos abarcan varios órdenes de magnitud (2.4.7);
- una sola figura con curvas de colores para comparar (corrección recurrente de Parisi).

Las cantidades con potencias se escriben como superíndice (mm$^{-1}$), no como 1/mm ni 1E-2 (1.9).
Reciben observables ya calculados (ver observables.py) y guardan cada figura a un archivo.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # backend sin display (corridas headless)
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, MaxNLocator

CONTACT_DENSITY = 1.0 / 44.0  # mm^-1, densidad de contacto del VDV (largo 44 mm)
FONTSIZE = 20                 # guía 1.8: al menos 20
FIGSIZE = (9, 6)


def _coma(x) -> str:
    """Número con coma decimal (convención en español), sin decimales ni notación científica de más."""
    return f"{x:g}".replace(".", ",")


# Rótulos de eje con coma decimal, para que las figuras usen la misma convención que el texto del
# informe (no hay locale español en este TeX Live/Python; se formatea a mano).
_COMA_FMT = FuncFormatter(lambda x, _pos: _coma(x))


def _coma_ejes(ax, y: bool = True) -> None:
    """Aplica coma decimal a los rótulos de los ejes (x siempre; y salvo que sea logarítmico)."""
    ax.xaxis.set_major_formatter(_COMA_FMT)
    if y:
        ax.yaxis.set_major_formatter(_COMA_FMT)


def configure(base_fontsize: int = FONTSIZE) -> None:
    """Configura matplotlib con tipografía grande y legible (guía 1.8: fuente ≥ 20)."""
    plt.rcParams.update({
        "font.size": base_fontsize,
        "axes.labelsize": base_fontsize,
        "axes.titlesize": base_fontsize,
        "xtick.labelsize": base_fontsize - 2,
        "ytick.labelsize": base_fontsize - 2,
        "legend.fontsize": base_fontsize - 2,
        "figure.dpi": 120,
        "savefig.bbox": "tight",
    })


def _curve_label(key) -> str:
    if isinstance(key, (int, float)):
        return f"p = {_coma(key)}"
    return str(key)


def plot_mean_speed_vs_n(results_by_p, outfile, legend_title: str = "frenado aleatorio") -> None:
    """Velocidad media vs N, una curva por p (≈ Fig. 2 del artículo). Datos marcados con símbolo y
    barra de error; la recta que los une es solo guía para el ojo (2.4.6).

    ``results_by_p``: dict ``p/etiqueta -> (N, media, error)`` con arreglos del mismo largo."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for p in sorted(results_by_p):
        n, mean, err = results_by_p[p]
        ax.errorbar(n, mean, yerr=err, marker="o", capsize=4, label=_curve_label(p))
    ax.set_xlabel("número de vehículos")
    ax.set_ylabel("velocidad media (mm/s)")
    ax.legend(title=legend_title)
    _coma_ejes(ax)
    fig.savefig(outfile)
    plt.close(fig)


def plot_density_pdf(pdfs_by_n, outfile) -> None:
    """PDF de densidades, una curva por N (≈ Fig. 3). ``pdfs_by_n``: dict ``N -> (centros, pdf)``."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for n in sorted(pdfs_by_n):
        centros, pdf = pdfs_by_n[n]
        ax.plot(centros, pdf, label=f"N = {n}")
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1.5, label="contacto: 1/(44 mm)")
    ax.set_xlabel("densidad (mm$^{-1}$)")
    ax.set_ylabel("densidad de probabilidad")
    ax.set_yscale("log")  # 2.4.7: varios órdenes de magnitud
    # Leyenda FUERA del área de datos (el pico de densidad está a la derecha; una leyenda interna
    # taparía la curva). bbox='tight' en configure() la incluye al guardar.
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=FONTSIZE - 5)
    _coma_ejes(ax, y=False)  # el eje y es logarítmico: dejar el formateador de potencias
    fig.savefig(outfile)
    plt.close(fig)


def plot_velocity_pdf(pdfs_by_n, outfile) -> None:
    """PDF de velocidades, una curva por N (≈ Fig. 4). ``pdfs_by_n``: dict ``N -> (centros, pdf)``."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for n in sorted(pdfs_by_n):
        centros, pdf = pdfs_by_n[n]
        ax.plot(centros, pdf, label=f"N = {n}")
    ax.set_xlabel("velocidad (mm/s)")
    ax.set_ylabel("densidad de probabilidad")
    # Leyenda fuera del área de datos, igual que en la PDF de densidad (evita tapar los picos).
    ax.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=FONTSIZE - 5)
    _coma_ejes(ax)
    fig.savefig(outfile)
    plt.close(fig)


def plot_time_evolution(curves, outfile) -> None:
    """Evolución temporal de la velocidad media (regla 4 de la cátedra: respaldo visual para elegir el
    corte del estacionario por inspección). ``curves``: dict ``etiqueta -> (tiempo_s, serie, corte_s)``
    con el tiempo en segundos; ``corte_s`` puede ser None. Marca el corte sugerido con línea vertical."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for label, (t_s, serie, cut) in curves.items():
        line, = ax.plot(t_s, serie, label=label)
        if cut is not None:
            ax.axvline(cut, ls=":", lw=1.5, color=line.get_color())
    ax.set_xlabel("tiempo (s)")
    ax.set_ylabel("velocidad media (mm/s)")
    ax.legend()
    _coma_ejes(ax)
    fig.savefig(outfile)
    plt.close(fig)


def plot_fundamental_diagram(curves, outfile, legend_title: str = "caso", max_points: int = 3000) -> None:
    """Diagrama fundamental velocidad-densidad (≈ Fig. 5). ``curves``: dict ``p/orden -> (rho, v)``.
    Pocas curvas por figura (no todas las combinaciones juntas) para que sea legible.

    La curva de entrada es la media móvil (ya suavizada) y puede tener millones de puntos; se
    submuestrea de forma pareja a ``max_points`` para ploteo, lo que es visualmente idéntico y evita
    que el render y la ubicación automática de la leyenda se vuelvan lentísimos."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for key in sorted(curves):
        rho, v = curves[key]
        if getattr(rho, "size", 0) > max_points:
            idx = np.linspace(0, rho.size - 1, max_points).astype(int)
            rho, v = rho[idx], v[idx]
        ax.plot(rho, v, label=_curve_label(key))
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1.5, label="contacto: 1/(44 mm)")
    ax.set_xlabel("densidad (mm$^{-1}$)")
    ax.set_ylabel("velocidad (mm/s)")
    # Pocos ticks en el eje de densidad: si no, las etiquetas (varios decimales pequeños) se solapan.
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    # La leyenda va abajo a la izquierda: en el diagrama fundamental la velocidad decrece con la densidad,
    # así que esa esquina (baja densidad + baja velocidad) queda vacía y no tapa la curva superior.
    ax.legend(title=legend_title, loc="lower left")
    _coma_ejes(ax)
    fig.savefig(outfile)
    plt.close(fig)
