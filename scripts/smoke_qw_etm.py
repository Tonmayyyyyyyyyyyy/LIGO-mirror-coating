"""Day 1 smoke test: quarter-wave SiO2/TiTa2O5 end-mirror stacks.

Prints transmission at 1064 nm and coating Brownian noise at 100 Hz for
18 to 21 layer pairs, with and without a half-wave SiO2 cap.

Run:  pip install OptimalBragg   then   python scripts/smoke_qw_etm.py

Note: layer patterns must alternate. Two identical layers next to each other
(e.g. an SiO2 cap followed by an SiO2 layer) make coating_brownian return NaN.
"""
import warnings

import numpy as np
from OptimalBragg import Material, qw_stack
from OptimalBragg.layers import trans
from OptimalBragg.materials import SiO2, TiTa2O5, air
from OptimalBragg.noise import coating_brownian

warnings.filterwarnings("ignore")

LAMBDA = 1064e-9   # laser wavelength [m]
W_BEAM = 0.062     # ETM beam radius [m]
FREQ = 100.0       # frequency for noise [Hz]

substrate = Material(SiO2)
substrate.Temp = 295
films = {"L": Material(SiO2), "H": Material(TiTa2O5)}

for n_pairs in [18, 19, 20, 21]:
    designs = [
        ("no cap", "", "LH" * n_pairs),
        ("L cap ", "L", "HL" * (n_pairs - 1) + "H"),
    ]
    for label, cap, pattern in designs:
        stack = qw_stack(LAMBDA, substrate, Material(air), films, pattern, hwcap=cap)
        T = trans(LAMBDA, stack)
        S = coating_brownian(np.array([FREQ]), stack, W_BEAM)[0]
        print(f"{n_pairs} pairs, {label}: T = {T * 1e6:7.2f} ppm, "
              f"Brownian ASD = {np.sqrt(S):.3e} m/rtHz")
