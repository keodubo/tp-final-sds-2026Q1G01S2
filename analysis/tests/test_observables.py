"""Tests blackbox (solo comportamiento observable) de los observables, sobre datos sintéticos."""
import numpy as np

import observables as obs
from run_io import Run


def make_run(x_mm, v_mmps, n, ell=176, dx=0.25, lattice=5280):
    """Construye un Run sintético. x_mm/v_mmps: 2D (pasos, n) o 1D (un paso)."""
    x = np.atleast_2d(np.asarray(x_mm, dtype=float))
    v = np.atleast_2d(np.asarray(v_mmps, dtype=float))
    n_steps = x.shape[0]
    meta = {"N": n, "ell_celdas": ell, "dx_mm": dx, "L_celdas": lattice,
            "dv_mmps": 6.0, "p": 0.0, "protocol": "FIXED_N"}
    return Run(
        meta=meta,
        step=np.repeat(np.arange(n_steps), n),
        vid=np.tile(np.arange(n), n_steps),
        x_mm=x.ravel(),
        v_mmps=v.ravel(),
    )


def test_mean_speed_de_velocidad_constante():
    run = make_run(np.zeros((5, 3)), np.full((5, 3), 100.0), n=3)
    assert abs(obs.mean_speed(run) - 100.0) < 1e-9


def test_error_cero_si_las_realizaciones_son_iguales():
    run = make_run(np.zeros((3, 2)), np.full((3, 2), 80.0), n=2)
    media, err = obs.mean_speed_with_error([run, run, run])
    assert abs(media - 80.0) < 1e-9
    assert err == 0.0


def test_error_es_el_desvio_entre_realizaciones():
    r1 = make_run(np.zeros((1, 1)), np.array([[90.0]]), n=1)
    r2 = make_run(np.zeros((1, 1)), np.array([[110.0]]), n=1)
    media, err = obs.mean_speed_with_error([r1, r2])
    assert abs(media - 100.0) < 1e-9
    assert abs(err - np.std([90.0, 110.0], ddof=1)) < 1e-9


def test_density_pdf_pico_en_equiespaciado():
    # 4 vehículos equiespaciados (cola en 0,330,660,990 sobre L=1320 mm) → vecino a 330 mm → ρ=1/330
    run = make_run(np.array([[0.0, 330.0, 660.0, 990.0]]), np.zeros((1, 4)), n=4)
    centros, pdf = obs.density_pdf(run, bins=300, rho_range=(0.0, 0.03))
    pico = centros[int(np.argmax(pdf))]
    assert abs(pico - 1.0 / 330.0) < 3e-4


def test_density_pdf_sin_vecino_devuelve_nan():
    run = make_run(np.array([[0.0]]), np.zeros((1, 1)), n=1)

    centros, pdf = obs.density_pdf(run, bins=3, rho_range=(0.0, 0.03))

    assert centros.shape == (3,)
    assert np.all(np.isnan(pdf))


def test_fundamental_diagram_sin_vecino_devuelve_vacio():
    run = make_run(np.array([[0.0]]), np.array([[100.0]]), n=1)

    rho, v = obs.fundamental_diagram(run)

    assert rho.size == 0
    assert v.size == 0


def test_detect_stationary_encuentra_el_corte():
    serie = np.concatenate([np.linspace(0.0, 100.0, 40), np.full(60, 100.0)])
    corte = obs.detect_stationary(serie)
    assert 20 <= corte <= 60
