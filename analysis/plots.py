"""Figuras del informe. Respetan las correcciones de la cátedra:
- una sola figura con curvas de colores para comparar (no una por escenario);
- texto de la figura del mismo tamaño que el resto del texto;
- escala logarítmica donde mejore la visualización.

Esqueletos a completar en el Hito 6.
"""
from __future__ import annotations

import matplotlib.pyplot as plt


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


def plot_mean_speed_vs_n(results_by_p, outfile: str) -> None:
    """Velocidad media vs N, una curva de color por cada p (≈ Fig. 2 del artículo). TODO (Hito 6)."""
    raise NotImplementedError


def plot_density_pdf(pdfs_by_n, outfile: str) -> None:
    """PDF de densidades, una curva por N (≈ Fig. 3). TODO (Hito 6)."""
    raise NotImplementedError


def plot_velocity_pdf(pdfs_by_n, outfile: str) -> None:
    """PDF de velocidades, una curva por N (≈ Fig. 4). TODO (Hito 6)."""
    raise NotImplementedError


def plot_fundamental_diagram(curves, outfile: str) -> None:
    """Diagrama fundamental velocidad-densidad (≈ Fig. 5). TODO (Hito 6)."""
    raise NotImplementedError
