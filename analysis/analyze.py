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
import csv
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
    if _protocol(run) == "FIXED_N":
        return "SIN_ORDEN"
    return str(run.meta.get("order", "SIN_ORDEN"))


def _protocol(run) -> str:
    return str(run.meta.get("protocol", "FIXED_N"))


def _p(run) -> float:
    return float(run.meta["p"])


def _n_nominal(run) -> int:
    return int(run.meta["N"])


def _realizacion_id(run):
    for key in ("realizacion_id", "realization_seed", "seed"):
        if key in run.meta:
            return run.meta[key]
    return None


# Traducción de los enums internos del motor a texto legible en español para las etiquetas VISIBLES
# de las figuras (títulos, leyendas, curvas). NO se usa para nombres de archivo ni claves de
# agrupamiento: esos siguen con los enums en minúscula (los .tex del informe los referencian así).
_ETIQUETAS_ES = {
    "CONTACTO_PURO": "contacto puro",
    "CLASICA_SALVO_CERO": "clásica",
    "FIXED_N": "N fijo",
    "INCREMENTAL_180S": "incremental",
    "ASCENDING": "creciente",
    "DESCENDING": "decreciente",
    "RANDOM": "aleatorio",
}


def _es_label(value) -> str:
    """Mapea un enum interno a su etiqueta en español para el texto visible de las figuras."""
    return _ETIQUETAS_ES.get(str(value), str(value))


def _logical_run_key(run):
    # La cadencia de muestreo (output_every) NO es parte de la identidad física de una realización:
    # muestrear la misma corrida a dos cadencias sigue siendo la MISMA realización (mismo protocolo,
    # regla, orden, p, N, realizacion_id). Incluir output_every dejaría pasar ese duplicado y lo
    # promediaría dos veces, inflando M y achicando el desvío entre realizaciones.
    return (_protocol(run), _rule(run), _order(run), _p(run), _n_nominal(run),
            _realizacion_id(run))


def ensure_no_duplicate_runs(runs) -> None:
    """Falla si dos archivos representan la misma realización lógica.

    El nombre del archivo no forma parte del experimento. Si una corrida se copió o renombró, contarla
    dos veces inflaría M y achicaría artificialmente el desvío entre realizaciones.
    """
    seen = set()
    for run in runs:
        key = _logical_run_key(run)
        if key in seen:
            raise ValueError(f"corrida duplicada para clave logica {key}")
        seen.add(key)


def group_fixed_runs(runs):
    """Agrupa corridas de N fijo sin mezclar variante, orden ni p."""
    ensure_no_duplicate_runs(runs)
    groups = collections.defaultdict(list)
    for run in runs:
        if _protocol(run) != "FIXED_N":
            continue
        groups[(_rule(run), _order(run), _p(run), _n_nominal(run))].append(run)
    return dict(groups)


def group_fundamental_runs(runs):
    """Agrupa datos para diagrama fundamental sin mezclar variante, orden, protocolo ni p."""
    ensure_no_duplicate_runs(runs)
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
    ensure_no_duplicate_runs(runs)
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


def write_manifest(runs, since_step_fixed, figdir) -> Path:
    """Escribe un manifiesto CSV con las **realizaciones efectivas (M)** y el corte (since_step) POR
    FILA (regla, orden, protocolo, p, N). El corte se registra por protocolo: en FIXED_N es el corte
    por inspección (``since_step_fixed``); en INCREMENTAL_180S es 0 porque se promedia la ventana
    completa de 180 s por fase (⟨L_i/180 s⟩ del artículo). En el incremental, N es el N ACTIVO real y M
    cuenta cuántas realizaciones lo alcanzaron. Da trazabilidad a las figuras."""
    rows = []
    for (rule, order, p, n), rs in group_fixed_runs(runs).items():
        rows.append(("FIXED_N", rule, order, p, n, len(rs), since_step_fixed))
    inc = collections.defaultdict(list)  # (regla, orden, p) -> [N activo máximo por realización]
    for r in runs:
        if _protocol(r) != "INCREMENTAL_180S":
            continue
        last = r.step.max()
        max_activo = int(np.unique(r.vid[r.step == last]).size)
        inc[(_rule(r), _order(r), _p(r))].append(max_activo)
    for (rule, order, p), maxes in inc.items():
        for n in range(5, max(maxes) + 1, 5):
            rows.append(("INCREMENTAL_180S", rule, order, p, n, sum(1 for x in maxes if x >= n), 0))
    path = Path(figdir) / "manifiesto.csv"
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["protocolo", "regla", "orden", "p", "N", "M_realizaciones", "since_step"])
        for row in sorted(rows, key=lambda r: (r[0], r[1], r[2], float(r[3]), r[4])):
            w.writerow(list(row))
    return path


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

        # ≈ Figs. 3 y 4: PDF de densidad y velocidad por N, a un p representativo. Si el p pedido no
        # existe en ESTE grupo (regla, orden), se aborta: cambiar de p silenciosamente genera figuras
        # engañosas.
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

        # evolución temporal (regla 4 de la cátedra) + sugerencia de estacionario, en un caso
        # representativo. Eje temporal en SEGUNDOS (t = paso · dt), no en pasos.
        ns_rep = sorted(n for (p, n) in by_pN if p == p_rep)
        n_rep = max(ns_rep)
        rep = by_pN[(p_rep, n_rep)][0]
        dt = float(rep.meta["dt_s"])
        steps, serie = obs.mean_speed_series(rep)
        # La línea punteada marca el corte del estacionario REALMENTE usado para el observable:
        # args.since_step, elegido por inspección de esta misma figura y registrado en manifiesto.csv.
        # detect_stationary/stationary_cut_step siguen definidas y testeadas, pero YA NO tienen call-site
        # en este pipeline (no alimentan ni el corte dibujado ni el manifiesto). Así figura y epígrafe
        # ("promedio a partir de ese corte") quedan consistentes. Para FIXED_N el orden es SIN_ORDEN y no
        # se muestra.
        plots.plot_time_evolution(
            {f"{_es_label(rule)} (N={n_rep}, p={p_rep:g})": (steps * dt, serie, args.since_step * dt)},
            figdir / f"evolucion_temporal_{tag}.png",
        )

    incremental_summary = incremental_speed_by_order(runs)
    incremental_by_rule_p = collections.defaultdict(dict)
    for (rule, order, p), values in incremental_summary.items():
        incremental_by_rule_p[(rule, p)][_es_label(order)] = values
    for (rule, p), by_order in sorted(incremental_by_rule_p.items()):
        tag = _label_key((rule, f"p{p:g}", "incremental"))
        # ≈ Fig. 2: velocidad media vs N, una curva por orden de inserción
        plots.plot_mean_speed_vs_n(
            by_order,
            figdir / f"velocidad_media_incremental_{tag}.png",
            legend_title="orden de inserción",
        )

    # Incremental: evolución temporal por orden (regla 4 / EST-2: sin esta figura no se puede elegir
    # el estacionario por inspección) y PDFs de densidad/velocidad por N ACTIVO (≈ Figs. 3 y 4 por
    # orden, FIG-01/02). Se usan sobre la ventana COMPLETA de 180 s por fase (replica ⟨L_i/180 s⟩ del
    # artículo; el transitorio de empuje por fase se documenta como limitación en el informe).
    incr_runs = collections.defaultdict(list)          # (regla, orden, p) -> corridas
    incr_ps_by_rule = collections.defaultdict(set)
    for r in runs:
        if _protocol(r) == "INCREMENTAL_180S":
            incr_runs[(_rule(r), _order(r), _p(r))].append(r)
            incr_ps_by_rule[_rule(r)].add(_p(r))
    orders_canon = ["ASCENDING", "DESCENDING", "RANDOM"]
    for rule, ps in sorted(incr_ps_by_rule.items()):
        p_rep = select_representative_p(sorted(ps), args.p_representativo)
        # evolución temporal: una curva por orden (una realización representativa cada una), en segundos
        evo = {}
        for order in orders_canon:
            rs = incr_runs.get((rule, order, p_rep), [])
            if not rs:
                continue
            dt = float(rs[0].meta["dt_s"])
            steps, serie = obs.mean_speed_series(rs[0])
            evo[_es_label(order)] = (steps * dt, serie, None)
        if evo:
            etag = _label_key((rule, f"p{p_rep:g}", "incremental"))
            plots.plot_time_evolution(evo, figdir / f"evolucion_temporal_incremental_{etag}.png")
        # PDFs por N activo: una figura por orden (los paneles A/B/C del artículo)
        for order in orders_canon:
            rs = incr_runs.get((rule, order, p_rep), [])
            if not rs:
                continue
            otag = _label_key((rule, order, f"p{p_rep:g}", "incremental"))
            dens = obs.density_pdf_by_active_n(rs, since_step=0, bins=args.bins, rho_range=(0.0, 0.03))
            vels = obs.velocity_pdf_by_active_n(rs, since_step=0, bins=args.bins, v_range=(0.0, 130.0))
            if dens:
                plots.plot_density_pdf(dens, figdir / f"pdf_densidad_incremental_{otag}.png")
            if vels:
                plots.plot_velocity_pdf(vels, figdir / f"pdf_velocidad_incremental_{otag}.png")

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
            # Criterio de estacionario CONSISTENTE con velocidad-vs-N (EST-1): FIXED_N usa el corte por
            # inspección (args.since_step); INCREMENTAL_180S usa la ventana completa (0), que replica
            # ⟨L_i/180 s⟩ del artículo. Antes el FD incremental recortaba solo la fase 1 (incoherente).
            cut = args.since_step if protocol == "FIXED_N" else 0
            if protocol == "INCREMENTAL_180S" and len(orders_here) > 1:
                p_rep = select_representative_p(ps_here, args.p_representativo)
                for order in orders_here:
                    rs = fd_groups.get((rule, order, protocol, p_rep), [])
                    if rs:
                        curves[_es_label(order)] = obs.fundamental_diagram(rs, cut, window=args.fd_window)
                suffix, legend_title = f"_p{p_rep:g}", "orden de inserción"
            else:
                for p in ps_here:
                    rs = [r for k in keys if k[3] == p for r in fd_groups[k]]
                    curves[p] = obs.fundamental_diagram(rs, cut, window=args.fd_window)
            if curves:
                tag = _label_key((rule, protocol))
                plots.plot_fundamental_diagram(
                    curves, figdir / f"diagrama_fundamental_{tag}{suffix}.png", legend_title=legend_title)

    manifiesto = write_manifest(runs, args.since_step, figdir)
    print(f"figuras generadas en {figdir} (manifiesto: {manifiesto}, since_step={args.since_step})")


if __name__ == "__main__":
    main()
