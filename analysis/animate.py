"""Animación de una corrida — sigue las guías de formato de la cátedra.

La pista es una **línea periódica** (no un círculo): un segmento horizontal de longitud L; lo que sale
por un extremo reentra por el otro. Cada vehículo es un rectángulo de largo ℓ, coloreado por su
**velocidad** (derivada post-simulación; el motor no guarda color).

Cumple las guías de formato (GuiaPresentaciones):
- ejes con leyenda en palabras y unidad MKS entre paréntesis (1.8), fuente grande (≥ 20);
- barra de color rotulada con unidades (velocidad, mm/s);
- los **parámetros fijos** del sistema van al costado de la figura (1.7), no embebidos como adorno;
- el tiempo se muestra en segundos (t = paso · dt);
- por defecto reproduce en **tiempo real** (fps = 1/(output_every·dt)); para corridas con
  ``output_every=1`` eso son 24 fps, igual que la cámara del experimento.

Además exporta un **fotograma representativo (PNG)**: en el PDF entregable NO van animaciones
(GuiaPresentaciones 2.4.8) — va esa imagen fija y, debajo, un link a YouTube o similar.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle

from run_io import load_run

FONTSIZE = 20


def _config_text(run) -> str:
    """Parámetros fijos del sistema, para mostrar al costado de la figura (guía 1.7)."""
    m = run.meta
    return "\n".join([
        "Parámetros",
        f"N = {m.get('N')}",
        f"p = {m.get('p')}",
        f"regla = {m.get('regla2')}",
        f"orden = {m.get('order')}",
        f"protocolo = {m.get('protocol')}",
        f"L = {float(m['L_celdas']) * float(m['dx_mm']):.0f} mm",
    ])


def animate(path, outfile=None, fps=None, max_frames=600, still=True):
    """Genera la animación de la realización en ``path`` (GIF) y un fotograma representativo (PNG).

    ``fps=None`` reproduce en tiempo real según la cadencia de muestreo. Devuelve (ruta_gif, ruta_png).
    """
    run = load_run(path)
    ell = float(run.meta["ell_celdas"]) * float(run.meta["dx_mm"])
    track = float(run.meta["L_celdas"]) * float(run.meta["dx_mm"])
    dt = float(run.meta["dt_s"])
    output_every = int(run.meta.get("output_every", 1))
    if fps is None:
        fps = max(1.0, 1.0 / (output_every * dt))  # tiempo real

    steps = np.unique(run.step)[:max_frames]
    frames = [(run.x_mm[run.step == s], run.v_mmps[run.step == s]) for s in steps]
    vmax = max((v.max() for _, v in frames if v.size), default=1.0) or 1.0
    cmap = plt.cm.viridis
    norm = Normalize(vmin=0.0, vmax=vmax)

    with plt.rc_context({"font.size": FONTSIZE, "axes.labelsize": FONTSIZE,
                         "xtick.labelsize": FONTSIZE - 2, "ytick.labelsize": FONTSIZE - 2}):
        fig, ax = plt.subplots(figsize=(15, 3.6))
        fig.subplots_adjust(left=0.05, right=0.78, bottom=0.30, top=0.82)
        cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, pad=0.02)
        cbar.set_label("velocidad (mm/s)", fontsize=FONTSIZE)
        fig.text(0.80, 0.55, _config_text(run), fontsize=FONTSIZE - 5,
                 va="center", ha="left", family="monospace")

        def draw(i):
            ax.clear()
            ax.set_xlim(0, track)
            ax.set_ylim(0, 1)
            ax.set_yticks([])
            ax.set_xlabel("posición (mm)")
            ax.set_title(f"t = {steps[i] * dt:6.1f} s")
            x, v = frames[i]
            for xi, vi in zip(x, v):
                color = cmap(norm(vi))
                base = xi % track
                ax.add_patch(Rectangle((base, 0.25), ell, 0.5, color=color))
                if base + ell > track:  # envoltura periódica
                    ax.add_patch(Rectangle((base - track, 0.25), ell, 0.5, color=color))
            return []

        out = str(outfile) if outfile else str(Path(path).with_suffix(".gif"))
        anim = FuncAnimation(fig, draw, frames=len(frames), interval=1000.0 / fps)
        anim.save(out, writer=PillowWriter(fps=fps))

        still_path = None
        if still:
            draw(len(frames) // 2)  # fotograma representativo (mitad de la corrida)
            still_path = str(Path(out).with_suffix("")) + "_fotograma.png"
            fig.savefig(still_path, dpi=150)
        plt.close(fig)

    return out, still_path
