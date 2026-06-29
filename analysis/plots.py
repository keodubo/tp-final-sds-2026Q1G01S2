"""Figuras del informe/presentación. Siguen las guías de formato de la cátedra:
- ejes con leyendas en PALABRAS y unidades MKS entre paréntesis (GuiaPresentaciones 1.8);
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

CONTACT_DENSITY = 1.0 / 44.0  # mm^-1, densidad de contacto del VDV (largo 44 mm)
FONTSIZE = 20                 # guía 1.8: al menos 20
FIGSIZE = (9, 6)


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
        return f"p = {key:g}"
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
    fig.savefig(outfile)
    plt.close(fig)


def plot_density_pdf(pdfs_by_n, outfile) -> None:
    """PDF de densidades, una curva por N (≈ Fig. 3). ``pdfs_by_n``: dict ``N -> (centros, pdf)``."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for n in sorted(pdfs_by_n):
        centros, pdf = pdfs_by_n[n]
        ax.plot(centros, pdf, label=f"N = {n}")
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1.5, label="contacto (1/44 mm)")
    ax.set_xlabel("densidad (mm$^{-1}$)")
    ax.set_ylabel("densidad de probabilidad")
    ax.set_yscale("log")  # 2.4.7: varios órdenes de magnitud
    ax.legend()
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
    ax.legend()
    fig.savefig(outfile)
    plt.close(fig)


def plot_time_evolution(curves, outfile) -> None:
    """Evolución temporal de la velocidad media (regla 4 de la cátedra: respaldo visual para elegir el
    corte del estacionario por inspección). ``curves``: dict ``etiqueta -> (pasos, serie, corte)``;
    ``corte`` puede ser None. Marca el corte sugerido con una línea vertical."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for label, (steps, serie, cut) in curves.items():
        line, = ax.plot(steps, serie, label=label)
        if cut is not None:
            ax.axvline(cut, ls=":", lw=1.5, color=line.get_color())
    ax.set_xlabel("tiempo (pasos)")
    ax.set_ylabel("velocidad media (mm/s)")
    ax.legend(title="corte sugerido: línea punteada")
    fig.savefig(outfile)
    plt.close(fig)


def plot_fundamental_diagram(curves, outfile) -> None:
    """Diagrama fundamental velocidad-densidad (≈ Fig. 5). ``curves``: dict ``etiqueta -> (rho, v)``."""
    configure()
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for label, (rho, v) in curves.items():
        ax.plot(rho, v, label=label)
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1.5, label="contacto (1/44 mm)")
    ax.set_xlabel("densidad (mm$^{-1}$)")
    ax.set_ylabel("velocidad (mm/s)")
    ax.legend()
    fig.savefig(outfile)
    plt.close(fig)
