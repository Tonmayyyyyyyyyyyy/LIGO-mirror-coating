"""Sanity checks for rescue.py.  Run:  python -m pytest -q tests"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rescue  # noqa: E402
from OptimalBragg import Material, qw_stack  # noqa: E402
from OptimalBragg.layers import refl  # noqa: E402
from OptimalBragg.materials import SiO2, TiTa2O5, air  # noqa: E402


def test_single_quarter_wave_layer_matches_textbook():
    """One quarter-wave layer of index n1 on glass: R = ((ns - n1^2)/(ns + n1^2))^2."""
    sub = Material(SiO2); sub.Temp = 295
    st = qw_stack(1064e-9, sub, Material(air), {"H": Material(TiTa2O5)}, "H")
    n1, ns = st["ns"][1], st["ns"][-1]
    expected = ((ns - n1 ** 2) / (ns + n1 ** 2)) ** 2
    assert abs(float(refl(1064e-9, st)) - expected) < 1e-6


def test_reference_design_meets_spec():
    L = rescue.load_reference()
    T1, T2 = rescue.transmissions(L)
    assert 4e-6 <= T1 <= 6e-6 and 0.01 <= T2 <= 0.04
    assert rescue.passes(L)


def test_zero_errors_leave_design_unchanged():
    L = rescue.load_reference()
    rng = np.random.default_rng(0)
    assert np.allclose(rescue.deposit(L, 3, 0.0, rng), L, rtol=1e-9, atol=0)
    assert np.allclose(rescue.measure(L, 3, 0.0, rng), L, rtol=1e-9, atol=0)


def test_cap_and_top_k_untouched_by_deposit():
    L = rescue.load_reference()
    out = rescue.deposit(L, 4, 0.02, np.random.default_rng(1))
    assert np.allclose(out[:5], L[:5], rtol=1e-9, atol=0)
    assert not np.allclose(out[5:], L[5:], rtol=1e-9, atol=0)


def test_common_model_uses_one_factor():
    L = rescue.load_reference()
    out = rescue.deposit(L, 2, 0.02, np.random.default_rng(2), model="common")
    ratios = out[3:] / L[3:]
    assert np.allclose(ratios, ratios[0], rtol=1e-9, atol=0)


def test_trial_with_no_errors_passes():
    L = rescue.load_reference()
    ok, dn = rescue.trial(L, 2, 0.0, 0.0, np.random.default_rng(0))
    assert ok and abs(dn) < 0.01
