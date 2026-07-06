import math
import sys

import numpy as np
import pytest

import analyze
import observables as obs
from run_io import Run


def make_run(*, rule="CONTACTO_PURO", protocol="FIXED_N", order="RANDOM", n=5, p=0.1, dt=1.0, steps=None,
             speeds=None, ids=None, realizacion_id=1, output_every=1):
    if speeds is None:
        speeds = np.full((2, n), 100.0)
    if isinstance(speeds, np.ndarray):
        if speeds.ndim == 1:
            speed_rows = [speeds.astype(float)]
        else:
            speed_rows = [row.astype(float) for row in speeds]
    else:
        speed_rows = [np.asarray(row, dtype=float) for row in speeds]
    rows = len(speed_rows)
    if steps is None:
        steps = np.arange(rows)
    steps = np.asarray(steps, dtype=int)
    if ids is None:
        ids = np.concatenate([np.arange(row.size) for row in speed_rows])
    else:
        ids = np.asarray(ids, dtype=int)
    meta = {
        "regla2": rule,
        "protocol": protocol,
        "order": order,
        "N": n,
        "p": p,
        "dt_s": dt,
        "ell_celdas": 1,
        "dx_mm": 1.0,
        "L_celdas": 1000,
        "realizacion_id": realizacion_id,
        "output_every": output_every,
    }
    return Run(
        meta=meta,
        step=np.concatenate([np.full(row.size, step, dtype=int) for step, row in zip(steps, speed_rows)]),
        vid=ids,
        x_mm=np.zeros(sum(row.size for row in speed_rows)),
        v_mmps=np.concatenate(speed_rows),
    )


def test_fixed_groups_canonicalizan_order_legacy_como_sin_orden():
    fixed_random = make_run(protocol="FIXED_N", order="RANDOM", n=10, speeds=[[80.0]], realizacion_id=1)
    fixed_ascending = make_run(protocol="FIXED_N", order="ASCENDING", n=10, speeds=[[100.0]], realizacion_id=2)
    incremental = make_run(protocol="INCREMENTAL_180S", order="RANDOM", n=30, speeds=[[120.0]])

    groups = analyze.group_fixed_runs([fixed_random, fixed_ascending, incremental])

    assert set(groups) == {("CONTACTO_PURO", "SIN_ORDEN", 0.1, 10)}
    assert groups[("CONTACTO_PURO", "SIN_ORDEN", 0.1, 10)] == [fixed_random, fixed_ascending]


def test_fixed_groups_rechazan_corridas_duplicadas_por_clave_logica():
    original = make_run(protocol="FIXED_N", order="RANDOM", n=10, p=0.1, realizacion_id=7, output_every=10)
    renamed_copy = make_run(protocol="FIXED_N", order="ASCENDING", n=10, p=0.1, realizacion_id=7,
                            output_every=10)

    with pytest.raises(ValueError, match="duplicada"):
        analyze.group_fixed_runs([original, renamed_copy])


def test_incremental_speed_groups_windows_by_actual_vehicle_count_and_order():
    # dt=60 s => cada ventana de 180 s contiene 3 pasos registrados.
    run_a = make_run(
        protocol="INCREMENTAL_180S",
        order="ASCENDING",
        n=30,
        dt=60.0,
        steps=[0, 1, 2, 3, 4, 5],
        speeds=[
            [10.0] * 5,
            [10.0] * 5,
            [10.0] * 5,
            [20.0] * 10,
            [20.0] * 10,
            [20.0] * 10,
        ],
    )
    run_b = make_run(
        protocol="INCREMENTAL_180S",
        order="ASCENDING",
        n=30,
        dt=60.0,
        realizacion_id=2,
        steps=[0, 1, 2, 3, 4, 5],
        speeds=[
            [14.0] * 5,
            [14.0] * 5,
            [14.0] * 5,
            [24.0] * 10,
            [24.0] * 10,
            [24.0] * 10,
        ],
    )

    summary = analyze.incremental_speed_by_order([run_a, run_b])

    assert set(summary) == {("CONTACTO_PURO", "ASCENDING", 0.1)}
    ns, means, errs = summary[("CONTACTO_PURO", "ASCENDING", 0.1)]
    assert ns.tolist() == [5, 10]
    assert means.tolist() == [12.0, 22.0]
    assert np.allclose(errs, [math.sqrt(8.0), math.sqrt(8.0)])


def test_incremental_speed_rechaza_corridas_duplicadas_por_clave_logica():
    original = make_run(protocol="INCREMENTAL_180S", order="ASCENDING", n=30, p=0.1, speeds=[[10.0] * 5],
                        realizacion_id=3, output_every=10)
    renamed_copy = make_run(protocol="INCREMENTAL_180S", order="ASCENDING", n=30, p=0.1, speeds=[[20.0] * 5],
                            realizacion_id=3, output_every=10)

    with pytest.raises(ValueError, match="duplicada"):
        analyze.incremental_speed_by_order([original, renamed_copy])


def test_stationary_cut_uses_recorded_step_not_sample_index():
    steps = np.array([0, 5, 10, 15, 20])
    serie = np.array([0.0, 50.0, 100.0, 100.0, 100.0])

    cut_step = analyze.stationary_cut_step(steps, serie)

    assert cut_step in steps
    assert cut_step != obs.detect_stationary(serie)


def test_fundamental_groups_no_mezclan_p():
    runs = [
        make_run(p=0.0, n=5, speeds=[[80.0, 80.0]]),
        make_run(p=0.2, n=5, speeds=[[40.0, 40.0]]),
    ]

    groups = analyze.group_fundamental_runs(runs)

    assert set(groups) == {
        ("CONTACTO_PURO", "SIN_ORDEN", "FIXED_N", 0.0),
        ("CONTACTO_PURO", "SIN_ORDEN", "FIXED_N", 0.2),
    }
    assert groups[("CONTACTO_PURO", "SIN_ORDEN", "FIXED_N", 0.0)] == [runs[0]]
    assert groups[("CONTACTO_PURO", "SIN_ORDEN", "FIXED_N", 0.2)] == [runs[1]]


def test_p_representativo_prefiere_menor_positivo():
    assert analyze.select_representative_p([0.0, 0.2, 0.1]) == 0.1
    assert analyze.select_representative_p([0.0]) == 0.0
    assert analyze.select_representative_p([0.0, 0.1], requested=0.1) == 0.1


def test_main_falla_si_p_representativo_pedido_falta_en_un_grupo(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    fig_dir = tmp_path / "figures"
    data_dir.mkdir()
    (data_dir / "N5_p01.txt").write_text(
        "\n".join([
            "# regla2=CONTACTO_PURO",
            "# N=5 p=0.100000 order=SIN_ORDEN protocol=FIXED_N realizacion_id=1 output_every=1",
            "# dt_s=1.000000 ell_celdas=1 dx_mm=1.000000 L_celdas=1000",
            "0 0 0.0 10.0",
            "0 1 500.0 10.0",
            "1 0 10.0 10.0",
            "1 1 510.0 10.0",
            "",
        ])
    )
    for name in (
        "plot_mean_speed_vs_n",
        "plot_density_pdf",
        "plot_velocity_pdf",
        "plot_time_evolution",
        "plot_fundamental_diagram",
    ):
        monkeypatch.setattr(analyze.plots, name, lambda *args, **kwargs: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze.py",
            "--data-dir", str(data_dir),
            "--figures-dir", str(fig_dir),
            "--p-representativo", "0.2",
        ],
    )

    with pytest.raises(ValueError, match="p representativo 0.2"):
        analyze.main()
