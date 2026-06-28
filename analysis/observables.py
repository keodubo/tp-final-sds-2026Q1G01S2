"""Observables del modelo — se calculan SIEMPRE post-simulación (regla de la cátedra).

Todos toman objetos :class:`io.Run` (o listas de ellos, una por realización) y devuelven los
observables del paper: velocidad media vs N, PDF de densidades, PDF de velocidades y diagrama
fundamental. La detección del estacionario es por inspección (no descarte fijo) y el error se
calcula como desvío correcto entre realizaciones.

Esqueletos a completar en el Hito 5 (cuando tengamos datos reales del motor).
"""
from __future__ import annotations

import numpy as np

from io import Run  # type: ignore  # (se importa el Run del módulo io.py local en runtime)


def detect_stationary(time_series: np.ndarray) -> int:
    """Devuelve el paso a partir del cual la serie está en régimen estacionario.

    Por inspección visual (graficar la serie y elegir el corte), NO con un porcentaje fijo.
    Esta función ayuda a proponer un corte automático (p. ej. cuando la media móvil se estabiliza),
    pero la decisión final es del grupo mirando la figura.
    TODO (Hito 5).
    """
    raise NotImplementedError


def mean_speed(run: Run, since_step: int = 0) -> float:
    """Velocidad media de una realización [mm/s]: promedio temporal por vehículo (desde
    ``since_step``) y luego promedio sobre vehículos. TODO (Hito 5)."""
    raise NotImplementedError


def mean_speed_with_error(runs: list[Run], since_step: int = 0) -> tuple[float, float]:
    """Velocidad media y su error sobre varias realizaciones. El error es el desvío entre los
    valores por realización (no promedio-de-promedios mal calculado). TODO (Hito 5)."""
    raise NotImplementedError


def density_pdf(runs: list[Run], since_step: int = 0, bins: int = 100):
    """PDF de la densidad individual ρ_i = 1 / d_i, con d_i = distancia (centro a centro) al vecino
    más cercano sobre el anillo, calculada desde las posiciones. Esperado: pico en 1/44 mm.
    Devuelve (centros_bins, pdf). TODO (Hito 5)."""
    raise NotImplementedError


def velocity_pdf(runs: list[Run], since_step: int = 0, bins: int = 100):
    """PDF de la velocidad microscópica [mm/s] sobre todos los vehículos y pasos del estacionario.
    Devuelve (centros_bins, pdf). TODO (Hito 5)."""
    raise NotImplementedError


def fundamental_diagram(runs: list[Run], since_step: int = 0, window: int = 1000):
    """Diagrama fundamental: velocidad instantánea vs densidad local ρ_i, con media móvil.
    Devuelve (rho, v_media_movil). TODO (Hito 5)."""
    raise NotImplementedError
