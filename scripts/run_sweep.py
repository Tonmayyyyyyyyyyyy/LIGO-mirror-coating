"""Pass rate of the rescued end mirror over a grid of settings.

Example (quick):
  python scripts/run_sweep.py --trials 20 --k 0 4 --dep 0.02 --meas 0 0.01

Writes one row per (k, deposition error, measurement error) to a CSV in
results/ and prints a table. Use --model common for the common-factor check.

Random numbers: trial i always gets the same deposition errors for a given
deposition level (same mirror across every k and measurement level), and its
own measurement errors per measurement level. So differences between rows
come from k and measurement, not luck. Trials run in parallel (--jobs).
"""
import argparse
import csv
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import rescue  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--trials", type=int, default=200)
p.add_argument("--k", type=int, nargs="+", default=[0, 2, 4, 6, 8])
p.add_argument("--dep", type=float, nargs="+", default=[0.005, 0.01, 0.02, 0.03])
p.add_argument("--meas", type=float, nargs="+", default=[0.0, 0.0025, 0.005, 0.01, 0.02])
p.add_argument("--abs-nm", type=float, default=0.0, help="absolute deposition error, nm")
p.add_argument("--spec", default="aligo", choices=list(rescue.SPECS))
p.add_argument("--model", default="independent", choices=["independent", "common"])
p.add_argument("--method", default="local", choices=["local", "de"])
p.add_argument("--t2", type=float, default=0.025, help="532 nm target used by the rescue")
p.add_argument("--noise-weight", type=float, default=0.05)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--jobs", type=int, default=os.cpu_count())
p.add_argument("--out", default=None)
a = p.parse_args()

L = rescue.load_reference()


def one(args):
    i, k, dep, meas = args
    rng = np.random.default_rng([a.seed, int(round(dep * 1e5)), i])
    rng_m = np.random.default_rng([a.seed, int(round(dep * 1e5)),
                                   int(round(meas * 1e5)) + 1, i])
    return rescue.trial(L, k, dep, meas, rng, a.spec, a.model, a.abs_nm * 1e-9,
                        rng_meas=rng_m, noise_weight=a.noise_weight,
                        t2_target=a.t2, method=a.method)


if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    out = a.out or (f"results/sweep_{a.model}_{a.spec}_{a.method}_n{a.trials}_"
                    f"{time.strftime('%Y%m%d-%H%M%S')}.csv")
    rows = []
    t0 = time.time()
    print(f"{'k':>2} {'dep%':>5} {'meas%':>6} {'pass':>5} {'+/-':>5} {'noise%':>7}")
    with Pool(a.jobs) as pool:
        for dep in a.dep:
            for meas in a.meas:
                for k in a.k:
                    if k == 0 and meas != a.meas[0]:
                        continue        # k = 0 never uses the measurement
                    res = pool.map(one, [(i, k, dep, meas) for i in range(a.trials)])
                    ok = np.array([r[0] for r in res], float)
                    dn = np.array([r[1] for r in res])
                    pr = ok.mean()
                    se = np.sqrt(pr * (1 - pr) / len(ok))
                    rows.append(dict(k=k, dep=dep, meas=meas if k else "", trials=a.trials,
                                     pass_rate=pr, stderr=se, noise_change=dn.mean(),
                                     model=a.model, spec=a.spec, method=a.method,
                                     t2_target=a.t2, noise_weight=a.noise_weight,
                                     abs_nm=a.abs_nm))
                    print(f"{k:>2} {dep*100:5.2f} {(meas*100 if k else float('nan')):6.2f} "
                          f"{pr:5.2f} {se:5.2f} {dn.mean()*100:+7.2f}", flush=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"saved {out} ({time.time()-t0:.0f} s)")
