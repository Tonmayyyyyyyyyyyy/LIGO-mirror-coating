# LIGO-mirror-coating

Simulation study: can re-optimizing the last few layers of a LIGO end-mirror
coating, during deposition, rescue mirrors whose lower layers came out wrong?
See `PROPOSAL.md` and `WORK_PLAN.md`.

## Setup

    pip3 install -r requirements.txt
    python3 -m pytest -q tests

## Main pieces

- `rescue.py`: the model (design, deposition errors, measurement, rescue, pass/fail).
- `scripts/run_sweep.py`: pass rate over k, deposition error, measurement error.
  Quick test: `python3 scripts/run_sweep.py --trials 20 --k 0 4 --dep 0.02 --meas 0 0.01`
- `scripts/dichroic_sensitivity.py`: designs the reference mirror and checks it without rescue.
- `notes/`: day-by-day findings. `LAB_NOTEBOOK.md`: Tonmay's log.
