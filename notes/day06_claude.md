# Day 6, Claude's side (14 Nov 2026)

Three small checks done. The slow differential-evolution spot check is left
for the next session.

## 1. Shared-error model (one error for all layers)

Same setup as Day 4 (200 trials, aLIGO spec, rescue aims at 5 ppm / 2.5%),
but every layer, including the re-made top layers, gets the same relative
error. Data: `results/day6/common_*.csv`. Columns are k = 0, 2, 4, 6.

Sturdy design:

| meas \ dep | 1% | 2% | 3% |
| --- | --- | --- | --- |
| 0% | 0.73 0.88 0.92 0.92 | 0.42 0.52 0.56 0.57 | 0.31 0.39 0.42 0.45 |
| 1% | 0.73 0.86 0.89 0.88 | 0.42 0.52 0.56 0.57 | 0.31 0.37 0.41 0.44 |
| 2% | 0.73 0.85 0.87 0.89 | 0.42 0.50 0.52 0.52 | 0.31 0.38 0.39 0.40 |

Quiet design:

| meas \ dep | 1% | 2% | 3% |
| --- | --- | --- | --- |
| 0% | 0.61 0.62 0.58 0.67 | 0.39 0.43 0.33 0.46 | 0.33 0.42 0.26 0.43 |
| 1% | 0.61 0.57 0.56 0.58 | 0.39 0.42 0.34 0.42 | 0.33 0.37 0.29 0.44 |
| 2% | 0.61 0.55 0.47 0.46 | 0.39 0.37 0.37 0.38 | 0.33 0.35 0.34 0.36 |

What it says:
- A shared error is far more damaging than independent errors of the same
  size. Sturdy design at 1%: 100% pass (independent) vs 73% (shared).
  Independent errors partly cancel across 40 layers; a shared one shifts
  the whole spectrum.
- Rescue still helps the sturdy design (73% -> 92% at 1%, 42% -> 56% at 2%),
  but it cannot reach 95% at 1% error. Four top layers cannot undo a shift
  of the whole stack.
- Quiet design: rescue gives no clear gain, same as Day 4.
- Our rescue does not use the fact that the error is shared. A smarter rescue
  could estimate the bias from the measured layers and pre-correct the
  remaining ones. Not tested; worth one line in the discussion.

Why it matters: the Advanced LIGO paper (arXiv 1411.4547, Sec. 4.3) says "a
systematic error in the layer thicknesses" left the ETMs in spec at 1064 nm
but made the 532 nm transmission "larger than desired by an order of
magnitude". That is this shared-error case, in real mirrors. Good motivation
for the introduction. Tonmay: read Sec. 4.3 yourself before citing it.

## 2. Full-formula noise check

`scripts/day6_full_noise.py`, 40 mirrors, 2% independent errors, k = 4.
Rescue changes the full Hong et al. noise by -0.13% to -0.20% on average
(per mirror -0.85% to +0.55%). The fast stand-in said -0.23% to -0.34%.
Same sign, same size: the stand-in is fine, and the rescue costs no noise.

## 3. Noise-model assumptions

Advanced LIGO paper (arXiv 1411.4547, Tables 1 and 3): ETM beam radius
6.2 cm, matching ours. Its high-index loss is 2.3e-4 (we use 2e-4). It
gives no temperature; 295 K is room temperature. Added as `aLIGO2015` in
the .bib.

## Next session

- Slow differential-evolution spot check at k = 4.
