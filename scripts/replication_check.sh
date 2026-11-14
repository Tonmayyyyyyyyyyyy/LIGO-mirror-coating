#!/bin/sh
# Replication: rerun the main measurement-error test on the three designs made
# by scripts/make_designs.py (not the original Day 3 files).
# Same settings for all three: 200 mirrors, k = 0 and 4, independent errors,
# 1-3% deposition error in 0.5% steps, measurement error 0, 1, 2%, aim 2.5%.
set -e
for s in 5 2 9; do
  python3 scripts/run_sweep.py --design designs/remade_seed$s.npy --trials 200 \
    --k 0 4 --dep 0.01 0.015 0.02 0.025 0.03 --meas 0 0.01 0.02 --t2 0.025 \
    --jobs 2 --out results/replication/remade_seed$s.csv > results/replication/log_seed$s.txt 2>&1
  python3 scripts/day7_bootstrap.py results/replication/remade_seed$s.csv > results/replication/bootstrap_seed$s.txt
done
echo done > results/replication/DONE
