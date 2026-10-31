#!/usr/bin/env python3
"""Blind re-derivation J1 of the EXP-PFDR-bb0d26 toy reading (TASK-20261029-2c7b52).

Written from experiments/EXP-PFDR-bb0d26/specification.yaml (/experiment/inputs, cell_classes,
calibration_gate, replication_rule, toy_reading_rules, headline), ledger/hypotheses/H-PFDR-727bfc.yaml
and the raw jobs records only. Python standard library only; run with python3 -I from the blind tree root.

Subcommands (run in this order):
  invariants  -> out/outputs/record-invariants.json
  design      -> out/outputs/blind-design.json
  seed        -> out/outputs/bootstrap-seed.json   (written BEFORE any bootstrap draw)
  cells       -> out/outputs/blind-cells.json      (reads bootstrap-seed.json, refuses if absent)
  reading     -> out/outputs/blind-reading.json and out/outputs/ambiguity-table.json
  freeze      -> out/outputs/freeze-manifest.json
"""
import hashlib
import itertools
import json
import math
import os
import random
import statistics
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # the blind tree root $T
OUT = os.path.join(ROOT, "out", "outputs")
MAIN_JOBS = "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl"
REP_JOBS = "experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-cd03e2/toy-rep-jobs.jsonl"

# ---- constants transcribed by hand from specification.yaml (no producer code exists in this tree) ----
BITS = [20, 24, 28]                      # inputs.curves.toy_bits
RANKS = [1, 2, 3]                        # inputs.toy_cells.rule
NS = [256, 512, 1024, 2048, 4096]        # inputs.toy_cells.rule
NULL_REPS = 20                           # inputs.null_builder
TARGET = 2500                            # inputs.sizing / statistics.powered
SAFETY = F(3, 2)                         # inputs.sizing "1.5 x 2500"
CLAMP_LO, CLAMP_HI = 50, 2000            # inputs.sizing
P_REF_FACTOR = F(3, 4)                   # inputs.sizing p_ref = 0.75 x 2^bits
PLANT_FRAC = F(3, 10)                    # inputs.planted_builder 0.30
BOOT_B = 2000                            # inputs.statistics.per_cell
GATE_SD_LO, GATE_SD_HI = F(3, 4), F(5, 4)  # inputs.calibration_gate
GATE_MEAN = F(35, 100)
FLAG_K, FLAG_Z = F(1, 10), 4             # inputs.cell_classes.flagged
NULL_K = F(1, 20)                        # inputs.cell_classes.null
CI_LO, CI_HI = F(9, 10), F(11, 10)
PLANT_K, PLANT_Z = F(115, 100), 4        # inputs.cell_classes.inconclusive_plant_not_recovered
REP_Z, REP_K = 3, F(1, 20)               # inputs.replication_rule
VALID_MIN, NULL_FRAC = F(1, 2), F(4, 5)  # inputs.toy_reading_rules
SEED_OFFSET = {"main": 8100000, "replication": 8200000, "selftest": 8900000}  # inputs.curves.seed_rule
STATUSES = {"ok", "failed_infrastructure", "degenerate"}
SCHEMA_FIELDS = {"cell", "block", "c", "p", "a", "b_coef", "N", "bits", "r", "n", "status", "null_C", "null_D",
                 "gap_C", "gap_D", "gap_meta", "plant_m", "plant_internal", "plant_C", "plant_D", "plant_feasible",
                 "seconds"}
PREC = 60


def cell_id(bits, r, n):
    return "b%d-r%d-n%d" % (bits, r, n)


CELLS = [(b, r, n) for b in BITS for r in RANKS for n in NS]
CELL_IDS = [cell_id(*t) for t in CELLS]


def parse_cell(s):
    try:
        b, r, n = s.split("-")
        assert b[0] == "b" and r[0] == "r" and n[0] == "n"
        return int(b[1:]), int(r[1:]), int(n[1:])
    except Exception:
        return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def frac_str(x):
    x = F(x)
    return "%d/%d" % (x.numerator, x.denominator) if x.denominator != 1 else "%d" % x.numerator


def dec(x, prec=PREC):
    x = F(x)
    with localcontext() as ctx:
        ctx.prec = prec
        return Decimal(x.numerator) / Decimal(x.denominator)


def dsqrt(x, prec=PREC):
    with localcontext() as ctx:
        ctx.prec = prec
        return dec(x, prec).sqrt()


def dstr(d, sig=40):
    with localcontext() as ctx:
        ctx.prec = sig
        return str(+d)


def write_json(name, obj):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("wrote", os.path.relpath(path, ROOT), sha256_file(path))


def load_jobs(rel):
    recs = []
    with open(os.path.join(ROOT, rel)) as fh:
        for ln, line in enumerate(fh, 1):
            if not line.strip():
                recs.append((ln, None))
                continue
            recs.append((ln, json.loads(line)))
    return recs


# ---------------------------------------------------------------- number theory / curve helpers
def is_prime(n):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for q in small:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:  # deterministic for n < 3.3e24
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


def sqrt_mod(a, p):
    a %= p
    if a == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r


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


def order_check(p, a, b, N):
    """N*P == O for a deterministic point P != O (first x >= 1 with f(x) a nonzero square)."""
    x = 1
    while True:
        f = (x * x * x + a * x + b) % p
        if f != 0 and pow(f, (p - 1) // 2, p) == 1:
            y = sqrt_mod(f, p)
            assert y * y % p == f
            return ec_mul(N, (x, y), a, p) is None, x
        x += 1


# ---------------------------------------------------------------- design
def binom(n, k):
    return math.comb(n, k)


def design_row(bits, r, n):
    p_ref = P_REF_FACTOR * 2 ** bits
    mu_ref = F(3 * binom(n, 4)) / p_ref
    raw = SAFETY * TARGET / mu_ref
    ceil_raw = -((-raw.numerator) // raw.denominator)
    n_curves = min(max(ceil_raw, CLAMP_LO), CLAMP_HI)
    # float path, as a sizing implementation would plausibly compute it
    mu_f = 3 * binom(n, 4) / (0.75 * 2 ** bits)
    n_float = min(max(math.ceil(1.5 * 2500 / mu_f), 50), 2000)
    return {"cell": cell_id(bits, r, n), "bits": bits, "r": r, "n": n, "binom_n_4": binom(n, 4),
            "p_ref": frac_str(p_ref), "mu_ref_exact": frac_str(mu_ref), "mu_ref": float(mu_ref),
            "ceil_arg_exact": frac_str(raw), "ceil_arg_is_integer": raw.denominator == 1,
            "ceil_unclamped": ceil_raw, "n_curves": n_curves, "n_curves_float_path": n_float,
            "float_path_agrees": n_float == n_curves, "clamped": ceil_raw != n_curves,
            "expected_null_total_at_p_ref": float(mu_ref * n_curves)}


def design():
    return {c: design_row(*t) for c, t in zip(CELL_IDS, CELLS)}


# ---------------------------------------------------------------- half-box
_HB = {}


def half_box(r, T):
    key = (r, T)
    if key not in _HB:
        vecs = []
        for v in itertools.product(range(-T, T + 1), repeat=r):
            nz = next((x for x in v if x != 0), 0)
            if nz > 0:
                vecs.append(v)
        _HB[key] = (vecs, {v: i + 1 for i, v in enumerate(vecs)})
    return _HB[key]


def least_T(r, n):
    need = -((-102 * n) // 100) + 8  # ceil(1.02 n) + 8, exact
    T = 0
    while ((2 * T + 1) ** r - 1) // 2 < need:
        T += 1
    return T, need


# ---------------------------------------------------------------- invariants
class Checks:
    def __init__(self):
        self.items = {}
        self.order = []

    def define(self, cid, desc):
        self.items[cid] = {"id": cid, "description": desc, "n_checked": 0, "n_violations": 0, "violations": []}
        self.order.append(cid)

    def check(self, cid, ok, key=None, detail=None):
        it = self.items[cid]
        it["n_checked"] += 1
        if not ok:
            it["n_violations"] += 1
            if len(it["violations"]) < 200:
                it["violations"].append({"key": key, "detail": detail})

    def out(self):
        return [self.items[c] for c in self.order]


def set_consistency(C, D, n, p):
    P = n * (n - 1) // 2
    probs = []
    if not (isinstance(C, int) and isinstance(D, int)):
        return ["non-integer count"]
    if C < 0:
        probs.append("C < 0")
    if not (n - 1 <= D <= min(p, P)):
        probs.append("D outside [n-1, min(p, n(n-1)/2)]")
    if D > 0 and D * (2 * C + P) < P * P:
        probs.append("Cauchy-Schwarz: D (2C + P) < P^2")
    if 2 * C > (n // 2 - 1) * P:
        probs.append("C above the m_s <= n/2 bound")
    return probs


def cmd_invariants():
    des = design()
    ck = Checks()
    defs = [
        ("I01", "record parses as one JSON object per line and carries exactly the toy_jobs_jsonl schema fields"),
        ("I02", "block == 'main' in the main census file"),
        ("I03", "cell id is one of the 45 grid cells and bits, r, n equal the values in b<bits>-r<r>-n<n>"),
        ("I04", "c is an integer in [0, n_curves(cell)) of the re-derived design"),
        ("I05", "one record per (cell, block, c): no duplicate key"),
        ("I06", "census completeness: every planned (cell, c < n_curves) key is present"),
        ("I07", "p is prime and p.bit_length() == bits"),
        ("I08", "N prime (prime order), Hasse |p + 1 - N| <= 2 sqrt(p), N != p, a != 0, b != 0, 4a^3 + 27b^2 != 0 mod p, 0 <= a, b < p"),
        ("I09", "N = #E(F_p) confirmed: N * P == O for a deterministic point P != O (per distinct curve)"),
        ("I10", "cells at the same bits share the curve of index c (same p, a, b_coef, N)"),
        ("I11", "status in {ok, failed_infrastructure, degenerate}; failed_infrastructure carries a reason"),
        ("I12", "ok record: null_C and null_D are lists of 20 ints; gap_C, gap_D, plant_m, plant_internal, plant_C, plant_D ints; plant_feasible bool"),
        ("I13", "gap_meta T is the least T with ((2T+1)^r - 1)/2 >= ceil(1.02 n) + 8 (every record)"),
        ("I14", "ok record: enumerated - duplicate_skips - infinity_skips == n; enumerated <= |H(r,T)|; last is the enumerated-th vector of H(r,T); first is at position <= 1 + infinity_skips"),
        ("I15", "degenerate record: enumerated == |H(r,T)| (whole half-box), last == final vector of H(r,T), and the collected labels fall short of n"),
        ("I16", "r = 1 records: duplicate_skips == 0 and infinity_skips == 0 (cP = +-c'P forces c = c' when 2T < N)"),
        ("I17", "count consistency of every ok set (gap, 20 nulls, plant): n-1 <= D <= min(p, n(n-1)/2), D(2C+P) >= P^2 (Cauchy-Schwarz, P = n(n-1)/2), 2C <= (floor(n/2) - 1) P"),
        ("I18", "plant: 4 <= plant_m <= n/2, plant_C >= plant_internal (superset monotonicity)"),
        ("I19", "plant_feasible agrees with the rule: feasible iff plant_internal >= 0.30 x mean(null_C) (exact); infeasible records carry plant_m == n/2"),
        ("I20", "seconds is a non-negative number"),
        ("I21", "degenerate / failed records carry no counts (gap, null, plant fields null)"),
        ("I22", "replication jobs file: records (if any) have block 'replication' and a flagged cell; count reported"),
    ]
    for d in defs:
        ck.define(*d)
    recs = load_jobs(MAIN_JOBS)
    seen = {}
    curves = {}
    status_count = {}
    for ln, rec in recs:
        key = "line %d" % ln
        ok_obj = isinstance(rec, dict)
        ck.check("I01", ok_obj and set(rec) == SCHEMA_FIELDS or (ok_obj and rec.get("status") == "failed_infrastructure" and set(rec) == SCHEMA_FIELDS | {"reason"}),
                 key, None if not ok_obj else sorted(set(rec) ^ SCHEMA_FIELDS))
        if not ok_obj:
            continue
        cell = rec.get("cell")
        key = "%s/%s/c=%s (line %d)" % (cell, rec.get("block"), rec.get("c"), ln)
        ck.check("I02", rec.get("block") == "main", key, rec.get("block"))
        pc = parse_cell(cell) if isinstance(cell, str) else None
        ck.check("I03", pc is not None and cell in des and pc == (rec.get("bits"), rec.get("r"), rec.get("n")), key,
                 [pc, rec.get("bits"), rec.get("r"), rec.get("n")])
        if cell not in des:
            continue
        bits, r, n = pc
        c = rec.get("c")
        ck.check("I04", isinstance(c, int) and 0 <= c < des[cell]["n_curves"], key, c)
        k3 = (cell, rec.get("block"), c)
        ck.check("I05", k3 not in seen, key, "duplicate of line %s" % seen.get(k3))
        seen.setdefault(k3, ln)
        p, a, b, N = rec["p"], rec["a"], rec["b_coef"], rec["N"]
        ck.check("I07", is_prime(p) and p.bit_length() == bits, key, [p, p.bit_length()])
        hasse = (p + 1 - N) ** 2 <= 4 * p
        disc = (4 * a ** 3 + 27 * b * b) % p != 0
        ck.check("I08", is_prime(N) and hasse and N != p and a % p != 0 and b % p != 0 and disc and 0 <= a < p and 0 <= b < p,
                 key, {"N_prime": is_prime(N), "hasse": hasse, "anomalous": N == p, "a": a, "b": b, "disc_nonzero": disc})
        ck_curve = (bits, c)
        if ck_curve in curves:
            ck.check("I10", curves[ck_curve] == (p, a, b, N), key, [curves[ck_curve], (p, a, b, N)])
        else:
            curves[ck_curve] = (p, a, b, N)
        st = rec.get("status")
        status_count[st] = status_count.get(st, 0) + 1
        ck.check("I11", st in STATUSES and (st != "failed_infrastructure" or bool(rec.get("reason"))), key, st)
        gm = rec.get("gap_meta") or {}
        T = gm.get("T")
        Tw, need = least_T(r, n)
        ck.check("I13", T == Tw, key, {"T": T, "T_rule": Tw, "need": need})
        vecs, pos = half_box(r, Tw)
        H = len(vecs)
        enum, dup, inf = gm.get("enumerated"), gm.get("duplicate_skips"), gm.get("infinity_skips")
        first, last = tuple(gm.get("first") or ()), tuple(gm.get("last") or ())
        if r == 1:
            ck.check("I16", dup == 0 and inf == 0, key, [dup, inf])
        ck.check("I20", isinstance(rec.get("seconds"), (int, float)) and rec["seconds"] >= 0, key, rec.get("seconds"))
        if st == "ok":
            nc, nd = rec.get("null_C"), rec.get("null_D")
            ints = all(isinstance(rec.get(f), int) and not isinstance(rec.get(f), bool)
                       for f in ("gap_C", "gap_D", "plant_m", "plant_internal", "plant_C", "plant_D"))
            lists = (isinstance(nc, list) and isinstance(nd, list) and len(nc) == NULL_REPS and len(nd) == NULL_REPS
                     and all(isinstance(x, int) for x in nc + nd))
            ck.check("I12", ints and lists and isinstance(rec.get("plant_feasible"), bool), key, None)
            okb = (isinstance(enum, int) and enum - dup - inf == n and enum <= H and pos.get(last) == enum
                   and first in pos and pos[first] - 1 <= inf)
            ck.check("I14", okb, key, {"enumerated": enum, "dup": dup, "inf": inf, "H": H,
                                       "pos_last": pos.get(last), "pos_first": pos.get(first)})
            probs = []
            for nm, C, D in [("gap", rec["gap_C"], rec["gap_D"]), ("plant", rec["plant_C"], rec["plant_D"])] + \
                    [("null%d" % i, nc[i], nd[i]) for i in range(NULL_REPS)]:
                pr = set_consistency(C, D, n, p)
                if pr:
                    probs.append({nm: pr})
            ck.check("I17", not probs, key, probs)
            pm, pi, pC = rec["plant_m"], rec["plant_internal"], rec["plant_C"]
            ck.check("I18", 4 <= pm <= n // 2 and pC >= pi, key, [pm, pi, pC])
            meanN = F(sum(nc), NULL_REPS)
            feas_rule = pi >= PLANT_FRAC * meanN
            okf = (rec["plant_feasible"] == feas_rule) and (rec["plant_feasible"] or pm == n // 2)
            ck.check("I19", okf, key, {"recorded": rec["plant_feasible"], "internal": pi,
                                       "threshold": float(PLANT_FRAC * meanN), "m": pm})
        else:
            nulls = all(rec.get(f) is None for f in ("null_C", "null_D", "gap_C", "gap_D", "plant_m", "plant_internal",
                                                     "plant_C", "plant_D", "plant_feasible"))
            ck.check("I21", nulls, key, None)
            if st == "degenerate":
                okd = enum == H and last == vecs[-1] and isinstance(dup, int) and enum - dup - inf < n
                ck.check("I15", okd, key, {"enumerated": enum, "H": H, "last": list(last),
                                           "collected": (enum - dup - inf) if isinstance(dup, int) else None})
    # completeness
    for cell, row in des.items():
        for c in range(row["n_curves"]):
            ck.check("I06", (cell, "main", c) in seen, "%s/main/c=%d" % (cell, c), "missing")
    # order check per distinct curve
    for (bits, c), (p, a, b, N) in sorted(curves.items()):
        ok, x = order_check(p, a, b, N)
        ck.check("I09", ok, "bits=%d c=%d seed=%d" % (bits, c, SEED_OFFSET["main"] + c), {"p": p, "N": N, "x": x})
    rep = load_jobs(REP_JOBS)
    for ln, rec in rep:
        ck.check("I22", isinstance(rec, dict) and rec.get("block") == "replication", "rep line %d" % ln, None)
    out = {
        "task": "TASK-20261029-2c7b52", "joint": "J1",
        "sources": {MAIN_JOBS: sha256_file(os.path.join(ROOT, MAIN_JOBS)), REP_JOBS: sha256_file(os.path.join(ROOT, REP_JOBS))},
        "main_records": len(recs), "main_status_count": status_count,
        "main_distinct_keys": len(seen), "planned_keys": sum(r["n_curves"] for r in des.values()),
        "distinct_curves_checked": len(curves), "replication_records": len(rep),
        "not_checkable_from_records": [
            "minimality of plant_m (internal(m-1) is not recorded)",
            "the label sets themselves (only C and D are recorded), hence exact C, D values; only consistency bounds are checked",
            "the base points P_i and therefore any Q = O or duplicate skip for r >= 2",
            "seeded determinism of a record (requires the producer's generator and seed streams; maximum_runs 0)",
        ],
        "checks": ck.out(),
        "total_violations": sum(it["n_violations"] for it in ck.out()),
    }
    write_json("record-invariants.json", out)


def cmd_design():
    des = design()
    recs = load_jobs(MAIN_JOBS)
    obs = {}
    for _, rec in recs:
        obs.setdefault(rec["cell"], set()).add(rec["c"])
    rows = []
    for cell in CELL_IDS:
        row = dict(des[cell])
        cs = obs.get(cell, set())
        row["observed_records"] = len(cs)
        row["observed_c_range"] = [min(cs), max(cs)] if cs else None
        row["observed_matches_design"] = cs == set(range(row["n_curves"]))
        rows.append(row)
    out = {"task": "TASK-20261029-2c7b52", "joint": "J1",
           "rule": "n_curves = clamp(ceil(1.5 x 2500 / mu_ref), 50, 2000), mu_ref = 3 binom(n,4) / p_ref, p_ref = 0.75 x 2^bits (exact rationals)",
           "source": "specification.yaml /experiment/inputs/sizing",
           "cells": rows,
           "total_planned_jobs": sum(r["n_curves"] for r in rows),
           "any_cap_reached": any(r["ceil_unclamped"] > CLAMP_HI for r in rows),
           "any_ceil_argument_integer": any(r["ceil_arg_is_integer"] for r in rows),
           "float_path_agrees_everywhere": all(r["float_path_agrees"] for r in rows)}
    write_json("blind-design.json", out)


# ---------------------------------------------------------------- bootstrap seed (fixed before drawing)
SEED_RULE = ("seed(cell, family) = int.from_bytes(sha256(('TASK-20261029-2c7b52|J1|bootstrap|' + family + '|' + cell)"
             ".encode()).digest()[:8], 'big'); random.Random(seed); records sorted by curve index; each resample draws "
             "k = (number of ok curves) indices by rng.randrange(k) in sequence; 2000 resamples; kappa* = sum gap_C / "
             "sum mean null_C over the drawn curves (with multiplicity). Family A is the primary; family B is a "
             "Monte Carlo sensitivity draw only.")


def boot_seed(cell, family):
    s = "TASK-20261029-2c7b52|J1|bootstrap|%s|%s" % (family, cell)
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "big")


def cmd_seed():
    path = os.path.join(OUT, "bootstrap-seed.json")
    if os.path.exists(path):
        sys.exit("bootstrap-seed.json exists; the seed is written once, before drawing")
    out = {"task": "TASK-20261029-2c7b52", "joint": "J1", "written_before_any_draw": True, "rule": SEED_RULE,
           "families": ["A", "B"], "primary_family": "A", "resamples": BOOT_B,
           "python": sys.version,
           "seeds": {cell: {"A": boot_seed(cell, "A"), "B": boot_seed(cell, "B")} for cell in CELL_IDS}}
    write_json("bootstrap-seed.json", out)


# ---------------------------------------------------------------- per-cell statistics
def var_sum_sq(xs, divisor):
    k = len(xs)
    s = sum(xs)
    ss = sum(x * x for x in xs)
    return F(ss * k - s * s, k * divisor)


def zinfo(num, den2):
    """z = num / sqrt(den2), exact rational num and den2."""
    if den2 == 0:
        return {"z": None, "z_str": None, "abs_gt_4": None}
    z = dec(num) / dsqrt(den2)
    return {"z": float(z), "z_str": dstr(z), "num_exact": frac_str(num), "den2_exact": frac_str(den2), "_zd": z}


def abs_gt(num, den2, t):
    return num * num > t * t * den2


def gt(num, den2, t):
    return num > 0 and num * num > t * t * den2


def percentiles(sorted_vals):
    B = len(sorted_vals)
    # nearest rank: value at 1-based rank ceil(q B / 100)
    def nr(q):
        rank = -((-q * B) // 100)
        return sorted_vals[max(rank, 1) - 1]

    # linear interpolation (Hyndman-Fan type 7): h = (B - 1) q / 100, 0-based
    def lin(q):
        h = F(B - 1) * q / 100
        lo = h.numerator // h.denominator
        fr = h - lo
        if lo + 1 >= B:
            return sorted_vals[-1]
        return sorted_vals[lo] + fr * (sorted_vals[lo + 1] - sorted_vals[lo])

    q_lo, q_hi = F(5, 2), F(195, 2)
    return {"nearest_rank": [nr(q_lo), nr(q_hi)], "linear": [lin(q_lo), lin(q_hi)]}


def bootstrap(gs, sn, gd, sd, seed):
    """gs: gap_C per curve; sn: sum of 20 null_C per curve (mean = sn/20); gd, sd: same for D."""
    rng = random.Random(seed)
    k = len(gs)
    ks, ds = [], []
    for _ in range(BOOT_B):
        idx = [rng.randrange(k) for _ in range(k)]
        g = sum(gs[i] for i in idx)
        m = sum(sn[i] for i in idx)
        ks.append(F(NULL_REPS * g, m))
        g2 = sum(gd[i] for i in idx)
        m2 = sum(sd[i] for i in idx)
        ds.append(F(NULL_REPS * g2, m2))
    ks.sort()
    ds.sort()
    return percentiles(ks), percentiles(ds)


def cell_stats(cell, recs_cell, n_curves, seeds):
    bits, r, n = parse_cell(cell)
    ok = sorted([x for x in recs_cell if x["status"] == "ok"], key=lambda x: x["c"])
    ok_in_range = [x for x in ok if 0 <= x["c"] < n_curves]
    ok_cs = sorted({x["c"] for x in ok_in_range})
    nonok = sorted([{"c": x["c"], "status": x["status"]} for x in recs_cell if x["status"] != "ok"], key=lambda d: d["c"])
    st = {"cell": cell, "bits": bits, "r": r, "n": n, "n_curves": n_curves, "records": len(recs_cell),
          "ok_records": len(ok_cs), "non_ok_records": nonok}
    if not ok:
        st["empty"] = True
        return st
    gs = [x["gap_C"] for x in ok]
    sn = [sum(x["null_C"]) for x in ok]
    S = sum(gs)
    M = F(sum(sn), NULL_REPS)
    V_s = sum(var_sum_sq(x["null_C"], NULL_REPS - 1) for x in ok)
    V_p = sum(var_sum_sq(x["null_C"], NULL_REPS) for x in ok)
    Sp = sum(x["plant_C"] for x in ok)
    kappa = F(S) / M
    plant_kappa = F(Sp) / M
    fz = F(NULL_REPS + 1, NULL_REPS)
    z = zinfo(S - M, V_s * fz)
    z_pop = zinfo(S - M, V_p * fz)
    pz = zinfo(Sp - M, V_s * fz)
    pz_pop = zinfo(Sp - M, V_p * fz)
    # calibration: replicate 0 against replicates 1..19, pooled like z, variance factor 1 + 1/19
    S0 = sum(x["null_C"][0] for x in ok)
    M19 = sum(F(sum(x["null_C"][1:]), NULL_REPS - 1) for x in ok)
    V19_s = sum(var_sum_sq(x["null_C"][1:], NULL_REPS - 2) for x in ok)
    V19_p = sum(var_sum_sq(x["null_C"][1:], NULL_REPS - 1) for x in ok)
    fc = F(NULL_REPS, NULL_REPS - 1)
    zc = zinfo(S0 - M19, V19_s * fc)
    zc_pop = zinfo(S0 - M19, V19_p * fc)
    # Stouffer alternative: per-curve z, combined sum / sqrt(k); curves with zero variance skipped
    per = []
    for x in ok:
        v = var_sum_sq(x["null_C"][1:], NULL_REPS - 2)
        if v > 0:
            per.append(dec(F(x["null_C"][0]) - F(sum(x["null_C"][1:]), NULL_REPS - 1)) / dsqrt(v * fc))
    with localcontext() as ctx:
        ctx.prec = PREC
        zc_st = sum(per) / Decimal(len(per)).sqrt() if per else None
    # alternative: replicate 0 against the mean of the other 19 but with the cell's 20-replicate V
    zc_v20 = zinfo(S0 - M19, V_s * fc)
    # robustness: pooled z_cal with replicate j (list position j) as the pseudo-structured set
    zc_pos = []
    for j in range(NULL_REPS):
        Sj = sum(x["null_C"][j] for x in ok)
        oth = [[v for i, v in enumerate(x["null_C"]) if i != j] for x in ok]
        Mj = sum(F(sum(o), NULL_REPS - 1) for o in oth)
        Vj = sum(var_sum_sq(o, NULL_REPS - 2) for o in oth)
        zc_pos.append(zinfo(Sj - Mj, Vj * fc)["_zd"])
    gm_dup = [x["gap_meta"]["duplicate_skips"] for x in recs_cell]
    gm_inf = [x["gap_meta"]["infinity_skips"] for x in recs_cell]
    feas_rec = all(x["plant_feasible"] for x in ok)
    feas_rule = all(x["plant_internal"] >= PLANT_FRAC * F(sum(x["null_C"]), NULL_REPS) for x in ok)
    infeasible = [x["c"] for x in ok if not x["plant_feasible"]]
    gd = [x["gap_D"] for x in ok]
    sd = [sum(x["null_D"]) for x in ok]
    d_ratio = F(NULL_REPS * sum(gd), sum(sd))
    ev = [x for x in ok if x["c"] % 2 == 0]
    od = [x for x in ok if x["c"] % 2 == 1]
    k_even = F(NULL_REPS * sum(x["gap_C"] for x in ev), sum(sum(x["null_C"]) for x in ev)) if ev else None
    k_odd = F(NULL_REPS * sum(x["gap_C"] for x in od), sum(sum(x["null_C"]) for x in od)) if od else None
    formula = sum(F(3 * binom(n, 4), x["p"]) for x in ok)
    boot = {}
    for fam in ("A", "B"):
        kp, dp = bootstrap(gs, sn, gd, sd, seeds[fam])
        boot[fam] = {"kappa": kp, "d_ratio": dp}
    st.update({
        "curves_used": len(ok), "S": S, "M_exact": frac_str(M), "M": float(M),
        "V_exact": frac_str(V_s), "V": float(V_s), "V_population_exact": frac_str(V_p),
        "kappa_exact": frac_str(kappa), "kappa": float(kappa), "kappa_str": dstr(dec(kappa)),
        "z": z["z"], "z_str": z["z_str"], "z_population_variance": z_pop["z"],
        "powered": M >= TARGET,
        "plant_S": Sp, "plant_kappa_exact": frac_str(plant_kappa), "plant_kappa": float(plant_kappa),
        "plant_z": pz["z"], "plant_z_str": pz["z_str"], "plant_z_population_variance": pz_pop["z"],
        "plant_feasible_all_recorded": feas_rec, "plant_feasible_all_rederived": feas_rule,
        "plant_infeasible_curves": infeasible,
        "plant_m_range": [min(x["plant_m"] for x in ok), max(x["plant_m"] for x in ok)],
        "zcal_S0": S0, "zcal_M19_exact": frac_str(M19), "zcal_M19": float(M19), "zcal_V19_exact": frac_str(V19_s),
        "z_cal": zc["z"], "z_cal_str": zc["z_str"], "z_cal_population_variance": zc_pop["z"],
        "z_cal_stouffer": float(zc_st) if zc_st is not None else None,
        "z_cal_V20_alternative": zc_v20["z"],
        "z_cal_by_list_position": [float(v) for v in zc_pos],
        "gap_meta_summary": {"T": recs_cell[0]["gap_meta"]["T"], "records_with_duplicate_skips": sum(1 for v in gm_dup if v),
                             "max_duplicate_skips": max(gm_dup), "total_infinity_skips": sum(gm_inf)},
        "powered_by_M19": M19 >= TARGET,
        "d_ratio": float(d_ratio), "d_ratio_exact": frac_str(d_ratio),
        "kappa_even": float(k_even) if k_even is not None else None,
        "kappa_odd": float(k_odd) if k_odd is not None else None,
        "null_mean_over_formula": float(M / formula),
        "null_mean_over_formula_anomaly": not (F(4, 5) <= M / formula <= F(5, 4)),
        "bootstrap": {fam: {"kappa_ci95_nearest_rank": [float(v) for v in boot[fam]["kappa"]["nearest_rank"]],
                            "kappa_ci95_nearest_rank_exact": [frac_str(v) for v in boot[fam]["kappa"]["nearest_rank"]],
                            "kappa_ci95_linear": [float(v) for v in boot[fam]["kappa"]["linear"]],
                            "kappa_ci95_linear_exact": [frac_str(v) for v in boot[fam]["kappa"]["linear"]],
                            "d_ratio_ci95_nearest_rank": [float(v) for v in boot[fam]["d_ratio"]["nearest_rank"]],
                            "d_ratio_ci95_linear": [float(v) for v in boot[fam]["d_ratio"]["linear"]]}
                      for fam in boot},
        "_exact": {"M": M, "V_s": V_s, "V_p": V_p, "S": S, "Sp": Sp, "S0": S0, "M19": M19, "V19_s": V19_s,
                   "V19_p": V19_p, "zcal_d": zc["_zd"], "zcal_pop_d": zc_pop["_zd"], "zcal_st_d": zc_st,
                   "zcal_v20_d": zc_v20["_zd"], "zcal_pos_d": zc_pos,
                   "boot": boot},
    })
    return st


def cmd_cells():
    seed_path = os.path.join(OUT, "bootstrap-seed.json")
    if not os.path.exists(seed_path):
        sys.exit("refusing: bootstrap-seed.json must be written (seed subcommand) before drawing")
    seeds = json.load(open(seed_path))["seeds"]
    des = design()
    recs = [r for _, r in load_jobs(MAIN_JOBS)]
    by = {}
    for r in recs:
        by.setdefault(r["cell"], []).append(r)
    cells = []
    for cell in CELL_IDS:
        st = cell_stats(cell, by.get(cell, []), des[cell]["n_curves"], seeds[cell])
        st["cls"] = classify(st, BASE)
        ex = st["_exact"]
        st["ci95"] = st["bootstrap"]["A"]["kappa_ci95_nearest_rank"]
        st["ci95_convention"] = "family A seed, nearest-rank"
        st["planted_recovered"] = bool(st["plant_feasible_all_recorded"] and F(ex["Sp"]) / ex["M"] >= PLANT_K
                                       and gt(ex["Sp"] - ex["M"], ex["V_s"] * F(NULL_REPS + 1, NULL_REPS), PLANT_Z))
        st["flag_rule_met"] = bool(abs(F(ex["S"]) / ex["M"] - 1) >= FLAG_K and abs_gt(ex["S"] - ex["M"], ex["V_s"] * F(NULL_REPS + 1, NULL_REPS), FLAG_Z))
        st.pop("_exact", None)
        cells.append(st)
    out = {"task": "TASK-20261029-2c7b52", "joint": "J1",
           "conventions": {
               "S": "sum over ok curves (sorted by c) of gap_C (integer)",
               "M": "sum over ok curves of the mean of the 20 null_C (exact rational)",
               "V": "sum over ok curves of the SAMPLE variance (divisor 19) of the 20 null_C, as the statement says; V_population (divisor 20) reported for sensitivity",
               "kappa": "S / M exact",
               "z": "(S - M) / sqrt(V (1 + 1/20)), Decimal at 60 digits; threshold comparisons decided exactly as (S-M)^2 vs 16 V 21/20",
               "plant": "plant_kappa = sum plant_C / M, plant_z = (sum plant_C - M) / sqrt(V 21/20) with the same M and V",
               "z_cal": "pooled over the cell's ok curves exactly like z: (sum null_C[0] - sum mean(null_C[1..19])) / sqrt(sum samplevar(null_C[1..19]) (1 + 1/19)); Stouffer and population-variance alternatives reported",
               "bootstrap": SEED_RULE + " Percentiles 2.5 and 97.5 under nearest-rank (rank ceil(qB/100), i.e. 50th and 1950th of 2000) and linear interpolation (h = (B-1) q/100, type 7).",
               "plant_feasible": "recorded per-job flag; rederived as plant_internal >= 0.30 x mean(null_C) for comparison",
               "invalid_cells": "statistics of an invalid cell are computed over its ok records and are descriptive only",
               "null_mean_over_formula": "M / sum over ok curves of 3 binom(n,4)/p_curve; anomaly outside [0.8, 1.25] (R6), descriptive"},
           "cells": cells}
    write_json("blind-cells.json", out)


# ---------------------------------------------------------------- classes, gate, reading
BASE = {"var": "sample", "ci": "nearest_rank", "fam": "A", "cal_set": "powered_by_M_all", "zcal": "pooled",
        "cal_sd": "population", "ok_acc": "strict", "plant_first": False, "ci_inside": "closed",
        "feas": "recorded"}


def compute_all():
    seeds = json.load(open(os.path.join(OUT, "bootstrap-seed.json")))["seeds"]
    des = design()
    recs = [r for _, r in load_jobs(MAIN_JOBS)]
    by = {}
    for r in recs:
        by.setdefault(r["cell"], []).append(r)
    return {cell: cell_stats(cell, by.get(cell, []), des[cell]["n_curves"], seeds[cell]) for cell in CELL_IDS}


def classify(st, o):
    ex = st["_exact"]
    fz = F(NULL_REPS + 1, NULL_REPS)
    V = ex["V_s"] if o["var"] == "sample" else ex["V_p"]
    M, S, Sp = ex["M"], ex["S"], ex["Sp"]
    kappa = F(S) / M
    if o["ok_acc"] == "strict":
        invalid = st["ok_records"] < st["n_curves"]
    else:  # inadmissible reading: count records present regardless of status
        invalid = st["records"] < st["n_curves"]
    if invalid:
        return "invalid"
    feas = st["plant_feasible_all_recorded"] if o["feas"] == "recorded" else st["plant_feasible_all_rederived"]
    plant_ok = feas and F(Sp) / M >= PLANT_K and gt(Sp - M, V * fz, PLANT_Z)
    powered = M >= TARGET
    if o["plant_first"]:
        if not plant_ok:
            return "inconclusive_plant_not_recovered"
        if not powered:
            return "inconclusive_underpowered"
    else:
        if not powered:
            return "inconclusive_underpowered"
        if not plant_ok:
            return "inconclusive_plant_not_recovered"
    if abs(kappa - 1) >= FLAG_K and abs_gt(S - M, V * fz, FLAG_Z):
        return "flagged"
    lo, hi = ex["boot"][o["fam"]]["kappa"][o["ci"]]
    inside = (CI_LO <= lo and hi <= CI_HI) if o["ci_inside"] == "closed" else (CI_LO < lo and hi < CI_HI)
    if abs(kappa - 1) < NULL_K and inside:
        return "null"
    return "intermediate"


def gate(stats, classes, o):
    sel = []
    for cell in CELL_IDS:
        st = stats[cell]
        ex = st["_exact"]
        if o["cal_set"] == "powered_by_M_all":
            use = ex["M"] >= TARGET
        elif o["cal_set"] == "powered_by_M_noninvalid":
            use = ex["M"] >= TARGET and classes[cell] != "invalid"
        elif o["cal_set"] == "powered_by_M19_all":
            use = ex["M19"] >= TARGET
        elif o["cal_set"] == "powered_valid_classes":
            use = ex["M"] >= TARGET and classes[cell] in ("null", "flagged", "intermediate")
        else:
            raise ValueError(o["cal_set"])
        if use:
            if o["zcal"] == "pooled":
                zc = ex["zcal_d"] if o["var"] == "sample" else ex["zcal_pop_d"]
            elif o["zcal"] == "stouffer":
                zc = ex["zcal_st_d"]
            elif o["zcal"] == "pooled_V20":
                zc = ex["zcal_v20_d"]
            elif o["zcal"].startswith("position_"):
                zc = ex["zcal_pos_d"][int(o["zcal"].split("_")[1])]
            else:
                raise ValueError(o["zcal"])
            sel.append((cell, zc))
    k = len(sel)
    with localcontext() as ctx:
        ctx.prec = PREC
        zs = [z for _, z in sel]
        mean = sum(zs) / k
        ssd = sum((z - mean) ** 2 for z in zs)
        sd_pop = (ssd / k).sqrt()
        sd_smp = (ssd / (k - 1)).sqrt()
    sd = sd_pop if o["cal_sd"] == "population" else sd_smp
    passed = (dec(GATE_SD_LO) <= sd <= dec(GATE_SD_HI)) and abs(mean) <= dec(GATE_MEAN)
    return {"n": k, "cells": [c for c, _ in sel], "mean": float(mean), "mean_str": dstr(mean),
            "sd_population": float(sd_pop), "sd_population_str": dstr(sd_pop), "sd_sample": float(sd_smp),
            "sd_used": o["cal_sd"], "pass": passed,
            "margins": {"sd_to_lower": float(sd - dec(GATE_SD_LO)), "sd_to_upper": float(dec(GATE_SD_HI) - sd),
                        "abs_mean_to_bound": float(dec(GATE_MEAN) - abs(mean))}}


def reading(stats, o, rep_records):
    classes = {cell: classify(stats[cell], o) for cell in CELL_IDS}
    g = gate(stats, classes, o)
    valid = [c for c in CELL_IDS if classes[c] in ("null", "flagged", "intermediate")]
    fv = F(len(valid), len(CELL_IDS))
    flagged = [c for c in CELL_IDS if classes[c] == "flagged"]
    # replication: complete iff distinct ok replication curves == n_curves of the cell (R7)
    rep_by = {}
    for r in rep_records:
        if r.get("block") == "replication" and r.get("status") == "ok":
            rep_by.setdefault(r["cell"], set()).add(r["c"])
    complete = {c: rep_by.get(c, set()) >= set(range(stats[c]["n_curves"])) for c in flagged}

    def outcome(stage):
        if not g["pass"] or fv < VALID_MIN:
            return "O-INVALID"
        if stage == "final" and any(complete[c] for c in flagged):
            # replication statistics are only needed when replication records exist; the actual
            # toy-rep-jobs.jsonl is empty, so this branch is not implemented rather than guessed
            raise NotImplementedError("replication survival with non-empty replication records")
        if any(not complete[c] for c in flagged) and flagged:
            return "O-PENDING-REPLICATION"
        if all(classes[c] == "null" for c in valid) and fv >= NULL_FRAC:
            return "O-NULL"
        return "O-MIXED"

    out_main = outcome("main")
    out_final = outcome("final")
    final_effective = "O-MIXED (pending repair)" if out_final == "O-PENDING-REPLICATION" else out_final

    def headline(oc):
        if oc == "O-STRUCT":
            return "FALSIFY_SCOPED"
        if oc == "O-INVALID":
            return "NOT_EVIDENCE"
        if oc == "O-NULL":
            return "SUPPORT_SCOPED"
        return "INCONCLUSIVE"

    counts = {}
    for c in CELL_IDS:
        counts[classes[c]] = counts.get(classes[c], 0) + 1
    return {"classes": classes, "class_counts": counts, "calibration": g, "valid_cells": valid,
            "n_valid": len(valid), "fraction_valid_exact": frac_str(fv), "fraction_valid": float(fv),
            "flagged_cells": flagged, "replication_complete": complete,
            "outcome_main": out_main, "outcome_final": out_final, "outcome_final_effective": final_effective,
            "headline": headline(out_final)}


def summarize(rd):
    return {"class_counts": rd["class_counts"], "gate_pass": rd["calibration"]["pass"],
            "gate_n": rd["calibration"]["n"], "gate_mean": rd["calibration"]["mean"],
            "gate_sd_population": rd["calibration"]["sd_population"], "gate_sd_sample": rd["calibration"]["sd_sample"],
            "fraction_valid": rd["fraction_valid_exact"], "flagged": rd["flagged_cells"],
            "outcome_main": rd["outcome_main"], "outcome_final": rd["outcome_final"], "headline": rd["headline"]}


def diff(base, alt):
    ch = [c for c in CELL_IDS if base["classes"][c] != alt["classes"][c]]
    return {"classes_changed": [{"cell": c, "base": base["classes"][c], "alt": alt["classes"][c]} for c in ch],
            "gate_pass_changes": base["calibration"]["pass"] != alt["calibration"]["pass"],
            "fraction_valid_changes": base["fraction_valid_exact"] != alt["fraction_valid_exact"],
            "flagged_set_changes": base["flagged_cells"] != alt["flagged_cells"],
            "reading_changes": (base["outcome_main"], base["outcome_final"]) != (alt["outcome_main"], alt["outcome_final"]),
            "headline_changes": base["headline"] != alt["headline"]}


def cmd_reading():
    stats = compute_all()
    rep = [r for _, r in load_jobs(REP_JOBS) if r is not None]
    base = reading(stats, BASE, rep)
    des = design()
    required_rep = [{"cell": c, "block": "replication", "n_curves": des[c]["n_curves"],
                     "curve_indices": "0..%d" % (des[c]["n_curves"] - 1),
                     "curve_seeds": "%d..%d" % (SEED_OFFSET["replication"], SEED_OFFSET["replication"] + des[c]["n_curves"] - 1),
                     "status_required": "ok for every curve (complete: distinct ok curves == n_curves, R7)"}
                    for c in base["flagged_cells"]]
    margins = []
    for c in CELL_IDS:
        st = stats[c]
        ex = st["_exact"]
        row = {"cell": c, "class": base["classes"][c], "kappa": float(F(ex["S"]) / ex["M"]), "z": st["z"]}
        for fam in ("A", "B"):
            for conv in ("nearest_rank", "linear"):
                lo, hi = ex["boot"][fam]["kappa"][conv]
                row["ci_%s_%s" % (fam, conv)] = [float(lo), float(hi)]
        row["min_margin_to_band"] = min(float(min(ex["boot"][f]["kappa"][cv][0] - CI_LO, CI_HI - ex["boot"][f]["kappa"][cv][1]))
                                        for f in ("A", "B") for cv in ("nearest_rank", "linear"))
        row["kappa_margin_to_0.05"] = float(NULL_K - abs(F(ex["S"]) / ex["M"] - 1))
        row["kappa_margin_to_0.10"] = float(FLAG_K - abs(F(ex["S"]) / ex["M"] - 1))
        row["plant_kappa_margin_to_1.15"] = float(F(ex["Sp"]) / ex["M"] - PLANT_K)
        row["plant_z"] = st["plant_z"]
        row["M_margin_to_2500"] = float(ex["M"] - TARGET)
        margins.append(row)
    rd = {"task": "TASK-20261029-2c7b52", "joint": "J1", "resolution_set": BASE,
          "calibration": base["calibration"],
          "class_per_cell": base["classes"], "class_counts": base["class_counts"],
          "valid_cells": base["valid_cells"], "n_valid": base["n_valid"],
          "fraction_valid_exact": base["fraction_valid_exact"], "fraction_valid": base["fraction_valid"],
          "invalid_cells": [{"cell": c, "ok_records": stats[c]["ok_records"], "n_curves": stats[c]["n_curves"],
                             "non_ok_records": stats[c]["non_ok_records"]}
                            for c in CELL_IDS if base["classes"][c] == "invalid"],
          "flagged_cells": base["flagged_cells"],
          "replication": {"rule": "every flagged cell re-run on the replication block with its n_curves; survives iff same sign, |z| > 3, |kappa - 1| >= 0.05",
                          "required_content": required_rep,
                          "required_record_count": sum(x["n_curves"] for x in required_rep),
                          "actual_records": len(rep),
                          "file_sha256": sha256_file(os.path.join(ROOT, REP_JOBS)),
                          "satisfies_rule": (len(rep) == 0 and not required_rep) or all(base["replication_complete"].values()) and bool(required_rep),
                          "note": "spec replication.trials census-toy-rep note and stopping_rules: an empty toy-rep-jobs.jsonl is the recorded result when no cell is flagged"},
          "outcome_main": base["outcome_main"], "outcome_final": base["outcome_final"],
          "outcome_final_effective": base["outcome_final_effective"], "headline": base["headline"],
          "tail_checks": {
              "max_abs_z_over_powered": max((abs(stats[c]["z"]), c) for c in CELL_IDS if stats[c]["powered"] and base["classes"][c] != "invalid"),
              "cells_abs_z_gt_3": [c for c in CELL_IDS if stats[c]["z"] is not None and abs(stats[c]["z"]) > 3],
              "plant_infeasible_cells": [c for c in CELL_IDS if not stats[c]["plant_feasible_all_recorded"]],
              "null_mean_over_formula_anomalies": [c for c in CELL_IDS if stats[c]["null_mean_over_formula_anomaly"]],
              "intermediate_cells": [c for c in CELL_IDS if base["classes"][c] == "intermediate"]},
          "margins": margins}
    # secondary slope (descriptive)
    slopes = {}
    for b in BITS:
        for r in RANKS:
            pts = [(math.log2(n), math.log(F(stats[cell_id(b, r, n)]["_exact"]["S"]) / stats[cell_id(b, r, n)]["_exact"]["M"]))
                   for n in NS if base["classes"][cell_id(b, r, n)] in ("null", "flagged", "intermediate")
                   and stats[cell_id(b, r, n)]["_exact"]["S"] > 0]
            if len(pts) >= 3:
                mx = statistics.fmean(x for x, _ in pts)
                my = statistics.fmean(y for _, y in pts)
                slopes["b%d-r%d" % (b, r)] = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x, _ in pts)
            else:
                slopes["b%d-r%d" % (b, r)] = None
    rd["secondary_slope_logkappa_per_log2n"] = slopes
    write_json("blind-reading.json", rd)

    # ---- ambiguity table
    def alt(**kw):
        o = dict(BASE)
        o.update(kw)
        a = reading(stats, o, rep)
        return {"resolution": kw, "summary": summarize(a), "effect": diff(base, a)}

    def combo_all():
        res = []
        for var in ("sample", "population"):
            for ci in ("nearest_rank", "linear"):
                for fam in ("A", "B"):
                    for cal_set in ("powered_by_M_all", "powered_by_M_noninvalid", "powered_by_M19_all", "powered_valid_classes"):
                        for zc in ("pooled", "stouffer", "pooled_V20"):
                            for cal_sd in ("population", "sample"):
                                for pf in (False, True):
                                    for cin in ("closed", "open"):
                                        for feas in ("recorded", "rederived"):
                                            o = dict(var=var, ci=ci, fam=fam, cal_set=cal_set, zcal=zc, cal_sd=cal_sd,
                                                     ok_acc="strict", plant_first=pf, ci_inside=cin, feas=feas)
                                            a = reading(stats, o, rep)
                                            res.append((o, a))
        return res

    rows = [
        {"id": "A1", "topic": "null variance divisor in V (sample vs population)",
         "text": "statistics.per_cell: 'V = sum of per-curve null sample variances'",
         "chosen": "sample variance (divisor 19), as stated", "admissible_alternatives": [alt(var="population")],
         "note": "population divisor 20 multiplies z, plant_z and z_cal by sqrt(20/19) (z_cal by sqrt(19/18)); the statement says sample, so the alternative is a misreading tested for sensitivity"},
        {"id": "A2", "topic": "calibration-gate sd divisor (population vs sample sd of z_cal)",
         "text": "calibration_gate: 'population sd of z_cal in [0.75, 1.25]'; R1 speaks of 'the sampling sd of a sample sd'",
         "chosen": "population sd (divisor n), as stated", "admissible_alternatives": [alt(cal_sd="sample")]},
        {"id": "A3", "topic": "which cells form the calibration set ('over powered cells')",
         "text": "calibration_gate 'over powered cells'; statistics 'powered: M >= 2500'",
         "chosen": "every cell whose M (20-replicate null mean summed over its ok curves) >= 2500, the invalid cell included",
         "admissible_alternatives": [alt(cal_set="powered_by_M_noninvalid"), alt(cal_set="powered_by_M19_all"),
                                     alt(cal_set="powered_valid_classes")]},
        {"id": "A4", "topic": "pooling of z_cal over a cell's curves",
         "text": "statistics.per_cell: 'z_cal = null replicate 0 of each curve as a pseudo-structured set against the other 19 (variance factor 1 + 1/19)'",
         "chosen": "pooled exactly like z (sum over curves, then one z per cell); sample variance of replicates 1..19 (divisor 18)",
         "admissible_alternatives": [alt(zcal="stouffer"), alt(var="population"), alt(zcal="pooled_V20")],
         "note": "the population alternative of A4 is shared with A1 (it changes V and V19 together)"},
        {"id": "A5", "topic": "bootstrap seed (spec: 'seeded per cell', seed not given in the allowlist)",
         "text": "statistics.per_cell bootstrap; R7",
         "chosen": "family A seed written in bootstrap-seed.json before drawing", "admissible_alternatives": [alt(fam="B")],
         "note": "the producer's per-cell seed is not derivable from the allowlist; any seed is admissible, so interval edges are reproducible only up to Monte Carlo error; family B measures that error"},
        {"id": "A6", "topic": "bootstrap percentile convention",
         "text": "'percentile 2.5 and 97.5'",
         "chosen": "nearest-rank (50th and 1950th of 2000 sorted)", "admissible_alternatives": [alt(ci="linear"), alt(ci="linear", fam="B")]},
        {"id": "A7", "topic": "'interval inside [0.90, 1.10]': closed or open band",
         "text": "cell_classes.null", "chosen": "closed band (lo >= 0.90 and hi <= 1.10)",
         "admissible_alternatives": [alt(ci_inside="open")]},
        {"id": "A8", "topic": "how degenerate / failed records enter 'ok records'",
         "text": "cell_classes.invalid: 'fewer ok main-census records than n_curves (failed_infrastructure or degenerate)'; log_gap_builder 'a cell with a degenerate curve is invalid, never null'",
         "chosen": "a degenerate record is not ok; a cell is invalid when distinct ok curves < n_curves",
         "admissible_alternatives": [],
         "inadmissible_alternative_tested": None,
         "note": "the parenthetical names degenerate records as the shortfall, and the builder text says a degenerate curve makes its cell invalid; counting a degenerate record as present is not an admissible reading"},
        {"id": "A9", "topic": "plant feasibility decided before or after power",
         "text": "cell_classes order: invalid, inconclusive_underpowered, inconclusive_plant_not_recovered, ...",
         "chosen": "frozen order (power first)", "admissible_alternatives": [alt(plant_first=True)]},
        {"id": "A10", "topic": "source of plant feasibility (recorded per-job flag vs re-derived from plant_internal and the null mean)",
         "text": "planted_builder; schema plant_feasible", "chosen": "recorded flag (I19 checks agreement)",
         "admissible_alternatives": [alt(feas="rederived")]},
    ]
    # A8 inadmissible sensitivity: classify the invalid cell(s) on their ok records as if complete
    o8 = dict(BASE)
    o8["ok_acc"] = "records_present"
    a8 = reading(stats, o8, rep)
    rows[7]["inadmissible_alternative_tested"] = {"resolution": {"ok_acc": "records_present (degenerate counted as present)"},
                                                  "summary": summarize(a8), "effect": diff(base, a8)}
    # A11: replication outcome label at analyze-final
    rows.append({"id": "A11", "topic": "outcome label at analyze-final when a flagged cell has no replication records",
                 "text": "toy_reading_rules O-PENDING-REPLICATION: 'at analyze-final it means the replication did not run and the reading is O-MIXED pending repair'",
                 "chosen": "field value O-PENDING-REPLICATION read as O-MIXED pending repair; headline INCONCLUSIVE either way",
                 "admissible_alternatives": [],
                 "applies": bool(base["flagged_cells"]),
                 "note": "moot unless the flagged set is non-empty"})
    pos_alts = [alt(zcal="position_%d" % j) for j in range(1, NULL_REPS)]
    rows.append({"id": "A14", "topic": "which list position of null_C is 'replicate 0' (schema: 'null_C (20 counts)', order not stated)",
                 "text": "statistics.per_cell z_cal; artifact_schema toy_jobs_jsonl",
                 "chosen": "list position 0 is replicate 0",
                 "admissible_alternatives": [pos_alts[-1]],
                 "robustness_all_positions": {"gate_pass_by_position": [True if j == 0 else pos_alts[j - 1]["summary"]["gate_pass"] for j in range(NULL_REPS)],
                                              "gate_mean_by_position": [base["calibration"]["mean"]] + [a["summary"]["gate_mean"] for a in pos_alts],
                                              "gate_sd_population_by_position": [base["calibration"]["sd_population"]] + [a["summary"]["gate_sd_population"] for a in pos_alts]},
                 "note": "only position 19 (a reversed list) is a plausible alternative reading; positions 1..18 are reported as a robustness check of the gate against the choice of pseudo-structured replicate, not as admissible readings"})
    rows.append({"id": "A15", "topic": "P1 and the hypothesis say 'every powered toy cell'; O-NULL says 'every valid cell'",
                 "text": "preregistered_predictions P1 vs toy_reading_rules O-NULL; hypothesis statement",
                 "chosen": "the toy_reading_rules decide the outcome field; the powered-but-invalid cell b20-r3-n4096 is not read",
                 "admissible_alternatives": [], "inadmissible_alternative_tested": "see A8 (the invalid cell read on its 46 ok curves classifies null)",
                 "note": "no flip: read on its ok curves the invalid cell would itself be null, so the two texts do not disagree on these records; the scope of the reading is 44 of 45 cells"})
    rows.append({"id": "A12", "topic": "sizing arithmetic: exact rational vs floating point ceil",
                 "text": "inputs.sizing", "chosen": "exact rationals",
                 "admissible_alternatives": [], "note": "blind-design.json: float_path_agrees_everywhere and no ceil argument is an integer, so no cell can move"})
    rows.append({"id": "A13", "topic": "'powered' threshold for an invalid cell's partial M",
                 "text": "statistics.powered", "chosen": "M over the ok curves of that cell",
                 "admissible_alternatives": [], "note": "only affects A3 (calibration membership); covered there"})
    allc = combo_all()
    flips = [{"resolution": o, "summary": summarize(a), "effect": diff(base, a)} for o, a in allc
             if any(v for k, v in diff(base, a).items() if k != "classes_changed") or diff(base, a)["classes_changed"]]
    amb = {"task": "TASK-20261029-2c7b52", "joint": "J1", "base_resolution": BASE, "base_summary": summarize(base),
           "rows": rows,
           "full_cross_product": {"n_combinations": len(allc),
                                  "dimensions": ["var", "ci", "fam", "cal_set", "zcal", "cal_sd", "plant_first", "ci_inside", "feas"],
                                  "n_combinations_with_any_change": len(flips),
                                  "distinct_headlines": sorted({a["headline"] for _, a in allc}),
                                  "distinct_outcomes_final": sorted({a["outcome_final"] for _, a in allc}),
                                  "distinct_gate_pass": sorted({a["calibration"]["pass"] for _, a in allc}),
                                  "distinct_fraction_valid": sorted({a["fraction_valid_exact"] for _, a in allc}),
                                  "distinct_flagged_sets": sorted({tuple(a["flagged_cells"]) for _, a in allc}),
                                  "gate_sd_range": [min(a["calibration"]["sd_population"] if o["cal_sd"] == "population" else a["calibration"]["sd_sample"] for o, a in allc),
                                                    max(a["calibration"]["sd_population"] if o["cal_sd"] == "population" else a["calibration"]["sd_sample"] for o, a in allc)],
                                  "gate_abs_mean_range": [min(abs(a["calibration"]["mean"]) for _, a in allc), max(abs(a["calibration"]["mean"]) for _, a in allc)],
                                  "changed_examples": flips[:40]}}
    write_json("ambiguity-table.json", amb)


def cmd_freeze():
    files = sorted(f for f in os.listdir(OUT) if f != "freeze-manifest.json")
    scripts = sorted(os.listdir(HERE))
    out = {"task": "TASK-20261029-2c7b52", "joint": "J1", "frozen": True,
           "outputs": {"out/outputs/" + f: sha256_file(os.path.join(OUT, f)) for f in files},
           "scripts": {"out/scripts/" + f: sha256_file(os.path.join(HERE, f)) for f in scripts if f.endswith((".py", ".txt"))},
           "python": sys.version}
    path = os.path.join(OUT, "freeze-manifest.json")
    if os.path.exists(path):
        sys.exit("freeze-manifest.json exists; outputs are frozen")
    write_json("freeze-manifest.json", out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"invariants": cmd_invariants, "design": cmd_design, "seed": cmd_seed, "cells": cmd_cells,
     "reading": cmd_reading, "freeze": cmd_freeze}[cmd]()
