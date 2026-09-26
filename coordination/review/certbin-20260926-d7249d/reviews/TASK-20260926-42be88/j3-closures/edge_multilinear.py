"""J3 (4): multilinear-reduction edge cases where v_j divides monomials of b.

Expected values are written by hand (in B, v_j^2 = v_j and coefficients are mod 2):
  v_j * (v_j m) = v_j m  (reduced, kept: not dropped, not squared)
  v_j * (v_j m + m) = 0  (the two images collide and cancel: not doubled)
Checked on: the pinned engine's native products kernel (Closure.products), the numpy reference
products (reference.products with Closure.maps), Closure.build_M (Macaulay rows with collisions),
a full engine W_4 on a constructed system, and the validator's own literal map.
usage: python3 edge_multilinear.py <snapshot_root>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from literal_w4 import Lit  # noqa: E402

ROOT = sys.argv[1]
sys.path.insert(0, os.path.join(ROOT, "src"))
from crypto_autoresearcher.gf2 import closure as gclosure  # noqa: E402
from crypto_autoresearcher.gf2 import kernels, reference  # noqa: E402


def M(*idx):
    s = 0
    for i in idx:
        s |= 1 << i
    return s


# (b as list of monomials, j, expected v_j*b as a set of monomials) -- expectations by hand
CASES = [
    ("v3v5 + v5, j=3 -> 0 (collision cancels)", [M(3, 5), M(5)], 3, []),
    ("v3, j=3 -> v3 (reduced, not dropped)", [M(3)], 3, [M(3)]),
    ("v3v5v7, j=3 -> v3v5v7 (degree stays 3)", [M(3, 5, 7)], 3, [M(3, 5, 7)]),
    ("1 + v3, j=3 -> 0", [0, M(3)], 3, []),
    ("v1v2v3 + v1v2, j=3 -> 0", [M(1, 2, 3), M(1, 2)], 3, []),
    ("v0v19 + v19 + v0 + 1, j=19 -> 0", [M(0, 19), M(19), M(0), 0], 19, []),
    ("v0v19 + v19 + v0 + 1, j=0 -> 0", [M(0, 19), M(19), M(0), 0], 0, []),
    ("v2v4v6 + v4v6 + v1v4, j=4 -> unchanged", [M(2, 4, 6), M(4, 6), M(1, 4)], 4, [M(2, 4, 6), M(4, 6), M(1, 4)]),
    ("v1v2v3, j=4 -> v1v2v3v4 (degree 4)", [M(1, 2, 3)], 4, [M(1, 2, 3, 4)]),
    ("v1v2v3 + v1v2v4 + v1v2, j=4 -> v1v2v3v4", [M(1, 2, 3), M(1, 2, 4), M(1, 2)], 4, [M(1, 2, 3, 4)]),
    ("v17v18v19 + v17v18 + v18v19 + v18, j=18 -> unchanged (every monomial contains v18)", [M(17, 18, 19), M(17, 18), M(18, 19), M(18)], 18,
     [M(17, 18, 19), M(17, 18), M(18, 19), M(18)]),
    # CORRECTION NOTE: the first run of this script expected [] for the case above; that hand expectation was wrong
    # (all four monomials contain v18, so each maps to itself). Native, reference and own map agreed on b throughout.
    ("v17v18v19 + v17v19 + v18v19 + v19, j=18 -> 0 (pairs collide)", [M(17, 18, 19), M(17, 19), M(18, 19), M(19)], 18, []),
]

cl = gclosure.Closure(20, 4, 19)
L = Lit(20, 4)
res = {"backend": kernels.backend(), "cases": []}


def eng_vec(monos):
    return cl.vec(monos)


def eng_to_monos(row):
    d = cl.unpack(row[None, :])[0]
    return sorted(int(cl.col_mask[c]) for c in np.flatnonzero(d))


all_ok = True
for name, b, j, exp in CASES:
    row = eng_vec(b)[None, :].copy()
    Pn = cl.products(row)  # (nv * 1, W), j-major
    got_native = eng_to_monos(Pn[j])
    Pr = reference.products(row, cl.maps, cl.nv, cl.C, cl.W)
    got_ref = eng_to_monos(Pr[j])
    x = L.poly_from_masks(b)
    y = L.times_vj(x, j)
    got_mine = sorted(L.mons[p] for p in L.bits_of(y))
    ok = got_native == sorted(exp) and got_ref == sorted(exp) and got_mine == sorted(exp)
    # all other j too: native == reference == mine
    others = all(eng_to_monos(Pn[jj]) == eng_to_monos(Pr[jj]) ==
                 sorted(L.mons[p] for p in L.bits_of(L.times_vj(x, jj))) for jj in range(20))
    all_ok &= ok and others
    res["cases"].append({"case": name, "expected": sorted(exp), "native": got_native, "reference": got_ref,
                         "mine": got_mine, "ok": ok, "all_j_native_eq_reference_eq_mine": others})

# Macaulay rows with collisions: f_0 = v0v1 + v1 -> row (mu = v0, k = 0) must be ZERO;
# row (mu = v2, k = 0) = v0v1v2 + v1v2.
eqs = [[M(0, 1), M(1)]] + [[M(k % 20, (k + 7) % 20), M(k % 20), 0] for k in range(1, 19)]
Mm = cl.build_M(eqs)
mus = [int(m) for m in cl.mu_mask]
r_v0 = mus.index(M(0)) * 19 + 0
r_v2 = mus.index(M(2)) * 19 + 0
row_v0 = eng_to_monos(Mm[r_v0])
row_v2 = eng_to_monos(Mm[r_v2])
bm_ok = row_v0 == [] and row_v2 == sorted([M(0, 1, 2), M(1, 2)])
res["build_M"] = {"row(mu=v0,k=0)": row_v0, "expected_v0": [], "row(mu=v2,k=0)": row_v2,
                  "expected_v2": sorted([M(0, 1, 2), M(1, 2)]), "ok": bm_ok}
all_ok &= bm_ok

# Full W_4 on a constructed system whose closure needs the reductions: engine vs own literal
erec, _ = cl.w_closure(eqs, want_cert=False)
mrec, lrec, per_iter, piv = L.w_closure(eqs)
same = all(erec[f] == lrec[f] for f in ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg"))
res["constructed_system_W4"] = {"engine": {f: erec[f] for f in ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg")},
                                "mine": {f: lrec[f] for f in ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg")},
                                "equal": same}
all_ok &= same
# second constructed system, not refuted at iteration 0, with collision-prone rows
eqs2 = [[M(0, 1), M(1)]] + [[M(k, (k + 7) % 20), M((k + 3) % 20)] for k in range(1, 19)]
erec2, _ = cl.w_closure(eqs2, want_cert=False)
_, lrec2, _, _ = L.w_closure(eqs2)
F = ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg")
same2 = all(erec2[f] == lrec2[f] for f in F)
res["constructed_system_2_W4"] = {"engine": {f: erec2[f] for f in F}, "mine": {f: lrec2[f] for f in F}, "equal": same2}
all_ok &= same2
res["all_ok"] = bool(all_ok)
with open(os.path.join(HERE, "edge-multilinear.json"), "w") as fh:
    json.dump(res, fh, indent=1)
print(json.dumps(res, indent=1)[:4000])
