"""Check: is the 532 nm transmission of a dichroic ETM (T1064 <= 5 ppm,
T532 = 3.2%) sensitive to random thickness errors, unlike the 1064 nm one?

1. Optimize a 20-pair SiO2/TiTa2O5 stack (+ half-wave SiO2 cap kept fixed)
   for T1064 = 5 ppm, T532 = 3.2%, with a Brownian proxy penalty.
2. Monte Carlo: independent errors at 0.5/1/2%, report spread of T532 and
   T1064, and pass rates against the aLIGO spec (E0900068-v5):
   T1064 = 5 +/- 1 ppm and T532 between 1% and 4%.
"""
import time
import warnings

import numpy as np
from scipy.optimize import differential_evolution
from OptimalBragg import Material, qw_stack
from OptimalBragg.layers import trans
from OptimalBragg.materials import SiO2, TiTa2O5, air
from OptimalBragg.noise import brownian_proxy

warnings.filterwarnings("ignore")
LAM1, LAM2 = 1064e-9, 532e-9
N_PAIRS = 20

sub = Material(SiO2); sub.Temp = 295
films = {"L": Material(SiO2), "H": Material(TiTa2O5)}
base = qw_stack(LAM1, sub, Material(air), films, "HL" * (N_PAIRS - 1) + "H", hwcap="L")
L0 = base["Ls"].copy()
IS_H = np.array([c == "H" for c in base["pattern"]])
GAM_H = brownian_proxy(base)["H"]
P0 = L0[~IS_H].sum() + GAM_H * L0[IS_H].sum()


def Ts(Ls):
    base["Ls"] = Ls
    return float(trans(LAM1, base)), float(trans(LAM2, base))


def cost(x):
    Ls = L0.copy(); Ls[1:] = x          # layer 0 = half-wave cap, fixed
    T1, T2 = Ts(Ls)
    noise = (Ls[~IS_H].sum() + GAM_H * Ls[IS_H].sum()) / P0
    return (5 * max(0, np.log10(T1 / 5e-6)) ** 2
            + 3 * (np.log10(T2 / 0.032)) ** 2
            + 0.5 * noise)


t = time.time()
bounds = [(0.3 * L, 1.7 * L) for L in L0[1:]]
res = differential_evolution(cost, bounds, seed=2, maxiter=400, popsize=8,
                             tol=1e-10, polish=True, init="sobol")
Lopt = L0.copy(); Lopt[1:] = res.x
T1, T2 = Ts(Lopt)
print(f"optimized in {time.time()-t:.0f}s: T1064 = {T1*1e6:.2f} ppm, "
      f"T532 = {T2*100:.2f} %, noise proxy / QW = "
      f"{(Lopt[~IS_H].sum() + GAM_H*Lopt[IS_H].sum())/P0:.3f}")
np.save("scripts/dichroic_Lopt.npy", Lopt)

rng = np.random.default_rng(0)
for sigma in [0.005, 0.01, 0.02]:
    out = np.array([Ts(Lopt * (1 + rng.normal(0, sigma, len(Lopt))))
                    for _ in range(500)])
    p1 = np.mean((out[:, 0] >= 4e-6) & (out[:, 0] <= 6e-6))
    p2 = np.mean((out[:, 1] >= 0.01) & (out[:, 1] <= 0.04))
    print(f"sigma {sigma*100:.1f}%: T1064 median {np.median(out[:,0])*1e6:.2f} ppm "
          f"(pass {p1:.2f}); T532 5-95% = {np.percentile(out[:,1],5)*100:.2f}-"
          f"{np.percentile(out[:,1],95)*100:.2f} % (pass {p2:.2f}); both {np.mean((out[:,0]>=4e-6)&(out[:,0]<=6e-6)&(out[:,1]>=0.01)&(out[:,1]<=0.04)):.2f}")
