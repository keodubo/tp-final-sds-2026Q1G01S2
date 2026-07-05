#!/usr/bin/env python3
"""Validación del motor contra el diagrama fundamental TRIANGULAR analítico.

Con la variante clásica (B) en su régimen de validez —partículas puntuales (ℓ=1), velocidad máxima
homogénea, p=0 y condición inicial de reparto uniforme (--even-spread)— el estado estacionario del
NaSch canónico es v̄ = min(vmax, g) y el flujo Q = ρ·v̄ debe coincidir con

    Q(ρ) = min(ρ·vmax, 1 − ρ).

Este script barre la densidad variando el hueco g (con L = n·(1+g), ℓ=1), corre el motor por CLI y
compara Q_simulado con Q_analítico, generando figures/validacion_triangular.png. Es la contraparte
gráfica del test JUnit deterministaReproduceDiagramaFundamentalAnalitico (que valida a 1e-9).

Uso:  python3 validacion.py [--jar ...] [--figures-dir ../figures]
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import plots
from run_io import load_run

VMAX = 5
N = 20
TRANSIENT = 60
MEASURE = 60


def q_simulado(jar: str, gap: int, tmpdir: Path) -> tuple[float, float]:
    """Corre una densidad (hueco ``gap``) y devuelve (ρ, Q_sim) en unidades de malla (Δx=Δt=1)."""
    lattice = N * (1 + gap)          # ℓ=1 ⇒ hueco exactamente g entre vehículos equiespaciados
    out = tmpdir / f"val_g{gap}.txt"
    cmd = [
        "java", "-jar", jar,
        "--rule", "CLASICA_SALVO_CERO", "--protocol", "FIXED_N", "--even-spread",
        "--n", str(N), "--ell", "1", "--L", str(lattice),
        "--dx", "1", "--dt", "1", "--vfree-min", str(VMAX), "--vfree-max", str(VMAX),
        "--p", "0", "--steps", str(TRANSIENT + MEASURE), "--output-every", "1",
        "--out", str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    run = load_run(out)
    # con Δv=1 la columna v_mmps ya está en celdas/paso; promediar la cola estacionaria
    v = run.v_mmps[run.step >= TRANSIENT]
    vbar = float(np.mean(v))
    rho = N / lattice
    return rho, rho * vbar


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", default="../engine/target/nasch-vdv-1.0-SNAPSHOT.jar")
    ap.add_argument("--figures-dir", default="../figures")
    args = ap.parse_args()

    gaps = [1, 2, 3, 4, 5, 6, 8, 10, 14, 20]  # cubre la rama congestionada, el pico y el flujo libre
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        pts = [q_simulado(args.jar, g, tmp) for g in gaps]
    rho_sim = np.array([p[0] for p in pts])
    q_sim = np.array([p[1] for p in pts])

    rho_teo = np.linspace(0, 1, 400)
    q_teo = np.minimum(rho_teo * VMAX, 1 - rho_teo)

    plots.configure()
    fig, ax = plt.subplots(figsize=plots.FIGSIZE)
    ax.plot(rho_teo, q_teo, "-", color="tab:blue", label=r"analítico $\min(\rho\,v_{max},1-\rho)$")
    ax.plot(rho_sim, q_sim, "o", color="tab:red", ms=9, label="simulado (variante clásica)")
    ax.set_xlabel(r"densidad $\rho$ (veh/celda)")
    ax.set_ylabel(r"flujo $Q=\rho\,\bar v$ (veh/paso)")
    ax.legend(title=f"$v_{{max}}={VMAX}$, $p=0$, reparto uniforme")
    figdir = Path(args.figures_dir)
    figdir.mkdir(parents=True, exist_ok=True)
    outfile = figdir / "validacion_triangular.png"
    fig.savefig(outfile)
    plt.close(fig)

    err = np.max(np.abs(q_sim - np.minimum(rho_sim * VMAX, 1 - rho_sim)))
    print(f"validación triangular: {outfile} (error máx |Q_sim - Q_teo| = {err:.2e})")


if __name__ == "__main__":
    main()
