"""Statistical checks for the 32-design study.

1. Sign tests: is "rescue raised it in X of 32 designs" more than chance?
2. Paired test per design (exact McNemar), mirror by mirror, from
   results/stats/paired_*.csv (made by scripts/paired_outcomes.py).
3. All Spearman correlations reported in the paper, with Holm correction.
4. How much the "below = 0" choice matters.

Uses only saved results. Run:
  python3 scripts/stats_checks.py > results/stats/stats_checks.txt
"""
import csv
import glob
import os
import sys
from collections import defaultdict

import numpy as np
from scipy.stats import binomtest, spearmanr

sys.path.insert(0, ".")
import rescue  # noqa: E402

LEVEL = 0.95
KEYS = ("k0", "m0", "m1", "m2")
MEAS = {"m0": "perfect measurement", "m1": "1% measurement error", "m2": "2% measurement error"}


def read(path):
    d = defaultdict(dict)
    for r in csv.DictReader(open(path)):
        key = "k0" if r["k"] == "0" else f"m{int(round(float(r['meas']) * 100))}"
        d[key][round(float(r["dep"]), 6)] = float(r["pass_rate"])
    return d


def crossing(dep, p):
    """Same rule as scripts/population_tolerable.py; nan = 'below'."""
    for i in range(1, len(dep)):
        if p[i] < LEVEL:
            if p[i - 1] < LEVEL:
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - LEVEL) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf


def path_of(name):
    return f"designs/{name}.npy" if "_t2.5" in name else f"designs/population/{name}.npy"


fine = {os.path.basename(f)[6:-4]: read(f) for f in sorted(glob.glob("results/population_fine/sweep_*.csv"))}
names = sorted(fine)
assert len(names) == 32
deps = sorted(fine[names[0]]["k0"])
tol_raw = {n: {k: crossing(np.array(deps), np.array([fine[n][k][d] for d in deps])) for k in KEYS} for n in names}
tol = {n: {k: (0.0 if np.isnan(v) else v) for k, v in tol_raw[n].items()} for n in names}
proxy = {n: rescue.noise_proxy(np.load(path_of(n))) for n in names}


def point(dirname, dep):
    out = {}
    for n in names:
        d = read(f"{dirname}/sweep_{n}.csv")
        out[n] = {k: d[k][dep] for k in KEYS}
    return out


runs = {"independent 2%": point("results/population", 0.02),
        "shared 1%": point("results/population_shared", 0.01),
        "shared 2%": point("results/population_shared", 0.02)}


def sign(up, down):
    return binomtest(up, up + down, 0.5).pvalue if up + down else 1.0


# ---------- 1. sign tests ----------
print("1. SIGN TESTS (ties left out; null: up and down equally likely)\n")
print("Tolerable error, independent errors (fine scan):")
for k in ("m0", "m1", "m2"):
    up = sum(tol[n][k] > tol[n]["k0"] for n in names)
    down = sum(tol[n][k] < tol[n]["k0"] for n in names)
    print(f"  rescue, {MEAS[k]:22s}: up {up:2d}, down {down:2d}, tie {32-up-down}  p = {sign(up, down):.1g}")
for run, d in runs.items():
    print(f"Pass rate, {run}:")
    for k in ("m0", "m1", "m2"):
        up = sum(d[n][k] > d[n]["k0"] for n in names)
        down = sum(d[n][k] < d[n]["k0"] for n in names)
        print(f"  rescue, {MEAS[k]:22s}: up {up:2d}, down {down:2d}, tie {32-up-down}  p = {sign(up, down):.1g}")

# ---------- 2. paired test per design ----------
print("\n2. PAIRED TEST PER DESIGN (exact McNemar: same 200 mirrors with and without rescue)")
print("   b = mirrors saved by the rescue, c = mirrors broken by it; p = two-sided binomial on b vs c.")
print("   Holm correction over the 32 designs of each row.\n")


def holm(ps):
    ps = np.asarray(ps); order = np.argsort(ps); m = len(ps)
    adj = np.empty(m); run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * ps[i])); adj[i] = run
    return adj


for f in sorted(glob.glob("results/stats/paired_*.csv")):
    rows = defaultdict(list)
    for r in csv.DictReader(open(f)):
        rows[r["design"]].append([int(r[k]) for k in KEYS])
    assert sorted(rows) == names, f
    print(os.path.basename(f))
    for j, k in enumerate(KEYS[1:], start=1):
        res = []
        for n in names:
            a = np.array(rows[n])
            b = int(np.sum((a[:, j] == 1) & (a[:, 0] == 0)))
            c = int(np.sum((a[:, j] == 0) & (a[:, 0] == 1)))
            res.append((b, c, sign(b, c)))
        adj = holm([r[2] for r in res])
        better = sum(1 for (b, c, _), q in zip(res, adj) if q < 0.05 and b > c)
        worse = sum(1 for (b, c, _), q in zip(res, adj) if q < 0.05 and c > b)
        better_raw = sum(1 for b, c, p in res if p < 0.05 and b > c)
        worse_raw = sum(1 for b, c, p in res if p < 0.05 and c > b)
        tb = sum(r[0] for r in res); tc = sum(r[1] for r in res)
        print(f"  rescue, {MEAS[k]:22s}: significantly better in {better_raw:2d} (Holm: {better:2d}), "
              f"worse in {worse_raw:2d} (Holm: {worse:2d}); all designs: {tb} saved, {tc} broken")
    print()

# ---------- 3. correlations with Holm ----------
print("3. SPEARMAN CORRELATIONS REPORTED IN THE PAPER, Holm-corrected over all of them\n")
tests = []
v = {k: np.array([tol[n][k] for n in names]) for k in KEYS}
px = np.array([proxy[n] for n in names])
tests += [("fine scan: noise proxy vs tolerable error (no rescue)", px, v["k0"]),
          ("fine scan: sturdiness vs gain, perfect measurement", v["k0"], v["m0"] - v["k0"]),
          ("fine scan: sturdiness vs gain, 2% measurement", v["k0"], v["m2"] - v["k0"]),
          ("fine scan: sturdiness vs loss from 0 to 2% measurement", v["k0"], v["m0"] - v["m2"])]
for run, d in runs.items():
    p = {k: np.array([d[n][k] for n in names]) for k in KEYS}
    tests += [(f"{run}: noise proxy vs pass rate (no rescue)", px, p["k0"]),
              (f"{run}: sturdiness vs gain, perfect measurement", p["k0"], p["m0"] - p["k0"]),
              (f"{run}: sturdiness vs gain, 2% measurement", p["k0"], p["m2"] - p["k0"]),
              (f"{run}: sturdiness vs loss from 0 to 2% measurement", p["k0"], p["m0"] - p["m2"])]
rhos = [spearmanr(a, b) for _, a, b in tests]
adj = holm([r.pvalue for r in rhos])
print(f"  {len(tests)} tests.")
for (lab, _, _), r, q in zip(tests, rhos, adj):
    flag = "significant" if q < 0.05 else "not significant"
    print(f"  {lab:62s} rho = {r.statistic:+.2f}  p = {r.pvalue:.1g}  Holm p = {q:.1g}  {flag}")

# ---------- 4. the "below = 0" choice ----------
print("\n4. HOW MUCH THE 'BELOW = 0' CHOICE MATTERS (fine scan)\n")
for k in KEYS:
    raw = np.array([tol_raw[n][k] for n in names])
    nb = int(np.isnan(raw).sum())
    a0 = np.where(np.isnan(raw), 0.0, raw)
    a25 = np.where(np.isnan(raw), 0.0025, raw)
    ex = raw[~np.isnan(raw)]
    print(f"  {k}: {nb:2d} 'below'. Median with below = 0: {np.median(a0)*100:.2f}%; "
          f"below = 0.25%: {np.median(a25)*100:.2f}%; below left out: "
          f"{(np.median(ex)*100 if len(ex) else float('nan')):.2f}% (of {len(ex)})")
print("  Spearman uses ranks, so 'below' is the lowest rank whether it is entered as 0 or 0.25%.")
print("  Leaving 'below' out would drop the designs that did worst, which flatters the rescue.")
