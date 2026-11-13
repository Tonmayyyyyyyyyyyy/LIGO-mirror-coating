# Work plan: 10 days, 14 to 23 November 2026

## Ground rules

- Claude does most of the coding, runs and literature digging.
- Tonmay makes the decisions, checks the numbers, understands every plot,
  and writes the paper in his own words.
- Nothing goes in the paper that Tonmay can't explain without notes.
- Every run is a script in the repo. Every result has a commit.
- Lab notebook (`LAB_NOTEBOOK.md`): a few lines from Tonmay each day.

## Day by day

| Day | Date | Claude | Tonmay | Done when |
| --- | --- | --- | --- | --- |
| 1 | Sat 14 Nov | Find published monitoring accuracy (optical, quartz) to set measurement-error levels. Clean up prototype scripts into one module. | Read the proposal and `notes/day01b_new_direction.md`. Read Venugopalan 2024 Sec. 1, 2.1, 2.4. Run `scripts/dichroic_sensitivity.py`. | Error levels chosen with sources |
| 2 | Sun 15 Nov | Add measurement error to the rescue code. Check the code against a hand-worked case. | Read E0900068 (spec, 2 pages) and the Brownian noise part of Harry 2002. **Gate 1.** | Code runs with measurement error; Gate 1 passed |
| 3 | Mon 16 Nov | Re-optimize the reference design properly (more iterations, several seeds); check it against full Hong 2013 noise. | Re-run one Monte Carlo case yourself and compare with Claude's number. | Reference design fixed and frozen |
| 4 | Tue 17 Nov | Main sweep part 1: k = 0..8, errors 0.5–3%, perfect measurement, 200 trials per case. | Make the first pass-rate plot yourself from the saved data. | Sweep 1 data in repo |
| 5 | Wed 18 Nov | Main sweep part 2: add measurement error (0.25, 0.5, 1%). | Write the Method section draft. **Gate 2.** | Sweep 2 data in repo |
| 6 | Thu 19 Nov | Checks: common-factor errors; full-formula noise for the rescued designs; trial count large enough. | Look at the plots and write what they say, in plain words, in the notebook. | All checks done |
| 7 | Fri 20 Nov | Final figures (3 or 4). Table of tolerable error at 95% pass rate. | Write Results section draft. | Figures final |
| 8 | Sat 21 Nov | Review Tonmay's draft for errors; fill in references. | Write Introduction and Discussion. | Full first draft |
| 9 | Sun 22 Nov | Second check of every number in the paper against the data. | Send draft to supervisor. **Gate 3.** Revise. | Draft sent |
| 10 | Mon 23 Nov | Tidy repo: README, how to reproduce every figure. Draft a short email to the Caltech and LMA authors. | Final read. Decide on arXiv/journal, email to authors. | Paper and repo final |

## Understanding gates (Tonmay answers without notes)

**Gate 1 (day 2)**
1. Why does a coating cause thermal noise? What is a loss angle?
2. Why do alternating high/low index layers reflect so well?
3. Why is a quarter-wave mirror almost immune to thickness errors at its
   own wavelength, but a dual-wavelength mirror isn't?
4. What does "re-optimizing the top k layers" mean, step by step?

**Gate 2 (day 5)**
1. Why does measurement error matter for the rescue?
2. What exactly is a "pass" in our Monte Carlo?
3. Why do we use a proxy for noise inside the optimizer, and when do we
   use the full formula?

**Gate 3 (day 9)**
1. What is our main result in one sentence, with a number?
2. What would make our result wrong?
3. What does our work not show?

## Deliverables on day 10

- A 6–8 page paper (arXiv style).
- The GitHub repo with code that reproduces every figure.
- The lab notebook.

## Acknowledgment wording

"This work was carried out independently by the author. Computational and
literature work was assisted by Claude (Anthropic), an AI model. [Professor]
of Rajshahi University provided guidance."
