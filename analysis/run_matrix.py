#!/usr/bin/env python3
"""Orquesta el barrido de experimentos invocando el motor (jar de Java).

Recorre la matriz N × p × variante × realizaciones y corre una simulación por combinación,
guardando cada salida en ``data/``. Una realización queda identificada por el valor técnico
``--seed`` que recibe el motor.

Ejemplos:
    python3 run_matrix.py --dry-run                  # muestra los comandos sin correr
    python3 run_matrix.py --n 5 10 15 --p 0 0.1 0.3 --realizations 30
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
from pathlib import Path

DEFAULT_JAR = "../engine/target/nasch-vdv-1.0-SNAPSHOT.jar"
DEFAULT_OUT = "../data"


def build_command(jar: str, out_dir: Path, n: int, p: float, rule: str, order: str,
                  protocol: str, realization: int, steps: int, output_every: int) -> tuple[list[str], Path]:
    tag = f"N{n}_p{p}_{rule}_{order}_{protocol}_r{realization}".replace(".", "")
    out_file = out_dir / f"{tag}.txt"
    cmd = [
        "java", "-jar", jar,
        "--n", str(n),
        "--p", str(p),
        "--rule", rule,
        "--order", order,
        "--protocol", protocol,
        "--seed", str(realization),
        "--steps", str(steps),
        "--output-every", str(output_every),
        "--out", str(out_file),
    ]
    return cmd, out_file


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", default=DEFAULT_JAR)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--n", type=int, nargs="+", default=[5, 10, 15, 20, 25, 30])
    ap.add_argument("--p", type=float, nargs="+", default=[0.0, 0.1, 0.2, 0.3, 0.4])
    ap.add_argument("--rule", nargs="+", default=["CLASICA_SALVO_CERO", "CONTACTO_PURO"],
                    choices=["CONTACTO_PURO", "CLASICA_SALVO_CERO"])
    ap.add_argument("--order", nargs="+", default=["ASCENDING", "DESCENDING", "RANDOM"],
                    choices=["ASCENDING", "DESCENDING", "RANDOM"])
    ap.add_argument("--protocol", nargs="+", default=["FIXED_N", "INCREMENTAL_180S"],
                    choices=["FIXED_N", "INCREMENTAL_180S"])
    ap.add_argument("--realizations", type=int, default=30, help="cantidad de realizaciones")
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--output-every", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="solo imprime los comandos")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    combos = list(itertools.product(
        args.n, args.p, args.rule, args.order, args.protocol, range(1, args.realizations + 1)
    ))
    print(
        f"{len(combos)} corridas (N={args.n} × p={args.p} × reglas={args.rule} "
        f"× órdenes={args.order} × protocolos={args.protocol} × {args.realizations} realizaciones)"
    )

    for n, p, rule, order, protocol, realization in combos:
        cmd, out_file = build_command(
            args.jar, out_dir, n, p, rule, order, protocol, realization, args.steps, args.output_every
        )
        if args.dry_run:
            print(" ".join(cmd))
        else:
            subprocess.run(cmd, check=True)
            print("ok →", out_file)


if __name__ == "__main__":
    main()
