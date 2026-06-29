"""Animación de una corrida.

La pista es una **línea periódica**: se dibuja como un segmento horizontal de longitud L [mm] y lo
que sale por un extremo reentra por el otro (no se dibuja como un círculo). Cada vehículo es un
rectángulo (de largo ℓ) ubicado por su posición; el **color se deriva de la velocidad**
(post-simulación; el motor no guarda color). Pensada para exportar a GIF y enlazar desde el informe
y la presentación.
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


def animate(path, outfile: str | None = None, fps: int = 24, max_frames: int = 300):
    """Genera la animación de la realización en ``path`` sobre una línea periódica horizontal.

    El color de cada vehículo se deriva de su velocidad (mm/s) recién acá, en el análisis. Devuelve
    la ruta del archivo generado (GIF). Se limita a ``max_frames`` cuadros para que el GIF no explote.
    """
    run = load_run(path)
    ell = float(run.meta["ell_celdas"]) * float(run.meta["dx_mm"])
    track = float(run.meta["L_celdas"]) * float(run.meta["dx_mm"])

    steps = np.unique(run.step)[:max_frames]
    frames = [(run.x_mm[run.step == s], run.v_mmps[run.step == s]) for s in steps]
    vmax = max((v.max() for _, v in frames if v.size), default=1.0) or 1.0

    cmap = plt.cm.viridis
    norm = Normalize(vmin=0.0, vmax=vmax)
    fig, ax = plt.subplots(figsize=(12, 2.2))
    fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax, label="velocidad [mm/s]")

    def draw(i):
        ax.clear()
        ax.set_xlim(0, track)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel("posición [mm] (ruta periódica: sale por un extremo, entra por el otro)")
        ax.set_title(f"paso {int(steps[i])}")
        x, v = frames[i]
        for xi, vi in zip(x, v):
            color = cmap(norm(vi))
            base = xi % track
            ax.add_patch(Rectangle((base, 0.25), ell, 0.5, color=color))
            if base + ell > track:  # envoltura: dibujar la parte que reentra
                ax.add_patch(Rectangle((base - track, 0.25), ell, 0.5, color=color))
        return []

    anim = FuncAnimation(fig, draw, frames=len(frames), interval=1000.0 / fps)
    out = str(outfile) if outfile else str(Path(path).with_suffix(".gif"))
    anim.save(out, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return out
