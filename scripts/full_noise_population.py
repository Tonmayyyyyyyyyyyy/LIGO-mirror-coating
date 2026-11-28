"""Question 3 with the full Brownian calculation, on all 32 designs.

For every design: the same 200 mirrors as the main runs (independent errors,
sigma_dep = 2%, seed 0), made without rescue (k = 0) and with rescue (k = 4) at
measurement errors 0, 1 and 2%. For each finished mirror we compute coating
Brownian noise at 100 Hz (Hong et al., OptimalBragg, beam radius 6.2 cm) and
report the change from rescue, mirror by mirror (rescued vs the same mirror
not rescued). Also: the same with a fused-silica substrate Young's modulus of
72.7 GPa instead of the library's 60 GPa, and the noise proxy for comparison.

Run: python3 scripts/full_noise_population.py > results/revision/full_noise_population.txt
Per-mirror values: results/revision/full_noise_population.csv
"""
import copy
import csv
import os
import sys
from multiprocessing import Pool

import numpy as np
from OptimalBragg.noise import coating_brownian

sys.path.insert(0, ".")
import rescue  # noqa: E402

DEP, N, MEAS = 0.02, 200, (0.0, 0.01, 0.02)
NAMES = [f"seed{s}" for s in range(1, 31) if s != 21] + \
        ["lownoise_seed5_t2.5", "seed2_t2.5", "robust_seed9_t2.5"]
STACK_FS = copy.deepcopy(rescue.STACK)
STACK_FS["sub"].Y = 72.7e9


def path(n):
    return f"designs/{n}.npy" if "_t2.5" in n else f"designs/population/{n}.npy"


def asd(stack, L):
    st = dict(stack)
    st["Ls"] = L
    return float(np.sqrt(coating_brownian(np.array([100.0]), st, 0.062)[0]))


def one(args):
    name, i = args
    L = rescue.load_reference(path(name))
    out = []
    for k, meas in [(0, 0.0)] + [(4, m) for m in MEAS]:
        rng = np.random.default_rng([0, int(round(DEP * 1e5)), i])
        rng_m = np.random.default_rng([0, int(round(DEP * 1e5)), int(round(meas * 1e5)) + 1, i])
        ok, dn, Lt = rescue.trial(L, k, DEP, meas, rng, rng_meas=rng_m, return_stack=True)
        out.append((k, meas, int(ok), asd(rescue.STACK, Lt), asd(STACK_FS, Lt), rescue.noise_proxy(Lt)))
    return name, i, out


if __name__ == "__main__":
    os.makedirs("results/revision", exist_ok=True)
    rows = []
    with Pool(2) as pool:
        for name, i, out in pool.imap(one, [(n, i) for n in NAMES for i in range(N)], chunksize=20):
            base = out[0]
            for k, meas, ok, a60, a73, px in out[1:]:
                rows.append(dict(design=name, mirror=i, meas=meas, passed_rescued=ok,
                                 passed_norescue=base[2],
                                 dfull=a60 / base[3] - 1, dfull_fs=a73 / base[4] - 1,
                                 dproxy=px / base[5] - 1))
    with open("results/revision/full_noise_population.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(NAMES)} designs x {N} mirrors, independent errors {DEP:.0%}. Change in full Brownian noise "
          "at 100 Hz from rescue (k = 4), same mirror with vs without rescue.\n")
    for meas in MEAS:
        r = [x for x in rows if x["meas"] == meas]
        d = np.array([x["dfull"] for x in r]) * 100
        dfs = np.array([x["dfull_fs"] for x in r]) * 100
        dp = np.array([x["dproxy"] for x in r]) * 100
        per = [np.median([x["dfull"] for x in r if x["design"] == n]) * 100 for n in NAMES]
        print(f"measurement error {meas:.0%}: all mirrors median {np.median(d):+.3f}%, "
              f"5-95% range {np.percentile(d, 5):+.2f}% to {np.percentile(d, 95):+.2f}%, "
              f"max increase {d.max():+.2f}%")
        print(f"   per-design medians: {min(per):+.3f}% to {max(per):+.3f}%")
        print(f"   with 72.7 GPa substrate: median {np.median(dfs):+.3f}%; proxy: median {np.median(dp):+.3f}%; "
              f"proxy/full ratio of medians {np.median(dp)/np.median(d):.2f}")
