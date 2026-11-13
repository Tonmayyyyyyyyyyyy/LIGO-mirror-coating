# Lab notebook

One entry per work day, in your own words. A few lines is enough:
what was decided, what was run, what came out, what's next.

---

## 2026-11-13 (Day 1)

- Read: Venugopalan et al. 2024, introduction, Sections 2.1 and 2.4. The introduction sounded very similar to our original plan (layer count vs tolerance), so we switched to the rescue project.
- Section 2.4 says (fill in your own words): 
- Decided: modified research question. started fresh. Start with a big & important question, focusing on manufacturing ease. Modified too fit in a 10 day work. (not exactly modified. trimmed it. we'll complete a small part of that project)
- Ran: scripts/dichroic_sensitivity.py. It designs the mirror: 4.92 ppm at 1064 nm, 3.16% at 532 nm. Pass rates from the first run (old tight 532 nm band, 500 trials): 0.5% errors 0.77, 1% 0.58, 2% 0.39. Re-run with the real aLIGO spec matched: 1.00 at 0.5%, 0.90 at 1%, 0.66 at 2%.
- Confused by: not sure what the code did or measured. Now: it designs the mirror, breaks it with random layer errors, and counts how many still pass both targets.
- Next: Day 2: Gate 1 questions, then add measurement error to the rescue code.
