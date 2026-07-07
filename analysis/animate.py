"""Animación de una realización — material DEFENDIBLE (no gráfico de depuración).

La pista se modela como una **línea periódica horizontal** (no un círculo): un segmento de longitud
``L``; lo que sale por el extremo derecho (``x=L``) reentra por el izquierdo (``x=0``). Ambos extremos
se **identifican** y el movimiento es siempre hacia ``+x`` (izquierda → derecha). Cada vehículo es un
rectángulo de largo ``ℓ`` coloreado por su **velocidad**, derivada post-simulación (el motor sólo
escribe variables físicas ``id, x, v``; nunca color).

Cumple las guías de la cátedra:
- ejes rotulados en palabras con unidad MKS y fuente grande; barra de color anclada a un **máximo
  físico fijo** (``vfree_max_mmps``) para que el color signifique lo mismo en todas las figuras;
- panel compacto de parámetros **al costado**, en su propio recuadro con margen: N (activos y nominal),
  p, regla, protocolo, orden, **realización** (nunca "seed"/"semilla") y tiempo en segundos;
- el fotograma fijo (PNG que va al PDF, donde no van animaciones) se toma en el **estado estacionario**
  (último fotograma registrado, o el primero en/después de ``since_step``), no en el transitorio.

Las funciones puras (``real_time_fps``, ``color_scale_max``, ``config_lines``, ``still_frame_index``,
``active_count``, ``wrap_positions``) no tienen efectos secundarios y están cubiertas por tests de
comportamiento en ``tests/test_animate.py``.
"""
from __future__ import annotations

import shutil
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
DEFAULT_VMAX_MMPS = 120.0  # respaldo si la cabecera no trae vfree_max_mmps

# Traducción de los enums internos del motor a texto legible en español para el panel VISIBLE de la
# animación. No afecta nombres de archivo ni claves internas.
_ETIQUETAS_ES = {
    "CONTACTO_PURO": "contacto puro",
    "CLASICA_SALVO_CERO": "clásica",
    "FIXED_N": "N fijo",
    "INCREMENTAL_180S": "incremental",
    "ASCENDING": "creciente",
    "DESCENDING": "decreciente",
    "RANDOM": "aleatorio",
}


def _es(value) -> str:
    """Traduce un enum interno del motor a su etiqueta en español para el panel visible."""
    return _ETIQUETAS_ES.get(str(value), str(value))


# --------------------------------------------------------------------------------------------------
# Funciones puras (sin efectos secundarios) — cubiertas por tests de comportamiento.
# --------------------------------------------------------------------------------------------------
def real_time_fps(output_every: int, dt: float) -> float:
    """Cuadros por segundo para reproducir en **tiempo real**: ``1 / (output_every·dt)``.

    Con ``output_every=1`` y ``dt=1/24`` da 24.0 (la cadencia de la cámara del experimento).
    """
    return 1.0 / (float(output_every) * float(dt))


def color_scale_max(meta: dict) -> float:
    """Máximo físico para anclar la escala de color: ``vfree_max_mmps`` si es válido, si no un
    respaldo positivo (``DEFAULT_VMAX_MMPS``). Así el color significa lo mismo en todas las figuras.
    """
    try:
        vmax = float(meta.get("vfree_max_mmps"))
    except (TypeError, ValueError):
        vmax = None
    if vmax is not None and vmax > 0.0:
        return vmax
    return DEFAULT_VMAX_MMPS


def config_lines(meta: dict) -> list[str]:
    """Parámetros fijos del sistema, una línea por parámetro (para el panel al costado).

    Incluye siempre una línea con **"realización"** (regla de la cátedra: nunca "seed"/"semilla").
    Para ``FIXED_N`` el orden no aplica (la cabecera trae ``order=SIN_ORDEN``).
    """
    order = meta.get("order")
    order_txt = "no aplica" if order in (None, "", "SIN_ORDEN") else _es(order)
    return [
        f"N = {meta.get('N')}",
        f"p = {meta.get('p')}",
        f"regla = {_es(meta.get('regla2'))}",
        f"protocolo = {_es(meta.get('protocol'))}",
        f"orden = {order_txt}",
        f"realización = {meta.get('realizacion_id')}",
    ]


def still_frame_index(steps, since_step: int = 0) -> int:
    """Índice del fotograma representativo (estacionario): el último fotograma con ``paso ≥ since_step``.

    Si ninguno califica (``since_step`` mayor que todos los pasos), devuelve el último fotograma.
    Con el valor por defecto ``since_step=0`` esto es siempre el último fotograma registrado.
    """
    steps = np.asarray(steps)
    if steps.size == 0:
        return 0
    qualifying = np.nonzero(steps >= since_step)[0]
    if qualifying.size:
        return int(qualifying[-1])
    return int(steps.size - 1)


def active_count(x_mm) -> int:
    """Cantidad de vehículos presentes en un fotograma (útil para el protocolo incremental)."""
    return int(np.asarray(x_mm).size)


def wrap_positions(base: float, ell: float, track: float) -> list[float]:
    """Posiciones ``x`` donde dibujar el rectángulo de un vehículo con envoltura periódica.

    ``base`` es la posición ya reducida a ``[0, track)``. Siempre se dibuja en ``base``; si el vehículo
    cruza el extremo (``base + ell > track``) se dibuja **también** su copia envuelta en ``base - track``,
    de modo que un vehículo a caballo de ``x=L`` aparece en ambos extremos.
    """
    positions = [base]
    if base + ell > track:
        positions.append(base - track)
    return positions


# --------------------------------------------------------------------------------------------------
# Composición del panel (usa las puras; no es pura porque mezcla estado dinámico del fotograma).
# --------------------------------------------------------------------------------------------------
def _panel_text(meta: dict, n_active: int, t_s: float) -> str:
    dinamico = [f"t = {t_s:.1f} s", f"activos = {n_active}"]
    return "\n".join(dinamico + config_lines(meta))


# --------------------------------------------------------------------------------------------------
# Punto de entrada.
# --------------------------------------------------------------------------------------------------
def animate(path, outfile=None, fps=None, max_frames=600, still=True, since_step=0):
    """Renderiza la realización en ``path``: un GIF (animación) y un fotograma fijo (PNG estacionario).

    ``fps=None`` reproduce en tiempo real según la cadencia de muestreo. ``since_step`` fija desde qué
    paso se considera estacionario para el fotograma fijo (por defecto 0 ⇒ último fotograma).
    Devuelve ``(ruta_gif, ruta_png)``. Si hay ffmpeg exporta además un MP4 al lado (sin fallar si no).
    """
    run = load_run(path)
    meta = run.meta
    ell = float(meta["ell_celdas"]) * float(meta["dx_mm"])
    track = float(meta["L_celdas"]) * float(meta["dx_mm"])
    dt = float(meta["dt_s"])
    output_every = int(meta.get("output_every", 1))
    if fps is None:
        fps = max(1.0, real_time_fps(output_every, dt))

    all_steps = np.unique(run.step)
    if all_steps.size == 0:
        raise ValueError("la realización no tiene pasos registrados")
    # Para la animación: si hay más pasos que max_frames, submuestreo uniforme (mantengo TODA la
    # evolución visible, incluidos primero y último paso), en vez de truncar al comienzo.
    if all_steps.size > max_frames:
        idx = np.unique(np.linspace(0, all_steps.size - 1, max_frames).astype(int))
        anim_steps = all_steps[idx]
    else:
        anim_steps = all_steps
    frames = [(run.x_mm[run.step == s], run.v_mmps[run.step == s]) for s in anim_steps]

    vmax = color_scale_max(meta)
    cmap = plt.cm.viridis
    norm = Normalize(vmin=0.0, vmax=vmax)

    margin = 0.02 * track

    with plt.rc_context({"font.size": FONTSIZE, "axes.labelsize": FONTSIZE,
                         "xtick.labelsize": FONTSIZE - 4, "ytick.labelsize": FONTSIZE - 4}):
        fig = plt.figure(figsize=(16, 4.4))
        ax = fig.add_axes([0.06, 0.24, 0.62, 0.54])
        cax = fig.add_axes([0.70, 0.24, 0.014, 0.54])
        cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax)
        cbar.set_label("velocidad (mm/s)", fontsize=FONTSIZE - 2)

        fig.suptitle("Pista periódica — vehículos coloreados por velocidad",
                     fontsize=FONTSIZE, y=0.96)
        # Panel de parámetros: recuadro propio con margen, al costado derecho (no encima de la pista).
        panel = fig.text(0.775, 0.51, "", fontsize=FONTSIZE - 6, va="center", ha="left",
                         family="monospace",
                         bbox=dict(boxstyle="round,pad=0.6", facecolor="white", edgecolor="0.6"))

        def draw(i):
            ax.clear()
            ax.set_xlim(-margin, track + margin)
            ax.set_ylim(0.0, 1.0)
            ax.set_yticks([])
            ax.set_xlabel("posición sobre la pista (mm)")

            # Recta base de la pista (segmento periódico horizontal).
            ax.plot([0.0, track], [0.5, 0.5], color="0.8", lw=1.5, zorder=0)
            # Extremos identificados x=0 ≡ x=L (reentrada periódica).
            ax.axvline(0.0, color="0.5", ls="--", lw=1.2, zorder=1)
            ax.axvline(track, color="0.5", ls="--", lw=1.2, zorder=1)
            ax.text(0.0, 0.86, "↺", ha="center", va="center", fontsize=FONTSIZE - 2, color="0.4")
            ax.text(track, 0.86, "↺", ha="center", va="center", fontsize=FONTSIZE - 2, color="0.4")
            ax.text(0.5, 0.03, "los extremos x=0 y x=L se identifican (reentrada periódica)",
                    transform=ax.transAxes, ha="center", va="bottom",
                    fontsize=FONTSIZE - 8, style="italic", color="0.35")
            # Sentido de avance (el movimiento es +x, izquierda → derecha).
            ax.annotate("", xy=(0.60, 0.90), xytext=(0.40, 0.90), xycoords="axes fraction",
                        arrowprops=dict(arrowstyle="-|>", lw=2.0, color="black"))
            ax.text(0.50, 0.965, "sentido de avance", transform=ax.transAxes,
                    ha="center", va="center", fontsize=FONTSIZE - 6)

            x, v = frames[i]
            for xi, vi in zip(x, v):
                color = cmap(norm(vi))
                base = xi % track
                for px in wrap_positions(base, ell, track):
                    ax.add_patch(Rectangle((px, 0.35), ell, 0.30, facecolor=color,
                                           edgecolor="0.25", lw=0.4, zorder=3))

            t_s = float(anim_steps[i]) * dt
            ax.set_title(f"t = {t_s:5.1f} s", fontsize=FONTSIZE - 2)
            panel.set_text(_panel_text(meta, active_count(x), t_s))
            return []

        out = str(outfile) if outfile else str(Path(path).with_suffix(".gif"))
        anim = FuncAnimation(fig, draw, frames=len(frames), interval=1000.0 / fps)
        anim.save(out, writer=PillowWriter(fps=fps))

        # MP4 opcional (mejor para proyectar); no es parte del contrato: si falla, se ignora.
        if shutil.which("ffmpeg"):
            try:
                from matplotlib.animation import FFMpegWriter
                mp4 = str(Path(out).with_suffix(".mp4"))
                anim.save(mp4, writer=FFMpegWriter(fps=fps))
                print(f"[animate] MP4 exportado → {mp4}")
            except Exception as exc:  # pragma: no cover - depende del entorno
                print(f"[animate] MP4 no exportado ({exc})")

        still_path = None
        if still:
            draw(still_frame_index(anim_steps, since_step))  # fotograma estacionario
            still_path = str(Path(out).with_suffix("")) + "_fotograma.png"
            fig.savefig(still_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

    return out, still_path
