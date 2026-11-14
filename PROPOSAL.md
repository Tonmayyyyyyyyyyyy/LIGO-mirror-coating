# Rescuing LIGO mirror coatings during deposition: a simulation study

Tasdik Ahmed Tonmay. Draft, 13 November 2026.

## Background

The mirrors in LIGO reflect laser light using a coating made of about forty
thin layers of two materials, silica (SiO2) and titania-doped tantala
(Ti:Ta2O5). Each layer is a few hundred nanometres thick. The end mirrors
have two optical targets at once. At the main laser wavelength (1064 nm)
they must let through only 5 ± 1 parts per million of the light. At 532 nm,
the green light used to lock the detector, they must let through between 1%
and 4% (LIGO E0900068). The coating is also the largest source of thermal
noise in LIGO's most sensitive frequency band (Brownian noise), so its
design is a careful trade-off.

Coatings are designed on a computer and then deposited one layer at a time.
Real layers come out slightly thicker or thinner than designed. Current
practice in gravitational-wave coating work, as far as published papers
show, is to design once and then check by simulation how often random
errors push the mirror out of spec (Venugopalan et al. 2024; Pierro et al.
2021, 2026). If a layer comes out wrong during deposition, the remaining
layers are still deposited as originally designed.

In other parts of optics there is a known alternative: measure the layers
already deposited, then re-optimize the layers that have not been deposited
yet, so they cancel the errors (Tikhonravov, Trubetskov and Amotchkina;
Fraunhofer IOF; a 2025 study on laser facet coatings). We found no
published study of this for gravitational-wave mirrors, and none that keeps
thermal noise in the re-optimization.

## Research question

For an aLIGO-style end mirror (SiO2/Ti:Ta2O5, 20 layer pairs plus a
half-wave silica cap, dual-wavelength spec), if only the top k layers are
re-optimized after the rest have been deposited with random errors:

1. How much larger can the deposition errors be while still keeping 95% of
   mirrors in spec?
2. How does this depend on how accurately the deposited layers can be
   measured?
3. What does the rescue cost in Brownian thermal noise?

## Why this matters

Tight thickness control is one of the things that makes these coatings
hard and expensive to make. If re-optimizing a few top layers lets the same
spec be met with looser control, the coating maker's job gets easier: fewer
rejected mirrors, or a simpler deposition process. If the rescue only works
when measurement is near-perfect, that is also useful to know, because it
says where the effort should go (better monitoring, not better deposition).

## Preliminary results

Prototype runs (scripts and notes in the repository; noise from the full
Hong et al. formula unless stated).

- A plain quarter-wave mirror built only for 1064 nm passed in every trial
  even with 2% errors. The single-wavelength case does not need rescue; the
  532 nm requirement is what makes the mirror sensitive.
- Optimizing the dual-wavelength design gives two kinds of design. A quiet
  one (Brownian noise 6.19e-21 m/rtHz at 100 Hz) is fragile: with 2% errors
  it passes the aLIGO spec in about 64-68% of trials. A sturdy one
  (6.68e-21 m/rtHz, about 8% noisier) passes in about 91-98%.
- Re-optimizing the top 4 layers raised the quiet design from 64% to 70%
  and the sturdy one from 98% to 100% (50 trials, 2% errors, perfect
  measurement, all layers deposited with errors, including re-optimized
  ones). With 8 layers the quiet design reached 83% (200 trials).
- Earlier prototype numbers (for example 58% to 95%) were on a design that
  sat near the edge of the 532 nm window, and deposited the re-optimized
  layers without error. They overstated the gain and are not used.

So the question becomes concrete: can rescue let the quieter design approach
the pass rate of the sturdy one, and at what error and measurement levels?

## Method

All work is computational, in Python, on a laptop.

1. **Optics and noise.** Transmission from the transfer-matrix method and
   Brownian noise from Hong et al. (2013), both through the open-source
   OptimalBragg package (Caltech). The fast E0900068 proxy is used inside
   optimization loops; the full formula is used for final numbers.
2. **Two reference designs.** 20-pair dual-wavelength end mirrors
   optimized with differential evolution for 5 ppm at 1064 nm and 2.5% at
   532 nm (the middle of the 1-4% window), with a noise penalty: one quiet
   but fragile, one about 8% noisier but sturdy. The rescue aims at the
   same targets.
3. **Errors.** Each deposited layer gets an independent random thickness
   error (standard deviation 0.5% to 3%). A common-factor error (all layers
   off together) is run as a check, since that is what the existing
   OptimalBragg Monte Carlo uses.
4. **Measurement.** The re-optimization sees measured thicknesses, not true
   ones: true value plus a random measurement error (0, 0.25%, 0.5%, 1%,
   2%). Sources for the scale: deposition errors of about 1 nm + 1% are
   typical (Tikhonravov & Trubetskov 2012); run-to-run thickness spread
   0.9% (Ta2O5) to 1.5% (SiO2), and optical vs quartz-crystal thickness
   readings differing by about 2.6% (Wilbrandt et al. 2008); in-situ
   fitted thicknesses off by up to about 4 nm per layer (Melzig et al. 2024).
   No source gives a single per-layer measurement accuracy, so we sweep.
   The re-optimized top layers and the cap are also deposited with errors.
5. **Rescue.** The top k layers (k = 0 to 8) are re-optimized for the
   transmission targets with a noise penalty, using the measured values.
   The mirror then passes or fails on its true thicknesses.
6. **Output.** Pass rate against error size, for each k and each
   measurement level. From this, the largest error that still gives 95%
   pass rate, and the noise cost.

## Relation to existing work

| Work | What it does | What we add |
| --- | --- | --- |
| Venugopalan et al. 2024 (OptimalBragg) | Design by global optimization, then Monte Carlo check at 0.5% | Correction during deposition; error sizes up to 3%; measurement error |
| Pierro et al. 2021 | Exhaustive search over multi-material quarter-wave designs; robustness tested for absorption (extinction coefficient) only, not thickness | Thickness errors and their correction |
| Pierro et al. 2026 | Ternary coatings built at LMA with fixed designs; tolerance check with independent ±0.5 nm errors | Correction during deposition for the standard two-material end mirror |
| Poitras & Ma, Sci. Rep. 2025 | Simulated re-optimization after every layer for laser facet coatings; surrogate sensitivity analysis | Same idea applied to a GW mirror: dual-wavelength spec, thermal noise in the cost, measurement error |
| Tikhonravov & Trubetskov; Fraunhofer IOF (Wilbrandt 2008); Melzig et al. 2024 | In-situ characterization and re-optimization in general optical coating production | Applied to a GW mirror, with thermal noise in the cost |

## Expected results

One of two outcomes, both reportable:

- Rescue of 2 to 4 top layers still raises the tolerable error clearly
  (for example from about 1% to about 2–3%) at realistic measurement error.
  Then a looser deposition process could meet the aLIGO spec at almost no
  noise cost.
- The gain shrinks fast as measurement error grows. Then the result is a
  number: how accurate monitoring must be before rescue is worth doing.

## Limitations

- Simulation only. No coating is made. Real deposition has effects not
  modelled here (refractive index drift, absorption, non-uniform layers).
- Rescue is done once, near the end, not after every layer.
- One mirror type (aLIGO end mirror). Future detectors are not covered.
- Coating labs may already correct errors this way without publishing it.
  We will ask the authors of the Caltech and LMA papers.

## Timeline

Ten days, 14 to 23 November 2026. See the work plan.

## Guidance needed from supervisor

- Whether the measurement-error levels are reasonable.
- Feedback on the draft write-up (day 9).
- Advice on whether and how to contact the Caltech and LMA groups.

## Sources

- Venugopalan, Salces-Cárcoba, Arai, Adhikari, Optics Express 32(7), 11751
  (2024), arXiv 2110.13437. OptimalBragg code: PyPI and
  github.com/CaltechExperimentalGravity/OptimalBragg.
- Pierro et al., Phys. Rev. Research (2021), arXiv 2012.02146.
- Pierro et al., "Experimental realization of optimized ternary mirror
  coatings", arXiv 2601.17886 (2026).
- Hong, Yang, Gustafson, Adhikari, Chen, Phys. Rev. D 87, 082001 (2013).
- Harry et al., Class. Quantum Grav. 19, 897 (2002).
- LIGO E0900068-v5, Advanced LIGO End Test Mass Coating Specification.
- Pinard et al., arXiv 1712.05701 (review of LMA coatings).
- "Online characterization and reoptimization of optical coatings",
  Proc. SPIE vol. 5250 (authors and year to confirm).
- Poitras & Ma, "Surrogate sensitivity analysis of facet optical coatings
  produced without and with in situ design reoptimization", Sci. Rep. (2025).
- Tikhonravov & Trubetskov, "Modern design tools and a new paradigm in optical
  coating design", Appl. Opt. 51(30), 7319 (2012).
- Wilbrandt, Stenzel, Kaiser, "All-optical in-situ analysis of PIAD deposition
  processes", Proc. SPIE 7101 (2008).
- Melzig, Amotchkina, Bruns, Farr, Terhürne, Trubetskov, Vergöhl, "Influence of
  fitting algorithms on thickness determination during monitoring of optical
  coatings", Surf. Coat. Technol. 476, 130197 (2024).
