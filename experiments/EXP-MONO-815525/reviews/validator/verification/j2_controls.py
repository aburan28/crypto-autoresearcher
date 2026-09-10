"""Controls for J1/J2.

POS  : g-irreducible instances WITHOUT a degree drop -- all four signed sums
       must be finite, exactly one with an F_p-rational x, and Q_e monic must
       equal prod over all four classes.
DISCR: the 'proves too much' check -- does my criterion also fire on a genuine
       repeated-root (ramification) event?  It must NOT, and it must be able to
       see one when one exists."""
import json, random, sys, time
from collections import Counter
sys.path.insert(0, ".")
from ffield import norm, deg, gcdp, derivp, has_root_Fp, factor_shape
from qe_indep import qe_from_my_S4, to_Fp, s3_of_e
from j2_pointarith import verify_instance

CURVES = [("C1", 101, 2, 3), ("C2", 1009, 5, 7), ("C3", 211, 3, 11),
          ("C4", 1999, 7, 13), ("C5", 101, 37, 29)]

# ---------------------------------------------------- POSITIVE CONTROL
print("=== POSITIVE CONTROL: g-irreducible, NO degree drop ===")
rng = random.Random(20260904)
res = []
for cid, p, A, B in CURVES:
    got = 0
    while got < 10:
        e1, e2, e3 = (rng.randrange(p) for _ in range(3))
        gp = [(-e3) % p, e2 % p, (-e1) % p, 1]
        if has_root_Fp(gp, p):
            continue
        if s3_of_e(p, A, B, e1, e2, e3) == 0:
            continue                     # that is the drop locus; excluded here
        o = verify_instance(p, A, B, e1, e2, e3)
        o["curve"] = cid
        res.append(o); got += 1
keys = ["g_irreducible", "P2_on_curve", "P3_on_curve", "x_coords_are_roots_of_g",
        "deg_drop_equals_n_at_infinity", "all_finite_sums_are_roots_of_Qe",
        "Qe_monic_equals_prod_over_finite_classes", "Qe_lands_in_Fp"]
for k in keys:
    print("  %-42s %d / %d" % (k, sum(1 for o in res if o[k]), len(res)))
print("  n_sign_classes_at_infinity:", dict(Counter(o["n_sign_classes_at_infinity"] for o in res)))
print("  deg Q_e:", dict(Counter(o["Qe_degree"] for o in res)))
print("  #finite sums with F_p-rational x:",
      dict(Counter(o["n_finite_sums_with_Fp_rational_x"] for o in res)))
print("  curves:", dict(Counter(o["curve"] for o in res)))

# --------------------------------------- DISCRIMINATION: repeated roots
print("\n=== DISCRIMINATION CONTROL: repeated roots vs roots at infinity ===")
print("full F_p^3 scan (g irreducible OR NOT), p=101, both curves\n")
for cid, p, A, B in (("C1", 101, 2, 3), ("C5", 101, 37, 29)):
    cnt = Counter()
    examples = {}
    for e1 in range(p):
        for e2 in range(p):
            for e3 in range(p):
                cs, _F, _a, _b, _c = (None,)*5
                # symmetric evaluation (fast path): reuse S_3 for the drop test
                q = None
                from sweep_indep import CK
                vals = []
                for k in range(5):
                    s = 0
                    for (i, j, d, l, m), co in CK[k].items():
                        s += co * pow(e1, i, p) * pow(e2, j, p) * pow(e3, d, p) \
                             * pow(A, l, p) * pow(B, m, p)
                    vals.append(s % p)
                q = norm(vals, p)
                if not q:
                    cnt["Q_e identically zero"] += 1; continue
                d = deg(q)
                sqfree = deg(gcdp(q, derivp(q, p), p)) == 0
                girr = not has_root_Fp([(-e3) % p, e2 % p, (-e1) % p, 1], p)
                key = ("g_irr" if girr else "g_red", "deg%d" % d,
                       "squarefree" if sqfree else "REPEATED_ROOT")
                cnt[key] += 1
                if key not in examples:
                    examples[key] = (e1, e2, e3, q)
    print(" ", cid, "->")
    for k in sorted(cnt, key=str):
        print("     %-46s %d" % (str(k), cnt[k]))
    print("     example REPEATED_ROOT cases:")
    for k, v in examples.items():
        if isinstance(k, tuple) and k[2] == "REPEATED_ROOT":
            print("       ", k, "e=", v[:3], "Q_e=", v[3],
                  "shape=", factor_shape(v[3], p))
    break_flag = any(isinstance(k, tuple) and k[0] == "g_irr" and k[2] == "REPEATED_ROOT"
                     for k in cnt)
    print("     ANY repeated root inside the g-irreducible locus:", break_flag)
