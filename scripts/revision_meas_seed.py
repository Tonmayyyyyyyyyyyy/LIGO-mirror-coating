"""Extra measurement levels (A2) and second master seed (A5), from results/revision/.

A2: pass rate with rescue (k = 4, always rescue) at measurement errors 0, 0.5, 1, 1.5, 2%,
    compared with no rescue on the same 200 mirrors, at sigma_dep 0.25, 0.5, 1, 2%.
A5: rescue vs no rescue per design, seed 0 (main runs) and seed 1 (new mirrors).
Run: python3 scripts/revision_meas_seed.py > results/revision/meas_seed.txt
"""
import csv, glob, os
from collections import defaultdict
import numpy as np
from scipy.stats import binomtest, spearmanr

def load(f):
    d = {}
    for r in csv.DictReader(open(f)):
        key = (int(r["k"]), round(float(r["dep"]), 6), 0.0 if r["meas"] == "" else round(float(r["meas"]), 6))
        d[key] = float(r["pass_rate"])
    return d

names = [os.path.basename(f)[6:-4] for f in sorted(glob.glob("results/revision/meas_extra/sweep_*.csv"))]
print(f"{len(names)} designs, 200 mirrors per point, independent errors, always rescue, k = 4\n")
print("A2. Rescue minus no rescue, per design (pass rate, same mirrors)")
print(f"{'dep':>5s} {'meas':>5s} {'median pass':>11s} {'no rescue':>9s} {'better':>6s} {'worse':>5s} {'sign p':>7s}")
for dep in (0.0025, 0.005, 0.01, 0.02):
    for meas in (0.0, 0.005, 0.01, 0.015, 0.02):
        r, b = [], []
        for n in names:
            a = load(f"results/population_fine/sweep_{n}.csv"); a.update(load(f"results/revision/meas_extra/sweep_{n}.csv"))
            b.append(a[(0, dep, 0.0)]); r.append(a[(4, dep, meas)])
        d = np.array(r) - np.array(b); up, dn = int((d > 0).sum()), int((d < 0).sum())
        p = binomtest(up, up + dn).pvalue if up + dn else 1.0
        print(f"{dep*100:4.2f}% {meas*100:4.1f}% {np.median(r)*100:10.1f}% {np.median(b)*100:8.1f}% {up:6d} {dn:5d} {p:7.2g}")
    print()

print("A5. Second master seed: rescue (k = 4) minus no rescue, per design")
print(f"{'model':12s} {'dep':>5s} {'meas':>4s} | {'seed 0: better/worse, p':>24s} | {'seed 1: better/worse, p':>24s} | rank agreement of gain")
for model, d0, d1, deps in (("independent", "population_fine", "seed1_indep", (0.0025, 0.02)),
                            ("shared", "population_shared", "seed1_shared", (0.01, 0.02))):
    for dep in deps:
        for meas in (0.0, 0.01, 0.02):
            out, gains = [], []
            for d in (d0, d1):
                g = []
                for n in names:
                    a = load(f"results/{d}/sweep_{n}.csv" if d.startswith("pop") else f"results/revision/{d}/sweep_{n}.csv")
                    g.append(a[(4, dep, meas)] - a[(0, dep, 0.0)])
                g = np.array(g); up, dn = int((g > 0).sum()), int((g < 0).sum())
                out.append(f"{up:2d}/{dn:2d}, p {binomtest(up, up+dn).pvalue if up+dn else 1:7.2g}, med {np.median(g)*100:+5.1f}")
                gains.append(g)
            rho = spearmanr(*gains).statistic if np.std(gains[0]) and np.std(gains[1]) else float("nan")
            print(f"{model:12s} {dep*100:4.2f}% {meas*100:3.0f}% | {out[0]:>24s} | {out[1]:>24s} | rho {rho:+.2f}")
