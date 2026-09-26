#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J3: a LITERAL, SLOW transcription of M_D and
W_D (EXP-CERTBIN-e94b27 object.macaulay_M_D / mutant_closure_W_D as restated in
EXP-CERTBIN-ddfe75 object) and of object.rc_b (1)-(5), in pure Python over
F_2. It imports nothing from impl/, verifier/ or src/crypto_autoresearcher/.

Representation: a polynomial of B_{<=D} (multilinear, nv variables) is a
Python int; bit p is the monomial POS[p]. Positions are GRADED (degree
ascending), so the leading bit of a polynomial is a monomial of maximal degree
and, for an echelon basis (distinct leading bits), dim(W cap B_{<=d}) = the
number of basis leads of degree <= d.

M_D  = span{ mu * f_k : |mu| <= D - 2, k = 0..16 }  (rows kept, zero rows allowed)
W_D  : W^(0) = rowspace(M_D); W^(i+1) = W^(i) + span{ v_j g : g in a basis of
       W^(i) cap B_{<=D-1}, j = 0..nv-1 }  -- EVERY low-degree basis element
       multiplied at EVERY iteration (no "new rows only" shortcut); stop when
       dim W^(i+1) = dim W^(i).
Systems are selected by an outcome-independent rule fixed before any closure
record was read (see SELECTION).
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from itertools import combinations
from pathlib import Path

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"

# selection rule (fixed before reading closures.jsonl.gz): required three, then
# slot 0 of every other arm, N-CONV unsat at slots 62 and 124 (first S62, first C20)
SELECTION_REQUIRED = ["N-CONV:0:unsat", "@S3-U62@0", "N-CONV:0:sat"]
SELECTION_EXT = ["N-CONVL:0:unsat", "N-CONV17:0:unsat", "N-ELL144:0:unsat", "@NULL-F262@0", "@NULL-AFF62@0",
                 "@S3-S62@62", "@S3-C20@124", "N-CONV:62:unsat", "N-CONV:124:unsat", "@NELL-A20@0"]
RCB_HAND = "N-CONV:0:unsat"


class Ring:
    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        self.pos2mask = []
        self.deg = []
        for d in range(D + 1):
            for m in combinations(range(nv), d):
                mk = 0
                for i in m:
                    mk |= 1 << i
                self.pos2mask.append(mk)
                self.deg.append(d)
        self.mask2pos = {m: p for p, m in enumerate(self.pos2mask)}
        self.C = len(self.pos2mask)

    def poly(self, masks):
        v = 0
        for m in masks:
            v ^= 1 << self.mask2pos[m]
        return v

    def mul_mask(self, g, mk):
        """mk * g (multilinear), g an int over this ring; result must stay in B_{<=D}."""
        out = 0
        x = g
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            out ^= 1 << self.mask2pos[self.pos2mask[b] | mk]
        return out

    def masks_of(self, g):
        out = []
        x = g
        while x:
            b = (x & -x).bit_length() - 1
            x &= x - 1
            out.append(self.pos2mask[b])
        return out


class Echelon:
    def __init__(self):
        self.piv = {}

    def insert(self, v):
        piv = self.piv
        while v:
            L = v.bit_length() - 1
            p = piv.get(L)
            if p is None:
                piv[L] = v
                return True
            v ^= p
        return False

    def dims_by_deg(self, ring):
        out = []
        for d in range(ring.D + 1):
            out.append(sum(1 for L in self.piv if ring.deg[L] <= d))
        return out

    def one(self):
        return 0 in self.piv


def macaulay(ring, eqs_masks):
    """eqs_masks: list of lists of monomial masks (deg <= 2). -> Echelon of M_D."""
    E = Echelon()
    for d in range(ring.D - 2 + 1):
        for mu in combinations(range(ring.nv), d):
            mk = 0
            for i in mu:
                mk |= 1 << i
            for f in eqs_masks:
                row = 0
                for m in f:
                    row ^= 1 << ring.mask2pos[m | mk]
                E.insert(row)
    return E


def w_literal(ring, eqs_masks):
    E = macaulay(ring, eqs_masks)
    dims = [len(E.piv)]
    by_deg_hist = [E.dims_by_deg(ring)]
    one_first = 0 if E.one() else None
    nrows_M = sum(1 for d in range(ring.D - 1) for _ in combinations(range(ring.nv), d)) * len(eqs_masks)
    stack = [nrows_M]
    new_fallen = []
    prev_low = 0
    it = 0
    while True:
        low = [E.piv[L] for L in sorted(E.piv) if ring.deg[L] <= ring.D - 1]
        new_fallen.append(len(low) - prev_low)
        stack.append(len(E.piv) + ring.nv * (len(low) - prev_low))
        prev_low = len(low)
        before = len(E.piv)
        for g in low:                      # EVERY low basis element
            for j in range(ring.nv):       # times EVERY variable
                E.insert(ring.mul_mask(g, 1 << j))
        if len(E.piv) == before:
            break
        it += 1
        dims.append(len(E.piv))
        by_deg_hist.append(E.dims_by_deg(ring))
        if one_first is None and E.one():
            one_first = it
    return {"iterations_to_fixpoint": it, "dims": dims, "final_dim": dims[-1], "one": one_first is not None,
            "one_first_iteration": one_first, "dims_by_deg": E.dims_by_deg(ring),
            "new_fallen_per_iteration_literal": new_fallen, "stack_rows_per_iteration_literal": stack,
            "dims_by_deg_per_iteration": by_deg_hist}


# ---------------------------------------------------------------- systems
MONOS2 = [()] + [(i,) for i in range(18)] + list(combinations(range(18), 2))


def rows_to_masks(E_hex):
    out = []
    for h in E_hex:
        r = int(h, 16)
        f = []
        for col, m in enumerate(MONOS2):
            if (r >> col) & 1:
                mk = 0
                for i in m:
                    mk |= 1 << i
                f.append(mk)
        out.append(f)
    return out


# ---------------------------------------------------------------- rc_b by hand
N = 17
POLY = (1 << 17) | (1 << 3) | 1


def fmul(a, b):
    r = 0
    for i in range(N):
        if (b >> i) & 1:
            r ^= a << i
    for d in range(2 * N - 2, N - 1, -1):
        if (r >> d) & 1:
            r ^= POLY << (d - N)
    return r


def finv(a):
    r, e = 1, (1 << N) - 2
    while e:
        if e & 1:
            r = fmul(r, a)
        a = fmul(a, a)
        e >>= 1
    return r


def ftr(a):
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = fmul(x, x)
    return s


def rcb_by_hand(eqs, xR):
    """object.rc_b (1)-(5) from the text, own code."""
    # (1) left kernel of the 17 x 153 quadratic-column submatrix: vectors c with
    # sum_k c_k * quadpart(f_k) = 0. Own Gaussian elimination on [quad | identity].
    quad = []
    for f in eqs:
        q = frozenset(m for m in f if bin(m).count("1") == 2)
        quad.append(q)
    allq = sorted({m for q in quad for m in q})
    qidx = {m: i for i, m in enumerate(allq)}
    rows = []
    for k, q in enumerate(quad):
        v = 0
        for m in q:
            v |= 1 << qidx[m]
        rows.append((v, 1 << k))
    # column-by-column elimination
    rows = list(rows)
    pivots = []
    work = rows[:]
    for col in range(len(allq)):
        pr = None
        for t, (v, c) in enumerate(work):
            if (v >> col) & 1:
                pr = t
                break
        if pr is None:
            continue
        pv, pc = work.pop(pr)
        pivots.append((pv, pc))
        work = [((v ^ pv, c ^ pc) if (v >> col) & 1 else (v, c)) for (v, c) in work]
    kernel = [c for (v, c) in work if v == 0]
    out = {"kernel_dim": len(kernel)}
    if len(kernel) != 1:
        out["label"] = f"not applicable (kernel dim {len(kernel)})"
        return out, None
    c = kernel[0]
    out["c"] = c
    # (2) ell = sum c_k f_k; C-ELL: c_k = Tr(t^k / x_R^2)
    ell = {}
    for k in range(17):
        if (c >> k) & 1:
            for m in eqs[k]:
                ell[m] = ell.get(m, 0) ^ 1
    ellm = sorted(m for m, p in ell.items() if p)
    assert all(bin(m).count("1") <= 1 for m in ellm), "ell has a quadratic term"
    out["ell_monomials"] = ellm
    lin = sorted(m.bit_length() - 1 for m in ellm if m)
    const = 1 if 0 in ellm else 0
    out["ell_linear_support"] = lin
    out["ell_const"] = const
    if xR is not None:
        ixr2 = finv(fmul(xR, xR))
        tk = 1
        want = 0
        for k in range(17):
            want |= ftr(fmul(tk, ixr2)) << k
            tk = fmul(tk, 2)
        out["c_equals_Tr(t^k/x_R^2)"] = (want == c)
    # (3)
    if not lin:
        out["label"] = "REFUTED-AT-DEGREE-2" if const else "ELL-TRIVIAL"
        return out, None
    # (4) j* least index; v_{j*} := ell + v_{j*}; relabel ascending; reduce multilinearly
    js = lin[0]
    out["j_star"] = js
    out["label"] = "SUBSTITUTED"
    affine = [m for m in ellm if m != (1 << js)]  # ell + v_{j*}: the other terms (masks; 0 = constant)
    keep = [i for i in range(18) if i != js]
    newi = {i: n for n, i in enumerate(keep)}
    sub = []
    for f in eqs:
        acc = {}
        for m in f:
            if (m >> js) & 1:
                rest = m & ~(1 << js)
                for a in affine:
                    mm = rest | a
                    acc[mm] = acc.get(mm, 0) ^ 1
            else:
                acc[m] = acc.get(m, 0) ^ 1
        g = []
        for m, p in acc.items():
            if not p:
                continue
            assert not (m >> js) & 1
            r = 0
            for i in keep:
                if (m >> i) & 1:
                    r |= 1 << newi[i]
            g.append(r)
        assert all(bin(x).count("1") <= 2 for x in g)
        sub.append(sorted(g))
    return out, sub


def main():
    t0 = time.time()
    inst = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(RUN / "instances.jsonl.gz", "rt")}
    by_arm_slot = {}
    for r in inst.values():
        by_arm_slot[(r["arm"], r["slot"], r["role"])] = r["key"]

    def resolve(tok):
        if tok.startswith("@"):
            _, arm, slot = tok.split("@")
            cands = [k for (a, s, _), k in by_arm_slot.items() if a == arm and s == int(slot)]
            assert len(cands) == 1, (tok, cands)
            return cands[0]
        return tok
    full = "--ext" in sys.argv
    sel = [resolve(t) for t in SELECTION_REQUIRED + (SELECTION_EXT if full else [])]
    R4 = Ring(18, 4)
    R3 = Ring(18, 3)
    S4 = Ring(17, 4)
    S3 = Ring(17, 3)
    res = {"task": "TASK-20260926-0f8aec", "joint": "J3", "selection": sel, "systems": {}}
    for key in sel:
        ts = time.time()
        r = inst[key]
        eqs = rows_to_masks(r["E_hex"])
        E4 = macaulay(R4, eqs)
        m4 = {"rank": len(E4.piv), "one": E4.one(), "dims_by_deg": E4.dims_by_deg(R4)}
        d = m4["dims_by_deg"]
        m4.update(P=m4["rank"] - d[3], fallen=d[3], linear_forms=d[1] - d[0])
        E3 = macaulay(R3, eqs)
        m3 = {"rank": len(E3.piv), "one": E3.one(), "dims_by_deg": E3.dims_by_deg(R3)}
        w4 = w_literal(R4, eqs)
        ent = {"arm": r["arm"], "role": r["role"], "slot": r["slot"], "s": r["s"], "M_3_literal": m3,
               "M_4_literal": m4, "W_4_literal": w4}
        rb, sub = rcb_by_hand(eqs, r.get("x_R"))
        ent["rc_b_literal"] = rb
        if sub is not None:
            e3 = macaulay(S3, sub)
            e4 = macaulay(S4, sub)
            ent["R'_3_literal"] = {"rank": len(e3.piv), "one": e3.one(), "dims_by_deg": e3.dims_by_deg(S3)}
            ent["R'_4_literal"] = {"rank": len(e4.piv), "one": e4.one(), "dims_by_deg": e4.dims_by_deg(S4)}
            ent["W'_4_literal"] = w_literal(S4, sub)
            ent["T4_literal"] = {"final_dim_W4_minus_final_dim_Wp4": w4["final_dim"] - ent["W'_4_literal"]["final_dim"],
                                 "one_equal": w4["one"] == ent["W'_4_literal"]["one"]}
            ent["T5_applicable_literal"] = ent["R'_4_literal"]["dims_by_deg"][3] == ent["R'_3_literal"]["rank"]
            if key == RCB_HAND:
                ent["substituted_system_by_hand"] = sub
        ent["seconds"] = round(time.time() - ts, 1)
        res["systems"][key] = ent
        print(key, json.dumps({k: v for k, v in ent.items() if k not in ("substituted_system_by_hand",)})[:600],
              flush=True)
    res["seconds"] = round(time.time() - t0, 1)
    import resource
    res["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    out = OUTDIR / ("j3-literal-ext.json" if full else "j3-literal.json")
    json.dump(res, open(out, "w"), indent=1)
    print("WROTE", out, res["seconds"])


if __name__ == "__main__":
    main()
