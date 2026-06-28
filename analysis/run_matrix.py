#!/usr/bin/env python3
"""Orquesta el barrido de experimentos invocando el motor (jar de Java).

Por defecto corre el NÚCLEO que pidió el profe: variar N y p con protocolo de N fijo
(``N × p × variante × realizaciones``). Los órdenes de inserción (ascending/descending/random) y el
protocolo incremental cada 180 s son la CAPA DE COMPARACIÓN con el artículo (Figs. 2-5); están
disponibles de forma opcional y pendientes de confirmar el alcance con el profe (ver diseño §6/§11).

Reglas de combinación (para no generar corridas sin sentido):
- ``FIXED_N``: el orden de inserción es irrelevante (no hay historia de inserción) → no se cruza con
  ``--order``.
- ``INCREMENTAL_180S``: el protocolo define su propia progresión 5→30 → no se cruza con ``--n``; ahí
  sí importan los tres órdenes.

Una realización queda identificada por el valor técnico ``--seed`` que recibe el motor.

Ejemplos:
    python3 run_matrix.py --dry-run                          # núcleo: N×p, N fijo
    python3 run_matrix.py --protocol INCREMENTAL_180S \\
        --order ASCENDING DESCENDING RANDOM \\
        --rule CONTACTO_PURO CLASICA_SALVO_CERO --dry-run    # capa de comparación con el artículo
"""
from __future__ import annotations

import argparse
import itertools
import subprocess
from pathlib import Path

DEFAULT_JAR = "../engine/target/nasch-vdv-1.0-SNAPSHOT.jar"
DEFAULT_OUT = "../data"
FIXED_STEPS = 10_000          # ventana de ~180 s + transitorio
INCREMENTAL_STEPS = 25_920    # 6 fases × 180 s × 24 fps (el protocolo va de N=5 a N=30)
NOMINAL_N_INCREMENTAL = 30    # nominal: el protocolo incremental define su propia progresión 5→30


def build_command(jar, out_dir, *, n, p, rule, protocol, realization, steps, output_every, order=None):
    if protocol == "INCREMENTAL_180S":
        tag = f"INC_p{p}_{rule}_{order}_r{realization}".replace(".", "")
    else:
        tag = f"N{n}_p{p}_{rule}_FIXED_N_r{realization}".replace(".", "")
    out_file = out_dir / f"{tag}.txt"
    cmd = [
        "java", "-jar", jar,
        "--n", str(n),
        "--p", str(p),
        "--rule", rule,
        "--protocol", protocol,
        "--seed", str(realization),
        "--steps", str(steps),
        "--output-every", str(output_every),
        "--out", str(out_file),
    ]
    if order is not None:
        cmd += ["--order", order]
    return cmd, out_file


def build_jobs(args) -> list[dict]:
    """Genera las corridas respetando la semántica de cada protocolo (sin cruces redundantes)."""
    fixed_steps = args.steps if args.steps is not None else FIXED_STEPS
    incr_steps = args.steps if args.steps is not None else INCREMENTAL_STEPS
    realizations = range(1, args.realizations + 1)
    jobs: list[dict] = []
    for protocol in args.protocol:
        if protocol == "FIXED_N":
            for n, p, rule, r in itertools.product(args.n, args.p, args.rule, realizations):
                jobs.append(dict(n=n, p=p, rule=rule, protocol=protocol, order=None,
                                 realization=r, steps=fixed_steps))
        elif protocol == "INCREMENTAL_180S":
            for p, rule, order, r in itertools.product(args.p, args.rule, args.order, realizations):
                jobs.append(dict(n=NOMINAL_N_INCREMENTAL, p=p, rule=rule, protocol=protocol,
                                 order=order, realization=r, steps=incr_steps))
    return jobs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jar", default=DEFAULT_JAR)
    ap.add_argument("--out-dir", default=DEFAULT_OUT)
    ap.add_argument("--n", type=int, nargs="+", default=[5, 10, 15, 20, 25, 30])
    ap.add_argument("--p", type=float, nargs="+", default=[0.0, 0.1, 0.2, 0.3, 0.4])
    # núcleo: variante de validación primero (ambas siguen disponibles en la capa de comparación)
    ap.add_argument("--rule", nargs="+", default=["CLASICA_SALVO_CERO"],
                    choices=["CONTACTO_PURO", "CLASICA_SALVO_CERO"])
    # los órdenes solo se usan bajo INCREMENTAL_180S
    ap.add_argument("--order", nargs="+", default=["RANDOM"],
                    choices=["ASCENDING", "DESCENDING", "RANDOM"])
    # por defecto solo el núcleo (N fijo); el incremental es opt-in
    ap.add_argument("--protocol", nargs="+", default=["FIXED_N"],
                    choices=["FIXED_N", "INCREMENTAL_180S"])
    ap.add_argument("--realizations", type=int, default=30, help="cantidad de realizaciones")
    ap.add_argument("--steps", type=int, default=None,
                    help="por defecto 10000 (N fijo) / 25920 (incremental)")
    ap.add_argument("--output-every", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="solo imprime los comandos")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = build_jobs(args)
    print(
        f"{len(jobs)} corridas | protocolos={args.protocol} N={args.n} p={args.p} "
        f"reglas={args.rule} órdenes(incremental)={args.order} realizaciones={args.realizations}"
    )

    for job in jobs:
        cmd, out_file = build_command(args.jar, out_dir, output_every=args.output_every, **job)
        if args.dry_run:
            print(" ".join(cmd))
        else:
            subprocess.run(cmd, check=True)
            print("ok →", out_file)


if __name__ == "__main__":
    main()
