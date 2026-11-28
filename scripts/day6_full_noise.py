"""Day 6: check the rescue's noise cost with the full Brownian formula.

Inside the optimizer we use a fast stand-in for thermal noise (E0900068
proxy). Here we take finished mirrors (2% independent errors, perfect and
1% measurement) and compute the full Hong et al. noise with OptimalBragg,
with and without rescue (k = 4), using the same random mirrors.
"""
import sys
import numpy as np
sys.path.insert(0, ".")
import rescue
from OptimalBragg.noise import coating_brownian

W_BEAM, FREQ, N = 0.062, 100.0, 40


def asd(Ls):
    rescue.STACK["Ls"] = Ls
    return float(np.sqrt(coating_brownian(np.array([FREQ]), rescue.STACK, W_BEAM)[0]))


for name, path in [("sturdy", "designs/robust_seed9_t2.5.npy"),
                   ("quiet", "designs/lownoise_seed5_t2.5.npy")]:
    L = np.load(path)
    a0 = asd(L)
    print(f"\n{name}: design ASD {a0:.3e} m/rtHz")
    for meas in (0.0, 0.01):
        full, prox = {0: [], 4: []}, {0: [], 4: []}
        for i in range(N):
            for k in (0, 4):
                rng = np.random.default_rng([6, i])
                rng_m = np.random.default_rng([6, i, 1])
                ok, dn, Lt = rescue.trial(L, k, 0.02, meas, rng, rng_meas=rng_m,
                                          return_stack=True)
                full[k].append(asd(Lt) / a0 - 1)
                prox[k].append(dn)
        d = np.array(full[4]) - np.array(full[0])
        print(f"  meas {meas:.0%}: full-formula change vs design, "
              f"no rescue {np.mean(full[0]):+.2%}, k=4 {np.mean(full[4]):+.2%}; "
              f"rescue minus no rescue {np.mean(d):+.2%} "
              f"(range {d.min():+.2%} to {d.max():+.2%}); "
              f"proxy said {np.mean(prox[4]) - np.mean(prox[0]):+.2%}")
