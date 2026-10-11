#!/usr/bin/env python3
"""Blind re-derivation (TASK-20261001-1894f8, J3) of the EXP-ICEX-aaccfc v4
stage-2 factor-base pair-output test for fixture index 0.

Written from the protocol text alone (specification.yaml + the three
amendments). No implementation or run artifact of EXP-ICEX-aaccfc was read.
Every reading of an underdetermined rule is enumerated, never chosen silently.
"""
import hashlib
import json
import math
import sys

FIXTURES = "experiments/EXP-SDEG-85eefd/amendments/ic_leads_fixtures_v2.json"
EXPECTED_SHA = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"

raw = open(FIXTURES, "rb").read()
sha = hashlib.sha256(raw).hexdigest()
fx_all = json.loads(raw)
fx = fx_all["EXP-ICEX-aaccfc"][0]
p, a, b, N = fx["p"], fx["a"], fx["b"], fx["N"]
G = tuple(fx["G"])
bits, seed = fx["bits"], fx["seed"]

out = {"fixture_file_sha256": sha, "fixture_sha_matches_C1": sha == EXPECTED_SHA,
       "fixture": fx}


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def legendre(v):
    v %= p
    if v == 0:
        return 0
    return 1 if pow(v, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(v):
    v %= p
    if v == 0:
        return 0
    for y in range(p):  # p ~ 6e4: brute force is fine and transparent
        if y * y % p == v:
            return y
    raise ValueError


def on_curve(P):
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0


def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P):
    return None if P is None else (P[0], (-P[1]) % p)


def mul(k, P):
    R = None
    k %= N
    while k:
        if k & 1:
            R = add(R, P)
        P = add(P, P)
        k >>= 1
    return R


# ---- fixture sanity: curve order by exact point counting ----
count = 1 + sum(1 + legendre(x * x * x + a * x + b) for x in range(p))
disc = (4 * a ** 3 + 27 * b ** 2) % p
out["sanity"] = {
    "p_prime": is_prime(p), "N_prime": is_prime(N),
    "point_count_#E": count, "#E_equals_N": count == N,
    "G_on_curve": on_curve(G), "N_times_G_is_O": mul(N, G) is None and add(mul(N - 1, G), G) is None,
    "nonsingular": disc != 0, "N_gt_sqrt_p": N * N > p,
    "trace": p + 1 - count,
}
assert count == N and is_prime(N), "cofactor != 1; subgroup reading would matter"

# ---- (1) factor base at the frozen B rule (AMD-20260926-ced670 C-2) ----
def iroot_ceil(n, k):
    r = round(n ** (1.0 / k))
    while r ** k < n:
        r += 1
    while r > 1 and (r - 1) ** k >= n:
        r -= 1
    return r

B_p = iroot_ceil(p, 5)        # C-2 literal: B = ceil(p^{1/5})
B_q = iroot_ceil(N, 5)        # review-plan wording "~q^{1/5}"
fb_x = [x for x in range(B_p) if legendre(x * x * x + a * x + b) != -1]
F = []
for x in fb_x:
    y = sqrt_mod(x * x * x + a * x + b)
    F.append((x, y))
    if y != 0:
        F.append((x, (-y) % p))
nonlift = [x for x in range(B_p) if legendre(x * x * x + a * x + b) == -1]
out["factor_base"] = {
    "p_pow_1_5": p ** 0.2, "q_pow_1_5": N ** 0.2,
    "B_ceil_p_1_5": B_p, "B_ceil_q_1_5": B_q, "B_readings_agree": B_p == B_q,
    "x_range": f"0 <= x < {B_p} (integer representative in [0,p))",
    "liftable_x_classes": fb_x, "L": len(fb_x),
    "non_liftable_x": nonlift,
    "two_torsion_in_F": [P for P in F if P[1] == 0],
    "F_points": F, "F_size_points": len(F),
}
Fset = set(F)
F_xset = set(fb_x)


def stage2(S):
    """Scan P1 over F (points, both signs), test x(S - P1) < B.

    Returns (tests_full_scan, pair_hits, tests_until_first_hit_or_full)."""
    hits = 0
    first = None
    for i, P1 in enumerate(F):
        D = add(S, neg(P1))
        hit = D is not None and D[0] < B_p
        if hit:
            hits += 1
            if first is None:
                first = i + 1
    return len(F), hits, (first if first is not None else len(F))


# ---- reading-independent population statistic over every point of E ----
def all_points():
    yield None
    for x in range(p):
        r = (x * x * x + a * x + b) % p
        l = legendre(r)
        if l == -1:
            continue
        y = sqrt_mod(r) if l == 1 else 0
        yield (x, y)
        if y:
            yield (x, (-y) % p)

# membership of S in F+F computed by enumerating sums (exact, cheap: |F|^2)
sumset = {}
for P1 in F:
    for P2 in F:
        S = add(P1, P2)
        sumset.setdefault(S, 0)
        sumset[S] += 1
# number of P1 in F with S-P1 in F, for a given S == ordered representation count
pop_any = sum(1 for S in sumset if S is not None)
pop_pairs_total = sum(c for S, c in sumset.items() if S is not None)
out["population_over_all_N_points"] = {
    "note": "Reading-independent: exact over every S != O in E(F_p) (#E = N prime).",
    "distinct_S_in_F_plus_F_excl_O": pop_any,
    "frac_S_with_any_hit": pop_any / (N - 1),
    "ordered_pair_hits_total": pop_pairs_total,
    "expected_pair_hits_per_S": pop_pairs_total / (N - 1),
    "expected_per_test_hit_rate": pop_pairs_total / ((N - 1) * len(F)),
    "O_representations": sumset.get(None, 0),
}


# ---- held-out point readings ----
def h_int(label):
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest(), "big")


def scalar(prefix_label, mode, lo=1):
    """Draw a scalar in [lo, N) from a label under a named mapping."""
    nb = N.bit_length()
    if mode == "mod_N":
        return h_int(prefix_label) % N
    if mode == "mod_Nm1_plus1":
        return 1 + h_int(prefix_label) % (N - 1)
    c = 0
    while True:
        lab = prefix_label if c == 0 and mode.endswith("_c0bare") else f"{prefix_label}|{c}"
        v = h_int(lab)
        v = v >> (256 - nb) if mode.startswith("rej_top") else v & ((1 << nb) - 1)
        if lo <= v < N:
            return v
        c += 1


def summarize(points):
    n = len(points)
    any_hit = pair_hits = tests = early = 0
    s_is_O = 0
    for S in points:
        if S is None:
            s_is_O += 1
            t, h, e = len(F), 0, len(F)
        else:
            t, h, e = stage2(S)
        tests += t
        pair_hits += h
        early += e
        any_hit += h > 0
    return {
        "n_points": n, "S_equal_O": s_is_O,
        "points_with_any_hit": any_hit, "frac_points_with_any_hit": any_hit / n,
        "pair_hits_total": pair_hits, "tests_total_full_scan": tests,
        "per_test_hit_fraction": pair_hits / tests,
        "mean_pair_hits_per_point": pair_hits / n,
        "mean_tests_per_point_full_scan": tests / n,
        "mean_tests_per_point_early_stop": early / n,
    }


readings = {}
prefixes = {"v2": "EXP-ICEX-aaccfc/v2", "v1": "EXP-ICEX-aaccfc/v1"}
argforms = {
    "bits|seed|i": lambda i: f"{bits}|{seed}|{i}",
    "bits|seed|i (i from 1)": lambda i: f"{bits}|{seed}|{i + 1}",
}
modes = ["mod_N", "mod_Nm1_plus1", "rej_top", "rej_low", "rej_top_c0bare", "rej_low_c0bare"]
for pk, pre in prefixes.items():
    for ak, af in argforms.items():
        for mode in modes:
            pts = [mul(scalar(f"{pre}|heldout|{af(i)}", mode), G) for i in range(256)]
            readings[f"S=h*G|{pk}|{ak}|{mode}"] = summarize(pts)
        # random-x reading: x from hash (rejection to [0,p)), lift, y-sign from a bit
        pts = []
        for i in range(256):
            c = 0
            while True:
                v = h_int(f"{pre}|heldout|{af(i)}|{c}")
                x = (v >> (256 - p.bit_length()))
                r = (x * x * x + a * x + b) % p
                if x < p and legendre(r) != -1:
                    y = sqrt_mod(r)
                    if (v & 1) and y:
                        y = (-y) % p
                    pts.append((x, y))
                    break
                c += 1
        readings[f"S=random_x_lift|{pk}|{ak}"] = summarize(pts)
out["held_out_readings"] = readings

anyfr = [r["frac_points_with_any_hit"] for r in readings.values()]
ptf = [r["per_test_hit_fraction"] for r in readings.values()]
out["spread_across_readings"] = {
    "n_readings": len(readings),
    "frac_points_with_any_hit_min_max": [min(anyfr), max(anyfr)],
    "points_with_any_hit_min_max": [min(r["points_with_any_hit"] for r in readings.values()),
                                    max(r["points_with_any_hit"] for r in readings.values())],
    "per_test_hit_fraction_min_max": [min(ptf), max(ptf)],
    "pair_hits_total_min_max": [min(r["pair_hits_total"] for r in readings.values()),
                                max(r["pair_hits_total"] for r in readings.values())],
}
json.dump(out, sys.stdout, indent=1, default=str)
print()
