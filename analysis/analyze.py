#!/usr/bin/env python3
"""Orquestador del análisis posterior a la simulación.

Lee las salidas del motor en un directorio (``data/``), agrupa las realizaciones por
(**variante de R2**, orden, protocolo, p, N) según los metadatos de cada archivo, calcula los
observables y genera las figuras en ``figures/``. Nada se calcula durante la simulación: esto corre
después, sobre los archivos ya escritos.

IMPORTANTE: las corridas se agrupan por variante de R2 (``regla2``), orden, protocolo y ``p`` donde
corresponde. Mezclar esos metadatos en un mismo promedio sería comparar experimentos distintos y
reportar su diferencia como si fuera error entre realizaciones.

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


def _rule(run) -> str:
    return str(run.meta.get("regla2", "SIN_REGLA"))


def _order(run) -> str:
    return str(run.meta.get("order", "SIN_ORDEN"))


def _protocol(run) -> str:
    return str(run.meta.get("protocol", "FIXED_N"))


def _p(run) -> float:
    return float(run.meta["p"])


def _n_nominal(run) -> int:
    return int(run.meta["N"])


def group_fixed_runs(runs):
    """Agrupa corridas de N fijo sin mezclar variante, orden ni p."""
    groups = collections.defaultdict(list)
    for run in runs:
        if _protocol(run) != "FIXED_N":
            continue
        groups[(_rule(run), _order(run), _p(run), _n_nominal(run))].append(run)
    return dict(groups)


def group_fundamental_runs(runs):
    """Agrupa datos para diagrama fundamental sin mezclar variante, orden, protocolo ni p."""
    groups = collections.defaultdict(list)
    for run in runs:
        groups[(_rule(run), _order(run), _protocol(run), _p(run))].append(run)
    return dict(groups)


def select_representative_p(ps, requested=None) -> float:
    """Elige el p para PDFs de apoyo: pedido explícito, o el menor p positivo disponible."""
    values = sorted(float(p) for p in ps)
    if not values:
        raise ValueError("no hay valores de p disponibles")
    if requested is not None:
        requested = float(requested)
        if requested not in values:
            raise ValueError(f"p representativo {requested:g} no existe en las corridas: {values}")
        return requested
    positive = [p for p in values if p > 0]
    return positive[0] if positive else values[0]


def stationary_cut_step(steps, serie) -> int:
    """Mapea el índice sugerido por ``detect_stationary`` al paso real registrado."""
    steps = np.asarray(steps, dtype=int)
    if steps.size == 0:
        return 0
    cut_idx = int(obs.detect_stationary(serie))
    cut_idx = max(0, min(cut_idx, steps.size - 1))
    return int(steps[cut_idx])


def _step_groups(run):
    for step in np.unique(run.step):
        mask = run.step == step
        yield int(step), run.vid[mask], run.v_mmps[mask]


def incremental_speed_by_order(runs):
    """Velocidad media incremental por (regla, orden, p) y N activo.

    El header de una corrida incremental contiene el N nominal final. Para comparar contra el artículo
    se usa el N realmente activo en cada paso registrado, lo que además vuelve robusta la frontera de
    inserción si la salida está desplazada una muestra.
    """
    means_by_key_and_n = collections.defaultdict(lambda: collections.defaultdict(list))
    for run in runs:
        if _protocol(run) != "INCREMENTAL_180S":
            continue
        key = (_rule(run), _order(run), _p(run))
        values_by_n = collections.defaultdict(list)
        for _, vids, velocities in _step_groups(run):
            active_n = int(np.unique(vids).size)
            values_by_n[active_n].append(velocities)
        for active_n, chunks in values_by_n.items():
            values = np.concatenate(chunks)
            if values.size:
                means_by_key_and_n[key][active_n].append(float(np.mean(values)))

    summary = {}
    for key, by_n in means_by_key_and_n.items():
        ns = np.array(sorted(by_n), dtype=int)
        means = []
        errs = []
        for n in ns:
            per_run = np.array(by_n[int(n)], dtype=float)
            means.append(float(np.mean(per_run)))
            errs.append(float(np.std(per_run, ddof=1)) if per_run.size > 1 else float("nan"))
        summary[key] = (ns, np.array(means), np.array(errs))
    return summary


def _label_key(key) -> str:
    return "_".join(str(part).lower().replace(".", "") for part in key)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="../data")
    ap.add_argument("--figures-dir", default="../figures")
    ap.add_argument("--since-step", type=int, default=0,
                    help="corte del transitorio (por inspección; 0 = sin recorte, incluye el cuadro 0 "
                         "con v=0). Mirá la figura de evolución temporal para elegirlo.")
    ap.add_argument("--p-representativo", type=float, default=None,
                    help="p usado para PDFs de densidad/velocidad; por defecto, el menor p positivo disponible")
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

    fixed_groups = group_fixed_runs(runs)
    fixed_by_rule_order = collections.defaultdict(lambda: collections.defaultdict(list))
    fixed_ps = collections.defaultdict(set)
    for (rule, order, p, n), rs in fixed_groups.items():
        fixed_by_rule_order[(rule, order)][(p, n)].extend(rs)
        fixed_ps[(rule, order)].add(p)

    for (rule, order), by_pN in sorted(fixed_by_rule_order.items()):
        ps = sorted(fixed_ps[(rule, order)])
        ns_all = sorted({n for (_, n) in by_pN})
        tag = _label_key((rule, order, "fixed"))

        # ≈ Fig. 2: velocidad media vs N, una curva por p
        results_by_p = {}
        for p in ps:
            ns = sorted({n for (pp, n) in by_pN if pp == p})
            mean, err = zip(*(obs.mean_speed_with_error(by_pN[(p, n)], args.since_step) for n in ns))
            results_by_p[p] = (np.array(ns), np.array(mean), np.array(err))
        plots.plot_mean_speed_vs_n(results_by_p, figdir / f"velocidad_media_vs_N_{tag}.png")

        # ≈ Figs. 3 y 4: PDF de densidad y velocidad por N, a un p representativo (el menor)
        p_rep = select_representative_p(ps, args.p_representativo)
        dens, vels = {}, {}
        for n in ns_all:
            rs_p = by_pN.get((p_rep, n), [])
            if not rs_p:
                continue
            dens[n] = obs.density_pdf(rs_p, args.since_step, args.bins, rho_range=(0.0, 0.03))
            vels[n] = obs.velocity_pdf(rs_p, args.since_step, args.bins, v_range=(0.0, 130.0))
        if dens:
            plots.plot_density_pdf(dens, figdir / f"pdf_densidad_p{p_rep:g}_{tag}.png")
            plots.plot_velocity_pdf(vels, figdir / f"pdf_velocidad_p{p_rep:g}_{tag}.png")

        # evolución temporal (regla 4 de la cátedra) + sugerencia de estacionario, en un caso representativo
        n_rep = max(ns_all)
        rep = by_pN.get((p_rep, n_rep), next(iter(by_pN.values())))[0]
        steps, serie = obs.mean_speed_series(rep)
        cut = stationary_cut_step(steps, serie)
        plots.plot_time_evolution(
            {f"{rule} {order} (N={n_rep}, p={p_rep:g})": (steps, serie, cut)},
            figdir / f"evolucion_temporal_{tag}.png",
        )

    incremental_summary = incremental_speed_by_order(runs)
    incremental_by_rule_p = collections.defaultdict(dict)
    for (rule, order, p), values in incremental_summary.items():
        incremental_by_rule_p[(rule, p)][order] = values
    for (rule, p), by_order in sorted(incremental_by_rule_p.items()):
        tag = _label_key((rule, f"p{p:g}", "incremental"))
        plots.plot_mean_speed_vs_n(
            by_order,
            figdir / f"velocidad_media_incremental_{tag}.png",
            legend_title="orden de inserción",
        )

    # Diagramas fundamentales: UNA figura por (regla, protocolo) con pocas curvas legibles
    # (no todas las combinaciones juntas). FIXED_N → una curva por p; INCREMENTAL → una curva por
    # orden a un p representativo (≈ Fig. 5D del artículo).
    fd_groups = group_fundamental_runs(runs)  # (regla, orden, protocolo, p) -> corridas
    rules_fd = sorted({k[0] for k in fd_groups})
    protocols_fd = sorted({k[2] for k in fd_groups})
    for rule in rules_fd:
        for protocol in protocols_fd:
            keys = [k for k in fd_groups if k[0] == rule and k[2] == protocol]
            if not keys:
                continue
            orders_here = sorted({k[1] for k in keys})
            ps_here = sorted({k[3] for k in keys})
            curves, suffix, legend_title = {}, "", "frenado aleatorio"
            if protocol == "INCREMENTAL_180S" and len(orders_here) > 1:
                p_rep = select_representative_p(ps_here)
                for order in orders_here:
                    rs = fd_groups.get((rule, order, protocol, p_rep), [])
                    if rs:
                        curves[order] = obs.fundamental_diagram(rs, args.since_step, window=args.fd_window)
                suffix, legend_title = f"_p{p_rep:g}", "orden de inserción"
            else:
                for p in ps_here:
                    rs = [r for k in keys if k[3] == p for r in fd_groups[k]]
                    curves[p] = obs.fundamental_diagram(rs, args.since_step, window=args.fd_window)
            if curves:
                tag = _label_key((rule, protocol))
                plots.plot_fundamental_diagram(
                    curves, figdir / f"diagrama_fundamental_{tag}{suffix}.png", legend_title=legend_title)
    print(f"figuras generadas en {figdir}")


if __name__ == "__main__":
    main()
