"""Per-mirror pass/fail for every design, so rescue vs no rescue can be tested
mirror by mirror (paired test), not only by comparing pass rates.

Re-runs two points with exactly the seeding of scripts/run_sweep.py (seed 0),
so the pass rates must equal the saved ones (checked at the end):
  independent errors, 2%   (same as results/population/)
  shared error, 1%         (same as results/population_shared/)
k = 0, and k = 4 at measurement error 0 / 1 / 2%. 200 mirrors.

Output: results/stats/paired_<model>_<dep>.csv, one row per (design, mirror):
  design, mirror, k0, m0, m1, m2   (1 = pass, 0 = fail)
Run: python3 scripts/paired_outcomes.py
"""
import csv
import glob
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, ".")
import rescue  # noqa: E402

N = 200
SETTINGS = [("k0", 0, 0.0), ("m0", 4, 0.0), ("m1", 4, 0.01), ("m2", 4, 0.02)]
RUNS = [("independent", 0.02, "results/population"),
        ("common", 0.01, "results/population_shared")]


def designs():
    out = {f"seed{s}": f"designs/population/seed{s}.npy" for s in range(1, 31) if s != 21}
    for d in ("lownoise_seed5_t2.5", "seed2_t2.5", "robust_seed9_t2.5"):
        out[d] = f"designs/{d}.npy"
    return out


def one(args):
    path, model, dep, i = args
    L = rescue.load_reference(path)
    res = []
    for _, k, meas in SETTINGS:
        rng = np.random.default_rng([0, int(round(dep * 1e5)), i])
        rng_m = np.random.default_rng([0, int(round(dep * 1e5)), int(round(meas * 1e5)) + 1, i])
        ok, _ = rescue.trial(L, k, dep, meas, rng, "aligo", model, 0.0, rng_meas=rng_m,
                             noise_weight=0.05, t2_target=0.025, method="local")
        res.append(int(ok))
    return res


if __name__ == "__main__":
    os.makedirs("results/stats", exist_ok=True)
    D = designs()
    assert len(D) == 32
    for model, dep, saved_dir in RUNS:
        out = f"results/stats/paired_{model}_{dep}.csv"
        with Pool(2) as pool, open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["design", "mirror"] + [s[0] for s in SETTINGS])
            for name, path in D.items():
                res = pool.map(one, [(path, model, dep, i) for i in range(N)])
                for i, r in enumerate(res):
                    w.writerow([name, i] + r)
                # check against the saved pass rates
                saved = {}
                for r in csv.DictReader(open(f"{saved_dir}/sweep_{name}.csv")):
                    if abs(float(r["dep"]) - dep) < 1e-9:
                        key = "k0" if r["k"] == "0" else f"m{int(round(float(r['meas']) * 100))}"
                        saved[key] = float(r["pass_rate"])
                got = np.mean(res, axis=0)
                for j, (key, _, _) in enumerate(SETTINGS):
                    assert abs(got[j] - saved[key]) < 1e-12, (name, model, key, got[j], saved[key])
                print(model, dep, name, "ok", flush=True)
    print("all pass rates match the saved runs")
