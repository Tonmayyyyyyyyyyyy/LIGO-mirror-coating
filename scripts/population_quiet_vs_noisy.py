"""Can the rescue make quiet (fragile) designs as error-tolerant as noisy (sturdy) ones?

Uses only saved results:
  results/population/summary.txt       noise proxy and full noise per design
  results/population_fine/summary.txt  tolerable error per design
Groups: the 10 quietest and the 10 noisiest of the 32 designs (by noise proxy).
"below" counts as 0, as in population_tolerable.py.
Run: python3 scripts/population_quiet_vs_noisy.py > results/population_fine/quiet_vs_noisy.txt
"""
import re
import numpy as np
from scipy.stats import spearmanr

px, asd = {}, {}
for line in open("results/population/summary.txt"):
    m = re.match(r"(\S+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ok", line)
    if m:
        px[m.group(1)], asd[m.group(1)] = float(m.group(4)), float(m.group(5))

tol = {}
for line in open("results/population_fine/summary.txt"):
    p = line.split()
    if len(p) > 6 and p[0] in px:
        v = lambda s: 0.0 if s == "below" else float(s.rstrip("%"))
        tol[p[0]] = [v(p[1]), v(p[3]), v(p[5]), v(p[6])]   # k0, m0, m1, m2
assert len(tol) == 32, len(tol)

names = sorted(tol, key=lambda k: px[k])
rho, p = spearmanr([px[k] for k in names], [tol[k][0] for k in names])
print(f"32 designs. Noise proxy vs tolerable error without rescue: Spearman rho = {rho:+.2f}, p = {p:.1g}")
print(f"Full noise at 100 Hz over all 32: {min(asd.values()):.2f}-{max(asd.values()):.2f} e-21 m/rtHz\n")
print("Median tolerable error (%) of each group:")
print(f"{'group':14s} {'noise':>6s} {'no rescue':>10s} {'meas 0%':>8s} {'meas 1%':>8s} {'meas 2%':>8s}")
for lab, g in [("10 quietest", names[:10]), ("10 noisiest", names[-10:])]:
    med = [np.median([tol[k][i] for k in g]) for i in range(4)]
    print(f"{lab:14s} {np.median([asd[k] for k in g]):6.2f} {med[0]:10.2f} {med[1]:8.2f} {med[2]:8.2f} {med[3]:8.2f}")
