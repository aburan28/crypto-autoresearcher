#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J2 (construction and draw fidelity).

Written by the validator from the EXP-CERTBIN-ddfe75 specification text
(object.E_layout, object.parts, object.union_support, instance_sets.fresh_arms,
generator_rule, keep_rule). It imports NOTHING from impl/, verifier/ or
src/crypto_autoresearcher/. numpy is used as a container and for the frozen
numpy.random.Generator(PCG64) stream only.

What it does:
  S0  self-tests: F_{2^17} irreducibility; S_3 against elliptic-curve point
      addition on the archived curve; the Mobius-interpolated descent against
      direct field evaluation at random v; the exhaustive evaluator against
      naive per-assignment evaluation.
  S1  own E_S3(x_R) at all 144 archived x_R versus the archived E_hex of
      instance-sets.json; E_sha256 convention versus the archived E_sha256.
  S2  own union support U and S_L versus support.json.
  S3  stream replays from the seeds: N-CONV slots 0..9 and N-CONVL slots 0..4
      (required by the card), then, as an extension, the FULL streams of all
      four fresh arms; compared attempt by attempt with draws-<ARM>.jsonl.gz
      (E_sha256, s, outcome, b'/c) and kept systems with instances.jsonl.gz.
  S4  full construction sweep over every kept system of every arm.
Output: j2-results.json next to this file.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import random
import sys
import time
from itertools import combinations
from pathlib import Path

import numpy as np

WT = Path(sys.argv[1])  # worktree at c7f5e3dfa
OUTDIR = Path(__file__).resolve().parent
RUN = WT / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
FULL = "--full" in sys.argv

# ---------------------------------------------------------------- F_{2^17}
N = 17
POLY = (1 << 17) | (1 << 3) | 1


def fmul(a, b):
    r = 0
    for i in range(N):
        if (b >> i) & 1:
            r ^= a << i
    for d in range(2 * N - 2, N - 1, -1):
        if (r >> d) & 1:
            r ^= POLY << (d - N)
    return r


def fpow(a, e):
    r = 1
    while e:
        if e & 1:
            r = fmul(r, a)
        a = fmul(a, a)
        e >>= 1
    return r


def finv(a):
    return fpow(a, (1 << N) - 2)


def ftr(a):
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = fmul(x, x)
    return s


def half_trace(c):
    s, x = 0, c
    for _ in range((N - 1) // 2 + 1):
        s ^= x
        x = fmul(fmul(x, x), fmul(x, x))
    return s


# ---------------------------------------------------------------- layout
NV, NEQ = 18, 17
MONOS = [()] + [(i,) for i in range(NV)] + list(combinations(range(NV), 2))
NCOL = len(MONOS)
assert NCOL == 172
COL = {m: j for j, m in enumerate(MONOS)}
QUADCOLS = set(range(19, 172))


def ehex(rows):
    return [format(r, "x") for r in rows]


def esha(rows_or_hex):
    h = rows_or_hex if isinstance(rows_or_hex[0], str) else ehex(rows_or_hex)
    return hashlib.sha256(json.dumps(h).encode()).hexdigest()


# ---------------------------------------------------------------- S_3
def s3(x1, x2, x3, B):
    t = fmul(x1, x2) ^ fmul(x1, x3) ^ fmul(x2, x3)
    return fmul(t, t) ^ fmul(fmul(x1, x2), x3) ^ B


TP = [fpow(2, j) for j in range(N)]  # t^j


def xs_of(v):
    x1 = x2 = 0
    for i in range(9):
        if (v >> i) & 1:
            x1 ^= TP[i]
        if (v >> (9 + i)) & 1:
            x2 ^= TP[i]
    return x1, x2


def descent_coeffs(xR, B):
    """Coefficients (F_{2^17}) of the multilinear degree<=2 polynomial
    v -> S_3(x1(v), x2(v), xR), by Mobius inversion from evaluations at all
    v of Hamming weight <= 2 (valid because the polynomial has degree <= 2;
    checked separately at random v in S0)."""
    val = {}

    def ev(v):
        if v not in val:
            x1, x2 = xs_of(v)
            val[v] = s3(x1, x2, xR, B)
        return val[v]

    c = [0] * NCOL
    f0 = ev(0)
    c[0] = f0
    for i in range(NV):
        c[COL[(i,)]] = ev(1 << i) ^ f0
    for (i, j) in combinations(range(NV), 2):
        c[COL[(i, j)]] = ev((1 << i) | (1 << j)) ^ ev(1 << i) ^ ev(1 << j) ^ f0
    return c


def coeffs_to_rows(c):
    rows = [0] * NEQ
    for col, x in enumerate(c):
        for k in range(NEQ):
            if (x >> k) & 1:
                rows[k] |= 1 << col
    return rows


def E_S3(xR, B):
    return coeffs_to_rows(descent_coeffs(xR, B))


def eval_poly_coeffs(c, v):
    acc = 0
    for col, m in enumerate(MONOS):
        if c[col] and all((v >> i) & 1 for i in m):
            acc ^= c[col]
    return acc


def eval_rows_naive(rows, v):
    out = 0
    for k, r in enumerate(rows):
        acc = 0
        for col in range(NCOL):
            if (r >> col) & 1 and all((v >> i) & 1 for i in MONOS[col]):
                acc ^= 1
        out |= acc << k
    return out


# ---------------------------------------------------------------- exhaustive s
# Truth tables as Python ints of 2^18 bits: bit u = value at assignment u
# (bit i of u = v_i). numpy only builds the byte strings.
NA = 1 << NV
_u = np.arange(NA, dtype=np.uint32)
VT = []
for i in range(NV):
    bits = ((_u >> i) & 1).astype(np.uint8)
    VT.append(int.from_bytes(np.packbits(bits, bitorder="little").tobytes(), "little"))
ALL1 = (1 << NA) - 1
MT = []
for m in MONOS:
    t = ALL1
    for i in m:
        t &= VT[i]
    MT.append(t)


def count_s(rows, want=False):
    bad = 0
    for r in rows:
        acc = 0
        x = r
        while x:
            b = (x & -x).bit_length() - 1
            acc ^= MT[b]
            x &= x - 1
        bad |= acc
    good = ALL1 & ~bad
    s = good.bit_count()
    if not want:
        return s, None
    sols = []
    x = good
    while x:
        b = (x & -x).bit_length() - 1
        sols.append(b)
        x &= x - 1
    return s, sols


# ---------------------------------------------------------------- curve
def curve_points(A, B, count, rng):
    pts = []
    while len(pts) < count:
        x = rng.randrange(1, 1 << N)
        c = x ^ A ^ fmul(B, finv(fmul(x, x)))
        if ftr(c) != 0:
            continue
        z = half_trace(c)
        y = fmul(x, z)
        assert fmul(y, y) ^ fmul(x, y) == fmul(fmul(x, x), x) ^ fmul(A, fmul(x, x)) ^ B
        pts.append((x, y))
    return pts


def padd(P, Q, A):
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2:
        return None
    lam = fmul(y1 ^ y2, finv(x1 ^ x2))
    x3 = fmul(lam, lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = fmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    R = {"task": "TASK-20260926-0f8aec", "joint": "J2", "worktree_commit": None}
    import subprocess
    R["worktree_commit"] = subprocess.run(["git", "-C", str(WT), "rev-parse", "HEAD"],
                                          capture_output=True, text=True).stdout.strip()
    R["numpy_version"] = np.__version__
    curve = json.load(open(WT / "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json"))
    A, B = int(curve["A"]), int(curve["B"])
    rng = random.Random(20260926)

    # S0 self-tests ---------------------------------------------------------
    S0 = {}
    x = 2
    for _ in range(N):
        x = fmul(x, x)
    S0["t^(2^17)==t"] = (x == 2)
    # no factor of degree <= 8: gcd(t^(2^i)-t, f) = 1 for i=1..8 (f of degree 17 is
    # irreducible iff t^(2^17)=t and gcd(t^(2^(17/p)) - t, f)=1 for prime p|17; 17
    # prime, so t^(2^17)=t plus f having no root suffices; we check i<=8 anyway)

    def pgcd(a, b):
        while b:
            while a.bit_length() >= b.bit_length():
                a ^= b << (a.bit_length() - b.bit_length())
            a, b = b, a
        return a
    x = 2
    ok = True
    for i in range(1, 9):
        x = fmul(x, x)
        ok &= pgcd(POLY, x ^ 2) == 1
    S0["gcd(t^(2^i)-t,f)==1 for i<=8"] = ok
    pts = curve_points(A, B, 60, rng)
    s3ok = 0
    for i in range(0, 60, 2):
        P, Q = pts[i], pts[i + 1]
        Rp = padd(P, Q, A)
        if Rp is None:
            continue
        s3ok += int(s3(P[0], Q[0], Rp[0], B) == 0)
    S0["S3_vs_point_addition_zero"] = s3ok
    S0["S3_vs_point_addition_trials"] = 30
    # nonzero on random triples (S_3 is not identically 0)
    S0["S3_random_triples_nonzero"] = sum(
        1 for _ in range(30) if s3(rng.randrange(1 << N), rng.randrange(1 << N), rng.randrange(1 << N), B) != 0)
    # descent degree<=2 check at random v
    bad = 0
    for _ in range(200):
        xR = rng.randrange(1, 1 << N)
        c = descent_coeffs(xR, B)
        v = rng.randrange(NA)
        x1, x2 = xs_of(v)
        if eval_poly_coeffs(c, v) != s3(x1, x2, xR, B):
            bad += 1
    S0["descent_vs_direct_eval_mismatches_of_200"] = bad
    # exhaustive evaluator vs naive
    bad = 0
    for _ in range(40):
        rows = [rng.getrandbits(NCOL) for _ in range(NEQ)]
        s, _ = count_s(rows)
        # s must equal the number of zeros of the value table; check 300 random u
        # plus every claimed solution when s is small
        s2, sols = count_s(rows, want=True)
        for u in [rng.randrange(NA) for _ in range(60)]:
            if (eval_rows_naive(rows, u) == 0) != (u in set(sols)):
                bad += 1
    # small-s systems: planted solution
    for _ in range(20):
        u0 = rng.randrange(NA)
        rows = []
        for k in range(NEQ):
            r = rng.getrandbits(NCOL) & ~1
            val = 0
            for col in range(1, NCOL):
                if (r >> col) & 1 and all((u0 >> i) & 1 for i in MONOS[col]):
                    val ^= 1
            rows.append(r | val)
        s, sols = count_s(rows, want=True)
        if u0 not in sols:
            bad += 1
        for u in sols:
            if eval_rows_naive(rows, u) != 0:
                bad += 1
    S0["exhaustive_vs_naive_mismatches"] = bad
    S0["pass"] = (S0["t^(2^17)==t"] and S0["gcd(t^(2^i)-t,f)==1 for i<=8"] and s3ok == 30
                  and S0["S3_random_triples_nonzero"] == 30 and S0["descent_vs_direct_eval_mismatches_of_200"] == 0
                  and bad == 0)
    R["S0_selftests"] = S0
    print("S0", S0, flush=True)

    # S1 archived S_3 systems and slot table --------------------------------
    iset = json.load(open(WT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/instance-sets.json"))
    sets = iset["sets"]
    xr144 = []
    for sname in ["U62", "S62", "C20"]:
        idxs = [r["idx"] for r in sets[sname]]
        assert idxs == sorted(idxs), sname
        for r in sets[sname]:
            xr144.append((sname, r["idx"], r["archived"]["x_R"], r["key"]))
    S1 = {"slots": len(xr144), "sizes": {k: len(v) for k, v in sets.items()}}
    mism, shamism = [], []
    ES3 = []
    for n, (sname, idx, xR, key) in enumerate(xr144):
        E = E_S3(xR, B)
        ES3.append(E)
        rec = [r for r in sets[sname] if r["idx"] == idx][0]
        if ehex(E) != rec["E_hex"]:
            mism.append(key)
        if esha(rec["E_hex"]) != rec["E_sha256"]:
            shamism.append(key)
    # sha convention on the null sets too
    for sname in ["N-AFF62", "N-F262"]:
        for r in sets[sname]:
            if esha(r["E_hex"]) != r["E_sha256"]:
                shamism.append(r["key"])
    S1["own_E_S3_vs_archived_E_hex_mismatches"] = mism
    S1["E_sha256_convention_mismatches"] = shamism
    # structural facts of E_S3 read against object.parts
    parts_bad = []
    bil = {COL[(i, 9 + j)] for i in range(9) for j in range(9)}
    for n, E in enumerate(ES3):
        for k, r in enumerate(E):
            for col in range(NCOL):
                if (r >> col) & 1 and not (col in bil or 1 <= col <= 18 or col == 0):
                    parts_bad.append((n, k, col))
            if ((r >> 0) & 1) != ((B >> k) & 1):
                parts_bad.append((n, k, "const!=B_k"))
    S1["E_S3_support_outside_bilinear_linear_constant_or_const_ne_B"] = parts_bad[:20]
    S1["pass"] = not mism and not shamism and not parts_bad
    R["S1_archived_construct"] = S1
    print("S1", {k: v for k, v in S1.items()}, flush=True)

    # S2 union support ------------------------------------------------------
    E0 = E_S3(0, B)
    U = list(E0)
    for j in range(17):
        Ej = E_S3(TP[j], B)
        for k in range(NEQ):
            U[k] |= Ej[k] ^ E0[k]
    SL = [(k, c) for k in range(NEQ) for c in range(19) if (U[k] >> c) & 1]
    SLc = [(k, c) for (k, c) in SL if c == 0]
    sup = json.load(open(RUN / "support.json"))
    p1 = json.load(gzip.open(WT / "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/checkpoint/p1-instances.json.gz"))
    arch_sizes = p1["F-NULLF2"]["union_support_size_per_eq"]
    S2 = {
        "own_U_hex_equals_support_json": ehex(U) == sup["U_hex"],
        "own_S_L_equals_support_json": [list(x) for x in SL] == [list(x) for x in sup["S_L"]],
        "S_L_size": len(SL),
        "S_L_const_positions": [k for (k, c) in SLc],
        "own_sizes_equal_archived_p1_union_support_size_per_eq": [bin(u).count("1") for u in U] == arch_sizes,
        "coordinator_reading_true": all(
            U[k] == (sum(1 << c for c in bil) | sum(1 << c for c in range(1, 19)) | ((B >> k) & 1)) for k in range(NEQ)),
        "expected_S_L_size_17x18_plus_popcount_B": 17 * 18 + bin(B).count("1"),
    }
    # NULL-F262 inside U
    S2["NULL_F262_outside_U"] = [r["key"] for r in sets["N-F262"]
                                 if any(int(h, 16) & ~U[k] for k, h in enumerate(r["E_hex"]))]
    S2["pass"] = (S2["own_U_hex_equals_support_json"] and S2["own_S_L_equals_support_json"]
                  and S2["own_sizes_equal_archived_p1_union_support_size_per_eq"] and not S2["NULL_F262_outside_U"])
    R["S2_union_support"] = S2
    print("S2", S2, flush=True)

    # S3 stream replays -----------------------------------------------------
    Upos = np.array([k * NCOL + c for k in range(NEQ) for c in range(NCOL) if (U[k] >> c) & 1], dtype=np.int64)
    QP = [[r & ~((1 << 19) - 1) for r in E] for E in ES3]            # quadratic columns only
    QLP = [[r & ~1 for r in E] for E in ES3]                          # quadratic + linear
    CONV17 = [0] * NEQ
    for i in range(9):
        for j in range(9):
            CONV17[i + j] |= 1 << COL[(i, 9 + j)]
    Bbits_c = [(B >> k) & 1 for (k, c) in SLc]

    def place(base, pos, bits):
        rows = list(base)
        for (k, c), b in zip(pos, bits):
            if b:
                rows[k] |= 1 << c
        return rows

    def replay(arm, seed, nslots):
        g = np.random.Generator(np.random.PCG64(seed))
        kept_h = set()
        att, kept, exh = [], [], []
        for slot in range(nslots):
            nu = ns = True
            for a in range(256):
                info = {}
                rej = None
                if arm == "N-CONV":
                    bits = g.integers(0, 2, size=len(SL))
                    rows = place(QP[slot], SL, bits)
                    if rows == ES3[slot]:
                        rej = "identity"
                elif arm == "N-CONVL":
                    bits = g.integers(0, 2, size=len(SLc))
                    rows = place(QLP[slot], SLc, bits)
                    bp = 0
                    for (k, c), b in zip(SLc, bits):
                        if b:
                            bp |= 1 << k
                    info["bprime"] = bp
                    if list(bits) == Bbits_c:
                        rej = "identity"
                    elif bp == 0:
                        rej = "bprime_zero"
                elif arm == "N-CONV17":
                    bits = g.integers(0, 2, size=len(SL))
                    rows = place(CONV17, SL, bits)
                elif arm == "N-ELL144":
                    M = np.zeros(NEQ * NCOL, dtype=np.int64)
                    M[Upos] = g.integers(0, 2, size=Upos.size)
                    cc = int(g.integers(0, 2))
                    info["c"] = cc
                    M = M.reshape(NEQ, NCOL)
                    rows = [sum(1 << int(j) for j in np.flatnonzero(M[k])) for k in range(NEQ - 1)]
                    rows.append((1 << COL[(0,)]) | (1 << COL[(9,)]) | cc)
                h = esha(rows)
                if rej is None and h in kept_h:
                    rej = "duplicate"
                rec = {"slot": slot, "attempt": a, "E_sha256": h, **info}
                if rej:
                    rec.update(s=None, outcome="rejected:" + rej)
                    att.append(rec)
                    continue
                s, sols = count_s(rows, want=True)
                rec["s"] = s
                if s == 0 and nu:
                    nu = False
                    rec["outcome"] = "kept_unsat"
                    kept_h.add(h)
                    kept.append({"slot": slot, "role": "unsat", "attempt": a, "E_hex": ehex(rows), "E_sha256": h,
                                 "s": 0, **info})
                elif s >= 1 and ns:
                    ns = False
                    rec["outcome"] = "kept_sat"
                    kept_h.add(h)
                    kept.append({"slot": slot, "role": "sat", "attempt": a, "E_hex": ehex(rows), "E_sha256": h,
                                 "s": s, "solutions": sols, **info})
                else:
                    rec["outcome"] = "discarded"
                att.append(rec)
                if not nu and not ns:
                    break
            if nu:
                exh.append((slot, "unsat"))
            if ns:
                exh.append((slot, "sat"))
        return att, kept, exh

    inst = [json.loads(l) for l in gzip.open(RUN / "instances.jsonl.gz", "rt")]
    ikey = {r["key"]: r for r in inst}
    seeds = {"N-CONV": 2026092450101, "N-CONVL": 2026092450102, "N-CONV17": 2026092450103, "N-ELL144": 2026092450104}
    plan = [("N-CONV", 10, "required"), ("N-CONVL", 5, "required")]
    if FULL:
        plan += [("N-CONV", 144, "extension"), ("N-CONVL", 144, "extension"),
                 ("N-CONV17", 144, "extension"), ("N-ELL144", 144, "extension")]
    S3 = []
    for arm, nsl, why in plan:
        ta = time.time()
        att, kept, exh = replay(arm, seeds[arm], nsl)
        logged = [json.loads(l) for l in gzip.open(RUN / f"draws-{arm}.jsonl.gz", "rt")]
        logged_pref = [r for r in logged if r["slot"] < nsl]
        att_cmp = []
        for a, b in zip(att, logged_pref):
            if a != b:
                att_cmp.append({"own": a, "logged": b})
        kept_cmp = []
        for kp in kept:
            key = f"{arm}:{kp['slot']}:{kp['role']}"
            ir = ikey.get(key)
            if ir is None:
                kept_cmp.append({"key": key, "problem": "missing in instances"})
                continue
            diffs = [f for f in ("attempt", "E_hex", "E_sha256", "s") if kp[f] != ir[f]]
            if kp["role"] == "sat" and kp["solutions"] != ir.get("solutions"):
                diffs.append("solutions")
            for f in ("bprime", "c"):
                if f in kp and kp[f] != ir.get(f):
                    diffs.append(f)
            if diffs:
                kept_cmp.append({"key": key, "fields": diffs})
        ent = {"arm": arm, "slots": f"0..{nsl - 1}", "scope": why, "attempts_own": len(att),
               "attempts_logged_in_prefix": len(logged_pref), "attempt_record_mismatches": len(att_cmp),
               "attempt_mismatch_examples": att_cmp[:3], "kept_own": len(kept), "kept_mismatches": kept_cmp[:5],
               "n_kept_mismatches": len(kept_cmp), "exhausted_own": exh,
               "rejections_own": {k: sum(1 for r in att if r["outcome"] == k) for k in
                                  sorted({r["outcome"] for r in att})},
               "sat_before_unsat_slots_own": sorted({kp["slot"] for kp in kept if kp["role"] == "sat"
                                                     and any(k2["slot"] == kp["slot"] and k2["role"] == "unsat"
                                                             and k2["attempt"] > kp["attempt"] for k2 in kept)}),
               "attempts_per_slot_own": [sum(1 for r in att if r["slot"] == s) for s in range(min(nsl, 10))],
               "seconds": round(time.time() - ta, 1)}
        if nsl == 144:
            ent["whole_log_equal"] = (len(att) == len(logged) and not att_cmp)
        ent["pass"] = (not att_cmp and not kept_cmp and len(att) == len(logged_pref))
        S3.append(ent)
        print("S3", {k: v for k, v in ent.items() if k not in ("attempt_mismatch_examples",)}, flush=True)
    R["S3_stream_replays"] = S3

    # S4 full construction sweep -------------------------------------------
    slot_x = {n: (s, i, x) for n, (s, i, x, _) in enumerate(xr144)}
    viol = {}

    def add(kind, key):
        viol.setdefault(kind, []).append(key)
    LOW = (1 << 19) - 1
    SLmask = [0] * NEQ
    for (k, c) in SL:
        SLmask[k] |= 1 << c
    counts = {}
    for r in inst:
        arm = r["arm"]
        counts[arm] = counts.get(arm, 0) + 1
        rows = [int(h, 16) for h in r["E_hex"]]
        if esha(r["E_hex"]) != r["E_sha256"]:
            add("E_sha256_convention", r["key"])
        if len(rows) != 17 or any(x >> 172 for x in rows):
            add("shape", r["key"])
        if arm in ("N-CONV", "N-CONVL"):
            sname, idx, xR = slot_x[r["slot"]]
            if (r["source_set"], r["idx"], r["x_R"]) != (sname, idx, xR):
                add(f"{arm}:slot_to_xR_binding", r["key"])
            E = ES3[r["slot"]]
            if arm == "N-CONV":
                if any((a & ~LOW) != (b & ~LOW) for a, b in zip(rows, E)):
                    add("N-CONV:quadratic_part_ne_S3", r["key"])
                if any((a & LOW) & ~SLmask[k] for k, a in enumerate(rows)):
                    add("N-CONV:drawn_bit_outside_S_L", r["key"])
                if rows == E:
                    add("N-CONV:identity_kept", r["key"])
            else:
                if any((a & ~1) != (b & ~1) for a, b in zip(rows, E)):
                    add("N-CONVL:quadratic_or_linear_ne_S3", r["key"])
                if any((a & 1) and not (SLmask[k] & 1) for k, a in enumerate(rows)):
                    add("N-CONVL:constant_bit_outside_S_L", r["key"])
                bp = sum((a & 1) << k for k, a in enumerate(rows))
                if bp == B:
                    add("N-CONVL:identity_kept", r["key"])
                if bp == 0:
                    add("N-CONVL:bprime_zero_kept", r["key"])
                if bp != r.get("bprime"):
                    add("N-CONVL:bprime_field_mismatch", r["key"])
        elif arm == "N-CONV17":
            if r["x_R"] is not None or r["source_set"] is not None:
                add("N-CONV17:x_R_not_null", r["key"])
            if any((a & ~LOW) != b for a, b in zip(rows, CONV17)):
                add("N-CONV17:quadratic_part_ne_Q", r["key"])
            if any((a & LOW) & ~SLmask[k] for k, a in enumerate(rows)):
                add("N-CONV17:drawn_bit_outside_S_L", r["key"])
        elif arm == "N-ELL144":
            if r["x_R"] is not None:
                add("N-ELL144:x_R_not_null", r["key"])
            if any(a & ~U[k] for k, a in enumerate(rows[:16])):
                add("N-ELL144:row_outside_U", r["key"])
            if rows[16] != ((1 << 1) | (1 << 10) | r.get("c", -99)):
                add("N-ELL144:row16_ne_v0+v9+c", r["key"])
        elif arm in ("S3-U62", "S3-S62", "S3-C20", "NULL-AFF62", "NULL-F262"):
            sname = {"S3-U62": "U62", "S3-S62": "S62", "S3-C20": "C20", "NULL-AFF62": "N-AFF62",
                     "NULL-F262": "N-F262"}[arm]
            rec = [x for x in sets[sname] if x["key"] == r["key"]]
            if len(rec) != 1 or rec[0]["E_hex"] != r["E_hex"] or rec[0]["E_sha256"] != r["E_sha256"]:
                add(f"{arm}:not_the_archived_system", r["key"])
            if arm.startswith("S3-"):
                sn, idx, xR = slot_x[r["slot"]]
                if (sn, idx, xR) != (sname, rec[0]["idx"], rec[0]["archived"]["x_R"]) or r["x_R"] != xR:
                    add(f"{arm}:slot_binding", r["key"])
                if rows != ES3[r["slot"]]:
                    add(f"{arm}:ne_own_E_S3", r["key"])
    nell = json.load(open(WT / "coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/n-ell-instances.json"))
    nel_arch = {"NELL-A20:" + x["label"]: x for x in nell["instances"]}
    for r in inst:
        if r["arm"] == "NELL-A20":
            x = nel_arch.get(r["key"])
            if x is None or x["E_hex"] != r["E_hex"]:
                add("NELL-A20:not_the_archived_system", r["key"])
    # per-arm distinctness of kept systems (duplicate rule)
    for arm in seeds:
        hs = [r["E_sha256"] for r in inst if r["arm"] == arm]
        if len(hs) != len(set(hs)):
            add(f"{arm}:duplicate_kept", arm)
    # role vs s
    for r in inst:
        if (r["role"] == "unsat") != (r["s"] == 0):
            add("role_ne_s", r["key"])
    S4 = {"systems_swept": len(inst), "per_arm": counts,
          "violations": {k: {"count": len(v), "examples": v[:5]} for k, v in viol.items()},
          "pass": not viol}
    R["S4_full_sweep"] = S4
    print("S4", S4, flush=True)
    R["seconds"] = round(time.time() - t0, 1)
    R["pass"] = S0["pass"] and S1["pass"] and S2["pass"] and all(e["pass"] for e in S3) and S4["pass"]
    out = OUTDIR / ("j2-results-full.json" if FULL else "j2-results.json")
    json.dump(R, open(out, "w"), indent=1)
    print("WROTE", out, "pass", R["pass"], "seconds", R["seconds"])


if __name__ == "__main__":
    main()
