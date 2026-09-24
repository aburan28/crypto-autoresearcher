"""Phase 1 (per cell): curve or V, points, per-cell C-SELF items, C-TR, and the
references and test targets of every family, with both satisfiability oracles
and witness re-verification.

Copied from EXP-CERTBIN-4e92d7/impl/families.py and generalised for
EXP-CERTBIN-3f06d1 (see impl-provenance.json):
  * a cell has its own curve (R1: h = 2, R2: h = 4 excluding the Stage-1
    curve, R3: the archived Stage-1 curve) and its own V basis (R1/R2: the
    polynomial basis; R3: a random rank-9 RREF basis);
  * the degenerate stratum is x_R in V by the linear-algebra test V.coord;
  * only one affine null draw (F-AFF-1); F-S3-REV uses the 200 lowest-idx
    F-S3 targets (engine level);
  * every curve-algebra instance carries its x(2E) class ([#E/2] test).

Every stream is numpy.random.Generator(numpy.random.PCG64(seed)); the draw
procedure of each stream is fixed in trial-plan-v1.json ("draw_procedures")
and consumed strictly in order. Every rejection is counted.
"""
import hashlib
import json

import numpy as np

from curve import Curve, is_prime
from macaulay import descended_E, affine_basis, affine_combine, NEQ, L, EQ_MONS
from oracles import oracle_A, oracle_B, verify_witnesses, rational_flag
from vspace import polynomial_V, draw_random_V, VBasis
from x2e import enumerate_classes, c_tr, CLASS_NAMES

Q17 = 1 << 17
VSIZE = 1 << L
STAGE1_CURVE = (97044, 126251)


def gen(seed):
    return np.random.Generator(np.random.PCG64(seed))


def draw_int(g, lo, hi):
    return int(g.integers(lo, hi))


# ---------------------------------------------------------------------------
def draw_curve(F, seed, want_h, exclude=None):
    """Draw (A, B) = (integers(0, 2^17), integers(0, 2^17)) in order; B = 0 is
    rejected; accept the first with #E = want_h * q, q prime, (A, B) not
    excluded."""
    g = gen(seed)
    rej = {"B_zero": 0, "order_not_h_times_prime": 0, "excluded_stage1_curve": 0}
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
        if not (n % want_h == 0 and is_prime(n // want_h)):
            rej["order_not_h_times_prime"] += 1
            tried.append({"A": A, "B": B, "order": n, "reason": f"order not {want_h}*q with q prime"})
            continue
        if exclude is not None and (A, B) == tuple(exclude):
            rej["excluded_stage1_curve"] += 1
            tried.append({"A": A, "B": B, "order": n, "reason": "equals the Stage-1 curve"})
            continue
        return E, {"A": A, "B": B, "order": n, "h": want_h, "q": n // want_h,
                   "draws": len(tried) + 1, "draws_rejected": len(tried), "rejections": rej,
                   "rejected_draws": tried}


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


# ---------------------------------------------------------------------------
def classify_curve_instance(F, E, xR, E0, Ej, V, cls):
    """Both oracles, witnesses, affine identity, rational flag, x(2E) class."""
    Emat = descended_E(F, E.B, xR, V.basis)
    aff_ok = bool(np.array_equal(Emat, affine_combine(E0, Ej, xR)))
    sB = oracle_B(Emat)
    sA = oracle_A(F, E.B, xR, V)
    wit = verify_witnesses(F, E.B, xR, Emat, sB, curve_algebra=True, V=V)
    return {
        "s": len(sB), "s_A": len(sA), "oracle_agree": (sA == sB),
        "sols": sB, "wit_fail": wit, "aff_ok": aff_ok,
        "rational_flag": rational_flag(E, xR, sB, V),
        "x2E_class": CLASS_NAMES[int(cls[xR])],
    }


def classify_null_instance(F, Emat):
    sB = oracle_B(Emat)
    wit = verify_witnesses(F, None, None, Emat, sB, curve_algebra=False)
    return {"s": len(sB), "s_A": None, "oracle_agree": None, "sols": sB, "wit_fail": wit,
            "rational_flag": None}


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
    refs.sort(key=lambda r: (r["selected_as"][0] != "U", r["selected_as"]))
    return refs, scanned, shortfall


def curve_ref_candidates(stream, classify, V):
    seen = set()
    while True:
        d = stream.next()
        xR = d["x_R"]
        c = {"draw": stream.draws, "a": d["a"], "b": d["b"], "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif V.contains(xR):
            seen.add(xR)
            c["status"] = "rejected_degenerate_reference"
        else:
            seen.add(xR)
            c.update(classify(xR))
            c["status"] = "classified"
        yield c


def randx_ref_candidates(g, classify, V):
    seen = set()
    draw = 0
    while True:
        xR = draw_int(g, 0, Q17)
        draw += 1
        c = {"draw": draw, "x_R": xR}
        if xR in seen:
            c["status"] = "rejected_duplicate"
        elif V.contains(xR):
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
def factor_base_points(E, V):
    pts = []
    for u in range(VSIZE):
        x = V.comb(u)
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


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cell_curve_and_V(F, cfg, log):
    """Curve, points and V of one cell (frozen streams S_curve/S_pts/S_V, or
    the archived Stage-1 curve for R3)."""
    info = {}
    if cfg["curve_mode"] == "draw":
        E, cinfo = draw_curve(F, cfg["seeds"]["S_curve"], cfg["h"],
                              exclude=STAGE1_CURVE if cfg.get("exclude_stage1_curve") else None)
        P, Qp, kQ, pinfo = draw_points(E, cinfo["h"], cinfo["q"], cfg["seeds"]["S_pts"])
        cinfo.update({"P": list(P), "Q": list(Qp), "k_Q": kQ, "points_draw": pinfo, "source": "drawn (S_curve, S_pts)"})
    else:
        p = cfg["stage1_curve_json"]
        got = sha256_file(p)
        if got != cfg["stage1_curve_sha256"]:
            raise RuntimeError(f"Stage-1 curve.json sha256 {got} != receipt {cfg['stage1_curve_sha256']}")
        cj = json.load(open(p))
        E = Curve(F, cj["A"], cj["B"])
        P, Qp = tuple(cj["P"]), tuple(cj["Q"])
        order = E.count_by_trace()
        if order != cj["order"]:
            raise RuntimeError("recount of the Stage-1 curve order differs from curve.json")
        cinfo = {"A": cj["A"], "B": cj["B"], "order": order, "h": cj["h"], "q": cj["q"],
                 "P": list(P), "Q": list(Qp), "k_Q": cj["k_Q"], "draws": 0, "draws_rejected": 0,
                 "rejections": {}, "rejected_draws": [],
                 "source": f"archived Stage-1 curve.json (sha256 {got}, matches the TASK-20260923-c2e57b receipt)",
                 "points_draw": {"source": "archived", "checks": {
                     "P_on_curve": E.on_curve(P), "qP_is_O": E.mul(cj["q"], P) is None,
                     "Q_on_curve": E.on_curve(Qp), "Q_eq_kQ_P": E.mul(cj["k_Q"], P) == Qp}}}
    if cfg["V_mode"] == "poly":
        V = polynomial_V()
        vinfo = {"source": "polynomial basis b_j = t^j (V = {deg < 9})", "draws": 0, "rank_rejections": 0}
    else:
        V, vinfo = draw_random_V(cfg["seeds"]["S_V"])
        vinfo["source"] = "drawn (S_V)"
    info["curve"] = cinfo
    info["V"] = {**V.as_json(), **vinfo}
    log(f"[{cfg['cell']}] curve A={cinfo['A']} B={cinfo['B']} #E={cinfo['order']} h={cinfo['h']} q={cinfo['q']}; V {V.label}")
    return E, P, Qp, V, info


def run_phase1_cell(F, cfg, counts, log, cell_selftest):
    """Everything of phase 1 for one cell. cell_selftest(F, E, order, V, cls,
    cellno) runs the per-cell C-SELF items; on failure the cell stops BEFORE
    any reference or target stream is drawn."""
    seeds = cfg["seeds"]
    NT = counts["test_targets"]
    NP = counts["planted_targets"]
    MAXD = counts["reference_scan_max_draws"]
    E, P, Qp, V, info = cell_curve_and_V(F, cfg, log)
    out = {"cell": cfg["cell"], "rejections": {}}
    out.update(info)
    curve_info = info["curve"]
    order, q = curve_info["order"], curve_info["q"]
    out["rejections"]["S_curve"] = curve_info.get("rejections")
    out["rejections"]["S_pts"] = curve_info.get("points_draw", {}).get("rejections")
    out["rejections"]["S_V"] = {"rank_rejections": info["V"].get("rank_rejections")}
    out["tau"] = [F.trace(1 << j) for j in range(17)]
    # x(2E) classes of every x (definition path), then C-TR
    log(f"[{cfg['cell']}] x(2E) enumeration over all 2^17 x")
    cls = enumerate_classes(E, order)
    out["C-TR"] = c_tr(E, order, cls)
    log(f"[{cfg['cell']}] C-TR pass={out['C-TR']['pass']} (x2E {out['C-TR']['count_x2E']}, Tr(A) = {out['C-TR']['Tr_A']})")
    st = cell_selftest(F, E, order, V, cls, cfg["c"])
    out["cell_selftest"] = st
    if not st["pass"]:
        out["stopped"] = "per-cell C-SELF failed; no reference or target stream drawn (SR-2)"
        log(f"[{cfg['cell']}] per-cell C-SELF FAILED; stop")
        return out, cls
    log(f"[{cfg['cell']}] per-cell C-SELF pass")

    E0, Ej = affine_basis(F, E.B, V.basis)
    classify = lambda xR: classify_curve_instance(F, E, xR, E0, Ej, V, cls)  # noqa: E731

    # ---- F-S3 references
    st_ = CurveStream(E, P, Qp, q, seeds["S_ref"])
    refs, scanned, short = select_references(curve_ref_candidates(st_, classify, V), MAXD)
    out["F-S3"] = {"refs": refs, "ref_scan": scanned, "ref_shortfall": short}
    out["rejections"]["S_ref"] = {"R_is_O": st_.rej_O,
                                  "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned),
                                  "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned),
                                  "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned),
                                  "draws": len(scanned)}
    ref_x = {r["x_R"] for r in refs}
    log(f"[{cfg['cell']}] F-S3 refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs]} shortfall={short}")

    # ---- F-S3 test targets
    st_ = CurveStream(E, P, Qp, q, seeds["S_test"])
    seen = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    targets = []
    while len(targets) < NT:
        d = st_.next()
        xR = d["x_R"]
        if xR in ref_x:
            rej["reference_collision"] += 1
            continue
        if xR in seen:
            rej["duplicate"] += 1
            continue
        seen.add(xR)
        t = {"idx": len(targets) + 1, "draw": st_.draws, "a": d["a"], "b": d["b"], "x_R": xR,
             "degenerate": V.contains(xR)}
        t.update(classify(xR))
        targets.append(t)
    rej["R_is_O"] = st_.rej_O
    rej["draws"] = st_.draws
    out["rejections"]["S_test"] = rej
    out["F-S3"]["targets"] = targets
    log(f"[{cfg['cell']}] F-S3 targets: {len(targets)} (degenerate {sum(t['degenerate'] for t in targets)}, "
        f"unsat {sum(1 for t in targets if not t['degenerate'] and t['s'] == 0)})")

    # ---- F-PLANT
    FV = factor_base_points(E, V)
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
        if V.contains(z):
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
        t["planted_witness"] = (V.coord(P1[0]) | (V.coord(P2[0]) << L))
        t["planted_witness_found"] = t["planted_witness"] in set(t["sols"])
        plant.append(t)
    rej["draws"] = draws
    out["rejections"]["S_plant"] = rej
    out["F-PLANT"] = {"targets": plant, "factor_base_size": len(FV)}
    log(f"[{cfg['cell']}] F-PLANT: {len(plant)} targets, |F_V| = {len(FV)}")

    # ---- F-RANDX
    g = gen(seeds["S_randx_ref"])
    refs_x, scanned_x, short_x = select_references(randx_ref_candidates(g, classify, V), MAXD)
    out["rejections"]["S_randx_ref"] = {
        "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned_x),
        "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned_x),
        "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned_x),
        "draws": len(scanned_x)}
    rx = {r["x_R"] for r in refs_x}
    g = gen(seeds["S_randx_test"])
    seen_x = set()
    rej = {"duplicate": 0, "reference_collision": 0}
    tx = []
    draws = 0
    while len(tx) < NT:
        xR = draw_int(g, 0, Q17)
        draws += 1
        if xR in rx:
            rej["reference_collision"] += 1
            continue
        if xR in seen_x:
            rej["duplicate"] += 1
            continue
        seen_x.add(xR)
        t = {"idx": len(tx) + 1, "draw": draws, "x_R": xR, "degenerate": V.contains(xR)}
        t.update(classify(xR))
        tx.append(t)
    rej["draws"] = draws
    out["rejections"]["S_randx_test"] = rej
    out["F-RANDX"] = {"refs": refs_x, "ref_scan": scanned_x, "ref_shortfall": short_x, "targets": tx,
                      "x_R_shared_with_F-S3_targets": sorted(t["idx"] for t in tx if t["x_R"] in seen)}
    log(f"[{cfg['cell']}] F-RANDX refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_x]}")

    # ---- F-AFF-1 (one draw per cell)
    fam = "F-AFF-1"
    A0, Aj = draw_affine_null(seeds["S_nullAff_draw1"], E0, Ej)

    def cls_aff(xR, A0=A0, Aj=Aj):
        Em = affine_combine(A0, Aj, xR)
        alt = affine_combine_alt(A0, Aj, xR)
        c = classify_null_instance(F, Em)
        c["aff_ok"] = bool(np.array_equal(Em, alt))
        c["x2E_class"] = CLASS_NAMES[int(cls[xR])]
        return c

    st_ = CurveStream(E, P, Qp, q, seeds["S_ref"])
    refs_a, scanned_a, short_a = select_references(curve_ref_candidates(st_, cls_aff, V), MAXD)
    s3_test_x = {t["x_R"] for t in targets}
    ta = []
    for t0 in targets:
        t = {"idx": t0["idx"], "x_R": t0["x_R"], "degenerate": t0["degenerate"], "paired_F-S3_idx": t0["idx"]}
        t.update(cls_aff(t0["x_R"]))
        ta.append(t)
    out[fam] = {"refs": refs_a, "ref_scan": scanned_a, "ref_shortfall": short_a, "targets": ta,
                "A0_hex": E_to_hex(A0), "Aj_hex": [E_to_hex(x) for x in Aj],
                "ref_x_collides_with_F-S3_test_x": sum(r["x_R"] in s3_test_x for r in refs_a)}
    out["rejections"]["S_nullAff_draw1"] = {"note": "drawn once; no rejection possible"}
    out["rejections"][f"S_ref(rescan for {fam})"] = {
        "R_is_O": st_.rej_O,
        "duplicate": sum(c["status"] == "rejected_duplicate" for c in scanned_a),
        "degenerate_reference": sum(c["status"] == "rejected_degenerate_reference" for c in scanned_a),
        "classified_not_selected": sum(c["status"] == "classified" and not c.get("selected_as") for c in scanned_a),
        "draws": len(scanned_a)}
    log(f"[{cfg['cell']}] {fam} refs: {[(r['selected_as'], r['x_R'], r['s']) for r in refs_a]}")

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
                       "union_support_size_per_eq": [int(x) for x in U.sum(axis=1)],
                       "union_support_positions": [int(x) for x in Upos]}
    log(f"[{cfg['cell']}] F-NULLF2 refs: {[(r['selected_as'], r['s']) for r in refs_n]}")
    return out, cls
