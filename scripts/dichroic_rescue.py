"""Rescue test on the dichroic ETM (from dichroic_sensitivity.py).

Errors hit all layers except the top k (not yet deposited; layer 0 is the
fixed half-wave cap and is never re-optimized). Then the top k layers below
the cap are re-optimized to bring T1064 <= 5 ppm and T532 back to 3.2%.
Pass: aLIGO spec (E0900068 v5) or a tighter hypothetical spec.

Run:  python scripts/dichroic_rescue.py [n_trials] [sigma] [aligo|tight]
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
LAM1, LAM2 = 1064e-9, 532e-9
N_TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 20
SIGMA = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01
KS = [0, 2, 4, 6]

sub = Material(SiO2); sub.Temp = 295
films = {"L": Material(SiO2), "H": Material(TiTa2O5)}
base = qw_stack(LAM1, sub, Material(air), films, "HL" * 19 + "H", hwcap="L")
Lopt = np.load("scripts/dichroic_Lopt.npy")
IS_H = np.array([c == "H" for c in base["pattern"]])
GAM_H = brownian_proxy(base)["H"]
P0 = Lopt[~IS_H].sum() + GAM_H * Lopt[IS_H].sum()


def Ts(Ls):
    base["Ls"] = Ls
    return float(trans(LAM1, base)), float(trans(LAM2, base))


SPEC = sys.argv[3] if len(sys.argv) > 3 else "aligo"


def passes(T1, T2):
    if SPEC == "aligo":   # E0900068 v5: T1064 = 5 +/- 1 ppm, T532 in 1-4%
        return 4e-6 <= T1 <= 6e-6 and 0.01 <= T2 <= 0.04
    return T1 <= 5e-6 and abs(T2 - 0.032) <= 0.005   # "tight" hypothetical


def rescue(Ls_err, k):
    if k == 0:
        return Ls_err

    def cost(x):
        Ls = Ls_err.copy(); Ls[1:k + 1] = x
        T1, T2 = Ts(Ls)
        noise = (Ls[~IS_H].sum() + GAM_H * Ls[IS_H].sum()) / P0
        return (5 * max(0, np.log10(T1 / 4.5e-6)) ** 2
                + 3 * np.log10(T2 / 0.032) ** 2 + 0.05 * noise)

    bounds = [(0.5 * Lopt[i], 1.5 * Lopt[i]) for i in range(1, k + 1)]
    res = differential_evolution(cost, bounds, seed=0, maxiter=300,
                                 popsize=15, tol=1e-10, polish=True)
    Ls = Ls_err.copy(); Ls[1:k + 1] = res.x
    return Ls


rng = np.random.default_rng(3)
errs = rng.normal(0, SIGMA, size=(N_TRIALS, len(Lopt)))
print(f"sigma {SIGMA*100:.1f}%, {N_TRIALS} trials, spec {SPEC}")
for k in KS:
    ok, dnoise = [], []
    for e in errs:
        Ls_err = Lopt * (1 + e)
        Ls_err[:k + 1] = Lopt[:k + 1]      # cap + top k not yet deposited
        Ls = rescue(Ls_err, k)
        ok.append(passes(*Ts(Ls)))
        dnoise.append((Ls[~IS_H].sum() + GAM_H * Ls[IS_H].sum()) / P0 - 1)
    print(f"k={k}: pass {np.mean(ok):.2f}, mean noise-proxy change "
          f"{np.mean(dnoise)*100:+.2f}%", flush=True)
