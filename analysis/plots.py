"""Figuras del informe. Respetan las correcciones de la cátedra:
- una sola figura con curvas de colores para comparar (no una por escenario);
- texto de la figura del mismo tamaño que el resto del texto;
- escala logarítmica donde mejore la visualización.

Reciben observables ya calculados (ver observables.py) y guardan cada figura a un archivo.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # backend sin display (corridas headless)
import matplotlib.pyplot as plt

CONTACT_DENSITY = 1.0 / 44.0  # 1/mm, densidad de contacto del VDV (largo 44 mm)


def configure(base_fontsize: int = 14) -> None:
    """Configura matplotlib con tipografía grande y legible (corrección recurrente de Parisi)."""
    plt.rcParams.update({
        "font.size": base_fontsize,
        "axes.labelsize": base_fontsize,
        "axes.titlesize": base_fontsize,
        "xtick.labelsize": base_fontsize - 1,
        "ytick.labelsize": base_fontsize - 1,
        "legend.fontsize": base_fontsize - 1,
        "figure.dpi": 120,
        "savefig.bbox": "tight",
    })


def plot_mean_speed_vs_n(results_by_p, outfile) -> None:
    """Velocidad media vs N, una curva de color por cada p (≈ Fig. 2 del artículo).

    ``results_by_p``: dict ``p -> (N, media, error)`` con arreglos del mismo largo."""
    configure()
    fig, ax = plt.subplots(figsize=(7, 5))
    for p in sorted(results_by_p):
        n, mean, err = results_by_p[p]
        ax.errorbar(n, mean, yerr=err, marker="o", capsize=3, label=f"p = {p:g}")
    ax.set_xlabel("N (vehículos)")
    ax.set_ylabel("velocidad media [mm/s]")
    ax.legend(title="frenado aleatorio")
    fig.savefig(outfile)
    plt.close(fig)


def plot_density_pdf(pdfs_by_n, outfile) -> None:
    """PDF de densidades, una curva por N (≈ Fig. 3). ``pdfs_by_n``: dict ``N -> (centros, pdf)``."""
    configure()
    fig, ax = plt.subplots(figsize=(7, 5))
    for n in sorted(pdfs_by_n):
        centros, pdf = pdfs_by_n[n]
        ax.plot(centros, pdf, label=f"N = {n}")
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1, label="contacto 1/44 mm")
    ax.set_xlabel("densidad ρ [1/mm]")
    ax.set_ylabel("PDF")
    ax.set_yscale("log")
    ax.legend()
    fig.savefig(outfile)
    plt.close(fig)


def plot_velocity_pdf(pdfs_by_n, outfile) -> None:
    """PDF de velocidades, una curva por N (≈ Fig. 4). ``pdfs_by_n``: dict ``N -> (centros, pdf)``."""
    configure()
    fig, ax = plt.subplots(figsize=(7, 5))
    for n in sorted(pdfs_by_n):
        centros, pdf = pdfs_by_n[n]
        ax.plot(centros, pdf, label=f"N = {n}")
    ax.set_xlabel("velocidad [mm/s]")
    ax.set_ylabel("PDF")
    ax.legend()
    fig.savefig(outfile)
    plt.close(fig)


def plot_time_evolution(curves, outfile) -> None:
    """Evolución temporal de la velocidad media (regla 4 de la cátedra: respaldo visual para elegir el
    corte del estacionario por inspección). ``curves``: dict ``etiqueta -> (pasos, serie, corte)``;
    ``corte`` puede ser None. Marca el corte sugerido con una línea vertical."""
    configure()
    fig, ax = plt.subplots(figsize=(7, 5))
    for label, (steps, serie, cut) in curves.items():
        line, = ax.plot(steps, serie, label=label)
        if cut is not None:
            ax.axvline(cut, ls=":", lw=1, color=line.get_color())
    ax.set_xlabel("paso de tiempo")
    ax.set_ylabel("velocidad media [mm/s]")
    ax.legend(title="corte sugerido (línea punteada)")
    fig.savefig(outfile)
    plt.close(fig)


def plot_fundamental_diagram(curves, outfile) -> None:
    """Diagrama fundamental velocidad-densidad (≈ Fig. 5). ``curves``: dict ``etiqueta -> (rho, v)``."""
    configure()
    fig, ax = plt.subplots(figsize=(7, 5))
    for label, (rho, v) in curves.items():
        ax.plot(rho, v, label=label)
    ax.axvline(CONTACT_DENSITY, ls="--", color="grey", lw=1, label="contacto 1/44 mm")
    ax.set_xlabel("densidad ρ [1/mm]")
    ax.set_ylabel("velocidad [mm/s]")
    ax.legend()
    fig.savefig(outfile)
    plt.close(fig)
