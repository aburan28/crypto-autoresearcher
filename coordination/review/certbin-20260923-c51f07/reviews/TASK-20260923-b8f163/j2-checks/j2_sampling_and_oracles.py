#!/usr/bin/env python3
"""TASK-20260923-b8f163, joint J2: sampling-layer audit and a third oracle.

(A) SAMPLING-LAYER REGENERATION. The curve, points, reference scans, test
    targets, planted targets and null-family draws are regenerated from the 13
    frozen seeds with the validator's OWN curve/field code and numpy's
    Generator(PCG64(seed)) (numpy 2.4.6, as the run), following the trial
    plan's interpretations I-1..I-10 as written. The regenerated instance
    INPUTS are compared with the archive. This is not a trial: no Macaulay
    matrix is built and no elimination is run. No driver phase is run.
(B) THIRD ORACLE on every archived instance:
    - curve-algebra families: direct vectorised evaluation of
      S_3(x_1, x_2, x_R) on the whole 512 x 512 grid V x V (not root-finding
      like oracle A, and not the descended equations like oracle B);
    - null families: an exhaustive evaluation of the 17 equations at all 2^18
      assignments by a mod-2 matrix product (not oracle B's bit-sliced XOR).
    Solution SETS are compared with the archived `sols`.

Uses impl/ nothing. Reads committed bytes only. Zero trials; no RUN-id.
Run with: python3 -B j2_sampling_and_oracles.py
"""
import gzip
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "j1-constructions"))
import j1_spec_literal as J  # noqa: E402  (validator's own module: field, descent)

RUN = J.RUN
T0 = time.time()
LOG = []


def log(m):
    s = f"[{time.time() - T0:8.1f}s] {m}"
    print(s, flush=True)
    LOG.append(s)


# ----------------------------------------------------------------------------
# field helpers (validator's own; tables from j1_spec_literal)
ORDER = (1 << 17) - 1
EXPT, LOGT = J.EXPT, J.LOGT
tmul = J.tmul


def tinv(a):
    return EXPT[(ORDER - LOGT[a]) % ORDER]


def tdiv(a, b):
    return 0 if a == 0 else EXPT[(LOGT[a] - LOGT[b]) % ORDER]


TRMASK = 0
for _j in range(17):
    if J.gtrace(1 << _j):
        TRMASK |= 1 << _j


def tr(a):
    return bin(a & TRMASK).count("1") & 1


def half_trace(c):
    s, x = 0, c
    for _ in range(9):
        s ^= x
        x = tmul(x, x)
        x = tmul(x, x)
    return s


def sqrt(a):
    x = a
    for _ in range(16):
        x = tmul(x, x)
    return x


# ----------------------------------------------------------------------------
# curve Y^2 + XY = X^3 + A X^2 + B (validator's own group law); O = None
class Curve:
    def __init__(self, A, B):
        self.A, self.B = A, B

    def neg(self, P):
        return None if P is None else (P[0], P[0] ^ P[1])

    def dbl(self, P):
        if P is None or P[0] == 0:
            return None
        x, y = P
        lam = x ^ tdiv(y, x)
        x3 = tmul(lam, lam) ^ lam ^ self.A
        y3 = tmul(x, x) ^ tmul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        if P[0] == Q[0]:
            if Q[1] == P[0] ^ P[1]:
                return None
            return self.dbl(P)
        lam = tdiv(P[1] ^ Q[1], P[0] ^ Q[0])
        x3 = tmul(lam, lam) ^ lam ^ P[0] ^ Q[0] ^ self.A
        y3 = tmul(lam, P[0] ^ x3) ^ x3 ^ P[1]
        return (x3, y3)

    def mul(self, k, P):
        R, Q = None, P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.dbl(Q)
            k >>= 1
        return R

    def on(self, P):
        if P is None:
            return True
        x, y = P
        return tmul(y, y) ^ tmul(x, y) == tmul(tmul(x, x), x) ^ tmul(self.A, tmul(x, x)) ^ self.B

    def lift(self, x):
        if x == 0:
            return (0, sqrt(self.B))
        c = x ^ self.A ^ tdiv(self.B, tmul(x, x))
        if tr(c):
            return None
        return (x, tmul(x, half_trace(c)))

    def order(self):
        good = 0
        for x in range(1, 1 << 17):
            if tr(x ^ self.A ^ tdiv(self.B, tmul(x, x))) == 0:
                good += 1
        return 2 + 2 * good


def isprime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def gen(seed):
    return np.random.Generator(np.random.PCG64(seed))


# ----------------------------------------------------------------------------
# third oracle, curve algebra: direct S_3 over the V x V grid (vectorised)
NPEXP = np.array(EXPT, dtype=np.int64)
NPLOG = np.array(LOGT, dtype=np.int64)
X1G, X2G = np.meshgrid(np.arange(512, dtype=np.int64), np.arange(512, dtype=np.int64), indexing="ij")
X1G, X2G = X1G.reshape(-1), X2G.reshape(-1)


def vmul(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    r = NPEXP[(NPLOG[a] + NPLOG[b]) % ORDER]
    return np.where((a == 0) | (b == 0), 0, r)


def oracle3_curve(B, xR):
    x3 = np.full_like(X1G, xR)
    e = vmul(X1G, X2G) ^ vmul(X1G, x3) ^ vmul(X2G, x3)
    S = vmul(e, e) ^ vmul(vmul(X1G, X2G), x3) ^ B
    z = np.flatnonzero(S == 0)
    return sorted(int(X1G[i] | (X2G[i] << 9)) for i in z)


# third oracle, null families: exhaustive via a mod-2 matrix product
EQ_MONS_OWN = sorted(J.monomials_upto(2), key=lambda m: (len(m), m))   # 'mu order' (I-7)
assert len(EQ_MONS_OWN) == 172
_U = np.arange(1 << 18, dtype=np.int64)
MONVAL = np.ones((172, 1 << 18), dtype=np.float32)
for _j, _m in enumerate(EQ_MONS_OWN):
    for _i in _m:
        MONVAL[_j] *= ((_U >> _i) & 1).astype(np.float32)


def oracle3_matrix(E):
    vals = (E.astype(np.float32) @ MONVAL)
    bad = (np.mod(vals, 2.0) != 0).any(axis=0)
    return [int(u) for u in np.flatnonzero(~bad)]


def hex_to_E(hx):
    E = np.zeros((17, 172), dtype=np.uint8)
    for k, h in enumerate(hx):
        v = int(h, 16)
        for j in range(172):
            E[k, j] = (v >> j) & 1
    return E


# ----------------------------------------------------------------------------
def main():
    res = {"task": "TASK-20260923-b8f163", "joint": "J2", "part_A_sampling": {}, "part_B_third_oracle": {}}
    A_ = res["part_A_sampling"]
    P1 = json.load(gzip.open(os.path.join(RUN, "checkpoint", "p1-instances.json.gz"), "rt"))
    plan = json.load(open(os.path.join(J.EXP, "trial-plan-v1.json")))
    S = plan["seeds"]
    cj = json.load(open(os.path.join(RUN, "curve.json")))

    # ---- I-1 curve
    g = gen(S["S_curve"])
    rej = 0
    while True:
        A = int(g.integers(0, 1 << 17))
        B = int(g.integers(0, 1 << 17))
        if B == 0:
            rej += 1
            continue
        E = Curve(A, B)
        n = E.order()
        h = 2 if (n % 2 == 0 and isprime(n // 2)) else (4 if (n % 4 == 0 and isprime(n // 4)) else None)
        if h is None:
            rej += 1
            continue
        break
    q = n // h
    A_["curve"] = {"A": A, "B": B, "order": n, "h": h, "q": q, "rejected": rej,
                   "equal_curve_json": (A, B, n, h, q, rej) == (cj["A"], cj["B"], cj["order"], cj["h"], cj["q"], cj["draws_rejected"])}
    log(f"curve {A_['curve']}")

    # ---- I-2 points
    g = gen(S["S_pts"])
    while True:
        x = int(g.integers(0, 1 << 17))
        pt = E.lift(x)
        if pt is None:
            continue
        Pp = E.mul(h, pt)
        if Pp is None:
            continue
        break
    kQ = int(g.integers(1, q))
    Qp = E.mul(kQ, Pp)
    A_["points"] = {"P": list(Pp), "Q": list(Qp), "k_Q": kQ, "qP_is_O": E.mul(q, Pp) is None,
                    "equal_curve_json": (list(Pp), list(Qp), kQ) == (cj["P"], cj["Q"], cj["k_Q"])}
    log(f"points {A_['points']}")

    class Stream:
        def __init__(self, seed):
            self.g = gen(seed)
            self.draws = 0
            self.rejO = 0

        def next(self):
            while True:
                a = int(self.g.integers(0, q))
                b = int(self.g.integers(0, q))
                self.draws += 1
                R = E.add(E.mul(a, Pp), E.mul(b, Qp))
                if R is None:
                    self.rejO += 1
                    continue
                return a, b, R[0]

    def scan(cands, classify, maxd=500):
        out, nu, ns = [], 0, 0
        for c in cands:
            if c["status"] == "classified":
                s = classify(c)
                c["s_own"] = s
                if s == 0 and nu < 3:
                    nu += 1
                    c["sel"] = f"U{nu}"
                elif s >= 1 and ns < 2:
                    ns += 1
                    c["sel"] = f"S{ns}"
                else:
                    c["sel"] = None
            else:
                c["sel"] = None
            out.append(c)
            if nu == 3 and ns == 2:
                break
            if c["draw"] >= maxd:
                break
        return out

    def curve_cands(seed):
        st = Stream(seed)
        seen = set()
        while True:
            a, b, xR = st.next()
            c = {"draw": st.draws, "a": a, "b": b, "x_R": xR}
            if xR in seen:
                c["status"] = "rejected_duplicate"
            elif xR < 512:
                seen.add(xR)
                c["status"] = "rejected_degenerate_reference"
            else:
                seen.add(xR)
                c["status"] = "classified"
            yield c

    def cmp_scan(mine, arch, keys):
        if len(mine) != len(arch):
            return {"equal": False, "len_mine": len(mine), "len_arch": len(arch)}
        bad = []
        for i, (m, a) in enumerate(zip(mine, arch)):
            for k in keys:
                mk = {"sel": "selected_as"}.get(k, k)
                av = a.get(mk)
                mv = m.get(k)
                if k == "s_own":
                    av = a.get("s")
                if mv != av:
                    bad.append((i, k, mv, av))
        return {"equal": not bad, "n": len(mine), "mismatches": bad[:10]}

    cls_curve = lambda c: len(oracle3_curve(B, c["x_R"]))  # noqa: E731

    # ---- I-3/I-5 F-S3 references
    fs3_scan = scan(curve_cands(S["S_ref"]), cls_curve)
    A_["F-S3_ref_scan"] = cmp_scan(fs3_scan, P1["F-S3"]["ref_scan"], ["draw", "a", "b", "x_R", "status", "s_own", "sel"])
    ref_x = {c["x_R"] for c in fs3_scan if c["sel"]}
    log(f"F-S3 ref scan: {A_['F-S3_ref_scan']}")

    # ---- I-4 F-S3 targets
    st = Stream(S["S_test"])
    seen, tg, rj = set(), [], {"duplicate": 0, "reference_collision": 0}
    while len(tg) < 1000:
        a, b, xR = st.next()
        if xR in ref_x:
            rj["reference_collision"] += 1
            continue
        if xR in seen:
            rj["duplicate"] += 1
            continue
        seen.add(xR)
        tg.append({"idx": len(tg) + 1, "draw": st.draws, "a": a, "b": b, "x_R": xR, "degenerate": xR < 512})
    rj["R_is_O"] = st.rejO
    rj["draws"] = st.draws
    arch = P1["F-S3"]["targets"]
    A_["F-S3_targets"] = {
        "sequence_equal": [(t["idx"], t["draw"], t["a"], t["b"], t["x_R"], t["degenerate"]) for t in tg]
        == [(t["idx"], t["draw"], t["a"], t["b"], t["x_R"], t["degenerate"]) for t in arch],
        "rejections_mine": rj, "rejections_archived": P1["rejections"]["S_test"],
        "rejections_equal": rj == P1["rejections"]["S_test"],
        "degenerate_count": sum(t["degenerate"] for t in tg)}
    # the targets file carries the same x_R per idx
    recs = {}
    with gzip.open(os.path.join(RUN, "targets-F-S3.jsonl.gz"), "rt") as fh:
        for line in fh:
            r = json.loads(line)
            recs.setdefault(r["idx"], set()).add(r["x_R"])
    A_["F-S3_targets"]["targets_file_x_R_equal"] = all(recs[t["idx"]] == {t["x_R"]} for t in tg) and len(recs) == 1000
    log(f"F-S3 targets: {A_['F-S3_targets']}")

    # ---- I-9 F-PLANT
    FV = []
    for x in range(512):
        P = E.lift(x)
        if P is None:
            continue
        if x == 0:
            FV.append(P)
        else:
            FV.extend([P, E.neg(P)])
    FV.sort()
    g = gen(S["S_plant"])
    s3x = seen | ref_x
    pr = {"P1_eq_pm_P2": 0, "z_in_V": 0, "duplicate": 0, "collides_F-S3": 0}
    pl, pseen, draws = [], set(), 0
    while len(pl) < 200:
        i1 = int(g.integers(0, len(FV)))
        i2 = int(g.integers(0, len(FV)))
        draws += 1
        P1_, P2_ = FV[i1], FV[i2]
        if P1_ == P2_ or P1_ == E.neg(P2_):
            pr["P1_eq_pm_P2"] += 1
            continue
        z = E.add(P1_, P2_)[0]
        if z < 512:
            pr["z_in_V"] += 1
            continue
        if z in pseen:
            pr["duplicate"] += 1
            continue
        if z in s3x:
            pr["collides_F-S3"] += 1
            continue
        pseen.add(z)
        pl.append((len(pl) + 1, draws, i1, i2, z))
    pr["draws"] = draws
    archp = P1["F-PLANT"]["targets"]
    A_["F-PLANT"] = {"factor_base_size": len(FV), "equal_archived_size": len(FV) == P1["F-PLANT"]["factor_base_size"],
                     "sequence_equal": pl == [(t["idx"], t["draw"], t["i1"], t["i2"], t["x_R"]) for t in archp],
                     "rejections_equal": pr == P1["rejections"]["S_plant"], "rejections_mine": pr}
    log(f"F-PLANT: {A_['F-PLANT']}")

    # ---- I-10 F-RANDX
    def randx_cands(seed):
        g = gen(seed)
        seen_, d = set(), 0
        while True:
            xR = int(g.integers(0, 1 << 17))
            d += 1
            c = {"draw": d, "x_R": xR}
            if xR in seen_:
                c["status"] = "rejected_duplicate"
            elif xR < 512:
                seen_.add(xR)
                c["status"] = "rejected_degenerate_reference"
            else:
                seen_.add(xR)
                c["status"] = "classified"
            yield c

    rx_scan = scan(randx_cands(S["S_randx_ref"]), cls_curve)
    A_["F-RANDX_ref_scan"] = cmp_scan(rx_scan, P1["F-RANDX"]["ref_scan"], ["draw", "x_R", "status", "s_own", "sel"])
    rx = {c["x_R"] for c in rx_scan if c["sel"]}
    g = gen(S["S_randx_test"])
    seen2, tx, rr, draws = set(), [], {"duplicate": 0, "reference_collision": 0}, 0
    while len(tx) < 1000:
        xR = int(g.integers(0, 1 << 17))
        draws += 1
        if xR in rx:
            rr["reference_collision"] += 1
            continue
        if xR in seen2:
            rr["duplicate"] += 1
            continue
        seen2.add(xR)
        tx.append((len(tx) + 1, draws, xR, xR < 512))
    rr["draws"] = draws
    A_["F-RANDX_targets"] = {"sequence_equal": tx == [(t["idx"], t["draw"], t["x_R"], t["degenerate"]) for t in P1["F-RANDX"]["targets"]],
                             "rejections_equal": rr == P1["rejections"]["S_randx_test"], "rejections_mine": rr,
                             "degenerate_count": sum(t[3] for t in tx),
                             "x_R_shared_with_F-S3_targets": sorted(t[0] for t in tx if t[2] in seen)}
    log(f"F-RANDX: scan {A_['F-RANDX_ref_scan']} targets {A_['F-RANDX_targets']}")

    # ---- I-7 F-AFF draws, I-6 F-AFF reference rescans
    f0 = J.equations_from_coef(J.descent_mobius(B, 0))
    E0 = np.zeros((17, 172), dtype=np.uint8)
    col = {m: j for j, m in enumerate(EQ_MONS_OWN)}
    for k in range(17):
        for m in f0[k]:
            E0[k, col[m]] = 1
    Ejs = []
    for jj in range(17):
        fx = J.equations_from_coef(J.descent_mobius(B, 1 << jj))
        Ex = np.zeros((17, 172), dtype=np.uint8)
        for k in range(17):
            for m in fx[k]:
                Ex[k, col[m]] = 1
        Ejs.append(Ex ^ E0)
    for d in (1, 2, 3):
        fam = f"F-AFF-{d}"
        g = gen(S[f"S_nullAff_draw{d}"])

        def one(Mx):
            pos = np.flatnonzero(Mx.reshape(-1))
            out = np.zeros(17 * 172, dtype=np.uint8)
            out[pos] = g.integers(0, 2, size=pos.size).astype(np.uint8)
            return out.reshape(17, 172)
        A0 = one(E0)
        Aj = [one(x) for x in Ejs]
        eqA0 = np.array_equal(A0, hex_to_E(P1[fam]["A0_hex"]))
        eqAj = all(np.array_equal(Aj[j], hex_to_E(P1[fam]["Aj_hex"][j])) for j in range(17))

        def comb(r, A0=A0, Aj=Aj):
            Ex = A0.copy()
            for j in range(17):
                if (r >> j) & 1:
                    Ex ^= Aj[j]
            return Ex
        sc = scan(curve_cands(S["S_ref"]), lambda c, comb=comb: len(oracle3_matrix(comb(c["x_R"]))))
        A_[fam] = {"A0_equal": eqA0, "Aj_equal": eqAj,
                   "ref_scan": cmp_scan(sc, P1[fam]["ref_scan"], ["draw", "a", "b", "x_R", "status", "s_own", "sel"]),
                   "targets_x_R_equal_F-S3": [t["x_R"] for t in P1[fam]["targets"]] == [t["x_R"] for t in tg]}
        res.setdefault("_aff", {})[fam] = (A0, Aj)
        log(f"{fam}: {A_[fam]}")

    # ---- I-8 F-NULLF2
    U = E0.astype(bool).copy()
    for x in Ejs:
        U |= x.astype(bool)
    Upos = np.flatnonzero(U.reshape(-1))

    def nf2(g):
        Mx = np.zeros(17 * 172, dtype=np.uint8)
        Mx[Upos] = g.integers(0, 2, size=Upos.size).astype(np.uint8)
        return Mx.reshape(17, 172)
    g = gen(S["S_nullF2_ref"])
    seen_h, sc, d = set(), [], 0
    nu = ns = 0

    def nf2_cands():
        nonlocal d
        while True:
            Ex = nf2(g)
            d += 1
            key = Ex.tobytes()
            c = {"draw": d, "E": Ex}
            if key in seen_h:
                c["status"] = "rejected_duplicate"
            else:
                seen_h.add(key)
                c["status"] = "classified"
            yield c
    sc = scan(nf2_cands(), lambda c: len(oracle3_matrix(c["E"])))
    arch = P1["F-NULLF2"]["ref_scan"]
    nf_ok = len(sc) == len(arch) and all(np.array_equal(m["E"], hex_to_E(a["E_hex"])) and m["status"] == a["status"]
                                         and m.get("s_own") == a.get("s") and m["sel"] == a.get("selected_as")
                                         for m, a in zip(sc, arch))
    refkeys = {m["E"].tobytes() for m in sc if m["sel"]}
    g = gen(S["S_nullF2_test"])
    seen_t, tn, rn, draws = set(), [], {"duplicate": 0, "reference_collision": 0}, 0
    while len(tn) < 1000:
        Ex = nf2(g)
        draws += 1
        kb = Ex.tobytes()
        if kb in refkeys:
            rn["reference_collision"] += 1
            continue
        if kb in seen_t:
            rn["duplicate"] += 1
            continue
        seen_t.add(kb)
        tn.append(Ex)
    rn["draws"] = draws
    tn_ok = all(np.array_equal(Ex, hex_to_E(t["E_hex"])) for Ex, t in zip(tn, P1["F-NULLF2"]["targets"]))
    A_["F-NULLF2"] = {"union_support_size": int(Upos.size), "ref_scan_equal": nf_ok, "targets_E_equal": tn_ok,
                      "rejections_equal": rn == P1["rejections"]["S_nullF2_test"], "rejections_mine": rn}
    log(f"F-NULLF2: {A_['F-NULLF2']}")

    # ---- (B) third oracle on every archived instance
    B_ = res["part_B_third_oracle"]
    t1 = time.time()
    for fam in ("F-S3", "F-PLANT", "F-RANDX"):
        insts = [c for c in P1[fam].get("ref_scan", []) if c.get("status") == "classified"] + P1[fam]["targets"]
        n_eq = sum(1 for c in insts if oracle3_curve(B, c["x_R"]) == sorted(c["sols"]))
        B_[fam] = {"instances": len(insts), "solution_sets_equal": n_eq}
        log(f"oracle3 {fam}: {B_[fam]} ({time.time() - t1:.0f}s)")
    for d in (1, 2, 3):
        fam = f"F-AFF-{d}"
        A0, Aj = res["_aff"][fam]
        insts = [c for c in P1[fam]["ref_scan"] if c.get("status") == "classified"] + P1[fam]["targets"]
        n_eq = 0
        for c in insts:
            Ex = A0.copy()
            for j in range(17):
                if (c["x_R"] >> j) & 1:
                    Ex ^= Aj[j]
            n_eq += oracle3_matrix(Ex) == sorted(c["sols"])
        B_[fam] = {"instances": len(insts), "solution_sets_equal": n_eq}
        log(f"oracle3 {fam}: {B_[fam]} ({time.time() - t1:.0f}s)")
    insts = [c for c in P1["F-NULLF2"]["ref_scan"] if c.get("status") == "classified"] + P1["F-NULLF2"]["targets"]
    n_eq = sum(1 for c in insts if oracle3_matrix(hex_to_E(c["E_hex"])) == sorted(c["sols"]))
    B_["F-NULLF2"] = {"instances": len(insts), "solution_sets_equal": n_eq}
    log(f"oracle3 F-NULLF2: {B_['F-NULLF2']} ({time.time() - t1:.0f}s)")
    # archived per-target s equals archived sols length (targets files vs checkpoint)
    res.pop("_aff", None)
    res["wall_seconds"] = round(time.time() - T0, 1)
    res["log"] = LOG
    json.dump(res, open(os.path.join(HERE, "j2_sampling_and_oracles.json"), "w"), indent=1,
              default=lambda o: bool(o) if isinstance(o, np.bool_) else int(o))
    log("done")


if __name__ == "__main__":
    main()
