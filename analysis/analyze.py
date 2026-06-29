#!/usr/bin/env python3
"""Orquestador del análisis POST-simulación.

Lee las salidas del motor en un directorio (``data/``), agrupa las realizaciones por
(protocolo, p, N, regla) según los metadatos de cada archivo, calcula los observables y genera las
figuras en ``figures/``. Nada se calcula durante la simulación: esto corre después, sobre los
archivos ya escritos.

Ejemplo:
    python3 analyze.py --data-dir ../data --figures-dir ../figures --since-step 2000
"""
from __future__ import annotations

import argparse
import collections
from pathlib import Path

import numpy as np

import observables as obs
import plots
from run_io import load_run


def _discover(data_dir: Path):
    return sorted(data_dir.glob("*.txt"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="../data")
    ap.add_argument("--figures-dir", default="../figures")
    ap.add_argument("--since-step", type=int, default=0,
                    help="corte del transitorio (por inspección; ver observables.detect_stationary)")
    ap.add_argument("--bins", type=int, default=80)
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    files = _discover(data_dir)
    if not files:
        print(f"no hay datos en {data_dir} (corré primero run_matrix.py)")
        return

    runs = [load_run(f) for f in files]
    figdir = Path(args.figures_dir)
    figdir.mkdir(parents=True, exist_ok=True)

    # núcleo: solo FIXED_N (variar N y p)
    fixed = [r for r in runs if str(r.meta.get("protocol")) == "FIXED_N"]
    if not fixed:
        print("no hay corridas FIXED_N; nada que graficar en el núcleo")
        return

    by_pN = collections.defaultdict(list)
    by_N = collections.defaultdict(list)
    ps = set()
    for r in fixed:
        p, n = float(r.meta["p"]), int(r.meta["N"])
        by_pN[(p, n)].append(r)
        by_N[n].append(r)
        ps.add(p)
    ps = sorted(ps)

    # ≈ Fig. 2: velocidad media vs N, una curva por p
    results_by_p = {}
    for p in ps:
        ns = sorted({n for (pp, n) in by_pN if pp == p})
        mean, err = zip(*(obs.mean_speed_with_error(by_pN[(p, n)], args.since_step) for n in ns))
        results_by_p[p] = (np.array(ns), np.array(mean), np.array(err))
    plots.plot_mean_speed_vs_n(results_by_p, figdir / "velocidad_media_vs_N.png")

    # ≈ Figs. 3 y 4: PDF de densidad y de velocidad por N, a un p representativo (el menor disponible)
    p_rep = ps[0]
    dens, vels = {}, {}
    for n, rs in by_N.items():
        rs_p = [r for r in rs if float(r.meta["p"]) == p_rep] or rs
        dens[n] = obs.density_pdf(rs_p, args.since_step, args.bins, rho_range=(0.0, 0.03))
        vels[n] = obs.velocity_pdf(rs_p, args.since_step, args.bins, v_range=(0.0, 130.0))
    plots.plot_density_pdf(dens, figdir / "pdf_densidad.png")
    plots.plot_velocity_pdf(vels, figdir / "pdf_velocidad.png")

    # ≈ Fig. 5: diagrama fundamental con todas las corridas del núcleo
    rho, v = obs.fundamental_diagram(fixed, args.since_step, window=2000)
    plots.plot_fundamental_diagram({"simulación": (rho, v)}, figdir / "diagrama_fundamental.png")

    print(f"figuras generadas en {figdir} (p representativo para PDFs: {p_rep})")


if __name__ == "__main__":
    main()
