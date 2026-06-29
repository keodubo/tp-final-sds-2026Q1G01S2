"""Observables del modelo — se calculan SIEMPRE post-simulación (regla de la cátedra).

Todos toman objetos :class:`run_io.Run` (o listas de ellos, una por realización) y devuelven los
observables del artículo: velocidad media vs N, PDF de densidades, PDF de velocidades y diagrama
fundamental. La detección del estacionario es por inspección (no descarte fijo) y el error se
calcula como desvío correcto entre realizaciones.

Nada de esto vive dentro del motor: el motor solo escribe estado físico (paso, id, x_mm, v_mmps) y
acá se reconstruye todo desde esos archivos.
"""
from __future__ import annotations

import numpy as np

from run_io import Run


# --- helpers de calibración / agrupamiento por paso ---

def _ell_mm(run: Run) -> float:
    return float(run.meta["ell_celdas"]) * float(run.meta["dx_mm"])


def _track_mm(run: Run) -> float:
    return float(run.meta["L_celdas"]) * float(run.meta["dx_mm"])


def _as_runs(runs) -> list[Run]:
    return [runs] if isinstance(runs, Run) else list(runs)


def _steps(run: Run, since_step: int = 0):
    """Devuelve (pasos_unicos, [x_mm por paso], [v_mmps por paso]) desde ``since_step``."""
    mask = run.step >= since_step
    s, x, v = run.step[mask], run.x_mm[mask], run.v_mmps[mask]
    order = np.argsort(s, kind="stable")
    s, x, v = s[order], x[order], v[order]
    uniq, idx = np.unique(s, return_index=True)
    return uniq, np.split(x, idx[1:]), np.split(v, idx[1:])


def _nearest_center_distances(x_mm: np.ndarray, ell_mm: float, track_mm: float) -> np.ndarray:
    """Distancia (centro a centro) al vecino más cercano sobre la ruta periódica, en orden de
    posición creciente. ``x_mm`` es la cola; el centro es x + ℓ/2."""
    centers = np.sort((x_mm + ell_mm / 2.0) % track_mm)
    n = centers.size
    if n < 2:
        return np.array([])
    diffs = np.diff(centers)
    wrap = centers[0] + track_mm - centers[-1]
    ahead = np.append(diffs, wrap)          # hueco hacia el de adelante
    behind = np.append(wrap, diffs)         # hueco hacia el de atrás
    return np.minimum(ahead, behind)


# --- estacionario ---

def mean_speed_series(run: Run):
    """Serie temporal de la velocidad media (sobre vehículos) por paso registrado: (pasos, v_media)."""
    uniq, _, gv = _steps(run, 0)
    return uniq, np.array([float(np.mean(v)) for v in gv])


def detect_stationary(time_series, tol_frac: float = 0.05) -> int:
    """Propone el paso de corte del transitorio **por inspección asistida** (no descarte fijo en %).

    Heurística: sobre la serie suavizada, devuelve el primer paso a partir del cual la serie se
    mantiene dentro de una banda ``tol_frac`` alrededor de su valor de régimen (media de la cola).
    La decisión final es del grupo mirando la figura; esto solo sugiere un corte.
    """
    s = np.asarray(time_series, dtype=float)
    n = s.size
    if n < 4:
        return 0
    w = max(1, n // 20)
    smooth = np.convolve(s, np.ones(w) / w, mode="same")
    final = float(np.mean(s[max(0, n - n // 4):]))
    tol = tol_frac * abs(final) if final != 0 else tol_frac * (float(np.std(s)) + 1e-9)
    for t in range(n):
        if np.all(np.abs(smooth[t:] - final) <= tol):
            return t
    return n // 2


# --- velocidad media (≈ Fig. 2) ---

def mean_speed(run: Run, since_step: int = 0) -> float:
    """Velocidad media [mm/s] de una realización. El promedio de la velocidad de cuadro sobre todos
    los vehículos y pasos equivale a ⟨L_i/T⟩ del artículo (la velocidad de cuadro es el
    desplazamiento real por paso, sin problemas de envoltura).

    Válido tal cual para ``FIXED_N``. Para ``INCREMENTAL_180S`` conviene recortar por ventanas de 180 s
    (los vehículos insertados tarde tienen menos cuadros y arrancan en v=0): pasar el ``since_step`` del
    tramo correspondiente."""
    v = run.v_mmps[run.step >= since_step]
    return float(np.mean(v)) if v.size else float("nan")


def mean_speed_with_error(runs, since_step: int = 0) -> tuple[float, float]:
    """Velocidad media y su error sobre varias **realizaciones**.

    El error es el **desvío entre realizaciones** (desvío muestral, ddof=1) de las medias por
    realización — NO el desvío de todos los cuadros juntos, que subrepresenta el error
    (corrección puntual de la cátedra en el TP2). Devuelve (media, desvío)."""
    means = np.array([mean_speed(r, since_step) for r in _as_runs(runs)], dtype=float)
    means = means[~np.isnan(means)]
    if means.size == 0:
        return float("nan"), float("nan")
    mean = float(np.mean(means))
    # con una sola realización el error no está definido: nan (no 0.0, que sugeriría precisión perfecta)
    err = float(np.std(means, ddof=1)) if means.size > 1 else float("nan")
    return mean, err


# --- PDF de densidades (≈ Fig. 3) ---

def density_pdf(runs, since_step: int = 0, bins: int = 100, rho_range=None):
    """PDF de la densidad individual ρ_i = 1/d_i, con d_i = distancia centro-a-centro al vecino más
    cercano sobre la ruta periódica. Esperado: pico en 1/44 mm ≈ 0.0227 1/mm. Devuelve (centros, pdf)."""
    rhos = []
    for run in _as_runs(runs):
        ell, track = _ell_mm(run), _track_mm(run)
        for x in _steps(run, since_step)[1]:
            distances = _nearest_center_distances(x, ell, track)
            if distances.size:
                rhos.append(1.0 / distances)
    rho = np.concatenate(rhos) if rhos else np.array([])
    if rho.size == 0:
        if rho_range is None:
            edges = np.linspace(0.0, 1.0, bins + 1)
        else:
            edges = np.linspace(rho_range[0], rho_range[1], bins + 1)
        return 0.5 * (edges[:-1] + edges[1:]), np.full(bins, np.nan)
    hist, edges = np.histogram(rho, bins=bins, range=rho_range, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), hist


# --- PDF de velocidades (≈ Fig. 4) ---

def velocity_pdf(runs, since_step: int = 0, bins: int = 100, v_range=None):
    """PDF de la velocidad microscópica [mm/s] sobre todos los vehículos y pasos del estacionario.
    Devuelve (centros, pdf)."""
    vs = [run.v_mmps[run.step >= since_step] for run in _as_runs(runs)]
    v = np.concatenate(vs) if vs else np.array([])
    hist, edges = np.histogram(v, bins=bins, range=v_range, density=True)
    return 0.5 * (edges[:-1] + edges[1:]), hist


# --- diagrama fundamental (≈ Fig. 5) ---

def fundamental_diagram(runs, since_step: int = 0, window: int = 1000):
    """Velocidad instantánea vs densidad local ρ_i, ordenada por densidad y suavizada con media
    móvil. Devuelve (rho, v_media_movil)."""
    rho_all, v_all = [], []
    for run in _as_runs(runs):
        ell, track = _ell_mm(run), _track_mm(run)
        _, gx, gv = _steps(run, since_step)
        for x, v in zip(gx, gv):
            distances = _nearest_center_distances(x, ell, track)
            if distances.size == 0:
                continue
            order = np.argsort((x + ell / 2.0) % track)
            rho_all.append(1.0 / distances)  # en orden de posición
            v_all.append(v[order])
    if not rho_all:
        return np.array([]), np.array([])
    rho = np.concatenate(rho_all)
    v = np.concatenate(v_all)
    order = np.argsort(rho)
    rho, v = rho[order], v[order]
    w = max(1, min(window, v.size))
    kernel = np.ones(w) / w
    return np.convolve(rho, kernel, mode="valid"), np.convolve(v, kernel, mode="valid")
