# How to reproduce the paper

This guide re-makes every number, table and figure in the paper from the code
in this repository. Everything is deterministic: with the versions below you
should get the same numbers as the ones committed here. Some files will still
differ in small ways that do not touch any result: figures carry a creation
timestamp, and a few logs (`de_check.txt`, the design-generation logs, the run
logs) record how long each step took.

## 1. What you need

- Linux or macOS, Python 3.13 (we used 3.13.18), about 1 GB of free disk.
- About 11 hours of computer time on a 2-core machine for the whole thing
  (5 hours for the main study, 6 hours for the additional checks in step 7b)
  (about 20 minutes more if you also regenerate the designs). Most steps can be run alone.
- For building the PDF: a LaTeX installation with `latexmk` (TeX Live 2023 used).

## 2. Set up

```
git clone https://github.com/Tonmayyyyyyyyyyyy/LIGO-mirror-coating
cd LIGO-mirror-coating
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python3 -m pytest -q tests          # 6 tests, all should pass
```

`requirements.txt` pins the exact versions we used: OptimalBragg 1.0.2,
NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, pytest 9.1.1. Other versions
of NumPy or SciPy can change the last digits of an optimizer result, and so
occasionally flip one mirror from pass to fail; the conclusions should not
change, but the numbers may no longer match exactly.

## 3. Run everything

```
sh scripts/reproduce_all.sh            # uses the committed designs
sh scripts/reproduce_all.sh designs    # also regenerates the 30 designs from their seeds
```

Steps whose output already exists are skipped. To force a full re-run, delete
the result folders first:

```
rm -r results/population_fine results/population results/population_shared results/stats/paired_*.csv \
      results/day5/fine_sturdy.csv results/checks results/day6/de_check.txt \
      results/day6/full_noise.txt results/day7/failures.txt
sh scripts/reproduce_all.sh
git status          # anything listed as modified differs from our results
```

## 4. What each step does

| Step | Command | Output | Time |
| --- | --- | --- | --- |
| Designs (seeds 1-30) | `python3 scripts/make_designs.py SEED designs/population/seedSEED.npy` | `designs/population/` | ~40 s each |
| Run A: fine scan, independent errors 0.25-3% | `sh scripts/population_fine.sh` | `results/population_fine/sweep_*.csv` | ~1.5 h |
| Run B: independent errors 2% | `sh scripts/population_study.sh` | `results/population/sweep_*.csv` | ~15 min |
| Run C: shared errors 1%, 2% | `sh scripts/population_shared.sh` | `results/population_shared/sweep_*.csv` | ~25 min |
| Paired per-mirror re-run | `python3 scripts/paired_outcomes.py` | `results/stats/paired_*.csv` | ~25 min |
| Choice of k (one design, k = 0, 2, 4, 6) | `sh scripts/check_k_choice.sh` | `results/day5/fine_sturdy.csv` | ~15 min |
| Bootstrap for the k test | `python3 scripts/day7_bootstrap.py results/day5/fine_sturdy.csv` | `results/day7/bootstrap_sturdy.txt` | seconds |
| Noise weight in the rescue cost | `sh scripts/check_noise_weight.sh` | `results/checks/noise_weight_*.csv` | ~5 min |
| Quarter-wave transmission vs layer count | `python3 scripts/smoke_qw_etm.py` | `results/checks/layer_count.txt` | seconds |
| Tantala loss angle | `python3 scripts/check_loss_angle.py` | `results/checks/loss_angle.txt` | seconds |
| Fast vs slow rescue optimizer | `python3 scripts/day6_de_check.py` | `results/day6/de_check.txt` | ~30 min |
| Full noise vs proxy | `python3 scripts/day6_full_noise.py` | `results/day6/full_noise.txt` | ~5 min |
| Why mirrors fail | `python3 scripts/day7_failures.py` | `results/day7/failures.txt` | ~5 min |
| Size of the aLIGO systematic error | `python3 scripts/day6_aligo_size.py` | `results/day6/aligo_size.txt` | seconds |
| Tolerable error per design | `python3 scripts/population_tolerable.py` | `results/population_fine/summary.txt` | seconds |
| Per-design summary at one error size | `python3 scripts/population_summary.py DIR SIGMA` | `results/population*/summary*.txt` | seconds |
| Quiet vs noisy designs | `python3 scripts/population_quiet_vs_noisy.py` | `results/population_fine/quiet_vs_noisy.txt` | seconds |
| Sign tests, McNemar, Holm, correlations | `python3 scripts/stats_checks.py` | `results/stats/stats_checks.txt` | seconds |
| Additional checks: gated rule, k = 2-12, global optimizer, measurement 0.5/1.5%, second seed, full noise | `sh scripts/revision_runs.sh` | `results/revision/*/sweep_*.csv`, `results/revision/full_noise_population.*` | ~6 h |
| Re-analysis of existing results (below coding, families, effect sizes, 90% threshold, proxy vs full noise) | `python3 scripts/revision_reanalysis.py` | `results/revision/reanalysis.txt` | ~1 min |
| Gated rule, k sweep, global optimizer | `python3 scripts/revision_gated_k.py` | `results/revision/gated_k.txt` | seconds |
| Measurement levels, second seed | `python3 scripts/revision_meas_seed.py` | `results/revision/meas_seed.txt` | seconds |
| Figures 1-4 | `python3 scripts/make_population_figures.py` | `paper/figures/`, every plotted number in `figure_values.txt` | seconds |
| Paper PDF | `cd paper && latexmk -pdf main.tex` | `paper/main.pdf` | seconds |

## 5. Where each number in the paper comes from

| In the paper | File |
| --- | --- |
| Pass test, layer thicknesses, material values | `rescue.py`, `tests/test_rescue.py` |
| Seed 21 fails (6.35 ppm); noise range of the 32 designs | `results/population/summary.txt` |
| Tolerable errors, medians, counts, ratio | `results/population_fine/summary.txt` |
| Pass rates at 2% independent and 1%/2% shared | `results/population/summary.txt`, `results/population_shared/summary_dep0.0*.txt` |
| Sign tests, saved/broken mirrors, McNemar, Holm, all correlations | `results/stats/stats_checks.txt` |
| Quiet vs noisy groups | `results/population_fine/quiet_vs_noisy.txt` |
| Families, effect sizes, without E1-E3, 90% threshold, below coding, proxy vs full noise | `results/revision/reanalysis.txt` |
| Gated rule, number of rescued layers, global optimizer on all designs | `results/revision/gated_k.txt` |
| Measurement errors 0.5% and 1.5%, second seed | `results/revision/meas_seed.txt` |
| Full noise change from rescue, all designs | `results/revision/full_noise_population.txt` |
| Figure values | `paper/figures/figure_values.txt` |
| Choice of k | `results/day7/bootstrap_sturdy.txt` |
| Noise weight check | `results/checks/noise_weight_*.csv` |
| Why 40 layers (2.2 / 4.4 / 8.9 ppm) | `results/checks/layer_count.txt` |
| Design transmissions 4.46-5.55 ppm | `results/population/summary.txt` |
| Loss-angle check (25-29%) | `results/checks/loss_angle.txt` |
| Optimizer check, full noise check, failures, aLIGO size | `results/day6/de_check.txt`, `full_noise.txt`, `results/day7/failures.txt`, `results/day6/aligo_size.txt` |

## 6. How the random numbers work

Mirror `i` at deposition error `sigma` always gets its errors from
`numpy.random.default_rng([0, round(sigma*1e5), i])`, and its measurement
errors from `default_rng([0, round(sigma*1e5), round(sigma_meas*1e5)+1, i])`
(`scripts/run_sweep.py`). The second-seed runs replace the leading 0 by 1
(`--seed 1`). So every design, rescue setting and measurement
level sees exactly the same mirrors, and any single mirror can be re-made on
its own with `rescue.trial()`.

## 7. Known limits of reproduction

- Three of the 32 designs (`designs/lownoise_seed5_t2.5.npy`,
  `designs/seed2_t2.5.npy`, `designs/robust_seed9_t2.5.npy`) came from an early
  exploratory run whose script was not kept. The files are committed and every
  result that uses them reproduces from them, but the files themselves cannot
  be regenerated. The other 29 regenerate from their seeds.
- Exact agreement of the numbers needs the pinned versions (Section 2).
  Figure files and timing lines in logs differ from run to run.
- Figure 4 (failure modes) and the four checks on E1 and E3 use their own random
  seeds, set in their scripts (`day7_failures.py`, `day6_*.py`), not the seeding
  scheme of the main runs.
