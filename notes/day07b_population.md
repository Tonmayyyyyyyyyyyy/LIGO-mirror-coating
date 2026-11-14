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

## Update (15 Nov): all 32 designs as one sample

The three originals are now ordinary members of the sample (Tonmay's
decision). Recomputed on all 32 designs that meet the spec
(`results/population/summary.txt`):

- rescue raises pass rate, perfect measurement: 32 of 32 (27 beyond 2 s.e.)
- 1% measurement error: 28 of 32; 2%: 15 gain, 13 lose (4 beyond 2 s.e.)
- sturdiness vs loss from 0 to 2% measurement error: rho = -0.87, p < 0.001
- noise proxy vs sturdiness: rho = +0.66, p < 0.001
- sturdiness vs gain at perfect measurement: rho = -0.16, p = 0.38
- medians: no rescue 76%; rescue 92% / 89% / 78% at 0 / 1 / 2% measurement

These numbers replace the 29-design ones above.

## Shared-error population test (15 Nov)

`scripts/population_shared.sh`: all 33 designs, one error shared by all
layers, 1% and 2%, 200 mirrors (same for every design), k = 0 and 4,
measurement 0 / 1 / 2%. Summaries: `results/population_shared/summary_dep0.01.txt`
and `summary_dep0.02.txt`. Sample: the 32 designs that meet the spec.

| | 1% shared error | 2% shared error |
| --- | --- | --- |
| Median pass, no rescue | 66% | 40% |
| Median pass, rescue (meas 0 / 1 / 2%) | 76 / 74 / 69% | 48 / 46 / 42% |
| Rescue raises pass rate, perfect measurement | 31 of 32 (18 beyond 2 s.e.) | 29 of 32 (14 beyond 2 s.e.) |
| Best design after rescue | 92% (original sturdy) | 56% (original sturdy) |
| Designs reaching 95% | 0 | 0 |

- The Day 6 conclusion holds across the population: a shared error is much
  harsher, rescue helps a little (median +10 points at 1%), and no design
  reaches 95%.
- The Day 6 numbers (73 -> 92% at 1%, 42 -> 56% at 2%) are reproduced
  exactly for the original sturdy design, but that design turns out to be
  the best of all 32 under shared error. So those were the best case, not
  the typical case. Report the medians.
- At 1% shared error, sturdier designs again lose less from measurement
  error (rho = -0.88). At 2% everything fails so often that the pattern
  is not clear (rho = -0.29, p = 0.10).

## Research question 1 on all 32 designs (fine scan, 15 Nov 2026)

`scripts/population_fine.sh`, `scripts/population_tolerable.py`, output
`results/population_fine/summary.txt`. Independent errors, 0.25-3% in
0.25% steps, 200 mirrors per point (same mirrors for every design), rescue
= top 4 layers. Tolerable error = largest error with 95% pass; "below" =
under 95% already at 0.25% (counted as 0).

| Curve | Median tolerable error | Middle half of designs |
| --- | --- | --- |
| no rescue | 1.14% | 0.96-1.48% |
| rescue, perfect measurement | 1.71% | 1.52-2.19% |
| rescue, 1% measurement error | 1.58% | 0.91-1.96% |
| rescue, 2% measurement error | 0 (below) | 0-1.43% |

- Perfect measurement: rescue raises tolerable error in 30 of 32 (27 with
  no overlap of 95% ranges). Median ratio 1.43 (range 0.68-2.04).
- 1% measurement: raises it in 25 of 32 (14 clearly), lowers in 7 (3 clearly).
- 2% measurement: lowers it in 25 of 32 (18 clearly). 18 designs are
  "below": rescue with 2% measurement error fails even tiny-error mirrors.
- Sturdier designs lose less from measurement error (rho = -0.52, p = 0.002).
  Sturdiness vs gain at perfect measurement: rho = +0.30, p = 0.09 (weak).
- Noise change from rescue: median -0.02% (range -0.43 to +0.19%). Negligible.
- Original sturdy design here: 1.79% -> 2.54% (200 mirrors); Day 5 with 400
  mirrors gave 1.69% -> 2.65%. Ranges overlap. It is the 3rd sturdiest of 32,
  so the Day 5 headline is near the top, not typical. Typical is 1.14 -> 1.71%.

Why 2% measurement error is so harmful at small errors: in rescue.py the
rescue runs on every mirror, even ones that were already fine. With 2%
measurement error, the optimizer "fixes" errors that are mostly measurement
noise and breaks good mirrors. A real process would probably only re-optimize
when the measured mirror is out of spec. We did not test that; it belongs in
Limitations (it changes how question 2 should be read).
