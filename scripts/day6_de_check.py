"""Day 6: does the fast optimizer (L-BFGS-B, 3 starts) miss fixes that the
slow global one (differential evolution) finds?

Same mirrors, same errors, same measurement noise; only the optimizer used
in the rescue changes. k = 4. Counts mirrors where the two disagree on
pass/fail, and in which direction.
"""
import sys
from itertools import product
from multiprocessing import Pool
import numpy as np
sys.path.insert(0, ".")
import rescue

N, K = 100, 4
DESIGNS = {"sturdy": "designs/robust_seed9_t2.5.npy",
           "quiet": "designs/lownoise_seed5_t2.5.npy"}


def one(args):
    name, model, dep, meas, i = args
    L = np.load(DESIGNS[name])
    out = []
    for m in ("local", "de"):
        rng = np.random.default_rng([8, int(dep * 1e4), int(meas * 1e4), i])
        rm = np.random.default_rng([8, int(dep * 1e4), int(meas * 1e4), i, 1])
        out.append(rescue.trial(L, K, dep, meas, rng, model=model,
                                rng_meas=rm, method=m)[0])
    return (name, model, dep, meas), out


if __name__ == "__main__":
    jobs = [(n, mo, d, me, i) for n, mo, d, me in
            product(DESIGNS, ("independent", "common"), (0.02, 0.03), (0.0, 0.01))
            for i in range(N)]
    res = {}
    with Pool(2) as p:
        for key, (a, b) in p.imap_unordered(one, jobs, chunksize=4):
            res.setdefault(key, []).append((a, b))
    print(f"k = {K}, {N} mirrors per row")
    print("design  model        dep  meas  pass(fast) pass(DE)  only-DE-passes  only-fast-passes")
    tot = [0, 0, 0]
    for key in sorted(res):
        r = np.array(res[key])
        a, b = r[:, 0], r[:, 1]
        od, of = int(np.sum(~a & b)), int(np.sum(a & ~b))
        tot[0] += len(r); tot[1] += od; tot[2] += of
        print(f"{key[0]:7s} {key[1]:12s} {key[2]:.0%}  {key[3]:.0%}   "
              f"{a.mean():.2f}       {b.mean():.2f}      {od:3d}             {of:3d}")
    print(f"total {tot[0]} mirrors: DE-only passes {tot[1]}, fast-only passes {tot[2]}")
