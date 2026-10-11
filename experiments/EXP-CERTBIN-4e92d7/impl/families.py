"""Phase 1: curve, points, references and test targets for every family, both
satisfiability oracles and witness re-verification.

Every stream is numpy.random.Generator(numpy.random.PCG64(seed)); the draw
procedure of each stream is fixed in trial-plan-v1.json ("draw_procedures")
and consumed strictly in order. Every rejection is counted.
"""
import numpy as np

from curve import Curve, is_prime
from macaulay import descended_E, affine_basis, affine_combine, NEQ, L, EQ_MONS
from oracles import oracle_A, oracle_B, verify_witnesses, rational_flag

Q17 = 1 << 17
VSIZE = 1 << L


def gen(seed):
    return np.random.Generator(np.random.PCG64(seed))


def draw_int(g, lo, hi):
    return int(g.integers(lo, hi))


# ---------------------------------------------------------------------------
def draw_curve(F, seed):
    g = gen(seed)
    rej = {"B_zero": 0, "cofactor_or_primality": 0}
    tried = []
    while True:
        A = draw_int(g, 0, Q17)
        B = draw_int(g, 0, Q17)
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
    g = gen(seed)
    rej = {"x_not_liftable": 0, "hP_is_O": 0}
    while True:
        x = draw_int(g, 0, Q17)
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


def degenerate(xR):
    return xR < VSIZE


# ---------------------------------------------------------------------------
def classify_curve_instance(F, E, xR, E0, Ej):
    """Both oracles, witnesses, affine identity, rational flag."""
    Emat = descended_E(F, E.B, xR)
    aff_ok = bool(np.array_equal(Emat, affine_combine(E0, Ej, xR)))
    sB = oracle_B(Emat)
    sA = oracle_A(F, E.B, xR)
    wit = verify_witnesses(F, E.B, xR, Emat, sB, curve_algebra=True)
    return {
        "s": len(sB), "s_A": len(sA), "oracle_agree": (sA == sB),
        "sols": sB, "wit_fail": wit, "aff_ok": aff_ok,
        "rational_flag": rational_flag(E, xR, sB),
    }


def classify_null_instance(F, Emat, curve_algebra=False):
    sB = oracle_B(Emat)
    wit = verify_witnesses(F, None, None, Emat, sB, curve_algebra=False)
    return {"s": len(sB), "s_A": None, "oracle_agree": None, "sols": sB, "wit_fail": wit,
            "rational_flag": None}


def stratum(inst):
    if inst.get("degenerate"):
        return "degenerate"
    return "sat" if inst["s"] >= 1 else "unsat"


def select_references(candidates_iter, max_draws=500, n_unsat=3, n_sat=2):
    """reference_rule: scan in order; classify each non-degenerate,
    non-duplicate instance; take the first n_unsat unsatisfiable and n_sat
    satisfiable; stop at 5 or after max_draws draws."""
    refs = []
    scanned = []
    nu = ns = 0
    for cand in candidates_iter:
        scanned.append(cand)
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
        if nu == n_unsat and ns == n_sat:
            break
        if cand["draw"] >= max_draws:
            break
    shortfall = {"unsat_missing": n_unsat - nu, "sat_missing": n_sat - ns}
    # order references U1, U2, U3, S1, S2
    refs.sort(key=lambda r: (r["selected_as"][0] != "U", r["selected_as"]))
    return refs, scanned, shortfall


def curve_ref_candidates(stream, classify):
    """Yield classified candidates from a curve stream (duplicates and
    degenerate x_R are rejections, recorded)."""
    seen = set()
    while True:
        d = stream.next()
        xR = d["x_R"]
        c = {"draw": stream.draws, "a": d["a"], "b": d["b"], "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif degenerate(xR):
            seen.add(xR)
            c["status"] = "rejected_degenerate_reference"
        else:
            seen.add(xR)
            c.update(classify(xR))
            c["status"] = "classified"
        yield c


def randx_ref_candidates(g, classify):
    seen = set()
    draw = 0
    while True:
        xR = draw_int(g, 0, Q17)
        draw += 1
        c = {"draw": draw, "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif degenerate(xR):
            seen.add(xR)
            c["status"] = "rejected_degenerate_reference"
        else:
            seen.add(xR)
            c.update(classify(xR))
            c["status"] = "classified"
        yield c


# ---------------------------------------------------------------------------
def support_positions(E0, Ej):
    s0 = np.flatnonzero(E0.reshape(-1))
    sj = [np.flatnonzero(x.reshape(-1)) for x in Ej]
    return s0, sj


def draw_affine_null(seed, E0, Ej):
    """E'^0 iid Bernoulli(1/2) on supp(E^0), then E'^j on supp(E^j) for
    j = 0..16, positions in row-major order of the 17 x 172 matrix."""
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
    rb = np.array([(r >> j) & 1 for j in range(NEQ)], dtype=np.int64)
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
    return [format(int("".join(str(int(b)) for b in row[::-1]), 2), "x") for row in Emat]


def E_from_hex(hx):
    E = np.zeros((NEQ, len(EQ_MONS)), dtype=np.uint8)
    for k, h in enumerate(hx):
        v = int(h, 16)
        for j in range(len(EQ_MONS)):
            E[k, j] = (v >> j) & 1
    return E


# ---------------------------------------------------------------------------
def factor_base_points(E):
    F = E.F
    pts = []
    for x in range(VSIZE):
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


def run_phase1(F, plan, log):
    seeds = plan["seeds"]
    cnt = plan["counts"]
    NT = cnt["test_targets"]
    NP = cnt["planted_targets"]
    MAXD = cnt["reference_scan_max_draws"]
    out = {"rejections": {}}

    E, curve_info = draw_curve(F, seeds["S_curve"])
    h, q = curve_info["h"], curve_info["q"]
    P, Qp, kQ, pinfo = draw_points(E, h, q, seeds["S_pts"])
    curve_info.update({"P": list(P), "Q": list(Qp), "k_Q": kQ, "points_draw": pinfo})
    out["curve"] = curve_info
    out["rejections"]["S_curve"] = curve_info["rejections"]
    out["rejections"]["S_pts"] = pinfo["rejections"]
    log(f"curve A={curve_info['A']} B={curve_info['B']} #E={curve_info['order']} h={h} q={q}")

    E0, Ej = affine_basis(F, E.B)
    classify = lambda xR: classify_curve_instance(F, E, xR, E0, Ej)  # noqa: E731

    # ---- F-S3 references
    st = CurveStream(E, P, Qp, q, seeds["S_ref"])
    refs, scanned, short = select_references(curve_ref_candidates(st, classify), MAXD)
    out["F-S3"] = {"refs": refs, "ref_scan": scanned, "ref_shortfall": short,
                   "ref_stream_rej_R_is_O": st.rej_O}
    out["rejections"]["S_ref"] = {"R_is_O": st.rej_O,
                                  "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned),
                                  "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned),
                                  "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned),
                                  "draws": len(scanned)}
    ref_x = {r["x_R"] for r in refs}
    log(f"F-S3 refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs]} shortfall={short}")

    # ---- F-S3 test targets
    st = CurveStream(E, P, Qp, q, seeds["S_test"])
    seen = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    targets = []
    while len(targets) < NT:
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
             "degenerate": degenerate(xR)}
        t.update(classify(xR))
        targets.append(t)
    rej["R_is_O"] = st.rej_O
    rej["draws"] = st.draws
    out["rejections"]["S_test"] = rej
    out["F-S3"]["targets"] = targets
    log(f"F-S3 targets: {len(targets)} (degenerate {sum(t['degenerate'] for t in targets)})")

    # ---- F-PLANT
    FV = factor_base_points(E)
    g = gen(seeds["S_plant"])
    s3x = seen | ref_x
    rej = {"P1_eq_pm_P2": 0, "z_in_V": 0, "duplicate": 0, "collides_F-S3": 0}
    plant = []
    pseen = set()
    draws = 0
    while len(plant) < NP:
        i1 = draw_int(g, 0, len(FV))
        i2 = draw_int(g, 0, len(FV))
        draws += 1
        P1, P2 = FV[i1], FV[i2]
        if P1 == P2 or P1 == E.neg(P2):
            rej["P1_eq_pm_P2"] += 1
            continue
        z = E.add(P1, P2)[0]
        if degenerate(z):
            rej["z_in_V"] += 1
            continue
        if z in pseen:
            rej["duplicate"] += 1
            continue
        if z in s3x:
            rej["collides_F-S3"] += 1
            continue
        pseen.add(z)
        t = {"idx": len(plant) + 1, "draw": draws, "i1": i1, "i2": i2, "P1": list(P1), "P2": list(P2),
             "x_R": z, "degenerate": False}
        t.update(classify(z))
        t["planted_witness"] = (P1[0] | (P2[0] << L))
        t["planted_witness_found"] = t["planted_witness"] in set(t["sols"])
        plant.append(t)
    rej["draws"] = draws
    out["rejections"]["S_plant"] = rej
    out["F-PLANT"] = {"targets": plant, "factor_base_size": len(FV)}
    log(f"F-PLANT: {len(plant)} targets, |F_V| = {len(FV)}")

    # ---- F-RANDX
    g = gen(seeds["S_randx_ref"])
    refs_x, scanned_x, short_x = select_references(randx_ref_candidates(g, classify), MAXD)
    out["rejections"]["S_randx_ref"] = {
        "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned_x),
        "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned_x),
        "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned_x),
        "draws": len(scanned_x)}
    rx = {r["x_R"] for r in refs_x}
    g = gen(seeds["S_randx_test"])
    seen = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tx = []
    draws = 0
    while len(tx) < NT:
        xR = draw_int(g, 0, Q17)
        draws += 1
        if xR in rx:
            rej["reference_collision"] += 1
            continue
        if xR in seen:
            rej["duplicate"] += 1
            continue
        seen.add(xR)
        t = {"idx": len(tx) + 1, "draw": draws, "x_R": xR, "degenerate": degenerate(xR)}
        t.update(classify(xR))
        tx.append(t)
    rej["draws"] = draws
    out["rejections"]["S_randx_test"] = rej
    out["F-RANDX"] = {"refs": refs_x, "ref_scan": scanned_x, "ref_shortfall": short_x, "targets": tx}
    log(f"F-RANDX refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_x]}")

    # ---- F-AFF-1..3
    for d in (1, 2, 3):
        fam = f"F-AFF-{d}"
        A0, Aj = draw_affine_null(seeds[f"S_nullAff_draw{d}"], E0, Ej)

        def cls_aff(xR, A0=A0, Aj=Aj):
            Em = affine_combine(A0, Aj, xR)
            alt = affine_combine_alt(A0, Aj, xR)
            c = classify_null_instance(F, Em)
            c["aff_ok"] = bool(np.array_equal(Em, alt))
            return c

        st = CurveStream(E, P, Qp, q, seeds["S_ref"])
        refs_a, scanned_a, short_a = select_references(curve_ref_candidates(st, cls_aff), MAXD)
        s3_test_x = {t["x_R"] for t in targets}
        ta = []
        for t0 in targets:
            t = {"idx": t0["idx"], "x_R": t0["x_R"], "degenerate": t0["degenerate"],
                 "paired_F-S3_idx": t0["idx"]}
            t.update(cls_aff(t0["x_R"]))
            ta.append(t)
        out[fam] = {"refs": refs_a, "ref_scan": scanned_a, "ref_shortfall": short_a, "targets": ta,
                    "A0_hex": E_to_hex(A0), "Aj_hex": [E_to_hex(x) for x in Aj],
                    "ref_x_collides_with_F-S3_test_x": sum(r["x_R"] in s3_test_x for r in refs_a)}
        out["rejections"][f"S_nullAff_draw{d}"] = {"note": "drawn once; no rejection possible"}
        out["rejections"][f"S_ref(rescan for {fam})"] = {
            "R_is_O": st.rej_O,
            "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned_a),
            "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned_a),
            "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned_a),
            "draws": len(scanned_a)}
        log(f"{fam} refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_a]}")

    # ---- F-NULLF2
    Upos, U = nullF2_union_support(E0, Ej)
    shape = E0.shape
    g = gen(seeds["S_nullF2_ref"])

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
                c.update(classify_null_instance(F, Em))
                c["status"] = "classified"
            yield c

    refs_n, scanned_n, short_n = select_references(nf2_cands(g), MAXD)
    refkeys = {tuple(r["E_hex"]) for r in refs_n}
    g = gen(seeds["S_nullF2_test"])
    seen_h = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tn = []
    draws = 0
    while len(tn) < NT:
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
        t.update(classify_null_instance(F, Em))
        tn.append(t)
    rej["draws"] = draws
    out["rejections"]["S_nullF2_ref"] = {
        "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned_n),
        "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned_n),
        "draws": len(scanned_n)}
    out["rejections"]["S_nullF2_test"] = rej
    out["F-NULLF2"] = {"refs": refs_n, "ref_scan": scanned_n, "ref_shortfall": short_n, "targets": tn,
                       "union_support_size_per_eq": [int(x) for x in U.sum(axis=1)]}
    log(f"F-NULLF2 refs: {[(r['selected_as'], r['s']) for r in refs_n]}")
    return out
