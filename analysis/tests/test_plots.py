import numpy as np

import plots


def test_mean_speed_vs_n_accepts_textual_curve_keys(tmp_path):
    out = tmp_path / "incremental.png"

    plots.plot_mean_speed_vs_n(
        {"ASCENDING": (np.array([5, 10]), np.array([90.0, 80.0]), np.array([1.0, 2.0]))},
        out,
        legend_title="orden",
    )

    assert out.exists()
