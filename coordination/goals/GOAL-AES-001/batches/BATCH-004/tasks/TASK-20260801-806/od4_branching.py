#!/usr/bin/env python3
# =====================================================================
# od4_branching.py -- TASK-20260801-806, GOAL-AES-001, BATCH-004
#
# WHAT THIS IS
#   Exact, exhaustive computation of the BRANCHING FACTOR B forced on an
#   F-LINEAR per-super-box-word projection pi : F^4 -> F^4/K across one AES
#   super-box interface Phi = ARK . MC . SR, together with the sibling-null
#   controls for the structural ingredients that the bound names.
#
#   This is derivation support. It is NOT a cryptanalytic measurement, NOT a
#   distinguisher, NOT a key recovery, and it asserts NOTHING about AES
#   security at any round count. The GF(2^4) and GF(2^2) computations are
#   ANALOGUES: their readings are NOT evidence about GF(2^8) and certainly
#   not about AES.
#
# ENVIRONMENT NOTE (recorded because it changed the plan): numpy is NOT
#   installed in this environment. Every phase below is pure Python, and the
#   scale of the from-definition brute force was reduced accordingly. The
#   reduction, and every check that consequently did NOT run, is recorded in
#   the output under `checks_not_run`.
#
# PROVENANCE / INFERENCE STANZA (protocol-amendment-GOAL-AES-001-004 Part B,
# class SOURCE_CODE: this comment-block stanza AND an artifact_provenance
# entry in the covering manifest od4_results.json are both required):
#   policy                 : executor-implementation
#   requested_policy       : executor-implementation
#   resolved_model_id      : claude-opus-5
#   fallback_used          : true
#   fallback_reason        : orchestration/model-policies.yaml routes
#                            executor-implementation to a GPT-5.6-family policy
#                            alias that Claude Code cannot resolve; per
#                            CLAUDE.md's model policy note this harness's
#                            subagents run `model: inherit`. Requested policy
#                            and actual resolved model are both recorded and
#                            neither is silently substituted.
#   reasoning_effort       : null
#   degraded_allowed       : false
#   degraded_requirements  : []
#   model_verified         : false
#   model_verified_reason  : `python3 -m orchestration.adapter doctor --probe`
#                            was NOT run in this task; the resolved model
#                            identifier is unprobed configuration taken from
#                            the runtime's self-report.
#   independent_session    : false
#   standing_basis         : inference-amendment commit
#                            0137a051eb5828789eb267fa83c8278086578d4c
#   covering_manifest      : od4_results.json
#
# SUPERSEDES: nothing. This file is new. No BATCH-001, BATCH-002 or BATCH-003
# artifact is modified, re-run into, or deleted by it.
#
# DETERMINISM: every phase is a deterministic enumeration in a fixed order.
# The only pseudo-random construction is the positive control matrix CTRL-POS,
# drawn from random.Random(SEED_CTRL_POS); the seed is recorded in the output.
# =====================================================================
#
# =====================================================================
# PRE-REGISTERED PREDICTIONS -- WRITTEN BEFORE ANY PHASE WAS EXECUTED
# No prediction below was altered after a measurement was seen. Each measured
# value is placed beside its prediction in od4_results.json under
# `preregistration`.
#
#   PRED-1  Every entry of the AES MixColumns matrix M is nonzero.
#   PRED-2  Every square minor of M is nonzero, i.e. M is MDS.
#   PRED-3  For every S subset {0,1,2,3}, with W_S the F-span of the columns
#           {m_i : i in S} and F^S the coordinate subspace supported on S,
#           dim(W_S cap F^S) = max(0, 2|S| - 4).
#   PRED-4  i -> (j+i) mod 4 is a bijection of {0,1,2,3} for each fixed output
#           word index j, so the four coordinates of the pre-MixColumns vector
#           of one output word come from four DIFFERENT input words.
#   PRED-5  For F-linear pi with kernel K, the per-word branching is
#           B(K) = q^(|S| - dim(W_S cap K)),  S = {i : proj_i(K) != 0};
#           and this closed form agrees with brute-force enumeration in every
#           case where enumeration is performed, with zero discrepancies.
#   PRED-6  min over K not in {0, F^4} of B(K) = q. In GF(2^8) that is 256;
#           in the GF(2^4) analogue 16; in the GF(2^2) analogue 4. The minimum
#           does not depend on dim K.
#   PRED-7  CONTROL CTRL-NULL-1 (a MixColumns-shaped matrix with a 2x2 ZERO
#           BLOCK, negating "every entry is nonzero" in its strongest form)
#           admits B = 1 for a lossy non-constant K: the bound FAILS on it.
#   PRED-8  SIBLING NULL CTRL-NULL-2 (exactly ONE zero entry -- the SAME named
#           ingredient negated DIFFERENTLY -- invertible, all other entries
#           nonzero) is predicted to STILL read min B = q, i.e. NOT to void
#           the bound. If that holds, CTRL-NULL-1 does NOT isolate "every entry
#           is nonzero"; it isolates the strictly stronger "M has no zero
#           block", and the report must say so. Recorded before measurement
#           precisely because the opposite outcome is the convenient one.
#   PRED-9  CONTROL CTRL-NULL-3 (all entries nonzero, invertible, NOT MDS) is
#           predicted to STILL read min B = q: the MDS property is predicted
#           NOT to be load bearing for the MINIMUM, only for the per-case value
#           at |S| = 2.
#  PRED-10  CONTROL CTRL-POS (deterministically seeded random invertible matrix
#           with all entries nonzero) reads min B = q.
#  PRED-11  The JOINT branching over all four output words of one interface is
#           q^(dim of the image of the F-linear map K^4 -> (F^4/K)^4), and for
#           the minimising kernels it is STRICTLY LESS than B^4 -- the four
#           per-word branchings are NOT independent. Recorded because the cost
#           model in the report depends on it and the convenient assumption is
#           the opposite one.
# =====================================================================

import json
import random
import sys
import time
from itertools import combinations, product

SEED_CTRL_POS = 20260801806
TIME_CAP_P5_SECONDS = 260.0

# ---------------------------------------------------------------------
# Finite field GF(2^n).
# ---------------------------------------------------------------------


class GF:
    def __init__(self, n, modulus, name):
        self.n = n
        self.q = 1 << n
        self.modulus = modulus
        self.name = name
        self.mt = [[self._mul_slow(a, b) for b in range(self.q)]
                   for a in range(self.q)]

    def _mul_slow(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a & self.q:
                a ^= self.modulus
        return r

    def mul(self, a, b):
        return self.mt[a][b]

    def inv(self, a):
        assert a != 0
        for b in range(1, self.q):
            if self.mt[a][b] == 1:
                return b
        raise AssertionError


GF256 = GF(8, 0x11B, "GF(2^8), modulus 0x11B (AES)")
GF16 = GF(4, 0x13, "GF(2^4), modulus 0x13 (x^4+x+1) -- campaign analogue")
GF4 = GF(2, 0x7, "GF(2^2), modulus 0x7 (x^2+x+1) -- smaller analogue")

M_AES = [[0x02, 0x03, 0x01, 0x01],
         [0x01, 0x02, 0x03, 0x01],
         [0x01, 0x01, 0x02, 0x03],
         [0x03, 0x01, 0x01, 0x02]]

# Same circulant shape and same entry symbols in the analogues. ANALOGUE ONLY.
M_ANA16 = [row[:] for row in M_AES]
M_ANA4 = [row[:] for row in M_AES]


# ---------------------------------------------------------------------
# Linear algebra over GF.
# ---------------------------------------------------------------------

def rref(F, rows):
    mat = [list(r) for r in rows]
    if not mat:
        return [], []
    ncols = len(mat[0])
    piv = []
    r = 0
    for c in range(ncols):
        sel = None
        for i in range(r, len(mat)):
            if mat[i][c] != 0:
                sel = i
                break
        if sel is None:
            continue
        mat[r], mat[sel] = mat[sel], mat[r]
        iv = F.inv(mat[r][c])
        mat[r] = [F.mt[iv][x] for x in mat[r]]
        for i in range(len(mat)):
            if i != r and mat[i][c] != 0:
                f = mat[i][c]
                mat[i] = [mat[i][k] ^ F.mt[f][mat[r][k]] for k in range(ncols)]
        piv.append(c)
        r += 1
        if r == len(mat):
            break
    return [row[:] for row in mat[:r]], piv


def rank(F, rows):
    if not rows:
        return 0
    b, _ = rref(F, rows)
    return len(b)


def dim_intersection(F, A, B):
    if not A or not B:
        return 0
    return rank(F, A) + rank(F, B) - rank(F, list(A) + list(B))


def matvec(F, Mx, v):
    return [F.mt[Mx[r][0]][v[0]] ^ F.mt[Mx[r][1]][v[1]] ^
            F.mt[Mx[r][2]][v[2]] ^ F.mt[Mx[r][3]][v[3]] for r in range(4)]


def det(F, sub):
    k = len(sub)
    mat = [list(r) for r in sub]
    d = 1
    for c in range(k):
        sel = None
        for i in range(c, k):
            if mat[i][c] != 0:
                sel = i
                break
        if sel is None:
            return 0
        if sel != c:
            mat[c], mat[sel] = mat[sel], mat[c]
        d = F.mt[d][mat[c][c]]
        iv = F.inv(mat[c][c])
        mat[c] = [F.mt[iv][x] for x in mat[c]]
        for i in range(c + 1, k):
            if mat[i][c] != 0:
                f = mat[i][c]
                mat[i] = [mat[i][j] ^ F.mt[f][mat[c][j]] for j in range(k)]
    return d


def minors_report(F, Mx):
    out = {}
    for k in (1, 2, 3, 4):
        cnt = nz = 0
        zeros = []
        for rs in combinations(range(4), k):
            for cs in combinations(range(4), k):
                sub = [[Mx[r][c] for c in cs] for r in rs]
                cnt += 1
                if det(F, sub) != 0:
                    nz += 1
                else:
                    zeros.append({"rows": list(rs), "cols": list(cs)})
        out[k] = {"minors": cnt, "nonzero": nz, "zero_minors": zeros}
    return out


def columns(Mx):
    return [[Mx[r][c] for r in range(4)] for c in range(4)]


def all_subspaces(F, d):
    """Every d-dimensional subspace of F^4 exactly once, as its RREF basis."""
    if d == 0:
        yield []
        return
    q = F.q
    for piv in combinations(range(4), d):
        free = [(r, c) for r in range(d) for c in range(4)
                if c > piv[r] and c not in piv]
        for vals in product(range(q), repeat=len(free)):
            basis = [[0] * 4 for _ in range(d)]
            for r in range(d):
                basis[r][piv[r]] = 1
            for (r, c), v in zip(free, vals):
                basis[r][c] = v
            yield basis


# ---------------------------------------------------------------------
# THE CLOSED FORM.
#   S    = { i : proj_i(K) != 0 }
#   W_S  = F-span of { m_i : i in S }
#   B(K) = q ^ ( |S| - dim(W_S cap K) )
# ---------------------------------------------------------------------

def support_set(basis):
    S = set()
    for b in basis:
        for i in range(4):
            if b[i] != 0:
                S.add(i)
    return sorted(S)


def branching_closed_form(F, Mx, basis, cols=None):
    S = support_set(basis)
    if not S:
        return 1, S, 0
    if cols is None:
        cols = columns(Mx)
    W = [cols[i] for i in S]
    di = dim_intersection(F, W, basis)
    return F.q ** (len(S) - di), S, di


def branching_by_enumeration(F, Mx, basis, limit=1 << 20):
    """Independent recomputation: explicitly enumerate the reachable output
    perturbation set M . (prod_i proj_i(K)) and count distinct pi-images."""
    S = support_set(basis)
    s = len(S)
    if F.q ** s > limit:
        return None
    red, piv = rref(F, basis)
    seen = set()
    for vals in product(range(F.q), repeat=s):
        y = [0, 0, 0, 0]
        for idx, i in enumerate(S):
            y[i] = vals[idx]
        w = matvec(F, Mx, y)
        for row, p in zip(red, piv):
            c = w[p]
            if c:
                w = [w[k] ^ F.mt[c][row[k]] for k in range(4)]
        seen.add(tuple(w))
    return len(seen)


# ---------------------------------------------------------------------
# FROM-DEFINITION brute force. Perturbs the four INPUT WORDS by arbitrary
# elements of K, applies the actual ShiftRows index map and the actual
# MixColumns, and counts distinct pi-images per output word and jointly.
# Uses NO structural shortcut: the perturbation tuple ranges over K^4.
# ---------------------------------------------------------------------

def branching_from_definition(F, Mx, basis):
    q = F.q
    red, piv = rref(F, basis)
    d = len(red)
    # all elements of K, in a fixed order
    Kelems = []
    for coeffs in product(range(q), repeat=d):
        v = [0, 0, 0, 0]
        for c, row in zip(coeffs, red):
            if c:
                for k in range(4):
                    v[k] ^= F.mt[c][row[k]]
        Kelems.append(v)
    nk = len(Kelems)
    # reduction table over all packed vectors of F^4
    def pack(v):
        return ((v[0] * q + v[1]) * q + v[2]) * q + v[3]

    red_table = [0] * (q ** 4)
    for a in range(q):
        for b in range(q):
            for c in range(q):
                for e in range(q):
                    w = [a, b, c, e]
                    for row, p in zip(red, piv):
                        cf = w[p]
                        if cf:
                            w = [w[k] ^ F.mt[cf][row[k]] for k in range(4)]
                    red_table[pack([a, b, c, e])] = pack(w)
    # contribution table: contrib[t_index_of_K_elem][i] = packed(k_i * m_i)
    cols = columns(Mx)
    contrib = []
    for kv in Kelems:
        row = []
        for i in range(4):
            c = kv[i]
            row.append(pack([F.mt[c][cols[i][r]] for r in range(4)]))
        contrib.append(row)
    per_word = [set() for _ in range(4)]
    joint = set()
    for a in range(nk):
        ca = contrib[a]
        for b in range(nk):
            cb = contrib[b]
            for c in range(nk):
                cc = contrib[c]
                for e in range(nk):
                    ce = contrib[e]
                    # input word t contributes k^{(t)}_{(t-j) mod 4} * m_{(t-j) mod 4}
                    key = []
                    for j in range(4):
                        w = (ca[(0 - j) % 4] ^ cb[(1 - j) % 4] ^
                             cc[(2 - j) % 4] ^ ce[(3 - j) % 4])
                        rw = red_table[w]
                        per_word[j].add(rw)
                        key.append(rw)
                    joint.add(tuple(key))
    return [len(s) for s in per_word], len(joint)


# ---------------------------------------------------------------------
# JOINT four-word branching, exact, by linear algebra.
# ---------------------------------------------------------------------

def joint_branching(F, Mx, basis):
    d = len(basis)
    if d == 0:
        return 1
    red, piv = rref(F, basis)
    gens = []
    for t in range(4):
        for bi in range(d):
            img = []
            for j in range(4):
                y = [0, 0, 0, 0]
                for i in range(4):
                    if (j + i) % 4 == t:
                        y[i] = red[bi][i]
                w = matvec(F, Mx, y)
                for row, p in zip(red, piv):
                    c = w[p]
                    if c:
                        w = [w[k] ^ F.mt[c][row[k]] for k in range(4)]
                img.extend(w)
            gens.append(img)
    return F.q ** rank(F, gens)


# ---------------------------------------------------------------------
# Exhaustive minimisation over ALL subspaces.
# ---------------------------------------------------------------------

def exhaustive_minimum(F, Mx, cross_check_limit=1 << 8, with_joint=False):
    cols = columns(Mx)
    res = {"per_dim": {}, "discrepancies": [], "subspaces_examined": 0,
           "cross_checked": 0}
    gmin = None
    gwit = None
    for d in range(0, 5):
        best = None
        bwit = None
        hist = {}
        jhist = {}
        n = 0
        for basis in all_subspaces(F, d):
            n += 1
            B, S, di = branching_closed_form(F, Mx, basis, cols)
            hist[B] = hist.get(B, 0) + 1
            if best is None or B < best:
                best = B
                bwit = {"basis": basis, "S": S, "dim_W_S_cap_K": di, "B": B}
            if with_joint:
                J = joint_branching(F, Mx, basis)
                jhist[J] = jhist.get(J, 0) + 1
            if F.q ** len(S) <= cross_check_limit:
                Be = branching_by_enumeration(F, Mx, basis)
                res["cross_checked"] += 1
                if Be is not None and Be != B:
                    res["discrepancies"].append(
                        {"basis": basis, "closed_form": B, "enumerated": Be})
        res["subspaces_examined"] += n
        entry = {"subspaces": n, "min_B": best, "min_witness": bwit,
                 "B_histogram": {str(k): v for k, v in sorted(hist.items())}}
        if with_joint:
            entry["joint_histogram"] = {str(k): v for k, v in sorted(jhist.items())}
            entry["min_joint"] = min(jhist) if jhist else None
        res["per_dim"][str(d)] = entry
        if d not in (0, 4) and (gmin is None or best < gmin):
            gmin, gwit = best, bwit
    res["min_B_over_lossy_nonconstant"] = gmin
    res["min_B_witness"] = gwit
    return res


# ---------------------------------------------------------------------
# Controls.
# ---------------------------------------------------------------------

def build_controls(F):
    ctrls = {}
    ctrls["CTRL-NULL-1_zero_block"] = {
        "matrix": [[0x02, 0x03, 0x00, 0x00],
                   [0x01, 0x02, 0x00, 0x00],
                   [0x00, 0x00, 0x02, 0x03],
                   [0x00, 0x00, 0x01, 0x02]],
        "negates": "every entry of M is nonzero -- STRONGEST form: a 2x2 zero block",
        "isolation_target": "the absence of a zero block in M",
    }
    m2 = [row[:] for row in M_AES]
    m2[3][0] = 0x00
    ctrls["CTRL-NULL-2_single_zero_entry_SIBLING"] = {
        "matrix": m2,
        "negates": "every entry of M is nonzero -- WEAKEST form: exactly one zero entry",
        "isolation_target": "SIBLING NULL for CTRL-NULL-1: negates the SAME named "
                            "ingredient differently, to test whether CTRL-NULL-1 "
                            "isolates that ingredient or something stronger",
    }
    found = None
    for r in range(4):
        for c in range(4):
            for val in range(1, F.q):
                m3 = [row[:] for row in M_AES]
                m3[r][c] = val % F.q
                if any(x == 0 or x >= F.q for row in m3 for x in row):
                    continue
                if det(F, m3) == 0:
                    continue
                mn = minors_report(F, m3)
                if mn[2]["zero_minors"] or mn[3]["zero_minors"]:
                    found = (m3, r, c, val,
                             (mn[2]["zero_minors"] + mn[3]["zero_minors"])[0])
                    break
            if found:
                break
        if found:
            break
    if found:
        ctrls["CTRL-NULL-3_not_MDS_all_entries_nonzero"] = {
            "matrix": found[0],
            "negates": "M is MDS (a proper minor vanishes) while every entry stays nonzero",
            "isolation_target": "the MDS property of M, with the nonzero-entry "
                                "ingredient held fixed",
            "edit": {"row": found[1], "col": found[2], "new_value": found[3]},
            "example_zero_minor": found[4],
        }
    else:
        ctrls["CTRL-NULL-3_not_MDS_all_entries_nonzero"] = {
            "matrix": None,
            "negates": "M is MDS while every entry stays nonzero",
            "note": "NO single-entry edit of M over this field produced an "
                    "invertible, all-entries-nonzero, non-MDS matrix.",
        }
    rng = random.Random(SEED_CTRL_POS)
    mp = None
    for _ in range(100000):
        cand = [[rng.randrange(1, F.q) for _ in range(4)] for _ in range(4)]
        if det(F, cand) != 0:
            mp = cand
            break
    ctrls["CTRL-POS_random_invertible_all_nonzero"] = {
        "matrix": mp,
        "negates": "nothing -- POSITIVE control",
        "isolation_target": "n/a (positive control)",
        "seed": SEED_CTRL_POS,
    }
    return ctrls


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main():
    t0 = time.time()
    out = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "python": sys.version, "numpy_available": False,
           "seeds": {"SEED_CTRL_POS": SEED_CTRL_POS},
           "phases": {}, "timings_s": {}, "checks_not_run": []}

    # ---- PHASE 1: GF(2^8) structural ingredients ----------------------
    t = time.time()
    cols = columns(M_AES)
    p1 = {"field": GF256.name, "M_AES": M_AES}
    p1["PRED-1_all_entries_nonzero"] = all(x != 0 for row in M_AES for x in row)
    mn = minors_report(GF256, M_AES)
    p1["PRED-2_minors"] = {str(k): v for k, v in mn.items()}
    p1["PRED-2_is_MDS"] = all(not mn[k]["zero_minors"] for k in mn)
    d3 = {}
    for r in range(5):
        for S in combinations(range(4), r):
            W = [cols[i] for i in S]
            FS = [[1 if k == i else 0 for k in range(4)] for i in S]
            dv = dim_intersection(GF256, W, FS) if S else 0
            d3["".join(map(str, S)) or "empty"] = {
                "s": len(S), "dim_W_cap_F_S": dv,
                "predicted_max_0_2s_minus_4": max(0, 2 * len(S) - 4)}
    p1["PRED-3_dim_W_S_cap_F_S"] = d3
    p1["PRED-3_holds"] = all(v["dim_W_cap_F_S"] == v["predicted_max_0_2s_minus_4"]
                             for v in d3.values())
    bij = {str(j): {"image": sorted(((j + i) % 4) for i in range(4))}
           for j in range(4)}
    for j in bij:
        bij[j]["is_bijection"] = bij[j]["image"] == [0, 1, 2, 3]
    p1["PRED-4_shiftrows_index_map"] = bij
    p1["PRED-4_holds"] = all(v["is_bijection"] for v in bij.values())
    out["phases"]["P1_gf256_structural"] = p1
    out["timings_s"]["P1"] = round(time.time() - t, 3)

    # ---- PHASE 2: GF(2^8) witness kernels -----------------------------
    t = time.time()
    p2 = {"witnesses": []}
    wks = [
        {"label": "d=1, K=span(e_0)", "basis": [[1, 0, 0, 0]]},
        {"label": "d=1, K=span(m_0)", "basis": [cols[0]]},
        {"label": "d=1, K=span(01,01,00,00)", "basis": [[1, 1, 0, 0]]},
        {"label": "d=2, K=span(e_0,e_1)", "basis": [[1, 0, 0, 0], [0, 1, 0, 0]]},
        {"label": "d=3, K=span(e_0,e_1,e_2)",
         "basis": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]},
    ]
    # tight witness at s=3, d=2:  K = W_S cap F^S for S = {0,1,2}
    S = (0, 1, 2)
    inter_vecs = []
    m30, m31, m32 = M_AES[3][S[0]], M_AES[3][S[1]], M_AES[3][S[2]]
    assert m32 != 0
    inv32 = GF256.inv(m32)
    for c0, c1 in [(1, 0), (0, 1)]:
        c2 = GF256.mt[inv32][GF256.mt[m30][c0] ^ GF256.mt[m31][c1]]
        inter_vecs.append([GF256.mt[c0][cols[S[0]][r]] ^
                           GF256.mt[c1][cols[S[1]][r]] ^
                           GF256.mt[c2][cols[S[2]][r]] for r in range(4)])
    wks.append({"label": "d=2, K = W_S cap F^S for S={0,1,2}  (TIGHT WITNESS)",
                "basis": inter_vecs})
    for wk in wks:
        basis, _ = rref(GF256, wk["basis"])
        B, Sset, di = branching_closed_form(GF256, M_AES, basis, cols)
        Be = branching_by_enumeration(GF256, M_AES, basis)
        J = joint_branching(GF256, M_AES, basis)
        d = len(basis)
        p2["witnesses"].append({
            "label": wk["label"], "basis_rref": basis, "dim_K": d,
            "entropy_loss_L_bits": 8 * d,
            "log2_image_size_of_pi_bits": 8 * (4 - d),
            "S": Sset, "dim_W_S_cap_K": di,
            "B_closed_form": B, "log2_B": B.bit_length() - 1,
            "B_by_enumeration": Be,
            "enumeration_agrees": (Be is None or Be == B),
            "enumeration_skipped_reason":
                None if Be is not None else "q^|S| exceeds the 2^20 limit",
            "joint_4word_branching": J, "log2_joint": J.bit_length() - 1,
            "B_to_the_4": B ** 4,
            "joint_strictly_less_than_B4": J < B ** 4,
        })
    out["phases"]["P2_gf256_witnesses"] = p2
    out["timings_s"]["P2"] = round(time.time() - t, 3)

    # ---- PHASE 3: GF(2^8) exhaustive over the 16 subsets S ------------
    t = time.time()
    p3 = {"note": "For each of the 15 nonempty subsets S the row records the "
                  "bound ingredients over GF(2^8) exhaustively. The "
                  "minimisation is proved in the report from these rows.",
          "rows": []}
    for r in range(1, 5):
        for Ss in combinations(range(4), r):
            W = [cols[i] for i in Ss]
            FS = [[1 if k == i else 0 for k in range(4)] for i in Ss]
            dwf = dim_intersection(GF256, W, FS)
            s = len(Ss)
            best = min(s - min(dwf, dd) for dd in range(1, s + 1))
            p3["rows"].append({"S": list(Ss), "s": s, "dim_W_S": rank(GF256, W),
                               "dim_W_S_cap_F_S": dwf,
                               "min_exponent_over_dim_K": best,
                               "min_B_for_this_S": GF256.q ** best})
    p3["min_over_all_S"] = min(r["min_B_for_this_S"] for r in p3["rows"])
    out["phases"]["P3_gf256_per_S"] = p3
    out["timings_s"]["P3"] = round(time.time() - t, 3)

    # ---- PHASE 4: GF(2^4) ANALOGUE, exhaustive over ALL subspaces -----
    t = time.time()
    mn4 = minors_report(GF16, M_ANA16)
    p4 = {"ANALOGUE_WARNING":
          "GF(2^4) is a SCALED-DOWN ANALOGUE. Its readings are NOT evidence "
          "about GF(2^8) and are certainly not evidence about AES.",
          "field": GF16.name, "M_analogue": M_ANA16,
          "all_entries_nonzero": all(x != 0 for row in M_ANA16 for x in row),
          "is_MDS": all(not mn4[k]["zero_minors"] for k in mn4),
          "invertible": det(GF16, M_ANA16) != 0}
    p4["exhaustive"] = exhaustive_minimum(GF16, M_ANA16, cross_check_limit=1 << 8,
                                          with_joint=True)
    out["phases"]["P4_analogue16_exhaustive"] = p4
    out["timings_s"]["P4"] = round(time.time() - t, 3)

    # ---- PHASE 5: GF(2^2) ANALOGUE, exhaustive + from-definition ------
    t = time.time()
    mn2 = minors_report(GF4, M_ANA4)
    p5 = {"ANALOGUE_WARNING":
          "GF(2^2) is a SECOND, SMALLER analogue, used because numpy is absent "
          "and the from-definition brute force is pure Python. Its readings are "
          "NOT evidence about GF(2^8) and not about AES.",
          "field": GF4.name, "M_analogue": M_ANA4,
          "all_entries_nonzero": all(x != 0 for row in M_ANA4 for x in row),
          "is_MDS": all(not mn2[k]["zero_minors"] for k in mn2),
          "invertible": det(GF4, M_ANA4) != 0,
          "zero_minors": {str(k): mn2[k]["zero_minors"] for k in mn2}}
    if p5["invertible"]:
        p5["exhaustive"] = exhaustive_minimum(GF4, M_ANA4,
                                              cross_check_limit=1 << 12,
                                              with_joint=True)
        fd = {"description":
              "FROM-DEFINITION brute force: the perturbation tuple ranges over "
              "K^4 (all four input words perturbed independently by arbitrary "
              "elements of K), the actual ShiftRows index map and the actual "
              "MixColumns are applied, and distinct pi-images are counted per "
              "output word and jointly. NO structural shortcut is used.",
              "kernels_checked": 0, "discrepancies": [], "samples": [],
              "exhaustive_for_dims": [], "capped": False}
        for d in (1, 2):
            done = 0
            total = sum(1 for _ in all_subspaces(GF4, d))
            for basis in all_subspaces(GF4, d):
                if time.time() - t > TIME_CAP_P5_SECONDS:
                    fd["capped"] = True
                    break
                pw, jt = branching_from_definition(GF4, M_ANA4, basis)
                B, Sset, di = branching_closed_form(GF4, M_ANA4, basis)
                J = joint_branching(GF4, M_ANA4, basis)
                done += 1
                fd["kernels_checked"] += 1
                if any(x != B for x in pw):
                    fd["discrepancies"].append(
                        {"basis": basis, "closed_form_B": B,
                         "from_definition_per_word": pw})
                if jt != J:
                    fd["discrepancies"].append(
                        {"basis": basis, "closed_form_joint": J,
                         "from_definition_joint": jt})
                if len(fd["samples"]) < 6:
                    fd["samples"].append(
                        {"basis": basis, "S": Sset, "B": B,
                         "from_definition_per_word": pw,
                         "B_to_the_4": B ** 4, "joint": jt})
            if done == total and not fd["capped"]:
                fd["exhaustive_for_dims"].append(d)
            else:
                out["checks_not_run"].append(
                    {"check": "from-definition brute force, GF(2^2), dim K = %d" % d,
                     "completed": done, "of": total,
                     "reason": "time cap %ss reached; pure Python, numpy absent"
                               % TIME_CAP_P5_SECONDS})
        fd["all_agree"] = (len(fd["discrepancies"]) == 0)
        p5["from_definition"] = fd
    out["checks_not_run"].append(
        {"check": "from-definition brute force at dim K = 3 in GF(2^2), and at "
                  "any dim in GF(2^4) or GF(2^8)",
         "reason": "NOT RUN. The perturbation tuple space is q^(4 dim K): "
                   "4^12 = 16.7M per kernel at dim 3 over GF(2^2), 16^4 = 65536 "
                   "per kernel over 4369 kernels at dim 1 over GF(2^4), and "
                   "256^4 per kernel over GF(2^8). Pure Python without numpy "
                   "puts all three outside this task's 1600 s budget. The "
                   "closed form is instead cross-checked at those scales by the "
                   "independent enumeration of M.(prod_i proj_i(K)) in "
                   "branching_by_enumeration()."})
    out["phases"]["P5_analogue4_exhaustive_and_from_definition"] = p5
    out["timings_s"]["P5"] = round(time.time() - t, 3)

    # ---- PHASE 6: controls / sibling nulls ----------------------------
    t = time.time()
    p6 = {"ANALOGUE_WARNING": "Controls are run exhaustively over all subspaces "
                              "in BOTH analogues.",
          "controls": {}}
    for name, spec in build_controls(GF16).items():
        mx = spec["matrix"]
        e = {k: spec[k] for k in spec if k != "matrix"}
        e["matrix"] = mx
        if mx is None:
            p6["controls"][name] = e
            continue
        for tag, Fx in (("GF(2^4)", GF16), ("GF(2^2)", GF4)):
            mxf = [[v % Fx.q for v in row] for row in mx]
            sub = {"matrix_in_field": mxf,
                   "invertible": det(Fx, mxf) != 0,
                   "all_entries_nonzero": all(v != 0 for r in mxf for v in r)}
            mnx = minors_report(Fx, mxf)
            sub["is_MDS"] = all(not mnx[k]["zero_minors"] for k in mnx)
            if sub["invertible"]:
                ex = exhaustive_minimum(Fx, mxf, cross_check_limit=1 << 8)
                sub["min_B_over_lossy_nonconstant"] = ex["min_B_over_lossy_nonconstant"]
                sub["min_witness"] = ex["min_B_witness"]
                sub["per_dim_min_B"] = {d: ex["per_dim"][d]["min_B"]
                                        for d in ex["per_dim"]}
                sub["cross_check_discrepancies"] = len(ex["discrepancies"])
            else:
                sub["min_B_over_lossy_nonconstant"] = None
                sub["skipped"] = "matrix not invertible over this field; a " \
                                 "MixColumns analogue must be invertible"
            e[tag] = sub
        p6["controls"][name] = e
    out["phases"]["P6_controls"] = p6
    out["timings_s"]["P6"] = round(time.time() - t, 3)

    out["timings_s"]["total"] = round(time.time() - t0, 3)
    out["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(out, sys.stdout, indent=1, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
