# Day 6, Claude's side (14 Nov 2026)

All Day 6 checks done (sections 1-5).

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

## 4. Size check against the real aLIGO mirrors (done 14 Nov, afternoon)

`scripts/day6_aligo_size.py`, output `results/day6/aligo_size.txt`. No
rescue, no randomness: one systematic error applied to the design, swept
from -10% to +10% in 0.25% steps.

Smallest systematic error that makes T(532) about 10x the design value:

| Error on | Sturdy | Quiet |
| --- | --- | --- |
| all layers | -2.25% (1064 nm out of spec, 7.98 ppm) | -1.00% (1064 nm just out, 6.24 ppm) |
| Ta2O5 only | -3.50% (1064 out, 6.75 ppm) | -2.25% (1064 out, 6.55 ppm) |
| SiO2 only | +6.00% (1064 in spec, 5.21 ppm) | -1.50% (1064 in spec, 5.85 ppm) |

532 nm leaves the 1-4% window already at about 0.5-1% systematic error
(all layers), 1-2.5% for one material only.

What it says:
- Size: a systematic error of 1-3% is enough for a 10x jump at 532 nm.
  That is a realistic size for a coating run, so the aLIGO report is
  consistent with our model in size, not just in kind.
- But in most cases 1064 nm also leaves our 4-6 ppm window. It stays in
  only when one material is off (silica in both designs; tantala in the
  quiet one only for a large +6.75%). So our model matches the aLIGO
  report fully only if the error was mostly in one material.
- We cannot go further: their real design is not ours, and the paper does
  not give the error size or which material.
- Paper wording: "In our model, a systematic error of 1-3% raises the
  532 nm transmission tenfold, the size of the problem reported for the
  Advanced LIGO end mirrors; keeping 1064 nm in spec at the same time
  requires the error to be mostly in one material." Plus: different design.

## 5. Slow optimizer (differential evolution) vs fast one (done 14 Nov)

`scripts/day6_de_check.py`, output `results/day6/de_check.txt`. Same
mirrors, only the rescue optimizer changes. k = 4, 100 mirrors per row,
both designs, both error models, 2% and 3% errors, 0 and 1% measurement.
1600 mirrors in total, 17 minutes.

- Sturdy design (our main result): 4 disagreements in 800 mirrors, 2 each
  way. The fast optimizer is fine.
- Quiet design, independent errors: 1 disagreement in 400.
- Quiet design, shared error: DE passes more: +8, +5, +5 in 100 at
  perfect / 1% measurement, one row -2. So for this one case our fast
  numbers are a few points pessimistic. The conclusion does not change:
  the quiet design stays far below 95% either way.
- Total: DE-only passes 22, fast-only passes 5, out of 1600.
- method.tex updated (the old "50 mirrors, same answer every time" line).

## Next session

Nothing left from Day 6. (Done: slow-optimizer check, section 5; size
check, section 4. Original plan text below for the record.)
- Size check against real aLIGO mirrors: for both designs, find how large
  a shared thickness error makes T(532 nm) about 10x the design value, and
  whether T(1064 nm) stays inside 4-6 ppm at that error. Also try an error
  on only one material (tantala only, silica only). If the error needed is
  small (about 1-2%), our model matches the aLIGO report in size, not just in
  kind. Paper wording either way: "reproduces the qualitative behaviour",
  not "validates".
