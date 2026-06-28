"""Animación de una corrida.

La pista es una **línea periódica**: se dibuja como un segmento horizontal de longitud L_fis
[mm] y lo que sale por un extremo reentra por el otro (no se dibuja como un círculo). Cada vehículo
es un rectángulo (de largo ℓ) ubicado por su posición; el **color se deriva de la velocidad**
(post-simulación; el motor no guarda color). Pensada para exportar a video/GIF y enlazar desde el
informe y la presentación.

Esqueleto a completar en el Hito 6.
"""
from __future__ import annotations

from run_io import load_run


def animate(path: str, outfile: str | None = None, fps: int = 24) -> None:
    """Genera la animación de la realización en ``path`` sobre una línea periódica horizontal.

    Pasos previstos (TODO Hito 6):
    1. Cargar la corrida (posiciones x_mm y velocidades v_mmps por paso).
    2. Dibujar la pista como un eje horizontal [0, L_fis] con envoltura periódica.
    3. Por frame, ubicar cada vehículo como un rectángulo de largo ℓ y colorearlo por su velocidad
       (mapa de color + colorbar en mm/s).
    4. Reproducir a ``fps`` (24 para comparar con la cámara del experimento) y exportar a video/GIF.
    """
    raise NotImplementedError
