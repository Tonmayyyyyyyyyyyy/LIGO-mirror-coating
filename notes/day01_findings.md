# Day 1 findings (Claude's side)

Date: 2026-11-13. Covers: what the OptimalBragg code really does, a first
smoke test, where the noise formulas live, and a fresh overlap check.

## 1. The most important finding: the existing Monte Carlo uses *correlated* errors

Our proposal said the Caltech work tests "independent 0.5% errors". The code
says otherwise.

- **Paper text** (arXiv 2110.13437, Sec. 2.4): errors are "i.i.d." with
  standard deviation 0.5%. But the footnote to its Table 1 says "all layers
  are expected to have identical *fractional* uncertainties in physical
  thickness". So the paper itself is ambiguous.
- **PyPI code** (OptimalBragg 1.0.2, `analysis.py`, `mc_sens`): one random
  factor multiplies *every* layer thickness at once (`stack["Ls"] * perturb[1]`).
  That is a fully correlated error: the whole stack gets thicker or thinner
  together. The comment says 0.5% standard deviation, but the covariance it
  builds (`diag(0.01)` squared) gives 1%.
- **Current GitHub code** (CaltechExperimentalGravity/OptimalBragg, last commit
  2026-05-11, `mc.py`): same model, one common thickness factor, 0.5%.

What this means for us: the correlated case is already what the field's tool
does. Independent per-layer errors are **not** implemented anywhere we found.
So the gap flips: independent errors (and the comparison of the two models)
become our clearer contribution. The proposal doc gets corrected for this.

## 2. Closely related work in progress at Caltech (unpublished)

The GitHub repo has planning documents that touch our territory:

- `projects/aLIGO/README.md`: a "green finesse sweep" that varies the number
  of bilayers (ETM 18 to 24) and keeps Brownian noise within 2% of a baseline,
  validated by Monte Carlo at 0.5% (common factor). The variable there is the
  532 nm transmission, not manufacturing tolerance.
- `projects/SFG/PLAN_robust_sfg.md`: a three-wavelength coating where they
  scan the number of pairs (16 to 24) against Monte Carlo robustness and add
  curvature penalties to the cost.

Neither is published, and neither studies a single-wavelength ETM with
independent per-layer errors, error sizes above 0.5%, or a transmission-target
sweep. But it shows the same group is circling "layer count vs robustness".
We must cite the repo and say exactly how ours differs. Worth considering:
a short, polite email to the authors once we have results.

## 3. What OptimalBragg can do (inventory)

| Need | In the package? | Where |
| --- | --- | --- |
| Transmission/reflection of a stack | Yes | `layers.trans`, `layers.refl`, `layers.multilayer_diel` |
| Quarter-wave starting stack, half-wave cap | Yes | `qw_stack(lam, sub, sup, films, pattern, hwcap)` |
| Coating Brownian noise (full Hong 2013) | Yes | `noise.coating_brownian` (adapted from gwinc) |
| Brownian noise proxy (fast) | Yes | `noise.brownian_proxy`, from LIGO doc E0900068 p.4 |
| Thermo-optic noise | Yes | `noise.coating_thermooptic` |
| Differential evolution optimizer | Yes | `optimizer.diff_evo` (SciPy, weighted cost) |
| Monte Carlo tolerance | Partly | Common-factor errors only; no per-layer errors |
| Varying layer count | Manually | Set the number of pairs per run; GitHub version has a sweep tool |
| Transmission-target sweep | Manually | Change `Trans1.target` per run |
| aLIGO ETM example | GitHub only | `projects/aLIGO/ETM_params.yml`: 21 pairs, T = 5 ppm, 532 nm T = 3.2% |

License: BSD-style (Caltech, 2017). Python 3.10+. PyPI is version 1.0.2;
GitHub is a newer rewrite (pyproject version 0.2.0, with numba, a CLI and tests).
Decision for Tonmay: which one we build on (see the end).

## 4. Smoke test (rerun it yourself: `python scripts/smoke_qw_etm.py`)

Quarter-wave SiO2/TiTa2O5 stacks at 1064 nm, beam radius 6.2 cm, 295 K,
PyPI material values (TiTa2O5 loss angle 2e-4):

| Pairs | T, no cap (ppm) | T, half-wave SiO2 cap (ppm) | Brownian ASD @100 Hz (m/rtHz) |
| --- | --- | --- | --- |
| 18 | 18.8 | 8.9 | 6.17e-21 |
| 19 | 9.3 | 4.4 | 6.35e-21 |
| 20 | 4.6 | 2.2 | 6.52e-21 |
| 21 | 2.3 | 1.1 | 6.69e-21 |

Read-offs, all preliminary:
- Each pair roughly halves the transmission (set by the SiO2/TiTa2O5 index
  contrast).
- Each pair adds only about 2.7% noise. Our prediction holds so far: noise
  changes slowly with layer count while transmission changes fast.
- With quarter-wave layers, 20 pairs (no cap) or 19 pairs (with cap) already
  meet 5 ppm. aLIGO uses 21 optimized pairs because it must also meet the
  532 nm spec. So the real margin depends on whether we keep the 532 nm
  requirement. That is a decision for Tonmay (see below).
- The noise magnitude (~6.5e-21) is in the right range: the Caltech paper's
  ETM requirement is 7.5e-21. The difference likely comes from the loss angle
  (code: 2e-4; paper: 3.6e-4).

Gotcha found: `coating_brownian` returns NaN if two identical layers sit
next to each other (e.g. an SiO2 cap followed by an SiO2 layer), because it
divides by a zero reflection coefficient. Patterns must alternate.

## 5. Noise formulas: where they come from

- Full calculation: Hong et al., Phys. Rev. D 87, 082001 (2013), Eqs. 94 to 96
  (as implemented in `coating_brownian`; derivation notes in LIGO T2000552).
- Fast proxy: LIGO E0900068 p.4 (aLIGO ETM coating spec). Weights each
  material's thickness by loss angle, index and Young's modulus relative to
  the substrate.
- Tonmay does not need to re-derive Hong 2013. He needs to know what goes in
  (thicknesses, loss angles, Young's moduli, Poisson ratios, beam size,
  temperature) and why noise scales with thickness times loss angle.

## 6. Material values disagree between sources

| Value | PyPI/GitHub code | Caltech paper |
| --- | --- | --- |
| TiTa2O5 loss angle | 2e-4 (ref arXiv 0912.0107) | 3.6e-4 |
| Ta2O5 loss angle | 3.8e-4 | n/a |
| SiO2 loss angle | 0.5e-4 | n/a |
| TiTa2O5 index | 2.06 | n/a |

We should run everything at both 2e-4 and 3.6e-4 and report both. Rankings
of designs should not change much; absolute noise will.

## 7. Overlap check (citations of the Caltech and Pierro papers)

Could not query citation databases directly (blocked from this environment);
used web search instead. New items found, none overlapping our question:
- Kranhold et al. 2026, arXiv 2605.00714: metasurface-Bragg hybrid mirror,
  Monte Carlo on the metasurface only, not on Bragg layers.
- Applied Optics 65(12), 4018 (2026): deep-UV anti-reflective coatings,
  Monte Carlo with large thickness errors; different application.
Tonmay should still do a 30-minute Google Scholar "cited by" pass on both
papers, since our search was limited.

## Decisions for Tonmay (needed before day 3)

1. **Build on PyPI 1.0.2 or the newer GitHub version?** PyPI is simpler and
   already works in our smoke test. GitHub is newer, faster and tested, but
   more complex. My suggestion: PyPI for the optics and noise functions, our
   own code for the sweep and Monte Carlo.
2. **Keep the 532 nm requirement or drop it?** Dropping it makes a cleaner,
   simpler study (one wavelength). Keeping it matches the real aLIGO mirror.
   My suggestion: drop it, and say so clearly in the paper.
3. **Loss angle for TiTa2O5:** report both 2e-4 and 3.6e-4, or pick one?
