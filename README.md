# In-situ re-optimization of gravitational-wave detector coatings

Code, data and paper source for *In-Situ Re-optimization of Gravitational-wave
Detector Coatings for Improved Deposition Error Tolerance* (T. A. Tonmay, 2026).

The study simulates a 40-layer SiO2 / Ti:Ta2O5 end-mirror coating of the
Advanced LIGO type. After the lower layers are deposited (with thickness errors)
and measured (with measurement errors), the top few layers are re-optimized to
bring the mirror back into its transmission specification at 1064 nm and 532 nm.
The question is how much larger a deposition error the mirror can then tolerate,
how this depends on the measurement error, and what it costs in coating thermal
noise. All results are from Monte Carlo simulations on a population of 32
coating designs.

To re-make every number, table and figure in the paper, see
[REPRODUCE.md](REPRODUCE.md).

## Layout

| Path | Contents |
| --- | --- |
| `rescue.py` | The model: coating stack, transmission, pass test, noise proxy, deposition and measurement errors, the rescue (`trial()`) |
| `tests/` | Tests of the model (`python3 -m pytest -q tests`) |
| `designs/` | The 32 coating designs (`population/seed*.npy` regenerate from their seeds; seed 21 is excluded because it misses the 1064 nm target) |
| `scripts/` | Design generation, Monte Carlo runs, checks, statistics and figures; `reproduce_all.sh` runs everything in order |
| `results/` | All simulation outputs and analysis summaries used in the paper |
| `paper/` | LaTeX source, figures and the compiled PDF |

## Requirements

Python 3.13 with the pinned packages in `requirements.txt` (OptimalBragg 1.0.2,
NumPy, SciPy, Matplotlib, pytest). Building the PDF needs a LaTeX installation
with `latexmk`.
