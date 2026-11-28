"""How much does the tantala loss angle change the noise?

Full Brownian noise (Hong et al. 2013, OptimalBragg) at 100 Hz, beam radius
6.2 cm, for all 32 designs, with the tantala loss angle 2e-4 (our value,
from the OptimalBragg library) and 3.6e-4 (Venugopalan et al. 2024).
Pass rates do not depend on the loss angle: passing depends only on light.

Run: python3 scripts/check_loss_angle.py > results/checks/loss_angle.txt
"""
import copy
import sys

import numpy as np
from OptimalBragg.noise import coating_brownian

sys.path.insert(0, ".")
import rescue  # noqa: E402

names = [f"designs/population/seed{s}.npy" for s in range(1, 31) if s != 21] + \
        [f"designs/{d}.npy" for d in ("lownoise_seed5_t2.5", "seed2_t2.5", "robust_seed9_t2.5")]


def asd(stack, L):
    stack["Ls"] = L
    return float(np.sqrt(coating_brownian(np.array([100.0]), stack, 0.062)[0]))


base = rescue.STACK
alt = copy.deepcopy(base)
phis = np.array(alt["phis"], dtype=float)
assert set(np.unique(phis)) == {5e-5, 2e-4}, np.unique(phis)
phis[phis == 2e-4] = 3.6e-4
alt["phis"] = phis

rise = []
for n in names:
    L = np.load(n)
    a, b = asd(base, L), asd(alt, L)
    rise.append(b / a - 1)
    print(f"{n:42s} {a*1e21:.3f} -> {b*1e21:.3f} e-21 m/rtHz  (+{(b/a-1)*100:.1f}%)")
print(f"\n{len(names)} designs. Noise rise with tantala loss angle 3.6e-4 instead of 2e-4: "
      f"{min(rise)*100:.1f}% to {max(rise)*100:.1f}%")
