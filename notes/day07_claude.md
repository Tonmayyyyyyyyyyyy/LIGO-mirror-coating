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
