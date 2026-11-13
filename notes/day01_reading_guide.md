# Day 1-2 reading guide (Tonmay's side)

About 2 hours a day. Read only what's listed; skip the rest.

## Read

1. **Venugopalan et al. 2024**, arXiv 2110.13437 (html: https://arxiv.org/html/2110.13437v2)
   - Sec. 1 (Introduction): the whole thing.
   - Sec. 2.1: the reflectivity recursion (Eq. 1-2). Try it by hand for one
     layer on glass.
   - Sec. 2.3 and 2.4: noise and the tolerance analysis. Note the Table 1
     footnote about "identical fractional uncertainties". See
     `notes/day01_findings.md`, section 1, for why it matters.
   - Sec. 4.2: the aLIGO end-mirror case.
2. **Pierro et al. 2021**, arXiv 2012.02146
   - Abstract, introduction, and Sec. IV.C (robustness to thickness errors).
   - Ask yourself: what did they test, and what didn't they?
3. **Our day 1 findings**: `notes/day01_findings.md`. Then make the three
   decisions at the bottom.

## Do

- Install: `pip install OptimalBragg`, then run `python scripts/smoke_qw_etm.py`.
  You should get the same numbers as the table in the findings file.
- Start `LAB_NOTEBOOK.md`: write today's entry (what you read, what you
  decided, what confused you).
- Email the professor the proposal (the doc link).
- 30 minutes on Google Scholar: "Cited by" for both papers. Note anything
  that studies tolerance against number of layers.

## Gate 1 questions (end of day 2, no notes)

1. Why does a mirror coating create thermal noise at all?
2. What is a mechanical loss angle, in one sentence?
3. Why does a stack of alternating high- and low-index layers reflect more
   than a single layer? Why quarter-wave thicknesses?
4. Our smoke test shows each extra pair halves the transmission but adds only
   ~3% noise. Why might that be?
5. What does our project test that the Caltech code doesn't?
