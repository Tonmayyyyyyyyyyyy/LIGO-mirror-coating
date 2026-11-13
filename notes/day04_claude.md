# Day 4, Claude's side (14 Nov 2026)

Full sweep, both locked designs, 200 trials per cell, independent errors,
aLIGO spec, rescue aims at 5 ppm / 2.5%. Data: `results/day4/`.
Standard error per cell: up to about 0.035.

Pass rates. Columns are k = 0, 2, 4, 6, 8 (k = 0 is no rescue).

## Sturdy design (robust_seed9, 6.68e-21 m/rtHz)

| meas \ dep | 0.5% | 1% | 2% | 3% |
| --- | --- | --- | --- | --- |
| 0% | 1.00 all | 1.00 all | 0.92 0.96 0.99 0.99 0.98 | 0.55 0.82 0.88 0.88 0.85 |
| 0.5% | 1.00 all | 1.00 all | 0.92 0.96 0.99 0.99 0.97 | 0.55 0.82 0.85 0.86 0.84 |
| 1% | 1.00 all | 1.00 all | 0.92 0.95 0.99 0.99 0.97 | 0.55 0.81 0.88 0.88 0.85 |
| 2% | 1.00 all | 1.00 all (0.99 at k=8) | 0.92 0.96 0.96 0.95 0.94 | 0.55 0.79 0.87 0.87 0.88 |

## Quiet design (lownoise_seed5, 6.19e-21 m/rtHz)

| meas \ dep | 0.5% | 1% | 2% | 3% |
| --- | --- | --- | --- | --- |
| 0% | 1.00 all | 0.93 0.94 0.92 0.97 0.99 | 0.68 0.67 0.69 0.76 0.83 | 0.46 0.48 0.51 0.56 0.64 |
| 0.5% | 1.00 0.99 0.98 0.99 0.99 | 0.93 0.91 0.88 0.95 0.98 | 0.68 0.67 0.67 0.73 0.81 | 0.46 0.46 0.48 0.55 0.62 |
| 1% | 1.00 0.94 0.80 0.83 0.85 | 0.93 0.86 0.76 0.80 0.84 | 0.68 0.62 0.58 0.62 0.69 | 0.46 0.43 0.41 0.48 0.54 |
| 2% | 1.00 0.80 0.56 0.63 0.73 | 0.93 0.69 0.51 0.54 0.65 | 0.68 0.49 0.48 0.46 0.48 | 0.46 0.41 0.38 0.39 0.42 |

Noise change from rescue: -0.3 to -0.4% (proxy), both designs. Negligible.

## What it says (preliminary; checks on Day 6)

1. **Sturdy design: rescue works and is robust to measurement error.**
   At 3% deposition error, 55% -> 88% with 4 top layers. At 2%,
   92% -> 99%. Even 2% measurement error barely changes this.
   95% pass rate: without rescue, between 1% and 2% deposition error;
   with k = 4, at least 2%. Finer error steps needed to pin the numbers.
2. **Quiet design: rescue does not close the gap.** Best case (perfect
   measurement) at 2% error: 68% -> 83% (k = 8). The sturdy design
   without rescue is already at 92%.
3. **Quiet design + noisy measurement: rescue makes it worse.** At 0.5%
   deposition error and 1% measurement error, 100% -> 80% (k = 4). A
   fragile design turns measurement error into wrong corrections.
4. **Best k is about 4 for the sturdy design**; more layers do not help.

Answer to the Day 3 question: no, rescue does not let the quieter design
reach the sturdy one's pass rate. Rescue is useful as an add-on to a sturdy
design, where it raises the tolerable deposition error.

## Next (Day 5-6)

- Finer deposition steps (1.25, 1.5, 1.75, 2.25, 2.5%) on the sturdy
  design, to pin the 95% tolerable error with and without rescue.
- Common-factor error model check.
- Spot checks with the slow optimizer (differential evolution).
