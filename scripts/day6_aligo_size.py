"""Day 6: how big a systematic thickness error does it take, in our model,
to make T(532 nm) about 10x too high (the aLIGO ETM report, arXiv 1411.4547
Sec. 4.3), and is T(1064 nm) still in spec (4-6 ppm) at that point?

Three error types: all layers off together, only Ti:Ta2O5 off, only SiO2
off. The cap (layer 0, SiO2) follows its material.
"""
import sys
import numpy as np
sys.path.insert(0, ".")
import rescue

errs = np.round(np.arange(-0.10, 0.1001, 0.0025), 4)
is_h = rescue.IS_H
for name, path in [("sturdy", "designs/robust_seed9_t2.5.npy"),
                   ("quiet", "designs/lownoise_seed5_t2.5.npy")]:
    L = np.load(path)
    T1d, T2d = rescue.transmissions(L)
    print(f"\n{name}: design T1064 {T1d*1e6:.2f} ppm, T532 {T2d:.2%}")
    for kind, mask in [("all layers", np.ones_like(is_h)),
                       ("Ta2O5 only", is_h), ("SiO2 only", ~is_h)]:
        rows = []
        for e in errs:
            Lx = L * (1 + e * mask)
            T1, T2 = rescue.transmissions(Lx)
            rows.append((e, T1, T2))
        hits = [r for r in rows if r[2] >= 10 * T2d]
        print(f"  {kind}:")
        for sign in (+1, -1):
            h = [r for r in hits if np.sign(r[0]) == sign]
            if not h:
                print(f"    {'+' if sign>0 else '-'}: T532 never reaches 10x within 10%")
                continue
            e, T1, T2 = min(h, key=lambda r: abs(r[0]))
            ok = 4e-6 <= T1 <= 6e-6
            print(f"    smallest {'thicker' if sign>0 else 'thinner'} error giving 10x: "
                  f"{e:+.2%} -> T532 {T2:.1%}, T1064 {T1*1e6:.2f} ppm "
                  f"({'in spec' if ok else 'OUT of spec'})")
        # where does 532 first leave the 1-4% window?
        out = [r for r in rows if not (0.01 <= r[2] <= 0.04)]
        e = min(out, key=lambda r: abs(r[0]))[0]
        print(f"    532 nm first leaves the 1-4% window at {e:+.2%}")
