"""Day 7: uncertainty on the main number (largest error with 95% pass rate).

For each (k, measurement error) curve in a fine-scan CSV, the crossing of
95% is found by linear interpolation between error steps, at the first step
that drops below 95%. To get its uncertainty we redraw every pass count from
a binomial with the measured pass rate (parametric bootstrap, 2000 draws)
and recompute the crossing. Each curve is redrawn independently; the real
curves share their random mirrors, so the uncertainty on the *difference*
between curves is, if anything, overstated.

Usage: python3 scripts/day7_bootstrap.py results/day5/fine_sturdy.csv
"""
import sys
import csv
from collections import defaultdict
import numpy as np

LEVEL, NBOOT = 0.95, 2000


def crossing(dep, p):
    for i in range(1, len(dep)):
        if p[i] < LEVEL:
            if p[i - 1] < LEVEL:          # already below at the first step
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - LEVEL) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf                          # never drops below within range


curves = defaultdict(list)
for r in csv.DictReader(open(sys.argv[1])):
    meas = r["meas"] if r["k"] != "0" else ""
    curves[(int(r["k"]), meas)].append((float(r["dep"]), float(r["pass_rate"]), int(r["trials"])))

rng = np.random.default_rng(0)
print(f"{sys.argv[1]}\n k  meas   tolerable error   68% range        95% range")
for (k, meas), rows in sorted(curves.items()):
    rows.sort()
    dep = np.array([r[0] for r in rows]); p = np.array([r[1] for r in rows])
    n = np.array([r[2] for r in rows])
    c0 = crossing(dep, p)
    boot = np.array([crossing(dep, rng.binomial(n, p) / n) for _ in range(NBOOT)])
    # below the first error step -> 0 (shown as "<1%"); above the last -> 99
    boot = np.nan_to_num(boot, nan=0.0, posinf=0.99)
    q = np.percentile(boot, [16, 84, 2.5, 97.5]) * 100
    f = lambda x: "  <1% " if x == 0 else (" >3%  " if x > 90 else f"{x:.2f}%")
    c = f(0.0 if np.isnan(c0) else min(c0, 0.99) * 100)
    m = "  -  " if meas == "" else f"{float(meas):.0%}".rjust(4) + " "
    print(f" {k}  {m}  {c}          {f(q[0])}-{f(q[1])}      {f(q[2])}-{f(q[3])}")
