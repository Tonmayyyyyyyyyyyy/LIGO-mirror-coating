# Day 3, Claude's side (14 Nov 2026, early)

Decision (Tonmay): the rescue aims at 2.5% at 532 nm (middle of the 1-4%
window). For a fair comparison, the starting design aims there too.

## Finding: lower-noise designs are more fragile

Same design cost, three random starts, plus the earlier designs. Robustness
= pass rate (aLIGO spec) with random independent errors, no rescue, 500 trials.

| Design | T1064 (ppm) | T532 | Noise proxy / quarter-wave | Pass @1% | T532 5-95% @1% | Pass @2% |
| --- | --- | --- | --- | --- | --- | --- |
| old (aim 3.2%, Day 1) | 4.92 | 3.16% | 0.949 | 0.94 | 2.70-4.06% | 0.66 |
| best seed, aim 3.2% (Day 3) | 5.26 | 3.25% | 0.908 | 0.66 | 2.04-6.72% | 0.53 |
| seed 5, aim 2.5% (low noise) | 5.31 | 2.47% | 0.915 | 0.90 | 1.64-4.46% | 0.66 |
| seed 2, aim 2.5% | 5.12 | 2.45% | 1.046 | 0.97 | 1.93-3.60% | 0.80 |
| seed 9, aim 2.5% (robust) | 5.05 | 2.50% | 1.040 | 1.00 | 2.16-3.13% | 0.91 |

Full Brownian ASD at 100 Hz: seed 5 = 6.19e-21; plain quarter-wave stack =
6.53e-21 m/rtHz (5% lower). Correction: earlier tonight I labelled 6.33e-21
as "QW start"; that was the old Day 1 design, not the plain quarter-wave stack.

The optimizer found designs about 9% quieter (proxy) than quarter-wave, but
they are much more sensitive to errors at 532 nm. Designs near quarter-wave
noise are very robust. Our design cost had no robustness term (Caltech's
has one, "Lsens"), so which design came out was partly luck of the start.

## What this does to the rescue result (seed 5 design, 2% errors, 200 trials)

| k | meas 0% | meas 0.5% | meas 1% |
| --- | --- | --- | --- |
| 0 | 0.68 | 0.68 | 0.68 |
| 2 | 0.67 | 0.67 | 0.62 |
| 4 | 0.69 | 0.67 | 0.58 |
| 6 | 0.76 | 0.73 | 0.62 |
| 8 | 0.83 | 0.81 | 0.69 |

Much smaller gains than on Day 2. Failure breakdown (perfect measurement):
without rescue, failures are at 532 nm (65 of 200); with rescue at k = 4,
they move to 1064 nm (61 of 200). Re-making the top layers with 2% errors
hurts 1064 nm.

Part of the earlier large gain came from a design sitting near the edge
of the window. The fair comparison is smaller.

## Proposed new framing (needs Tonmay's decision)

Rescue's real value may be this: it could let a manufacturer use the quieter
but fragile design (seed 5) and still reach the pass rate of the robust one
(seed 9). Question: does rescue let the 5%-quieter design reach the robust
design's pass rate, and at what error and measurement levels? That puts
noise at the centre of the result.

Files: `designs/` holds all candidates. `scripts/reference.npy` is still
seed 5 and is NOT frozen.
