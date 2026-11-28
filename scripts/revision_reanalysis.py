"""Re-analyses of existing results (no new simulations).

B1 correlations with "below" entered as 0 vs 0.25%
B2 the two design families (by noise proxy), results per family
B3 paired effect sizes: per-design gain with bootstrap CI, Wilcoxon, Hodges-Lehmann
B4 results without the three exploratory designs (E1-E3)
B5 tolerable error at a 90% threshold instead of 95%
B7 noise proxy vs sturdiness with the exact (unrounded) proxy
B8 noise proxy (physical and optical thickness) vs full noise, rank correlation

Run: python3 scripts/revision_reanalysis.py > results/revision/reanalysis.txt
"""
import csv
import glob
import os
import sys
from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr, wilcoxon, binomtest
from OptimalBragg.noise import coating_brownian

sys.path.insert(0, ".")
import rescue  # noqa: E402

E = {"lownoise_seed5_t2.5": "E1", "seed2_t2.5": "E2", "robust_seed9_t2.5": "E3"}


def label(n):
    return E.get(n, "S" + n[4:])


def path(n):
    return f"designs/{n}.npy" if n in E else f"designs/population/{n}.npy"


def read(f):
    d = defaultdict(dict)
    for r in csv.DictReader(open(f)):
        key = "k0" if r["k"] == "0" else f"m{int(round(float(r['meas']) * 100))}"
        d[key][round(float(r["dep"]), 6)] = float(r["pass_rate"])
    return d


def crossing(dep, p, level):
    for i in range(1, len(dep)):
        if p[i] < level:
            if p[i - 1] < level:
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - level) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf


fine = {os.path.basename(f)[6:-4]: read(f) for f in sorted(glob.glob("results/population_fine/sweep_*.csv"))}
names = sorted(fine, key=label)
deps = sorted(fine[names[0]]["k0"])
K = ("k0", "m0", "m1", "m2")


def tol(level, below):
    out = {}
    for n in names:
        out[n] = {}
        for k in K:
            c = crossing(np.array(deps), np.array([fine[n][k][d] for d in deps]), level)
            out[n][k] = below if np.isnan(c) else c
    return out


T0 = tol(0.95, 0.0)
T25 = tol(0.95, 0.0025)
proxy = {n: rescue.noise_proxy(np.load(path(n))) for n in names}
P0 = rescue.noise_proxy(rescue.STACK["Ls"]) if False else None
v = lambda T, k, ns=names: np.array([T[n][k] for n in ns])

print("B1. Spearman correlations with 'below' entered as 0 (paper) and as 0.25%")
for lab, f in [("sturdiness vs gain, perfect measurement", lambda T: (v(T, "k0"), v(T, "m0") - v(T, "k0"))),
               ("sturdiness vs gain, 2% measurement", lambda T: (v(T, "k0"), v(T, "m2") - v(T, "k0"))),
               ("sturdiness vs loss 0 -> 2% measurement", lambda T: (v(T, "k0"), v(T, "m0") - v(T, "m2")))]:
    a = spearmanr(*f(T0)); b = spearmanr(*f(T25))
    print(f"  {lab:40s} below=0: rho {a.statistic:+.2f} p {a.pvalue:.3f} | below=0.25%: rho {b.statistic:+.2f} p {b.pvalue:.3f}")
cens = np.array([1.0 if T0[n]["m2"] == 0 else 0.0 for n in names])
r = spearmanr(v(T0, "k0"), cens)
print(f"  sturdiness vs being 'below' at 2% measurement: rho {r.statistic:+.2f} p {r.pvalue:.1g} "
      f"({int(cens.sum())} of {len(names)} below)")

print("\nB2. Two design families by noise proxy (relative to the quarter-wave stack)")
pv = np.array([proxy[n] for n in names])
order = np.sort(pv)
gap = np.argmax(np.diff(order))
cut = (order[gap] + order[gap + 1]) / 2
fam = {n: ("quiet" if proxy[n] < cut else "noisy") for n in names}
print(f"  largest gap in proxy between {order[gap]:.4g} and {order[gap+1]:.4g}: "
      f"{sum(1 for n in names if fam[n]=='quiet')} quiet, {sum(1 for n in names if fam[n]=='noisy')} noisy")
asd = {}
for n in names:
    st = dict(rescue.STACK); st["Ls"] = np.load(path(n))
    asd[n] = float(np.sqrt(coating_brownian(np.array([100.0]), st, 0.062)[0]))
for f in ("quiet", "noisy"):
    ns = [n for n in names if fam[n] == f]
    print(f"  {f}: n = {len(ns)}, noise {min(asd[n] for n in ns)*1e21:.2f}-{max(asd[n] for n in ns)*1e21:.2f} e-21; "
          "median tolerable error " + ", ".join(f"{k} {np.median(v(T0, k, ns))*100:.2f}%" for k in K)
          + f"; below at 2% meas: {sum(1 for n in ns if T0[n]['m2']==0)}")
    up = sum(T0[n]["m0"] > T0[n]["k0"] for n in ns)
    rr = spearmanr([proxy[n] for n in ns], v(T0, "k0", ns))
    print(f"     rescue raised tolerable error (perfect meas.) in {up} of {len(ns)}; "
          f"proxy vs sturdiness within family rho {rr.statistic:+.2f} p {rr.pvalue:.2f}")

print("\nB3. Paired effect sizes (perfect measurement)")
rng = np.random.default_rng(0)
for k in ("m0", "m1", "m2"):
    g = (v(T0, k) - v(T0, "k0")) * 100
    bs = [np.median(rng.choice(g, len(g))) for _ in range(2000)]
    walsh = [(g[i] + g[j]) / 2 for i in range(len(g)) for j in range(i, len(g))]
    w = wilcoxon(g)
    print(f"  {k}: median per-design change {np.median(g):+.2f} pp of sigma_dep "
          f"(95% CI {np.percentile(bs,2.5):+.2f} to {np.percentile(bs,97.5):+.2f}); "
          f"Hodges-Lehmann {np.median(walsh):+.2f}; Wilcoxon p = {w.pvalue:.1g}")
ok = v(T0, "k0") > 0
ratio = v(T0, "m0")[ok] / v(T0, "k0")[ok]
bs = [np.median(rng.choice(ratio, len(ratio))) for _ in range(2000)]
print(f"  ratio rescued/not (perfect meas.): median {np.median(ratio):.2f} "
      f"(95% CI {np.percentile(bs,2.5):.2f}-{np.percentile(bs,97.5):.2f}); "
      f"ratio of medians {np.median(v(T0,'m0'))/np.median(v(T0,'k0')):.2f}")
q1 = np.percentile(v(T0, "k0"), 25) * 100, np.percentile(v(T0, "m1"), 25) * 100
print(f"  lower quartile, no rescue vs rescue at 1% meas.: {q1[0]:.2f}% vs {q1[1]:.2f}%")

print("\nB4. Without E1-E3 (29 seeded designs)")
ns = [n for n in names if n not in E]
for k in ("m0", "m1", "m2"):
    up = sum(T0[n][k] > T0[n]["k0"] for n in ns); dn = sum(T0[n][k] < T0[n]["k0"] for n in ns)
    print(f"  {k}: median {np.median(v(T0,'k0',ns))*100:.2f}% -> {np.median(v(T0,k,ns))*100:.2f}%; "
          f"up {up}, down {dn}, sign p {binomtest(up, up+dn).pvalue:.1g}")

print("\nB5. 90% pass threshold instead of 95%")
T90 = tol(0.90, 0.0)
for k in ("m0", "m1", "m2"):
    up = sum(T90[n][k] > T90[n]["k0"] for n in names); dn = sum(T90[n][k] < T90[n]["k0"] for n in names)
    nb = sum(1 for n in names if T90[n][k] == 0)
    print(f"  {k}: median {np.median(v(T90,'k0'))*100:.2f}% -> {np.median(v(T90,k))*100:.2f}%; "
          f"up {up}, down {dn} (sign p {binomtest(up, up+dn).pvalue:.1g}); below at 0.25%: {nb}")

print("\nB7. Noise proxy vs sturdiness, exact proxy")
r = spearmanr(pv, v(T0, "k0"))
print(f"  rho {r.statistic:+.3f}, p {r.pvalue:.1g}")

print("\nB8. Proxy vs full noise across the 32 designs (rank correlation)")
nH, nL = 2.06, 1.45
isH = rescue.IS_H
phys = [rescue.noise_proxy(np.load(path(n))) for n in names]
gam = rescue.GAM_H
opt = [nL * np.load(path(n))[~isH].sum() + gam * nH * np.load(path(n))[isH].sum() for n in names]
tant = [np.load(path(n))[isH].sum() for n in names]
full = [asd[n] for n in names]
for lab, x in [("proxy as used (physical thickness)", phys), ("E0900068 form (optical thickness)", opt),
               ("total tantala thickness", tant)]:
    print(f"  {lab:38s} rho = {spearmanr(x, full).statistic:.3f}")
print(f"  gamma_H = {gam:.3f} with the library substrate Y = {rescue.STACK['sub'].Y/1e9:.0f} GPa")
