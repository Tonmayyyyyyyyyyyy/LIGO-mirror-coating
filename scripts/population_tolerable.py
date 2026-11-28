"""Research question 1 on the whole population: tolerable error per design.

Reads results/population_fine/sweep_*.csv (made by population_fine.sh).
For each design and each curve (no rescue; rescue of top 4 layers at 0 / 1 /
2% measurement error), the tolerable error is the deposition error where the
pass rate first drops below 95%, by linear interpolation between steps (same
rule as scripts/day7_bootstrap.py). Its 95% range comes from a parametric
bootstrap: 2000 redraws of every pass count, random seed 0.

"below" = already under 95% at the smallest error tested (0.25%), entered
as 0 in medians and counts. ">3%" = never drops below 95% in the range,
entered as 3%. Both are flagged in the table.

Also reports the noise change from rescue (fast proxy, as stored in the
sweep CSVs) and rank correlations with sturdiness.
"""
import csv
import glob
import os
from collections import defaultdict
import numpy as np
from scipy.stats import spearmanr

LEVEL, NBOOT, TOP = 0.95, 2000, 0.03


def crossing(dep, p):
    for i in range(1, len(dep)):
        if p[i] < LEVEL:
            if p[i - 1] < LEVEL:
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - LEVEL) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf


def as_value(c):
    return 0.0 if np.isnan(c) else (TOP if np.isinf(c) else c)


def label(c):
    return " below" if np.isnan(c) else (" >3%  " if np.isinf(c) else f"{c*100:5.2f}%")


rng = np.random.default_rng(0)
designs = []
for f in sorted(glob.glob("results/population_fine/sweep_*.csv")):
    curves, noise = defaultdict(list), defaultdict(list)
    for r in csv.DictReader(open(f)):
        key = "k0" if r["k"] == "0" else f"m{int(round(float(r['meas']) * 100))}"
        curves[key].append((float(r["dep"]), float(r["pass_rate"]), int(r["trials"])))
        noise[key].append(float(r["noise_change"]))
    if set(curves) != {"k0", "m0", "m1", "m2"} or len({len(v) for v in curves.values()}) != 1:
        print("incomplete, skipped:", f)
        continue
    d = dict(name=os.path.basename(f)[6:-4])
    for key, rows in curves.items():
        rows.sort()
        dep = np.array([r[0] for r in rows]); p = np.array([r[1] for r in rows])
        n = np.array([r[2] for r in rows])
        c = crossing(dep, p)
        b = np.array([as_value(crossing(dep, rng.binomial(n, p) / n)) for _ in range(NBOOT)])
        d[key] = c
        d[key + "_lo"], d[key + "_hi"] = np.percentile(b, [2.5, 97.5])
    d["dnoise"] = np.mean(noise["m0"]) - np.mean(noise["k0"])
    designs.append(d)

designs.sort(key=lambda d: as_value(d["k0"]))
print(f"{len(designs)} designs. Tolerable error = largest deposition error with 95% pass "
      "(independent errors, 200 mirrors per point, same mirrors for every design).\n"
      "Rescue = top 4 layers. In brackets: 95% range from bootstrap.\n")
print(f"{'design':20s} {'no rescue':>22s} {'rescue, meas 0%':>22s} {'meas 1%':>9s} {'meas 2%':>9s}")
for d in designs:
    print(f"{d['name']:20s} {label(d['k0'])} [{d['k0_lo']*100:4.2f}-{d['k0_hi']*100:4.2f}]  "
          f"{label(d['m0'])} [{d['m0_lo']*100:4.2f}-{d['m0_hi']*100:4.2f}]  "
          f"{label(d['m1'])}   {label(d['m2'])}")

v = {k: np.array([as_value(d[k]) for d in designs]) for k in ("k0", "m0", "m1", "m2")}
N = len(designs)
print(f"\nMedian tolerable error over {N} designs:")
for k, lab in [("k0", "no rescue"), ("m0", "rescue, perfect measurement"),
               ("m1", "rescue, 1% measurement error"), ("m2", "rescue, 2% measurement error")]:
    q1, q3 = np.percentile(v[k], [25, 75]) * 100
    print(f"  {lab:32s} {np.median(v[k])*100:.2f}%   (middle half of designs: {q1:.2f}-{q3:.2f}%)")

print("\nCounts:")
for k, lab in [("m0", "perfect measurement"), ("m1", "1% measurement error"), ("m2", "2% measurement error")]:
    up = int(np.sum(v[k] > v["k0"]))
    clear_up = sum(1 for d in designs if d[k + "_lo"] > d["k0_hi"])
    down = int(np.sum(v[k] < v["k0"]))
    clear_down = sum(1 for d in designs if d[k + "_hi"] < d["k0_lo"])
    print(f"  {lab:22s}: rescue raises tolerable error in {up} of {N} "
          f"({clear_up} with no overlap of 95% ranges); lowers it in {down} ({clear_down} clearly)")
ok = v["k0"] > 0
ratio = v["m0"][ok] / v["k0"][ok]
print(f"\nRatio rescued / not rescued (perfect measurement), designs with a nonzero baseline "
      f"({ok.sum()}): median {np.median(ratio):.2f}, range {ratio.min():.2f}-{ratio.max():.2f}")

print("\nSpearman rank correlations:")
for a, b, lab in [(v["k0"], v["m0"] - v["k0"], "sturdiness (no-rescue tolerable error) vs gain, perfect measurement"),
                  (v["k0"], v["m2"] - v["k0"], "sturdiness vs gain, 2% measurement error"),
                  (v["k0"], v["m0"] - v["m2"], "sturdiness vs loss from 0 to 2% measurement error")]:
    rho, p = spearmanr(a, b)
    print(f"  {lab}: rho = {rho:+.2f}, p = {p:.3f}")

dn = np.array([d["dnoise"] for d in designs]) * 100
print(f"\nNoise change from rescue (fast proxy, mean over all error sizes): median {np.median(dn):+.2f}%, "
      f"range {dn.min():+.2f}% to {dn.max():+.2f}%")
