"""Prototype: can re-optimizing the last-deposited k layers rescue an ETM
whose lower layers came out with random thickness errors?

Stack order in OptimalBragg: Ls[0] is the top layer (next to air), so the
last k layers deposited are Ls[:k]. Errors hit Ls[k:] (already deposited).
Then Ls[:k] are re-optimized to minimize transmission with a small
Brownian-noise penalty (proxy). Pass = T <= T_TARGET.

Run:  python scripts/rescue_prototype.py  [n_trials]
"""
import sys
import warnings

import numpy as np
from scipy.optimize import differential_evolution
from OptimalBragg import Material, qw_stack
from OptimalBragg.layers import trans
from OptimalBragg.materials import SiO2, TiTa2O5, air
from OptimalBragg.noise import brownian_proxy

warnings.filterwarnings("ignore")

LAMBDA = 1064e-9
T_TARGET = 5e-6
N_PAIRS = 20
N_TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 40
SIGMAS = [0.005, 0.01, 0.02]
KS = [0, 2, 4, 6]
NOISE_WEIGHT = 0.1
rng = np.random.default_rng(1)

sub = Material(SiO2); sub.Temp = 295
films = {"L": Material(SiO2), "H": Material(TiTa2O5)}
base = qw_stack(LAMBDA, sub, Material(air), films, "LH" * N_PAIRS)
L0 = base["Ls"].copy()
GAM_H = brownian_proxy(base)["H"]
IS_H = np.array([c == "H" for c in base["pattern"]])


def proxy(Ls):
    """E0900068-style proxy: low-index thickness + gamma_H * high-index thickness."""
    return Ls[~IS_H].sum() + GAM_H * Ls[IS_H].sum()


P0 = proxy(L0)
print(f"nominal: T = {trans(LAMBDA, base)*1e6:.2f} ppm, gamma_H = {GAM_H:.3f}")


def T_of(Ls):
    base["Ls"] = Ls
    return float(trans(LAMBDA, base))


def rescue(Ls_err, k):
    if k == 0:
        return Ls_err, T_of(Ls_err)

    def cost(x):
        Ls = Ls_err.copy(); Ls[:k] = x
        T = T_of(Ls)
        noise = proxy(Ls) / P0 - 1
        return np.log10(T / T_TARGET) + NOISE_WEIGHT * noise

    bounds = [(0.7 * L0[i], 1.3 * L0[i]) for i in range(k)]
    res = differential_evolution(cost, bounds, seed=0, maxiter=200,
                                 popsize=15, tol=1e-8, polish=True)
    Ls = Ls_err.copy(); Ls[:k] = res.x
    return Ls, T_of(Ls)


print(f"{N_TRIALS} trials per cell; pass = T <= {T_TARGET*1e6:.0f} ppm")
print("sigma  " + "  ".join(f"k={k}: pass  medT(ppm)" for k in KS))
for sigma in SIGMAS:
    errs = rng.normal(0, sigma, size=(N_TRIALS, len(L0)))
    row = []
    for k in KS:
        Ts = []
        for e in errs:
            Ls_err = L0 * (1 + e)
            Ls_err[:k] = L0[:k]          # top k not yet deposited
            _, T = rescue(Ls_err, k)
            Ts.append(T)
        Ts = np.array(Ts)
        row.append(f"{np.mean(Ts <= T_TARGET):5.2f}  {np.median(Ts)*1e6:6.2f}  ")
    print(f"{sigma*100:4.1f}%  " + "  ".join(row), flush=True)
