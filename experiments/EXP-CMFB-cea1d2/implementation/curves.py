"""Curve, instance and scan arithmetic for EXP-CMFB-cea1d2.

Everything here is a pure function of (cell, arm, seed): the FAM sieve, the N-A
and N-B draws, the twist selection and the instance-list sha256 that every
trial recomputes and compares with the one recorded by t1-inventory.

Integers only except the angle draw of N-A (a float64 recipe fixed below).
"""

from __future__ import annotations

import hashlib
import json
import math
from math import isqrt

import numpy as np

EXPERIMENT_ID = "EXP-CMFB-cea1d2"
J0 = -96 ** 3
E0_A, E0_B = -152, 722
SEEDS = {
    "na": 7001, "nb": 7002, "ctrl": 7003, "fam_subset": 7004, "random_bases": 7005,
    "bootstrap": 7006, "randomization": 7007, "labels_points": 7008, "brute": 7009,
    "mestre": 7010,
}
FROZEN_SEEDS = list(range(7001, 7011))
CELL_EDGES = {"C16": (2 ** 14, 2 ** 18), "C20": (2 ** 18, 2 ** 22),
              "C24": (2 ** 22, 2 ** 25), "C18": (2 ** 14, 2 ** 22)}
CELL_CODE = {"C16": 16, "C18": 18, "C20": 20, "C24": 24}
ARM_CODE = {"FAM": 1, "N-A": 2, "N-B": 3, "N-B-ctrl": 4}
STREAM_INSTANCE, STREAM_POINTS, STREAM_TIE, STREAM_TRIPLES = 0, 1, 202, 203
T_MAX_SIEVE = 2600
K_RANDOM = 200
QUOTAS = {"fam_cap": 16, "full": 16, "under": 8, "ctrl": 8}  # tests shrink this; the study never does
MAX_DRAWS = 2_000_000  # attempt cap per member: a hang is an infrastructure failure, not a result
S_M2_CAP = 131072
# trial id -> (run id, workers, memory_mb, role); run ids and limits are the spec's trial_plan.
TRIALS = {
    "t1-inventory": ("RUN-CMFB-2373be", 1, 2048, "inventory_and_instances"),
    "t2-gate-instrument": ("RUN-CMFB-5905c0", 4, 4096, "control_gate_instrument"),
    "t3-gate-sensitivity": ("RUN-CMFB-66b0fe", 4, 4096, "control_gate_sensitivity"),
    "t4-measure-c16-c20": ("RUN-CMFB-3dc120", 4, 4096, "measure_small_cells"),
    "t5-measure-c24-fam": ("RUN-CMFB-42a578", 4, 8192, "measure_c24_fam"),
    "t6-measure-c24-na": ("RUN-CMFB-e13f0e", 4, 8192, "measure_c24_na"),
    "t7-measure-c24-nb": ("RUN-CMFB-c71d35", 4, 8192, "measure_c24_nb"),
    "t8-analysis": ("RUN-CMFB-2010d3", 1, 2048, "analysis_and_decision"),
}
MEASURE_TRIALS = ("t4-measure-c16-c20", "t5-measure-c24-fam", "t6-measure-c24-na", "t7-measure-c24-nb")


def select_for_trial(trial_id: str, instances: list[dict]) -> list[dict]:
    """The instances a measurement trial owns (t4: small cells or pooled C18; t5-t7: C24 by arm)."""
    if trial_id == "t4-measure-c16-c20":
        return [i for i in instances if i["cell"] in ("C16", "C18", "C20") and i["arm"] != "N-B-ctrl"]
    arm = {"t5-measure-c24-fam": "FAM", "t6-measure-c24-na": "N-A", "t7-measure-c24-nb": "N-B"}[trial_id]
    return [i for i in instances if i["cell"] == "C24" and i["arm"] == arm]
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


class InstanceError(ValueError):
    """An instance violates a stated invariant (invalidation rule I4)."""


SEED_OFFSET = 0  # development only: tests and dry runs shift every seed so the frozen streams stay unseen


def rng(seed: int, cell: str, arm: str, member: int, stream: int) -> np.random.Generator:
    """numpy Generator(PCG64(SeedSequence([seed, cell_code, arm_code, member, stream])))."""
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(
        [int(seed) + SEED_OFFSET, CELL_CODE[cell], ARM_CODE[arm], int(member), int(stream)])))


# ----------------------------------------------------------------- number theory
def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin (first twelve prime bases, exact below 3.3e24)."""
    if n < 2:
        return False
    for q in SMALL_PRIMES:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in SMALL_PRIMES:
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


def next_prime(n: int) -> int:
    n = max(n, 2)
    while not is_prime(n):
        n += 1
    return n


def legendre(a: int, p: int) -> int:
    r = pow(a % p, (p - 1) // 2, p)
    return 0 if r == 0 else (1 if r == 1 else -1)


def sqrt_mod(n: int, p: int) -> int:
    """The smaller square root of a quadratic residue n modulo odd prime p (Tonelli-Shanks)."""
    n %= p
    if n == 0:
        return 0
    if legendre(n, p) != 1:
        raise ValueError("not a quadratic residue")
    if p % 4 == 3:
        r = pow(n, (p + 1) // 4, p)
    else:
        q, s = p - 1, 0
        while q % 2 == 0:
            q //= 2
            s += 1
        z = 2
        while legendre(z, p) != -1:
            z += 1
        c, t, r, m = pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p), s
        while t != 1:
            i, tt = 0, t
            while tt != 1:
                tt = tt * tt % p
                i += 1
            b = pow(c, 1 << (m - i - 1), p)
            r, c = r * b % p, b * b % p
            t, m = t * c % p, i
    assert r * r % p == n
    return min(r, p - r)


def cell_of(p: int, cells=("C16", "C20", "C24")) -> str | None:
    for c in cells:
        lo, hi = CELL_EDGES[c]
        if lo < p <= hi:
            return c
    return None


# ------------------------------------------------------------------- elliptic curve
def ec_add(P, Q, A: int, p: int):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_neg(P, p: int):
    return None if P is None else (P[0], (-P[1]) % p)


def ec_mul(k: int, P, A: int, p: int):
    if k < 0:
        return ec_mul(-k, ec_neg(P, p), A, p)
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, A, p)
        P = ec_add(P, P, A, p)
        k >>= 1
    return R


def on_curve(P, A: int, B: int, p: int) -> bool:
    return P is None or (P[1] * P[1] - P[0] ** 3 - A * P[0] - B) % p == 0


def f_value(x: int, A: int, B: int, p: int) -> int:
    return (x * x * x + A * x + B) % p


def j_is_target(A: int, B: int, p: int) -> bool:
    """j(E) = -96^3 mod p for a nonsingular y^2 = x^3 + A x + B."""
    disc = (4 * A ** 3 + 27 * B * B) % p
    return disc != 0 and (1728 * 4 * A ** 3 - J0 * (4 * A ** 3 + 27 * B * B)) % p == 0


def nonsingular(A: int, B: int, p: int) -> bool:
    return (4 * A ** 3 + 27 * B * B) % p != 0


def _poly_mulmod(u, v, A, B, p):
    """Product of two polynomials of degree <= 2 modulo x^3 + A x + B (coefficient lists, low first)."""
    prod = [0] * 5
    for i, ui in enumerate(u):
        for j, vj in enumerate(v):
            prod[i + j] = (prod[i + j] + ui * vj) % p
    for k in (4, 3):  # x^3 = -A x - B
        c = prod[k]
        if c:
            prod[k] = 0
            prod[k - 2] = (prod[k - 2] - A * c) % p
            prod[k - 3] = (prod[k - 3] - B * c) % p
    return prod[:3]


def has_root(A: int, B: int, p: int) -> bool:
    """Does x^3 + A x + B have a root in F_p?  gcd(x^p - x, f) by Euclid, no enumeration."""
    result, base, e = [1, 0, 0], [0, 1, 0], p
    while e:
        if e & 1:
            result = _poly_mulmod(result, base, A, B, p)
        base = _poly_mulmod(base, base, A, B, p)
        e >>= 1
    g = [(result[0]) % p, (result[1] - 1) % p, result[2] % p]  # x^p - x mod f
    a = [B % p, A % p, 0, 1]
    b = g[:]

    def trim(v):
        while v and v[-1] % p == 0:
            v.pop()
        return v

    a, b = trim(a), trim(b)
    while b:
        inv = pow(b[-1], -1, p)
        while len(a) >= len(b):
            c = a[-1] * inv % p
            shift = len(a) - len(b)
            for i, bi in enumerate(b):
                a[shift + i] = (a[shift + i] - c * bi) % p
            a = trim(a)
            if not a:
                break
        a, b = b, a
    return len(a) > 1  # gcd of positive degree


def random_points(A: int, B: int, p: int, gen: np.random.Generator, count: int):
    pts = []
    while len(pts) < count:
        x = int(gen.integers(0, p))
        f = f_value(x, A, B, p)
        if f == 0 or legendre(f, p) != 1 or any(x == q[0] for q in pts):
            continue
        y = sqrt_mod(f, p)
        if int(gen.integers(0, 2)):
            y = p - y
        pts.append((x, y))
    return pts


# --------------------------------------------------------------- twist selection
def twist_list(limit: int = 400):
    """L = [1, -1, 2, -2, 3, -3, 5, -5, 6, -6, 7, -7, 10, ...]: 1, -1, then both signs of every squarefree n >= 2
    (the spec prints this list; non-squarefree n never changes the first d with (d/p) = -1)."""
    out = [1, -1]
    for n in range(2, limit + 1):
        if all(n % (q * q) for q in range(2, isqrt(n) + 1)):  # squarefree: 8 = 2 * 2^2 is the class of 2
            out += [n, -n]
    return out


def chart(d: int) -> tuple[int, int]:
    return E0_A * d * d, E0_B * d ** 3


def select_twist(p: int, N: int) -> dict:
    """The spec's rule: smallest liftable x0 on the d = 1 chart, test [N]P0 = O, else the first d in L
    with (d/p) = -1.  Returns d, A, B, twisted."""
    A1, B1 = chart(1)
    x0 = 0
    while True:
        f = f_value(x0, A1, B1, p)
        if f != 0 and legendre(f, p) == 1:
            break
        x0 += 1
        if x0 >= p:
            raise InstanceError("no point on the d = 1 chart")
    P0 = (x0, sqrt_mod(f, p))
    if ec_mul(N, P0, A1, p) is None:
        d = 1
    else:
        d = next(c for c in twist_list() if legendre(c, p) == -1)
    A, B = chart(d)
    return {"d": d, "A": A, "B": B, "twisted": d != 1, "x0": x0}


# ------------------------------------------------------------------ FAM inventory
def fam_sieve(t_max: int = T_MAX_SIEVE) -> list[dict]:
    """All odd t in [3, t_max] with p = 5t^2+19t+19 and N = 5t^2+18t+20 both prime."""
    out = []
    for t in range(3, t_max + 1, 2):
        p, N = 5 * t * t + 19 * t + 19, 5 * t * t + 18 * t + 20
        if is_prime(p) and is_prime(N):
            out.append({"t": t, "v": t + 2, "p": p, "N": N})
    return out


def bateman_horn_cell(lo: int, hi: int, q_max: int = 100000) -> dict:
    """Heuristic H3: expected number of odd t with p(t), N(t) prime and lo < p(t) <= hi.

    C_odd = 4 * prod_{q odd} (1 - omega(q)/q) / (1 - 1/q)^2 (the 4 is the local factor at 2 on
    odd t: both values are odd for every odd t); omega(q) = number of roots of p(t)N(t) mod q,
    by brute force for q < 2000 and by the discriminant (-19) for larger q."""
    sieve = bytearray([1]) * (q_max + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(q_max) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    c = 4.0
    for q in range(3, q_max + 1, 2):
        if not sieve[q]:
            continue
        if q < 2000:
            w = sum(1 for t in range(q) if ((5 * t * t + 19 * t + 19) * (5 * t * t + 18 * t + 20)) % q == 0)
        else:
            w = 4 if legendre(-19, q) == 1 else 0
        c *= (1 - w / q) / (1 - 1 / q) ** 2
    total = 0.0
    for t in range(3, 100000, 2):
        p, N = 5 * t * t + 19 * t + 19, 5 * t * t + 18 * t + 20
        if p > hi:
            break
        if p > lo:
            total += c / (math.log(p) * math.log(N))
    return {"c_odd": c, "expected": total}


# --------------------------------------------------------- N-B order (Shanks-Mestre)
def order_mestre(A: int, B: int, p: int, gen: np.random.Generator, tries: int = 40):
    """Group order by baby-step giant-step over the Hasse interval from one random point.

    Returns the unique multiple of ord(P) in [p+1-2sqrt(p), p+1+2sqrt(p)], or None."""
    s = isqrt(4 * p)
    lo, W = p + 1 - s, 2 * s + 1
    m = isqrt(W) + 1
    for _ in range(tries):
        P = random_points(A, B, p, gen, 1)[0]
        table = {None: 0}
        cur = P
        for j in range(1, m):
            table[cur] = j
            cur = ec_add(cur, P, A, p)
        mP = cur  # m * P
        target = ec_neg(ec_mul(lo, P, A, p), p)  # k P = -lo P
        step = ec_neg(mP, p)
        hits = []
        cur = target
        for i in range(W // m + 2):
            j = table.get(cur)
            if j is not None:
                k = i * m + j
                if k < W:
                    hits.append(lo + k)
            cur = ec_add(cur, step, A, p)
        if len(set(hits)) == 1:
            return hits[0]
    return None


# --------------------------------------------------------------- instance draws
def _log_uniform_prime(gen, lo: int, hi: int) -> int:
    while True:
        u = gen.uniform(math.log2(lo), math.log2(hi))
        p = next_prime(int(2 ** u))
        if lo < p <= hi:
            return p


def draw_nb(cell: str, index: int, used: set, arm: str = "N-B", seed: int | None = None,
            band: tuple[int, int] | None = None) -> dict:
    """One N-B (or N-B-ctrl) member: random prime-order y^2 = x^3 + A x + B, |A|,|B| <= 1000.

    N-B-ctrl uses the lowest bit of the cell band, (lo, 2 lo], and seed 7003."""
    if seed is None:
        seed = SEEDS["nb"] if arm == "N-B" else SEEDS["ctrl"]
    lo, hi = band or CELL_EDGES[cell]
    if arm == "N-B-ctrl":
        hi = 2 * lo if band is None else band[1]
    gen = rng(seed, cell, arm, index, STREAM_INSTANCE)
    pgen = rng(SEEDS["mestre"], cell, arm, index, STREAM_INSTANCE)
    for _attempt in range(MAX_DRAWS):
        p = _log_uniform_prime(gen, lo, hi)
        A, B = int(gen.integers(-1000, 1001)), int(gen.integers(-1000, 1001))
        if not nonsingular(A, B, p) or j_is_target(A, B, p) or (p, A, B) in used:
            continue
        N = order_mestre(A, B, p, pgen)
        if N is None or N == p or not is_prime(N):
            continue
        used.add((p, A, B))
        return {"arm": arm, "stratum": None, "cell": cell, "index": index, "p": p, "N": N,
                "A": A, "B": B, "d": 1, "twisted": False, "t": None, "a": p + 1 - N, "b": None}
    raise InstanceError(f"{arm} draw exhausted {MAX_DRAWS} attempts (band too small?)")


def draw_na(cell: str, index: int, stratum: str, used_p: set, band: tuple[int, int] | None = None,
            seed: int | None = None) -> dict:
    """One N-A member: 4p = a^2 + 19b^2, a, b odd, N = p + 1 - a prime, b != a + 2.

    Recipe: log2 P uniform on the band; phi uniform on (0, pi) (stratum 'u') or uniform on
    [acos(0.25), acos(0.20)] (stratum 'theta'); a = nearest odd integer to 2 sqrt(P) cos(phi); b = nearest
    odd positive integer to 2 sqrt(P/19) sin(phi)."""
    lo, hi = band or CELL_EDGES[cell]
    gen = rng(SEEDS["na"] if seed is None else seed, cell, "N-A", index, STREAM_INSTANCE)
    fam_primes = {5 * t * t + 19 * t + 19 for t in range(3, T_MAX_SIEVE + 100, 2)}
    for _attempt in range(MAX_DRAWS):
        P = 2.0 ** gen.uniform(math.log2(lo), math.log2(hi))
        if stratum == "u":
            phi = gen.uniform(0.0, math.pi)
        else:
            phi = gen.uniform(math.acos(0.25), math.acos(0.20))
        a0, b0 = 2.0 * math.sqrt(P) * math.cos(phi), 2.0 * math.sqrt(P / 19.0) * math.sin(phi)
        a = 2 * int(round((a0 - 1.0) / 2.0)) + 1
        b = max(1, 2 * int(round((b0 - 1.0) / 2.0)) + 1)
        q = a * a + 19 * b * b
        if q % 4 != 0:
            continue
        p = q // 4
        if not lo < p <= hi or p in used_p or p in fam_primes or b == a + 2:
            continue
        if stratum == "theta" and not (a > 0 and 0.20 <= a / (2.0 * math.sqrt(p)) <= 0.25):
            continue
        N = p + 1 - a
        if not (is_prime(p) and is_prime(N)):
            continue
        used_p.add(p)
        ch = select_twist(p, N)
        return {"arm": "N-A", "stratum": stratum, "cell": cell, "index": index, "p": p, "N": N,
                "A": ch["A"], "B": ch["B"], "d": ch["d"], "twisted": ch["twisted"], "t": None,
                "a": a, "b": b}
    raise InstanceError(f"N-A draw exhausted {MAX_DRAWS} attempts (band too small?)")


def fam_instance(cell: str, index: int, m: dict) -> dict:
    ch = select_twist(m["p"], m["N"])
    return {"arm": "FAM", "stratum": None, "cell": cell, "index": index, "p": m["p"], "N": m["N"],
            "A": ch["A"], "B": ch["B"], "d": ch["d"], "twisted": ch["twisted"], "t": m["t"],
            "a": m["t"], "b": m["v"]}


# ----------------------------------------------------------------- the plan
def cell_plan(counts: dict) -> dict:
    """Pooling rule P1 and the powered flags: a deterministic function of the sieve counts only."""
    m16, m20, m24 = counts["C16"], counts["C20"], counts["C24"]
    if m16 < 8 and m20 < 8 and m16 + m20 >= 8:
        return {"branch": "P1_pooled_C18", "cells": ["C18", "C24"],
                "powered": {"C18": True, "C24": m24 >= 8}}
    return {"branch": "P1_not_applied", "cells": ["C16", "C20", "C24"],
            "powered": {"C16": m16 >= 8, "C20": m20 >= 8, "C24": m24 >= 8}}


def t_ranges() -> dict:
    """Odd t with p(t) in each band: first, last and number of candidates (the spec states 86 / 343 / 837)."""
    out = {}
    for cell in ("C16", "C20", "C24"):
        lo, hi = CELL_EDGES[cell]
        ts = [t for t in range(3, 6000, 2) if lo < 5 * t * t + 19 * t + 19 <= hi]
        out[cell] = {"t_first": ts[0], "t_last": ts[-1], "candidates": len(ts)}
    return out


def sieve_counts(fam: list[dict]) -> dict:
    return {c: sum(1 for m in fam if cell_of(m["p"], (c,)) == c) for c in ("C16", "C20", "C24")}


def fam_members_for(fam: list[dict], cell: str) -> list[dict]:
    lo, hi = CELL_EDGES[cell]
    return sorted((m for m in fam if lo < m["p"] <= hi), key=lambda m: m["t"])


def build_instances(fam: list[dict] | None = None, plan: dict | None = None) -> dict:
    """The whole frozen instance list for the study, with its sha256 and the P1 branch."""
    fam = fam_sieve() if fam is None else fam
    counts = sieve_counts(fam)
    plan = plan or cell_plan(counts)
    instances = []
    for cell in plan["cells"]:
        full = plan["powered"][cell]
        members = fam_members_for(fam, cell)
        cap = QUOTAS["fam_cap"]
        if len(members) > cap:
            g = rng(SEEDS["fam_subset"], cell, "FAM", 0, 0)
            keep = sorted(int(i) for i in g.choice(len(members), cap, replace=False))
            members = [members[i] for i in keep]
        for j, m in enumerate(members):
            instances.append(fam_instance(cell, j, m))
        half = (QUOTAS["full"] if full else QUOTAS["under"]) // 2
        used_p: set = set()
        for stratum, offset in (("u", 0), ("theta", half)):
            for k in range(half):
                instances.append(draw_na(cell, offset + k, stratum, used_p))
        used: set = set()
        for k in range(QUOTAS["full"] if full else QUOTAS["under"]):
            instances.append(draw_nb(cell, k, used, "N-B"))
        cused: set = set(used)  # the control curves are disjoint from the N-B curves of the cell
        for k in range(QUOTAS["ctrl"]):
            instances.append(draw_nb(cell, k, cused, "N-B-ctrl"))
    return {"counts": counts, "plan": plan, "instances": instances, "sha256": instance_sha(instances)}


def instance_sha(instances: list[dict]) -> str:
    core = [{k: i[k] for k in ("arm", "stratum", "cell", "index", "p", "N", "A", "B", "d", "t", "a", "b")}
            for i in instances]
    return hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def spread(n: int, k: int) -> list[int]:
    """k indices spread over range(n), deterministic."""
    if n <= k:
        return list(range(n))
    return sorted({round(i * (n - 1) / (k - 1)) for i in range(k)}) if k > 1 else [0]


# ------------------------------------------------------------ instance validity
def verify_instance(inst: dict) -> dict:
    """Curve and twist validity for one instance (invalidation rule I4), with three fresh points."""
    p, N, A, B = inst["p"], inst["N"], inst["A"], inst["B"]
    arm, cell = inst["arm"], inst["cell"]
    gen = rng(SEEDS["labels_points"], cell, arm, inst["index"], STREAM_POINTS)
    pts = random_points(A, B, p, gen, 3)
    lo, hi = CELL_EDGES[cell]
    checks = {
        "p_prime": is_prime(p), "N_prime": is_prime(N),
        "hasse": (N - (p + 1)) ** 2 <= 4 * p,
        "nonsingular": nonsingular(A, B, p),
        "points_on_curve": all(on_curve(P, A, B, p) for P in pts),
        "order_kills_3_points": all(ec_mul(N, P, A, p) is None for P in pts),
        "no_root_of_f": not has_root(A, B, p),
        "in_band": lo < p <= hi,
    }
    if arm == "N-B-ctrl":
        checks["in_band"] = lo < p <= 2 * lo
    if arm in ("FAM", "N-A"):
        a, b = inst["a"], inst["b"]
        checks["j_is_minus_96_cubed"] = j_is_target(A, B, p)
        checks["trace_identity"] = (4 * p == a * a + 19 * b * b and N == p + 1 - a)
        checks["chart_is_twist"] = (A, B) == chart(inst["d"]) and inst["twisted"] == (inst["d"] != 1)
        checks["twist_order_N"] = all(ec_mul(N, P, A, p) is None for P in pts)
        checks["b_not_a_plus_2"] = (b != a + 2) if arm == "N-A" else (b == a + 2)
        if arm == "FAM":
            t = inst["t"]
            checks["family_formulas"] = (t % 2 == 1 and p == 5 * t * t + 19 * t + 19
                                         and N == 5 * t * t + 18 * t + 20 and b == t + 2 and a == t)
    else:
        checks["j_not_minus_96_cubed"] = not j_is_target(A, B, p)
        checks["not_anomalous"] = N != p
    return {"ok": all(checks.values()), "checks": checks}


# ------------------------------------------------------------- base and labelling
def small_x_base(A: int, B: int, p: int, count: int) -> tuple[list, int]:
    """First `count` liftable abscissae x = 0, 1, ... with the smaller y; window W = last x + 1."""
    pts, x = [], 0
    while len(pts) < count:
        if x >= p:
            raise InstanceError("window requires a scan beyond p (I10)")
        f = f_value(x, A, B, p)
        if f != 0 and legendre(f, p) == 1:
            pts.append((x, sqrt_mod(f, p)))
        x += 1
    return pts, x


def bsgs_labels(points: list, A: int, p: int, N: int) -> list[int]:
    """Discrete logs l(Q) = log_g(Q) in Z_N, g = points[0], by BSGS folded by sign."""
    g = points[0]
    m = isqrt(len(points) * N // 2) + 1
    table, cur = {}, g
    for j in range(1, m + 1):
        table[cur[0]] = (j, cur[1])
        cur = ec_add(cur, g, A, p)
    width = 2 * m + 1
    neg_step = ec_neg(ec_mul(width, g, A, p), p)
    labels = []
    for Q in points:
        R, i = Q, 0
        while True:
            if R is None:
                lab = i * width
                break
            hit = table.get(R[0])
            if hit is not None:
                lab = i * width + (hit[0] if R[1] == hit[1] else -hit[0])
                break
            R = ec_add(R, neg_step, A, p)
            i += 1
            if i > N // width + 2:
                raise InstanceError("BSGS giant-step bound exceeded")
        labels.append(lab % N)
    return labels


def verify_labels(points: list, labels: list[int], A: int, p: int, N: int, gen) -> dict:
    """[l(Q)]g = Q for every point; 64 random triples compared with [l_i+l_j+l_k]g."""
    g = points[0]
    points_ok = sum(1 for Q, lab in zip(points, labels) if ec_mul(lab, g, A, p) == Q)
    triples_ok = 0
    for _ in range(64):
        i, j, k = (int(v) for v in gen.integers(0, len(points), size=3))
        S = ec_add(ec_add(points[i], points[j], A, p), points[k], A, p)
        triples_ok += int(S == ec_mul((labels[i] + labels[j] + labels[k]) % N, g, A, p))
    return {"points": len(points), "points_ok": points_ok, "triples": 64, "triples_ok": triples_ok,
            "ok": points_ok == len(points) and triples_ok == 64 and labels[0] == 1}


# ---------------------------------------------------------------- vector scans
def powmod_vec(a: np.ndarray, e: int, p: int) -> np.ndarray:
    result, base = np.ones_like(a), a % p
    while e:
        if e & 1:
            result = result * base % p
        base = base * base % p
        e >>= 1
    return result


def sqrt_vec(n: np.ndarray, p: int) -> np.ndarray:
    """Square roots of nonzero quadratic residues (vectorised Tonelli-Shanks)."""
    n = n % p
    if p % 4 == 3:
        return powmod_vec(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre(z, p) != -1:
        z += 1
    c = np.full(n.shape, pow(z, q, p), dtype=np.int64)
    t, r = powmod_vec(n, q, p), powmod_vec(n, (q + 1) // 2, p)
    m = np.full(n.shape, s, dtype=np.int64)
    while True:
        active = t != 1
        if not active.any():
            return r
        cur, i = t.copy(), np.zeros(n.shape, dtype=np.int64)
        for _ in range(s):
            mask = (cur != 1) & active
            cur = np.where(mask, cur * cur % p, cur)
            i = np.where(mask, i + 1, i)
        b = c.copy()
        reps = np.where(active, m - i - 1, 0)
        for k in range(s):
            b = np.where(reps > k, b * b % p, b)
        r = np.where(active, r * b % p, r)
        c_new = b * b % p
        t = np.where(active, t * c_new % p, t)
        c = np.where(active, c_new, c)
        m = np.where(active, i, m)


def f_vec(x: np.ndarray, A: int, B: int, p: int) -> np.ndarray:
    return (((x * x % p) * x % p) + (A % p) * x % p + (B % p)) % p


def scan_stats(A: int, B: int, p: int, S: int) -> dict:
    """qr_window control on x = 0..S-1: residuosity of f(x), NOT the Legendre symbol of x.

    L = #{x : f(x) a nonzero square} (the filtered stream yields one point per scanned candidate, the
    unfiltered one L/S).  V = {x : Legendre(x) in {0,1}} is the lab-note definition; Vlift = #{x in V :
    f(x) square}.  Every lifted y is verified y^2 = f(x)."""
    x = np.arange(S, dtype=np.int64)
    f = f_vec(x, A, B, p)
    chi = powmod_vec(f, (p - 1) // 2, p)
    square = chi == 1
    zero = int((f == 0).sum())
    chi_x = powmod_vec(x, (p - 1) // 2, p)
    in_v = chi_x != p - 1
    kept = f[square]
    y = sqrt_vec(kept, p)
    lift_ok = bool(np.all(y * y % p == kept))
    return {"S": S, "L": int(square.sum()), "zero": zero, "V": int(in_v.sum()),
            "Vlift": int((in_v & square).sum()), "lifts_verified": int(len(kept)), "lifts_ok": lift_ok}


def full_period_identity(A: int, B: int, p: int, chunk: int = 1 << 21) -> dict:
    """#{x in F_p : f(x) nonzero square} and sum chi(f(x)), via a table of squares (independent of
    the Euler-criterion scan).  Expected L = (N-1)/2, zero = 0, chi_sum = N - p - 1 = -trace."""
    sq = np.zeros(p, dtype=bool)
    for lo in range(1, (p - 1) // 2 + 1, chunk):
        y = np.arange(lo, min(lo + chunk, (p - 1) // 2 + 1), dtype=np.int64)
        sq[y * y % p] = True
    L = Z = 0
    for lo in range(0, p, chunk):
        x = np.arange(lo, min(lo + chunk, p), dtype=np.int64)
        f = f_vec(x, A, B, p)
        L += int(sq[f].sum())
        Z += int((f == 0).sum())
    return {"L": L, "zero": Z, "chi_sum": L - (p - L - Z)}
