#!/bin/sh
# Population fine scan (research question 1 on all designs): for each of the
# 32 designs that meet the spec, pass rate across deposition errors 0.25-3%
# in 0.25% steps, independent errors, 200 mirrors (same mirrors for every
# design), k = 0 and 4, measurement error 0 / 1 / 2%, aim 2.5%.
# Seed 21 is skipped: it fails the spec at zero error (6.35 ppm).
set -e
mkdir -p results/population_fine
DEPS="0.0025 0.005 0.0075 0.01 0.0125 0.015 0.0175 0.02 0.0225 0.025 0.0275 0.03"
run() {  # $1 = design file, $2 = tag
  test -f results/population_fine/sweep_$2.csv || \
  python3 scripts/run_sweep.py --design $1 --trials 200 --k 0 4 --dep $DEPS \
    --meas 0 0.01 0.02 --t2 0.025 --jobs 2 \
    --out results/population_fine/sweep_$2.csv > results/population_fine/log_$2.txt 2>&1
}
for s in $(seq 1 30); do
  [ $s -eq 21 ] && continue
  run designs/population/seed$s.npy seed$s
done
for d in lownoise_seed5_t2.5 seed2_t2.5 robust_seed9_t2.5; do run designs/$d.npy $d; done
echo done > results/population_fine/DONE
