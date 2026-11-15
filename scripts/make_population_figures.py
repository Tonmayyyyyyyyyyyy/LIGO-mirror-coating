"""Paper figures for the 32-design population, made only from saved results.

Run from the repository root: python3 scripts/make_population_figures.py
Writes paper/figures/fig1..fig4 (PDF for LaTeX, PNG for checking) and
paper/figures/figure_values.txt (every number drawn, for checking).

Inputs:
  results/population_fine/sweep_*.csv    independent errors, 0.25-3%, k = 0 and 4
  results/population_shared/sweep_*.csv  shared error, 1% and 2%
  results/population/sweep_*.csv         independent error, 2%
  results/day7/failures.txt              failure reasons, one design (worked example)
The sample is the 32 designs that meet the spec at zero error (seed 21 does not
and has no fine-scan file; it is left out of the shared/independent panels too).
"""
import csv
import glob
import os
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "lines.linewidth": 2, "legend.frameon": False,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})
LEVEL = 0.95
CURVES = [("k0", "no rescue", BLUE, "o", "-"),
          ("m0", "rescue, perfect measurement", ORANGE, "s", "-"),
          ("m1", "rescue, 1% measurement error", AQUA, "^", "--"),
          ("m2", "rescue, 2% measurement error", YELLOW, "D", ":")]
values = open(OUT / "figure_values.txt", "w")


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)


def read(path):
    """{curve key: {dep: pass_rate}}"""
    d = defaultdict(dict)
    for r in csv.DictReader(open(path)):
        key = "k0" if r["k"] == "0" else f"m{int(round(float(r['meas']) * 100))}"
        d[key][round(float(r["dep"]), 6)] = float(r["pass_rate"])
    return d


def crossing(dep, p):
    """Same rule as scripts/population_tolerable.py."""
    for i in range(1, len(dep)):
        if p[i] < LEVEL:
            if p[i - 1] < LEVEL:
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - LEVEL) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf


fine = {os.path.basename(f)[6:-4]: read(f)
        for f in sorted(glob.glob("results/population_fine/sweep_*.csv"))}
names = sorted(fine)
assert len(names) == 32, len(names)
deps = sorted(fine[names[0]]["k0"])

# ---- Figure 1: the typical design (median over 32) ----
fig, ax = plt.subplots(figsize=(5.4, 3.5))
ax.axhline(95, color=INK2, lw=1, ls=":")
ax.text(0.3, 96.2, "95% pass", color=INK2, fontsize=8)
values.write("Figure 1: median [25th-75th percentile] pass rate (%) over 32 designs\n")
x = np.array(deps) * 100
label_pos = {"k0": -3, "m0": 3, "m1": 0, "m2": -1}
for key, lab, col, mk, ls in CURVES:
    P = np.array([[fine[n][key][d] for d in deps] for n in names]) * 100
    med = np.median(P, axis=0); q1, q3 = np.percentile(P, [25, 75], axis=0)
    if key in ("k0", "m0"):
        ax.fill_between(x, q1, q3, color=col, alpha=0.13, lw=0)
    ax.plot(x, med, color=col, marker=mk, ms=4, ls=ls)
    ax.annotate(lab, (x[-1], med[-1] + label_pos[key]), xytext=(6, 0),
                textcoords="offset points", va="center", fontsize=8, color=INK)
    values.write(f"  {lab}: " + ", ".join(f"{d*100:.2f}%: {m:.1f} [{a:.1f}-{b:.1f}]"
                                         for d, m, a, b in zip(deps, med, q1, q3)) + "\n")
ax.set_xlabel("Deposition error per layer (%, standard deviation)")
ax.set_ylabel("Mirrors that pass (%)")
ax.set_ylim(40, 101)
ax.set_xlim(0, 3.1)
ax.set_title("The typical design (median of 32; bands: middle half of designs)",
             loc="left", fontsize=9, color=INK)
save(fig, "fig1_typical_design")

# ---- Figure 2: every design, rescued vs not rescued ----
tol = {n: {k: crossing(np.array(deps), np.array([fine[n][k][d] for d in deps]))
           for k in ("k0", "m0", "m1", "m2")} for n in names}
fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.8), sharex=True, sharey=True)
values.write("\nFigure 2: tolerable error (%) per design: no rescue -> rescue "
             "('below' = under 95% at 0.25%, drawn at 0)\n")
for ax, (key, lab, col, mk, _) in zip(axes, CURVES[1:]):
    ax.plot([0, 3], [0, 3], color=INK2, lw=1, ls="--")
    xs = np.array([tol[n]["k0"] for n in names]) * 100
    ys = np.array([tol[n][key] for n in names]) * 100
    below = np.isnan(ys)
    above = np.sum(ys[~below] > xs[~below])
    ax.scatter(xs[~below], ys[~below], s=22, color=col, marker=mk,
               edgecolor="white", linewidth=0.6, zorder=3)
    ax.scatter(xs[below], np.zeros(below.sum()) + 0.06, s=26, color=col,
               marker="v", edgecolor="white", linewidth=0.6, zorder=3)
    ax.set_title(lab.replace("rescue, ", "Rescue, "), fontsize=8.5, color=INK, loc="left")
    ax.text(0.05, 0.93, f"helped: {above} of 32", fontsize=8, color=INK, transform=ax.transAxes)
    if below.any():
        ax.text(1.0, 0.18, f"{below.sum()} below (▼)", fontsize=7.5, color=INK2)
    ax.text(2.0, 1.75, "no change", fontsize=7, color=INK2, rotation=38)
    values.write(f"  {lab}: helped {above}/32, below {below.sum()}/32\n")
axes[0].set_xlim(0.6, 2.2); axes[0].set_ylim(0, 3.0)
axes[0].set_ylabel("With rescue (%)")
axes[1].set_xlabel("Largest error with 95% pass, no rescue (%)")
fig.suptitle("Each dot is one design. Above the dashed line, the rescue helped.",
             x=0.07, ha="left", fontsize=9, color=INK, y=1.03)
save(fig, "fig2_every_design")
for n in sorted(names, key=lambda n: tol[n]["k0"]):
    values.write(f"    {n:20s} " + "  ".join(
        "below" if np.isnan(tol[n][k]) else f"{tol[n][k]*100:.2f}" for k in ("k0", "m0", "m1", "m2")) + "\n")

# ---- Figure 3: independent vs shared errors, pass rates of all 32 ----
def at(path_glob, dep):
    out = {}
    for f in glob.glob(path_glob):
        n = os.path.basename(f)[6:-4]
        if n in names:
            d = read(f)
            out[n] = (d["k0"][dep], d["m0"][dep])
    assert len(out) == 32, (path_glob, len(out))
    return out

cases = [("Independent errors, 2%", at("results/population/sweep_*.csv", 0.02)),
         ("Shared error, 1%", at("results/population_shared/sweep_*.csv", 0.01)),
         ("Shared error, 2%", at("results/population_shared/sweep_*.csv", 0.02))]
fig, axes = plt.subplots(1, 3, figsize=(6.6, 3.0), sharey=True)
values.write("\nFigure 3: pass rate (%) no rescue -> rescue (top 4, perfect measurement), 32 designs\n")
for ax, (title, d) in zip(axes, cases):
    a = np.array([v[0] for v in d.values()]) * 100
    b = np.array([v[1] for v in d.values()]) * 100
    ax.axhline(95, color=INK2, lw=1, ls=":")
    for y0, y1 in zip(a, b):
        ax.plot([0, 1], [y0, y1], color="#b9b8b3", lw=0.8, zorder=1)
    ax.scatter(np.zeros_like(a), a, s=14, color=BLUE, zorder=2)
    ax.scatter(np.ones_like(b), b, s=14, color=ORANGE, marker="s", zorder=2)
    ma, mb = np.median(a), np.median(b)
    ax.plot([0, 1], [ma, mb], color=INK, lw=2.2, zorder=3)
    ax.text(1.08, mb, f"median\n{ma:.0f}% → {mb:.0f}%", va="center", fontsize=7.5, color=INK)
    ax.set_xticks([0, 1], ["no\nrescue", "rescue"])
    ax.set_xlim(-0.3, 1.9)
    ax.set_title(title, fontsize=8.5, color=INK, loc="left")
    ax.grid(axis="x", visible=False)
    values.write(f"  {title}: median {ma:.1f} -> {mb:.1f}; max after rescue {b.max():.1f}; "
                 f"reach 95%: {np.sum(b >= 95)} of 32\n")
axes[0].set_ylabel("Mirrors that pass (%)")
axes[0].set_ylim(0, 102)
axes[2].text(1.95, 95, "95%", fontsize=7.5, color=INK2, va="center")
save(fig, "fig3_shared_error")

# ---- Figure 4: why mirrors fail (one design, worked example) ----
cases, block = [], None
for line in open("results/day7/failures.txt"):
    m = re.match(r"(\w+), (\w+) errors, (\d+)%", line)
    if m:
        block = f"{m.group(2).replace('common', 'shared')}, {m.group(3)}%"
        design = m.group(1)
        continue
    m = re.match(r"\s+(no rescue|k=4, meas 0%)\s+pass\s+(\d+)\s+fails: (.*)", line)
    if m and block and design == "sturdy":
        c = {"pass": int(m.group(2))}
        for part in m.group(3).split(", "):
            mm = re.match(r"(.+) (\d+)$", part.strip())
            if mm:
                c[mm.group(1)] = int(mm.group(2))
        cases.append((block, "no rescue" if m.group(1) == "no rescue" else "rescue", c))
cats = [("532 high", "532 nm too high", AQUA), ("1064 high", "1064 nm too high", ORANGE),
        ("1064 high + 532 high", "both too high", YELLOW)]
fig, ax = plt.subplots(figsize=(5.4, 3.0))
labels, ys, y = [], [], 0
values.write("\nFigure 4 (design robust_seed9_t2.5, 200 mirrors per bar): fail % by reason\n")
for block, tag, c in cases:
    left = 0
    parts = []
    for key, _, col in cats:
        v = c.get(key, 0) / 2
        ax.barh(y, v, left=left, color=col, height=0.7, edgecolor="white", linewidth=1)
        left += v; parts.append(f"{key} {v:.1f}")
    other = (200 - c["pass"] - sum(c.get(k, 0) for k, _, _ in cats)) / 2
    if other > 0:
        ax.barh(y, other, left=left, color="#b9b8b3", height=0.7, edgecolor="white", linewidth=1)
        left += other
    if left == 0:
        ax.text(0.5, y, "no failures", va="center", fontsize=7.5, color=INK2)
    labels.append(f"{block}, {tag}"); ys.append(y)
    values.write(f"  {block}, {tag}: " + ", ".join(parts) + f", other {other:.1f}\n")
    y += 1 if tag == "no rescue" else 1.6
ax.set_yticks(ys, labels, fontsize=7.5)
ax.invert_yaxis()
ax.set_xlabel("Mirrors that fail (%), by reason")
ax.grid(axis="y", visible=False)
h = [plt.Rectangle((0, 0), 1, 1, color=col) for _, _, col in cats]
ax.legend(h, [l for _, l, _ in cats], loc="upper center",
          bbox_to_anchor=(0.4, -0.2), ncol=3, fontsize=7.5)
ax.set_title("One design, worked example: rescue fixes 532 nm failures; 1064 nm limits it",
             loc="left", fontsize=8.5, color=INK)
save(fig, "fig4_failures")
values.close()
print("figures written to", OUT)
