#!/bin/sh
# Why k = 4: fine scan of one design (robust_seed9_t2.5) with k = 0, 2, 4, 6,
# independent errors 1-3%, measurement error 0/1/2%, 400 mirrors per point.
# This is the command that made results/day5/fine_sturdy.csv (settings read back
# from that file). Bootstrap: python3 scripts/day7_bootstrap.py <csv>
set -e
python3 scripts/run_sweep.py --design designs/robust_seed9_t2.5.npy --trials 400 \
  --k 0 2 4 6 --dep 0.01 0.0125 0.015 0.0175 0.02 0.0225 0.025 0.0275 0.03 \
  --meas 0 0.01 0.02 --t2 0.025 --noise-weight 0.05 --jobs 2 --out "${1:-results/day5/fine_sturdy.csv}"
