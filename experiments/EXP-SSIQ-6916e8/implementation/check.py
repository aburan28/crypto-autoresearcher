#!/usr/bin/env python3
"""EXP-SSIQ-6916e8 independent checker (frozen spec v1, S7).

Reads ONLY raw-result.json and recomputes, with code independent of
driver.py (nothing is imported from it):

  * every Gram matrix from the recorded basis and the recorded PARI
    structure constants, via the Cayley-Hamilton route
    Nrd(x) = (Trd(x)^2 - Trd(x^2)) / 2, Trd(y) = tr(L_y)/2
    (driver.py uses sqrt(det L_x) and PARI uses algnorm);
    arm A2 via Nrd(x) = scalar part of x * conj(x) in (1, i, j, k);
  * every determinant with sympy Matrix.det(method="bareiss");
  * R, R_sub, indices [O : I] from the recorded bases, n(I) as a gcd;
  * C-ALG order/ideal checks, control ratios, all counts;
  * the outcome code, applying the frozen criteria mechanically.

Exits 0 iff every recomputed value, flag, count and the outcome code
agree with what raw-result.json records; otherwise exits 1 and lists
every disagreement. Exact arithmetic only.
"""

import json
import math
import sys
from fractions import Fraction as Q

import sympy

M_LIST = [2, 3, 4, 5, 6, 8, 12, 30, 97, 1024]
problems = []


def bad(msg):
    problems.append(msg)


def q(s):
    return Q(s)


def qs(x):
    x = Q(x)
    return str(x.numerator) if x.denominator == 1 else "%d/%d" % (x.numerator, x.denominator)


def sdet(M):
    if not M:
        return Q(1)
    d = sympy.Matrix([[sympy.Rational(qs(v)) for v in row] for row in M]).det(method="bareiss")
    d = sympy.Rational(d)
    return Q(int(d.p), int(d.q))


def rows_of(cols):
    return [[cols[j][i] for j in range(len(cols))] for i in range(len(cols[0]))]


def solve_coords(basis_cols):
    """returns function y -> coordinates of y in the basis (sympy exact inverse)."""
    Minv = sympy.Matrix([[sympy.Rational(qs(v)) for v in row] for row in rows_of(basis_cols)]).inv()
    Mi = [[Q(int(sympy.Rational(Minv[i, j]).p), int(sympy.Rational(Minv[i, j]).q)) for j in range(Minv.cols)]
          for i in range(Minv.rows)]
    return lambda y: [sum(Mi[i][j] * y[j] for j in range(len(y))) for i in range(len(Mi))]


def integral(v):
    return all(Q(x).denominator == 1 for x in v)


class CH:
    """Cayley-Hamilton instrument on recorded PARI structure constants."""

    def __init__(self, multable, one):
        self.MT = [[[q(v) for v in row] for row in m] for m in multable]
        self.one = [q(v) for v in one]
        self.trMT = [sum(m[i][i] for i in range(4)) for m in self.MT]

    def mul(self, x, y):
        return [sum(x[i] * y[j] * self.MT[i][r][j] for i in range(4) for j in range(4) if x[i] and y[j])
                for r in range(4)]

    def trd(self, x):
        return sum(x[i] * self.trMT[i] for i in range(4)) / 2

    def nrd(self, x):
        t = self.trd(x)
        return (t * t - self.trd(self.mul(x, x))) / 2

    def conj(self, x):
        t = self.trd(x)
        return [t * o - xi for o, xi in zip(self.one, x)]


class IJK:
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.one = [Q(1), Q(0), Q(0), Q(0)]

    def mul(self, x, y):
        a, b = self.a, self.b
        # table of products of 1, i, j, k: (coef, index)
        T = {(0, 0): (1, 0), (0, 1): (1, 1), (0, 2): (1, 2), (0, 3): (1, 3),
             (1, 0): (1, 1), (1, 1): (a, 0), (1, 2): (1, 3), (1, 3): (a, 2),
             (2, 0): (1, 2), (2, 1): (-1, 3), (2, 2): (b, 0), (2, 3): (-b, 1),
             (3, 0): (1, 3), (3, 1): (-a, 2), (3, 2): (b, 1), (3, 3): (-a * b, 0)}
        z = [Q(0)] * 4
        for i in range(4):
            for j in range(4):
                c, k = T[(i, j)]
                z[k] += c * x[i] * y[j]
        return z

    def conj(self, x):
        return [x[0], -x[1], -x[2], -x[3]]

    def nrd(self, x):
        return self.mul(x, self.conj(x))[0]

    def trd(self, x):
        return 2 * x[0]


def gram(alg, basis, scale=Q(1)):
    n = len(basis)
    qv = [alg.nrd(v) for v in basis]
    A = [[Q(0)] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = qv[i]
        for j in range(i + 1, n):
            A[i][j] = A[j][i] = (alg.nrd([u + v for u, v in zip(basis[i], basis[j])]) - qv[i] - qv[j]) / 2
    return [[v / scale for v in row] for row in A]


def gcdq(vals):
    g = Q(0)
    for v in vals:
        v = Q(v)
        if v == 0:
            continue
        if g == 0:
            g = abs(v)
        else:
            g = Q(math.gcd(g.numerator * v.denominator, v.numerator * g.denominator), g.denominator * v.denominator)
    return g


def order_ok(alg, basis):
    co = solve_coords(basis)
    return (integral(co(alg.one)) and all(integral(co(alg.mul(x, y))) for x in basis for y in basis)
            and all(Q(alg.nrd(x)).denominator == 1 for x in basis) and all(Q(alg.trd(x)).denominator == 1 for x in basis))


def mat_of(strs):
    return [[q(v) for v in row] for row in strs]


def main():
    path = sys.argv[1]
    raw = json.load(open(path))
    L = raw["lattices"]
    byp = {}
    for x in L:
        byp.setdefault(x["p"], {})[x["name"]] = x
    rec_valid = {}
    my = {}   # id -> dict(valid, R, rkey, index_ok ...)
    ctrl_my = {}
    for pe in raw["primes"]:
        ps = pe["p"]
        p = int(ps)
        st = raw["prime_status"].get(ps, {})
        lat = byp.get(ps, {})
        # prime-level checks
        prime_ok = True
        if "multable_stage1" in st:
            fin = [int(v) for v in st["calg_a"]["ramified_finite"]]
            hil = st["calg_a"]["hilbert"]
            ram_ok = fin == [p] and st["calg_a"]["ramified_infinite_count"] == 1 and \
                all((int(v) == -1) == (k in (ps, "inf")) for k, v in hil.items()) and int(hil.get("inf", 1)) == -1
            mt = st["multable_stage1"]
            prods = st["algmul_products_stage1"]
            sc_ok = all([mt[i][r][j] for r in range(4)] == prods[4 * i + j] for i in range(4) for j in range(4))
            nb_ok = q(st["calg_b"]["nrd_one"]) == 1 and q(st["calg_b"]["nrd_two"]) == 4
            if not nb_ok:
                bad("%s: C-ALG (b) failed but run continued" % ps)
            prime_ok = ram_ok and sc_ok
            s2_same = st.get("multable_stage2") == st.get("multable_stage1")
        # ---- A2
        a2 = lat.get("A2")
        pres = pe["presentation"]
        if a2 is None:
            bad("%s: A2 missing" % ps)
        else:
            alg = IJK(Q(pres["a"]), Q(pres["b"]))
            basis = [[q(v) for v in c] for c in a2["basis"]]
            G = gram(alg, basis)
            if G != mat_of(a2["gram"]):
                bad("%s:A2 gram differs" % ps)
            d = sdet(G)
            cross = a2.get("det_pari") is not None and q(a2["det_pari"]) == d and q(a2["det_python"]) == d
            valid = order_ok(alg, basis) and cross
            my[a2["id"]] = {"valid": valid, "val": d * 16 / (p * p) if cross else None, "arm": "A2",
                            "calg": order_ok(alg, basis), "cross": cross}
        if "multable_stage1" not in st or "multable_stage2" not in st:
            for nm, x in lat.items():
                if nm != "A2":
                    if not x.get("missing"):
                        bad("%s: lattice %s present without stage data" % (ps, nm))
                    my[x["id"]] = {"valid": False, "val": None, "arm": x["arm"], "missing": True}
            ctrl_my[ps] = None
            continue
        alg1 = CH(st["multable_stage1"], st["one_stage1"])
        alg2 = CH(st["multable_stage2"], st["one_stage2"])

        def recheck(x, alg, extra_calg, parent_cols=None, want_index=False, scale=None):
            basis = [[q(v) for v in c] for c in x["basis"]]
            s = q(x["form_scale"]) if scale is None else scale
            Gu = gram(alg, basis)
            G = [[v / s for v in row] for row in Gu]
            gram_ok = G == mat_of(x["gram"]) and ("gram_nrd_unscaled" not in x or Gu == mat_of(x["gram_nrd_unscaled"]))
            if "gram_regrep_unscaled" in x:
                gram_ok = gram_ok and Gu == mat_of(x["gram_regrep_unscaled"])
            d = sdet(G)
            cross = gram_ok and q(x["det_pari"]) == d and q(x["det_python"]) == d
            n = gcdq([Gu[i][i] for i in range(len(Gu))] + [2 * Gu[i][j] for i in range(len(Gu)) for j in range(i + 1, len(Gu))])
            out = {"basis": basis, "G": G, "Gu": Gu, "det": d, "detu": sdet(Gu), "n": n, "cross": cross}
            if parent_cols is not None:
                co = solve_coords(parent_cols)
                out["index"] = abs(sdet(rows_of([co(v) for v in basis])))
            if want_index:
                cross = cross and q(x["index_pari"]) == out["index"] and q(x["n_pari"]) == n
                out["cross"] = cross
            out["calg"] = prime_ok and s2_same and all(extra_calg(basis, out))
            out["valid"] = out["calg"] and cross
            return out

        # ---- A1 (stage-1 structure constants)
        a1 = lat["A1"]
        r1 = recheck(a1, alg1, lambda b, o: [order_ok(alg1, b)])
        r1["calg"] = prime_ok and order_ok(alg1, r1["basis"])  # A1 does not depend on stage 2
        r1["valid"] = r1["calg"] and r1["cross"]
        my[a1["id"]] = {"valid": r1["valid"], "calg": r1["calg"], "cross": r1["cross"], "val": r1["det"] * 16 / (p * p) if r1["cross"] else None, "arm": "A1"}
        # ---- base
        base = lat["base"]
        rb = recheck(base, alg2, lambda b, o: [order_ok(alg2, b)])
        B = rb["basis"]
        coB = solve_coords(B)
        my[base["id"]] = {"valid": rb["valid"], "calg": rb["calg"], "cross": rb["cross"], "val": None, "arm": "base"}
        # ---- C-TRD
        T = [[alg2.trd(alg2.mul(x, alg2.conj(y))) for y in B] for x in B]
        c = next(cc for cc in raw["controls"] if cc["p"] == ps)
        dT = sdet(T)
        trd_cross = T == mat_of(c["C-TRD"]["trace_form"]) and q(c["C-TRD"]["det_pari"]) == dT and rb["cross"]
        cm = {"C-TRD": {"pass": trd_cross and dT / rb["det"] == 16 and dT * 16 / (p * p) != 1,
                        "ratio_ok": dT / rb["det"] == 16, "cross": trd_cross, "R_ne_1": dT * 16 / (p * p) != 1}}
        # ---- C-NONMAX
        nm_ = lat["C-NONMAX"]
        rn = recheck(nm_, alg2, lambda b, o: [order_ok(alg2, b)], parent_cols=B)
        TN = [[alg2.trd(alg2.mul(x, alg2.conj(y))) for y in rn["basis"]] for x in rn["basis"]]
        dTN = sdet(TN)
        my[nm_["id"]] = {"valid": rn["valid"], "calg": rn["calg"], "cross": rn["cross"], "val": None, "arm": "C-NONMAX"}
        idx_ok = rn["index"] == 8 and q(c["C-NONMAX"]["index_pari"]) == 8
        cm["C-NONMAX"] = {"index_ok": idx_ok, "ratio_ok": rn["det"] / rb["det"] == 64, "valid": rn["valid"],
                          "pass": idx_ok and rn["det"] / rb["det"] == 64 and dTN != p * p and
                          TN == mat_of(c["C-NONMAX"]["trace_form"]) and rn["det"] * 16 / (p * p) != 1 and rn["valid"]}
        # ---- A3
        P = lat["A3"]

        def calgP(b, o):
            co = solve_coords(b)
            return [all(integral(coB(x)) for x in b),
                    all(integral(co(alg2.mul(ob, x))) for ob in B for x in b),
                    all(integral(co(alg2.mul(x, ob))) for ob in B for x in b),
                    all((alg2.nrd(x) / p).denominator == 1 for x in b), rb["calg"]]
        rP = recheck(P, alg2, calgP, parent_cols=B, want_index=True)
        my[P["id"]] = {"valid": rP["valid"], "calg": rP["calg"], "cross": rP["cross"], "val": rP["det"] * 16 / (p * p) if rP["cross"] else None, "arm": "A3",
                       "index_eq": rP["index"] == rP["n"] ** 2}
        PB = rP["basis"]
        # ---- C-NEAR
        near_ok = True
        for nm, par, exp in (("C-NEAR-O0", B, Q(p * p, 4)), ("C-NEAR-P0", PB, Q(p, 4))):
            x = lat[nm]
            cop = solve_coords(par)
            rr = recheck(x, alg2, lambda b, o: [all(alg2.trd(v) == 0 for v in b), all(integral(cop(v)) for v in b)])
            my[x["id"]] = {"valid": rr["valid"], "calg": rr["calg"], "cross": rr["cross"], "val": None, "arm": nm}
            near_ok = near_ok and rr["det"] == exp and rr["valid"]
        cm["C-NEAR"] = {"pass": near_ok}
        # ---- A4 / A5 / C-NOSCALE
        cm["C-NOSCALE"] = []
        parents = {0: (B, Q(1), my[base["id"]]["valid"]), 1: (PB, Q(p), rP["valid"])}
        for k in range(1, 21):
            x = lat["A4_%d" % k]
            if x.get("missing"):
                my[x["id"]] = {"valid": False, "val": None, "arm": "A4", "missing": True}
                my[lat["A5_%d" % k]["id"]] = {"valid": False, "val": None, "arm": "A5", "missing": True}
                cm["C-NOSCALE"].append({"pass": False, "missing": True})
                continue

            def calgI(b, o):
                co = solve_coords(b)
                return [all(integral(coB(v)) for v in b), all(integral(co(alg2.mul(ob, v))) for ob in B for v in b),
                        rb["calg"]]
            basisI = [[q(v) for v in cc] for cc in x["basis"]]
            nI = gcdq([v for v in [gram(alg2, basisI)[i][i] for i in range(4)]] +
                      [2 * gram(alg2, basisI)[i][j] for i in range(4) for j in range(i + 1, 4)])
            if q(x["form_scale"]) != nI:
                bad("%s: form scale %s != recomputed n(I) %s" % (x["id"], x["form_scale"], qs(nI)))
            rI = recheck(x, alg2, calgI, parent_cols=B, want_index=True, scale=nI)
            my[x["id"]] = {"valid": rI["valid"], "calg": rI["calg"], "cross": rI["cross"], "val": rI["det"] * 16 / (p * p) if rI["cross"] else None, "arm": "A4",
                           "index_eq": rI["index"] == rI["n"] ** 2, "normhit": rI["n"] == q(x["target_norm"])}
            cross_u = rI["cross"] and q(x["det_pari_unscaled"]) == rI["detu"] and q(x["det_python_unscaled"]) == rI["detu"]
            cm["C-NOSCALE"].append({"pass": rI["detu"] / rI["det"] == nI ** 4 and rI["detu"] * 16 / (p * p) != 1 and cross_u,
                                    "ratio_ok": rI["detu"] / rI["det"] == nI ** 4, "cross": cross_u})
            parents[k + 1] = (rI["basis"], nI, rI["valid"])
            y = lat["A5_%d" % k]
            if y.get("missing"):
                my[y["id"]] = {"valid": False, "val": None, "arm": "A5", "missing": True}
                continue
            coI = solve_coords(rI["basis"])
            rO = recheck(y, alg2, lambda b, o: [order_ok(alg2, b),
                                                all(integral(coI(alg2.mul(v, w))) for v in rI["basis"] for w in b),
                                                rI["calg"]])
            my[y["id"]] = {"valid": rO["valid"], "calg": rO["calg"], "cross": rO["cross"], "val": rO["det"] * 16 / (p * p) if rO["cross"] else None, "arm": "A5"}
        # ---- A6
        for k in range(22):
            x = lat["A6_%d" % k]
            m = M_LIST[k % 10]
            if x.get("missing") or k not in parents:
                my[x["id"]] = {"valid": False, "val": None, "arm": "A6", "missing": True}
                continue
            Mb, sc, pvalid = parents[k]
            Hrows = mat_of(x["H"])
            upper = all(Hrows[i][j] == 0 for i in range(4) for j in range(i)) and all(Hrows[i][i] > 0 for i in range(4)) \
                and all(0 <= Hrows[i][j] < Hrows[j][j] for j in range(4) for i in range(j))
            r6 = recheck(x, alg2, lambda b, o: [o["index"] == m, abs(sdet(Hrows)) == m, upper, pvalid],
                         parent_cols=Mb, scale=sc)
            mm = abs(sdet(Hrows))
            my[x["id"]] = {"valid": r6["valid"], "calg": r6["calg"], "cross": r6["cross"], "val": r6["det"] * 16 / (mm * mm * p * p) if r6["cross"] else None,
                           "arm": "A6"}
        ctrl_my[ps] = cm

    # ---- compare per-lattice validity and R with the record
    for x in L:
        m_ = my.get(x["id"])
        if m_ is None:
            bad("%s: not rechecked" % x["id"])
            continue
        if bool(x.get("valid")) != bool(m_["valid"]):
            bad("%s: validity recorded %s, recomputed %s" % (x["id"], x.get("valid"), m_["valid"]))
        rkey = "R_sub" if x["arm"] == "A6" else "R"
        if m_.get("val") is not None and x["arm"] in ("A1", "A2", "A3", "A4", "A5", "A6"):
            if x.get(rkey) is None or q(x[rkey]) != m_["val"]:
                bad("%s: %s recorded %s, recomputed %s" % (x["id"], rkey, x.get(rkey), qs(m_["val"])))
        if "index_eq" in m_ and x.get("index_equals_n_squared") is not None and x["index_equals_n_squared"] != m_["index_eq"]:
            bad("%s: index==n^2 flag differs" % x["id"])

    # ---- recount
    arms = ["A1", "A2", "A3", "A4", "A5"]
    cnt = {}
    fnorm, fsub, dstd, idxmis = [], [], [], []
    for x in L:
        m_ = my.get(x["id"], {})
        a = x["arm"]
        if a not in arms + ["A6"]:
            continue
        c = cnt.setdefault(a, {"planned": 0, "valid": 0, "R_eq_1": 0, "R_ne_1": 0})
        c["planned"] += 1
        if not m_.get("valid"):
            if a == "A2" and not m_.get("calg", True):
                dstd.append(x["id"])
            continue
        c["valid"] += 1
        if m_["val"] == 1:
            c["R_eq_1"] += 1
        else:
            c["R_ne_1"] += 1
            (fsub if a == "A6" else dstd if a == "A2" else fnorm).append(x["id"])
        if a in ("A3", "A4") and not m_.get("index_eq"):
            idxmis.append(x["id"])
    S = raw["counts"]["summary"]
    tot = lambda aa, k: sum(cnt.get(a, {}).get(k, 0) for a in aa)
    mine = {"M_R_listed": tot(arms, "planned"), "M_R_valid": tot(arms, "valid"), "M_R_R_eq_1": tot(arms, "R_eq_1"),
            "M_R_R_ne_1": tot(arms, "R_ne_1"), "M_SUB_listed": tot(["A6"], "planned"),
            "M_SUB_valid": tot(["A6"], "valid"), "M_SUB_R_eq_1": tot(["A6"], "R_eq_1"),
            "M_SUB_R_ne_1": tot(["A6"], "R_ne_1"), "M_INDEX_mismatches": len(idxmis),
            "M_INDEX_listed": sum(1 for x in L if x["arm"] in ("A3", "A4")),
            "M_NORMHIT_hits": sum(1 for v in my.values() if v.get("normhit") is True)}
    for k, v in mine.items():
        if S.get(k) != v:
            bad("count %s recorded %s, recomputed %s" % (k, S.get(k), v))
    cross_bad = [i for i, v in my.items() if not v.get("missing") and v.get("cross") is False]
    ctrl_pass = {"C-TRD": 0, "C-NONMAX": 0, "C-NEAR": 0, "C-NOSCALE": 0}
    ctrl_fail = {k: [] for k in ctrl_pass}
    invalid = []
    for ps, cm in ctrl_my.items():
        if cm is None:
            for k in ctrl_fail:
                ctrl_fail[k].append(ps)
            continue
        for k in ("C-TRD", "C-NONMAX", "C-NEAR"):
            if cm[k]["pass"]:
                ctrl_pass[k] += 1
            else:
                ctrl_fail[k].append(ps)
        if cm["C-TRD"]["cross"] and not cm["C-TRD"]["ratio_ok"]:
            invalid.append(ps + ":C-TRD")
        if cm["C-NONMAX"]["valid"] and not (cm["C-NONMAX"]["ratio_ok"] and cm["C-NONMAX"]["index_ok"]):
            invalid.append(ps + ":C-NONMAX")
        for i, cn in enumerate(cm["C-NOSCALE"]):
            if cn["pass"]:
                ctrl_pass["C-NOSCALE"] += 1
            else:
                ctrl_fail["C-NOSCALE"].append("%s:%d" % (ps, i + 1))
            if not cn.get("missing") and cn["cross"] and not cn["ratio_ok"]:
                invalid.append("%s:C-NOSCALE_%d" % (ps, i + 1))
    if S.get("controls_pass_counts") != ctrl_pass:
        bad("control pass counts recorded %s, recomputed %s" % (S.get("controls_pass_counts"), ctrl_pass))
    # ---- outcome (frozen criteria)
    trig = []
    if raw["status"] == "infra_failure":
        trig.append("F-INFRA")
    if raw["status"] == "stopped_calg_b":
        trig.append("F-INSTR")
    if invalid:
        trig.append("INVALID")
    if fnorm or idxmis:
        trig.append("F-NORM")
    if fsub:
        trig.append("F-SUB")
    if dstd:
        trig.append("INCONCLUSIVE-INSTRUMENT")
    if ctrl_fail["C-NEAR"]:
        trig.append("INCONCLUSIVE-NEAR")
    excl = [x["id"] for x in L if x["arm"] in ("A1", "A3", "A4", "A5", "A6") and
            (x.get("missing") or my.get(x["id"], {}).get("calg") is False)]
    if excl:
        trig.append("INCONCLUSIVE-CONSTRUCTION")
    if cross_bad or S.get("M_CROSS_disagreements"):
        trig.append("F-INSTR")
    if ctrl_fail["C-TRD"] or ctrl_fail["C-NONMAX"] or ctrl_fail["C-NOSCALE"]:
        trig.append("INCONCLUSIVE")
    order = ["F-INFRA", "F-INSTR", "INVALID", "F-NORM", "F-SUB", "INCONCLUSIVE-INSTRUMENT", "INCONCLUSIVE-NEAR",
             "INCONCLUSIVE-CONSTRUCTION", "INCONCLUSIVE"]
    trig = sorted(set(trig), key=order.index)
    s_all = (mine["M_R_listed"] == 946 and mine["M_R_R_eq_1"] == 946 and mine["M_SUB_listed"] == 484 and
             mine["M_SUB_R_eq_1"] == 484 and mine["M_INDEX_listed"] == 462 and not idxmis and
             not any(ctrl_fail.values()) and not cross_bad and len(ctrl_my) == 22)
    primary = trig[0] if trig else ("SUCCESS" if s_all else "INCONCLUSIVE")
    rec = raw["outcome"]
    if rec["primary_code"] != primary or rec["triggered_codes"] != trig:
        bad("outcome recorded %s %s, recomputed %s %s" % (rec["primary_code"], rec["triggered_codes"], primary, trig))
    report = {"checked_file": path, "lattices_rechecked": len(my), "recomputed_counts": mine,
              "recomputed_control_pass_counts": ctrl_pass, "recomputed_control_failures": ctrl_fail,
              "recomputed_invalid_cells": invalid, "recomputed_F_NORM_cells": fnorm, "recomputed_F_SUB_cells": fsub,
              "recomputed_D_STD_cells": dstd, "recomputed_index_mismatch_cells": idxmis,
              "recomputed_cross_disagreements": cross_bad, "recomputed_triggered_codes": trig,
              "recomputed_primary_code": primary, "disagreements_with_record": problems,
              "verdict": "REPRODUCED" if not problems else "NOT_REPRODUCED"}
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
