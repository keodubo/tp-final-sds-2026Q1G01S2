#!/usr/bin/env python3
"""Análisis del estudio de sensibilidad de la calibración (dt, L, Δx).

Lee ../data_sens/ (generado por run_sensitivity.py), calcula la velocidad media estacionaria en
unidades físicas (mm/s) para el punto comparable (contacto puro, p=0.1, N fijo) y produce UNA figura
con tres paneles (una curva de color por valor del parámetro variado):

  panel Δx : Δx ∈ {0.125, 0.25, 0.5} mm      (dt=1/24 fijo)
  panel dt : dt ∈ {1/12, 1/24, 1/48} s        (Δx=0.25 fijo)
  panel L  : L ∈ {1313, 1320} mm              (N≤25; N=30 sólo cierra a contacto en 1320)

El corte del estacionario se toma en TIEMPO FÍSICO (t ≥ 2000·(1/24) s ≈ 83.3 s), consistente con el
--since-step 2000 del barrido principal, así funciona para todos los dt. Imprime además una tabla
base-vs-variación para el texto del informe.

Ejemplo:
    python3 analyze_sensitivity.py --data-dir ../data_sens --figures-dir ../figures
"""
from __future__ import annotations

import argparse
import collections
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import plots
from run_io import load_run

T_CUT_S = 2000.0 / 24.0   # corte del estacionario en segundos (igual que --since-step 2000 del barrido)

# etiqueta -> (grupo, valor legible para leyenda, orden dentro del grupo)
VARIACIONES = {
    "base":   ("dx", r"$\Delta x=0{,}25$ mm", 1),
    "dx0125": ("dx", r"$\Delta x=0{,}125$ mm", 0),
    "dx0500": ("dx", r"$\Delta x=0{,}5$ mm", 2),
    "dt12":   ("dt", r"$\Delta t=1/12$ s", 0),
    "dt48":   ("dt", r"$\Delta t=1/48$ s", 2),
    "L1313":  ("L", r"$L=1313$ mm", 0),
}
# 'base' participa además de los paneles dt (Δt=1/24) y L (L=1320): se agrega abajo.


def stationary_mean(run) -> float:
    """Velocidad media [mm/s] sobre la ventana estacionaria (t ≥ T_CUT_S), promediando vehículos y pasos."""
    dt = float(run.meta["dt_s"])
    mask = run.step * dt >= T_CUT_S
    v = run.v_mmps[mask]
    return float(np.mean(v)) if v.size else float("nan")


def collect(data_dir: Path):
    """Devuelve {etiqueta: {N: (media, err, M)}} a partir de los archivos SENS_*."""
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in sorted(data_dir.glob("SENS_*.txt")):
        # SENS_<label>_N<n>_p01_CONTACTO_PURO_r<r>.txt
        parts = f.stem.split("_")
        label = parts[1]
        n = int(parts[2][1:])
        per[label][n].append(stationary_mean(load_run(f)))
    out = {}
    for label, by_n in per.items():
        out[label] = {}
        for n, vals in by_n.items():
            a = np.array(vals, dtype=float)
            a = a[~np.isnan(a)]
            err = float(np.std(a, ddof=1)) if a.size > 1 else float("nan")
            out[label][n] = (float(np.mean(a)), err, a.size)
    return out


def _curve(data, label):
    ns = sorted(data[label])
    mean = np.array([data[label][n][0] for n in ns])
    err = np.array([data[label][n][1] for n in ns])
    return np.array(ns), mean, err


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="../data_sens")
    ap.add_argument("--figures-dir", default="../figures")
    args = ap.parse_args()

    data = collect(Path(args.data_dir))
    if "base" not in data:
        print("no hay corridas 'base' en data_sens (corré run_sensitivity.py)")
        return
    figdir = Path(args.figures_dir)
    figdir.mkdir(parents=True, exist_ok=True)
    plots.configure()

    # Paneles: cada uno lista (etiqueta, leyenda) ordenadas
    paneles = {
        "$\\Delta x$ (con $\\Delta t=1/24$ s)": [("dx0125", r"$\Delta x=0{,}125$"), ("base", r"$\Delta x=0{,}25$ (calib.)"), ("dx0500", r"$\Delta x=0{,}5$")],
        "$\\Delta t$ (con $\\Delta x=0{,}25$ mm)": [("dt12", r"$\Delta t=1/12$"), ("base", r"$\Delta t=1/24$ (calib.)"), ("dt48", r"$\Delta t=1/48$")],
        "$L$ (con calibración base)": [("L1313", r"$L=1313$ mm"), ("base", r"$L=1320$ mm (calib.)")],
    }
    fig, axes = plt.subplots(1, 3, figsize=(20, 6), sharey=True)
    for ax, (titulo, curvas) in zip(axes, paneles.items()):
        for label, leyenda in curvas:
            if label not in data:
                continue
            ns, mean, err = _curve(data, label)
            ax.errorbar(ns, mean, yerr=err, marker="o", capsize=3, label=leyenda)
        ax.set_title(titulo)
        ax.set_xlabel("N (vehículos)")
        ax.grid(True, alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("velocidad media (mm/s)")
    fig.tight_layout()
    out = figdir / "sensibilidad_dt_L_dx.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"figura → {out}")

    # Tabla resumen base-vs-variación (para el texto del informe)
    print("\n=== v̄ estacionaria [mm/s] por N (media ± desvío entre realizaciones, M) ===")
    labels = ["dx0125", "base", "dx0500", "dt12", "dt48", "L1313"]
    ns_all = sorted({n for lab in labels if lab in data for n in data[lab]})
    header = "  N | " + " | ".join(f"{lab:>12}" for lab in labels)
    print(header)
    for n in ns_all:
        row = f"{n:>3} | "
        cells = []
        for lab in labels:
            if lab in data and n in data[lab]:
                m, e, M = data[lab][n]
                cells.append(f"{m:6.1f}±{e:4.1f}({M:>2})")
            else:
                cells.append(f"{'—':>12}")
        print(row + " | ".join(cells))
    # Desviación máxima respecto de base (excluyendo N=30 singular)
    print("\n=== desviación |var - base| respecto de la calibración base (mm/s) ===")
    for lab in ["dx0125", "dx0500", "dt12", "dt48", "L1313"]:
        if lab not in data:
            continue
        difs = []
        difs_sat = None
        for n in data[lab]:
            if n in data["base"]:
                d = abs(data[lab][n][0] - data["base"][n][0])
                if n == 30:
                    difs_sat = d
                else:
                    difs.append(d)
        maxd = max(difs) if difs else float("nan")
        extra = f"  (N=30: {difs_sat:.1f})" if difs_sat is not None else ""
        print(f"  {lab:>8}: máx(N≤25) = {maxd:5.2f} mm/s{extra}")


if __name__ == "__main__":
    main()
