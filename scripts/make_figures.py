"""Day 7: the paper figures, made only from saved results (no new simulations).

Writes paper/figures/fig1..fig4 as PDF (for LaTeX) and PNG (for checking).
Run from the repository root: python3 scripts/make_figures.py
"""
import csv
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path("paper/figures")
OUT.mkdir(parents=True, exist_ok=True)

# Colours: validated categorical palette (blue, orange, aqua, yellow).
# Two of them are below 3:1 contrast on white, so every series also gets
# a direct label and its own marker/line style.
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "lines.linewidth": 2, "legend.frameon": False,
    "savefig.dpi": 200, "savefig.bbox": "tight",
})


def load(path):
    """{(k, meas or None): sorted list of (dep, pass, stderr, trials)}"""
    d = defaultdict(list)
    for r in csv.DictReader(open(path)):
        k = int(r["k"])
        meas = None if k == 0 else float(r["meas"])
        d[(k, meas)].append((float(r["dep"]), float(r["pass_rate"]),
                             float(r["stderr"]), int(r["trials"])))
    return {key: sorted(v) for key, v in d.items()}


def curve(ax, rows, color, marker, ls, label, label_y_shift=0.0):
    x = np.array([r[0] for r in rows]) * 100
    y = np.array([r[1] for r in rows]) * 100
    e = np.array([r[2] for r in rows]) * 100
    ax.errorbar(x, y, yerr=e, color=color, marker=marker, ms=5, ls=ls,
                capsize=0, elinewidth=1)
    ax.annotate(label, (x[-1], y[-1] + label_y_shift), xytext=(6, 0),
                textcoords="offset points", va="center", color=INK, fontsize=8)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)


# ---- Figure 1: the main result (sturdy design, independent errors) ----
d = load("results/day5/fine_sturdy.csv")
fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.axhline(95, color=INK2, lw=1, ls=":")
ax.text(1.0, 95.6, "95% pass", color=INK2, fontsize=8)
curve(ax, d[(0, None)], BLUE, "o", "-", "no rescue")
curve(ax, d[(4, 0.0)], ORANGE, "s", "-", "rescue, perfect measurement", 1.5)
curve(ax, d[(4, 0.01)], AQUA, "^", "--", "rescue, 1% measurement error", -1)
curve(ax, d[(4, 0.02)], YELLOW, "D", ":", "rescue, 2% measurement error", 0)
ax.set_xlabel("Deposition error per layer (%, standard deviation)")
ax.set_ylabel("Mirrors that pass (%)")
ax.set_ylim(58, 101)
ax.set_title("Sturdy design: re-optimizing the top 4 layers", loc="left",
             fontsize=9, color=INK)
save(fig, "fig1_main_result")

# ---- Figure 2: tolerable error vs measurement error, three designs ----
LEVEL = 0.95


def crossing(dep, p):
    for i in range(1, len(dep)):
        if p[i] < LEVEL:
            if p[i - 1] < LEVEL:
                return np.nan if i == 1 else dep[i - 1]
            return dep[i - 1] + (p[i - 1] - LEVEL) / (p[i - 1] - p[i]) * (dep[i] - dep[i - 1])
    return np.inf


def tolerable(rows, rng, nboot=2000):
    dep = np.array([r[0] for r in rows]); p = np.array([r[1] for r in rows])
    n = np.array([r[3] for r in rows])
    c0 = crossing(dep, p)
    b = np.array([crossing(dep, rng.binomial(n, p) / n) for _ in range(nboot)])
    b = np.nan_to_num(b, nan=0.0, posinf=dep[-1])
    lo, hi = np.percentile(b, [2.5, 97.5])
    return c0, lo, hi, dep[0]


rng = np.random.default_rng(0)
designs = [("Quiet", "results/day7/fine_quiet.csv"),
           ("Middle", "results/day7/fine_seed2.csv"),
           ("Sturdy", "results/day5/fine_sturdy.csv")]
fig, axes = plt.subplots(1, 3, figsize=(6.4, 3.0), sharey=True)
xs = np.array([0, 1, 2])
table = []
for ax, (name, path) in zip(axes, designs):
    d = load(path)
    c0, lo0, hi0, start = tolerable(d[(0, None)], rng)
    ax.axhspan(lo0 * 100, hi0 * 100, color=BLUE, alpha=0.12, lw=0)
    ax.axhline(c0 * 100, color=BLUE, lw=1.5, ls="--")
    good = []
    for xi, m in zip(xs, (0.0, 0.01, 0.02)):
        c, lo, hi, start = tolerable(d[(4, m)], rng)
        table.append((name, m, c0, c, lo, hi))
        if np.isnan(c):   # already below 95% at the smallest error tested
            ax.annotate("", (xi, 0.05), (xi, 0.45),
                        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.8))
        else:
            ax.errorbar(xi, c * 100, yerr=[[(c - lo) * 100], [(hi - c) * 100]],
                        color=ORANGE, marker="s", ms=6, capsize=0, elinewidth=1.2)
            good.append((xi, c * 100))
    if len(good) > 1:
        ax.plot(*zip(*good), color=ORANGE, lw=1.5)
    ax.set_title(name + " design", fontsize=9, color=INK)
    ax.set_xticks(xs, ["0%", "1%", "2%"])
    ax.set_xlim(-0.5, 2.5)
axes[0].set_ylim(0, 3.0)
axes[0].set_ylabel("Largest error with 95% pass (%)")
axes[1].set_xlabel("Measurement error (standard deviation)")
handles = [plt.Line2D([], [], color=BLUE, ls="--", lw=1.5),
           plt.Line2D([], [], color=ORANGE, marker="s", lw=1.5),
           plt.Line2D([], [], color=ORANGE, marker=r"$\downarrow$", ls="none", ms=9)]
fig.legend(handles, ["no rescue (band: 95% range)", "rescue, top 4 layers",
                     "rescue: below 95% even at the smallest error tested"],
           loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2, fontsize=8)
save(fig, "fig2_three_designs")
with open(OUT / "fig2_values.txt", "w") as f:
    f.write("design, meas, no-rescue tolerable, rescue tolerable [95% range] (%)\n")
    f.write("'below' = under 95% at the smallest error tested (0.25% quiet, 1% others)\n")
    for name, m, c0, c, lo, hi in table:
        r = "below" if np.isnan(c) else f"{c*100:.2f} [{lo*100:.2f}-{hi*100:.2f}]"
        f.write(f"{name:7s} {m:.0%}  {c0*100:.2f}  {r}\n")

# ---- Figure 3: independent vs shared errors (sturdy design) ----
ind = load("results/day5/fine_sturdy.csv")
com = load("results/day6/common_sturdy.csv")
fig, ax = plt.subplots(figsize=(5.2, 3.4))
ax.axhline(95, color=INK2, lw=1, ls=":")
ax.text(3.2, 96, "95% pass", color=INK2, fontsize=8)
curve(ax, ind[(0, None)], BLUE, "o", "-", "independent, no rescue", -2)
curve(ax, ind[(4, 0.0)], ORANGE, "s", "-", "independent, rescue", 2)
curve(ax, com[(0, None)], BLUE, "o", "--", "shared, no rescue")
curve(ax, com[(4, 0.0)], ORANGE, "s", "--", "shared, rescue")
ax.set_xlabel("Deposition error (%, standard deviation)")
ax.set_ylabel("Mirrors that pass (%)")
ax.set_ylim(25, 102)
ax.set_xlim(0.9, 3.9)
ax.set_title("Sturdy design: each layer its own error (solid) vs. one shared error (dashed)",
             loc="left", fontsize=8, color=INK)
save(fig, "fig3_shared_error")

# ---- Figure 4: why mirrors fail ----
cases, block = [], None
for line in open("results/day7/failures.txt"):
    m = re.match(r"(\w+), (\w+) errors, (\d+)%", line)
    if m:
        block = f"{m.group(1)}, {m.group(2).replace('common', 'shared')}, {m.group(3)}%"
        continue
    m = re.match(r"\s+(no rescue|k=4, meas 0%)\s+pass\s+(\d+)\s+fails: (.*)", line)
    if m and block:
        c = {"pass": int(m.group(2))}
        for part in m.group(3).split(", "):
            mm = re.match(r"(.+) (\d+)$", part.strip())
            if mm:
                c[mm.group(1)] = int(mm.group(2))
        cases.append((block, "no rescue" if m.group(1) == "no rescue" else "rescue", c))

cats = [("532 high", "532 nm too high", AQUA),
        ("1064 high", "1064 nm too high", ORANGE),
        ("1064 high + 532 high", "both too high", YELLOW)]
fig, ax = plt.subplots(figsize=(5.6, 4.0))
labels, y = [], 0
ys = []
for block, tag, c in cases:
    left = 0
    for key, _, color in cats:
        v = c.get(key, 0) / 2          # 200 mirrors -> percent
        ax.barh(y, v, left=left, color=color, height=0.7,
                edgecolor="white", linewidth=1)
        left += v
    other = (200 - c["pass"] - sum(c.get(k, 0) for k, _, _ in cats)) / 2
    if other > 0:
        ax.barh(y, other, left=left, color="#b9b8b3", height=0.7, edgecolor="white", linewidth=1)
        left += other
    if left == 0:
        ax.text(0.5, y, "no failures", va="center", fontsize=7.5, color=INK2)
    labels.append(f"{block} — {tag}")
    ys.append(y)
    y += 1 if tag == "no rescue" else 1.6
ax.set_yticks(ys, labels, fontsize=7.5)
ax.invert_yaxis()
ax.set_xlabel("Mirrors that fail (%), by reason (200 mirrors per bar)")
ax.grid(axis="y", visible=False)
handles = [plt.Rectangle((0, 0), 1, 1, color=col) for _, _, col in cats]
handles.append(plt.Rectangle((0, 0), 1, 1, color="#b9b8b3"))
ax.legend(handles, [lab for _, lab, _ in cats] + ["too low"], loc="upper center",
          bbox_to_anchor=(0.45, -0.13), ncol=4, fontsize=8)
ax.set_title("Rescue fixes 532 nm failures; most of what is left fails at 1064 nm",
             loc="left", fontsize=9, color=INK)
save(fig, "fig4_failures")
print("figures written to", OUT)
