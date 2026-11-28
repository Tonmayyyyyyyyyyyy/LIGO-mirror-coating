"""Day 7: why do mirrors fail? For each failed mirror, which wavelength is
out of spec and in which direction. Same mirrors with and without rescue.
Spec: 4-6 ppm at 1064 nm, 1-4% at 532 nm (E0900068).
"""
import sys
from collections import Counter
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, ".")
import rescue

N = 200
DESIGNS = {"sturdy": "designs/robust_seed9_t2.5.npy",
           "quiet": "designs/lownoise_seed5_t2.5.npy"}
CASES = [("sturdy", "independent", 0.02), ("sturdy", "independent", 0.03),
         ("quiet", "independent", 0.02), ("sturdy", "common", 0.01),
         ("sturdy", "common", 0.02), ("quiet", "common", 0.02)]


def label(L):
    T1, T2 = rescue.transmissions(L)
    bad = []
    if T1 < 4e-6: bad.append("1064 low")
    if T1 > 6e-6: bad.append("1064 high")
    if T2 < 0.01: bad.append("532 low")
    if T2 > 0.04: bad.append("532 high")
    return " + ".join(bad) or "pass"


def one(args):
    name, model, dep, meas, k, i = args
    L = np.load(DESIGNS[name])
    rng = np.random.default_rng([9, int(dep * 1e4), i])
    rm = np.random.default_rng([9, int(dep * 1e4), i, 1])
    Lt = rescue.trial(L, k, dep, meas, rng, model=model, rng_meas=rm,
                      return_stack=True)[2]
    return (name, model, dep, meas, k), label(Lt)


if __name__ == "__main__":
    jobs = [(n, mo, d, me, k, i) for n, mo, d in CASES
            for me, k in ((0.0, 0), (0.0, 4), (0.01, 4)) for i in range(N)]
    res = {}
    with Pool(2) as p:
        for key, lab in p.imap_unordered(one, jobs, chunksize=8):
            res.setdefault(key, Counter())[lab] += 1
    for n, mo, d in CASES:
        print(f"\n{n}, {mo} errors, {d:.0%} ({N} mirrors)")
        for me, k in ((0.0, 0), (0.0, 4), (0.01, 4)):
            c = res[(n, mo, d, me, k)]
            tag = "no rescue      " if k == 0 else f"k=4, meas {me:.0%}  "
            fails = ", ".join(f"{lab} {v}" for lab, v in c.most_common() if lab != "pass")
            print(f"  {tag} pass {c['pass']:3d}   fails: {fails or '-'}")
