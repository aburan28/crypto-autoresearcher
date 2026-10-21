#!/usr/bin/env python3
"""Independent checker for EXP-ECDLP-84af7b run artifacts. Reads only; exit 0 iff no problem.

Shares no code with the Rust runner. Carries its own exact arithmetic in Q[t]/(g) (Fractions),
finite-field elliptic-curve arithmetic, Legendre point count, primality test and polynomial root
test, and REPLAYS from the recorded inputs: every recorded sample point is re-verified on the curve
exactly, its residues at the recorded roots of g modulo p are recomputed, the Galois trace relation
[T] sum_i r_i(P) = O is re-evaluated, each non-torsion witness (q, root) is re-checked by reduction,
the torsion bound T is checked to divide #E(F_q) at a degree-one prime on a seeded sample of
cells, every root of g mod p is re-verified (CTRL-SPLIT), the cyclic-field discriminants
(CTRL-DISC) and the control conductors (p a d-th power residue mod m) are recomputed, every curve
model is rederived from its a-invariants, and every rung statistic, gamma fit and summary entry is
rebuilt from the recorded counts. A fabricated raw result fails here.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction
from pathlib import Path

EXP = "EXP-ECDLP-84af7b"
TORSION_SAMPLE_CELLS = 24


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def frac(s: str) -> Fraction:
    return Fraction(s)


def poly_mul_mod(a, b, g):
    """a * b in Q[t]/(g); a, b lists of Fractions (length d), g monic integer list (length d + 1)."""
    d = len(g) - 1
    if d == 1:
        return [a[0] * b[0]]
    res = [Fraction(0)] * (2 * d - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[i + j] += ai * bj
    for i in range(2 * d - 2, d - 1, -1):
        c = res[i]
        if c:
            for j in range(d + 1):
                res[i - d + j] -= c * g[j]
    return res[:d]


def padd(a, b):
    return [x + y for x, y in zip(a, b)]


def scal(a, r):
    return [x * r for x in a]


def const(r, d):
    return [Fraction(r)] + [Fraction(0)] * (d - 1)


def rhs(x, a2, a4, a6, g):
    d = len(g) - 1
    x2 = poly_mul_mod(x, x, g)
    return padd(padd(padd(poly_mul_mod(x2, x, g), scal(x2, a2)), scal(x, a4)), const(a6, d))


def embed(a, p, root):
    """Image of a in F_p under t -> root; None if a denominator vanishes mod p."""
    v, pw = 0, 1
    for c in a:
        if c:
            if c.denominator % p == 0:
                return None
            v = (v + c.numerator * pow(c.denominator, -1, p) * pw) % p
        pw = pw * root % p
    return v


def frac_mod(c: Fraction, p: int):
    return c.numerator * pow(c.denominator, -1, p) % p


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, a, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, a, p)
        P = ec_add(P, P, a, p)
        k >>= 1
    return R


def count_points(p, a, b):
    n = p + 1
    for x in range(p):
        v = (x * x * x + a * x + b) % p
        if v == 0:
            continue
        n += 1 if pow(v, (p - 1) // 2, p) == 1 else -1
    return n


def poly_eval_mod(g, r, q):
    v = 0
    for c in reversed(g):
        v = (v * r + c) % q
    return v


def gamma_fit(rungs):
    pts = [(math.log(r["work"]), math.log(r["distinct_residues"])) for r in rungs if r["distinct_residues"] > 0][-3:]
    if len(pts) < 2:
        return None
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in pts) / sxx


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main(run_dir: str) -> int:
    problems: list[str] = []
    raw = json.loads(Path(run_dir, "raw-result.json").read_text())
    if raw.get("experiment_id") != EXP:
        problems.append("experiment_id mismatch")
    rng = random.Random("check-84af7b")
    counts = {"cells": 0, "sample_points": 0, "residues": 0, "witnesses": 0, "torsion_bound_cells": 0, "fields": 0}
    # curve models from a-invariants (b-model: y' = y + (a1 x + a3)/2)
    models = {}
    for cv in raw.get("curves", []):
        a1, a2, a3, a4, a6 = cv["ainvs"]
        want = (Fraction(a1 * a1 + 4 * a2, 4), Fraction(2 * a4 + a1 * a3, 2), Fraction(a3 * a3 + 4 * a6, 4))
        got = tuple(frac(cv["model"][k]) for k in ("a2", "a4", "a6"))
        if got != want:
            problems.append(f"curve {cv['label']}: b-model does not follow from its a-invariants")
        models[cv["label"]] = got
        rk = cv.get("ctrl_rank0")
        if cv.get("excluded_not_rank0") != (bool(rk) and rk.get("rank_upper", 0) != 0):
            problems.append(f"curve {cv['label']}: exclusion flag inconsistent with ctrl_rank0")
    cells = [c for c in raw.get("cells", []) if "invalid" not in c]
    torsion_cells = set(id(c) for c in (cells if len(cells) <= TORSION_SAMPLE_CELLS else rng.sample(cells, TORSION_SAMPLE_CELLS)))
    seen_fields = set()
    for cell in cells:
        counts["cells"] += 1
        c, p, fld, label, T = cell["c"], cell["p"], cell["field"], cell["curve"], cell["torsion_bound_T"]
        tag = f"seed={cell['seed']} c={c} {fld['label']} {label}"
        if p != 2 ** c - 1 or not is_prime(p):
            problems.append(f"{tag}: p is not the Mersenne prime 2^c - 1")
            continue
        if label not in models:
            problems.append(f"{tag}: curve not in the curve table")
            continue
        g = [int(x) for x in fld["g"]]
        d = len(g) - 1
        if g[-1] != 1 or fld["d"] != d:
            problems.append(f"{tag}: g not monic or degree mismatch")
            continue
        a2, a4, a6 = models[label]
        A = frac_mod(a4 - a2 * a2 / 3, p)
        B = frac_mod(a6 - a2 * a4 / 3 + 2 * a2 ** 3 / 27, p)
        shift = frac_mod(a2 / 3, p)
        # CTRL-SPLIT and field metadata, once per (p, field)
        roots = cell["roots_mod_p"]
        fkey = (p, tuple(g))
        if fkey not in seen_fields:
            seen_fields.add(fkey)
            counts["fields"] += 1
            if len(roots) != d or len(set(roots)) != d or any(poly_eval_mod(g, r, p) != 0 for r in roots):
                problems.append(f"{tag}: CTRL-SPLIT: roots_mod_p are not d distinct roots of g mod p")
            m = fld.get("conductor")
            if fld["kind"] == "cyclotomic" and d > 1 and m != c:
                problems.append(f"{tag}: cyclotomic field must have conductor c")
            if fld["kind"] == "abelian_control":
                if not m or m == c or not is_prime(m) or (m - 1) % d != 0 or pow(p, (m - 1) // d, m) != 1:
                    problems.append(f"{tag}: abelian control conductor {m} fails the splitting condition")
            if m and d > 1:
                if int(fld["field_disc"]) != m ** (d - 1):
                    problems.append(f"{tag}: CTRL-DISC field_disc != m^(d-1)")
                if fld.get("ctrl_disc_pari_agrees") is False:
                    problems.append(f"{tag}: CTRL-DISC PARI disagreement recorded")
            rdf = fld.get("root_discriminant_field")
            if d > 1 and not close(rdf, math.exp(math.log(int(fld["field_disc"])) / d), 1e-9):
                problems.append(f"{tag}: root_discriminant_field does not match field_disc")
        # samples
        for s in cell.get("sample_points", []):
            counts["sample_points"] += 1
            x = [frac(v) for v in s["x"]]
            y = [frac(v) for v in s["y"]]
            if len(x) != d or len(y) != d:
                problems.append(f"{tag}: sample point has wrong length")
                continue
            if poly_mul_mod(y, y, g) != rhs(x, a2, a4, a6, g):
                problems.append(f"{tag}: sample point is not on the curve")
                continue
            if s["rational"] != all(v == 0 for v in x[1:] + y[1:]):
                problems.append(f"{tag}: rational flag wrong")
            res = []
            for r in roots:
                ex, ey = embed(x, p, r), embed(y, p, r)
                res.append(None if ex is None or ey is None else ((ex + shift) % p, ey))
            if s["residues"] is None:
                if all(v is not None for v in res):
                    problems.append(f"{tag}: residues recorded as missing but all reductions exist")
                continue
            counts["residues"] += len(res)
            if any(v is None for v in res) or [list(v) for v in res] != s["residues"]:
                problems.append(f"{tag}: residues do not recompute")
                continue
            for R in res:
                if (R[1] * R[1] - (R[0] ** 3 + A * R[0] + B)) % p != 0:
                    problems.append(f"{tag}: residue not on the short-model curve mod p")
            Ssum = None
            for R in res:
                Ssum = ec_add(Ssum, R, A, p)
            if s["trace_ok"] != (ec_mul(T, Ssum, A, p) is None):
                problems.append(f"{tag}: trace relation flag wrong")
            w = s.get("nontorsion_witness")
            if w is not None:
                counts["witnesses"] += 1
                q, root = w["q"], w["root"]
                if not is_prime(q) or poly_eval_mod(g, root, q) != 0:
                    problems.append(f"{tag}: witness (q, root) is not a degree-one prime of K")
                    continue
                ex, ey = embed(x, q, root), embed(y, q, root)
                if ex is None or ey is None:
                    problems.append(f"{tag}: witness point not integral at q")
                    continue
                Aq = frac_mod(a4 - a2 * a2 / 3, q)
                Rq = ((ex + frac_mod(a2 / 3, q)) % q, ey)
                if ec_mul(T, Rq, Aq, q) is None:
                    problems.append(f"{tag}: non-torsion witness fails: [T]R = O at q={q}")
        # torsion bound: T divides #E(F_q) at the first degree-one prime
        if id(cell) in torsion_cells and cell.get("torsion_bound_primes"):
            q = cell["torsion_bound_primes"][0]
            counts["torsion_bound_cells"] += 1
            Aq = frac_mod(a4 - a2 * a2 / 3, q)
            Bq = frac_mod(a6 - a2 * a4 / 3 + 2 * a2 ** 3 / 27, q)
            if count_points(q, Aq, Bq) % T != 0:
                problems.append(f"{tag}: torsion bound T={T} does not divide #E(F_{q})")
        # rungs and derived statistics
        rungs = cell["rungs"]
        prev_w, prev_d = -1, -1
        for r in rungs:
            if r["work"] < prev_w or r["distinct_residues"] < prev_d:
                problems.append(f"{tag}: rungs not monotone")
            prev_w, prev_d = r["work"], r["distinct_residues"]
            want = (r["new_nontorsion_points"] / r["distinct_residues"]) if r["distinct_residues"] else None
            if not close(r["relation_yield_ratio"], want):
                problems.append(f"{tag}: relation_yield_ratio does not recompute")
        if not close(cell["gamma"], gamma_fit(rungs)):
            problems.append(f"{tag}: gamma does not recompute from the rungs")
        max_r = max((r["relation_yield_ratio"] or 0) for r in rungs)
        if not close(cell["max_relation_yield_ratio"], max_r):
            problems.append(f"{tag}: max_relation_yield_ratio does not recompute")
        last = rungs[-1]
        if cell["total_new_nontorsion_points"] != last["new_nontorsion_points"] or cell["trace_relation_failures"] != last["trace_relation_fail"]:
            problems.append(f"{tag}: cell totals do not match the last rung")
        if cell["trace_relation_failures"] != 0:
            problems.append(f"{tag}: CTRL-TRACE failure recorded")
    # summary
    summ = {}
    for cell in cells:
        key = f"c={cell['c']} d={cell['field']['d']}"
        summ.setdefault(key, {"cyclotomic": [], "abelian_control": [], "random_split": []})[cell["field"]["kind"]].append(cell)
    def mean(xs):
        xs = [x for x in xs if x is not None]
        return sum(xs) / len(xs) if xs else None
    for key, arms in summ.items():
        got = raw.get("summary", {}).get(key)
        if got is None:
            problems.append(f"summary: missing {key}")
            continue
        for arm in ("abelian_control", "random_split"):
            gd = nd = None
            if arms[arm] and arms["cyclotomic"]:
                mc, ma = mean([x["gamma"] for x in arms["cyclotomic"]]), mean([x["gamma"] for x in arms[arm]])
                gd = (mc - ma) if (mc is not None and ma is not None) else None
                nd = mean([x["total_new_nontorsion_points"] for x in arms["cyclotomic"]]) - mean([x["total_new_nontorsion_points"] for x in arms[arm]])
            if not close(got.get(f"gamma_cyclotomic_minus_{arm}"), gd) or not close(got.get(f"N_cyclotomic_minus_{arm}"), nd):
                problems.append(f"summary {key}: {arm} differences do not recompute")
            rm = max((x["max_relation_yield_ratio"] for x in arms[arm]), default=None)
            if not close(got.get(f"Rmax_{arm}"), rm):
                problems.append(f"summary {key}: Rmax_{arm} does not recompute")
        if not close(got.get("Rmax_cyclotomic"), max((x["max_relation_yield_ratio"] for x in arms["cyclotomic"]), default=None)):
            problems.append(f"summary {key}: Rmax_cyclotomic does not recompute")
    if raw.get("trace_relation_failures_total") != sum(c["trace_relation_failures"] for c in cells):
        problems.append("trace_relation_failures_total does not recompute")
    report = {"experiment_id": EXP, "checked": counts, "problems": problems, "ok": not problems}
    print(json.dumps(report, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
