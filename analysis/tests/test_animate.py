"""Tests de comportamiento (solo API pública observable) de los ayudantes puros de ``animate``.

No se verifican píxeles ni colores exactos: sólo la lógica de las funciones puras que sostienen la
animación defendible (fps en tiempo real, escala de color anclada, panel de parámetros, fotograma
estacionario, conteo de activos y envoltura periódica).
"""
import numpy as np

import animate


def test_real_time_fps_da_24_para_output_every_1_y_dt_un_veinticuatroavo():
    assert animate.real_time_fps(1, 1.0 / 24.0) == 24.0


def test_real_time_fps_escala_con_output_every():
    # Con output_every=10 y dt=1/24, el tiempo real son 2.4 fps.
    assert abs(animate.real_time_fps(10, 1.0 / 24.0) - 2.4) < 1e-9


def test_color_scale_max_usa_vfree_max_de_la_cabecera():
    assert animate.color_scale_max({"vfree_max_mmps": 120.0}) == 120.0


def test_color_scale_max_respaldo_positivo_si_falta_o_es_invalido():
    assert animate.color_scale_max({}) > 0.0
    assert animate.color_scale_max({"vfree_max_mmps": "x"}) > 0.0
    assert animate.color_scale_max({"vfree_max_mmps": 0.0}) > 0.0


def test_config_lines_incluye_realizacion_y_no_dice_seed_ni_semilla():
    lineas = animate.config_lines(
        {"N": 15, "p": 0.1, "regla2": "CONTACTO_PURO", "protocol": "FIXED_N",
         "order": "SIN_ORDEN", "realizacion_id": 7}
    )
    texto = "\n".join(lineas).lower()
    assert any("realización" in linea for linea in lineas)
    assert "7" in "\n".join(lineas)
    assert "seed" not in texto
    assert "semilla" not in texto


def test_config_lines_orden_no_aplica_para_fixed_n():
    lineas = animate.config_lines({"order": "SIN_ORDEN"})
    assert any("no aplica" in linea for linea in lineas if linea.startswith("orden"))


def test_config_lines_muestra_orden_real_en_incremental():
    lineas = animate.config_lines({"order": "ASCENDING"})
    assert any("ASCENDING" in linea for linea in lineas)


def test_still_frame_index_elige_fotograma_estacionario():
    steps = np.arange(0, 100, 10)  # 0,10,...,90
    idx = animate.still_frame_index(steps, since_step=50)
    assert steps[idx] >= 50


def test_still_frame_index_por_defecto_es_el_ultimo():
    steps = np.arange(0, 100, 10)
    idx = animate.still_frame_index(steps, since_step=0)
    assert idx == steps.size - 1


def test_still_frame_index_devuelve_el_ultimo_si_ninguno_califica():
    steps = np.array([0, 10, 20])
    idx = animate.still_frame_index(steps, since_step=999)
    assert idx == steps.size - 1


def test_active_count_cuenta_los_vehiculos_del_fotograma():
    assert animate.active_count(np.array([1.0, 2.0, 3.0])) == 3
    assert animate.active_count(np.array([])) == 0


def test_wrap_positions_sin_envoltura_una_sola_copia():
    posiciones = animate.wrap_positions(0.0, 44.0, 1320.0)
    assert len(posiciones) == 1
    assert posiciones[0] == 0.0


def test_wrap_positions_con_envoltura_dibuja_copia_en_el_otro_extremo():
    track, ell = 1320.0, 44.0
    base = track - ell / 2.0  # el vehículo cruza x=L
    posiciones = animate.wrap_positions(base, ell, track)
    assert len(posiciones) == 2
    assert base in posiciones
    assert (base - track) in posiciones
