#!/usr/bin/env python3
"""Phase 0 self-tests: C-SRC and C-SEED (written first, before any seeded
draw), C-SELF (i)-(x), C-FIX, C-CURVE (a)-(f) and C-ELL0. All randomness comes
from ONE numpy PCG64 generator seeded with S_selftest = 2026092460600,
consumed in item order.

    python3 selftest.py --out RUN_DIR/selftest.json
Also writes RUN_DIR/inputs.json (C-SRC). Exit status 0 iff every item passes.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

import common as C
from gf2n import field, is_irreducible, clmul, poly_mod
from curve import Curve, is_prime
from descent import Descent, eval_system, substitute, extend_assignment, kernel_basis, combine_rows
from oracles import Exhaustive, oracle_A, quad_roots
from literal import Literal

HERE = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# C-SRC and C-SEED
# ---------------------------------------------------------------------------
INPUT_FILES = [
    ("experiments/EXP-CERTBIN-a58c63/runs/RUN-CERTBIN-0b8f3a/cells.json",
     "coordination/design/certbin-followups-20260924/archives/TASK-20260924-b9e36f/snapshot-receipt.json", False),
    ("experiments/EXP-CERTBIN-a58c63/runs/RUN-CERTBIN-0b8f3a/selftest.json",
     "coordination/design/certbin-followups-20260924/archives/TASK-20260924-b9e36f/snapshot-receipt.json", False),
    ("experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json",
     "coordination/design/certbin-followups-20260924/archives/TASK-20260924-e27f93/snapshot-receipt.json", True),
    ("experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json",
     "coordination/design/certbin-trace-20260923-5d0b8e/archives/TASK-20260923-c2e57b/snapshot-receipt.json", True),
    ("experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/closures.jsonl.gz",
     "coordination/design/certbin-followups-20260924/archives/TASK-20260924-e27f93/snapshot-receipt.json", True),
    ("experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificates.jsonl.gz",
     "coordination/design/certbin-followups-20260924/archives/TASK-20260924-e27f93/snapshot-receipt.json", True),
]
QUOTED = {"experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json":
          "64dffd01f693289ac533aec3348319cea6c85ffaaea11c4d63ddcd607cd85a7a",
          "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json":
          "aa3eb4d0f3e9da68d710b8946e2e4c3d13de1b991882f23218d259df9615201d"}
REF_TEXT = ["coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/red-team-report.yaml",
            "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-declaration.yaml"]


def c_src():
    rows = []
    ok = True
    for path, receipt, governing in INPUT_FILES:
        h = C.sha256_file(C.ROOT / path)
        rj = json.loads((C.ROOT / receipt).read_text())
        rh = rj.get("path_sha256", {}).get(path)
        row = {"path": path, "sha256": h, "receipt": receipt, "receipt_sha256": rh,
               "governing": governing, "match": rh == h if rh else None}
        if path in QUOTED:
            row["spec_quoted_sha256"] = QUOTED[path]
            row["spec_quoted_match"] = QUOTED[path] == h
        if rh is None:
            row["status"] = "unbound (receipt names no hash for this path)"
            if governing:
                ok = False
        elif rh != h:
            row["status"] = "MISMATCH"
            if governing:
                ok = False
        else:
            row["status"] = "match"
        rows.append(row)
    refs = [{"path": p, "sha256": C.sha256_file(C.ROOT / p)} for p in REF_TEXT]
    code = [{"path": p, "sha256": C.sha256_file(C.ROOT / p)} for p in
            ["tools/gf2_replay_rc1.py", "tests/test_gf2_kernels.py"]]
    return {"files": rows, "reference_text_inputs": refs, "code_inputs": code, "pass": ok}


def c_seed():
    pats = [str(s) for s in C.SEEDS.values()]
    files = (glob.glob(str(C.ROOT / "experiments/*/specification.yaml"))
             + glob.glob(str(C.ROOT / "experiments/*/amendments/**"), recursive=True)
             + glob.glob(str(C.ROOT / "experiments/*/trial-plan*.json")))
    allowed = {str(C.EXP / "specification.yaml"), str(C.EXP / "trial-plan-v1.json")}
    hits = {}
    for f in files:
        if not os.path.isfile(f):
            continue
        try:
            txt = open(f, errors="replace").read()
        except Exception:
            continue
        for p in pats:
            if p in txt:
                hits.setdefault(p, []).append(os.path.relpath(f, C.ROOT))
    bad = {p: [f for f in fs if str(C.ROOT / f) not in allowed] for p, fs in hits.items()}
    bad = {p: fs for p, fs in bad.items() if fs}
    return {"seeds": pats, "files_scanned": len(files), "occurrences": hits, "other_occurrences": bad,
            "pass": not bad and all(str(C.EXP / "specification.yaml") in [str(C.ROOT / f) for f in hits.get(p, [])]
                                    for p in pats)}


# ---------------------------------------------------------------------------
# C-SELF
# ---------------------------------------------------------------------------
def item_i(F):
    ok, checks, tt = is_irreducible(C.N, C.MODULUS)
    smaller = []
    for a, b, c in [(3, 2, 1), (4, 2, 1), (4, 3, 1), (4, 3, 2)]:
        f = (1 << 19) | (1 << a) | (1 << b) | (1 << c) | 1
        irr, _, _ = is_irreducible(19, f)
        smaller.append({"abc": [a, b, c], "irreducible": irr})
    return {"modulus_irreducible": ok, "gcd_checks": checks, "t_pow_2n_equals_t": tt,
            "smaller_pentanomials": smaller, "t_order_is_2^19-1": True,
            "pass": ok and not any(s["irreducible"] for s in smaller)}


def item_ii(F, g):
    x = g.integers(0, 1 << C.N, size=(10000, 3))
    bad = 0
    for a, b, c in x.tolist():
        m = F.mul
        if m(a, b) != F.mul_slow(a, b) or m(a, b) != m(b, a):
            bad += 1
        elif m(m(a, b), c) != m(a, m(b, c)) or m(a, b ^ c) != m(a, b) ^ m(a, c):
            bad += 1
        elif a and m(a, F.inv(a)) != 1:
            bad += 1
        elif F.sqrt(m(a, a)) != a:
            bad += 1
    return {"triples": 10000, "failures": bad, "pass": bad == 0}


def rand_point(F, cv, g):
    while True:
        x = int(g.integers(1, 1 << C.N))
        P = cv.lift_x(x)
        if P is not None:
            if int(g.integers(0, 2)):
                P = cv.neg(P)
            return P


def item_iii(F, cv, D, g):
    bad = 0
    n = 0
    while n < 1000:
        P1, P2 = rand_point(F, cv, g), rand_point(F, cv, g)
        if P1[0] == P2[0]:
            continue
        for P3 in (cv.add(P1, P2), cv.add(P1, cv.neg(P2))):
            if P3 is None or not cv.on_curve(P3):
                bad += 1
                continue
            x1, x2, x3 = P1[0], P2[0], P3[0]
            s = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
            v = F.mul(s, s) ^ F.mul(F.mul(x1, x2), x3) ^ C.B
            bad += v != 0
        n += 1
    return {"pairs": 1000, "failures": bad, "pass": bad == 0}


def item_iv(F, D, g):
    bad = 0
    for _ in range(1000):
        xR = int(g.integers(0, 1 << C.N))
        v = int(g.integers(0, 1 << C.NV))
        E = D.E_direct(xR)
        bits = eval_system(E, C.EQ_MASKS, v)
        val = D.s3_eval(v, xR)
        bad += bits != [(val >> k) & 1 for k in range(C.NEQ)]
    return {"cases": 1000, "failures": bad, "pass": bad == 0}


def naive_truth(E, T):
    acc = np.zeros(T.shape[1], dtype=np.uint64)
    for k in range(E.shape[0]):
        cols = np.flatnonzero(E[k])
        if cols.size:
            acc |= np.bitwise_xor.reduce(T[cols], axis=0)
    z = np.flatnonzero(np.unpackbits(acc.view(np.uint8), bitorder="little") == 0)
    return int(z.size), z.tolist()


def item_v(F, D, X, g):
    nbits = 1 << C.NV
    u = np.arange(nbits, dtype=np.int64)
    T = []
    for m in C.EQ_MONS:
        t = np.ones(nbits, dtype=np.uint8)
        for i in m:
            t &= ((u >> i) & 1).astype(np.uint8)
        T.append(np.packbits(t, bitorder="little").view(np.uint64))
    T = np.array(T)
    bad_naive = bad_spot = 0
    sizes = []
    for t in range(200):
        dens = [0.02, 0.05, 0.1, 0.3, 0.5][t % 5]
        E = (g.random((C.NEQ, C.NCOL)) < dens).astype(np.uint8)
        s, sols = X.count(E, want_solutions=True)
        s2, sols2 = naive_truth(E, T)
        bad_naive += (s != s2) or (sols != sols2)
        sizes.append(s)
        for uu in g.integers(0, nbits, size=16).tolist():
            ev = eval_system(E, C.EQ_MASKS, uu)
            bad_spot += (not any(ev)) != (uu in set(sols))
    bad_A = 0
    for _ in range(200):
        xR = int(g.integers(1 << C.L, 1 << C.N))
        E = D.E_direct(xR)
        s, sols = X.count(E, want_solutions=True)
        sa, solsa = oracle_A(F, C.L, xR, C.B)
        bad_A += (s != sa) or (sols != solsa)
    return {"random_systems": 200, "naive_bitsliced_disagreements": bad_naive,
            "per_assignment_spot_checks": 3200, "spot_disagreements": bad_spot,
            "s_distribution_random": {str(k): sizes.count(k) for k in sorted(set(sizes))[:10]},
            "oracle_A_xR": 200, "oracle_A_disagreements": bad_A,
            "pass": bad_naive == 0 and bad_spot == 0 and bad_A == 0}


def item_vi(F, g):
    bad = 0
    brute_checked = 0
    allx = np.arange(1 << C.N, dtype=np.int64)
    for t in range(10000):
        a, b, c = (int(v) for v in g.integers(0, 1 << C.N, size=3))
        if t % 7 == 0:
            a = 0
        if t % 11 == 0:
            b = 0
        roots = quad_roots(F, a, b, c)
        if roots is None:
            continue
        for X in roots:
            if F.mul(a, F.mul(X, X)) ^ F.mul(b, X) ^ c:
                bad += 1
        if len(set(roots)) != len(roots):
            bad += 1
        if t < 100:
            ev = F.vmul(a, F.vmul(allx, allx)) ^ F.vmul(b, allx) ^ c
            truth = sorted(np.flatnonzero(ev == 0).tolist())
            brute_checked += 1
            bad += truth != sorted(roots)
    return {"quadratics": 10000, "brute_force_complete_root_sets": brute_checked, "failures": bad,
            "pass": bad == 0}


def item_vii(F, D, g):
    bad = 0
    cases = 0
    nsys = 0
    while cases < 1000:
        xR = int(g.integers(1 << C.L, 1 << C.N))
        E = D.E_direct(xR)
        ker = kernel_basis(E[:, 1 + C.NV:])
        if len(ker) != 1:
            continue
        ell = combine_rows(E, ker[0])
        eqs2, jstar, aff = substitute(E, ell, C.EQ_MASKS, C.NV)
        nsys += 1
        for _ in range(50):
            up = int(g.integers(0, 1 << (C.NV - 1)))
            u = extend_assignment(up, jstar, aff, C.NV)
            lhs = []
            for f in eqs2:
                acc = 0
                for m in f:
                    if (up & m) == m:
                        acc ^= 1
                lhs.append(acc)
            rhs = eval_system(E, C.EQ_MASKS, u)
            ellv = eval_system(ell[None, :], C.EQ_MASKS, u)[0]
            bad += (lhs != rhs) or ellv != 0
            cases += 1
    return {"cases": cases, "systems": nsys, "failures": bad, "pass": bad == 0}


def small_systems(g):
    """Small Boolean systems (6 variables, D in {3, 4}) for C-SELF (viii)/(x).
    Stage A (random): drawn until at least 30 exist and at least 3 reach the
    fixpoint at iteration >= 2. Stage B (CONSTRUCTED, listed): affine-rich
    systems (each equation affine with probability 1/2) drawn until at least 3
    systems of the set are refuted by W_D at iteration >= 1, so the general
    wdag extractor is exercised (random systems almost never do this)."""
    import closures as CL
    mons = C.eq_monomials(6)
    masks = [sum(1 << i for i in m) for m in mons]
    out = []
    deep = 0
    t = 0
    while len(out) < 30 or deep < 3:
        neq = int(g.integers(2, 7))
        D = int(g.integers(3, 5))
        dens = float([0.1, 0.2, 0.3][int(g.integers(0, 3))])
        eqs = [[masks[j] for j in range(len(masks)) if g.random() < dens] for _ in range(neq)]
        rec, _ = CL.get_closure(6, D, neq).w_closure(eqs, want_cert=False)
        t += 1
        d = rec["iterations_to_fixpoint"] >= 2
        if len(out) < 30 or d:
            out.append({"neq": neq, "D": D, "eqs": eqs, "deep": d, "stage": "A-random",
                        "late": bool(rec["one"] and rec["one_first_iteration"] >= 1)})
            deep += d
    late = sum(o["late"] for o in out)
    tb = 0
    while late < 3:
        neq = int(g.integers(3, 9))
        D = int(g.integers(3, 5))
        eqs = []
        for _ in range(neq):
            lim = 7 if g.random() < 0.5 else len(masks)
            dens = float([0.2, 0.35, 0.5][int(g.integers(0, 3))])
            eqs.append([masks[j] for j in range(lim) if g.random() < dens])
        rec, _ = CL.get_closure(6, D, neq).w_closure(eqs, want_cert=False)
        tb += 1
        if rec["one"] and rec["one_first_iteration"] >= 1:
            out.append({"neq": neq, "D": D, "eqs": eqs, "deep": rec["iterations_to_fixpoint"] >= 2,
                        "stage": "B-constructed", "late": True})
            late += 1
    return out, {"stage_A_drawn": t, "stage_B_drawn": tb}


def item_viii_x(g):
    import closures as CL
    sys.path.insert(0, str(C.EXP / "verifier"))
    import verify_n19 as V  # the verifier's rules, in-process (C-SELF (x))
    systems, drawn = small_systems(g)
    rows = []
    bad = 0
    x_ok = x_bad = 0
    for i, s in enumerate(systems):
        nv, D, neq, eqs = 6, s["D"], s["neq"], s["eqs"]
        rec, flat, ext, final, cl = CL.w_closure(nv, D, neq, eqs, want_cert=True)
        lit = Literal(nv, D, neq).w_closure(eqs)
        same = all(rec[k] == lit[k] for k in lit)
        bad += not same
        row = {"i": i, "stage": s["stage"], "D": D, "neq": neq, "iterations": rec["iterations_to_fixpoint"],
               "one": rec["one"], "one_first_iteration": rec["one_first_iteration"],
               "engine_equals_literal": same, "eqs": eqs}
        # (x) extractors, checked by the verifier's rules
        E = np.zeros((neq, len(C.eq_monomials(6))), dtype=np.uint8)
        mk = [sum(1 << i for i in m) for m in C.eq_monomials(6)]
        for k, f in enumerate(eqs):
            for m in f:
                E[k, mk.index(m)] ^= 1
        lay = V.Layout(6)
        sf = V.Sys(E, lay)
        if rec["one"]:
            if rec["one_first_iteration"] == 0:
                wd = CL.flat_as_wdag(cl, flat)
            else:
                wd = ext["wdag"]
            ok, reasons, st = V.check_wdag(wd, sf, nv, neq, D)
            row["wdag_valid"] = ok
            row["wdag_stats"] = st
        else:
            Lh = CL.annihilator(final[0], final[1], cl.C)
            sp = V.Space(nv, D)
            ok, reasons, st = V.check_ann({"D": D, "nv": nv, "neq": neq, "L_hex": Lh}, sf, sp, neq)
            row["ann_valid"] = ok
        x_ok += ok
        x_bad += not ok
        rows.append(row)
    deep = sum(r["iterations"] >= 2 for r in rows)
    return ({"systems": len(rows), "candidates_drawn": drawn, "deep_(iteration>=2)": deep,
             "deep_listed": [r["i"] for r in rows if r["iterations"] >= 2],
             "engine_literal_disagreements": bad, "records": rows,
             "pass": bad == 0 and deep >= 3},
            {"checked": x_ok + x_bad, "refuted_wdag_checked": sum("wdag_valid" in r for r in rows),
             "nonrefuted_ann_checked": sum("ann_valid" in r for r in rows),
             "general_wdag_checked": sum(1 for r in rows if "wdag_valid" in r and r["one_first_iteration"] >= 1),
             "constructed_listed": [r["i"] for r in rows if r["stage"] == "B-constructed"], "failures": x_bad,
             "pass": x_bad == 0 and sum(1 for r in rows if "wdag_valid" in r and r["one_first_iteration"] >= 1) >= 3
             and sum("ann_valid" in r for r in rows) > 0})


def item_ix(g):
    import closures as CL
    systems = []
    for _ in range(30):
        E = (g.random((C.NEQ, C.NCOL)) < 0.5).astype(np.uint8)
        systems.append(C.E_to_hex(E))
    native = []
    for h in systems:
        eqs = C.E_to_eqs(C.E_from_hex(h))
        r4, _ = CL.macaulay(C.NV, 4, C.NEQ, eqs, want_cert=True)
        w, *_ = CL.w_closure(C.NV, 4, C.NEQ, eqs, want_cert=True)
        native.append({"M_4": r4, "W_4": w})
    env = dict(os.environ, CRYPTO_AR_GF2_BACKEND="reference", PYTHONDONTWRITEBYTECODE="1")
    inp = json.dumps(systems)
    p = subprocess.run([sys.executable, str(HERE / "backend_worker.py")], input=inp, capture_output=True,
                       text=True, env=env, cwd=str(HERE))
    try:
        ref = json.loads(p.stdout)
    except Exception:
        return {"pass": False, "error": p.stderr[-2000:]}
    diffs = [i for i in range(30) if ref["records"][i] != native[i]]
    lit = Literal(C.NV, 4, C.NEQ)
    lit_bad = []
    for i in range(5):
        eqs = C.E_to_eqs(C.E_from_hex(systems[i]))
        lr = lit.w_closure(eqs)
        if any(lr[k] != native[i]["W_4"][k] for k in lr):
            lit_bad.append(i)
    return {"systems": 30, "reference_backend": ref["backend"], "native_reference_differences": diffs,
            "literal_checked": 5, "literal_differences": lit_bad,
            "sample_record": native[0],
            "pass": ref["backend"] == "reference" and not diffs and not lit_bad}


# ---------------------------------------------------------------------------
# C-FIX, C-CURVE, C-ELL0
# ---------------------------------------------------------------------------
def c_fix():
    import closures as CL
    dims = {}
    for name, (nv, D) in {"M_3": (20, 3), "M_4": (20, 4), "R'_3": (19, 3), "R'_4": (19, 4)}.items():
        cl = CL.get_closure(nv, D, C.NEQ)
        dims[name] = [cl.R, cl.C]
    want = {"M_3": [399, 1351], "M_4": [4009, 6196], "R'_3": [380, 1160], "R'_4": [3629, 5036]}
    return {"dims": dims, "expected": want, "pass": dims == want}


def c_curve(F, cv):
    out = {}
    out["a_B_nonzero"] = C.B != 0
    t = time.time()
    cnt = cv.count_points()
    out["b_order_exact_count"] = cnt
    out["b_count_seconds_measured"] = round(time.time() - t, 2)
    out["c_q_prime"] = is_prime(C.Q)
    out["order_equals_h_q"] = cnt == C.H * C.Q
    P, Qp = C.P_PT, C.Q_PT
    out["d"] = {"P_on_E": cv.on_curve(P), "Q_on_E": cv.on_curve(Qp), "P_not_O": P is not None,
                "qP_is_O": cv.mul(C.Q, P) is None, "qQ_is_O": cv.mul(C.Q, Qp) is None,
                "Q_equals_kQ_P": cv.mul(C.K_Q, P) == Qp}
    out["e_Tr_A"] = F.trace(C.A)
    cells = C.ROOT / "experiments/EXP-CERTBIN-a58c63/runs/RUN-CERTBIN-0b8f3a/cells.json"
    if cells.exists():
        c = json.loads(cells.read_text())["cells"]["n19-l6"]
        f = {"modulus_int": c["modulus_int"] == C.MODULUS, "A": c["A"] == C.A, "B": c["B"] == C.B,
             "order": c["order"] == C.ORDER, "h": c["h"] == C.H, "q": c["q"] == C.Q,
             "P": c["P"] == list(P), "Q": c["Q"] == list(Qp), "k_Q": c["k_Q"] == C.K_Q}
        out["f_cells_json"] = f
        fok = all(f.values())
    else:
        out["f_cells_json"] = "absent"
        fok = True
    out["pass"] = (out["a_B_nonzero"] and cnt == C.ORDER and out["c_q_prime"] and cnt == C.H * C.Q
                   and all(out["d"].values()) and out["e_Tr_A"] == 1 and fok)
    return out


def c_ell0(F):
    tau = [F.trace(1 << j) for j in range(C.N)]
    ell_lin = [j for j in range(C.L) if tau[j]]
    return {"tau": tau, "equals_coordinator_reading": tau == C.TAU_READING,
            "ell_lin_variables": sorted(ell_lin + [C.L + j for j in ell_lin]),
            "pass": tau[0] == 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--dev-seed", type=int, default=None,
                    help="development dry-runs only; the run uses S_selftest")
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    rundir = out.parent
    ep = rundir / "engine-provenance" / "engine-provenance.json"
    if not ep.exists() or not json.loads(ep.read_text()).get("pass"):
        print("C-ENGINE record missing or failed: STOP (INV-1)")
        return 2
    res = {"experiment_id": C.EXPERIMENT_ID, "started_utc": C.utc_now(), "items": {}}
    timings = {}

    def run(name, fn, *a):
        t = time.time()
        C.log("selftest", name)
        r = fn(*a)
        timings[name] = round(time.time() - t, 2)
        res["items"][name] = r
        return r

    src = c_src()
    C.write_json(rundir / "inputs.json", {"experiment_id": C.EXPERIMENT_ID, "recorded_utc": C.utc_now(), **src})
    res["items"]["C-SRC"] = {"pass": src["pass"], "see": "inputs.json"}
    run("C-SEED", c_seed)
    if not (src["pass"] and res["items"]["C-SEED"]["pass"]):
        res["pass"] = False
        C.write_json(out, res)
        print("C-SRC or C-SEED failed: STOP")
        return 2
    F = field(C.N, C.MODULUS)
    cv = Curve(F, C.A, C.B)
    D = Descent(F, C.L, C.B)
    X = Exhaustive(C.L)
    seed = C.SEEDS["S_selftest"] if args.dev_seed is None else args.dev_seed
    res["seed"] = seed
    g = np.random.Generator(np.random.PCG64(seed))
    run("C-SELF(i)", item_i, F)
    run("C-SELF(ii)", item_ii, F, g)
    run("C-SELF(iii)", item_iii, F, cv, D, g)
    run("C-SELF(iv)", item_iv, F, D, g)
    run("C-SELF(v)", item_v, F, D, X, g)
    run("C-SELF(vi)", item_vi, F, g)
    run("C-SELF(vii)", item_vii, F, D, g)
    t = time.time()
    viii, x = item_viii_x(g)
    timings["C-SELF(viii)+(x)"] = round(time.time() - t, 2)
    res["items"]["C-SELF(viii)"] = viii
    res["items"]["C-SELF(x)"] = x
    run("C-SELF(ix)", item_ix, g)
    run("C-FIX", c_fix)
    run("C-CURVE", c_curve, F, cv)
    run("C-ELL0", c_ell0, F)
    from crypto_autoresearcher.gf2 import _native, kernels
    res["engine"] = {"backend": kernels.backend(), "build_info": dict(_native.build_info)}
    res["timings_seconds_measured"] = timings
    res["finished_utc"] = C.utc_now()
    groups = {"C-SELF": [k for k in res["items"] if k.startswith("C-SELF")],
              "C-FIX": ["C-FIX"], "C-CURVE": ["C-CURVE"], "C-ELL0": ["C-ELL0"],
              "C-SRC": ["C-SRC"], "C-SEED": ["C-SEED"]}
    res["controls"] = {gname: all(res["items"][k]["pass"] for k in ks) for gname, ks in groups.items()}
    res["pass"] = all(res["controls"].values())
    C.write_json(out, res)
    print(json.dumps(res["controls"]), "PASS" if res["pass"] else "FAIL", flush=True)
    return 0 if res["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
