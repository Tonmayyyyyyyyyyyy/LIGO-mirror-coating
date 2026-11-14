"""Summarize the population study: many designs, one test each.

Reads results/population/sweep_*.csv (made by population_study.sh), loads
each design, and reports per design: transmissions, noise, pass rate at 2%
deposition error without rescue (k=0) and with rescue of the top 4 layers
at 0 / 1 / 2% measurement error. Then counts how many designs show each
pattern. Works on whatever CSVs exist so far.
"""
import csv
import glob
import os
import sys
import numpy as np
from scipy.stats import spearmanr
sys.path.insert(0, ".")
import rescue
from OptimalBragg.noise import coating_brownian
from OptimalBragg import Material, qw_stack
from OptimalBragg.materials import SiO2, TiTa2O5, air

sub = Material(SiO2); sub.Temp = 295
Q = qw_stack(rescue.LAM1, sub, Material(air), {"L": Material(SiO2), "H": Material(TiTa2O5)},
             "HL" * (rescue.N_PAIRS - 1) + "H", hwcap="L")["Ls"]
P0 = rescue.noise_proxy(Q)


def asd(L):
    rescue.STACK["Ls"] = L
    return float(np.sqrt(coating_brownian(np.array([100.0]), rescue.STACK, 0.062)[0]))


rows = []
for f in sorted(glob.glob("results/population/sweep_*.csv")):
    r = {}
    for row in csv.DictReader(open(f)):
        key = (int(row["k"]), row["meas"])
        r[key] = (float(row["pass_rate"]), float(row["stderr"]))
        design = row["design"]
    need = [(0, ""), (4, "0.0"), (4, "0.01"), (4, "0.02")]
    if not all(k in r for k in need):
        print("incomplete:", f); continue
    path = ("designs/population/" if design.startswith("seed") and "_t2.5" not in design
            else "designs/") + design
    L = np.load(path)
    T1, T2 = rescue.transmissions(L)
    name = os.path.basename(f)[6:-4]
    rows.append(dict(name=name, T1=T1 * 1e6, T2=T2 * 100, proxy=rescue.noise_proxy(L) / P0,
                     asd=asd(L) * 1e21, spec=rescue.passes(L),
                     k0=r[(0, "")][0], se0=r[(0, "")][1],
                     m0=r[(4, "0.0")][0], m1=r[(4, "0.01")][0], m2=r[(4, "0.02")][0],
                     sem0=r[(4, "0.0")][1], sem2=r[(4, "0.02")][1]))

rows.sort(key=lambda d: d["k0"])
print(f"{len(rows)} designs. Test: 2% independent deposition error, 200 mirrors (the same"
      " mirrors for every design), rescue = top 4 layers. Pass rates in %.\n")
print(f"{'design':14s} {'T1064':>6s} {'T532':>6s} {'proxy':>6s} {'noise':>6s} spec  {'k0':>4s}  "
      f"{'k4 m0':>5s} {'k4 m1':>5s} {'k4 m2':>5s}   gain m0  gain m2")
for d in rows:
    print(f"{d['name']:14s} {d['T1']:6.2f} {d['T2']:6.2f} {d['proxy']:6.3f} {d['asd']:6.2f} "
          f"{'ok ' if d['spec'] else 'NO '}  {d['k0']*100:4.0f}  {d['m0']*100:5.0f} {d['m1']*100:5.0f} "
          f"{d['m2']*100:5.0f}   {(d['m0']-d['k0'])*100:+6.0f}  {(d['m2']-d['k0'])*100:+6.0f}")

ok = [d for d in rows if d["spec"]]
pop = [d for d in ok if d["name"].startswith("seed") and "_t2.5" not in d["name"]]
print(f"\nDesigns meeting the spec at zero error: {len(ok)} of {len(rows)}"
      f" ({len(pop)} from the population script, {len(ok)-len(pop)} originals).")
if len(pop) < 3:
    sys.exit()


def count(cond, label):
    n = sum(1 for d in pop if cond(d))
    print(f"  {label}: {n} of {len(pop)}")


print("\nPopulation designs only (originals excluded):")
sig = lambda d, a, b: (d[a] - d[b]) > 2 * np.hypot(d["se0"], d["sem0"])
count(lambda d: d["m0"] > d["k0"], "rescue raises pass rate, perfect measurement")
count(lambda d: sig(d, "m0", "k0"), "  ... by more than 2 standard errors")
count(lambda d: d["m1"] > d["k0"], "rescue raises pass rate, 1% measurement error")
count(lambda d: d["m2"] > d["k0"], "rescue raises pass rate, 2% measurement error")
count(lambda d: d["m2"] < d["k0"], "rescue LOWERS pass rate, 2% measurement error")
count(lambda d: d["m2"] < d["k0"] - 2 * np.hypot(d["se0"], d["sem2"]), "  ... by more than 2 standard errors")
count(lambda d: d["k0"] >= 0.95, "already >= 95% without rescue (rescue not needed at 2%)")

k0 = np.array([d["k0"] for d in pop]); px = np.array([d["proxy"] for d in pop])
loss = np.array([d["m0"] - d["m2"] for d in pop]); gain0 = np.array([d["m0"] - d["k0"] for d in pop])
gain2 = np.array([d["m2"] - d["k0"] for d in pop])
print("\nSpearman rank correlations (population designs):")
for a, b, lab in [(px, k0, "noise proxy vs sturdiness (k0 pass rate)"),
                  (k0, gain0, "sturdiness vs rescue gain at perfect measurement"),
                  (k0, gain2, "sturdiness vs rescue gain at 2% measurement error"),
                  (k0, loss, "sturdiness vs pass-rate loss from 0 to 2% measurement error")]:
    rho, p = spearmanr(a, b)
    print(f"  {lab}: rho = {rho:+.2f}, p = {p:.3f}")
print(f"\nMedian over population designs: k0 {np.median(k0)*100:.0f}%, k4 m0 "
      f"{np.median([d['m0'] for d in pop])*100:.0f}%, k4 m1 {np.median([d['m1'] for d in pop])*100:.0f}%, "
      f"k4 m2 {np.median([d['m2'] for d in pop])*100:.0f}%")
