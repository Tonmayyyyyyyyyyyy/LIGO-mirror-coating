# Day 7 (early), Claude's side: credibility checks (14 Nov 2026)

Tonmay asked for analysis that makes the existing result more credible,
without new research questions. Three checks.

## 1. Uncertainty on the main number

`scripts/day7_bootstrap.py`, output `results/day7/bootstrap_sturdy.txt`.
Parametric bootstrap (2000 redraws of every pass count) on the Day 5 fine
scan, sturdy design, independent errors.

| Rescue | Meas. error | Tolerable error (95% pass) | 95% range |
| --- | --- | --- | --- |
| none | - | 1.69% | 1.62-1.83% |
| k = 2 | 0% | 2.51% | 2.21-2.57% |
| k = 4 | 0% | 2.65% | 2.48-2.82% |
| k = 4 | 1% | 2.61% | 2.45-2.80% |
| k = 4 | 2% | 2.40% | 2.10-2.55% |
| k = 6 | 0% | 2.47% | 2.38-2.65% |

What it says:
- The main gain is solid: without rescue the range tops out at 1.83%; with
  4 layers it starts at 2.48%. No overlap.
- "k = 4 is best" is NOT solid: k = 2, 4, 6 overlap. Honest wording:
  "re-optimizing 2 to 6 top layers gives similar gains; 4 was best in our
  runs." (Correct the Day 4/5 notes when writing the paper.)
- 2% measurement error lowers the gain a little (2.65 -> 2.40%), but
  still far above no rescue.

## 2. A second design: is the sturdy result just one lucky design?

Design `designs/seed2_t2.5.npy` (from the Day 3 search: 5.12 ppm, 2.45%,
in between quiet and sturdy in robustness). Same fine scan as Day 5
(400 trials) and same shared-error sweep as Day 6 (200 trials).
Outputs: `results/day7/fine_seed2.csv`, `bootstrap_seed2.txt`,
`common_seed2.csv`.

Tolerable error at 95% pass (independent errors):

| Rescue | Meas. | Sturdy (seed 9) | Middle (seed 2) |
| --- | --- | --- | --- |
| none | - | 1.69% (1.62-1.83) | 1.21% (1.14-1.33) |
| k = 4 | 0% | 2.65% (2.48-2.82) | 1.76% (1.65-1.84) |
| k = 4 | 1% | 2.61% (2.45-2.80) | 1.45% (1.30-1.56) |
| k = 4 | 2% | 2.40% (2.10-2.55) | below 1% (worse than no rescue) |

Shared error, seed 2: 68% -> 74% at 1% (k = 4), 38% -> 47% at 2%.

What it says:
- With good measurement the gain repeats on a second design: about 1.5x
  the tolerable error in both (1.69 -> 2.65; 1.21 -> 1.76). So the main
  result is not one lucky design.
- But how much measurement error the rescue can stand depends on the
  design. Sturdy: 2% measurement error is fine. Middle: 1% costs half the
  gain, 2% makes things worse than no rescue (at 1% deposition error,
  99% -> 88% pass). Quiet (Day 4): even 1% hurts.
- So across three designs there is one clear pattern: the sturdier the
  design, the more measurement error the rescue can tolerate. This is a
  stronger, more general finding than the sturdy design alone, and it
  answers research question 2 better.
- Shared errors: the rescue gain is small on all three designs.

Paper: present all three designs as a ladder (quiet, middle, sturdy).
Methods Sec. 1.2 updated to mention the third design.

## 3. Why mirrors fail

`scripts/day7_failures.py`, output `results/day7/failures.txt`. 200 mirrors
per case, same mirrors with and without rescue (k = 4).

Without rescue, almost every failure is "too much green light" (532 nm
above 4%). With rescue those mostly disappear, and the remaining failures
move to "too much main-laser light" (1064 nm above 6 ppm). Example, sturdy,
independent 3%: no rescue 40 fail at 532 only, 17 at 1064 only, 18 both;
with rescue 5 at 532, 16 at 1064.

What it says:
- Rescue is good at fixing the 532 nm target, which is what breaks first.
- What limits rescue is the narrow 1064 nm window (4-6 ppm). The top
  layers cannot pull both wavelengths back at once when the errors are big.
- Shared errors push both wavelengths out at once ("1064 high + 532 high"
  is the biggest group at 2%). Four top layers cannot fix that: this is
  why rescue stops near 92% / 56% in the shared-error case.
- Quiet design: rescue turns 532 failures into 1064 failures one for one,
  no net gain. Explains the Day 4 result.
- Failures are almost always "too much light", never too little.

This gives the Discussion a mechanism, not just numbers.
