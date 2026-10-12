"""J3 (5): ell, rc_b and ell_route recomputed with the validator's own code, against the archived records.

Part A (every kept system of every arm): own left kernel of the 19 x 190 quadratic-column submatrix
  (own elimination), kernel dimension, c, ell, label, j*, substitution image; C-ELL condition
  (c_k = Tr(t^k / x_R^2) for S_3 and N-CONV19; ell = ell_lin + Tr(B / x_R^2) for S_3); compared with
  closures.jsonl.gz rc_b fields.
Part B (the J3 selection of run_literal_archived.py): own substitution pi, own R'_3 rank, R'_4 rank / one /
  dims_by_deg, sigma, T5_applicable, full_B3, ref_profile; ell_route computed DIRECTLY as
  1 in rowspace(M_4) + ell * B_{<=3}; own literal W'_4 on the substituted system where the archive
  carries a T4 record; T4 relation checked on own numbers.
usage: python3 rcb_recompute.py <snapshot_root>
"""
import gzip
import json
import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "j2-population"))
import gf219 as G  # noqa: E402
from literal_w4 import Lit, eqs_from_E  # noqa: E402

ROOT = sys.argv[1]
RUN = os.path.join(ROOT, "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60")
inst = [json.loads(l) for l in gzip.open(os.path.join(RUN, "instances.jsonl.gz"), "rt")]
clo = {r["key"]: r for r in (json.loads(l) for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt"))}
S3 = ("S3-U400", "S3-SAT100", "F-RANDX19")
ELL_ARMS = S3 + ("N-CONV19",)
MASKS = [sum(1 << i for i in m) for m in G.MONO2]


def left_kernel(Q):
    """Q: 19 x 190 0/1. Own elimination: returns list of kernel vectors (ints over rows), a basis."""
    rows = []
    for k in range(Q.shape[0]):
        v = 0
        for j in np.flatnonzero(Q[k]):
            v |= 1 << int(j)
        rows.append(v)
    # Gauss-Jordan on augmented [row | e_k]
    aug = [(rows[k], 1 << k) for k in range(len(rows))]
    piv = {}
    ker = []
    for v, c in aug:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                pv, pc = piv[h]
                v ^= pv
                c ^= pc
            else:
                piv[h] = (v, c)
                break
        if v == 0:
            ker.append(c)
    return ker


def combine(E, c):
    r = np.zeros(E.shape[1], dtype=np.uint8)
    for k in range(E.shape[0]):
        if (c >> k) & 1:
            r ^= E[k]
    return r


# ---------------------------------------------------------------- Part A
A_mism = []
A_count = 0
cell_fail = []
for r in inst:
    key, arm = r["key"], r["arm"]
    E = G.hex_to_E(r["E_hex"])
    ker = left_kernel(E[:, 21:])
    dim = len(ker)
    a = clo[key]["rc_b"]
    mine = {"kernel_dim": dim}
    cvec = None
    if arm == "N-ELL19":
        e18 = 1 << 18
        in_ker = not combine(E[:, 21:], e18).any()
        cvec = e18 if in_ker else None  # dim 1 => the kernel vector IS e18; dim > 1 => rule c = e_18
    elif dim == 1:
        cvec = ker[0]
    mine["applicable"] = cvec is not None
    if cvec is not None:
        ell = combine(E, cvec)
        assert not ell[21:].any()
        mine["c"] = [(cvec >> k) & 1 for k in range(19)]
        mine["ell_support"] = [int(j) for j in np.flatnonzero(ell)]
        lin = [i for i in range(20) if ell[1 + i]]
        if not lin:
            mine["label"] = "REFUTED-AT-DEGREE-2" if ell[0] else "ELL-TRIVIAL"
        else:
            mine["label"] = "substituted"
            mine["jstar"] = lin[0]
            mine["substitution"] = {"v_jstar": lin[0], "image_vars": lin[1:], "image_const": int(ell[0])}
        if arm in ELL_ARMS:
            xr2i = G.finv(G.fsq(r["x_R"]))
            want_c = [G.tr(G.fmul(1 << k, xr2i)) for k in range(19)]
            ok = dim == 1 and mine["c"] == want_c
            if arm in S3:
                want_ell = np.zeros(211, dtype=np.uint8)
                want_ell[1] = want_ell[11] = 1
                want_ell[0] = G.tr(G.fmul(G.B_CURVE, xr2i))
                ok = ok and bool((ell == want_ell).all())
            mine["C-ELL_ok"] = bool(ok)
            if not ok:
                cell_fail.append(key)
    else:
        mine["label"] = f"not applicable (kernel dim {dim})"
    A_count += 1
    for f, v in mine.items():
        if a.get(f) != v:
            A_mism.append({"key": key, "field": f, "mine": v, "archived": a.get(f)})

# ---------------------------------------------------------------- Part B
sel = json.load(open(os.path.join(HERE, "literal-vs-archived.json")))["selection"]
byk = {r["key"]: r for r in inst}
L19_3, L19_4, L20_4 = Lit(19, 3), Lit(19, 4), Lit(20, 4)
REF_SUB = [0, 0, 18, 360, 3267]
B_out = []
for key in sel:
    r = byk[key]
    a = clo[key]
    E = G.hex_to_E(r["E_hex"])
    eqs = eqs_from_E(E)
    rb = a["rc_b"]
    row = {"key": key, "arm": r["arm"]}
    if not rb.get("applicable") or rb.get("label") != "substituted":
        row["rc_b"] = "not applicable (archived label: %s)" % rb.get("label")
        row["ell_route_archived"] = a.get("ell_route")
        B_out.append(row)
        continue
    # own ell from Part A logic
    ker = left_kernel(E[:, 21:])
    cvec = (1 << 18) if r["arm"] == "N-ELL19" else ker[0]
    ell = combine(E, cvec)
    lin = [i for i in range(20) if ell[1 + i]]
    const = int(ell[0])
    js = lin[0]
    others = lin[1:]
    img = [1 << i for i in others] + ([0] if const else [])
    eqs2 = []
    for f in eqs:
        acc = {}
        for m in f:
            if m >> js & 1:
                rest = m & ~(1 << js)
                for t in img:
                    y = rest | t
                    acc[y] = acc.get(y, 0) ^ 1
            else:
                acc[m] = acc.get(m, 0) ^ 1
        out = []
        for y, p in acc.items():
            if p:
                z = 0
                for i in range(20):
                    if y >> i & 1:
                        z |= 1 << (i if i < js else i - 1)
                out.append(z)
        eqs2.append(out)
    p3 = L19_3.span(L19_3.macaulay_rows(eqs2))
    p4 = L19_4.span(L19_4.macaulay_rows(eqs2))
    r4 = {"rank": len(p4), "one": 0 in p4, "dims_by_deg": L19_4.dims_by_deg(p4)}
    mine = {"R3_rank": len(p3), "R3_one": 0 in p3, "R4": r4, "sigma": r4["dims_by_deg"][3] - 360,
            "full_B3": r4["dims_by_deg"][3] == 1160, "T5_applicable": r4["dims_by_deg"][3] == len(p3),
            "ref_profile": r4["dims_by_deg"] == REF_SUB, "jstar": js}
    row["rc_b_mine_vs_archived"] = {f: [v, rb.get(f)] for f, v in mine.items()}
    row["rc_b_differences"] = [f for f, v in mine.items() if rb.get(f) != v]
    # ell_route directly: 1 in rowspace(M_4) + ell * B_{<=3}
    if r["arm"] in ELL_ARMS:
        ellm = [MASKS[c] for c in np.flatnonzero(ell)]
        rows = L20_4.macaulay_rows(eqs)
        for m in L20_4.mons:
            if bin(m).count("1") <= 3:
                acc = {}
                for e in ellm:
                    y = m | e
                    acc[y] = acc.get(y, 0) ^ 1
                x = 0
                for y, p in acc.items():
                    if p:
                        x ^= 1 << L20_4.pos[y]
                rows.append(x)
        pv = L20_4.span(rows)
        row["ell_route_mine"] = 0 in pv
        row["ell_route_archived"] = a.get("ell_route")
        row["ell_route_equal"] = row["ell_route_mine"] == row["ell_route_archived"]
        row["D2_consistency_mine(ell_route == one(R'_4))"] = row["ell_route_mine"] == r4["one"]
    # own literal W'_4 where the archive has a T4 record
    t4 = a.get("T4")
    _, w2, _, _ = L19_4.w_closure(eqs2)
    row["Wp4_mine"] = {f: w2[f] for f in ("dims", "iterations_to_fixpoint", "one", "one_first_iteration", "final_dim", "dims_by_deg")}
    row["T4_on_own_Wp4_vs_archived_W4"] = {"final_dim(W_4) - final_dim(W'_4)": a["W_4"]["final_dim"] - w2["final_dim"],
                                           "one_equal": a["W_4"]["one"] == w2["one"]}
    if t4 and t4.get("applicable"):
        aw2 = t4["W'_4"]
        row["Wp4_mine_vs_archived"] = {f: [w2[f], aw2[f]] for f in ("dims", "iterations_to_fixpoint", "one",
                                                                      "one_first_iteration", "final_dim", "dims_by_deg")}
        row["Wp4_differences"] = [f for f, (x, y) in row["Wp4_mine_vs_archived"].items() if x != y]
        row["T4_on_own_numbers"] = {"final_dim(W_4) - final_dim(W'_4)": a["W_4"]["final_dim"] - w2["final_dim"],
                                    "one_equal": a["W_4"]["one"] == w2["one"]}
    else:
        row["Wp4"] = "no archived T4 record for this system (not in the C-T4 set)"
    B_out.append(row)
    print(key, row.get("rc_b_differences"), row.get("ell_route_equal"), row.get("Wp4_differences"), flush=True)

res = {"part_A": {"systems": A_count, "field_mismatches": A_mism[:50], "n_mismatches": len(A_mism),
                  "C-ELL_failures_own": cell_fail},
       "part_B": B_out}
res["pass"] = (not A_mism and not cell_fail and all(not x.get("rc_b_differences") and x.get("ell_route_equal", True)
                                                     and not x.get("Wp4_differences") for x in B_out))
json.dump(res, open(os.path.join(HERE, "rcb-recompute.json"), "w"), indent=1)
print("PART A systems", A_count, "mismatches", len(A_mism), A_mism[:5], "C-ELL own failures", len(cell_fail))
print("PASS", res["pass"])
