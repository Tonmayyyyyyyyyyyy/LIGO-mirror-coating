"""Pass rate of the rescued end mirror over a grid of settings.

Example (quick):
  python scripts/run_sweep.py --trials 20 --k 0 4 --dep 0.02 --meas 0 0.01

Writes one row per (k, deposition error, measurement error) to a CSV in
results/ and prints a table. Use --model common for the common-factor check.
"""
import argparse
import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rescue  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("--trials", type=int, default=200)
p.add_argument("--k", type=int, nargs="+", default=[0, 2, 4, 6, 8])
p.add_argument("--dep", type=float, nargs="+", default=[0.005, 0.01, 0.02, 0.03])
p.add_argument("--meas", type=float, nargs="+", default=[0.0, 0.0025, 0.005, 0.01])
p.add_argument("--abs-nm", type=float, default=0.0, help="absolute deposition error, nm")
p.add_argument("--spec", default="aligo", choices=list(rescue.SPECS))
p.add_argument("--model", default="independent", choices=["independent", "common"])
p.add_argument("--seed", type=int, default=0)
p.add_argument("--out", default=None)
a = p.parse_args()

L = rescue.load_reference()
os.makedirs("results", exist_ok=True)
out = a.out or (f"results/sweep_{a.model}_{a.spec}_n{a.trials}_"
                f"{time.strftime('%Y%m%d-%H%M%S')}.csv")

rows = []
print(f"{'k':>2} {'dep%':>5} {'meas%':>6} {'pass':>5} {'+/-':>5} {'noise%':>7}")
for dep in a.dep:
    for meas in a.meas:
        for k in a.k:
            # Same deposited mirrors for every k and measurement level:
            # differences come from k and measurement, not from luck.
            rng = np.random.default_rng([a.seed, int(round(dep * 1e5))])
            rng_m = np.random.default_rng([a.seed, int(round(dep * 1e5)),
                                           int(round(meas * 1e5)) + 1])
            res = [rescue.trial(L, k, dep, meas, rng, a.spec, a.model,
                                a.abs_nm * 1e-9, rng_meas=rng_m)
                   for _ in range(a.trials)]
            ok = np.array([r[0] for r in res], float)
            dn = np.array([r[1] for r in res])
            pr, se = ok.mean(), np.sqrt(ok.mean() * (1 - ok.mean()) / len(ok))
            rows.append(dict(k=k, dep=dep, meas=meas, trials=a.trials,
                             pass_rate=pr, stderr=se, noise_change=dn.mean(),
                             model=a.model, spec=a.spec, abs_nm=a.abs_nm))
            print(f"{k:>2} {dep*100:5.2f} {meas*100:6.2f} {pr:5.2f} {se:5.2f} "
                  f"{dn.mean()*100:+7.2f}", flush=True)

with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
print("saved", out)
