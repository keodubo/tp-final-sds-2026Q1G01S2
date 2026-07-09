#!/usr/bin/env python3
"""Estudio de sensibilidad de la calibración: dt, L y Δx (exigido por la cátedra).

Corre el punto físicamente comparable (contacto puro, p=0.1, protocolo N fijo, curva v̄ vs N) bajo
variaciones controladas de la malla, manteniendo FIJO el resto de la física (velocidades libres por
seed, geometría de 44 mm por vehículo, tiempo físico ≈417 s) y comparando el observable en unidades
físicas (mm/s). Como vfree depende sólo del seed, cada realización r es la MISMA población física en
todas las variaciones (comparación pareada); lo único que cambia es la discretización.

Tres botones (cada uno deja los otros dos anclados a la calibración base):
  * Δx  : 0.125 / 0.25 / 0.5 mm  (dt=1/24 fijo)  → ℓ=44/Δx celdas, Δv=Δx/dt = 3/6/12 mm/s
  * dt  : 1/12 / 1/24 / 1/48 s   (Δx=0.25 fijo) → Δv = 3/6/12 mm/s, pasos = 5000/10000/20000
  * L   : 1313 vs 1320 mm        (Δx=0.25, dt=1/24) → N≤25 (N=30 sólo cierra a contacto en 1320)

Salida a ../data_sens/. Analizar con analyze_sensitivity.py.

Ejemplo:
    python3 run_sensitivity.py --realizations 30
    python3 run_sensitivity.py --dry-run
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

DEFAULT_JAR = "../engine/target/nasch-vdv-1.0-SNAPSHOT.jar"
DEFAULT_OUT = "../data_sens"
T_PHYS_S = 10_000 / 24.0        # tiempo físico de la corrida base (≈416.7 s), fijo en todas
ELL_MM = 44.0                   # largo físico de vehículo (invariante)
NULL_L_MM_BASE = 1320.0         # L base (=30·44 mm)
OUTPUT_EVERY = 10

# dt como cadena de alta precisión (el motor derivará Δv=Δx/dt y vmax=round(vfree/Δv)).
DT = {12: "0.0833333333333333", 24: "0.0416666666666667", 48: "0.0208333333333333"}
NS_FULL = [5, 10, 15, 20, 25, 30]
NS_NO_SAT = [5, 10, 15, 20, 25]   # sin N=30 (no cierra a contacto si L<1320)


def _steps_for(fps: int) -> int:
    return round(T_PHYS_S * fps)


def variations() -> list[dict]:
    """Cada variación: etiqueta, Δx[mm], fps(=1/dt), ℓ[celdas], L[celdas], Ns."""
    v: list[dict] = []
    # --- base (referencia; Δx=0.25, dt=1/24, L=1320) ---
    v.append(dict(label="base", dx=0.25, fps=24, ell=176, L=5280, ns=NS_FULL))
    # --- botón Δx (dt=1/24 fijo) ---
    v.append(dict(label="dx0125", dx=0.125, fps=24, ell=352, L=10560, ns=NS_FULL))
    v.append(dict(label="dx0500", dx=0.5, fps=24, ell=88, L=2640, ns=NS_FULL))
    # --- botón dt (Δx=0.25 fijo) ---
    v.append(dict(label="dt12", dx=0.25, fps=12, ell=176, L=5280, ns=NS_FULL))
    v.append(dict(label="dt48", dx=0.25, fps=48, ell=176, L=5280, ns=NS_FULL))
    # --- botón L (Δx=0.25, dt=1/24) : 1313 mm = 5252 celdas ---
    v.append(dict(label="L1313", dx=0.25, fps=24, ell=176, L=5252, ns=NS_NO_SAT))
    return v


def build_command(jar, out_dir, var, n, r):
    dx = var["dx"]
    label = var["label"]
    tag = f"SENS_{label}_N{n}_p01_CONTACTO_PURO_r{r}"
    out_file = out_dir / f"{tag}.txt"
    cmd = [
        "java", "-jar", jar,
        "--rule", "CONTACTO_PURO",
        "--protocol", "FIXED_N",
        "--n", str(n),
        "--p", "0.1",
        "--dx", f"{dx}",
        "--dt", DT[var["fps"]],
        "--ell", str(var["ell"]),
        "--L", str(var["L"]),
        "--steps", str(_steps_for(var["fps"])),
        "--output-every", str(OUTPUT_EVERY),
        "--seed", str(r),
        "--out", str(out_file),
    ]
    return cmd, out_file


def _last_step(path: Path):
    last = None
    with open(path) as fh:
        for line in fh:
            if line and not line.startswith("#"):
                try:
                    last = int(line.split(None, 1)[0])
                except ValueError:
                    pass
    return last


def is_complete(path: Path, fps: int) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    steps = _steps_for(fps)
    expected_last = ((steps - 1) // OUTPUT_EVERY) * OUTPUT_EVERY
    last = _last_step(path)
    return last is not None and last >= expected_last


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", default=DEFAULT_JAR)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--realizations", type=int, default=30)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-existing", action="store_true", default=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(var, n, r) for var in variations() for n in var["ns"]
            for r in range(1, args.realizations + 1)]
    print(f"{len(jobs)} corridas de sensibilidad | variaciones={[v['label'] for v in variations()]} "
          f"realizaciones={args.realizations}")

    done = skipped = 0
    for var, n, r in jobs:
        cmd, out_file = build_command(args.jar, out_dir, var, n, r)
        if args.dry_run:
            print(" ".join(cmd))
        elif args.skip_existing and is_complete(out_file, var["fps"]):
            skipped += 1
        else:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
            done += 1
    if not args.dry_run:
        print(f"listo: {done} nuevas, {skipped} completas salteadas")


if __name__ == "__main__":
    main()
