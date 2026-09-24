"""Phase 1 per cell: curve and points, V, references and test targets of every
family, the three satisfiability oracles, witness re-verification, C-TR and the
x(2E) classes.

Copied from EXP-CERTBIN-4e92d7/impl/families.py and generalized to the Stage-2
cells (see impl-provenance.json). Every stream is
numpy.random.Generator(numpy.random.PCG64(seed)); the draw procedure of each
stream is fixed in trial-plan-v1.json ("draw_procedures") and consumed strictly
in order. Every rejection is counted.
"""
import numpy as np

from curve import Curve, is_prime
from oracles import (oracle_A, OracleB, OracleC, s3_coeffs, verify_witnesses, rational_flag,
                     solve_quadratic)


def gen(seed):
    return np.random.Generator(np.random.PCG64(seed))


def draw_int(g, lo, hi):
    return int(g.integers(lo, hi))


# ---------------------------------------------------------------------------
def draw_curve(F, seed):
    """Stage-1 curve rule (A, B uniform in [0, 2^n), B != 0, exact count,
    accept the first with #E = h*q, h in {2, 4}, q prime)."""
    g = gen(seed)
    rej = {"B_zero": 0, "cofactor_or_primality": 0}
    tried = []
    while True:
        A = draw_int(g, 0, F.q)
        B = draw_int(g, 0, F.q)
        if B == 0:
            rej["B_zero"] += 1
            tried.append({"A": A, "B": B, "reason": "B_zero"})
            continue
        E = Curve(F, A, B)
        n = E.count_by_trace()
        h = None
        if n % 2 == 0 and is_prime(n // 2):
            h = 2
        elif n % 4 == 0 and is_prime(n // 4):
            h = 4
        if h is None:
            rej["cofactor_or_primality"] += 1
            tried.append({"A": A, "B": B, "order": n, "reason": "order not h*q with h in {2,4}, q prime"})
            continue
        return E, {"A": A, "B": B, "order": n, "h": h, "q": n // h,
                   "draws_rejected": sum(rej.values()), "rejections": rej, "rejected_draws": tried}


def draw_points(E, h, q, seed):
    """Stage-1 point rule."""
    g = gen(seed)
    rej = {"x_not_liftable": 0, "hP_is_O": 0}
    while True:
        x = draw_int(g, 0, E.F.q)
        pt = E.lift_x(x)
        if pt is None:
            rej["x_not_liftable"] += 1
            continue
        P = E.mul(h, pt)
        if P is None:
            rej["hP_is_O"] += 1
            continue
        break
    kQ = draw_int(g, 1, q)
    Qp = E.mul(kQ, P)
    checks = {"P_on_curve": E.on_curve(P), "qP_is_O": E.mul(q, P) is None,
              "Q_on_curve": E.on_curve(Qp), "Q_not_O": Qp is not None}
    return P, Qp, kQ, {"lift_x": x, "rejections": rej, "checks": checks}


class CurveStream:
    """R = [a]P + [b]Q with a, b uniform in [0, q-1]; redraw if R = O."""

    def __init__(self, E, P, Qp, q, seed):
        self.E, self.P, self.Q, self.q = E, P, Qp, q
        self.g = gen(seed)
        self.draws = 0
        self.rej_O = 0

    def next(self):
        while True:
            a = draw_int(self.g, 0, self.q)
            b = draw_int(self.g, 0, self.q)
            self.draws += 1
            R = self.E.add(self.E.mul(a, self.P), self.E.mul(b, self.Q))
            if R is None:
                self.rej_O += 1
                continue
            return {"a": a, "b": b, "x_R": R[0], "y_R": R[1], "draw": self.draws}


class SharedCurveSeq:
    """AMD-20260924-3a9f06 C-19: stream 01 is ONE sequence per cell. The
    generator is instantiated once; its raw draws (a, b, R) are logged in order;
    every reader starts at position 0 of the log and pulls further draws from
    the same instance only past the end of the log."""

    def __init__(self, E, P, Qp, q, seed):
        self.E, self.P, self.Q, self.q = E, P, Qp, q
        self.g = gen(seed)
        self.log = []

    def pull(self):
        a = draw_int(self.g, 0, self.q)
        b = draw_int(self.g, 0, self.q)
        R = self.E.add(self.E.mul(a, self.P), self.E.mul(b, self.Q))
        self.log.append((a, b, R))

    def reader(self):
        return SeqReader(self)


class SeqReader:
    """CurveStream-compatible reader of a SharedCurveSeq."""

    def __init__(self, seq):
        self.seq = seq
        self.pos = 0
        self.draws = 0
        self.rej_O = 0

    def next(self):
        while True:
            if self.pos == len(self.seq.log):
                self.seq.pull()
            a, b, R = self.seq.log[self.pos]
            self.pos += 1
            self.draws = self.pos
            if R is None:
                self.rej_O += 1
                continue
            return {"a": a, "b": b, "x_R": R[0], "y_R": R[1], "draw": self.draws}


# ---------------------------------------------------------------------------
def curve_classes(E, order):
    """C-TR (v2, AMD-20260924-3a9f06 C-10) by enumeration over F_{2^n}.
    x(E): x = 0 or Tr(x + A + B/x^2) = 0. x(2E) by a POINT TEST that does not
    use the trace criterion: x in x(2E) iff the lifted point P satisfies
    [#E/2] P = O (the 2-Sylow subgroup of E(F_{2^n}) is cyclic). Cross-check:
    the doubling image {x^2 + B/x^2}. (i) restated check on x(E); (ii) the
    literal v1 statement over all of F_{2^n}, violations split into x(E) and
    twist abscissae. Returns (xE bool array, x2E bool array, C-TR dict)."""
    F = E.F
    xs = np.arange(F.q, dtype=np.int64)
    xE = np.zeros(F.q, dtype=bool)
    xE[0] = True
    nz = xs[1:]
    x2 = F.vmul(nz, nz)
    c = nz ^ E.A ^ F.vdiv(np.full_like(nz, E.B), x2)
    xE[1:] = F.vtrace(c) == 0
    half = order // 2
    x2E = np.zeros(F.q, dtype=bool)
    for x in np.flatnonzero(xE):
        P = E.lift_x(int(x))
        if E.mul(half, P) is None:
            x2E[x] = True
    lx = nz[xE[1:]]
    lx2 = F.vmul(lx, lx)
    dbl = lx2 ^ F.vdiv(np.full_like(lx, E.B), lx2)
    x2E_img = np.zeros(F.q, dtype=bool)
    x2E_img[dbl] = True
    trA = F.trace(E.A)
    trx = F.vtrace(xs).astype(bool)
    pred = trx == bool(trA)
    viol_i = np.flatnonzero((pred != x2E) & xE)
    viol_lit = np.flatnonzero(pred != x2E)
    ctr = {"version": 2, "Tr_A": trA, "n_xE": int(xE.sum()), "n_x2E": int(x2E.sum()),
           "point_test": "[#E/2] * lift_x(x) == O",
           "point_test_equals_doubling_image": bool(np.array_equal(x2E, x2E_img)),
           "restated_check_on_xE": {"statement": "for x in x(E): x in x(2E) iff Tr(x) == Tr(A)",
                                    "violations": int(viol_i.size), "violating_x_first20": viol_i[:20].tolist()},
           "literal_v1_count": {"statement": "over all of F_{2^n}: x in x(2E) iff Tr(x) == Tr(A)",
                                "violations": int(viol_lit.size),
                                "violations_in_xE": int(((pred != x2E) & xE).sum()),
                                "violations_in_twist": int(((pred != x2E) & ~xE).sum())},
           "pass": viol_i.size == 0,
           "fails_if": "any violation of the restated check (i)"}
    return xE, x2E, ctr


def x2e_class(xE, x2E, x):
    if x2E[x]:
        return "x2E"
    if xE[x]:
        return "xE_not_x2E"
    return "twist"


def subgroup_xset(E, P, q):
    """x-coordinates of [m]P, m = 1..q-1 (by iterated addition; checks qP = O)."""
    xs = set()
    R = None
    for _ in range(1, q):
        R = E.add(R, P)
        xs.add(R[0])
    assert E.add(R, P) is None
    return xs


def sat_population(F, E, B, l, subgroup_x):
    """E_SAT population (AMD-20260924-3a9f06 C-8): every non-degenerate subgroup
    abscissa x with s(x) >= 1, decided EXHAUSTIVELY with the SAME test the F-SAT
    scan uses (oracle A). Also returns the exact P_sat numerator/denominator."""
    pop = set()
    nd = 0
    for x in subgroup_x:
        if x < (1 << l):
            continue
        nd += 1
        if len(oracle_A(F, B, x, l)) >= 1:
            pop.add(x)
    return pop, nd


def sat_population_vv(F, B, l, subgroup_x):
    """AMD C-17 second, independent enumeration of the satisfiable subgroup
    abscissae: for every (x_1, x_2) in V^2, the roots X of S_3(x_1, x_2, X) =
    (x_1 + x_2)^2 X^2 + x_1 x_2 X + x_1^2 x_2^2 + B, kept if non-degenerate and
    a subgroup abscissa."""
    pop = set()
    for x1 in range(1 << l):
        for x2 in range(1 << l):
            s = x1 ^ x2
            kind, roots = solve_quadratic(F, F.mul(s, s), F.mul(x1, x2), F.mul(F.mul(x1, x2), F.mul(x1, x2)) ^ B)
            if kind == "all":
                raise RuntimeError("degenerate quadratic in sat_population_vv")
            for r in roots:
                if r >= (1 << l) and r in subgroup_x:
                    pop.add(r)
    return pop


def degenerate(xR, l):
    return xR < (1 << l)


# ---------------------------------------------------------------------------
def select_references(candidates_iter, max_draws, n_unsat=3, n_sat=2):
    """reference_rule: scan in order; classify each non-degenerate,
    non-duplicate instance; take the first 3 unsatisfiable and the first 2
    satisfiable; stop at 5 or after max_draws draws (shortfall recorded)."""
    refs = []
    scanned = []
    nu = ns = 0
    for cand in candidates_iter:
        if cand["status"] == "classified":
            if cand["s"] == 0 and nu < n_unsat:
                nu += 1
                cand["selected_as"] = f"U{nu}"
                refs.append(cand)
            elif cand["s"] >= 1 and ns < n_sat:
                ns += 1
                cand["selected_as"] = f"S{ns}"
                refs.append(cand)
            else:
                cand["selected_as"] = None
        scanned.append(_scan_summary(cand))
        if nu == n_unsat and ns == n_sat:
            break
        if cand["draw"] >= max_draws:
            break
    shortfall = {"unsat_missing": n_unsat - nu, "sat_missing": n_sat - ns}
    refs.sort(key=lambda r: (r["selected_as"][0] != "U", r["selected_as"]))
    return refs, scanned, shortfall


def _scan_summary(c):
    keep = ("draw", "status", "x_R", "s", "selected_as", "a", "b")
    return {k: c[k] for k in keep if k in c}


def scan_counts(scanned):
    return {"draws": len(scanned),
            "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned),
            "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned),
            "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned),
            "classified_unsat": sum(c["status"] == "classified" and c.get("s") == 0 for c in scanned),
            "classified_sat": sum(c["status"] == "classified" and (c.get("s") or 0) >= 1 for c in scanned)}


def curve_ref_candidates(stream, classify, l):
    seen = set()
    while True:
        d = stream.next()
        xR = d["x_R"]
        c = {"draw": stream.draws, "a": d["a"], "b": d["b"], "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif degenerate(xR, l):
            seen.add(xR)
            c["status"] = "rejected_degenerate_reference"
        else:
            seen.add(xR)
            c.update(classify(xR))
            c["status"] = "classified"
        yield c


def randx_ref_candidates(g, classify, q, l, counter):
    seen = set()
    while True:
        xR = draw_int(g, 0, q)
        counter["draws"] += 1
        c = {"draw": counter["draws"], "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif degenerate(xR, l):
            seen.add(xR)
            c["status"] = "rejected_degenerate_reference"
        else:
            seen.add(xR)
            c.update(classify(xR))
            c["status"] = "classified"
        yield c


# ---------------------------------------------------------------------------
# regime-A null constructions (Stage-1, on the cell's supports)
def support_positions(E0, Ej):
    s0 = np.flatnonzero(E0.reshape(-1))
    sj = [np.flatnonzero(x.reshape(-1)) for x in Ej]
    return s0, sj


def draw_affine_null(seed, E0, Ej):
    """E'^0 iid Bernoulli(1/2) on supp(E^0), then E'^j on supp(E^j) for
    j = 0..n-1, positions in row-major order of the n x |mons| matrix."""
    g = gen(seed)
    s0, sj = support_positions(E0, Ej)
    shape = E0.shape

    def one(pos):
        M = np.zeros(shape[0] * shape[1], dtype=np.uint8)
        bits = g.integers(0, 2, size=pos.size).astype(np.uint8)
        M[pos] = bits
        return M.reshape(shape)

    A0 = one(s0)
    Aj = [one(p) for p in sj]
    return A0, Aj


def affine_combine_alt(A0, Aj, r):
    """Second code path for C-AFF on F-AFF: tensor contraction mod 2."""
    n = len(Aj)
    rb = np.array([(r >> j) & 1 for j in range(n)], dtype=np.int64)
    stack = np.stack(Aj).astype(np.int64)
    return ((A0.astype(np.int64) + np.tensordot(rb, stack, axes=1)) % 2).astype(np.uint8)


def nullF2_union_support(E0, Ej):
    U = E0.astype(bool).copy()
    for x in Ej:
        U |= x.astype(bool)
    return np.flatnonzero(U.reshape(-1)), U


def draw_nullF2_instance(g, Upos, shape):
    M = np.zeros(shape[0] * shape[1], dtype=np.uint8)
    M[Upos] = g.integers(0, 2, size=Upos.size).astype(np.uint8)
    return M.reshape(shape)


def E_to_hex(Emat):
    return [format(int("".join(str(int(b)) for b in row[::-1]) or "0", 2), "x") for row in Emat]


def E_from_hex(hx, ncols):
    E = np.zeros((len(hx), ncols), dtype=np.uint8)
    for k, h in enumerate(hx):
        v = int(h, 16)
        for j in range(ncols):
            E[k, j] = (v >> j) & 1
    return E


def factor_base_points(E, l):
    pts = []
    for x in range(1 << l):
        P = E.lift_x(x)
        if P is None:
            continue
        if x == 0:
            pts.append(P)
        else:
            n = E.neg(P)
            pts.extend(sorted([P, n], key=lambda t: t[1]))
    pts.sort()
    return pts


# ---------------------------------------------------------------------------
class CellClassifier:
    """The three oracles and the witnesses for one cell."""

    def __init__(self, F, E, desc, l, xE, x2E):
        self.F, self.E, self.desc, self.l = F, E, desc, l
        self.B = E.B
        self.oB = OracleB(desc)
        self.oC = OracleC(F, l)
        self.E0, self.Ej = desc.affine_basis(E.B)
        self.xE, self.x2E = xE, x2E

    def curve(self, xR):
        F, l = self.F, self.l
        Emat = self.desc.descended_E(self.B, xR)
        aff_ok = bool(np.array_equal(Emat, self.desc.affine_combine(self.E0, self.Ej, xR)))
        sA = oracle_A(F, self.B, xR, l)
        sB = self.oB(Emat)
        sC = self.oC(s3_coeffs(F, self.B, xR))
        wit = verify_witnesses(F, self.B, xR, Emat, sA, l, self.desc, curve_algebra=True)
        return {"s": len(sA), "s_A": len(sA), "s_B": len(sB), "s_C": len(sC),
                "oracle_agree": (sA == sB == sC), "sols": sA, "wit_fail": wit, "aff_ok": aff_ok,
                "rational_flag": rational_flag(self.E, xR, sA, l),
                "x2E_class": x2e_class(self.xE, self.x2E, xR)}

    def quick_s(self, xR):
        return len(oracle_A(self.F, self.B, xR, self.l))

    def regA_null(self, Emat):
        sB = self.oB(Emat)
        wit = verify_witnesses(self.F, None, None, Emat, sB, self.l, self.desc, curve_algebra=False)
        return {"s": len(sB), "s_B": len(sB), "sols": sB, "wit_fail": wit}

    def regB_null(self, coeffs):
        sC = self.oC(coeffs)
        wit = verify_witnesses(self.F, None, None, None, sC, self.l, None, curve_algebra=False, coeffs=coeffs)
        return {"s": len(sC), "s_C": len(sC), "sols": sC, "wit_fail": wit}


def affb_coeffs(F, alpha, xR):
    xR2 = F.mul(xR, xR)
    return (alpha[0], F.mul(alpha[1], xR2), F.mul(alpha[2], xR2), F.mul(alpha[3], xR), alpha[4])


def run_phase1_cell(F, cell, curve_obj, E, P, Qp, desc, seeds, counts, xE, x2E, subgroup_x, log):
    """cell: dict(n, l, cidx, label). counts: the chosen schedule's counts.
    Returns the JSON-serializable phase-1 record of the cell."""
    l = cell["l"]
    q = curve_obj["q"]
    MAXD = counts["reference_scan_max_draws"]
    out = {"cell": cell, "rejections": {}}
    cls = CellClassifier(F, E, desc, l, xE, x2E)
    classify = cls.curve

    # ---- F-S3 references (stream 01: ONE logged sequence per cell, AMD C-19)
    seq01 = SharedCurveSeq(E, P, Qp, q, seeds["ref"])
    st = seq01.reader()
    refs, scanned, short = select_references(curve_ref_candidates(st, classify, l), MAXD)
    out["F-S3"] = {"refs": refs, "ref_shortfall": short}
    out["rejections"]["ref"] = dict(scan_counts(scanned), R_is_O=st.rej_O)
    out["ref_scan"] = scanned
    ref_x = {r["x_R"] for r in refs}
    log(f"  F-S3 refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs]} shortfall={short}")

    # ---- F-S3 test targets (stream 02)
    st = CurveStream(E, P, Qp, q, seeds["test"])
    seen = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    targets = []
    while len(targets) < counts["F-S3"]:
        d = st.next()
        xR = d["x_R"]
        if xR in ref_x:
            rej["reference_collision"] += 1
            continue
        if xR in seen:
            rej["duplicate"] += 1
            continue
        seen.add(xR)
        t = {"idx": len(targets) + 1, "draw": st.draws, "a": d["a"], "b": d["b"], "x_R": xR,
             "degenerate": degenerate(xR, l)}
        t.update(classify(xR))
        targets.append(t)
    rej["R_is_O"] = st.rej_O
    rej["draws"] = st.draws
    out["rejections"]["test"] = rej
    out["F-S3"]["targets"] = targets
    s3x = seen | ref_x
    log(f"  F-S3 targets: {len(targets)} (degenerate {sum(t['degenerate'] for t in targets)}, "
        f"sat {sum(t['s'] >= 1 for t in targets)})")

    # ---- F-SAT (stream 03), with exact exhaustion detection
    pop, n_sub_nd = sat_population(F, E, E.B, l, subgroup_x)
    pop_vv = sat_population_vv(F, E.B, l, subgroup_x)
    avail = pop - s3x
    st = CurveStream(E, P, Qp, q, seeds["sat"])
    rej = {"degenerate": 0, "duplicate": 0, "reference_or_F-S3_target": 0, "unsat": 0}
    satt = []
    seen_sat = set()
    seen_all = set()
    stop = None
    HARD = counts["sat_scan_hard_cap_draws"]
    while len(satt) < counts["F-SAT"]:
        if len(seen_sat) == len(avail) and seen_sat == avail:
            stop = "population_exhausted"
            break
        if st.draws >= HARD:
            stop = "hard_cap"
            break
        d = st.next()
        xR = d["x_R"]
        if degenerate(xR, l):
            rej["degenerate"] += 1
            continue
        if xR in s3x:
            rej["reference_or_F-S3_target"] += 1
            continue
        if xR in seen_all:
            rej["duplicate"] += 1
            continue
        seen_all.add(xR)
        if cls.quick_s(xR) == 0:
            rej["unsat"] += 1
            continue
        seen_sat.add(xR)
        t = {"idx": len(satt) + 1, "draw": st.draws, "a": d["a"], "b": d["b"], "x_R": xR, "degenerate": False}
        t.update(classify(xR))
        satt.append(t)
    if stop is None:
        stop = "count_reached"
    rej["R_is_O"] = st.rej_O
    rej["draws"] = st.draws
    out["rejections"]["sat"] = rej
    out["F-SAT"] = {"targets": satt, "stop_reason": stop, "population_size_sat_subgroup_nondegenerate": len(pop),
                    "E_SAT_size": len(avail), "n_subgroup_abscissae_nondegenerate": n_sub_nd,
                    "E_SAT_cross_check": {"oracle_A_route_size": len(pop), "VxV_solve_route_size": len(pop_vv),
                                          "equal": pop == pop_vv,
                                          "only_oracle_A": sorted(pop - pop_vv)[:20], "only_VxV": sorted(pop_vv - pop)[:20],
                                          "fails_if": "the two sets differ (AMD C-17; INV-3 for the cell)"},
                    "P_sat_exact": {"numerator": len(pop), "denominator": n_sub_nd},
                    "population_available_after_exclusions": len(avail), "draws": st.draws,
                    "distinct_nondegenerate_new_x_seen": len(seen_all),
                    "unsat_rejections": rej["unsat"]}
    log(f"  F-SAT: {len(satt)} targets ({stop}; draws {st.draws}; population {len(pop)}, available {len(avail)})")

    # ---- F-PLANT (stream 04), with exact exhaustion detection
    FV = factor_base_points(E, l)
    satx = {t["x_R"] for t in satt}
    excl = s3x
    achievable = set()
    for i1 in range(len(FV)):
        for i2 in range(len(FV)):
            P1, P2 = FV[i1], FV[i2]
            if P1 == P2 or P1 == E.neg(P2):
                continue
            z = E.add(P1, P2)[0]
            if degenerate(z, l) or z in excl:
                continue
            achievable.add(z)
    g = gen(seeds["plant"])
    rej = {"P1_eq_pm_P2": 0, "z_in_V": 0, "duplicate": 0, "collides_F-S3": 0}
    plant = []
    pseen = set()
    draws = 0
    stop = None
    while len(plant) < counts["F-PLANT"]:
        if pseen == achievable:
            stop = "achievable_set_exhausted"
            break
        if draws >= counts["plant_hard_cap_draws"]:
            stop = "hard_cap"
            break
        i1 = draw_int(g, 0, len(FV))
        i2 = draw_int(g, 0, len(FV))
        draws += 1
        P1, P2 = FV[i1], FV[i2]
        if P1 == P2 or P1 == E.neg(P2):
            rej["P1_eq_pm_P2"] += 1
            continue
        z = E.add(P1, P2)[0]
        if degenerate(z, l):
            rej["z_in_V"] += 1
            continue
        if z in pseen:
            rej["duplicate"] += 1
            continue
        if z in excl:
            rej["collides_F-S3"] += 1
            continue
        pseen.add(z)
        t = {"idx": len(plant) + 1, "draw": draws, "i1": i1, "i2": i2, "P1": list(P1), "P2": list(P2),
             "x_R": z, "degenerate": False, "also_in_F-SAT": z in satx}
        t.update(classify(z))
        t["planted_witness"] = (P1[0] | (P2[0] << l))
        t["planted_witness_found"] = t["planted_witness"] in set(t["sols"])
        plant.append(t)
    if stop is None:
        stop = "count_reached"
    rej["draws"] = draws
    out["rejections"]["plant"] = rej
    out["F-PLANT"] = {"targets": plant, "factor_base_size": len(FV), "stop_reason": stop,
                      "achievable_distinct_z": len(achievable), "E_PLANT_size": len(achievable), "draws": draws}
    log(f"  F-PLANT: {len(plant)} targets ({stop}; |F_V| = {len(FV)}, achievable {len(achievable)})")

    # ---- F-RANDX (stream 05): references first, then targets from the same stream
    g = gen(seeds["randx"])
    counter = {"draws": 0}
    refs_x, scanned_x, short_x = select_references(randx_ref_candidates(g, classify, F.q, l, counter), MAXD)
    out["rejections"]["randx_refs"] = scan_counts(scanned_x)
    rx = {r["x_R"] for r in refs_x}
    seen = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tx = []
    d0 = counter["draws"]
    while len(tx) < counts["F-RANDX"]:
        xR = draw_int(g, 0, F.q)
        counter["draws"] += 1
        if xR in rx:
            rej["reference_collision"] += 1
            continue
        if xR in seen:
            rej["duplicate"] += 1
            continue
        seen.add(xR)
        t = {"idx": len(tx) + 1, "draw": counter["draws"], "x_R": xR, "degenerate": degenerate(xR, l)}
        t.update(classify(xR))
        tx.append(t)
    rej["draws_after_references"] = counter["draws"] - d0
    out["rejections"]["randx_targets"] = rej
    out["F-RANDX"] = {"refs": refs_x, "ref_shortfall": short_x, "targets": tx, "ref_scan": scanned_x}
    log(f"  F-RANDX refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_x]}; targets {len(tx)}")

    # ---- F-AFF (regime A; stream 06, one draw)
    A0, Aj = draw_affine_null(seeds["nullAff"], cls.E0, cls.Ej)

    def cls_aff(xR):
        Em = desc.affine_combine(A0, Aj, xR)
        alt = affine_combine_alt(A0, Aj, xR)
        c = cls.regA_null(Em)
        c["aff_ok"] = bool(np.array_equal(Em, alt))
        return c

    st = seq01.reader()
    refs_a, scanned_a, short_a = select_references(curve_ref_candidates(st, cls_aff, l), MAXD)
    s3t_x = {t["x_R"] for t in targets}
    ta = []
    for t0 in targets:
        t = {"idx": t0["idx"], "x_R": t0["x_R"], "degenerate": t0["degenerate"], "paired_F-S3_idx": t0["idx"]}
        t.update(cls_aff(t0["x_R"]))
        ta.append(t)
    out["F-AFF"] = {"refs": refs_a, "ref_shortfall": short_a, "targets": ta,
                    "A0_hex": E_to_hex(A0), "Aj_hex": [E_to_hex(x) for x in Aj],
                    "ref_x_collides_with_F-S3_test_x": sum(r["x_R"] in s3t_x for r in refs_a)}
    out["rejections"]["ref (rescan for F-AFF)"] = dict(scan_counts(scanned_a), R_is_O=st.rej_O)
    log(f"  F-AFF refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_a]}")

    # ---- F-NULLF2 (regime A; streams 07, 08)
    Upos, U = nullF2_union_support(cls.E0, cls.Ej)
    shape = cls.E0.shape
    g = gen(seeds["nullF2_ref"])

    def nf2_cands(g):
        seen_h = set()
        draw = 0
        while True:
            Em = draw_nullF2_instance(g, Upos, shape)
            draw += 1
            key = Em.tobytes()
            c = {"draw": draw, "E_hex": E_to_hex(Em)}
            if key in seen_h:
                c["status"] = "rejected_duplicate"
            else:
                seen_h.add(key)
                c.update(cls.regA_null(Em))
                c["status"] = "classified"
            yield c

    refs_n, scanned_n, short_n = select_references(nf2_cands(g), MAXD)
    refkeys = {tuple(r["E_hex"]) for r in refs_n}
    g = gen(seeds["nullF2_test"])
    seen_h = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tn = []
    draws = 0
    while len(tn) < counts["F-NULLF2"]:
        Em = draw_nullF2_instance(g, Upos, shape)
        draws += 1
        hx = tuple(E_to_hex(Em))
        if hx in refkeys:
            rej["reference_collision"] += 1
            continue
        if hx in seen_h:
            rej["duplicate"] += 1
            continue
        seen_h.add(hx)
        t = {"idx": len(tn) + 1, "draw": draws, "E_hex": list(hx), "x_R": None, "degenerate": False}
        t.update(cls.regA_null(Em))
        tn.append(t)
    rej["draws"] = draws
    out["rejections"]["nullF2_ref"] = scan_counts(scanned_n)
    out["rejections"]["nullF2_test"] = rej
    out["F-NULLF2"] = {"refs": refs_n, "ref_shortfall": short_n, "targets": tn,
                       "union_support_size_per_eq": [int(x) for x in U.sum(axis=1)],
                       "union_support_positions": Upos.tolist()}
    log(f"  F-NULLF2 refs: {[(r['selected_as'], r['s']) for r in refs_n]}")

    # ---- F-NULLB (regime B; streams 09, 10)
    def nb_draw(g):
        return tuple(draw_int(g, 1, F.q) for _ in range(5))

    g = gen(seeds["nullB_ref"])

    def nb_cands(g):
        seen_c = set()
        draw = 0
        while True:
            co = nb_draw(g)
            draw += 1
            c = {"draw": draw, "coeffs": list(co)}
            if co in seen_c:
                c["status"] = "rejected_duplicate"
            else:
                seen_c.add(co)
                c.update(cls.regB_null(co))
                c["status"] = "classified"
            yield c

    refs_b, scanned_b, short_b = select_references(nb_cands(g), MAXD)
    refco = {tuple(r["coeffs"]) for r in refs_b}
    g = gen(seeds["nullB_test"])
    seen_c = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tb = []
    draws = 0
    while len(tb) < counts["F-NULLB"]:
        co = nb_draw(g)
        draws += 1
        if co in refco:
            rej["reference_collision"] += 1
            continue
        if co in seen_c:
            rej["duplicate"] += 1
            continue
        seen_c.add(co)
        t = {"idx": len(tb) + 1, "draw": draws, "coeffs": list(co), "x_R": None, "degenerate": False}
        t.update(cls.regB_null(co))
        tb.append(t)
    rej["draws"] = draws
    out["rejections"]["nullB_ref"] = scan_counts(scanned_b)
    out["rejections"]["nullB_test"] = rej
    out["F-NULLB"] = {"refs": refs_b, "ref_shortfall": short_b, "targets": tb}
    log(f"  F-NULLB refs: {[(r['selected_as'], r['s']) for r in refs_b]}")

    # ---- F-AFFB (regime B; stream 11 drawn once; references by re-scanning stream 01)
    g = gen(seeds["affB"])
    alpha = [draw_int(g, 1, F.q) for _ in range(5)]

    def cls_affb(xR):
        co = affb_coeffs(F, alpha, xR)
        c = cls.regB_null(co)
        c["coeffs"] = list(co)
        return c

    # References (executor reading, pending Coordinator confirmation): the F-S3
    # references' x_R keep their role wherever the F-AFFB classification agrees
    # (spec null_families_B "evaluated ... at the F-S3 references' x_R");
    # unfilled roles are filled by re-scanning stream 01 in order (reference_rule).
    refs_ab = []
    used = set()
    for r in refs:
        c = cls_affb(r["x_R"])
        agrees = (r["s"] == 0) == (c["s"] == 0)
        if agrees:
            d = {"draw": r["draw"], "a": r.get("a"), "b": r.get("b"), "x_R": r["x_R"], "status": "classified",
                 "selected_as": r["selected_as"], "source": "F-S3 reference x_R (classifications agree)"}
            d.update(c)
            refs_ab.append(d)
            used.add(r["x_R"])
    need_u = [f"U{i}" for i in (1, 2, 3) if f"U{i}" not in {x["selected_as"] for x in refs_ab}]
    need_s = [f"S{i}" for i in (1, 2) if f"S{i}" not in {x["selected_as"] for x in refs_ab}]
    st = seq01.reader()
    scanned_ab = []
    s3t_set = {t["x_R"] for t in targets}
    if need_u or need_s:
        for cand in curve_ref_candidates(st, cls_affb, l):
            if cand["status"] == "classified" and cand["x_R"] not in used and cand["x_R"] not in s3t_set:
                if cand["s"] == 0 and need_u:
                    cand["selected_as"] = need_u.pop(0)
                    cand["source"] = "re-scan of stream 01"
                    refs_ab.append(cand)
                    used.add(cand["x_R"])
                elif cand["s"] >= 1 and need_s:
                    cand["selected_as"] = need_s.pop(0)
                    cand["source"] = "re-scan of stream 01"
                    refs_ab.append(cand)
                    used.add(cand["x_R"])
            scanned_ab.append(_scan_summary(cand))
            if not need_u and not need_s:
                break
            if cand["draw"] >= MAXD:
                break
    refs_ab.sort(key=lambda r: (r["selected_as"][0] != "U", r["selected_as"]))
    short_ab = {"unsat_missing": len(need_u), "sat_missing": len(need_s)}
    tab = []
    for t0 in targets[:counts["F-AFFB"]]:
        t = {"idx": t0["idx"], "x_R": t0["x_R"], "degenerate": t0["degenerate"], "paired_F-S3_idx": t0["idx"]}
        t.update(cls_affb(t0["x_R"]))
        tab.append(t)
    out["F-AFFB"] = {"refs": refs_ab, "ref_shortfall": short_ab, "targets": tab, "alpha": alpha,
                     "reference_rule": "AMD C-19: F-S3 reference x_R where the F-AFFB classification agrees; unfilled roles, in role-index order, by the next eligible x_R of the c01 sequence (non-degenerate, not already an F-AFFB reference, not an F-S3 target)"}
    out["stream01_log_length"] = len(seq01.log)
    out["rejections"]["ref (rescan for F-AFFB)"] = dict(scan_counts(scanned_ab), R_is_O=st.rej_O)
    log(f"  F-AFFB refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_ab]}; alpha={alpha}")
    return out

