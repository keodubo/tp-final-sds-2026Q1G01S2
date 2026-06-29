"""Carga de los archivos de salida del motor (Java).

El motor escribe una cabecera con los parámetros (líneas con ``#``) y luego filas
``paso id x_mm v_mmps``. Acá se parsea todo a estructuras de numpy para el análisis.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Run:
    """Una realización cargada: metadatos de la cabecera + datos crudos."""
    meta: dict[str, object]
    step: np.ndarray   # entero, paso de tiempo
    vid: np.ndarray    # entero, id de vehículo
    x_mm: np.ndarray   # posición [mm]
    v_mmps: np.ndarray # velocidad [mm/s]

    @property
    def n_steps(self) -> int:
        """Cantidad de pasos REGISTRADOS (robusto ante output_every≠1, donde no son consecutivos)."""
        return int(np.unique(self.step).size) if self.step.size else 0

    @property
    def n_vehicles(self) -> int:
        return int(self.meta.get("N", len(np.unique(self.vid))))


def _coerce(value: str) -> object:
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            pass
    return value


def parse_header(path: Path) -> dict[str, object]:
    """Extrae todos los tokens ``clave=valor`` de las líneas de comentario."""
    meta: dict[str, object] = {}
    with open(path) as fh:
        for raw in fh:
            if not raw.startswith("#"):
                break
            for token in raw[1:].split():
                if "=" in token:
                    key, val = token.split("=", 1)
                    meta[key] = _coerce(val)
    return meta


def load_run(path: str | Path) -> Run:
    """Carga una realización completa desde un archivo de salida del motor."""
    path = Path(path)
    meta = parse_header(path)
    # Parseo rápido (np.loadtxt es ~10x más lento para estos volúmenes).
    rows = []
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.split()
            if parts:
                rows.append(parts)
    data = np.array(rows, dtype=float) if rows else np.empty((0, 4))
    if data.ndim == 1:  # un solo registro
        data = data.reshape(1, -1)
    return Run(
        meta=meta,
        step=data[:, 0].astype(int),
        vid=data[:, 1].astype(int),
        x_mm=data[:, 2],
        v_mmps=data[:, 3],
    )


def load_many(paths) -> list[Run]:
    """Carga varias realizaciones (p. ej. todas las de un mismo (N, p))."""
    return [load_run(p) for p in paths]
