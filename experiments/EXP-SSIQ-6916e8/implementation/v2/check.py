#!/usr/bin/env python3
"""EXP-SSIQ-6916e8 independent checker, PROTOCOL VERSION 2 (frozen specification
v1 + AMD-20260926-f9acf7), task TASK-20260926-fba7e0 (S7).

Started from the version-1 checker (implementation/check.py, sha256
39b9e1bf...d58c1, bound by RUN-SSIQ-81bd08). Reads ONLY raw-result.json (and
tests for the existence of derivation-note.md for S6) and recomputes, with
code independent of driver.py (nothing is imported from it):

  * the frozen algebra presentation of every prime (own implementation of the
    specification rule) and the Hilbert symbols (a, b)_l at every l | 2ab and
    at infinity, by the closed formulae -- NOT the PARI values the driver
    recorded -- so ramification exactly at {p, inf} is re-derived;
  * the ROUTE LADDER audit (amendment review obligations 1-3): R1 is the
    version-1 call on the frozen presentation; R2 = [b, a] with maxord only
    and exactly when R1 raised; R3 = [a, b], , 0 only and exactly when R2 gave
    no valid base; no other route; the recorded construction_route and base
    follow from the recorded attempts; at an A2-based base, gate G-A2 is
    re-evaluated, the images of i, j, k satisfy the defining relations under
    the structure constants, the base basis is the A2 basis mapped through
    them, and its Gram equals the Python A2 Gram;
  * every Gram matrix from the recorded basis and the recorded PARI structure
    constants, via the Cayley-Hamilton route Nrd(x) = (Trd(x)^2 - Trd(x^2))/2,
    Trd(y) = tr(L_y)/2 (driver.py uses sqrt(det L_x), PARI uses algnorm);
    arm A2 via Nrd(x) = scalar part of x * conj(x) in (1, i, j, k);
  * every determinant with sympy Matrix.det(method="bareiss");
  * R, R_sub, indices [O : I] from the recorded bases, n(I) as a gcd;
  * C-ALG order/ideal checks and control values;
  * the tally_rule: the state of every planned item (946 + 484 + 462 + 506),
    verdicts, codes, the triggered list, precedence, the primary label and
    the blocking cells; that no NOT_COMPUTED item appears in any mismatch
    list; and the recorded counts.

Exits 0 iff every recomputed value, flag, state, count, code and the blocking
set agree with what raw-result.json records; otherwise exits 1 and lists every
disagreement. Exact arithmetic only.
"""

import json
import math
import os
import sys
from fractions import Fraction as Q

import sympy

M_LIST = [2, 3, 4, 5, 6, 8, 12, 30, 97, 1024]
ORDER = ["F-INFRA", "F-INSTR", "INVALID", "F-NORM", "F-SUB", "INCONCLUSIVE-INSTRUMENT", "INCONCLUSIVE-NEAR",
         "INCONCLUSIVE-CONSTRUCTION", "INCONCLUSIVE"]
NC, OK, EX = "NOT_COMPUTED", "COMPUTED_VALID", "COMPUTED_EXCLUDED"
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


# ------------------------------------------------------------------ frozen presentation, Hilbert symbols
def frozen_presentation(p):
    if p == 2:
        return -1, -1
    if p % 4 == 3:
        return -1, -p
    if p % 8 == 5:
        return -2, -p
    qq = 3
    while not (sympy.isprime(qq) and qq % 4 == 3 and sympy.legendre_symbol(p % qq, qq) == -1):
        qq += 1
    return -qq, -p


def _split(x, l):
    a = 0
    while x % l == 0:
        x //= l
        a += 1
    return a, x


def hilbert(a, b, l):
    """(a, b)_l for a prime l, or l = 0 meaning the real place (closed formulae)."""
    if l == 0:
        return -1 if (a < 0 and b < 0) else 1
    al, u = _split(a, l)
    be, v = _split(b, l)
    if l == 2:
        eps = lambda t: ((t - 1) // 2) % 2
        om = lambda t: ((t * t - 1) // 8) % 2
        e = (eps(u) * eps(v) + al * om(v) + be * om(u)) % 2
        return -1 if e else 1
    e = (al * be * ((l - 1) // 2)) % 2
    s = -1 if e else 1
    return s * (sympy.legendre_symbol(u % l, l) ** be) * (sympy.legendre_symbol(v % l, l) ** al)


def ramified(a, b):
    places = sorted(set(sympy.primefactors(abs(2 * a * b))))
    fin = [l for l in places if hilbert(a, b, l) == -1]
    return fin, hilbert(a, b, 0) == -1


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


def att_algebra_ok(att, p):
    """C-ALG (a) (independent Hilbert symbols + recorded algramifiedplaces), C-ALG (b), structure constants
    of one recorded route attempt. Returns (ram_ok, nrd_ok, sc_ok)."""
    a, b = att["presentation"]
    fin, inf = ramified(a, b)
    rec_fin = [int(v) for v in att["calg_a"]["ramified_finite"]]
    ram_ok = fin == [p] and inf and rec_fin == [p] and att["calg_a"]["ramified_infinite_count"] == 1
    nrd_ok = q(att["calg_b"]["nrd_one"]) == 1 and q(att["calg_b"]["nrd_two"]) == 4
    mt, prods = att["multable"], att["algmul_products"]
    sc_ok = all([mt[i][r][j] for r in range(4)] == prods[4 * i + j] for i in range(4) for j in range(4))
    return ram_ok, nrd_ok, sc_ok


def main():
    path = sys.argv[1]
    raw = json.load(open(path))
    note_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path)))),
                             "derivation-note.md")
    L = raw["lattices"]
    byp = {}
    for x in L:
        byp.setdefault(x["p"], {})[x["name"]] = x
    my = {}        # lattice id -> dict(valid, calg, cross, val, arm, missing, index_eq)
    ctrl_my = {}   # p -> control dict or None
    route_audit = {}
    infra = raw["status"] == "infra_failure"
    for pe in raw["primes"]:
        ps = pe["p"]
        p = int(ps)
        st = raw["prime_status"].get(ps, {})
        lat = byp.get(ps, {})
        if raw["status"] != "completed" and not lat:
            continue   # stopped / infrastructure run: nothing recorded at this prime; items are NOT_COMPUTED
        a, b = frozen_presentation(p)
        if [pe["presentation"]["a"], pe["presentation"]["b"]] != [a, b]:
            bad("%s: recorded presentation %s differs from the frozen rule (%d, %d)" % (ps, pe["presentation"], a, b))
        # ---------------- route ladder audit
        atts = st.get("route_attempts", [])
        audit = {"attempts": [t["route"] for t in atts]}
        expect_calls = {"R1": "alginit(nfinit(y), [%d, %d])" % (a, b), "R2": "alginit(nfinit(y), [%d, %d])" % (b, a),
                        "R3": "alginit(nfinit(y), [%d, %d], , 0)" % (a, b)}
        for t, rname in zip(atts, ["R1", "R2", "R3"]):
            if t["route"] != rname or t["call"] != expect_calls[rname] or \
                    (t.get("call_gp_echo") is not None and t["call_gp_echo"] != expect_calls[rname]) or \
                    t["maxord_flag"] != (0 if rname == "R3" else 1) or t.get("setrand_before_alginit") != 1:
                bad("%s: route attempt %s is not the declared %s call %s" % (ps, t.get("call"), rname, expect_calls[rname]))
        if len(atts) > 3 or not atts:
            bad("%s: %d route attempts recorded (1..3 allowed)" % (ps, len(atts)))
        # derive the route from the recorded attempts
        derived_route, derived_base = None, None
        a1_route = None
        if atts and atts[0]["error"] is None:
            if len(atts) != 1:
                bad("%s: R1 did not raise but further routes were attempted" % ps)
            derived_route = "R1"
            a1_route = "R1"
        elif atts:
            if len(atts) < 2:
                bad("%s: R1 raised but R2 was not attempted" % ps)
            else:
                t2 = atts[1]
                r2_ok = False
                if t2["error"] is None:
                    ram_ok, nrd_ok, sc_ok = att_algebra_ok(t2, p)
                    if ram_ok and nrd_ok and sc_ok:
                        a1_route = "R2"   # A1 cell recorded from R2; its validity is rechecked below
                        r2_ok = None      # decided after the A1 recheck
                    audit["R2_algebra_ok"] = ram_ok and nrd_ok and sc_ok
                audit["R2_pending_A1"] = r2_ok is None
                derived_route = "R2?" if r2_ok is None else None
        route = st.get("construction_route")
        # ---------------- A2 (Python)
        a2 = lat.get("A2")
        a2_ok_R1 = None
        if a2 is None:
            bad("%s: A2 missing" % ps)
        else:
            alg = IJK(Q(a), Q(b))
            basisA2 = [[q(v) for v in c] for c in a2["basis"]]
            GA2 = gram(alg, basisA2)
            if GA2 != mat_of(a2["gram"]):
                bad("%s:A2 gram differs" % ps)
            d = sdet(GA2)
            cross = a2.get("det_pari") is not None and q(a2["det_pari"]) == d and q(a2["det_python"]) == d
            calg = order_ok(alg, basisA2)
            my[a2["id"]] = {"valid": calg and cross, "val": d * 16 / (p * p) if cross else None, "arm": "A2",
                            "calg": calg, "cross": cross}
            gate_expected = calg and d * 16 / (p * p) == 1
        # ---------------- A1 (from its recorded route's algebra)
        a1 = lat.get("A1")
        a1_valid = None
        if a1 is None:
            bad("%s: A1 record missing" % ps)
        elif a1.get("missing"):
            my[a1["id"]] = {"missing": True, "arm": "A1", "cause": a1.get("not_computed_cause")}
        else:
            r_a1 = a1.get("algebra_route")
            att = next((t for t in atts if t["route"] == r_a1), None)
            if att is None or r_a1 == "R3":
                bad("%s: A1 recorded from route %s without a maximal-order attempt" % (ps, r_a1))
            else:
                ram_ok, nrd_ok, sc_ok = att_algebra_ok(att, p)
                alg1 = CH(att["multable"], att["one"])
                basis = [[q(v) for v in c] for c in a1["basis"]]
                Gu = gram(alg1, basis)
                gram_ok = Gu == mat_of(a1["gram"]) and Gu == mat_of(a1["gram_nrd_unscaled"]) and \
                    ("gram_regrep_unscaled" not in a1 or Gu == mat_of(a1["gram_regrep_unscaled"]))
                dd = sdet(Gu)
                cross = gram_ok and q(a1["det_pari"]) == dd and q(a1["det_python"]) == dd
                calg = ram_ok and sc_ok and order_ok(alg1, basis)
                my[a1["id"]] = {"valid": calg and cross, "calg": calg, "cross": cross,
                                "val": dd * 16 / (p * p) if cross else None, "arm": "A1"}
                a1_valid = calg and cross
                a1_calg = calg
        # ---------------- finish the ladder derivation
        stage_bad = bool(st.get("stage2_error")) or st.get("stage2_multable_equals_stage1") is False
        if derived_route == "R1":
            if a1_valid is None and stage_bad:
                derived_base = st.get("base")   # A1 voided by the stage-consistency rule; base not re-derivable
            elif a1_valid is None:
                bad("%s: R1 did not raise but no A1 cell recorded" % ps)
            elif a1_calg:
                derived_base = "A1"
            else:
                derived_base = "A2_fallback" if st.get("g_a2", {}).get("pass") else "none"
        elif atts and atts[0]["error"] is not None:
            r2_valid_base = derived_route == "R2?" and a1_valid is True and a1_route == "R2"
            if r2_valid_base:
                derived_route, derived_base = "R2", "A1"
                if len(atts) != 2:
                    bad("%s: R2 yielded a valid base but R3 was attempted" % ps)
            else:
                if len(atts) != 3:
                    bad("%s: R2 gave no valid base but R3 was not attempted exactly once" % ps)
                    derived_route, derived_base = None, None
                else:
                    t3 = atts[2]
                    ok3 = False
                    if t3["error"] is None:
                        ram_ok, nrd_ok, sc_ok = att_algebra_ok(t3, p)
                        alg3 = CH(t3["multable"], t3["one"])
                        im = [alg3.one] + [[q(v) for v in w] for w in t3["ijk_images"]]
                        I_, J_, K_ = im[1], im[2], im[3]
                        rel_ok = (alg3.mul(I_, I_) == [a * o for o in alg3.one] and
                                  alg3.mul(J_, J_) == [b * o for o in alg3.one] and
                                  alg3.mul(I_, J_) == K_ and alg3.mul(J_, I_) == [-v for v in K_])
                        audit["R3_ijk_relations_ok"] = rel_ok
                        if ram_ok and nrd_ok and sc_ok and rel_ok and a2 is not None:
                            mapped = [[sum(x[t] * im[t][r] for t in range(4)) for r in range(4)] for x in basisA2]
                            pre_ok = order_ok(alg3, mapped) and gram(alg3, mapped) == GA2
                            audit["R3_mapped_base_order_and_gram_ok"] = pre_ok
                            ok3 = pre_ok and gate_expected and my[a2["id"]]["cross"]
                    derived_route, derived_base = ("R3", "A2_fallback") if ok3 else ("none", "none")
        if derived_route is not None and derived_route != route:
            bad("%s: construction_route recorded %s, derived from the attempts %s" % (ps, route, derived_route))
        if derived_base is not None and derived_base != st.get("base"):
            bad("%s: base recorded %s, derived %s" % (ps, st.get("base"), derived_base))
        # A1 must be NOT_COMPUTED exactly when no maximal-order attempt produced it
        if a1 is not None and a1.get("missing") and a1_route is not None and route in ("R1", "R2"):
            if not (st.get("stage2_error") or st.get("stage2_multable_equals_stage1") is False):
                bad("%s: A1 not computed although route %s produced it" % (ps, route))
        # gate G-A2 recheck wherever evaluated / required
        g = st.get("g_a2", {})
        if g.get("evaluated"):
            if a2 is not None:
                g_re = my[a2["id"]]["calg"] and q(g["det_pari"]) == sdet(GA2) and sdet(GA2) * 16 / (p * p) == 1
                if bool(g["pass"]) != bool(g_re):
                    bad("%s: gate G-A2 recorded %s, recomputed %s" % (ps, g["pass"], g_re))
                audit["g_a2_recomputed"] = g_re
        elif st.get("base") == "A2_fallback":
            bad("%s: A2-based base without an evaluated gate G-A2" % ps)
        audit.update({"route": route, "base": st.get("base"), "derived_route": derived_route,
                      "derived_base": derived_base})
        route_audit[ps] = audit

        # ---------------- no base / stage inconsistency: everything PARI-side must be NOT_COMPUTED
        stage_ok = st.get("base") not in (None, "none") and not st.get("stage2_error") and \
            st.get("stage2_multable_equals_stage1") is True and "multable_stage2" in st
        if not stage_ok:
            for nm, x in lat.items():
                if nm in ("A2",) or (nm == "A1" and not x.get("missing")):
                    continue
                if not x.get("missing"):
                    bad("%s: lattice %s present although no valid base / consistent stage 2" % (ps, nm))
                my[x["id"]] = {"missing": True, "arm": x["arm"], "cause": x.get("not_computed_cause")}
            ctrl_my[ps] = None
            continue
        chosen = next(t for t in atts if t["route"] == route)
        if st["multable_stage1"] != chosen["multable"] or st["multable_stage2"] != chosen["multable"]:
            bad("%s: stage-1/stage-2 structure constants differ from the chosen route's attempt" % ps)
        ram_ok, nrd_ok, sc_ok = att_algebra_ok(chosen, p)
        prime_ok = ram_ok and sc_ok
        s2_same = st.get("multable_stage2") == st.get("multable_stage1")
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
            out["valid"] = out["calg"] and out["cross"]
            return out

        # ---- base
        base = lat["base"]
        rb = recheck(base, alg2, lambda bb, o: [order_ok(alg2, bb)])
        B = rb["basis"]
        coB = solve_coords(B)
        my[base["id"]] = {"valid": rb["valid"], "calg": rb["calg"], "cross": rb["cross"], "val": None, "arm": "base"}
        if st["base"] == "A2_fallback":
            im = [alg2.one] + [[q(v) for v in w] for w in st["ijk_images"]]
            mapped = [[sum(x[t] * im[t][r] for t in range(4)) for r in range(4)] for x in basisA2]
            if mapped != B:
                bad("%s: A2-based base is not the A2 basis mapped through the recorded i, j, k images" % ps)
            if rb["Gu"] != GA2:
                bad("%s: A2-based base Gram (CH instrument) differs from the Python A2 Gram" % ps)
            audit["base_reproduces_A2_gram"] = rb["Gu"] == GA2
        elif B != [[Q(int(i == j)) for i in range(4)] for j in range(4)]:
            bad("%s: base = A1 but the base basis is not the stored order" % ps)
        base_valid = rb["valid"]
        # ---- C-TRD
        T = [[alg2.trd(alg2.mul(x, alg2.conj(y))) for y in B] for x in B]
        c = next(cc for cc in raw["controls"] if cc["p"] == ps)
        dT = sdet(T)
        trd_cross = T == mat_of(c["C-TRD"]["trace_form"]) and q(c["C-TRD"]["det_pari"]) == dT and rb["cross"]
        cm = {"C-TRD": {"cross": trd_cross, "calg": rb["calg"], "ratio_ok": dT / rb["det"] == 16,
                        "ok": dT / rb["det"] == 16 and dT * 16 / (p * p) != 1}}
        # ---- C-NONMAX
        nm_ = lat["C-NONMAX"]
        rn = recheck(nm_, alg2, lambda bb, o: [order_ok(alg2, bb)], parent_cols=B)
        TN = [[alg2.trd(alg2.mul(x, alg2.conj(y))) for y in rn["basis"]] for x in rn["basis"]]
        dTN = sdet(TN)
        my[nm_["id"]] = {"valid": rn["valid"], "calg": rn["calg"], "cross": rn["cross"], "val": None, "arm": "C-NONMAX"}
        nm_cross = rn["cross"] and q(c["C-NONMAX"]["index_pari"]) == rn["index"] and \
            TN == mat_of(c["C-NONMAX"]["trace_form"]) and q(c["C-NONMAX"]["trace_form_det_pari"]) == dTN
        idx8, r64 = rn["index"] == 8, rn["det"] / rb["det"] == 64
        cm["C-NONMAX"] = {"cross": nm_cross, "calg": rn["calg"], "ratio_ok": idx8 and r64,
                          "ok": idx8 and r64 and dTN != p * p and rn["det"] * 16 / (p * p) != 1}
        # ---- A3
        P = lat["A3"]

        def calgP(bb, o):
            co = solve_coords(bb)
            return [all(integral(coB(x)) for x in bb),
                    all(integral(co(alg2.mul(ob, x))) for ob in B for x in bb),
                    all(integral(co(alg2.mul(x, ob))) for ob in B for x in bb),
                    all((alg2.nrd(x) / p).denominator == 1 for x in bb), base_valid]
        rP = recheck(P, alg2, calgP, parent_cols=B, want_index=True)
        my[P["id"]] = {"valid": rP["valid"], "calg": rP["calg"], "cross": rP["cross"],
                       "val": rP["det"] * 16 / (p * p) if rP["cross"] else None, "arm": "A3",
                       "index_eq": rP["index"] == rP["n"] ** 2}
        PB = rP["basis"]
        # ---- C-NEAR
        nr = {}
        for nm, par, exp in (("C-NEAR-O0", B, Q(p * p, 4)), ("C-NEAR-P0", PB, Q(p, 4))):
            x = lat[nm]
            cop = solve_coords(par)
            rr = recheck(x, alg2, lambda bb, o: [all(alg2.trd(v) == 0 for v in bb), all(integral(cop(v)) for v in bb)])
            my[x["id"]] = {"valid": rr["valid"], "calg": rr["calg"], "cross": rr["cross"], "val": None, "arm": nm}
            nr[nm] = (rr, exp)
        cm["C-NEAR"] = {"cross": all(v[0]["cross"] for v in nr.values()), "calg": all(v[0]["calg"] for v in nr.values()),
                        "ratio_ok": True, "ok": all(v[0]["det"] == v[1] for v in nr.values())}
        # ---- A4 / A5 / C-NOSCALE
        cm["C-NOSCALE"] = []
        parents = {0: (B, Q(1), base_valid), 1: (PB, Q(p), rP["valid"])}
        for k in range(1, 21):
            x = lat["A4_%d" % k]
            if x.get("missing"):
                my[x["id"]] = {"missing": True, "arm": "A4", "cause": x.get("not_computed_cause")}
                y = lat["A5_%d" % k]
                if not y.get("missing"):
                    bad("%s present although its A4 parent is not computed" % y["id"])
                my[y["id"]] = {"missing": True, "arm": "A5", "cause": y.get("not_computed_cause")}
                cm["C-NOSCALE"].append(None)
                continue

            def calgI(bb, o):
                co = solve_coords(bb)
                return [all(integral(coB(v)) for v in bb), all(integral(co(alg2.mul(ob, v))) for ob in B for v in bb),
                        base_valid]
            basisI = [[q(v) for v in cc] for cc in x["basis"]]
            GI = gram(alg2, basisI)
            nI = gcdq([GI[i][i] for i in range(4)] + [2 * GI[i][j] for i in range(4) for j in range(i + 1, 4)])
            if q(x["form_scale"]) != nI:
                bad("%s: form scale %s != recomputed n(I) %s" % (x["id"], x["form_scale"], qs(nI)))
            rI = recheck(x, alg2, calgI, parent_cols=B, want_index=True, scale=nI)
            my[x["id"]] = {"valid": rI["valid"], "calg": rI["calg"], "cross": rI["cross"],
                           "val": rI["det"] * 16 / (p * p) if rI["cross"] else None, "arm": "A4",
                           "index_eq": rI["index"] == rI["n"] ** 2, "normhit": rI["n"] == q(x["target_norm"])}
            cross_u = rI["cross"] and q(x["det_pari_unscaled"]) == rI["detu"] and q(x["det_python_unscaled"]) == rI["detu"]
            cm["C-NOSCALE"].append({"cross": cross_u, "calg": rI["calg"], "ratio_ok": rI["detu"] / rI["det"] == nI ** 4,
                                    "ok": rI["detu"] / rI["det"] == nI ** 4 and rI["detu"] * 16 / (p * p) != 1})
            parents[k + 1] = (rI["basis"], nI, rI["valid"])
            y = lat["A5_%d" % k]
            if y.get("missing"):
                my[y["id"]] = {"missing": True, "arm": "A5", "cause": y.get("not_computed_cause")}
                continue
            coI = solve_coords(rI["basis"])
            rO = recheck(y, alg2, lambda bb, o: [order_ok(alg2, bb),
                                                 all(integral(coI(alg2.mul(v, w))) for v in rI["basis"] for w in bb),
                                                 rI["calg"]])
            my[y["id"]] = {"valid": rO["valid"], "calg": rO["calg"], "cross": rO["cross"],
                           "val": rO["det"] * 16 / (p * p) if rO["cross"] else None, "arm": "A5"}
        # ---- A6
        for k in range(22):
            x = lat["A6_%d" % k]
            m = M_LIST[k % 10]
            if x.get("missing") or k not in parents:
                if not x.get("missing"):
                    bad("%s present although its parent is not computed" % x["id"])
                my[x["id"]] = {"missing": True, "arm": "A6", "cause": x.get("not_computed_cause")}
                continue
            Mb, sc, pvalid = parents[k]
            Hrows = mat_of(x["H"])
            upper = all(Hrows[i][j] == 0 for i in range(4) for j in range(i)) and all(Hrows[i][i] > 0 for i in range(4)) \
                and all(0 <= Hrows[i][j] < Hrows[j][j] for j in range(4) for i in range(j))
            r6 = recheck(x, alg2, lambda bb, o: [o["index"] == m, abs(sdet(Hrows)) == m, upper, pvalid],
                         parent_cols=Mb, scale=sc)
            mm = abs(sdet(Hrows))
            my[x["id"]] = {"valid": r6["valid"], "calg": r6["calg"], "cross": r6["cross"],
                           "val": r6["det"] * 16 / (mm * mm * p * p) if r6["cross"] else None, "arm": "A6"}
        ctrl_my[ps] = cm

    # ------------------------------------------------------------------ per-lattice comparison with the record
    for x in L:
        m_ = my.get(x["id"])
        if m_ is None:
            bad("%s: not rechecked" % x["id"])
            continue
        if m_.get("missing"):
            if not x.get("missing"):
                bad("%s: recorded computed, rechecked as not computed" % x["id"])
            continue
        if bool(x.get("valid")) != bool(m_["valid"]):
            bad("%s: validity recorded %s, recomputed %s" % (x["id"], x.get("valid"), m_["valid"]))
        rkey = "R_sub" if x["arm"] == "A6" else "R"
        if m_.get("val") is not None and x["arm"] in ("A1", "A2", "A3", "A4", "A5", "A6"):
            if x.get(rkey) is None or q(x[rkey]) != m_["val"]:
                bad("%s: %s recorded %s, recomputed %s" % (x["id"], rkey, x.get(rkey), qs(m_["val"])))
        if "index_eq" in m_ and x.get("index_equals_n_squared") is not None and x["index_equals_n_squared"] != m_["index_eq"]:
            bad("%s: index==n^2 flag differs" % x["id"])

    # ------------------------------------------------------------------ tally_rule, independently
    default_cause = "INFRASTRUCTURE" if infra else "CONSTRUCTION"
    primes = [e["p"] for e in raw["primes"]]
    slots = primes + ["UNKNOWN_PRIME_SLOT_%d" % i for i in range(len(primes), 22)]
    names_primary = ["A1", "A2", "A3"] + ["A4_%d" % k for k in range(1, 21)] + ["A5_%d" % k for k in range(1, 21)]
    names_sub = ["A6_%d" % k for k in range(22)]
    names_index = ["A3"] + ["A4_%d" % k for k in range(1, 21)]
    items = {}
    for ps in slots:
        for kind, names in (("primary", names_primary), ("sub", names_sub), ("index", names_index)):
            for nm in names:
                lid = "%s:%s" % (ps, nm)
                iid = lid if kind != "index" else "%s:M-INDEX:%s" % (ps, nm)
                arm = "A6" if kind == "sub" else nm.split("_")[0]
                m_ = my.get(lid)
                it = {"kind": kind, "arm": arm, "codes": set(), "verdict": None}
                if m_ is None or m_.get("missing"):
                    cause = (m_ or {}).get("cause") or default_cause
                    if m_ is None:
                        cause = default_cause
                    elif not infra and cause != "CONSTRUCTION":
                        bad("%s: NOT_COMPUTED cause %s in a run without an infrastructure event" % (lid, cause))
                    it.update({"state": NC, "cause": cause})
                    it["codes"].add("F-INFRA" if cause == "INFRASTRUCTURE" else "INCONCLUSIVE-CONSTRUCTION")
                elif m_["valid"]:
                    it["state"] = OK
                    if kind == "index":
                        it["verdict"] = "pass" if m_["index_eq"] else "mismatch"
                        if not m_["index_eq"]:
                            it["codes"].add("F-NORM")
                    else:
                        okv = m_["val"] == 1
                        it["verdict"] = "pass" if okv else "mismatch"
                        if not okv:
                            it["codes"].add("F-SUB" if kind == "sub" else
                                            "INCONCLUSIVE-INSTRUMENT" if arm == "A2" else "F-NORM")
                else:
                    it["state"] = EX
                    if not m_["calg"]:
                        it["codes"].add("INCONCLUSIVE-INSTRUMENT" if arm == "A2" else "INCONCLUSIVE-CONSTRUCTION")
                    if not m_["cross"]:
                        it["codes"].add("F-INSTR")
                items[iid] = it
        cm = ctrl_my.get(ps)
        crec = next((cc for cc in raw["controls"] if cc["p"] == ps), None)
        for nm in ["C-TRD", "C-NONMAX", "C-NEAR"] + ["C-NOSCALE_%d" % k for k in range(1, 21)]:
            base_nm = nm.split("_")[0]
            it = {"kind": "control", "arm": base_nm, "codes": set(), "verdict": None, "invalid": False}
            v = None
            if cm is not None:
                v = cm["C-NOSCALE"][int(nm.split("_")[1]) - 1] if base_nm == "C-NOSCALE" else cm[base_nm]
            if v is None:
                cause = default_cause
                if crec is not None:
                    sub = crec["C-NOSCALE"][int(nm.split("_")[1]) - 1] if (base_nm == "C-NOSCALE" and crec.get("C-NOSCALE")) else None
                    cause = (sub or {}).get("not_computed_cause") or (crec.get("not_computed") or {}).get("cause") or cause
                it.update({"state": NC, "cause": cause})
                it["codes"].add("F-INFRA" if cause == "INFRASTRUCTURE" else "INCONCLUSIVE-CONSTRUCTION")
            else:
                if base_nm != "C-NEAR" and v["cross"] and not v["ratio_ok"]:
                    it["invalid"] = True
                    it["codes"].add("INVALID")
                if not (v["cross"] and v["calg"]):
                    it["state"] = EX
                    if not v["calg"]:
                        it["codes"].add("INCONCLUSIVE-CONSTRUCTION")
                    if not v["cross"]:
                        it["codes"].add("F-INSTR")
                else:
                    it["state"] = OK
                    it["verdict"] = "pass" if v["ok"] else "mismatch"
                    if not v["ok"]:
                        if base_nm == "C-NEAR":
                            it["codes"].add("INCONCLUSIVE-NEAR")
                        elif not it["invalid"]:
                            it["codes"].add("INCONCLUSIVE")
            items["%s:%s" % (ps, nm)] = it

    # M-CROSS: computed records failing an instrument, plus control instrument failures
    cross_bad = sorted(i for i, v in my.items() if not v.get("missing") and v.get("cross") is False)
    for ps, cm in ctrl_my.items():
        if cm is None:
            continue
        for k in ("C-TRD", "C-NONMAX"):
            if not cm[k]["cross"]:
                cross_bad.append("%s:%s" % (ps, k))
        for i, v in enumerate(cm["C-NOSCALE"]):
            if v is not None and not v["cross"]:
                cross_bad.append("%s:C-NOSCALE_%d" % (ps, i + 1))
    trig = set()
    for it in items.values():
        trig |= it["codes"]
    if infra:
        trig.add("F-INFRA")
    if raw["status"] == "stopped_calg_b":
        trig.add("F-INSTR")
    if cross_bad:
        trig.add("F-INSTR")
    blocking = sorted(i for i, it in items.items() if not (it["state"] == OK and it["verdict"] == "pass"))
    for i in blocking:
        if not items[i]["codes"]:
            items[i]["codes"].add("INCONCLUSIVE")
            trig.add("INCONCLUSIVE")

    def allpass(kind, n):
        xs = [it for it in items.values() if it["kind"] == kind]
        return len(xs) == n and all(it["state"] == OK and it["verdict"] == "pass" for it in xs)
    S = {"S1": allpass("primary", 946), "S2": allpass("sub", 484), "S3": allpass("index", 462),
         "S4": allpass("control", 506), "S5": not cross_bad, "S6_file_present": os.path.isfile(note_path)}
    if not trig and not all(S.values()):
        trig.add("INCONCLUSIVE")
    trig = sorted(trig, key=ORDER.index)
    primary = trig[0] if trig else "SUCCESS"

    # ------------------------------------------------------------------ compare with the record
    rec = raw["outcome"]
    if rec["primary_code"] != primary:
        bad("primary code recorded %s, recomputed %s" % (rec["primary_code"], primary))
    if rec["triggered_codes"] != trig:
        bad("triggered codes recorded %s, recomputed %s" % (rec["triggered_codes"], trig))
    if sorted(rec["blocking_cells"]) != blocking:
        diff = sorted(set(rec["blocking_cells"]) ^ set(blocking))
        bad("blocking cells differ (%d symmetric-difference items, first: %s)" % (len(diff), diff[:10]))
    for k, v in S.items():
        if rec["success_conditions"].get(k) != v:
            bad("success condition %s recorded %s, recomputed %s" % (k, rec["success_conditions"].get(k), v))
    recstates = {r["id"]: r for r in raw["counts"]["item_states"]}
    if set(recstates) != set(items):
        bad("planned item set differs: %d recorded vs %d recomputed" % (len(recstates), len(items)))
    for iid, it in items.items():
        r = recstates.get(iid)
        if r is None:
            continue
        if r["state"] != it["state"] or r.get("verdict") != it["verdict"] or sorted(r.get("codes", [])) != sorted(it["codes"]) \
                or (it["state"] == NC and r.get("cause") != it["cause"]):
            bad("%s: recorded %s/%s/%s/%s, recomputed %s/%s/%s/%s" % (iid, r["state"], r.get("verdict"), r.get("codes"),
                r.get("cause"), it["state"], it["verdict"], sorted(it["codes"]), it.get("cause")))
    # NOT_COMPUTED is never a mismatch (review obligation 4)
    nc_ids = {i for i, it in items.items() if it["state"] == NC}
    for key in ("controls_failed", "F_NORM_cells", "M_INDEX_mismatch_cells", "F_SUB_cells", "D_STD_cells",
                "INVALID_cells", "instrument_disagreement_cells", "construction_exclusions"):
        leak = nc_ids & set(rec.get(key, []))
        if leak:
            bad("NOT_COMPUTED items appear in %s: %s" % (key, sorted(leak)[:10]))
    # counts
    summ = raw["counts"]["summary"]

    def cnt(sel):
        xs = [it for it in items.values() if sel(it)]
        return {"planned": len(xs), "computed_valid": sum(1 for i in xs if i["state"] == OK),
                "computed_excluded": sum(1 for i in xs if i["state"] == EX),
                "not_computed": sum(1 for i in xs if i["state"] == NC),
                "not_computed_construction": sum(1 for i in xs if i["state"] == NC and i["cause"] == "CONSTRUCTION"),
                "not_computed_infrastructure": sum(1 for i in xs if i["state"] == NC and i["cause"] == "INFRASTRUCTURE"),
                "pass": sum(1 for i in xs if i["verdict"] == "pass"),
                "mismatch": sum(1 for i in xs if i["verdict"] == "mismatch")}
    mine = {"M_R": cnt(lambda i: i["kind"] == "primary"), "M_SUB": cnt(lambda i: i["kind"] == "sub"),
            "M_INDEX": cnt(lambda i: i["kind"] == "index"),
            "controls": {k: cnt(lambda i, k=k: i["kind"] == "control" and i["arm"] == k)
                         for k in ("C-TRD", "C-NONMAX", "C-NEAR", "C-NOSCALE")},
            "controls_total": cnt(lambda i: i["kind"] == "control"),
            "M_R_by_arm": {a: cnt(lambda i, a=a: i["kind"] == "primary" and i["arm"] == a)
                           for a in ("A1", "A2", "A3", "A4", "A5")},
            "M_NORMHIT_hits": sum(1 for v in my.values() if v.get("normhit") is True)}
    for k, v in mine.items():
        if summ.get(k) != v:
            bad("count %s recorded %s, recomputed %s" % (k, summ.get(k), v))
    if bool(summ.get("M_CROSS_disagreements")) != bool(cross_bad):
        bad("M-CROSS recorded %s, recomputed list %s" % (summ.get("M_CROSS_disagreements"), cross_bad))
    report = {"checked_file": path, "protocol_version": raw.get("protocol_version"),
              "lattices_rechecked": sum(1 for v in my.values() if not v.get("missing")),
              "lattice_records_not_computed": sum(1 for v in my.values() if v.get("missing")),
              "route_audit": route_audit, "recomputed_counts": mine,
              "recomputed_cross_disagreements": cross_bad, "recomputed_success_conditions": S,
              "recomputed_triggered_codes": trig, "recomputed_primary_code": primary,
              "recomputed_blocking_cells_count": len(blocking), "recomputed_blocking_cells": blocking,
              "disagreements_with_record": problems,
              "verdict": "REPRODUCED" if not problems else "NOT_REPRODUCED"}
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
