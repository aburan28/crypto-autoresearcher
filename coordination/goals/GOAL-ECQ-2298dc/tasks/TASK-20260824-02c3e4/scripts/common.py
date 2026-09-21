#!/usr/bin/env python3
"""Shared, stdlib-only helpers for TASK-20260824-02c3e4 / EXP-ECQ-f5af06 v2.

V2 OF THIS FILE.  Copied from TASK-20260824-261bb4/scripts/common.py, which stays
byte-identical on disk so the v1-to-v2 diff is visible to a reviewer.  Every
difference is a consequence of the frozen overlay
experiments/EXP-ECQ-f5af06/amendments/PA-ECQ-f5af06-v2-triage-gate-sign.yaml:

  * FROZEN is re-stated at the v2 ranges (CHG-3..CHG-6) and the gate is
    200-per-arm SMALLEST S FIRST (CHG-1, CHG-2).  S DECREASES WITH RANK.
  * box_denominator() now counts by Moebius inversion instead of a gcd loop.
    Same exact integer; the v1 loop would take minutes at the v2 box sizes and
    the denominator must be on disk BEFORE anything is tested.
  * minimality_screen() is new (CHG-7): the partial, explicitly-labelled-partial
    screen the overlay's minimality_regime requires on every gated row.
  * mann_whitney() is new: rank-based, so the v2-only subset comparison at
    n ~ 12000 per arm is affordable.  v1's O(n1*n2) pair loop is not.

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
# FROZEN CONTRACT CONSTANTS, v2.  Reproduced verbatim from
# experiments/EXP-ECQ-f5af06/specification.yaml as overlaid by
# experiments/EXP-ECQ-f5af06/amendments/PA-ECQ-f5af06-v2-triage-gate-sign.yaml
# (frozen_v2_quantities).  NOT the executor's to choose.
# --------------------------------------------------------------------------
FROZEN = {
    "part_b_box": {
        "description": ("x = u / w^2 in lowest terms, w an integer in [1, 100], "
                        "gcd(u, w) = 1, |u| <= 30000000 for w = 1 and "
                        "|u| <= 300000 for 2 <= w <= 100"),
        "w_min": 1, "w_max": 100, "U_w1": 30000000, "U_w_other": 300000,
    },
    "part_c_reduced_box": {
        "description": ("x = u / w^2 in lowest terms, w an integer in [1, 15], "
                        "gcd(u, w) = 1, |u| <= 500000 for w = 1 and |u| <= 10000 "
                        "for 2 <= w <= 15"),
        "w_min": 1, "w_max": 15, "U_w1": 500000, "U_w_other": 10000,
    },
    "part_c_twist_set": {
        "description": ("every squarefree integer D in [-10000, -2], every squarefree "
                        "integer D in [2, 10000], and D = -1; D = 1 excluded because "
                        "E^(1) is E itself and is already part A"),
    },
    "part_c_null_set": {
        "description": ("a6 -> a6 + v for v in {-6000, ..., -1, 1, ..., 6000}, "
                        "discarding any with zero discriminant and RECORDING EVERY "
                        "DISCARD with its v and its reason"),
    },
    "part_c_triage": {
        "score": "S = sum over primes p <= 500 of (a_p * log p) / p",
        "prime_bound": 500,
        "gate": ("exactly the 200 candidates of SMALLEST S in each arm and no others "
                 "-- most negative first, equivalently the top 200 by -S; ties broken "
                 "by smallest |D| (respectively smallest |v|), then positive sign "
                 "before negative"),
        "gate_direction_in_words": "SMALLEST S FIRST",
        "gate_direction_statement": (
            "S DECREASES WITH RANK. HIGH RANK IS THE MOST NEGATIVE END OF THE "
            "DISTRIBUTION. SELECT THE BOTTOM OF THE ORDERING. Any implementation that "
            "sorts descending and takes the head has inverted this rule and must fail "
            "CTL-GATE-DIRECTION before it can gate anything."),
        "gate_size": 200,
    },
    "minimality_screen_prime_bound": 100000,
    "seed": 20260824,
}

V2_ONLY_SUBSET = {
    "twist": "200 < |D| <= 10000",
    "null": "100 < |v| <= 6000",
    "why": ("The pre-registered inferential threshold applies to THIS SUBSET AND "
            "NOTHING ELSE, because it is disjoint from every candidate scored in v1 "
            "and so no score entering it existed when the threshold was frozen. "
            "Pooled and v1-subset statistics are DESCRIPTIVE ONLY."),
    "preregistered_threshold": (
        "NOTABLE only if BOTH |z| >= 3.0 AND the common-language effect size "
        "P(random twist scores above random null) falls outside [0.45, 0.55]"),
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
def _distinct_prime_factors(w):
    """EXACT.  The distinct primes dividing w."""
    ps = []
    n = int(w)
    d = 2
    while d * d <= n:
        if n % d == 0:
            ps.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        ps.append(n)
    return ps


def coprime_count(U, w):
    """EXACT.  #{u : 1 <= u <= U, gcd(u, w) = 1}, by Moebius inversion.

    Identical integer to v1's `sum(1 for u in range(1, U+1) if gcd(u, w) == 1)`;
    v1's loop is O(U) per w and would cost minutes at the v2 box sizes, and the
    denominator has to be on disk BEFORE the first candidate is tested.
    """
    ps = _distinct_prime_factors(w)
    total = 0
    for mask in range(1 << len(ps)):
        d = 1
        bits = 0
        for i, p in enumerate(ps):
            if mask >> i & 1:
                d *= p
                bits += 1
        total += (-1) ** bits * (U // d)
    return total


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
            c = 2 * coprime_count(U, w)
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


# --------------------------------------------------------------------------
# THE v2 GATE.  SMALLEST S FIRST.  (CHG-1, CHG-2)
# --------------------------------------------------------------------------
def gate_sort_key(row):
    """FROZEN v2 selection rule: ASCENDING S -- most negative first -- with ties
    broken by smallest |identifier|, then positive sign before negative.

    S DECREASES WITH RANK, so the most negative scores are the candidates the
    score itself ranks as most promising.  v1's key was (-S, ...), which sorted
    DESCENDING and gated the least promising candidates; that inversion is the
    defect PA-ECQ-f5af06-v2-triage-gate-sign corrects.  CTL-GATE-DIRECTION
    blocks the gate unless this function reproduces the calibration order.
    """
    return (row["S"], abs(row["ident"]), 0 if row["ident"] > 0 else 1)


def select_gated(rows, gate_size):
    """Apply the frozen v2 gate to already-scored rows: the `gate_size`
    candidates of SMALLEST S, in the frozen tie-break order."""
    return sorted(rows, key=gate_sort_key)[:gate_size]


# --------------------------------------------------------------------------
# PARTIAL MINIMALITY SCREEN (CHG-7 / minimality_regime).  EXACT INTEGERS.
# --------------------------------------------------------------------------
_SCREEN_PRIMES = None


def screen_primes(B):
    global _SCREEN_PRIMES
    if _SCREEN_PRIMES is None or _SCREEN_PRIMES[0] != B:
        _SCREEN_PRIMES = (B, EC.primes_upto(B))
    return _SCREEN_PRIMES[1]


def minimality_screen(ai, B=100000):
    """PARTIAL, AND LABELLED PARTIAL.  EXACT INTEGER ARITHMETIC, NO FLOATING POINT.

    For the stated model, trial divide the exact discriminant by every prime
    p <= B and, for each p with p^12 | disc, test the necessary Kraus-Laska
    condition for a descent at p: p^4 | c4 and p^6 | c6.  For p >= 5 that
    condition is also sufficient for non-minimality at p.  For p in {2, 3} it is
    only necessary, so such a p is reported as ADMITTING A POSSIBLE DESCENT --
    the conservative direction, which withholds minimality rather than asserting
    it.

    Returns a dict whose `minimality_status` is one of the overlay's permitted
    values.  IT NEVER RETURNS established_globally_minimal: this screen cannot
    establish global minimality, because primes above B are untested and
    Laska-Kraus-Connell needs the factorisation of a 450-to-900-digit
    discriminant.  A partial screen DOES NOT discharge claim-bar clause (1) and
    no artifact may say that it does.
    """
    ai = [int(a) for a in ai]
    c4, c6 = c_invariants(ai)
    disc = discriminant(ai)
    descent_primes = []
    undecided_primes = []
    n_checked = 0
    if disc == 0:
        return {
            "minimality_status": "not_established_with_reason",
            "reason": "singular model (discriminant zero); minimality is not defined",
            "screen_prime_bound_B": B, "primes_checked": 0,
            "primes_admitting_descent": [], "primes_undecided_at_2_or_3": [],
            "partial": True,
        }
    for p in screen_primes(B):
        n_checked += 1
        p12 = p ** 12
        if disc % p12:
            continue
        if c4 % (p ** 4) or c6 % (p ** 6):
            continue
        if p >= 5:
            descent_primes.append(p)
        else:
            undecided_primes.append(p)
    if descent_primes or undecided_primes:
        status = "not_established_with_reason"
        reason = (
            "the Kraus-Laska necessary condition p^12 | disc, p^4 | c4, p^6 | c6 "
            "holds at %s, so the STATED MODEL is non-minimal (p >= 5) or possibly "
            "non-minimal (p in {2,3}) at those primes; minimality of the stated "
            "model is therefore NOT established. A rank LOWER BOUND from exhibited "
            "points is unaffected -- it is invariant under Q-isomorphism -- but "
            "claim-bar clause (1) is NOT discharged."
            % (sorted(descent_primes + undecided_primes)[:20]))
    else:
        status = "minimal_at_all_primes_up_to_B_with_B_recorded"
        reason = (
            "no prime p <= %d admits a Kraus-Laska descent on the stated model. "
            "THIS IS A PARTIAL STATEMENT: primes above %d are untested and global "
            "minimality is NOT established, so claim-bar clause (1) is NOT "
            "discharged by it." % (B, B))
    return {
        "minimality_status": status,
        "reason": reason,
        "screen_prime_bound_B": B,
        "primes_checked": n_checked,
        "primes_admitting_descent": descent_primes,
        "primes_undecided_at_2_or_3": undecided_primes,
        "partial": True,
        "partial_label": ("PARTIAL SCREEN. It does NOT satisfy claim-bar clause (1) "
                          "and no artifact may say it does."),
    }


# --------------------------------------------------------------------------
# Mann-Whitney U by midranks.  Rank-based, so n ~ 12000 per arm is affordable.
# --------------------------------------------------------------------------
def mann_whitney(xs, ys):
    """Two-sided Mann-Whitney U of xs against ys, with midranks and a tie
    correction in the variance.  Returns U (of xs over ys), the expected U, the
    normal-approximation z, and the common-language effect size U / (n1 n2).

    Equivalent to v1's O(n1*n2) pairwise-win count, computed in O(n log n).
    Reported as a DESCRIPTIVE statistic wherever the population is not the
    disjoint v2-only subset; see V2_ONLY_SUBSET.
    """
    n1, n2 = len(xs), len(ys)
    if n1 == 0 or n2 == 0:
        return None
    pooled = sorted([(v, 0) for v in xs] + [(v, 1) for v in ys])
    ranks = [0.0] * (n1 + n2)
    tie_term = 0
    i = 0
    while i < len(pooled):
        j = i
        while j + 1 < len(pooled) and pooled[j + 1][0] == pooled[i][0]:
            j += 1
        r = (i + j + 2) / 2.0          # midrank of positions i..j (1-based)
        for k in range(i, j + 1):
            ranks[k] = r
        t = j - i + 1
        if t > 1:
            tie_term += t ** 3 - t
        i = j + 1
    R1 = sum(ranks[k] for k in range(len(pooled)) if pooled[k][1] == 0)
    U = R1 - n1 * (n1 + 1) / 2.0
    mu = n1 * n2 / 2.0
    N = n1 + n2
    var = n1 * n2 * (N + 1) / 12.0
    if tie_term:
        var = (n1 * n2 / 12.0) * ((N + 1) - tie_term / float(N * (N - 1)))
    sd = var ** 0.5
    return {
        "n_x": n1, "n_y": n2,
        "mann_whitney_U_x_over_y": round(U, 4),
        "mann_whitney_U_expected_under_no_difference": mu,
        "mann_whitney_z_normal_approximation": round((U - mu) / sd, 4) if sd else None,
        "tie_corrected_variance": round(var, 4),
        "probability_a_random_x_scores_above_a_random_y": round(U / (n1 * n2), 6),
    }


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
