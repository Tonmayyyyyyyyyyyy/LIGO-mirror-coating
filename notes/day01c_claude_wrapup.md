# Day 1, Claude's remaining items (13 Nov 2026, late)

## 1. Measurement-error levels: what the literature gives

No source gives one per-layer accuracy number for in-situ monitoring. What
we found, all read in full text:

| Source | Number | What it is |
| --- | --- | --- |
| Tikhonravov & Trubetskov, Appl. Opt. 51, 7319 (2012) | 1 nm + 1% (normal, per layer) | Error model they use for design studies; "close to those experimentally found" with quartz monitoring |
| Wilbrandt, Stenzel, Kaiser, Proc. SPIE 7101 (2008), Fraunhofer IOF | 0.9% (Ta2O5), 1.5% (SiO2) | Run-to-run thickness spread of single layers |
| same | ~2.6% | Optical vs quartz-crystal reading of the same film |
| Melzig et al., Surf. Coat. Technol. 476, 130197 (2024) | up to ~4 nm per layer | In-situ fitted vs designed thickness, 14-layer AR coating |
| Leybold note (photonics.com) | 1-5% | Time-based thickness control (no monitoring) |

Choice: deposition error 0.5-3% (plus an optional 1 nm absolute term);
measurement error 0, 0.25, 0.5, 1, 2% swept, since nothing pins it down.
Both Wilbrandt 2008 and Melzig 2024 say re-optimizing the remaining layers
is done in practice in general optics. That confirms the technique is
known; our claim stays limited to GW mirrors.

## 2. Novelty re-check

- Pierro et al. 2021 (full text): robustness is tested for absorption only
  (Sec. III.C, not IV.C). No thickness errors, no re-optimization. Our
  earlier note saying "+/-1 nm independent errors" was wrong; fixed.
- Poitras & Ma, Sci. Rep. 2025 (abstract via Sciety): simulated
  re-optimization after each layer for laser facet coatings. Closest
  method. No thermal noise, no GW mirrors. Must be cited as the nearest
  prior work.

## 3. Code clean-up

- `rescue.py`: one module with the model (reference design, deposition,
  measurement, rescue, pass/fail, noise proxy).
- Realism fix: the re-optimized top layers and the cap now get deposition
  errors too. Before, they were deposited perfectly.
- Fair comparison: every k and measurement level sees the same deposited
  mirrors (fixed random draws), so differences come from k, not luck.
- `tests/test_rescue.py`: 6 checks, including a single quarter-wave layer
  against the textbook formula. All pass.
- `scripts/run_sweep.py`: the sweep tool for days 4-5.
- `dichroic_rescue.py` removed (replaced by `rescue.py` + `run_sweep.py`).
  `rescue_prototype.py` kept: it is the only script for the single-wavelength
  quarter-wave result quoted in the proposal.

## 4. First result with the cleaned model (40 trials, 2% deposition error)

| k | meas 0% | meas 0.5% | meas 1% |
| --- | --- | --- | --- |
| 0 | 0.55 | 0.55 | 0.55 |
| 2 | 0.90 | 0.85 | 0.88 |
| 4 | 0.93 | 0.85 | 0.90 |

Standard error about 0.05 per cell. Read-off: with errors on the top
layers too, the gain is smaller than the first prototype showed, but still
large, and 1% measurement error costs little. 40 trials is too few to
separate k = 2 from k = 4. Days 4-5 use 200+.
