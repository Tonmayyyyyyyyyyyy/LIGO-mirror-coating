"""Re-make the starting designs with the method used on Day 3.

Same cost as scripts/dichroic_sensitivity.py, but aiming at 2.5% at 532 nm:
  cost = 5 * max(0, log10(T1064 / 5 ppm))^2
       + 3 * log10(T532 / 0.025)^2
       + 0.5 * (noise proxy / noise proxy of the plain quarter-wave stack)
Layer 0 (half-wave SiO2 cap) is fixed; the other 40 layers may vary between
0.3x and 1.7x their quarter-wave thickness. Differential evolution, popsize 8,
maxiter 400, Sobol start, polish on. Only the random seed differs.

Usage: python3 scripts/make_designs.py 5   (writes designs/remade_seed5.npy)
The designs used in the paper are the saved files in designs/; this script
checks whether the method gives them back.
"""
import sys
import time
import numpy as np
from scipy.optimize import differential_evolution
sys.path.insert(0, ".")
import rescue

seed = int(sys.argv[1])
L0 = rescue.STACK["Ls"].copy() if False else None
from OptimalBragg import Material, qw_stack
from OptimalBragg.materials import SiO2, TiTa2O5, air
sub = Material(SiO2); sub.Temp = 295
films = {"L": Material(SiO2), "H": Material(TiTa2O5)}
L0 = qw_stack(rescue.LAM1, sub, Material(air), films,
              "HL" * (rescue.N_PAIRS - 1) + "H", hwcap="L")["Ls"].copy()
P0 = rescue.noise_proxy(L0)


def cost(x):
    Ls = L0.copy(); Ls[1:] = x
    T1, T2 = rescue.transmissions(Ls)
    return (5 * max(0, np.log10(T1 / 5e-6)) ** 2
            + 3 * np.log10(T2 / 0.025) ** 2 + 0.5 * rescue.noise_proxy(Ls) / P0)


t = time.time()
res = differential_evolution(cost, [(0.3 * L, 1.7 * L) for L in L0[1:]], seed=seed,
                             maxiter=400, popsize=8, tol=1e-10, polish=True,
                             init="sobol")
L = L0.copy(); L[1:] = res.x
T1, T2 = rescue.transmissions(L)
np.save(f"designs/remade_seed{seed}.npy", L)
print(f"seed {seed}: {time.time()-t:.0f}s, T1064 {T1*1e6:.2f} ppm, T532 {T2:.2%}, "
      f"proxy/QW {rescue.noise_proxy(L)/P0:.3f}")
for name in ("lownoise_seed5", "seed2", "robust_seed9"):
    D = np.load(f"designs/{name}_t2.5.npy")
    print(f"  max layer difference vs {name}: {np.max(np.abs(L/D - 1)):.2%}")
