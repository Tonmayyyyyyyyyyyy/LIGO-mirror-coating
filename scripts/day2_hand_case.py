"""Day 2 hand check: does measure() report what it should, and does rescue()
pull a known-bad mirror back toward spec?

Case A: one deep layer 5% too thick (single known error), perfect measurement.
Case B: a random 2% error mirror that fails the spec without rescue.
Case C: case B again, but the measurement is wrong by 1%.
For each: T at 1064 and 532 nm before rescue, after rescue, and the change
in the top layers.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rescue as R  # noqa: E402

L = R.load_reference()
K = 4


def show(tag, Lx):
    T1, T2 = R.transmissions(Lx)
    print(f"  {tag:<28} T1064 = {T1*1e6:6.2f} ppm  T532 = {T2*100:5.2f} %  "
          f"pass = {R.passes(Lx)}")


def run(name, L_true, L_seen):
    print(name)
    show("design", L)
    show("as deposited (top k as design)", L_true)
    new = R.rescue(L_seen, L, K)
    L_fix = L_true.copy(); L_fix[1:K + 1] = new
    show("after rescue", L_fix)
    ch = (new / L[1:K + 1] - 1) * 100
    print("  top-layer changes (%):", " ".join(f"{c:+.1f}" for c in ch))
    return L_fix


# A: single known error
L_a = L.copy(); L_a[30] *= 1.05
seen = R.measure(L_a, K, 0.0, np.random.default_rng(0))
assert np.allclose(seen, L_a, rtol=1e-12, atol=0), "measure() with 0 error must be exact"
print("measure() with zero error returns the true stack: OK")
run("Case A: layer 30 is 5% too thick, perfect measurement", L_a, seen)

# B: find a random 2% mirror that fails without rescue
rng = np.random.default_rng(11)
for _ in range(100):
    rel = rng.normal(0, 0.02, len(L)); rel[:K + 1] = 0
    L_b = L * (1 + rel)
    if not R.passes(L_b):
        break
run("Case B: random 2% errors, failing, perfect measurement", L_b, L_b.copy())

# C: same mirror, measurement off by 1% per layer
seen_c = R.measure(L_b, K, 0.01, np.random.default_rng(5))
err = (seen_c[K + 1:] / L_b[K + 1:] - 1) * 100
print(f"\nmeasure() at 1%: measured/true - 1 has mean {err.mean():+.2f}% "
      f"and std {err.std():.2f}% (expect about 0 and 1)")
run("Case C: case B with 1% measurement error", L_b, seen_c)
