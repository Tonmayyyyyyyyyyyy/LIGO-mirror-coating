# Day 2, Claude's side (13 Nov 2026, night)

## 1. Hand check of measure() and rescue() - passes

`scripts/day2_hand_case.py`, rescue of the top 4 layers:

| Case | Before rescue | After rescue |
| --- | --- | --- |
| A: layer 30 is 5% too thick, perfect measurement | 4.80 ppm, 3.40% (passes) | 5.01 ppm, 3.20% |
| B: random 2% errors, failing | 5.12 ppm, 4.21% (fails) | 5.19 ppm, 3.25% (passes) |
| C: case B, measurement off by 1% | 5.12 ppm, 4.21% (fails) | 5.29 ppm, 3.02% (passes) |

- `measure()` with zero error returns the true stack exactly; at 1% the
  measured/true scatter is 0.84% over 35 layers (expect about 1%).
- The rescue pulls 532 nm back to near 3.2% in each case.
- The top layers change by up to about 10-12% to correct 2% errors deeper
  down. Small errors below need large changes on top.

## 2. Speed

- One transmission evaluation (both wavelengths): 0.07 ms.
- Differential evolution rescue: 0.1 s (k=2) to 3.9 s (k=8) per mirror.
  Full sweep would be about 4.5 hours on the 2 cores here.
- Switched the default to a local optimizer (L-BFGS-B, 3 starting points).
  Same pass/fail verdict as differential evolution on 50 of 50 test mirrors
  (25 at k=4, 25 at k=8), 12-20x faster. DE stays available
  (`--method de`) for spot checks.
- `run_sweep.py` now runs trials in parallel and gives every k and
  measurement level the same deposited mirrors.
- Full sweep (k 0-8, 4 deposition levels, 5 measurement levels, 200 trials):
  about 15 minutes.

## 3. Does the result depend on our choices in the rescue cost?

2% deposition error, 0.5% measurement error, 200 trials (+/- about 0.02):

| Rescue cost setting | k=0 | k=2 | k=4 | k=6 |
| --- | --- | --- | --- | --- |
| 532 target 3.2%, noise weight 0.05 (default) | 0.60 | 0.88 | 0.91 | 0.90 |
| 532 target 2.5%, noise weight 0.05 | 0.60 | 0.81 | 0.84 | 0.99 |
| 532 target 3.2%, noise weight 0.5 | 0.60 | 0.88 | 0.91 | 0.89 |
| 532 target 3.2%, noise weight 0 | 0.60 | 0.86 | 0.91 | 0.92 |

- **Noise weight: does not matter** for pass rates (0 to 0.5). Good news:
  noise and rescue do not fight. Noise change stays within +/-0.5%.
- **532 nm target: matters.** It changes pass rates by up to 9 points and
  changes which k looks best. So "the best k" is not yet a safe claim.
- Likely reason: the window is 1-4% and the design sits at 3.16%, near the
  top. Aiming at 3.2% leaves little margin above; aiming lower leaves more,
  but is harder to reach with few layers.

**Decision needed (Day 3):** what should the rescue aim for? Options:
1. The aLIGO goal, 3.2% (what we do now).
2. The middle of the window (2.5%, or 2% if measured in log terms).
3. Maximize the margin to the window edges for both wavelengths.
   This is the most defensible, but needs a small code change.
My suggestion: option 3, with option 1 reported as a check.

## 4. Early pattern (100 trials, 2% deposition error)

| k | 0 | 2 | 4 | 6 | 8 |
| --- | --- | --- | --- | --- | --- |
| meas 0% | 0.58 | 0.89 | 0.95 | 0.90 | 0.85 |
| meas 1% | 0.58 | 0.80 | 0.87 | 0.86 | 0.85 |

More layers re-optimized is not always better: each re-optimized layer is
deposited again with its own 2% error. If this holds in the full sweep,
there is a best k, which would be a clean result. But see section 3: the
best k depends on the rescue target, so decide that first.

## Still open from Day 1

- Package version (we use PyPI 1.0.2; fine so far).
- Keep the 532 nm requirement: yes, needed (single-wavelength mirrors do not
  need rescue).
- Ti:Ta2O5 loss angle 2e-4 vs 3.6e-4: affects noise numbers only, not pass
  rates. Report both.
