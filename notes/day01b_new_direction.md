# New direction: rescuing a coating during deposition (2026-11-13, evening)

Replaces the "layer count vs tolerance" plan. That question is already named
in the Caltech paper's intro (layer-pair count as a hyper-parameter checked
by Monte Carlo), so its novelty was too thin.

## Big question

Coatings are designed once, then deposited layer by layer. If the layers
already deposited came out wrong, can re-optimizing the layers *not yet
deposited* bring the mirror back into spec, with thermal noise in the cost?
How many layers does it take, and what does it cost in noise?

## 10-day question

For a dichroic aLIGO-style end mirror (T <= 5 ppm at 1064 nm, T = 3.2% at
532 nm, SiO2/TiTa2O5, 20 pairs + half-wave cap), how does the pass rate
change when the top k layers are re-optimized after random errors in the
rest, for k = 0..8, error size 0.5-2%, and how much does knowledge of the
deposited thicknesses (measurement error) limit it?

## Novelty check (web search + full-text reads, ~1 hour)

| Source | Re-optimizes during deposition? | Notes |
| --- | --- | --- |
| Venugopalan et al. 2024 (arXiv 2110.13437) | No | Design, then Monte Carlo check. Text: i.i.d. 0.5%; code: one common factor. No layer-count or error-size sweep. |
| Pierro et al. 2021 (arXiv 2012.02146) | No | Fixed designs; independent +/-1 nm errors. |
| Pierro et al. 2026 (arXiv 2601.17886), coatings grown at LMA | No | "Designs fixed before fabrication"; only post-deposition measurement described. |
| Pinard et al. review (arXiv 1712.05701) | Not described | Thickness measured after deposition by spectrophotometry. |
| Hartmann et al. 2026 (arXiv 2603.16656), Kranhold et al. (2605.00714, 2609.05001) | No | Metasurface hybrids; tolerance of metasurface only. |
| Facet coatings, Sci. Rep. 2025 (doi 10.1038/s41598-025-89625-6) | Yes | General optics, laser facets. Full text not reachable from here, title/abstract only. |
| Tikhonravov, Trubetskov, Amotchkina et al. (2000s-2010s); Fraunhofer IOF | Yes | "Online characterization and reoptimization" is established in general thin-film optics. |

Verdict: the technique is known in general optics. We found no published
application to gravitational-wave mirrors, and none with thermal noise in
the re-optimization cost. Risk: coating vendors (LMA) may do something like
this in practice without publishing it. We should say this openly and ask
in the email to the authors.

## Prototype results (scripts in `scripts/`, small trial counts)

1. `rescue_prototype.py` - single-wavelength quarter-wave ETM (20 pairs):
   T(1064) passes 100% even at 2% independent errors. A quarter-wave stack is
   very forgiving at its centre wavelength. Rescue is pointless there.
2. `dichroic_sensitivity.py` - optimized dichroic ETM (T1064 = 4.92 ppm,
   T532 = 3.16%, noise proxy 0.95 x quarter-wave). Pass rate for both specs
   (T1064 <= 5 ppm, T532 within 3.2 +/- 0.5%), 500 trials:
   0.5% -> 0.76, 1% -> 0.45, 2% -> 0.14. The 532 nm spec is what breaks.
3. `dichroic_rescue.py` - re-optimize the top k layers (cap fixed), 30 trials:

   | k | 1% errors: pass | 2% errors: pass | noise proxy change |
   | --- | --- | --- | --- |
   | 0 | 0.63 | 0.13 | ~0 |
   | 2 | 0.77 | 0.43 | ~0 |
   | 4 | 0.97 | 0.73 | +0.2% |
   | 6 | 1.00 | 0.97 | +0.4% |

   (k = 0 is higher than in item 2 because the top layers are error-free.)

Caveats: assumes the deposited thicknesses are known exactly (big
assumption, must test with measurement noise); 30 trials only; noise is the
E0900068 proxy, not full Hong 2013; 532 nm pass band (+/-0.5%) is our
choice, not an aLIGO number.

## Correction (same evening): the real aLIGO spec is looser

LIGO E0900068-v5: T1064 = 5 +/- 1 ppm, T532 between 1% and 4% (goal 3.2%).
The +/-0.5% band above was ours and too tight. With the real spec, the
dichroic design passes (1000 trials): 0.5% -> 1.00, 1% -> 0.93,
2% -> 0.66, 3% -> 0.42.

Rescue with the real spec (30 trials, perfect measurement):

| k | 2% errors | 3% errors |
| --- | --- | --- |
| 0 | 0.67 | 0.50 |
| 2 | 0.97 | 0.90 |
| 4 | 1.00 | 0.97 |
| 6 | 1.00 | 1.00 |

So the framing changes: at today's error levels aLIGO mirrors mostly pass
anyway. The useful question is how much *looser* deposition control the
rescue allows (the largest error that still gives 95% pass rate), and how
measurement error limits that. `dichroic_rescue.py` now takes a spec
argument: `aligo` (default) or `tight`.
