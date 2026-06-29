#!/usr/bin/env python3
"""Orquestador del análisis POST-simulación.

Lee las salidas del motor en un directorio (``data/``), agrupa las realizaciones por
(**variante de R2**, p, N) según los metadatos de cada archivo, calcula los observables y genera las
figuras en ``figures/``. Nada se calcula durante la simulación: esto corre después, sobre los
archivos ya escritos.

IMPORTANTE: las corridas se agrupan **por variante de R2** (``regla2``). Mezclar CONTACTO_PURO y
CLASICA_SALVO_CERO en un mismo promedio sería comparar dos modelos distintos y reportar su diferencia
como si fuera error entre realizaciones. Por eso cada variante genera su propio juego de figuras, y el
diagrama fundamental las muestra como curvas separadas y etiquetadas.

Ejemplo:
    python3 analyze.py --data-dir ../data --figures-dir ../figures --since-step 4320
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
                    help="corte del transitorio (por inspección; 0 = sin recorte, incluye el cuadro 0 "
                         "con v=0). Mirá la figura de evolución temporal para elegirlo.")
    ap.add_argument("--bins", type=int, default=80)
    ap.add_argument("--fd-window", type=int, default=20000, help="ventana de media móvil del diagrama fundamental")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    files = _discover(data_dir)
    if not files:
        print(f"no hay datos en {data_dir} (corré primero run_matrix.py)")
        return

    runs = [load_run(f) for f in files]
    figdir = Path(args.figures_dir)
    figdir.mkdir(parents=True, exist_ok=True)
    plots.configure()

    # núcleo: solo FIXED_N (variar N y p). Agrupado SIEMPRE por variante de R2.
    fixed = [r for r in runs if str(r.meta.get("protocol")) == "FIXED_N"]
    if not fixed:
        print("no hay corridas FIXED_N; nada que graficar en el núcleo")
        return

    rules = sorted({str(r.meta.get("regla2")) for r in fixed})
    fd_curves = {}

    for rule in rules:
        rule_runs = [r for r in fixed if str(r.meta.get("regla2")) == rule]
        by_pN = collections.defaultdict(list)
        by_N = collections.defaultdict(list)
        ps = set()
        for r in rule_runs:
            p, n = float(r.meta["p"]), int(r.meta["N"])
            by_pN[(p, n)].append(r)
            by_N[n].append(r)
            ps.add(p)
        ps = sorted(ps)
        tag = rule.lower()

        # ≈ Fig. 2: velocidad media vs N, una curva por p
        results_by_p = {}
        for p in ps:
            ns = sorted({n for (pp, n) in by_pN if pp == p})
            mean, err = zip(*(obs.mean_speed_with_error(by_pN[(p, n)], args.since_step) for n in ns))
            results_by_p[p] = (np.array(ns), np.array(mean), np.array(err))
        plots.plot_mean_speed_vs_n(results_by_p, figdir / f"velocidad_media_vs_N_{tag}.png")

        # ≈ Figs. 3 y 4: PDF de densidad y velocidad por N, a un p representativo (el menor)
        p_rep = ps[0]
        dens, vels = {}, {}
        for n, rs in by_N.items():
            rs_p = [r for r in rs if float(r.meta["p"]) == p_rep] or rs
            dens[n] = obs.density_pdf(rs_p, args.since_step, args.bins, rho_range=(0.0, 0.03))
            vels[n] = obs.velocity_pdf(rs_p, args.since_step, args.bins, v_range=(0.0, 130.0))
        plots.plot_density_pdf(dens, figdir / f"pdf_densidad_{tag}.png")
        plots.plot_velocity_pdf(vels, figdir / f"pdf_velocidad_{tag}.png")

        # evolución temporal (regla 4 de la cátedra) + sugerencia de estacionario, en un caso representativo
        n_rep = max(by_N)
        rep = by_pN.get((p_rep, n_rep), rule_runs)[0]
        steps, serie = obs.mean_speed_series(rep)
        cut = obs.detect_stationary(serie)
        plots.plot_time_evolution(
            {f"{rule} (N={n_rep}, p={p_rep:g})": (steps, serie, cut)},
            figdir / f"evolucion_temporal_{tag}.png",
        )

        # diagrama fundamental: curva por variante (NO se mezclan)
        rho, v = obs.fundamental_diagram(rule_runs, args.since_step, window=args.fd_window)
        fd_curves[rule] = (rho, v)

    plots.plot_fundamental_diagram(fd_curves, figdir / "diagrama_fundamental.png")
    print(f"figuras generadas en {figdir} para variantes: {rules}")


if __name__ == "__main__":
    main()
