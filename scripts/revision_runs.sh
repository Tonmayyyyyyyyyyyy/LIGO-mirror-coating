#!/bin/sh
# Additional checks of the main results (Nov 2026). All on the 32 designs,
# 200 mirrors per point, same mirrors as the main runs unless --seed 1 is given.
# Outputs under results/revision/. Steps with an existing output are skipped.
#   1. gated rule: rescue only mirrors predicted to fail (fine grid, meas 0, 1, 2%)
#   2. extra measurement levels 0.5% and 1.5% for the always-rescue rule (sigma_dep 0.25, 0.5, 1, 2%)
#   3. number of rescued layers k = 2, 4, 6, 8, 12 (independent 2%, shared 1%)
#   4. slow global optimizer (DE) for shared 1%
#   5. second master seed (seed 1) for the single-point runs
#   6. full Brownian noise for all designs at 2%
set -e
R=results/revision
mkdir -p $R/gated $R/meas_extra $R/k_indep $R/k_shared $R/de_shared $R/seed1_indep $R/seed1_shared
DEPS="0.0025 0.005 0.0075 0.01 0.0125 0.015 0.0175 0.02 0.0225 0.025 0.0275 0.03"
NAMES=""
for s in $(seq 1 30); do [ $s -ne 21 ] && NAMES="$NAMES population/seed$s"; done
NAMES="$NAMES lownoise_seed5_t2.5 seed2_t2.5 robust_seed9_t2.5"
run() { # outdir, extra args...
  d=$1; shift
  for n in $NAMES; do
    tag=$(basename $n)
    f=$R/$d/sweep_$tag.csv
    [ -f $f ] && continue
    python3 scripts/run_sweep.py --design designs/$n.npy --trials 200 --t2 0.025 --jobs 2 --out $f "$@" > $R/$d/log_$tag.txt 2>&1
    echo "$d $tag done"
  done
}
run gated      --gate --k 4 --dep $DEPS --meas 0 0.01 0.02
run k_indep    --k 2 4 6 8 12 --dep 0.02 --meas 0
run k_shared   --model common --k 2 4 6 8 12 --dep 0.01 --meas 0
run de_shared  --model common --method de --k 4 --dep 0.01 --meas 0
run meas_extra --k 4 --dep 0.0025 0.005 0.01 0.02 --meas 0.005 0.015
run seed1_indep  --seed 1 --k 0 4 --dep 0.0025 0.02 --meas 0 0.01 0.02
run seed1_shared --seed 1 --model common --k 0 4 --dep 0.01 0.02 --meas 0 0.01 0.02
[ -f $R/full_noise_population.txt ] || python3 scripts/full_noise_population.py > $R/full_noise_population.txt
touch $R/DONE
