#!/usr/bin/env python3
"""Shared, stdlib-only helpers for TASK-20260824-261bb4 / EXP-ECQ-f5af06.

EVERY DECISION IN THIS FILE IS EXACT INTEGER OR Fraction ARITHMETIC.
Floating point appears in exactly two places, both of which are REPORTING or
TRIAGE quantities that decide no certification:
  * naive_height_log() / log_abs()  -- reported logarithms of exact integers
  * mestre_nagao_score()            -- the part-C triage score
Both are labelled at their definition.  See CTL-NO-FLOATING-POINT-IN-A-DECISION.

The exact certifier itself is REUSED BYTE-IDENTICAL from
coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/tasks/TASK-20260823-827765/
scripts/exact_certify.py -- imported, never copied, never edited.
"""
import json
import math
import os
import sys
from fractions import Fraction as F
from math import gcd, isqrt

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", ".."))
CERTIFIER_PATH = os.path.join(
    REPO, "coordination/goals/GOAL-ECQ-002/batches/BATCH-8b08ef/"
          "tasks/TASK-20260823-827765/scripts/exact_certify.py")
sys.path.insert(0, os.path.dirname(CERTIFIER_PATH))
import exact_certify as EC  # noqa: E402  (reused instrument, byte-identical)

INPUT_PATH = os.path.join(REPO, "coordination/goals/GOAL-ECQ-2298dc/inputs/ICARM-302.json")
SNAPSHOT_PATH = os.path.join(REPO, "coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json")

# --------------------------------------------------------------------------
# FROZEN CONTRACT CONSTANTS.  Reproduced verbatim from
# experiments/EXP-ECQ-f5af06/specification.yaml.  NOT the executor's to choose.
# --------------------------------------------------------------------------
FROZEN = {
    "part_b_box": {
        "description": ("x = u / w^2 in lowest terms, w an integer in [1, 30], "
                        "gcd(u, w) = 1, |u| <= U(w) where U(1) = 1000000 and "
                        "U(w) = 10000 for 2 <= w <= 30"),
        "w_min": 1, "w_max": 30, "U_w1": 1000000, "U_w_other": 10000,
    },
    "part_c_reduced_box": {
        "description": ("x = u / w^2 with w in [1, 10], gcd(u, w) = 1, "
                        "|u| <= 100000 for w = 1 and |u| <= 2000 for 2 <= w <= 10"),
        "w_min": 1, "w_max": 10, "U_w1": 100000, "U_w_other": 2000,
    },
    "part_c_twist_set": {
        "description": ("every squarefree integer D in [-200, -2], every squarefree "
                        "integer D in [2, 200], and D = -1; D = 1 excluded"),
    },
    "part_c_null_set": {
        "description": ("a6 -> a6 + v for v in {-100, ..., -1, 1, ..., 100}, "
                        "discarding any with zero discriminant and recording the discard"),
    },
    "part_c_triage": {
        "score": "S = sum over primes p <= 500 of (a_p * log p) / p",
        "prime_bound": 500,
        "gate": ("exactly the top 20 candidates by S in each arm and no others; "
                 "ties broken by smallest |D| (respectively smallest |v|), then "
                 "positive sign before negative"),
        "gate_size": 20,
    },
    "seed": 20260824,
}

CITED = {"naive_height": 468.2771, "log_abs_disc": 453.0469}


# --------------------------------------------------------------------------
# exact model arithmetic (delegating to the reused certifier where it defines it)
# --------------------------------------------------------------------------
def b_invariants(ai):
    return EC.b_invariants(ai)


def c_invariants(ai):
    return EC.c_invariants(ai)


def discriminant(ai):
    return EC.discriminant(ai)


def log_abs(n):
    """FLOATING POINT, REPORTING ONLY.  log|n| of an exact integer n.

    Decides nothing.  Computed via the exact bit length so that integers far
    beyond float range are handled without overflow.
    """
    n = abs(int(n))
    if n == 0:
        return float("-inf")
    b = n.bit_length()
    if b <= 900:
        return math.log(n)
    shift = b - 900
    return math.log(n >> shift) + shift * math.log(2)


def naive_height_log(ai):
    """FLOATING POINT, REPORTING ONLY.  log max(|c4|^3, |c6|^2).  Decides nothing."""
    c4, c6 = c_invariants(ai)
    return max(3 * log_abs(c4), 2 * log_abs(c6))


def exact_invariants(ai):
    """All exact integer invariants of a model, plus reported logarithms."""
    ai = [int(a) for a in ai]
    b2, b4, b6, b8 = b_invariants(ai)
    c4, c6 = c_invariants(ai)
    disc = discriminant(ai)
    return {
        "a_invariants": [str(a) for a in ai],
        "b_invariants": [str(b2), str(b4), str(b6), str(b8)],
        "c4": str(c4), "c6": str(c6), "discriminant": str(disc),
        "curve_key": "%s:%s" % (c4, c6),
        "naive_height_log_REPORTING_FLOAT": None if disc == 0 else round(naive_height_log(ai), 6),
        "log_abs_disc_REPORTING_FLOAT": None if disc == 0 else round(log_abs(disc), 6),
    }


def to_standard_model(ai):
    """[a1,a2,a3,a4,a6] -> the standard integral model [0, b2, 0, 8*b4, 16*b6].

    This is the substitution (x, y) -> (X/4, Y/8) after completing the square;
    the resulting curve is Q-isomorphic to the input, so its Mordell-Weil rank
    and its a_p at good primes are unchanged.  APPLIED IDENTICALLY TO BOTH ARMS
    OF PART C so that the twist arm and the null arm are scored on the same
    model shape by the same code path (CTL-MATCHED-NULL).
    """
    b2, b4, b6, b8 = b_invariants([int(a) for a in ai])
    return [0, b2, 0, 8 * b4, 16 * b6]


def quadratic_twist_standard(ai_std, D):
    """Quadratic twist by D of a model [0, a2, 0, a4, a6] -> [0, a2 D, 0, a4 D^2, a6 D^3]."""
    a1, a2, a3, a4, a6 = ai_std
    assert a1 == 0 and a3 == 0, "twist helper requires a1 = a3 = 0"
    return [0, a2 * D, 0, a4 * D * D, a6 * D * D * D]


# --------------------------------------------------------------------------
# EXACT point search in a frozen box.  NO FLOATING POINT.
# --------------------------------------------------------------------------
def box_denominator(box):
    """Exact count of admissible (u, w) pairs in a frozen box description.

    MUST BE CALLED AND RECORDED BEFORE ANY CANDIDATE IS TESTED.
    """
    total = 0
    per_w = {}
    for w in range(box["w_min"], box["w_max"] + 1):
        U = box["U_w1"] if w == 1 else box["U_w_other"]
        if w == 1:
            c = 2 * U + 1                      # every u, including u = 0
        else:
            c = 2 * sum(1 for u in range(1, U + 1) if gcd(u, w) == 1)
        per_w[w] = c
        total += c
    return total, per_w


def enumerate_box(box):
    """Deterministic enumeration order of the frozen box: w ascending, then
    |u| ascending with the positive sign before the negative.  Recorded so a
    time-truncated run's numerator is reproducible."""
    for w in range(box["w_min"], box["w_max"] + 1):
        U = box["U_w1"] if w == 1 else box["U_w_other"]
        if w == 1:
            yield (0, 1)
        for a in range(1, U + 1):
            if gcd(a, w) != 1:
                continue
            yield (a, w)
            yield (-a, w)


def square_test_T(ai, u, w):
    """EXACT.  Return T = w^6 * D(x) at x = u/w^2, an integer.

    A rational point with this x exists iff D(x) is a rational square, and since
    w^6 = (w^3)^2 is a perfect square, iff T is a perfect square integer.
        D(x) = (a1 x + a3)^2 + 4 (x^3 + a2 x^2 + a4 x + a6)
        T    = w^2 (a1 u + a3 w^2)^2 + 4 (u^3 + a2 u^2 w^2 + a4 u w^4 + a6 w^6)
    """
    a1, a2, a3, a4, a6 = ai
    w2 = w * w
    w4 = w2 * w2
    w6 = w4 * w2
    t = a1 * u + a3 * w2
    return w2 * t * t + 4 * (u * u * u + a2 * u * u * w2 + a4 * u * w4 + a6 * w6)


def search_box(ai, box, deadline, progress_every=200000, log=None):
    """Search the frozen box for rational points.  EXACT INTEGER ARITHMETIC ONLY.

    Returns (hits, n_tested, exhausted, wall_seconds).  `hits` are exact
    [x_str, y_str] pairs on the SAME model `ai` that was passed in.
    """
    import time
    ai = [int(a) for a in ai]
    a1, a2, a3, a4, a6 = ai
    t0 = time.time()
    hits = []
    n = 0
    exhausted = True
    seen = set()
    for (u, w) in enumerate_box(box):
        n += 1
        if n % progress_every == 0:
            if time.time() > deadline:
                exhausted = False
                break
            if log:
                log("  tested %d candidates, %d hits, %.1fs" % (n, len(hits), time.time() - t0))
        T = square_test_T(ai, u, w)
        if T < 0:
            continue
        s = isqrt(T)
        if s * s != T:
            continue
        # exact rational y from y = (-(a1 x + a3) +- sqrt(D)) / 2, sqrt(D) = s / w^3
        x = F(u, w * w)
        for sign in (1, -1):
            y = (-(a1 * x + a3) + sign * F(s, w ** 3)) / 2
            if EC.on_curve(EC.Qfield(), [F(a) for a in ai], (x, y)):
                key = (str(x), str(y))
                if key not in seen:
                    seen.add(key)
                    hits.append([str(x), str(y)])
            if s == 0:
                break
    return hits, n, exhausted, time.time() - t0


# --------------------------------------------------------------------------
# a_p and the part-C triage score
# --------------------------------------------------------------------------
_QR_CACHE = {}


def _qr_table(p):
    t = _QR_CACHE.get(p)
    if t is None:
        t = bytearray(p)
        for i in range(1, (p // 2) + 1):
            t[(i * i) % p] = 1
        _QR_CACHE[p] = t
    return t


def count_points_fast(ai, p):
    """#E(F_p) on the GIVEN model, counted naively and exactly.

    Identical convention for every curve in both arms and for good and bad p
    alike: the number of affine solutions of the Weierstrass equation over F_p
    plus one point at infinity.  For p of good reduction this is the usual
    #E(F_p); for p of bad reduction it is the point count of the singular
    model, which is a well-defined uniform convention rather than a claim.
    """
    a1, a2, a3, a4, a6 = [a % p for a in ai]
    if p == 2:
        n = 1
        for x in range(2):
            for y in range(2):
                if (y * y + a1 * x * y + a3 * y - (x ** 3 + a2 * x * x + a4 * x + a6)) % 2 == 0:
                    n += 1
        return n
    qr = _qr_table(p)
    n = 1
    for x in range(p):
        f = (x * x * x + a2 * x * x + a4 * x + a6) % p
        b = (a1 * x + a3) % p
        D = (b * b + 4 * f) % p
        if D == 0:
            n += 1
        elif qr[D]:
            n += 2
    return n


_LOGP = {}


def mestre_nagao_score(ai, prime_bound=500):
    """FLOATING POINT, TRIAGE ONLY.  S = sum_{p <= B} a_p log p / p.

    CERTIFIES NOTHING.  Used only to select which candidates receive the exact
    gate.  a_p = p + 1 - #E(F_p) with #E(F_p) from count_points_fast above, the
    same implementation, prime bound and conventions in BOTH arms of part C.
    """
    ai = [int(a) for a in ai]
    S = 0.0
    aps = {}
    for p in EC.primes_upto(prime_bound):
        Np = count_points_fast(ai, p)
        ap = p + 1 - Np
        aps[p] = ap
        lp = _LOGP.get(p)
        if lp is None:
            lp = _LOGP[p] = math.log(p)
        S += ap * lp / p
    return S, aps


def squarefree(n):
    """EXACT.  Is |n| squarefree?"""
    n = abs(int(n))
    if n == 0:
        return False
    d = 2
    while d * d <= n:
        if n % (d * d) == 0:
            return False
        while n % d == 0:
            n //= d
        d += 1
    return True


# --------------------------------------------------------------------------
# provenance (CTL-PROVENANCE)
# --------------------------------------------------------------------------
_SNAP = None


def snapshot():
    global _SNAP
    if _SNAP is None:
        _SNAP = json.load(open(SNAPSHOT_PATH))
    return _SNAP


def provenance_check(ai, label):
    """Check a reported curve against the FROZEN board snapshot by curve_key AND
    by a-invariants.  Cremona's tables are recorded as not-applicable-with-reason
    rather than as a pass: they cover conductors far below anything here."""
    snap = snapshot()
    inv = exact_invariants(ai)
    key = inv["curve_key"]
    by_key = [c["id"] for c in snap["curves"] if c.get("curve_key") == key]
    ai_s = [str(int(a)) for a in ai]
    by_ainvs = [c["id"] for c in snap["curves"]
                if [str(int(a)) for a in c.get("ainvs", [])] == ai_s]
    return {
        "label": label,
        "curve_key": key,
        "frozen_snapshot": "coordination/goals/GOAL-ECQ-002/baseline/"
                           "icarm_database_20260823.json",
        "frozen_snapshot_sha256": "118db069fcfc0cddc61bb00a235736202f01dc72d608b3c743bd342935cadc59",
        "match_by_curve_key": by_key,
        "match_by_ainvs": by_ainvs,
        "in_frozen_snapshot": bool(by_key or by_ainvs),
        "cremona_check": "not_applicable_with_reason",
        "cremona_reason": ("Cremona's tables cover conductors far below the "
                           "~10^450 discriminant scale of this curve and its "
                           "twists, so a Cremona lookup is VACUOUS here and is "
                           "recorded as not-applicable rather than as a pass"),
    }


def load_input():
    d = json.load(open(INPUT_PATH))
    return d


PROVENANCE_CAVEAT = (
    "The a-invariants, the 31 witness points, the rank-31 claim, the naive "
    "height, the submitter and the date for ICARM no. 302 were retrieved on "
    "2026-08-24 from https://elliptic-rank.icarm.cloud/curve/302 THROUGH A "
    "SUMMARISING FETCH TOOL, NOT BY DIRECT PAGE-SOURCE INSPECTION. The board "
    "comment string 'BSD + GRH certified to rank 31, found by Claude, Levent "
    "Alpoge, and Ava Howell' is UNVERIFIED AT SOURCE. Every figure in this "
    "artifact that depends on that fetch carries this caveat. The a-invariants "
    "and the points are NOT trusted as published: they are re-derived through "
    "the certifier's exact on-curve check and exact recomputation of c4, c6 "
    "and the discriminant (CTL-CITED-INPUT-AGREEMENT)."
)
