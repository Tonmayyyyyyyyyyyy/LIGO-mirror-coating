#!/bin/sh
# Population study: 30 designs from scripts/make_designs.py (seeds 1-30),
# plus the three original designs, all given the same test:
# 2% independent deposition error, 200 mirrors, k = 0 and 4,
# measurement error 0 / 1 / 2%, rescue aims at 2.5% at 532 nm.
# Usage: sh scripts/population_study.sh [N_SEEDS]   (default 30)
set -e
N=${1:-30}
mkdir -p designs/population results/population
# 1. designs, two at a time
seq 1 $N | xargs -P 2 -I{} sh -c \
  'test -f designs/population/seed{}.npy || python3 scripts/make_designs.py {} designs/population/seed{}.npy > results/population/gen_seed{}.txt 2>&1'
# 2. the test, same settings for everyone
for s in $(seq 1 $N); do
  test -f results/population/sweep_seed$s.csv || \
  python3 scripts/run_sweep.py --design designs/population/seed$s.npy --trials 200 \
    --k 0 4 --dep 0.02 --meas 0 0.01 0.02 --t2 0.025 --jobs 2 \
    --out results/population/sweep_seed$s.csv > results/population/log_seed$s.txt 2>&1
done
for d in lownoise_seed5_t2.5 seed2_t2.5 robust_seed9_t2.5; do
  test -f results/population/sweep_$d.csv || \
  python3 scripts/run_sweep.py --design designs/$d.npy --trials 200 \
    --k 0 4 --dep 0.02 --meas 0 0.01 0.02 --t2 0.025 --jobs 2 \
    --out results/population/sweep_$d.csv > results/population/log_$d.txt 2>&1
done
# 3. summary
python3 scripts/population_summary.py > results/population/summary.txt 2>&1
echo done > results/population/DONE
