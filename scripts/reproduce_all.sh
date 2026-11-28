#!/bin/sh
# Re-make every number, table and figure in the paper from scratch.
# Run from the repository root:   sh scripts/reproduce_all.sh
# Optional first argument:        sh scripts/reproduce_all.sh designs
#   also regenerates the 30 script-made designs from their seeds (adds ~20 min).
#
# Steps that already have their output file are skipped. To redo a step,
# delete its output (see REPRODUCE.md). Times are for a 2-core machine.
set -e

echo "== 0. Tests (seconds)"
python3 -m pytest -q tests

if [ "$1" = "designs" ]; then
  echo "== 1. Regenerate the 30 designs from seeds 1-30 (~20 min)"
  mkdir -p designs/population results/population
  for s in $(seq 1 30); do
    python3 scripts/make_designs.py $s designs/population/seed$s.npy > results/population/gen_seed$s.txt 2>&1
  done
fi

echo "== 2. Run A: fine scan, independent errors 0.25-3% (~1.5 h)"
sh scripts/population_fine.sh
echo "== 3. Run B: independent errors 2% (~15 min)"
sh scripts/population_study.sh
echo "== 4. Run C: shared errors 1% and 2% (~25 min)"
sh scripts/population_shared.sh
echo "== 5. Paired per-mirror re-run for the McNemar test (~25 min)"
test -f results/stats/paired_common_0.01.csv || python3 scripts/paired_outcomes.py > results/stats/paired_log.txt

echo "== 6. Method checks (~1 h in total)"
mkdir -p results/checks results/day5 results/day6 results/day7
test -f results/day5/fine_sturdy.csv || sh scripts/check_k_choice.sh results/day5/fine_sturdy.csv
python3 scripts/day7_bootstrap.py results/day5/fine_sturdy.csv > results/day7/bootstrap_sturdy.txt
test -f results/checks/noise_weight_0.5.csv || sh scripts/check_noise_weight.sh
python3 scripts/check_loss_angle.py > results/checks/loss_angle.txt
python3 scripts/smoke_qw_etm.py > results/checks/layer_count.txt 2>/dev/null
test -f results/day6/de_check.txt   || python3 scripts/day6_de_check.py   > results/day6/de_check.txt
test -f results/day6/full_noise.txt || python3 scripts/day6_full_noise.py > results/day6/full_noise.txt
test -f results/day7/failures.txt   || python3 scripts/day7_failures.py   > results/day7/failures.txt
python3 scripts/day6_aligo_size.py > results/day6/aligo_size.txt

echo "== 7. Analysis (seconds)"
python3 scripts/population_tolerable.py > results/population_fine/summary.txt
python3 scripts/population_summary.py results/population 0.02 > results/population/summary.txt
python3 scripts/population_summary.py results/population_shared 0.01 > results/population_shared/summary_dep0.01.txt
python3 scripts/population_summary.py results/population_shared 0.02 > results/population_shared/summary_dep0.02.txt
python3 scripts/population_quiet_vs_noisy.py > results/population_fine/quiet_vs_noisy.txt
python3 scripts/stats_checks.py > results/stats/stats_checks.txt

echo "== 7b. Additional checks (about 6 hours): gated rule, k sweep, global optimizer, extra measurement levels, second seed, full noise"
sh scripts/revision_runs.sh
python3 scripts/revision_reanalysis.py > results/revision/reanalysis.txt
python3 scripts/revision_gated_k.py > results/revision/gated_k.txt
python3 scripts/revision_meas_seed.py > results/revision/meas_seed.txt

echo "== 8. Figures (seconds)"
python3 scripts/make_population_figures.py

echo "== 9. Paper"
cd paper && latexmk -pdf -interaction=nonstopmode -quiet main.tex && cd ..

echo "Done. 'git status' / 'git diff results/' shows anything that differs from the published results."
