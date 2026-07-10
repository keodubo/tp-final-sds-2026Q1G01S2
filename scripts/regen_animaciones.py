#!/usr/bin/env python3
"""Regenera las 5 animaciones hero FLUIDAS (para subir a YouTube) desde los datos de data_anim/.

Solo re-anima los .txt hero existentes (no re-corre simulaciones); usa muchos fotogramas y fps alto
(el problema de las versiones viejas era 120 fotogramas y, en los incrementales, 2,4 fps → choppy).
Exporta solo MP4 (make_gif=False) y el fotograma representativo, con los nombres SIN "_oe" que piden
los .tex. Correr desde la raíz del repo:  python3 scripts/regen_animaciones.py
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "analysis"))
import animate  # noqa: E402

DATA_ANIM = os.path.join(os.path.dirname(__file__), "..", "data_anim")

# Fijas: 2000 pasos oe1 (dinámica rápida) → pocos pasos/fotograma = muy fluido en ~24 s.
# Incrementales: 2592 fotogramas oe10 → TODOS los fotogramas + fps alto = fluido (0,85 ℓ/fotograma).
SPECS = {
    "FIXED": dict(max_frames=720, fps=30, still_step=None),      # 2000 pasos oe1 → 0,3 ℓ/fotograma, 24 s
    "INC": dict(max_frames=1800, fps=36, still_step=6480),       # ~1,1 ℓ/fotograma, 50 s; fase N=10 para el still
}


def main() -> None:
    txts = sorted(glob.glob(os.path.join(DATA_ANIM, "*.txt")))
    for f in txts:
        base = os.path.basename(f)[:-4]
        clean = re.sub(r"_oe\d+", "", base)
        out_gif = os.path.join(DATA_ANIM, clean + ".gif")  # base; se exporta .mp4 y _fotograma.png
        kind = "INC" if base.startswith("INC") else "FIXED"
        s = SPECS[kind]
        animate.animate(f, outfile=out_gif, make_gif=False,
                        max_frames=s["max_frames"], fps=s["fps"], still_step=s["still_step"])
        print(f"hero fluido: {clean}.mp4 ({kind}, fps={s['fps']})", flush=True)


if __name__ == "__main__":
    main()
