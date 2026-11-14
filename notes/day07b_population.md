# Population study: 30 script-made designs (14 Nov 2026, evening)

Why: the three Day 3 designs were single draws from an optimizer whose
exact run was not saved. Re-making them gave different designs and some
conclusions changed (`results/replication/`). So we tested the claims on a
population instead of three hand-picked files.

How: `scripts/population_study.sh`. `scripts/make_designs.py` with seeds
1-30 (deterministic; committed before the results). Same test for every
design and for the three originals: 2% independent deposition error, 200
mirrors (identical mirrors for all designs), k = 0 and k = 4, measurement
error 0 / 1 / 2%, rescue aims at 2.5%. Full table: `results/population/summary.txt`.

29 of 30 designs meet the spec at zero error (seed 21: 6.35 ppm, excluded
from counts, shown in the table).

## What holds across 29 designs

| Claim | Count |
| --- | --- |
| Rescue raises the pass rate, perfect measurement | 29 of 29 (25 beyond 2 s.e.) |
| Rescue raises the pass rate, 1% measurement error | 26 of 29 |
| Rescue raises the pass rate, 2% measurement error | 14 of 29 (11 lower it, 3 beyond 2 s.e.) |

Medians: no rescue 75%; rescue 92% (perfect), 89% (1%), 80% (2%).

Rank correlations (Spearman):
- Sturdiness (no-rescue pass rate) vs loss of pass rate from 0 to 2%
  measurement error: **rho = -0.88, p < 0.001**. Sturdier designs lose much
  less when measurement is poor. This is the Day 7 "ladder", now a strong
  general tendency instead of three points.
- Noise proxy vs sturdiness: rho = +0.65, p < 0.001. Quieter designs are
  more fragile (Day 3 finding, confirmed in general).
- Sturdiness vs rescue gain at perfect measurement: rho = -0.21, p = 0.27.
  With perfect measurement the rescue helps fragile and sturdy designs
  about equally.

## What the originals look like inside the population

- Original quiet design (lownoise_seed5): gain +2 at perfect measurement,
  the smallest of all 32 designs. Typical quiet designs (proxy about 0.91-
  0.93) gain +5 to +22. So "the quiet design cannot be rescued" was a fact
  about one unlucky design, not about quiet designs. Drop that claim.
- Original sturdy design (robust_seed9): among the sturdiest, with seeds 11,
  27, 2, 17; not an outlier.
- Original middle design (seed2_t2.5): mid-table.

## For the paper

Keep: rescue helps with good measurement (29/29); measurement error eats the
gain, and sturdier designs keep more of it (rho = -0.88); quieter designs
are more fragile (rho = +0.65); noise cost nil.
Change: present results on the population, with the three originals as
worked examples (the fine scans and figures), not as the evidence.
Remove: "a fragile design cannot be rescued" as a general statement.
