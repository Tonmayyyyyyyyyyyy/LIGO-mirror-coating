"""Gated rescue (A1) and number of rescued layers (A3), from results/revision/.

Gated rule: rescue a mirror only if its measured stack, finished with the planned
top layers, fails the spec. Compared with no rescue and always-rescue
(results/population_fine) on the same 200 mirrors per point.
Tolerable error = first 95% crossing, linear interpolation, "below" = 0.
Run: python3 scripts/revision_gated_k.py > results/revision/gated_k.txt
"""
import csv, glob, os
from collections import defaultdict
import numpy as np
from scipy.stats import binomtest, wilcoxon

def read(f, key):
    d = defaultdict(dict)
    for r in csv.DictReader(open(f)):
        d[key(r)][round(float(r["dep"]), 6)] = float(r["pass_rate"])
    return d

def crossing(dep, p, level=0.95):
    for i in range(1, len(dep)):
        if p[i] < level:
            if p[i-1] < level:
                return 0.0 if i == 1 else dep[i-1]
            return dep[i-1] + (p[i-1]-level)/(p[i-1]-p[i])*(dep[i]-dep[i-1])
    return np.inf

mk = lambda r: "k0" if r["k"] == "0" else f"m{int(round(float(r['meas'])*100))}"
gk = lambda r: f"g{int(round(float(r['meas'])*100))}"
names = [os.path.basename(f)[6:-4] for f in sorted(glob.glob("results/revision/gated/sweep_*.csv"))]
T, P = {}, {}
for n in names:
    a = read(f"results/population_fine/sweep_{n}.csv", mk)
    a.update(read(f"results/revision/gated/sweep_{n}.csv", gk))
    deps = sorted(a["k0"])
    T[n] = {k: crossing(np.array(deps), np.array([a[k][d] for d in deps])) for k in a}
    P[n] = a
print(f"{len(names)} designs, 200 mirrors per point, independent errors\n")
print("A1. Tolerable error (95%), median over designs; per-design comparison")
v = lambda k: np.array([T[n][k] for n in names])
for m in ("0", "1", "2"):
    k0, al, ga = v("k0"), v("m" + m), v("g" + m)
    print(f" meas {m}%: no rescue {np.median(k0)*100:.2f}%  always {np.median(al)*100:.2f}%  gated {np.median(ga)*100:.2f}%"
          f"  | below: always {sum(al==0)}, gated {sum(ga==0)}")
    for lab, x in (("gated vs no rescue", ga - k0), ("gated vs always", ga - al)):
        up, dn = int((x > 0).sum()), int((x < 0).sum())
        p = binomtest(up, up+dn).pvalue if up+dn else 1
        w = wilcoxon(x).pvalue if np.any(x != 0) else 1
        print(f"     {lab:20s} up {up:2d} down {dn:2d} (sign p {p:.2g}); median change {np.median(x)*100:+.2f} pp, Wilcoxon p {w:.2g}")
print("\n Pass rate at the smallest error (0.25%), median over designs [min]:")
for k in ("k0", "m0", "m1", "m2", "g0", "g1", "g2"):
    x = [P[n][k][0.0025] for n in names]
    print(f"   {k}: {np.median(x)*100:.1f}% [{min(x)*100:.1f}%]")
print(" Pass rate at 2% error, median over designs:")
for k in ("k0", "m0", "m1", "m2", "g0", "g1", "g2"):
    print(f"   {k}: {np.median([P[n][k][0.02] for n in names])*100:.1f}%")

for d, lab in (("k_indep", "independent 2%"), ("k_shared", "shared 1%")):
    fs = sorted(glob.glob(f"results/revision/{d}/sweep_*.csv"))
    if not fs: continue
    rows = defaultdict(dict)
    for f in fs:
        n = os.path.basename(f)[6:-4]
        for r in csv.DictReader(open(f)):
            rows[n][int(r["k"])] = float(r["pass_rate"])
    ref = "results/population_fine" if d == "k_indep" else None
    print(f"\nA3. Pass rate vs number of rescued layers, {lab}, perfect measurement ({len(rows)} designs)")
    ks = sorted(next(iter(rows.values())))
    for k in ks:
        x = np.array([rows[n][k] for n in rows])
        print(f"   k = {k:2d}: median {np.median(x)*100:5.1f}%, lower quartile {np.percentile(x,25)*100:5.1f}%, min {x.min()*100:5.1f}%, designs >= 95%: {(x>=0.95).sum()}")
    best = [max(ks, key=lambda k: rows[n][k]) for n in rows]
    print("   best k per design: " + ", ".join(f"k={k}: {best.count(k)}" for k in ks))
    x4, x12 = np.array([rows[n][4] for n in rows]), np.array([rows[n][max(ks)] for n in rows])
    up, dn = int((x12 > x4).sum()), int((x12 < x4).sum())
    print(f"   k = {max(ks)} vs 4: up {up}, down {dn}, sign p {binomtest(up, up+dn).pvalue:.2g}")

fs = sorted(glob.glob("results/revision/de_shared/sweep_*.csv"))
if fs:
    de, lo, k0 = {}, {}, {}
    for f in fs:
        n = os.path.basename(f)[6:-4]
        de[n] = float(next(csv.DictReader(open(f)))["pass_rate"])
        for r in csv.DictReader(open(f"results/revision/k_shared/sweep_{n}.csv")):
            if r["k"] == "4": lo[n] = float(r["pass_rate"])
        for r in csv.DictReader(open(f"results/population_shared/sweep_{n}.csv")) if os.path.exists(f"results/population_shared/sweep_{n}.csv") else []:
            if r["k"] == "0" and abs(float(r["dep"]) - 0.01) < 1e-9: k0[n] = float(r["pass_rate"])
    ns = sorted(de)
    d = np.array([de[n] - lo[n] for n in ns])
    up, dn = int((d > 0).sum()), int((d < 0).sum())
    print(f"\nA4. Global (DE) vs fast local optimizer, k = 4, shared 1%, perfect measurement ({len(ns)} designs, same mirrors)")
    print(f"   median pass rate: local {np.median([lo[n] for n in ns])*100:.1f}%, DE {np.median([de[n] for n in ns])*100:.1f}%"
          + (f", no rescue {np.median([k0[n] for n in ns if n in k0])*100:.1f}% ({len(k0)} designs)" if k0 else ""))
    print(f"   DE better on {up}, worse on {dn}, equal on {len(ns)-up-dn} (sign p {binomtest(up, up+dn).pvalue:.2g}); "
          f"median gain {np.median(d)*100:+.1f} pts, max {d.max()*100:+.1f} pts")
    print(f"   designs >= 95%: local {sum(lo[n]>=0.95 for n in ns)}, DE {sum(de[n]>=0.95 for n in ns)}")
    big = sorted(ns, key=lambda n: -(de[n]-lo[n]))[:3]
    print("   largest gains: " + ", ".join(f"{n} {lo[n]*100:.1f}->{de[n]*100:.1f}%" for n in big))
