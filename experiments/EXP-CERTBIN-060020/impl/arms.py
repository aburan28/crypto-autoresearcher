"""Instance sets (specification instance_sets): one numpy PCG64 generator per
arm, consumed exactly in the stated order; every attempt is logged.

Interpretations fixed here (recorded in implementation.md; the verifier
implements the same text independently):
* E_sha256 = sha256 of the compact JSON list of the 19 E_hex strings
  (bit j of row k's integer = column j; lowercase hex, no prefix).
* S3-PRIMARY: attempt order = draw order; the loop stops as soon as S3-U400
  holds 400 and S3-SAT100 holds 100 (checked before each attempt).
  Duplicate x_R = equal to the x_R of an earlier CLASSIFIED attempt.
* N-CONV19: the arm generator is consumed slot by slot (slot 0's attempts
  first); a duplicate is a draw equal to an already-KEPT system of the arm.
* N-ELL19 / N-F219: a duplicate is a draw equal to any earlier non-duplicate
  draw of the same stream.
* N-AFF19: the "non-degenerate S3-PRIMARY attempts" are the classified
  attempts (R != O, x_R >= 1024, not a duplicate x_R), in draw order;
  duplicates are within a family.
* F-RANDX19: per attempt, rejection order is degenerate (x < 1024), then
  duplicate of an earlier draw of this stream (any non-degenerate earlier
  draw), then equal to an S3-PRIMARY x_R (any attempt with R != O).
"""
from __future__ import annotations

import numpy as np

import common as C
from oracles import oracle_A


def rng(seed):
    return np.random.Generator(np.random.PCG64(seed))


class Ctx:
    """Field, curve, descent, exhaustive evaluator, U, S_L, Upos, ell_lin."""

    def __init__(self, F, curve, D, X):
        self.F, self.curve, self.D, self.X = F, curve, D, X
        E0, Ej = D.affine_parts()
        self.E0, self.Ej = E0, Ej
        U = D.union_support()
        self.U = U
        self.Upos = np.flatnonzero(U.ravel())
        low = np.zeros_like(U)
        low[:, :1 + D.nv] = True
        self.SL_pos = np.flatnonzero((U & low).ravel())  # row-major
        tau = [F.trace(1 << j) for j in range(F.n)]
        self.tau = tau
        ell = np.zeros(D.ncol, dtype=np.uint8)
        for j in range(D.l):
            if tau[j]:
                ell[1 + j] ^= 1
                ell[1 + D.l + j] ^= 1
        self.ell_lin = ell

    def E_s3(self, xR):
        E = self.D.E_direct(xR)
        aff_ok = bool((E == self.D.E_affine(xR)).all())
        return E, aff_ok


def _inst(arm, role, index, E, s, sols=None, **kw):
    rec = {"key": f"{arm}:{index}", "arm": arm, "role": role, "index": index,
           "E_hex": C.E_to_hex(E), "E_sha256": C.E_sha256(E), "s": int(s)}
    if role == "sat":
        rec["solutions"] = sols
    rec.update(kw)
    return rec


def s3_primary(ctx, seed, n_unsat=400, n_sat=100, cap=5000):
    F, cv, X = ctx.F, ctx.curve, ctx.X
    g = rng(seed)
    P, Qp = C.P_PT, C.Q_PT
    draws, U400, SAT, classified = [], [], [], []
    seen = set()
    all_x = set()
    checks = {"oracle_disagreements": [], "tr19_violations": [], "aff_violations": [],
              "qR_not_O": []}
    att = 0
    while att < cap and (len(U400) < n_unsat or len(SAT) < n_sat):
        a = int(g.integers(0, C.Q))
        b = int(g.integers(0, C.Q))
        R = cv.add(cv.mul(a, P), cv.mul(b, Qp))
        rec = {"attempt": att, "a": a, "b": b}
        if R is None:
            rec["outcome"] = "R_is_O"
        else:
            xR = R[0]
            rec["x_R"] = xR
            all_x.add(xR)
            if xR < (1 << C.L):
                rec["outcome"] = "degenerate"
            elif xR in seen:
                rec["outcome"] = "duplicate"
            else:
                seen.add(xR)
                E, aff_ok = ctx.E_s3(xR)
                if not aff_ok:
                    checks["aff_violations"].append(att)
                sA, solsA = oracle_A(F, C.L, xR, C.B)
                sB, solsB = X.count(E, want_solutions=True)
                if sA != sB or solsA != solsB:
                    checks["oracle_disagreements"].append({"attempt": att, "sA": sA, "sB": sB})
                if cv.mul(C.Q, R) is not None:
                    checks["qR_not_O"].append(att)
                if (F.trace(xR) == F.trace(C.A)) is not True:
                    checks["tr19_violations"].append(att)
                s = sB
                rec["s"] = s
                rec["sA"] = sA
                classified.append({"attempt": att, "x_R": xR, "s": s})
                if s == 0:
                    if len(U400) < n_unsat:
                        U400.append(_inst("S3-U400", "unsat", len(U400), E, s, x_R=xR, attempt=att))
                        rec["outcome"] = "kept:S3-U400"
                    else:
                        rec["outcome"] = "unsat_not_kept"
                else:
                    if len(SAT) < n_sat:
                        SAT.append(_inst("S3-SAT100", "sat", len(SAT), E, s, solsB, x_R=xR, attempt=att))
                        rec["outcome"] = "kept:S3-SAT100"
                    else:
                        rec["outcome"] = "sat_not_kept"
        draws.append(rec)
        att += 1
    short = {"S3-U400": max(0, n_unsat - len(U400)), "S3-SAT100": max(0, n_sat - len(SAT))}
    return {"draws": draws, "U400": U400, "SAT100": SAT, "classified": classified,
            "all_x": all_x, "checks": checks, "shortfall": short, "attempts": att}


def n_conv19(ctx, seed, slots, n_sat_slots=50, per_slot=256):
    """slots: list of S3-U400 instance records (the 200 lowest draw order)."""
    g = rng(seed)
    X = ctx.X
    draws, kept = [], []
    kept_sha = set()
    exhausted = []
    nq = 1 + ctx.D.nv
    for i, srec in enumerate(slots):
        Es = C.E_from_hex(srec["E_hex"])
        need_u, need_s = True, i < n_sat_slots
        for att in range(per_slot):
            if not need_u and not need_s:
                break
            bits = g.integers(0, 2, size=ctx.SL_pos.size)
            Ed = np.zeros_like(Es)
            Ed[:, nq:] = Es[:, nq:]
            flat = Ed.reshape(-1)
            flat[ctx.SL_pos] = bits.astype(np.uint8)
            sha = C.E_sha256(Ed)
            rec = {"slot": i, "attempt": att, "E_sha256": sha}
            if (Ed == Es).all():
                rec["outcome"] = "identity"
            elif sha in kept_sha:
                rec["outcome"] = "duplicate"
            else:
                s, sols = X.count(Ed, want_solutions=True)
                rec["s"] = s
                if s == 0 and need_u:
                    kept.append(_inst("N-CONV19", "unsat", len(kept), Ed, s, slot=i, x_R=srec["x_R"],
                                      attempt=att, s3_key=srec["key"]))
                    kept_sha.add(sha)
                    need_u = False
                    rec["outcome"] = "kept:unsat"
                elif s > 0 and need_s:
                    kept.append(_inst("N-CONV19", "sat", len(kept), Ed, s, sols, slot=i, x_R=srec["x_R"],
                                      attempt=att, s3_key=srec["key"]))
                    kept_sha.add(sha)
                    need_s = False
                    rec["outcome"] = "kept:sat"
                else:
                    rec["outcome"] = "not_needed"
            draws.append(rec)
        if need_u:
            exhausted.append({"slot": i, "role": "unsat"})
        if need_s:
            exhausted.append({"slot": i, "role": "sat"})
    return {"draws": draws, "kept": kept, "exhausted": exhausted}


def stream_arm(ctx, arm, seed, with_ell, n_unsat=200, n_sat=50, cap=20000):
    """N-ELL19 (with_ell) and N-F219."""
    g = rng(seed)
    X = ctx.X
    D = ctx.D
    draws, kept_u, kept_s = [], [], []
    seen = set()
    outside_U = []
    k = 0
    while k < cap and (len(kept_u) < n_unsat or len(kept_s) < n_sat):
        flat = np.zeros(D.neq * D.ncol, dtype=np.uint8)
        flat[ctx.Upos] = g.integers(0, 2, size=ctx.Upos.size).astype(np.uint8)
        M = flat.reshape(D.neq, D.ncol)
        rec = {"draw": k}
        if with_ell:
            c = int(g.integers(0, 2))
            M[D.neq - 1] = ctx.ell_lin
            M[D.neq - 1, 0] ^= c
            rec["c"] = c
        # C-SUPPORT: rows (0..17 for N-ELL19, all for N-F219) inside U
        rows = D.neq - 1 if with_ell else D.neq
        if (M[:rows] & ~ctx.U[:rows]).any():
            outside_U.append(k)
        sha = C.E_sha256(M)
        rec["E_sha256"] = sha
        if sha in seen:
            rec["outcome"] = "duplicate"
        else:
            seen.add(sha)
            s, sols = X.count(M, want_solutions=True)
            rec["s"] = s
            if s == 0 and len(kept_u) < n_unsat:
                kept_u.append((k, M.copy(), s, None))
                rec["outcome"] = "kept:unsat"
            elif s > 0 and len(kept_s) < n_sat:
                kept_s.append((k, M.copy(), s, sols))
                rec["outcome"] = "kept:sat"
            else:
                rec["outcome"] = "not_needed"
        draws.append(rec)
        k += 1
    kept = []
    merged = sorted([(d, "unsat", M, s, so) for d, M, s, so in kept_u] +
                    [(d, "sat", M, s, so) for d, M, s, so in kept_s], key=lambda t: t[0])
    for d, role, M, s, so in merged:
        kept.append(_inst(arm, role, len(kept), M, s, so, attempt=d, x_R=None))
    return {"draws": draws, "kept": kept, "outside_U": outside_U,
            "shortfall": {"unsat": max(0, n_unsat - len(kept_u)), "sat": max(0, n_sat - len(kept_s))},
            "attempts": k}


def n_aff19(ctx, seed, classified, n_fam=5, n_unsat=40, n_sat=10):
    g = rng(seed)
    X = ctx.X
    D = ctx.D
    E0, Ej = ctx.E0, ctx.Ej
    fams = []
    for d in range(n_fam):
        e0 = np.zeros(D.neq * D.ncol, dtype=np.uint8)
        nz = np.flatnonzero(E0.ravel())
        e0[nz] = g.integers(0, 2, size=nz.size).astype(np.uint8)
        ej = []
        for j in range(D.n):
            e = np.zeros(D.neq * D.ncol, dtype=np.uint8)
            nz = np.flatnonzero(Ej[j].ravel())
            e[nz] = g.integers(0, 2, size=nz.size).astype(np.uint8)
            ej.append(e.reshape(D.neq, D.ncol))
        fams.append((e0.reshape(D.neq, D.ncol), ej))
    draws, kept = [], []
    short = {}
    for d, (e0, ej) in enumerate(fams, start=1):
        seen = set()
        ku, ks = 0, 0
        for c in classified:
            if ku >= n_unsat and ks >= n_sat:
                break
            xR = c["x_R"]
            M = e0.copy()
            for j in range(D.n):
                if (xR >> j) & 1:
                    M ^= ej[j]
            sha = C.E_sha256(M)
            rec = {"family": d, "primary_attempt": c["attempt"], "x_R": xR, "E_sha256": sha}
            if sha in seen:
                rec["outcome"] = "duplicate"
            else:
                seen.add(sha)
                s, sols = X.count(M, want_solutions=True)
                rec["s"] = s
                if s == 0 and ku < n_unsat:
                    kept.append(_inst("N-AFF19", "unsat", len(kept), M, s, family=d, x_R=xR,
                                      attempt=c["attempt"]))
                    ku += 1
                    rec["outcome"] = "kept:unsat"
                elif s > 0 and ks < n_sat:
                    kept.append(_inst("N-AFF19", "sat", len(kept), M, s, sols, family=d, x_R=xR,
                                      attempt=c["attempt"]))
                    ks += 1
                    rec["outcome"] = "kept:sat"
                else:
                    rec["outcome"] = "not_needed"
            draws.append(rec)
        short[d] = {"unsat": n_unsat - ku, "sat": n_sat - ks}
    return {"draws": draws, "kept": kept, "shortfall": short}


STRATA = ("X2E", "XE-NOT-2E", "TWIST")


def f_randx19(ctx, seed, primary_x, quota=200, cap=30000):
    F, cv, X = ctx.F, ctx.curve, ctx.X
    g = rng(seed)
    draws = []
    kept = {s: [] for s in STRATA}
    seen = set()
    checks = {"oracle_disagreements": [], "tr19_violations": [], "aff_violations": []}
    att = 0
    while att < cap and any(len(kept[s]) < quota for s in STRATA):
        x = int(g.integers(0, 1 << C.N))
        rec = {"attempt": att, "x": x}
        att += 1
        if x < (1 << C.L):
            rec["outcome"] = "degenerate"
            draws.append(rec)
            continue
        if x in seen:
            rec["outcome"] = "duplicate"
            draws.append(rec)
            continue
        seen.add(x)
        if x in primary_x:
            rec["outcome"] = "primary_collision"
            draws.append(rec)
            continue
        cval = x ^ C.A ^ F.div(C.B, F.mul(x, x))
        if F.trace(cval) == 1:
            st = "TWIST"
        else:
            Pt = cv.lift_x(x)
            st = "X2E" if cv.mul(C.Q, Pt) is None else "XE-NOT-2E"
            if (st == "X2E") != (F.trace(x) == F.trace(C.A)):
                checks["tr19_violations"].append(rec["attempt"])
        rec["stratum"] = st
        if len(kept[st]) >= quota:
            rec["outcome"] = "quota_full"
            draws.append(rec)
            continue
        E, aff_ok = ctx.E_s3(x)
        if not aff_ok:
            checks["aff_violations"].append(rec["attempt"])
        sA, solsA = oracle_A(F, C.L, x, C.B)
        sB, solsB = X.count(E, want_solutions=True)
        if sA != sB or solsA != solsB:
            checks["oracle_disagreements"].append({"attempt": rec["attempt"], "sA": sA, "sB": sB})
        rec["s"] = sB
        rec["sA"] = sA
        if sB == 0:
            kept[st].append((rec["attempt"], x, E))
            rec["outcome"] = "kept:unsat"
        else:
            rec["outcome"] = "sat_recorded"
        draws.append(rec)
    out = []
    merged = sorted([(a, x, E, st) for st in STRATA for a, x, E in kept[st]], key=lambda t: t[0])
    for a, x, E, st in merged:
        out.append(_inst("F-RANDX19", "unsat", len(out), E, 0, x_R=x, stratum=st, attempt=a))
    return {"draws": draws, "kept": out, "checks": checks,
            "shortfall": {s: max(0, quota - len(kept[s])) for s in STRATA}, "attempts": att}
