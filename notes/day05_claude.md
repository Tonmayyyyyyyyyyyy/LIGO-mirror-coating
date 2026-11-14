# Day 5, Claude's side (14 Nov 2026)

Fine sweep on the sturdy design (robust_seed9), 400 trials per cell
(standard error about 0.011 near 95%). Data: `results/day5/fine_sturdy.csv`.

## The main number: largest thickness error that still gives 95% pass rate

Linear interpolation between error steps of 0.25%.

| Rescue | Measurement error | Tolerable error (95% pass) |
| --- | --- | --- |
| none (k = 0) | - | 1.7% |
| top 2 layers | 0% | 2.5% |
| top 4 layers | 0% | 2.65% |
| top 6 layers | 0% | 2.5% |
| top 4 layers | 1% | 2.6% |
| top 4 layers | 2% | 2.4% |
| top 2 layers | 2% | 2.2% |

Plain words: re-optimizing the top 4 layers lets the sturdy design tolerate
about 2.6% thickness error instead of 1.7%, roughly 1.5 times larger. A
measurement error of 1% costs almost nothing; 2% costs a little. Four layers
is the best k; six is slightly worse (more remade layers, more new errors).

## Full table (pass rates)

| dep | k=0 | meas 0: k2 k4 k6 | meas 1%: k2 k4 k6 | meas 2%: k2 k4 k6 |
| --- | --- | --- | --- | --- |
| 1.00% | 1.000 | 1.000 1.000 1.000 | 1.000 1.000 1.000 | 1.000 1.000 0.998 |
| 1.25% | 1.000 | 1.000 1.000 1.000 | 1.000 1.000 1.000 | 0.998 0.995 0.995 |
| 1.50% | 0.985 | 1.000 1.000 0.995 | 1.000 1.000 0.995 | 0.993 0.998 0.988 |
| 1.75% | 0.940 | 0.995 0.998 0.993 | 0.990 0.995 0.993 | 0.980 0.990 0.985 |
| 2.00% | 0.917 | 0.973 0.998 0.993 | 0.968 0.993 0.985 | 0.970 0.970 0.963 |
| 2.25% | 0.860 | 0.965 0.993 0.983 | 0.965 0.988 0.973 | 0.943 0.958 0.950 |
| 2.50% | 0.790 | 0.953 0.965 0.945 | 0.940 0.960 0.945 | 0.897 0.945 0.938 |
| 2.75% | 0.740 | 0.882 0.940 0.925 | 0.877 0.938 0.935 | 0.807 0.882 0.887 |
| 3.00% | 0.605 | 0.850 0.910 0.907 | 0.843 0.907 0.902 | 0.807 0.875 0.880 |

Caveat: crossing points have an uncertainty of roughly +/-0.1 to 0.15% in
error size, from the trial count and the 0.25% step.

## Next (Day 6)

- Common-factor error model check.
- Slow-optimizer (differential evolution) spot check at k = 4.
- Full-formula noise for a sample of rescued mirrors.
