#!/bin/sh
# Does the noise weight in the rescue cost change pass rates? One design
# (robust_seed9_t2.5), independent errors 2% and 3% (at 2% this design is near
# 100%, so 3% is where a difference could show), k = 4, measurement error 0 and 1%,
# 200 mirrors (the same mirrors as every other run), weights 0, 0.05, 0.5.
set -e
mkdir -p results/checks
for w in 0 0.05 0.5; do
  python3 scripts/run_sweep.py --design designs/robust_seed9_t2.5.npy --trials 200 \
    --k 4 --dep 0.02 0.03 --meas 0 0.01 --t2 0.025 --noise-weight $w --jobs 2 \
    --out results/checks/noise_weight_$w.csv
done
