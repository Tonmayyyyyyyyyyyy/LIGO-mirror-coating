"""Core code for the coating-rescue study.

The model, in plain words:
1. A reference end mirror (`load_reference`): 20 SiO2/Ti:Ta2O5 pairs plus a
   half-wave SiO2 cap, designed for the aLIGO dual-wavelength spec.
2. Deposition (`deposit`): every layer except the top k gets a random
   thickness error. Those top k are "not yet deposited".
3. Measurement (`measure`): the machine sees the deposited layers with its
   own random measurement error.
4. Rescue (`rescue`): the top k layers are re-optimized using the *measured*
   stack, then the mirror is judged on its *true* thicknesses (`passes`).

Layer order follows OptimalBragg: index 0 is the top layer (next to air,
deposited last). Index 0 here is the half-wave cap and is never changed.
"""
import warnings

import numpy as np
from scipy.optimize import differential_evolution, minimize
from OptimalBragg import Material, qw_stack
from OptimalBragg.layers import trans
from OptimalBragg.materials import SiO2, TiTa2O5, air
from OptimalBragg.noise import brownian_proxy

warnings.filterwarnings("ignore")

LAM1, LAM2 = 1064e-9, 532e-9
N_PAIRS = 20
REFERENCE_FILE = "designs/lownoise_seed5_t2.5.npy"   # Day 3: two locked designs,
# quiet (lownoise_seed5) and sturdy (robust_seed9), both aiming at 2.5% at 532 nm

# aLIGO ETM spec, LIGO E0900068-v5
SPECS = {
    "aligo": dict(T1=(4e-6, 6e-6), T2=(0.01, 0.04)),
    "tight": dict(T1=(0.0, 5e-6), T2=(0.027, 0.037)),   # hypothetical
}


def build_stack(n_pairs=N_PAIRS):
    """Quarter-wave starting stack; returns (stack, is_high_index, gamma_H)."""
    sub = Material(SiO2)
    sub.Temp = 295
    films = {"L": Material(SiO2), "H": Material(TiTa2O5)}
    stack = qw_stack(LAM1, sub, Material(air), films,
                     "HL" * (n_pairs - 1) + "H", hwcap="L")
    is_h = np.array([c == "H" for c in stack["pattern"]])
    return stack, is_h, brownian_proxy(stack)["H"]


STACK, IS_H, GAM_H = build_stack()


def load_reference(path=REFERENCE_FILE):
    return np.load(path)


def transmissions(Ls):
    """(T at 1064 nm, T at 532 nm) for physical thicknesses Ls [m]."""
    STACK["Ls"] = Ls
    return float(trans(LAM1, STACK)), float(trans(LAM2, STACK))


def noise_proxy(Ls):
    """E0900068-style Brownian proxy: SiO2 thickness + gamma_H * Ti:Ta2O5 thickness."""
    return Ls[~IS_H].sum() + GAM_H * Ls[IS_H].sum()


def passes(Ls, spec="aligo"):
    T1, T2 = transmissions(Ls)
    s = SPECS[spec]
    return s["T1"][0] <= T1 <= s["T1"][1] and s["T2"][0] <= T2 <= s["T2"][1]


def deposit(L_design, k, sigma_rel, rng, sigma_abs=0.0, model="independent"):
    """True thicknesses after depositing all but the cap and top k layers.

    model="independent": each layer gets its own error.
    model="common": one relative error shared by all deposited layers.
    sigma_abs adds an absolute error [m] per layer (Tikhonravov & Trubetskov
    2012 use 1 nm + 1%).
    """
    L = L_design.copy()
    n = len(L) - (k + 1)
    if model == "independent":
        rel = rng.normal(0, sigma_rel, n)
    elif model == "common":
        rel = np.full(n, rng.normal(0, sigma_rel))
    else:
        raise ValueError(model)
    L[k + 1:] = L[k + 1:] * (1 + rel) + rng.normal(0, sigma_abs, n)
    return L


def measure(L_true, k, sigma_rel, rng):
    """What the monitoring system reports for the deposited layers."""
    L = L_true.copy()
    n = len(L) - (k + 1)
    L[k + 1:] = L[k + 1:] * (1 + rng.normal(0, sigma_rel, n))
    return L


def rescue(L_seen, L_design, k, noise_weight=0.05, seed=0, t2_target=0.025,
           method="local"):
    """Re-optimize layers 1..k (top k below the cap) on the stack as seen.

    method="local": L-BFGS-B from three starting points (design, -10%, +10%).
        Default. Checked on Day 2 against "de": same pass/fail verdict on
        50/50 mirrors (k = 4 and 8), 12-20x faster.
    method="de": differential evolution (global, slow), for spot checks.
    Returns the new thicknesses for those k layers.
    """
    if k == 0:
        return np.array([])
    P0 = noise_proxy(L_design)
    scale = L_design[1:k + 1]

    def cost(y):
        L = L_seen.copy()
        L[1:k + 1] = y * scale
        T1, T2 = transmissions(L)
        return (5 * np.log10(T1 / 5e-6) ** 2 + 3 * np.log10(T2 / t2_target) ** 2
                + noise_weight * noise_proxy(L) / P0)

    bounds = [(0.5, 1.5)] * k
    if method == "de":
        res = differential_evolution(cost, bounds, seed=seed, maxiter=300,
                                     popsize=15, tol=1e-10, polish=True)
        return res.x * scale
    best = None
    for start in (1.0, 0.9, 1.1):
        r = minimize(cost, np.full(k, start), method="L-BFGS-B", bounds=bounds)
        if best is None or r.fun < best.fun:
            best = r
    return best.x * scale


def trial(L_design, k, sigma_dep, sigma_meas, rng, spec="aligo",
          model="independent", sigma_abs=0.0, rng_meas=None,
          noise_weight=0.05, t2_target=0.025, method="local", return_stack=False,
          gate=False):
    """One simulated mirror. Returns (passed, noise change relative to design).

    gate=True: rescue only if the measured stack, finished with the planned top
    layers, is predicted to fail the spec ("gated" rule). Default False: every
    mirror is rescued (the rule used in the main runs).

    Pass a separate rng_meas so that measurement noise does not change the
    deposition errors (keeps runs comparable across measurement levels).
    """
    rng_meas = rng if rng_meas is None else rng_meas
    # Draw the deposition error for every layer up front, so that the same
    # mirror is compared across different k.
    rel = rng.normal(0, sigma_dep, len(L_design))
    if model == "common":
        rel[:] = rel[-1]
    ab = rng.normal(0, sigma_abs, len(L_design))
    L_true = L_design * (1 + rel) + ab
    L_true[:k + 1] = L_design[:k + 1]          # not deposited yet
    L_seen = measure(L_true, k, sigma_meas, rng_meas)
    target_top = L_design[:k + 1].copy()
    if k and not (gate and passes(L_seen, spec)):
        target_top[1:] = rescue(L_seen, L_design, k, noise_weight=noise_weight,
                                t2_target=t2_target, method=method)
    # The top k layers and the cap are then deposited too, with their own errors.
    L_true[:k + 1] = target_top * (1 + rel[:k + 1]) + ab[:k + 1]
    dn = noise_proxy(L_true) / noise_proxy(L_design) - 1
    if return_stack:
        return passes(L_true, spec), dn, L_true
    return passes(L_true, spec), dn
