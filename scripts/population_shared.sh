#!/bin/sh
# Population study, shared-error version: every design in designs/population
# (seeds 1-30) and the three originals get the same test with ONE error shared
# by all layers: 1% and 2% deposition error, 200 mirrors (same mirrors for
# every design), k = 0 and 4, measurement error 0 / 1 / 2%, aim 2.5%.
set -e
mkdir -p results/population_shared
for s in $(seq 1 30); do
  test -f results/population_shared/sweep_seed$s.csv || \
  python3 scripts/run_sweep.py --design designs/population/seed$s.npy --model common \
    --trials 200 --k 0 4 --dep 0.01 0.02 --meas 0 0.01 0.02 --t2 0.025 --jobs 2 \
    --out results/population_shared/sweep_seed$s.csv > results/population_shared/log_seed$s.txt 2>&1
done
for d in lownoise_seed5_t2.5 seed2_t2.5 robust_seed9_t2.5; do
  test -f results/population_shared/sweep_$d.csv || \
  python3 scripts/run_sweep.py --design designs/$d.npy --model common \
    --trials 200 --k 0 4 --dep 0.01 0.02 --meas 0 0.01 0.02 --t2 0.025 --jobs 2 \
    --out results/population_shared/sweep_$d.csv > results/population_shared/log_$d.txt 2>&1
done
echo done > results/population_shared/DONE
