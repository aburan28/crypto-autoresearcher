#!/usr/bin/env python3
"""V3: independent certificate re-verification and rank-profile recomputation.

Written by the Validator for TASK-20260904-4c0d7d.  It imports NOTHING from
`harness/` and nothing from the producer's `run_experiment.py` / `analyze.py`:
only the Python standard library (`json`, `collections`, `sys`, `time`).
The elliptic-curve group law, the S_3 formula, the multilinear (a^2 = a)
polynomial arithmetic and the exact Gaussian elimination over F_p below are
this script's own.

S_3 for y^2 = x^3 + A x + B (classical third summation polynomial; the
producer's harness/semaev.py:s3_expr was read to confirm the same convention,
never called):

  S_3(X1,X2,X3) = (X1-X2)^2 X3^2
                - 2[(X1+X2)(X1 X2 + A) + 2B] X3
                + [(X1 X2 - A)^2 - 4B (X1+X2)]

Digit substitution: ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}, reduced in
F_p[a_1..a_6]/(a_i^2 - a_i).  Bit i of a monomial mask is variable
(a_{1,0}, a_{1,1}, a_{1,2}, a_{2,0}, a_{2,1}, a_{2,2})[i].

Per-layer Macaulay convention (the contract's primary convention): at degree
D the rows are { mu * S~ : mu squarefree monomial of degree exactly D - 4 };
full_rank is the rank of that row set over all squarefree columns,
top_rank the rank of the same rows restricted to the columns of degree
exactly D, fall_dim = full_rank - top_rank.
"""
import collections
import json
import os
import sys
import time

ROOT = "/home/user/crypto-autoresearcher"
RUNS = os.path.join(ROOT, "experiments/EXP-PFDR-fd901a/runs")

NVAR = 6
MASKS = list(range(1 << NVAR))
POPC = [bin(m).count("1") for m in MASKS]


# --------------------------------------------------------------------------
# multilinear polynomial arithmetic over F_p:  a_i^2 = a_i
# --------------------------------------------------------------------------
def pmul(f, g, p):
    out = collections.defaultdict(int)
    for m1, c1 in f.items():
        for m2, c2 in g.items():
            out[m1 | m2] = (out[m1 | m2] + c1 * c2) % p
    return {m: c for m, c in out.items() if c}


def padd(f, g, p):
    out = dict(f)
    for m, c in g.items():
        v = (out.get(m, 0) + c) % p
        if v:
            out[m] = v
        elif m in out:
            del out[m]
    return out


def pscal(f, k, p):
    k %= p
    if k == 0:
        return {}
    return {m: (c * k) % p for m, c in f.items() if (c * k) % p}


def psub(f, g, p):
    return padd(f, pscal(g, -1, p), p)


def const(c, p):
    c %= p
    return {0: c} if c else {}


def build_stilde(A, B, xR, p):
    """S~ = S_3(ell_1, ell_2, x_R) in the multilinear quotient."""
    e1 = {1: 1 % p, 2: 2 % p, 4: 4 % p}
    e2 = {8: 1 % p, 16: 2 % p, 32: 4 % p}
    e1 = {m: c for m, c in e1.items() if c}
    e2 = {m: c for m, c in e2.items() if c}
    d = psub(e1, e2, p)
    t1 = pscal(pmul(d, d, p), xR * xR % p, p)
    s = padd(e1, e2, p)
    prod = pmul(e1, e2, p)
    inner = padd(pmul(s, padd(prod, const(A, p), p), p), const(2 * B, p), p)
    t2 = pscal(inner, (-2 * xR) % p, p)
    q = psub(prod, const(A, p), p)
    t3 = psub(pmul(q, q, p), pscal(s, 4 * B % p, p), p)
    return padd(padd(t1, t2, p), t3, p)


def poly_eval(f, digits, p):
    """digits: list of 6 values (0/1 or any residue) for a_{1,0}..a_{2,2}."""
    acc = 0
    for m, c in f.items():
        t = c
        for i in range(NVAR):
            if m >> i & 1:
                t = t * digits[i] % p
        acc = (acc + t) % p
    return acc % p


# --------------------------------------------------------------------------
# exact rank over F_p (own Gaussian elimination, dict rows, no floats)
# --------------------------------------------------------------------------
def rank_mod_p(rows, p):
    rows = [dict(r) for r in rows if r]
    pivots = {}          # pivot column -> reduced row
    rank = 0
    for r in rows:
        r = dict(r)
        while r:
            col = max(r)          # deterministic pivot choice
            if col in pivots:
                fac = r[col] * pow(pivots[col][col], p - 2, p) % p
                pr = pivots[col]
                for c2, v2 in pr.items():
                    nv = (r.get(c2, 0) - fac * v2) % p
                    if nv:
                        r[c2] = nv
                    elif c2 in r:
                        del r[c2]
            else:
                pivots[col] = r
                rank += 1
                break
    return rank


def layer_rows(stilde, D, p):
    """rows = { mu * S~ : deg mu = D - 4 } in the multilinear quotient."""
    k = D - 4
    if k < 0:
        return []
    out = []
    for mu in MASKS:
        if POPC[mu] != k:
            continue
        row = collections.defaultdict(int)
        for m, c in stilde.items():
            mm = m | mu
            row[mm] = (row[mm] + c) % p
        out.append({m: c for m, c in row.items() if c})
    return out


def profile_from_stilde(stilde, p, degrees=(3, 4, 5, 6)):
    full, top, fall, rowc, ncols_full, ncols_top = [], [], [], [], [], []
    for D in degrees:
        rows = layer_rows(stilde, D, p)
        rowc.append(len(rows))
        ncols_full.append(sum(1 for m in MASKS if POPC[m] <= D))
        ncols_top.append(sum(1 for m in MASKS if POPC[m] == D))
        fr = rank_mod_p(rows, p)
        toprows = [{m: c for m, c in r.items() if POPC[m] == D} for r in rows]
        tr = rank_mod_p(toprows, p)
        full.append(fr)
        top.append(tr)
        fall.append(fr - tr)
    return {"full_rank": full, "top_rank": top, "fall_dim": fall,
            "row_count": rowc, "ncols_full": ncols_full, "ncols_top": ncols_top}


# --------------------------------------------------------------------------
# own affine group law on y^2 = x^3 + A x + B over F_p
# --------------------------------------------------------------------------
def on_curve(x, y, A, B, p):
    return (y * y - (x * x % p * x + A * x + B)) % p == 0


def point_add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 % p == x2 % p:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + A) % p * pow(2 * y1 % p, p - 2, p) % p
    else:
        lam = (y2 - y1) % p * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def s3_eval_scalar(A, B, v1, v2, v3, p):
    return ((v1 - v2) ** 2 * v3 * v3
            - 2 * ((v1 + v2) * (v1 * v2 + A) + 2 * B) * v3
            + ((v1 * v2 - A) ** 2 - 4 * B * (v1 + v2))) % p


# --------------------------------------------------------------------------
def load(run):
    with open(os.path.join(RUNS, run, "raw-result.json")) as fh:
        return json.load(fh)


SWEEPS = {"p4099": "RUN-PFDR-fd901a-sweep-p4099",
          "p64": "RUN-PFDR-fd901a-sweep-p64",
          "p256": "RUN-PFDR-fd901a-sweep-p256"}
OTHERS = {"fixture-p4099": "RUN-PFDR-fd901a-fixture-p4099",
          "posctrl-p4099": "RUN-PFDR-fd901a-posctrl-p4099",
          "posctrl-p16411": "RUN-PFDR-fd901a-posctrl-p16411"}


def main():
    t0 = time.time()
    out = {"certificates": {}, "ranks": {}, "planted_point": {}}

    # ---- (a) certificate re-verification, every run, every certificate ---
    cert_summary = {}
    cert_failures = []
    for label, run in list(SWEEPS.items()) + list(OTHERS.items()):
        d = load(run)
        draws = d["raw"].get("draws", [])
        if not draws and "draw" in d["raw"]:
            draws = [d["raw"]["draw"]]
        n_decomp = n_s3 = 0
        ok_decomp = ok_s3 = 0
        singular_ok = 0
        for x in draws:
            cert = x.get("certificate")
            if not cert:
                continue
            st = cert["statement"]
            if cert["kind"] == "decomposition":
                n_decomp += 1
                A = st["curve"]["a"]; B = st["curve"]["b"]; p = st["curve"]["p"]
                (u1, v1), (u2, v2) = st["summands"]
                tx, ty = st["target"]
                good = (on_curve(u1, v1, A, B, p) and on_curve(u2, v2, A, B, p)
                        and on_curve(tx, ty, A, B, p))
                R = point_add((u1, v1), (u2, v2), A, p)
                good = good and R is not None and R[0] % p == tx % p \
                    and R[1] % p == ty % p
                good = good and (tx % p == x["x_R"] % p)
                good = good and ({u1 % p, u2 % p} == {x["x1"] % p, x["x2"] % p})
                if good:
                    ok_decomp += 1
                else:
                    cert_failures.append([label, x["arm"], x["curve_seed"],
                                          x["target_seed"], "decomposition"])
            elif cert["kind"] == "s3_root":
                n_s3 += 1
                A = st["cubic"]["a"]; B = st["cubic"]["b"]; p = st["cubic"]["p"]
                val = s3_eval_scalar(A, B, st["x1"], st["x2"], st["x_R"], p)
                sing = (4 * A ** 3 + 27 * B * B) % p == 0
                if sing:
                    singular_ok += 1
                if val == 0 and st["x_R"] % p == x["x_R"] % p:
                    ok_s3 += 1
                else:
                    cert_failures.append([label, x["arm"], x["curve_seed"],
                                          x["target_seed"], "s3_root"])
        cert_summary[label] = {
            "decomposition_certificates": n_decomp,
            "decomposition_reverified": ok_decomp,
            "s3_root_certificates": n_s3,
            "s3_root_reverified": ok_s3,
            "noncurve_cubics_confirmed_singular": singular_ok,
        }
    out["certificates"] = {"per_run": cert_summary, "failures": cert_failures}

    # ---- (b) independent rank profiles -----------------------------------
    rank_results = {}
    disagreements = []
    checked = []
    for label, run in SWEEPS.items():
        d = load(run)
        p = d["metrics"]["prime"]
        for arm in ["semaev", "semaev_named_p256", "noncurve_cubic"]:
            draws = [x for x in d["raw"]["draws"] if x["arm"] == arm]
            agree = 0
            for x in draws:
                cert = x["certificate"]["statement"]
                if x["certificate"]["kind"] == "decomposition":
                    A, B = cert["curve"]["a"], cert["curve"]["b"]
                else:
                    A, B = cert["cubic"]["a"], cert["cubic"]["b"]
                xR = x["x_R"]
                st = build_stilde(A, B, xR, p)
                prof = profile_from_stilde(st, p)
                mine = (prof["full_rank"], prof["top_rank"], prof["fall_dim"])
                theirs = (x["profile_full_rank"], x["profile_top_rank"],
                          x["profile_fall_dim"])
                rowcols = ([x["per_layer"][str(D)]["row_count"] for D in (3, 4, 5, 6)],
                           [x["per_layer"][str(D)]["ncols_full"] for D in (3, 4, 5, 6)],
                           [x["per_layer"][str(D)]["ncols_top"] for D in (3, 4, 5, 6)])
                shape_ok = (prof["row_count"] == rowcols[0]
                            and prof["ncols_full"] == rowcols[1]
                            and prof["ncols_top"] == rowcols[2])
                nnz_ok = len(st) == x["generator_term_counts"][0]
                # planted point must be a root of S~
                planted_ok = poly_eval(st, x["planted_digits"], p) == 0
                dig = x["planted_digits"]
                ell1 = (dig[0] + 2 * dig[1] + 4 * dig[2])
                ell2 = (dig[3] + 2 * dig[4] + 4 * dig[5])
                digits_ok = {ell1, ell2} == {x["x1"], x["x2"]}
                if (mine == (list(theirs[0]), list(theirs[1]), list(theirs[2]))
                        and shape_ok and nnz_ok and planted_ok and digits_ok):
                    agree += 1
                else:
                    disagreements.append({
                        "prime": label, "arm": arm,
                        "curve_seed": x["curve_seed"],
                        "target_seed": x["target_seed"],
                        "mine": prof, "recorded_full": x["profile_full_rank"],
                        "recorded_top": x["profile_top_rank"],
                        "recorded_fall": x["profile_fall_dim"],
                        "shape_ok": shape_ok, "nnz_mine": len(st),
                        "nnz_recorded": x["generator_term_counts"][0],
                        "planted_root_ok": planted_ok,
                        "digits_ok": digits_ok})
                checked.append([label, arm, x["curve_seed"], x["target_seed"]])
            rank_results[f"{label}:{arm}"] = {
                "draws": len(draws), "agreeing": agree,
                "profile_recomputed": ("full_rank/top_rank/fall_dim at D=3..6, "
                                       "row/col shapes, S~ term count, planted "
                                       "root, digit decoding")}
    out["ranks"] = {"per_prime_arm": rank_results,
                    "disagreements": disagreements,
                    "draws_checked": checked}

    # ---- fixture draw ----------------------------------------------------
    d = load("RUN-PFDR-fd901a-fixture-p4099")
    fx = json.dumps(d["raw"])[:0]  # placeholder, structure inspected below
    out["fixture_raw_keys"] = sorted(d["raw"].keys())

    out["elapsed_seconds"] = round(time.time() - t0, 2)
    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
