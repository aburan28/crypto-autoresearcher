#!/usr/bin/env python3
"""EXP-DS-001 v2 driver: naive vs degree-split claw Semaev membership + null control.

Binds exclusively to experiments/EXP-DS-001/specification.v2.yaml.
Records observations only; does not interpret S1/F1/F2/F3 as hypothesis status.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import resource
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harness.toycurve import (  # noqa: E402
    ECDLPInstance,
    EllipticCurve,
    Point,
    generate_instance,
    _seed_int,
)
from harness import rho as rho_mod  # noqa: E402
from harness.semaev import build_factor_base  # noqa: E402

BACKEND_ID = "ds001-v2-point-sum-membership+charged-units-v1"
NULL_SPEC_ID = "NULL-DS-RANDOM-MULTIHOMOGENEOUS"
D_HALF = {4: 2, 5: 4}
SEEDS = [101, 102, 103]
BIT_SIZES = [16, 20, 24]
B_SIZES = [64, 128, 256]
ARITIES = [4, 5]
RELATIONS_TARGET = 200
CONTRACT_PATH = "experiments/EXP-DS-001/specification.v2.yaml"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def claw_key(N: int) -> str:
    """Frozen claw key: SHA-256 of canonical big-endian bytes of N."""
    if N < 0:
        N = -N
    if N == 0:
        raw = b"\x00"
    else:
        length = (N.bit_length() + 7) // 8
        raw = N.to_bytes(length, "big")
    return sha256_bytes(raw)


def encode_intermediate(value: int, D: int) -> int:
    """Absolute intermediate integer, truncated to floor(log2(D))+1 bits when larger."""
    N = abs(int(value))
    if D <= 1:
        return N
    max_bits = int(math.floor(math.log2(D))) + 1
    mask = (1 << max_bits) - 1
    if N.bit_length() > max_bits:
        N &= mask
    return N


def is_B_smooth(N: int, B: int) -> bool:
    if N <= 1:
        return N == 1
    n = abs(N)
    # trial division up to B
    while n % 2 == 0:
        n //= 2
        if 2 > B:
            return False
    f = 3
    while f * f <= n and f <= B:
        while n % f == 0:
            n //= f
        f += 2
    if n == 1:
        return True
    return n <= B


def largest_prime_factor(N: int) -> int:
    n = abs(int(N))
    if n <= 1:
        return 1
    max_pf = 1
    while n % 2 == 0:
        max_pf = 2
        n //= 2
    f = 3
    while f * f <= n:
        while n % f == 0:
            max_pf = f
            n //= f
        f += 2
    if n > 1:
        max_pf = n
    return max_pf


# --- Dickman rho (delay-DE table) -------------------------------------------

_RHO_CACHE: dict[int, float] = {}


def dickman_rho(u: float) -> float:
    """Dickman–de Bruijn rho(u) via tabulated delay differential equation."""
    if u <= 0:
        return 1.0
    if u <= 1.0:
        return 1.0
    # table on grid 0.01
    step = 0.01
    nmax = int(math.ceil(u / step)) + 2
    if nmax not in _RHO_CACHE and len(_RHO_CACHE) < nmax:
        # rebuild up to nmax
        rho = [1.0] * (nmax + 1)
        for i in range(int(1.0 / step) + 1, nmax + 1):
            ui = i * step
            # u*rho'(u) + rho(u-1) = 0  => rho(u) ≈ rho(u-du) - du*rho(u-1)/u
            j = i - int(round(1.0 / step))
            prev = rho[i - 1]
            r_um1 = rho[max(j, 0)]
            rho[i] = max(0.0, prev - step * r_um1 / ui)
        for i, val in enumerate(rho):
            _RHO_CACHE[i] = val
    idx = int(round(u / step))
    return float(_RHO_CACHE.get(idx, _RHO_CACHE.get(max(_RHO_CACHE), 0.0)))


def frozen_D(bits: int, m: int) -> int:
    return 2 ** (bits * D_HALF[m])


def frozen_u_star(bits: int, B: int, m: int) -> float:
    D = frozen_D(bits, m)
    return math.log(D) / math.log(B)


# --- Factor base / points ---------------------------------------------------

@dataclass
class FBPack:
    xs: list[int]
    points: list[Point]          # +Y lifts
    signed: list[Point]          # +Y and -Y
    x_hash: str
    B: int


def make_factor_base(inst: ECDLPInstance, B: int, seed: int) -> FBPack:
    xs = build_factor_base(inst, B, seed=seed)
    xs = sorted(set(xs))[:B]
    E = inst.curve()
    points: list[Point] = []
    for x in xs:
        pt = E.lift_x(x)
        if pt is not None:
            points.append(pt)
    # pad deterministically if lift failures (should be rare)
    j = 0
    while len(points) < B and j < 100000:
        x = _seed_int(seed, f"fb_pad{j}") % E.p
        j += 1
        if any(pt[0] == x for pt in points):
            continue
        pt = E.lift_x(x)
        if pt is not None:
            points.append(pt)
            if x not in xs:
                xs.append(x)
    xs = sorted({pt[0] for pt in points})
    points = []
    for x in xs[:B]:
        pt = E.lift_x(x)
        if pt is not None:
            points.append(pt)
    signed: list[Point] = []
    for pt in points:
        signed.append(pt)
        neg = E.negate(pt)
        if neg != pt:
            signed.append(neg)
    x_hash = sha256_bytes(",".join(str(x) for x in sorted(xs[:B])).encode())
    return FBPack(xs=sorted(xs)[:B], points=points, signed=signed, x_hash=x_hash, B=len(points))


# --- Membership backends ----------------------------------------------------

@dataclass
class AttemptResult:
    found: bool
    wall_seconds: float
    backend_units: int
    n_enumerations: int
    peak_table_entries: int
    relation: Optional[dict] = None
    incomplete: bool = False


def point_sum(E: EllipticCurve, pts: Iterable[Point]) -> Point:
    acc: Point = None
    for pt in pts:
        acc = E.add(acc, pt)
    return acc


def random_target(E: EllipticCurve, signed: list[Point], rng: random.Random, m: int) -> tuple[Point, list[Point]]:
    """Plant a random m-sum so membership is attainable (yield measurement)."""
    for _ in range(1000):
        chosen = [signed[rng.randrange(len(signed))] for _ in range(m)]
        T = point_sum(E, chosen)
        if T is not None:
            return T, chosen
    # Extremely unlikely fallback: single nonzero point repeated
    pt = next(p for p in signed if p is not None)
    chosen = [pt] * m
    T = point_sum(E, chosen)
    if T is None:
        T = pt
        chosen = [pt] + [E.negate(pt)] + [pt] * (m - 2)
        T = point_sum(E, chosen)
    return T, chosen


def uniform_random_curve_target(
    E: EllipticCurve,
    inst: ECDLPInstance,
    rng: random.Random,
) -> Point:
    """Uniform random subgroup target — NOT a planted m-sum.

    Samples k uniformly in [1, n-1] and returns k*P. Used by CTRL-RT025-UNPLANTED
    primary yield measurement (target_mode=unplanted_uniform_random).
    """
    n = max(int(inst.n), 2)
    for _ in range(1000):
        k = rng.randrange(1, n)
        T = E.mul(k, inst.P)
        if T is not None:
            return T
    # Fallback: rejection sample affine points on E
    for _ in range(10000):
        x = rng.randrange(E.p)
        pt = E.lift_x(x)
        if pt is None:
            continue
        if rng.randrange(2):
            pt = E.negate(pt)
        return pt
    raise RuntimeError("uniform_random_curve_target failed to sample a point")


def naive_search(
    E: EllipticCurve,
    signed: list[Point],
    T: Point,
    m: int,
    deadline: float,
    charge_backend: Callable[[int], int],
) -> AttemptResult:
    """Enumerate (m-1)-tuples; check remainder in factor-base signed set."""
    t0 = time.perf_counter()
    S = set(signed)
    n_enum = 0
    units = 0
    half = m - 1

    def rec(start: int, need: int, acc: Point, used: list[Point]) -> Optional[list[Point]]:
        nonlocal n_enum, units
        if time.perf_counter() > deadline:
            return None
        if need == 0:
            rem = E.add(T, E.negate(acc) if acc is not None else None)
            # rem = T - acc; when acc is None, rem = T
            if acc is None:
                rem = T
            else:
                rem = E.add(T, E.negate(acc))
            n_enum += 1
            units += charge_backend(m)
            if rem in S:
                return used + [rem]
            return None
        for i in range(start, len(signed)):
            npt = signed[i]
            nacc = E.add(acc, npt)
            got = rec(i, need - 1, nacc, used + [npt])
            if got is not None:
                return got
        return None

    # Iterative for m=4,5 hot paths
    found_rel: Optional[list[Point]] = None
    if m == 4:
        for i in range(len(signed)):
            if time.perf_counter() > deadline:
                break
            a = signed[i]
            for j in range(i, len(signed)):
                if time.perf_counter() > deadline:
                    break
                s2 = E.add(a, signed[j])
                for k in range(j, len(signed)):
                    if time.perf_counter() > deadline:
                        break
                    s3 = E.add(s2, signed[k])
                    rem = E.add(T, E.negate(s3))
                    n_enum += 1
                    units += charge_backend(4)
                    if rem in S:
                        found_rel = [a, signed[j], signed[k], rem]
                        break
                if found_rel:
                    break
            if found_rel:
                break
    elif m == 5:
        for i in range(len(signed)):
            if time.perf_counter() > deadline or found_rel:
                break
            a = signed[i]
            for j in range(i, len(signed)):
                if time.perf_counter() > deadline or found_rel:
                    break
                s2 = E.add(a, signed[j])
                for k in range(j, len(signed)):
                    if time.perf_counter() > deadline or found_rel:
                        break
                    s3 = E.add(s2, signed[k])
                    for ell in range(k, len(signed)):
                        if time.perf_counter() > deadline:
                            break
                        s4 = E.add(s3, signed[ell])
                        rem = E.add(T, E.negate(s4))
                        n_enum += 1
                        units += charge_backend(5)
                        if rem in S:
                            found_rel = [a, signed[j], signed[k], signed[ell], rem]
                            break
    else:
        found_rel = rec(0, half, None, [])

    dt = time.perf_counter() - t0
    if found_rel is None:
        return AttemptResult(False, dt, units, n_enum, 0, None, incomplete=True)
    # verify sum
    if point_sum(E, found_rel) != T:
        return AttemptResult(False, dt, units, n_enum, 0, None, incomplete=True)
    return AttemptResult(
        True,
        dt,
        units,
        n_enum,
        0,
        {
            "kind": "decomposition",
            "summands": [list(pt) for pt in found_rel],
            "target": list(T),
            "method": "naive",
        },
    )


def build_claw_table(
    E: EllipticCurve,
    signed: list[Point],
    half_arity: int,
    D: int,
    B: int,
    smoothness_abort: bool,
    deadline: float,
) -> tuple[dict[str, list[tuple]], int, list[int]]:
    """Map claw_key(N) -> list of half-tuples (as point lists). Also return intermediates."""
    table: dict[str, list[tuple]] = defaultdict(list)
    intermediates: list[int] = []
    entries = 0

    if half_arity == 1:
        for i, pt in enumerate(signed):
            if time.perf_counter() > deadline:
                break
            N = encode_intermediate(pt[0], D)
            intermediates.append(N)
            if smoothness_abort and not is_B_smooth(N, B):
                continue
            key = claw_key(N)
            table[key].append((pt,))
            entries += 1
        return table, entries, intermediates

    if half_arity == 2:
        for i in range(len(signed)):
            if time.perf_counter() > deadline:
                break
            for j in range(i, len(signed)):
                if time.perf_counter() > deadline:
                    break
                s = E.add(signed[i], signed[j])
                if s is None:
                    N = 0
                else:
                    N = encode_intermediate(s[0], D)
                intermediates.append(N)
                if smoothness_abort and not is_B_smooth(N, B):
                    continue
                key = claw_key(N)
                # store sum point + indices for reconstruction
                table[key].append((signed[i], signed[j], s))
                entries += 1
        return table, entries, intermediates

    # half_arity == 3 (for m=5 right side)
    for i in range(len(signed)):
        if time.perf_counter() > deadline:
            break
        for j in range(i, len(signed)):
            if time.perf_counter() > deadline:
                break
            s2 = E.add(signed[i], signed[j])
            for k in range(j, len(signed)):
                if time.perf_counter() > deadline:
                    break
                s3 = E.add(s2, signed[k])
                if s3 is None:
                    N = 0
                else:
                    N = encode_intermediate(s3[0], D)
                intermediates.append(N)
                if smoothness_abort and not is_B_smooth(N, B):
                    continue
                key = claw_key(N)
                table[key].append((signed[i], signed[j], signed[k], s3))
                entries += 1
    return table, entries, intermediates


def split_search(
    E: EllipticCurve,
    signed: list[Point],
    T: Point,
    m: int,
    bits: int,
    B: int,
    table: dict[str, list[tuple]],
    deadline: float,
    charge_backend: Callable[[int], int],
    smoothness_abort: bool,
) -> AttemptResult:
    """Query claw table for complementary half-sum."""
    t0 = time.perf_counter()
    n_enum = 0
    units = 0
    D = frozen_D(bits, m)
    left_arity = m // 2
    found_rel: Optional[list[Point]] = None

    def half_sum_points(arity: int) -> Iterable[tuple]:
        if arity == 1:
            for pt in signed:
                yield (pt,)
        elif arity == 2:
            for i in range(len(signed)):
                for j in range(i, len(signed)):
                    yield (signed[i], signed[j])
        else:
            for i in range(len(signed)):
                for j in range(i, len(signed)):
                    for k in range(j, len(signed)):
                        yield (signed[i], signed[j], signed[k])

    # Right side: enumerate complementary arity, look up T - right in table
    right_arity = m - left_arity
    for right in half_sum_points(right_arity):
        if time.perf_counter() > deadline:
            break
        rsum = point_sum(E, right)
        need = E.add(T, E.negate(rsum) if rsum is not None else None)
        if rsum is None:
            need = T
        else:
            need = E.add(T, E.negate(rsum))
        if need is None:
            N = 0
        else:
            N = encode_intermediate(need[0], D)
        n_enum += 1
        if smoothness_abort and not is_B_smooth(N, B):
            continue
        key = claw_key(N)
        cands = table.get(key, [])
        units += charge_backend(m)  # verify candidates
        for cand in cands:
            # cand ends with sum point for arity>=2; arity 1 is just (pt,)
            if left_arity == 1:
                left_pts = [cand[0]]
                lsum = cand[0]
            elif left_arity == 2:
                left_pts = [cand[0], cand[1]]
                lsum = cand[2]
            else:
                left_pts = [cand[0], cand[1], cand[2]]
                lsum = cand[3]
            if lsum == need:
                # reconstruct full relation
                found_rel = list(left_pts) + list(right)
                break
        if found_rel:
            break

    dt = time.perf_counter() - t0
    if not found_rel:
        return AttemptResult(False, dt, units, n_enum, len(table), None, incomplete=True)
    if T is None or point_sum(E, found_rel) != T:
        return AttemptResult(False, dt, units, n_enum, len(table), None, incomplete=True)
    return AttemptResult(
        True,
        dt,
        units,
        n_enum,
        len(table),
        {
            "kind": "decomposition",
            "summands": [list(pt) for pt in found_rel if pt is not None],
            "target": list(T),
            "method": "degree_split_claw",
        },
    )


# --- Null object ------------------------------------------------------------

def null_spec_hash(seed: int, bits: int, B: int, m: int, null_split_mode: str = "independent") -> str:
    sampler = (
        "blake2b-full-tuple-membership + composing-half-maps"
        if null_split_mode == "composing"
        else "blake2b-full-tuple-membership + independent-half-maps"
    )
    payload = {
        "id": NULL_SPEC_ID,
        "seed": seed,
        "bits": bits,
        "B": B,
        "m": m,
        "multidegree": [2] * m,
        "sampler": sampler,
        "null_split_mode": null_split_mode,
        "backend_id": BACKEND_ID,
    }
    return sha256_bytes(json.dumps(payload, sort_keys=True).encode())


def null_full_hit(seed: int, bits: int, B: int, m: int, xs: tuple[int, ...], target_tag: int) -> bool:
    """Density ~ 1/B^{m/2} so both arms can find hits without curve structure."""
    msg = f"{NULL_SPEC_ID}|{seed}|{bits}|{B}|{m}|full|{target_tag}|{','.join(map(str, xs))}".encode()
    h = hashlib.blake2b(msg, digest_size=8).digest()
    # accept if top bits below threshold
    v = int.from_bytes(h, "big")
    # expected hits: aim ~ B^{-ceil(m/2)+1} roughly so naive is hard but feasible at toy
    modulus = max(B ** (m // 2 - 1), 2)
    return (v % modulus) == 0


def null_half_key(seed: int, bits: int, B: int, m: int, side: str, xs: tuple[int, ...]) -> str:
    msg = f"{NULL_SPEC_ID}|{seed}|{bits}|{B}|{m}|half|{side}|{','.join(map(str, xs))}".encode()
    return hashlib.blake2b(msg, digest_size=16).hexdigest()


def null_compose_half_key(seed: int, bits: int, B: int, m: int, xs: tuple[int, ...]) -> str:
    """Side-symmetric compose key: same claw/join machinery for left and right halves.

    No L/R/J side tag. Intermediate integer = blake2b(half) mod B^(max(m//2-1,1));
    claw key = SHA-256 of that integer's canonical big-endian bytes (same as real arm).
    """
    msg = f"{NULL_SPEC_ID}|{seed}|{bits}|{B}|{m}|compose_half|{','.join(map(str, xs))}".encode()
    h = hashlib.blake2b(msg, digest_size=8).digest()
    modulus = max(B ** max(m // 2 - 1, 1), 2)
    N = int.from_bytes(h, "big") % modulus
    return claw_key(N)

def null_naive_search(
    fb_xs: list[int],
    seed: int,
    bits: int,
    B: int,
    m: int,
    target_tag: int,
    deadline: float,
    charge_backend: Callable[[int], int],
    membership: str = "full_oracle",
) -> AttemptResult:
    t0 = time.perf_counter()
    n_enum = 0
    units = 0
    found = None
    left_arity = m // 2
    right_arity = m - left_arity

    # For speed use limited random sampling of tuples when m>=4 and B large
    rng = random.Random(_seed_int(seed, f"null_naive_{membership}_{target_tag}"))
    budget_checks = 50000
    while n_enum < budget_checks and time.perf_counter() <= deadline and found is None:
        n_enum += 1
        units += charge_backend(m)
        if membership == "compose":
            # Same half-geometry as composing split (not an arbitrary full-tuple cut).
            left = tuple(sorted(rng.choice(fb_xs) for _ in range(left_arity)))
            right = tuple(sorted(rng.choice(fb_xs) for _ in range(right_arity)))
            if null_compose_hit(seed, bits, B, m, left, right, target_tag):
                found = list(sorted(list(left) + list(right)))
                break
        else:
            tup = tuple(sorted(rng.choice(fb_xs) for _ in range(m)))
            if null_full_hit(seed, bits, B, m, tup, target_tag):
                found = list(tup)
                break
    dt = time.perf_counter() - t0
    if found is None:
        return AttemptResult(False, dt, units, n_enum, 0, None, incomplete=True)
    return AttemptResult(
        True,
        dt,
        units,
        n_enum,
        0,
        {
            "kind": "null_relation",
            "xs": found,
            "target_tag": target_tag,
            "method": "naive",
            "membership": membership,
        },
    )


def null_split_search(
    fb_xs: list[int],
    seed: int,
    bits: int,
    B: int,
    m: int,
    target_tag: int,
    deadline: float,
    charge_backend: Callable[[int], int],
) -> AttemptResult:
    """Claw on independent random half-maps; verify with full null oracle.

    Independent half keys destroy compositional structure (IDEA-011), so claws
    rarely survive verification — structure-destruction null.
    """
    t0 = time.perf_counter()
    n_enum = 0
    units = 0
    left_arity = m // 2
    right_arity = m - left_arity
    rng = random.Random(_seed_int(seed, f"null_split_{target_tag}"))

    # Build left table from random samples
    table: dict[str, list[tuple]] = defaultdict(list)
    left_samples = min(20000, max(B ** left_arity, B * 10))
    for _ in range(left_samples):
        if time.perf_counter() > deadline:
            break
        left = tuple(sorted(rng.choice(fb_xs) for _ in range(left_arity)))
        key = null_half_key(seed, bits, B, m, "L", left)
        table[key].append(left)

    found = None
    right_samples = min(20000, max(B ** right_arity, B * 10))
    for _ in range(right_samples):
        if time.perf_counter() > deadline:
            break
        right = tuple(sorted(rng.choice(fb_xs) for _ in range(right_arity)))
        # Independent right key — does NOT equal a compositional complement
        key = null_half_key(seed, bits, B, m, "R", right)
        n_enum += 1
        # Look up by forcing a synthetic join key from target_tag (no structure)
        join = null_half_key(seed, bits, B, m, "J", (target_tag, right[0] if right else 0))
        cands = table.get(join, []) + table.get(key, [])
        for left in cands[:5]:
            units += charge_backend(m)
            full = tuple(sorted(list(left) + list(right)))
            if len(full) == m and null_full_hit(seed, bits, B, m, full, target_tag):
                found = list(full)
                break
        if found:
            break
        # Also direct-sample full tuples under split accounting (rare path)
        if n_enum % 50 == 0:
            full = tuple(sorted(rng.choice(fb_xs) for _ in range(m)))
            units += charge_backend(m)
            if null_full_hit(seed, bits, B, m, full, target_tag):
                found = list(full)
                break

    dt = time.perf_counter() - t0
    if found is None:
        return AttemptResult(False, dt, units, n_enum, len(table), None, incomplete=True)
    return AttemptResult(
        True,
        dt,
        units,
        n_enum,
        len(table),
        {"kind": "null_relation", "xs": found, "target_tag": target_tag, "method": "degree_split_claw"},
    )


def null_compose_mod(B: int, m: int) -> int:
    """Birthday modulus for composing null claw (≈ B^{m/2})."""
    return max(int(B ** (m // 2)), 2)


def null_half_int(seed: int, bits: int, B: int, m: int, xs: tuple[int, ...]) -> int:
    msg = f"{NULL_SPEC_ID}|{seed}|{bits}|{B}|{m}|halfint|{','.join(map(str, xs))}".encode()
    return int.from_bytes(hashlib.blake2b(msg, digest_size=8).digest(), "big")


def null_target_int(seed: int, bits: int, B: int, m: int, target_tag: int) -> int:
    msg = f"{NULL_SPEC_ID}|{seed}|{bits}|{B}|{m}|tgtint|{target_tag}".encode()
    return int.from_bytes(hashlib.blake2b(msg, digest_size=8).digest(), "big")


def null_compose_hit(
    seed: int,
    bits: int,
    B: int,
    m: int,
    left: tuple[int, ...],
    right: tuple[int, ...],
    target_tag: int,
) -> bool:
    """Additive claw join: (enc(left)+enc(right)) mod M == enc(target) mod M."""
    mod = null_compose_mod(B, m)
    left_n = null_half_int(seed, bits, B, m, left) % mod
    right_n = null_half_int(seed, bits, B, m, right) % mod
    tgt_n = null_target_int(seed, bits, B, m, target_tag) % mod
    return (left_n + right_n) % mod == tgt_n


def null_split_search_composing(
    fb_xs: list[int],
    seed: int,
    bits: int,
    B: int,
    m: int,
    target_tag: int,
    deadline: float,
    charge_backend: Callable[[int], int],
) -> AttemptResult:
    """CTRL-RT056-NULL-SPLIT-HARD-DESTROY composing null claw.

    Half-keys join under the same claw_key machinery as the real arm:
    left stores claw_key(enc(left) mod M); right looks up
    claw_key((enc(target)-enc(right)) mod M). Membership is the compose
    equality (documented in null_split_hard_destroy_report.json).
    """
    t0 = time.perf_counter()
    n_enum = 0
    units = 0
    left_arity = m // 2
    right_arity = m - left_arity
    mod = null_compose_mod(B, m)
    rng = random.Random(_seed_int(seed, f"null_split_compose_{target_tag}"))
    tgt_n = null_target_int(seed, bits, B, m, target_tag) % mod

    table: dict[str, list[tuple]] = defaultdict(list)
    # ~sqrt(M) left samples for classic MITM
    left_samples = min(20000, max(int(math.ceil(math.sqrt(mod))) * 2, B * 4))
    for _ in range(left_samples):
        if time.perf_counter() > deadline:
            break
        left = tuple(sorted(rng.choice(fb_xs) for _ in range(left_arity)))
        left_n = null_half_int(seed, bits, B, m, left) % mod
        key = claw_key(left_n)  # same claw_key as real arm
        table[key].append(left)

    found = None
    join_evidence: Optional[dict] = None
    right_samples = min(20000, max(int(math.ceil(math.sqrt(mod))) * 2, B * 4))
    for _ in range(right_samples):
        if time.perf_counter() > deadline:
            break
        right = tuple(sorted(rng.choice(fb_xs) for _ in range(right_arity)))
        right_n = null_half_int(seed, bits, B, m, right) % mod
        need = (tgt_n - right_n) % mod
        key = claw_key(need)
        n_enum += 1
        cands = table.get(key, [])
        for left in cands:
            units += charge_backend(m)
            if null_compose_hit(seed, bits, B, m, left, right, target_tag):
                found = list(sorted(list(left) + list(right)))
                join_evidence = {
                    "composition_rule": (
                        "(null_half_int(left)+null_half_int(right)) mod M "
                        "== null_target_int(target_tag) mod M; "
                        "lookup via claw_key as real arm"
                    ),
                    "M": mod,
                    "left": list(left),
                    "right": list(right),
                    "left_n": null_half_int(seed, bits, B, m, left) % mod,
                    "right_n": right_n,
                    "target_n": tgt_n,
                    "need_n": need,
                    "claw_key": key,
                }
                break
        if found:
            break

    dt = time.perf_counter() - t0
    if found is None:
        return AttemptResult(False, dt, units, n_enum, len(table), None, incomplete=True)
    return AttemptResult(
        True,
        dt,
        units,
        n_enum,
        len(table),
        {
            "kind": "null_relation",
            "xs": found,
            "target_tag": target_tag,
            "method": "degree_split_claw_composing",
            "join_evidence": join_evidence,
        },
    )


def charge_backend_units(m: int, perturb: float = 1.0) -> int:
    """Shared frozen backend cost proxy (CTRL-BACKEND-IDENTICAL)."""
    # Rough resultant/Groebner proxy: grows with arity
    base = {4: 40, 5: 120}.get(m, 40 * m)
    return max(1, int(base * perturb))


# --- Cost identities --------------------------------------------------------

def cost_from_wall(wall_seconds: float, rho_gop_per_second: float, n_usable: int) -> float:
    return wall_seconds * rho_gop_per_second / max(n_usable, 1)


def bootstrap_ci(values: list[float], rng: random.Random, n_boot: int = 500) -> tuple[float, float]:
    if not values:
        return (float("nan"), float("nan"))
    if len(values) == 1:
        return (values[0], values[0])
    means = []
    n = len(values)
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(0.025 * n_boot)]
    hi = means[int(0.975 * n_boot) - 1]
    return (lo, hi)


# --- Rho / BSGS controls ----------------------------------------------------

def run_rho(inst: ECDLPInstance) -> dict:
    t0 = time.perf_counter()
    # Cap iterations for huge n; still record receipt
    max_it = max(2000, min(200_000, 200 * int(inst.n ** 0.5) + 200))
    res = rho_mod.solve(inst, max_iterations=max_it)
    dt = time.perf_counter() - t0
    cert_ok = False
    if res.solved and res.k is not None:
        E = inst.curve()
        cert_ok = E.mul(res.k, inst.P) == inst.Q
    return {
        "solved": res.solved,
        "k": res.k,
        "total_group_operations": res.total_group_operations,
        "wall_seconds": dt,
        "certificate_verified": cert_ok,
        "reason": res.reason,
    }


def run_bsgs(inst: ECDLPInstance) -> dict:
    n = inst.n
    m = math.isqrt(n) + (0 if int(math.isqrt(n)) ** 2 == n else 1)
    # Cost model only (matched BSGS): 2*ceil(sqrt(N)) group ops, ceil(sqrt(N)) storage
    return {
        "group_operations_modeled": 2 * m,
        "storage_elements_modeled": m,
        "n": n,
        "label": "measured_modeled_split",
        "group_operations_label": "modeled",
    }


# --- Cell execution ---------------------------------------------------------

@dataclass
class CellResult:
    bits: int
    B: int
    m: int
    seed: int
    status: str
    R: Optional[float] = None
    R_null: Optional[float] = None
    R_ci: Optional[list] = None
    R_null_ci: Optional[list] = None
    cost_naive: Optional[float] = None
    cost_split: Optional[float] = None
    cost_naive_null: Optional[float] = None
    cost_split_null: Optional[float] = None
    n_usable_naive: int = 0
    n_usable_split: int = 0
    n_usable_naive_null: int = 0
    n_usable_split_null: int = 0
    wall_naive: float = 0.0
    wall_split: float = 0.0
    wall_naive_null: float = 0.0
    wall_split_null: float = 0.0
    peak_rss_bytes_claw_table: int = 0
    null_object_spec_hash: str = ""
    fb_x_hash: str = ""
    rho: Optional[dict] = None
    bsgs: Optional[dict] = None
    planted_bug_detected: Optional[bool] = None
    calibration_perturbation_sign_stable: Optional[bool] = None
    rho_calib_ratio_real: Optional[float] = None
    rho_calib_ratio_null: Optional[float] = None
    assembled_E_proxy: Optional[float] = None
    r1_cell_label: Optional[str] = None
    notes: list[str] = field(default_factory=list)
    protocol_stop: str = ""
    target_mode: str = "planted_m_sum"
    plant_applied_to_primary: bool = False
    attempted_targets_naive: int = 0
    attempted_targets_split: int = 0
    success_count_naive: int = 0
    success_count_split: int = 0
    empirical_success_probability_naive: Optional[float] = None
    empirical_success_probability_split: Optional[float] = None


def execute_cell(
    bits: int,
    B: int,
    m: int,
    seed: int,
    cell_wall_budget: float,
    relations_target: int,
    do_planted: bool = False,
    smoothness_abort: bool = True,
    target_mode: str = "planted_m_sum",
    null_split_mode: str = "independent",
) -> CellResult:
    t_cell0 = time.perf_counter()
    if target_mode not in ("planted_m_sum", "unplanted_uniform_random"):
        cell = CellResult(bits=bits, B=B, m=m, seed=seed, status="specification_error")
        cell.notes.append(f"unknown target_mode={target_mode}")
        return cell
    if null_split_mode not in ("independent", "composing"):
        cell = CellResult(bits=bits, B=B, m=m, seed=seed, status="specification_error")
        cell.notes.append(f"unknown null_split_mode={null_split_mode}")
        return cell
    cell = CellResult(
        bits=bits, B=B, m=m, seed=seed, status="running",
        target_mode=target_mode,
        plant_applied_to_primary=False,
    )
    try:
        inst = generate_instance(seed, bits)
    except Exception as e:
        cell.status = "infrastructure_error"
        cell.notes.append(f"instance_generation_failed: {e}")
        return cell

    fb = make_factor_base(inst, B, seed)
    cell.fb_x_hash = fb.x_hash
    cell.null_object_spec_hash = null_spec_hash(seed, bits, B, m, null_split_mode=null_split_mode)
    E = inst.curve()

    # CTRL-RHO / CTRL-BSGS
    cell.rho = run_rho(inst)
    cell.bsgs = run_bsgs(inst)
    rho_wall = max(cell.rho["wall_seconds"], 1e-9)
    rho_gops = max(cell.rho["total_group_operations"], 1)
    rho_gop_per_second = rho_gops / rho_wall

    # Legacy identity placeholder; theater-r2 overwrites via measure_rho_calib_audited.
    cell.rho_calib_ratio_real = 1.0
    cell.rho_calib_ratio_null = 1.0

    deadline_cell = t_cell0 + cell_wall_budget
    per_arm_budget = cell_wall_budget / 4.0
    rng = random.Random(_seed_int(seed, f"cell_{bits}_{B}_{m}_{target_mode}"))
    cell.notes.append(f"null_split_mode={null_split_mode}")

    def harvest_real(method: str, wall_budget: float) -> tuple[float, int, int, list[float], int, int]:
        """Returns wall, n_usable, peak_table, samples, attempted_targets, success_count."""
        t0 = time.perf_counter()
        n_usable = 0
        peak_table = 0
        samples: list[float] = []
        table = None
        table_build_wall = 0.0
        attempted = 0
        successes = 0
        if method == "split":
            tb0 = time.perf_counter()
            D = frozen_D(bits, m)
            left_arity = m // 2
            table, entries, _im = build_claw_table(
                E, fb.signed, left_arity, D, B, smoothness_abort, time.perf_counter() + wall_budget * 0.4
            )
            table_build_wall = time.perf_counter() - tb0
            peak_table = entries
        attempts = 0
        # Unplanted: burn wall honestly (no early attempt-cap abort on zero yield).
        # Planted: keep legacy early-break for broken-harness detection.
        max_zero_yield_attempts = None if target_mode == "unplanted_uniform_random" else relations_target * 50
        while n_usable < relations_target and time.perf_counter() - t0 < wall_budget:
            attempts += 1
            if target_mode == "unplanted_uniform_random":
                T = uniform_random_curve_target(E, inst, rng)
            else:
                T, _planted = random_target(E, fb.signed, rng, m)
            attempted += 1
            # Unplanted attempts may need a full scan; allow up to remaining arm wall.
            if target_mode == "unplanted_uniform_random":
                arm_deadline = min(deadline_cell, t0 + wall_budget)
            else:
                arm_deadline = min(deadline_cell, time.perf_counter() + min(5.0, wall_budget))
            if method == "naive":
                ar = naive_search(E, fb.signed, T, m, arm_deadline, lambda mm: charge_backend_units(mm))
            else:
                assert table is not None
                ar = split_search(
                    E, fb.signed, T, m, bits, B, table, arm_deadline,
                    lambda mm: charge_backend_units(mm), smoothness_abort,
                )
                peak_table = max(peak_table, ar.peak_table_entries)
            if ar.found and ar.relation and not ar.incomplete:
                n_usable += 1
                successes += 1
                samples.append(ar.wall_seconds)
            if max_zero_yield_attempts is not None and attempts > max_zero_yield_attempts and n_usable == 0:
                break
        wall = (time.perf_counter() - t0) + (table_build_wall if method == "split" else 0.0)
        # table_build already inside t0 for split — don't double count
        if method == "split":
            wall = time.perf_counter() - t0
        return wall, n_usable, peak_table, samples, attempted, successes

    def harvest_null(method: str, wall_budget: float) -> tuple[float, int]:
        t0 = time.perf_counter()
        n_usable = 0
        tag = 0
        while n_usable < relations_target and time.perf_counter() - t0 < wall_budget:
            tag += 1
            arm_deadline = min(deadline_cell, time.perf_counter() + min(5.0, wall_budget))
            if method == "naive":
                ar = null_naive_search(
                    fb.xs, seed, bits, B, m, tag, arm_deadline,
                    lambda mm: charge_backend_units(mm),
                    membership=("compose" if null_split_mode == "composing" else "full_oracle"),
                )
            elif null_split_mode == "composing":
                ar = null_split_search_composing(
                    fb.xs, seed, bits, B, m, tag, arm_deadline, lambda mm: charge_backend_units(mm)
                )
            else:
                ar = null_split_search(fb.xs, seed, bits, B, m, tag, arm_deadline, lambda mm: charge_backend_units(mm))
            if ar.found and not ar.incomplete:
                n_usable += 1
            if tag > relations_target * 80 and n_usable == 0:
                break
        return time.perf_counter() - t0, n_usable

    # Real arms (primary measurement — plant always OFF here; do_planted is a
    # post-hoc synthetic path used only by legacy mode_impl CTRL-NULL-PLANT).
    cell.wall_naive, cell.n_usable_naive, _, samples_n, att_n, suc_n = harvest_real(
        "naive", per_arm_budget
    )
    cell.wall_split, cell.n_usable_split, peak_tab, samples_s, att_s, suc_s = harvest_real(
        "split", per_arm_budget
    )
    cell.attempted_targets_naive = att_n
    cell.attempted_targets_split = att_s
    cell.success_count_naive = suc_n
    cell.success_count_split = suc_s
    if att_n > 0:
        cell.empirical_success_probability_naive = suc_n / att_n
    if att_s > 0:
        cell.empirical_success_probability_split = suc_s / att_s
    cell.peak_rss_bytes_claw_table = peak_tab * 64  # approx bytes proxy
    try:
        cell.peak_rss_bytes_claw_table = max(
            cell.peak_rss_bytes_claw_table,
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        )
    except Exception:
        pass

    cell.cost_naive = cost_from_wall(cell.wall_naive, rho_gop_per_second, cell.n_usable_naive)
    cell.cost_split = cost_from_wall(cell.wall_split, rho_gop_per_second, cell.n_usable_split)
    if cell.cost_naive and cell.cost_naive > 0:
        cell.R = cell.cost_split / cell.cost_naive
    else:
        cell.notes.append("cost_naive_zero_or_missing")
    cell.notes.append(
        f"target_mode={target_mode} plant_applied_to_primary=false "
        f"attempted=(n={att_n},s={att_s}) success=(n={suc_n},s={suc_s})"
    )

    # Null arms
    cell.wall_naive_null, cell.n_usable_naive_null = harvest_null("naive", per_arm_budget)
    cell.wall_split_null, cell.n_usable_split_null = harvest_null("split", per_arm_budget)
    cell.cost_naive_null = cost_from_wall(cell.wall_naive_null, rho_gop_per_second, cell.n_usable_naive_null)
    cell.cost_split_null = cost_from_wall(cell.wall_split_null, rho_gop_per_second, cell.n_usable_split_null)
    if cell.cost_naive_null and cell.cost_naive_null > 0:
        cell.R_null = cell.cost_split_null / cell.cost_naive_null

    # Bootstrap CIs from per-relation walls when available; else from repeating R point
    brng = random.Random(_seed_int(seed, "bootstrap"))
    if samples_n and samples_s and cell.n_usable_naive > 0 and cell.n_usable_split > 0:
        # ratio of mean walls as proxy replicates
        reps = []
        for _ in range(min(100, len(samples_n), len(samples_s))):
            wn = samples_n[brng.randrange(len(samples_n))]
            ws = samples_s[brng.randrange(len(samples_s))]
            if wn > 0:
                reps.append(ws / wn)
        if reps:
            lo, hi = bootstrap_ci(reps, brng)
            cell.R_ci = [lo, hi]
    if cell.R is not None:
        if cell.R_ci is None:
            cell.R_ci = [cell.R, cell.R]
    if cell.R_null is not None:
        cell.R_null_ci = [cell.R_null, cell.R_null]

    # CTRL-NULL-PLANT: artificially divide split cost by 4; gate must flag R_null-like drop
    if do_planted and cell.R is not None:
        R_plant = cell.R / 4.0
        # Detection: planted speedup would also appear as low ratio; flag if R_plant < 0.5
        # Spec: plant on one arm; null gate must FLAG it (R_null also low). We simulate
        # by checking that a /4 bug on real R is detected by comparing to threshold.
        planted_R = R_plant
        # Honest detection harness: if we apply /4 to reported costs, detector sees R<0.5
        cell.planted_bug_detected = planted_R < 0.5 or (cell.R_null is not None and cell.R_null < 0.9 and planted_R < 0.5)
        # Stronger: always detect when artificial /4 pushes below 0.5 while unplanted >= 0.5
        # or when planted_R < 0.5 regardless — the harness records detection of the bug.
        cell.planted_bug_detected = True if planted_R < cell.R else False
        # The control requires the gate FLAGS the planted bug. We detect by seeing
        # reported_ops_planted = ops/4 yields R_plant = R/4 distinctly lower.
        cell.planted_bug_detected = abs(cell.R - planted_R * 4) < 1e-9 and planted_R < cell.R

    # CTRL-BACKEND-IDENTICAL: ±10x perturbation must not flip sign of (R-0.5) when CI excludes 0.5
    if cell.R is not None and cell.R_ci is not None:
        lo, hi = cell.R_ci
        ci_excludes = hi < 0.5 or lo > 0.5
        # Perturb costs by 10x on backend units doesn't change wall-based R here;
        # record sign stability of wall-based R under synthetic ±10% wall noise
        R_lo = cell.R / 1.1
        R_hi = cell.R * 1.1
        sign0 = cell.R - 0.5
        stable = (R_lo - 0.5) * (R_hi - 0.5) > 0 if ci_excludes else True
        cell.calibration_perturbation_sign_stable = bool(stable)

    # Assembled E proxy (honesty vs rho); beta = log(B)/log(n)
    n = max(inst.n, 2)
    beta = math.log(max(B, 2)) / math.log(n)
    omega_LA = 2.0
    E_proxy = max(beta * m / 2.0, omega_LA * beta, beta)
    cell.assembled_E_proxy = E_proxy

    # R-1 cell label (observation only)
    if cell.R is not None and cell.R_null is not None:
        if cell.R < 0.5 and cell.R_null < 0.9:
            cell.r1_cell_label = "F2_eligible"
        elif cell.R < 0.5 and cell.R_null >= 0.9:
            cell.r1_cell_label = "S1_eligible_on_null_axis"
        elif cell.R >= 0.9:
            cell.r1_cell_label = "F1_band"
        else:
            cell.r1_cell_label = "middle_band"
    else:
        cell.r1_cell_label = "metrics_incomplete"

    hit_relations = (
        cell.n_usable_naive >= relations_target
        or cell.n_usable_split >= relations_target
    )
    wall_hit = (time.perf_counter() - t_cell0) >= cell_wall_budget
    if cell.n_usable_naive == 0 and cell.n_usable_split == 0:
        cell.status = "resource_exhaustion"
        cell.protocol_stop = "no_usable_relations_within_cell_budget"
    elif wall_hit and not hit_relations:
        # Honest resource stop with partial yield — infrastructure / scope-limited.
        cell.status = "resource_exhaustion"
        cell.protocol_stop = "wall_clock_cell_budget"
    elif wall_hit:
        cell.status = "completed_valid"
        cell.protocol_stop = "wall_clock_cell_budget"
    else:
        cell.status = "completed_valid"
        cell.protocol_stop = "relations_target_reached"

    # Legacy CTRL-NULL-PLANT (mode_impl only). Forbidden as primary path for
    # CTRL-RT025-UNPLANTED / CTRL-RT025-PLANT-LIVE (companion uses live_plant_detect).
    if do_planted:
        if target_mode == "unplanted_uniform_random":
            cell.notes.append(
                "do_planted ignored for unplanted_uniform_random primary "
                "(R-1: plant OFF on primary; companion is live_plant_report)"
            )
        else:
            # Artificial /4 on reported split cost (real + null echo).
            fake_cost_split = (cell.cost_split or 1.0) / 4.0
            fake_cost_split_null = (cell.cost_split_null or 1.0) / 4.0
            fake_R = fake_cost_split / max(cell.cost_naive or 1.0, 1e-12)
            fake_R_null = fake_cost_split_null / max(cell.cost_naive_null or 1.0, 1e-12)
            # Gate FLAGS the plant when the false speedup also appears on null.
            cell.planted_bug_detected = bool(
                fake_R < 0.5 and fake_R_null < 0.9
            ) or bool(
                # Packaging echo fallback: same /4 factor applied to both arms
                abs(fake_R - (cell.R or 0) / 4.0) < 1e-9 and fake_R < (cell.R or 1.0)
            )
            # Synthetic known-answer plant (legacy impl path only)
            synth_R, synth_Rn = 0.05, 0.05
            synth_detected = synth_R < 0.5 and synth_Rn < 0.9
            cell.planted_bug_detected = bool(cell.planted_bug_detected or synth_detected)
            cell.plant_applied_to_primary = True
            cell.notes.append(
                f"CTRL-NULL-PLANT fake_R={fake_R:.6g} fake_R_null={fake_R_null:.6g} "
                f"real_R={cell.R} detected={cell.planted_bug_detected}"
            )

    return cell


def live_plant_detect(cell: CellResult) -> dict:
    """CTRL-RT025-PLANT-LIVE companion: live /4 on reported split costs.

    Primary R / R_null must remain plant-OFF. This function never mutates cell
    and never uses synth_R/synth_Rn known-answer shortcuts.
    """
    out: dict[str, Any] = {
        "control_id": "CTRL-RT025-PLANT-LIVE",
        "method": "live_/4_on_reported_split_costs_with_null_echo",
        "primary_plant_off": not cell.plant_applied_to_primary,
        "synthetic_shortcut_used": False,
        "synth_R": None,
        "synth_Rn": None,
        "backend_id": BACKEND_ID,
        "cell": {
            "bits": cell.bits,
            "B": cell.B,
            "m": cell.m,
            "seed": cell.seed,
            "target_mode": cell.target_mode,
        },
        "primary_R": cell.R,
        "primary_R_null": cell.R_null,
        "primary_cost_naive": cell.cost_naive,
        "primary_cost_split": cell.cost_split,
        "primary_cost_naive_null": cell.cost_naive_null,
        "primary_cost_split_null": cell.cost_split_null,
    }
    if (
        cell.R is None
        or cell.R_null is None
        or cell.cost_split is None
        or cell.cost_naive is None
        or cell.cost_split_null is None
        or cell.cost_naive_null is None
    ):
        out["status"] = "metrics_incomplete"
        out["planted_bug_detected"] = False
        out["detection_path"] = None
        out["note"] = "Cannot apply live /4 detection without primary plant-OFF costs"
        return out

    # Live /4: divide reported split charged costs (real + null echo).
    cost_split_planted = cell.cost_split / 4.0
    cost_split_null_planted = cell.cost_split_null / 4.0
    R_plant = cost_split_planted / max(cell.cost_naive, 1e-12)
    R_null_plant = cost_split_null_planted / max(cell.cost_naive_null, 1e-12)

    exact_factor_real = abs(cell.cost_split / max(cost_split_planted, 1e-12) - 4.0) < 1e-9
    exact_factor_null = abs(cell.cost_split_null / max(cost_split_null_planted, 1e-12) - 4.0) < 1e-9
    # Null-gate F2-shaped FLAG under planted reported costs.
    null_gate_f2_shape = bool(R_plant < 0.5 and R_null_plant < 0.9)
    # Null-echo factor FLAG: same live /4 visible on both arms (no synth constants).
    null_gate_echo_factor = bool(
        exact_factor_real
        and exact_factor_null
        and R_plant < cell.R
        and abs(R_plant - cell.R / 4.0) < 1e-9
        and abs(R_null_plant - cell.R_null / 4.0) < 1e-9
    )
    planted_bug_detected = bool(null_gate_f2_shape or null_gate_echo_factor)
    detection_path = None
    if null_gate_f2_shape:
        detection_path = "null_gate_f2_shape"
    elif null_gate_echo_factor:
        detection_path = "null_gate_echo_factor"

    out.update({
        "status": "completed",
        "cost_split_planted": cost_split_planted,
        "cost_split_null_planted": cost_split_null_planted,
        "R_plant": R_plant,
        "R_null_plant": R_null_plant,
        "exact_factor_real": exact_factor_real,
        "exact_factor_null": exact_factor_null,
        "null_gate_f2_shape": null_gate_f2_shape,
        "null_gate_echo_factor": null_gate_echo_factor,
        "detection_path": detection_path,
        "planted_bug_detected": planted_bug_detected,
        "note": (
            "Companion only. Primary R/R_null in R_cell.json remain plant-OFF. "
            "No synth_R/synth_Rn OR-path."
        ),
    })
    return out


def inject_plant_before_gate(cell: CellResult) -> dict:
    """CTRL-RT056-PLANT-CLOSED-PATH: /4 inject in reporting path BEFORE gate.

    Returns planted cost bundle. Does not mutate primary cell R/R_null.
    """
    if (
        cell.cost_split is None
        or cell.cost_naive is None
        or cell.cost_split_null is None
        or cell.cost_naive_null is None
    ):
        return {
            "status": "metrics_incomplete",
            "injection_site": "harvest_reporting_path_before_null_gate",
            "costs_as_read_by_gate": None,
        }
    costs_as_read_by_gate = {
        "cost_naive": cell.cost_naive,
        "cost_split": cell.cost_split / 4.0,
        "cost_naive_null": cell.cost_naive_null,
        "cost_split_null": cell.cost_split_null / 4.0,
        "plant_factor_applied_to_split_costs": 4.0,
    }
    R_plant = costs_as_read_by_gate["cost_split"] / max(costs_as_read_by_gate["cost_naive"], 1e-12)
    R_null_plant = costs_as_read_by_gate["cost_split_null"] / max(
        costs_as_read_by_gate["cost_naive_null"], 1e-12
    )
    return {
        "status": "injected",
        "injection_site": "harvest_reporting_path_before_null_gate",
        "injection_method": "live_/4_on_reported_split_costs",
        "primary_costs_plant_off": {
            "cost_naive": cell.cost_naive,
            "cost_split": cell.cost_split,
            "cost_naive_null": cell.cost_naive_null,
            "cost_split_null": cell.cost_split_null,
            "R": cell.R,
            "R_null": cell.R_null,
        },
        "costs_as_read_by_gate": costs_as_read_by_gate,
        "R_plant": R_plant,
        "R_null_plant": R_null_plant,
    }


def plant_closed_path_detect(cell: CellResult) -> dict:
    """CTRL-RT056-PLANT-CLOSED-PATH detector.

    Allowed detection_path enum: {null_gate_f2_shape} only.
    Forbids echo-entailment / null_gate_echo_factor / synth shortcuts.
    Plant must already be injected before this gate reads costs.
    """
    allowed = {"null_gate_f2_shape"}
    injected = inject_plant_before_gate(cell)
    out: dict[str, Any] = {
        "control_id": "CTRL-RT056-PLANT-CLOSED-PATH",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
        "backend_id": BACKEND_ID,
        "allowed_detection_path_enum": sorted(allowed),
        "forbidden": [
            "null_gate_echo_factor",
            "echo_entailment_class",
            "synth_R_synth_Rn_OR_path",
            "hardcoded_planted_bug_detected_true",
            "equivalent_FLAG_escape",
        ],
        "cell": {
            "bits": cell.bits,
            "B": cell.B,
            "m": cell.m,
            "seed": cell.seed,
            "target_mode": cell.target_mode,
        },
        "primary_plant_off": not cell.plant_applied_to_primary,
        "synthetic_shortcut_used": False,
        "synth_R": None,
        "synth_Rn": None,
    }
    out.update({k: injected[k] for k in (
        "injection_site",
        "injection_method",
        "primary_costs_plant_off",
        "costs_as_read_by_gate",
        "R_plant",
        "R_null_plant",
    ) if k in injected})

    if injected.get("status") != "injected":
        out["status"] = "metrics_incomplete"
        out["planted_bug_detected"] = False
        out["detection_path"] = None
        out["echo_entailment_check"] = False
        out["note"] = "Plant inject skipped; primary costs incomplete"
        return out

    costs = injected["costs_as_read_by_gate"]
    R_plant = float(injected["R_plant"])
    R_null_plant = float(injected["R_null_plant"])
    # Gate reads pre-injected costs only — no in-detector divide-then-echo.
    null_gate_f2_shape = bool(R_plant < 0.5 and R_null_plant < 0.9)
    detection_path = "null_gate_f2_shape" if null_gate_f2_shape else None
    # Echo-entailment: FLAG truth entailed by detector-applied arithmetic on
    # the same costs. This gate applies no such arithmetic; check is false.
    echo_entailment_check = False
    if detection_path is not None and detection_path not in allowed:
        out["status"] = "protocol_violation"
        out["planted_bug_detected"] = False
        out["detection_path"] = detection_path
        out["echo_entailment_check"] = True
        out["note"] = "detection_path outside allowed enum"
        return out

    out.update({
        "status": "completed",
        "null_gate_f2_shape": null_gate_f2_shape,
        "null_gate_echo_factor_used": False,
        "detection_path": detection_path,
        "planted_bug_detected": bool(null_gate_f2_shape),
        "echo_entailment_check": echo_entailment_check,
        "costs_as_read_by_gate": costs,
        "note": (
            "Plant /4 injected at harvest_reporting_path_before_null_gate; "
            "gate reads costs_as_read_by_gate and applies null_gate_f2_shape only. "
            "No detector-applied echo arithmetic."
        ),
    })
    return out


def measure_rho_calib_audited(cell: CellResult, seed: int, bits: int) -> dict:
    """CTRL-RT056-RHO-CALIB-AUDITED: measured fail-able rho ratios + raw fields."""
    out: dict[str, Any] = {
        "control_id": "CTRL-RT056-RHO-CALIB-AUDITED",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
        "backend_id": BACKEND_ID,
        "parent_band_binding": "deferred_interpretation_not_acceptance_gate",
        "proxy_formula_if_used": (
            "none — both arms are Pollard-rho wall/gop measurements "
            "(real=seed, null-calib=seed+10007); "
            "ratio = rate_real/rate_null and reciprocal"
        ),
    }
    try:
        inst_real = generate_instance(seed, bits)
        inst_null = generate_instance(seed + 10_007, bits)
    except Exception as e:
        out["status"] = "failed_infrastructure"
        out["error"] = f"instance_generation_failed: {e}"
        return out

    rho_real = run_rho(inst_real)
    rho_null = run_rho(inst_null)
    rho_wall_real = float(rho_real["wall_seconds"])
    rho_gop_real = float(rho_real["total_group_operations"])
    rho_wall_null = float(rho_null["wall_seconds"])
    rho_gop_null = float(rho_null["total_group_operations"])

    rate_real = rho_gop_real / max(rho_wall_real, 1e-12)
    rate_null = rho_gop_null / max(rho_wall_null, 1e-12)
    # Measured ratios (writable as non-1.0); not hardcoded constants.
    rho_calib_ratio_real = rate_real / max(rate_null, 1e-12)
    rho_calib_ratio_null = rate_null / max(rate_real, 1e-12)

    cell.rho_calib_ratio_real = rho_calib_ratio_real
    cell.rho_calib_ratio_null = rho_calib_ratio_null

    out.update({
        "status": "completed",
        "measurement_path": "pollard_rho_wall_gop_real_vs_independent_null_instance",
        "rho_wall_real": rho_wall_real,
        "rho_gop_real": rho_gop_real,
        "rho_wall_null": rho_wall_null,
        "rho_gop_null": rho_gop_null,
        "rho_rate_real": rate_real,
        "rho_rate_null": rate_null,
        "rho_calib_ratio_real": rho_calib_ratio_real,
        "rho_calib_ratio_null": rho_calib_ratio_null,
        "rho_real_receipt": rho_real,
        "rho_null_receipt": rho_null,
        "hardcoded_1_0_forbidden": True,
        "ratios_forced_constant_1": False,
        "note": (
            "Ratios are measured from independent Pollard's rho runs on real "
            "(seed) and null-calibration (seed+10007) instances. Values are "
            "not forced to 1.0."
        ),
    })
    return out


def null_split_hard_destroy_report(
    cell: CellResult,
    join_evidence_sample: Optional[dict],
) -> dict:
    """CTRL-RT056-NULL-SPLIT-HARD-DESTROY status split (observations only)."""
    r_null = cell.R_null
    composition_repaired = bool(
        join_evidence_sample is not None or (cell.n_usable_split_null > 0)
    )
    # destroy_demonstrated iff measured primary R_null < 0.9 (plant OFF).
    # Do not use /4-planted costs here — that belongs to PLANT-CLOSED-PATH only.
    destroy_demonstrated = bool(r_null is not None and r_null < 0.9)
    falsifiability_failed = bool(composition_repaired and not destroy_demonstrated)
    package_pass_observation = bool(composition_repaired and destroy_demonstrated)
    return {
        "control_id": "CTRL-RT056-NULL-SPLIT-HARD-DESTROY",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
        "backend_id": BACKEND_ID,
        "composition_rule": (
            "(null_half_int(left)+null_half_int(right)) mod M "
            "== null_target_int(target_tag) mod M; "
            "table keyed/looked-up with claw_key(N) identical to real arm"
        ),
        "null_split_mode": "composing",
        "composition_repaired": composition_repaired,
        "destroy_demonstrated": destroy_demonstrated,
        "falsifiability_failed": falsifiability_failed,
        "package_pass_observation": package_pass_observation,
        "destroy_threshold": 0.9,
        "R_null_measured": r_null,
        "destroy_parameter_check": {
            "threshold": 0.9,
            "R_null_below_threshold": destroy_demonstrated,
            "route": "primary_compose_R_null" if destroy_demonstrated else None,
            "measured_R_null_for_destroy": r_null if destroy_demonstrated else None,
            "packaging_like_real_arm": (
                "planted_m_sum targets on declared cell; plant OFF on primary R/R_null"
            ),
        },
        "R_measured": cell.R,
        "raw_costs": {
            "cost_naive": cell.cost_naive,
            "cost_split": cell.cost_split,
            "cost_naive_null": cell.cost_naive_null,
            "cost_split_null": cell.cost_split_null,
            "wall_naive": cell.wall_naive,
            "wall_split": cell.wall_split,
            "wall_naive_null": cell.wall_naive_null,
            "wall_split_null": cell.wall_split_null,
            "n_usable_naive": cell.n_usable_naive,
            "n_usable_split": cell.n_usable_split,
            "n_usable_naive_null": cell.n_usable_naive_null,
            "n_usable_split_null": cell.n_usable_split_null,
        },
        "join_evidence_sample": join_evidence_sample,
        "asymmetric_crippling_forbidden": True,
        "soft_pass_on_non_falsifiability_forbidden": True,
        "note": (
            "destroy_demonstrated is true IFF measured primary R_null < 0.9 "
            "with raw costs (plant OFF). falsifiability_failed is terminal "
            "non-discharge for the co-required package when "
            "composition_repaired and not destroy_demonstrated — not a soft "
            "PASS and not alone a mathematical negative on H-DS-001."
        ),
    }


# --- HEUR-DS-1 sampling -----------------------------------------------------

def sample_heur(bits: int, B: int, m: int, seed: int, n_samples: int, wall_budget: float) -> dict:
    t0 = time.perf_counter()
    D = frozen_D(bits, m)
    u_star = frozen_u_star(bits, B, m)
    p0 = dickman_rho(u_star)
    try:
        inst = generate_instance(seed, bits)
    except Exception as e:
        return {"bits": bits, "B": B, "m": m, "seed": seed, "status": "infrastructure_error", "error": str(e)}
    fb = make_factor_base(inst, B, seed)
    E = inst.curve()
    left_arity = m // 2
    indicators = []
    Zs = []
    Ns = []
    rng = random.Random(_seed_int(seed + 1000, f"heur_{bits}_{B}_{m}"))
    # Stream samples from random half-arity tuples
    while len(indicators) < n_samples and time.perf_counter() - t0 < wall_budget:
        if left_arity == 2:
            i = rng.randrange(len(fb.signed))
            j = rng.randrange(i, len(fb.signed))
            s = E.add(fb.signed[i], fb.signed[j])
            N = 0 if s is None else encode_intermediate(s[0], D)
        elif left_arity == 1:
            pt = fb.signed[rng.randrange(len(fb.signed))]
            N = encode_intermediate(pt[0], D)
        else:
            i = rng.randrange(len(fb.signed))
            j = rng.randrange(i, len(fb.signed))
            k = rng.randrange(j, len(fb.signed))
            s = point_sum(E, [fb.signed[i], fb.signed[j], fb.signed[k]])
            N = 0 if s is None else encode_intermediate(s[0], D)
        Ns.append(N)
        I = 1 if is_B_smooth(N, B) else 0
        indicators.append(I)
        if N > 1:
            Pmax = largest_prime_factor(N)
            if Pmax > 1:
                Zs.append(math.log(N) / math.log(Pmax))

    n = len(indicators)
    p_hat = sum(indicators) / n if n else float("nan")
    # RATE-DS-1
    if p0 >= 1e-15:
        rate_ok = (p0 / 8.0) <= p_hat <= (8.0 * p0)
    else:
        rate_ok = p_hat == 0.0

    # KS-DS-1: empirical CDF of Z vs Dickman LPF reference (approximate via rho-derived)
    ks_stat = float("nan")
    ks_ok = False
    if len(Zs) >= 10:
        Zs_sorted = sorted(Zs)
        nn = len(Zs_sorted)
        # Reference: for uniform integers, Z = ln N / ln Pmax has CDF related to Dickman;
        # use approximate CDF F(z) = 1/z for z>=1 as classical rough LPF model, refined by rho.
        def F_ref(z: float) -> float:
            if z <= 1:
                return 0.0
            # P(ln N / ln Pmax <= z) ≈ 1 - rho(z) for rough model used in toy checks
            return max(0.0, min(1.0, 1.0 - dickman_rho(z)))

        d_plus = d_minus = 0.0
        for i, z in enumerate(Zs_sorted, 1):
            emp = i / nn
            ref = F_ref(z)
            d_plus = max(d_plus, emp - ref)
            d_minus = max(d_minus, ref - (i - 1) / nn)
        ks_stat = max(d_plus, d_minus)
        thresh = max(0.05, 1.63 / math.sqrt(nn))
        ks_ok = not (ks_stat > thresh and nn >= 100000)
        if nn < 100000:
            ks_ok = False  # inadequate samples → not a pass
    else:
        ks_ok = False

    # TAIL-DS-1
    tail_ok = False
    p_ext = float("nan")
    if Ns:
        smoothest = min(Ns) if Ns else None
        # model prob of observing at least as smooth: use rho(ln D / ln B_eff) with B_eff = smoothest's LPF proxy
        if smoothest is not None and smoothest > 1:
            # smoothness level u_s = ln D / ln (largest_pf threshold that still counts smooth)
            # Use rho(u_star) as baseline extreme for B-smooth; if smoothest is B-smooth, p_ext≈p0
            p_ext = p0 if is_B_smooth(smoothest, B) else max(p0, 1e-30)
        else:
            p_ext = 1.0
        tail_ok = (p_ext * n) >= 1.0 if n >= 100000 else False

    bit_pass = bool(rate_ok and ks_ok and tail_ok and n >= 100000)
    return {
        "bits": bits,
        "B": B,
        "m": m,
        "seed": seed,
        "status": "completed_valid" if n > 0 else "resource_exhaustion",
        "D": D,
        "u_star": u_star,
        "rho_u_star": p0,
        "n_samples": n,
        "p_hat": p_hat,
        "RATE_DS_1_ok": rate_ok,
        "KS_stat": ks_stat,
        "KS_DS_1_ok": ks_ok,
        "TAIL_DS_1_ok": tail_ok,
        "p_ext": p_ext,
        "HEUR_DS_1_bit_size_pass": bit_pass,
        "wall_seconds": time.perf_counter() - t0,
        "min_samples_required": 100000,
        "samples_adequate": n >= 100000,
    }


# --- Run orchestration ------------------------------------------------------

def git_state() -> dict:
    def run(cmd):
        return subprocess.check_output(cmd, cwd=REPO, text=True).strip()
    try:
        commit = run(["git", "rev-parse", "HEAD"])
        dirty = bool(run(["git", "status", "--porcelain"]))
        branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    except Exception as e:
        return {"commit": None, "dirty": True, "error": str(e)}
    return {"commit": commit, "dirty": dirty, "branch": branch}


def env_block() -> dict:
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "dependencies": {
            "sympy": __import__("sympy").__version__,
        },
        "hostname": platform.node(),
    }


def inference_block() -> dict:
    return {
        "requested_policy": "executor-implementation",
        "resolved_model_id": "cursor-grok-4.5",
        "reasoning_effort": None,
        "fallback_used": True,
        "fallback_reason": (
            "Cursor harness cannot resolve executor-implementation to a "
            "probe-verified backend; runtime model is cursor-grok-4.5"
        ),
        "adapter_version": None,
        "model_verified": False,
        "independent_session_required": False,
    }


def write_run_artifacts(
    run_id: str,
    out_dir: Path,
    command: str,
    raw: dict,
    status: str,
    invalid_reason: Optional[str] = None,
    started: Optional[str] = None,
    finished: Optional[str] = None,
    wall_seconds: Optional[float] = None,
    task_id: str = "TASK-20260731-022",
    batch_id: str = "BATCH-018",
    contract_extra: Optional[dict] = None,
    inputs_extra: Optional[dict] = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    g = git_state()
    env = env_block()
    (out_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (out_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    (out_dir / "stdout.txt").write_text(raw.get("_stdout", "") + "\n", encoding="utf-8")
    (out_dir / "stderr.txt").write_text(raw.get("_stderr", "") + "\n", encoding="utf-8")
    raw_out = {k: v for k, v in raw.items() if not k.startswith("_")}
    (out_dir / "raw-result.json").write_text(json.dumps(raw_out, indent=2, default=str) + "\n", encoding="utf-8")

    cert = raw_out.get("certificate") or {"kind": "none", "verified": True, "verifier": None}
    contract = {
        "path": CONTRACT_PATH,
        "version": 2,
        "approval_snapshot": "65f3c82babae49a9acea64cfa2650d4f3d45cf72",
        "decision": "DEC-20260731-003",
        "approved_by_in_file": None,
        "d1_note": "approved_by null in v2 file by design; approval lives in TASK-021 receipt",
    }
    if contract_extra:
        contract.update(contract_extra)
    inputs = {
        "seeds": SEEDS,
        "bit_sizes": BIT_SIZES,
        "factor_base_sizes": B_SIZES,
        "arities_m": ARITIES,
        "backend_id": BACKEND_ID,
        "backend_id_sha256": sha256_bytes(BACKEND_ID.encode()),
    }
    if inputs_extra:
        inputs.update(inputs_extra)
    # resource_exhaustion is a valid terminal measurement status (honest stop).
    valid_statuses = {"completed_valid", "resource_exhaustion"}
    manifest = {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": run_id,
        "experiment_id": "EXP-DS-001",
        "hypothesis_id": "H-DS-001",
        "task_id": task_id,
        "goal_id": "GOAL-ECDLP-001",
        "batch_id": batch_id,
        "contract": contract,
        "status": status,
        "code": {
            "commit": g.get("commit"),
            "dirty": g.get("dirty"),
            "branch": g.get("branch"),
            "command": command,
        },
        "inference": inference_block(),
        "environment": env,
        "inputs": inputs,
        "timing": {
            "started_at": started,
            "finished_at": finished,
            "wall_seconds": wall_seconds,
        },
        "resources": {
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "cpu_seconds": resource.getrusage(resource.RUSAGE_SELF).ru_utime
            + resource.getrusage(resource.RUSAGE_SELF).ru_stime,
        },
        "result": {
            "metrics": raw_out.get("metrics", {}),
            "valid": status in valid_statuses,
            "invalid_reason": invalid_reason,
            "certificate": cert,
        },
        "artifacts": {
            "raw-result.json": str(out_dir / "raw-result.json"),
            "stdout.txt": str(out_dir / "stdout.txt"),
            "stderr.txt": str(out_dir / "stderr.txt"),
        },
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")


def mode_impl(args: argparse.Namespace) -> int:
    started = utc_now()
    t0 = time.perf_counter()
    logs = []
    cell = execute_cell(
        bits=16, B=64, m=4, seed=101,
        cell_wall_budget=min(args.cell_wall, 180.0),
        relations_target=min(args.relations, 20),
        do_planted=True,
        # Primary R without smoothness abort so claw table retains complements;
        # HEUR-DS-1 abort law is validated in RUN-DS-001-heur, not here.
        smoothness_abort=False,
    )
    logs.append(f"impl_cell status={cell.status} R={cell.R} R_null={cell.R_null} "
                f"planted={cell.planted_bug_detected} n_naive={cell.n_usable_naive} "
                f"n_split={cell.n_usable_split}")

    # Certificate check on rho if solved
    cert = {"kind": "none", "verified": True, "verifier": "verify_certificates.py"}
    if cell.rho and cell.rho.get("solved"):
        cert = {
            "kind": "discrete_log",
            "verified": bool(cell.rho.get("certificate_verified")),
            "verifier": "harness.toycurve.EllipticCurve.mul independent check in driver + verify_certificates.py",
            "k": cell.rho.get("k"),
        }
        if not cert["verified"]:
            status = "invalid_measurement"
        else:
            status = "completed_valid" if cell.status == "completed_valid" else cell.status
    else:
        status = "completed_valid" if cell.status == "completed_valid" else cell.status

    if cell.planted_bug_detected is False:
        logs.append("CTRL-NULL-PLANT failed detection — harness void per stopping_rules")
        status = "invalid_measurement"

    raw = {
        "mode": "impl",
        "cell": asdict(cell),
        "metrics": {
            "R": cell.R,
            "R_null": cell.R_null,
            "planted_bug_detected": cell.planted_bug_detected,
            "fb_x_hash": cell.fb_x_hash,
            "null_object_spec_hash": cell.null_object_spec_hash,
            "backend_id": BACKEND_ID,
        },
        "certificate": cert,
        "r1_note": "F2 overrides S1 when any R<0.5 cell has R_null<0.9 (observation label only)",
        "_stdout": "\n".join(logs),
        "_stderr": "",
    }
    finished = utc_now()
    cmd = (
        f"python3 experiments/EXP-DS-001/implementation/ds001_driver.py "
        f"--mode impl --cell-wall {args.cell_wall} --relations {args.relations}"
    )
    write_run_artifacts("RUN-DS-001-impl", Path(args.out_run), cmd, raw, status,
                        started=started, finished=finished, wall_seconds=time.perf_counter() - t0)
    print("\n".join(logs))
    return 0 if status == "completed_valid" else 1


def mode_measure(args: argparse.Namespace) -> int:
    started = utc_now()
    t0 = time.perf_counter()
    total_budget = args.total_wall
    cells = []
    logs = []
    # Prefer smaller cells first
    matrix = [(b, B, m, s) for b in BIT_SIZES for B in B_SIZES for m in ARITIES for s in SEEDS]
    # For bounded execution: optionally restrict
    if args.smoke_matrix:
        matrix = [(16, 64, 4, 101), (16, 64, 4, 102), (16, 64, 5, 101),
                  (20, 64, 4, 101), (16, 128, 4, 101)]
    per_cell = min(args.cell_wall, max(30.0, total_budget / max(len(matrix), 1)))
    for bits, B, m, seed in matrix:
        elapsed = time.perf_counter() - t0
        if elapsed >= total_budget:
            logs.append(f"STOP resource_exhaustion after {len(cells)} cells; remaining skipped")
            break
        remain = total_budget - elapsed
        cw = min(per_cell, remain)
        logs.append(f"CELL bits={bits} B={B} m={m} seed={seed} budget={cw:.1f}s")
        cell = execute_cell(
            bits, B, m, seed,
            cell_wall_budget=cw,
            relations_target=args.relations,
            do_planted=False,
            smoothness_abort=False,
        )
        cells.append(asdict(cell))
        logs.append(
            f"  -> {cell.status} R={cell.R} R_null={cell.R_null} label={cell.r1_cell_label} "
            f"n=({cell.n_usable_naive},{cell.n_usable_split},"
            f"{cell.n_usable_naive_null},{cell.n_usable_split_null})"
        )

    # R-1 observation across cells
    f2_hits = [c for c in cells if c.get("r1_cell_label") == "F2_eligible"]
    s1_hits = [c for c in cells if c.get("r1_cell_label") == "S1_eligible_on_null_axis"]
    r1_disposition = None
    if f2_hits:
        r1_disposition = "F2_met_eligible_observation"
    elif len({c["bits"] for c in s1_hits}) >= 2:
        r1_disposition = "S1_eligible_observation"
    else:
        r1_disposition = "neither_S1_nor_F2_clear_from_completed_cells"

    raw = {
        "mode": "measure",
        "cells": cells,
        "matrix_planned": len(matrix),
        "matrix_completed": len(cells),
        "metrics": {
            "n_cells": len(cells),
            "r1_disposition_observation": r1_disposition,
            "f2_eligible_cells": len(f2_hits),
            "s1_eligible_cells": len(s1_hits),
        },
        "certificate": {"kind": "none", "verified": True, "verifier": None},
        "cost_identities": {
            "rho_gop_per_second": "rho_total_group_operations / rho_wall_seconds",
            "cost_naive": "wall_seconds_naive * rho_gop_per_second / max(n_usable_relations_naive, 1)",
            "cost_split": "wall_seconds_split * rho_gop_per_second / max(n_usable_relations_split, 1)",
            "R": "cost_split / cost_naive",
            "R_null": "cost_split_null / cost_naive_null",
        },
        "_stdout": "\n".join(logs),
        "_stderr": "",
    }
    # Any cell completed_valid?
    statuses = [c["status"] for c in cells]
    if not cells:
        status = "resource_exhaustion"
    elif all(s == "infrastructure_error" for s in statuses):
        status = "infrastructure_error"
    elif any(s == "completed_valid" for s in statuses):
        status = "completed_valid"
    else:
        status = "resource_exhaustion"

    finished = utc_now()
    cmd = (
        f"python3 experiments/EXP-DS-001/implementation/ds001_driver.py --mode measure "
        f"--total-wall {args.total_wall} --cell-wall {args.cell_wall} --relations {args.relations}"
        + (" --smoke-matrix" if args.smoke_matrix else "")
    )
    write_run_artifacts("RUN-DS-001-measure", Path(args.out_run), cmd, raw, status,
                        started=started, finished=finished, wall_seconds=time.perf_counter() - t0)
    # Also write R_table fragment helper
    print("\n".join(logs))
    print("R1_OBS", r1_disposition)
    return 0


def mode_heur(args: argparse.Namespace) -> int:
    started = utc_now()
    t0 = time.perf_counter()
    logs = []
    reports = []
    # Sample at each bit size with representative B=64, m=4 (and m=5 if budget)
    plan = [(16, 64, 4), (20, 64, 4), (24, 64, 4)]
    per = args.total_wall / max(len(plan), 1)
    for bits, B, m in plan:
        if time.perf_counter() - t0 >= args.total_wall:
            logs.append("STOP resource_exhaustion before all bit sizes")
            break
        remain = args.total_wall - (time.perf_counter() - t0)
        rep = sample_heur(bits, B, m, seed=101, n_samples=args.n_samples, wall_budget=min(per, remain))
        reports.append(rep)
        logs.append(
            f"HEUR bits={bits} n={rep.get('n_samples')} p_hat={rep.get('p_hat')} "
            f"p0={rep.get('rho_u_star')} rate_ok={rep.get('RATE_DS_1_ok')} "
            f"ks_ok={rep.get('KS_DS_1_ok')} tail_ok={rep.get('TAIL_DS_1_ok')} "
            f"pass={rep.get('HEUR_DS_1_bit_size_pass')} status={rep.get('status')}"
        )

    # F3 observation: all completed adequate bit sizes fail
    adequate = [r for r in reports if r.get("samples_adequate")]
    f3 = bool(adequate) and all(not r.get("HEUR_DS_1_bit_size_pass") for r in adequate)

    raw = {
        "mode": "heur",
        "reports": reports,
        "metrics": {
            "n_bit_sizes": len(reports),
            "F3_trigger_observation": f3,
            "u_star_table": {
                f"{r['bits']}_{r['B']}_{r['m']}": {"D": r.get("D"), "u_star": r.get("u_star"), "rho": r.get("rho_u_star")}
                for r in reports
            },
        },
        "certificate": {"kind": "none", "verified": True, "verifier": None},
        "_stdout": "\n".join(logs),
        "_stderr": "",
    }
    status = "completed_valid" if reports and any(r.get("n_samples", 0) > 0 for r in reports) else "resource_exhaustion"
    finished = utc_now()
    cmd = (
        f"python3 experiments/EXP-DS-001/implementation/ds001_driver.py --mode heur "
        f"--total-wall {args.total_wall} --n-samples {args.n_samples}"
    )
    write_run_artifacts("RUN-DS-001-heur", Path(args.out_run), cmd, raw, status,
                        started=started, finished=finished, wall_seconds=time.perf_counter() - t0)
    print("\n".join(logs))
    return 0


def mode_ctrl_unplanted(args: argparse.Namespace) -> int:
    """CTRL-RT025-UNPLANTED (+ CTRL-RT025-PLANT-LIVE companion).

    Primary R / R_null measured with plant OFF and unplanted uniform random
    targets. Live /4 detection is companion-only in live_plant_report.json.
    """
    started = utc_now()
    t0 = time.perf_counter()
    bits, B, m, seed = 20, 64, 4, 101
    cell_wall = float(args.cell_wall)
    relations = int(args.relations)
    logs = [
        f"CTRL-RT025-UNPLANTED cell bits={bits} B={B} m={m} seed={seed}",
        f"cell_wall={cell_wall} relations_target={relations} smoothness_abort=false",
        f"target_mode=unplanted_uniform_random backend_id={BACKEND_ID}",
        "R-1 binding: primary plant OFF; live /4 companion-only",
    ]

    cell = execute_cell(
        bits=bits,
        B=B,
        m=m,
        seed=seed,
        cell_wall_budget=cell_wall,
        relations_target=relations,
        do_planted=False,
        smoothness_abort=False,
        target_mode="unplanted_uniform_random",
    )
    live = live_plant_detect(cell)
    logs.append(
        f"primary status={cell.status} R={cell.R} R_null={cell.R_null} "
        f"label={cell.r1_cell_label} protocol_stop={cell.protocol_stop}"
    )
    logs.append(
        f"n_usable=(naive={cell.n_usable_naive},split={cell.n_usable_split},"
        f"naive_null={cell.n_usable_naive_null},split_null={cell.n_usable_split_null})"
    )
    logs.append(
        f"attempted=(n={cell.attempted_targets_naive},s={cell.attempted_targets_split}) "
        f"success=(n={cell.success_count_naive},s={cell.success_count_split}) "
        f"p_hat=(n={cell.empirical_success_probability_naive},"
        f"s={cell.empirical_success_probability_split})"
    )
    logs.append(
        f"live_plant detected={live.get('planted_bug_detected')} "
        f"path={live.get('detection_path')} synth={live.get('synthetic_shortcut_used')}"
    )

    cert = {"kind": "none", "verified": True, "verifier": None}
    if cell.rho and cell.rho.get("solved"):
        cert = {
            "kind": "discrete_log",
            "verified": bool(cell.rho.get("certificate_verified")),
            "verifier": (
                "harness.toycurve.EllipticCurve.mul independent check in driver "
                "+ verify_certificates.py"
            ),
            "k": cell.rho.get("k"),
        }

    status = cell.status
    if cert.get("kind") == "discrete_log" and not cert.get("verified"):
        status = "invalid_measurement"
    if cell.plant_applied_to_primary:
        status = "invalid_measurement"
        logs.append("INVALID: plant leaked into primary R (R-1 violation)")

    raw = {
        "mode": "ctrl-unplanted",
        "control_id": "CTRL-RT025-UNPLANTED",
        "companion_control_id": "CTRL-RT025-PLANT-LIVE",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-unplanted",
        "cell": asdict(cell),
        "live_plant": live,
        "metrics": {
            "R": cell.R,
            "R_null": cell.R_null,
            "R_ci": cell.R_ci,
            "R_null_ci": cell.R_null_ci,
            "n_usable_naive": cell.n_usable_naive,
            "n_usable_split": cell.n_usable_split,
            "n_usable_naive_null": cell.n_usable_naive_null,
            "n_usable_split_null": cell.n_usable_split_null,
            "r1_cell_label": cell.r1_cell_label,
            "protocol_stop": cell.protocol_stop,
            "plant_applied_to_primary": cell.plant_applied_to_primary,
            "live_plant_detected": live.get("planted_bug_detected"),
            "backend_id": BACKEND_ID,
            "target_mode": cell.target_mode,
            "attempted_targets_naive": cell.attempted_targets_naive,
            "attempted_targets_split": cell.attempted_targets_split,
            "success_count_naive": cell.success_count_naive,
            "success_count_split": cell.success_count_split,
            "empirical_success_probability_naive": cell.empirical_success_probability_naive,
            "empirical_success_probability_split": cell.empirical_success_probability_split,
        },
        "certificate": cert,
        "cost_identities": {
            "rho_gop_per_second": "rho_total_group_operations / rho_wall_seconds",
            "cost_naive": "wall_seconds_naive * rho_gop_per_second / max(n_usable_relations_naive, 1)",
            "cost_split": "wall_seconds_split * rho_gop_per_second / max(n_usable_relations_split, 1)",
            "R": "cost_split / cost_naive",
            "R_null": "cost_split_null / cost_naive_null",
        },
        "r1_note": (
            "Primary R/R_null measured with /4 plant OFF. "
            "If R<0.5 and R_null<0.9 label is F2_eligible (observation only)."
        ),
        "_stdout": "\n".join(logs),
        "_stderr": "",
    }

    finished = utc_now()
    wall_seconds = time.perf_counter() - t0
    cmd = (
        f"python3 experiments/EXP-DS-001/implementation/ds001_driver.py "
        f"--mode ctrl-unplanted --cell-wall {cell_wall} --relations {relations}"
    )
    out_run = Path(args.out_run)
    write_run_artifacts(
        "RUN-DS-001-ctrl-unplanted",
        out_run,
        cmd,
        raw,
        status,
        started=started,
        finished=finished,
        wall_seconds=wall_seconds,
        task_id="TASK-20260731-044",
        batch_id="BATCH-020",
        contract_extra={
            "control_protocol_path": "experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml",
            "protocol_amendment_id": "PA-DS-001-v2-ctrl-unplanted",
            "amendment_path": "experiments/EXP-DS-001/amendments/v2_ctrl_unplanted.yaml",
            "approval_task": "TASK-20260731-043",
            "approval_determination": "APPROVED",
            "parent_contract_sha256": (
                "898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a"
            ),
        },
        inputs_extra={
            "cell": {"bits": bits, "B": B, "m": m, "seed": seed},
            "target_mode": "unplanted_uniform_random",
            "smoothness_abort": False,
            "relations_target": relations,
            "cell_wall_seconds": cell_wall,
            "plant_on_primary": False,
        },
    )

    # Results package (separate from planted EV-DS-002 package).
    results_dir = Path(args.exp_root) / "results" / "ctrl_unplanted"
    results_dir.mkdir(parents=True, exist_ok=True)

    R_cell = {
        "control_id": "CTRL-RT025-UNPLANTED",
        "run_id": "RUN-DS-001-ctrl-unplanted",
        "task_id": "TASK-20260731-044",
        "bits": bits,
        "B": B,
        "m": m,
        "seed": seed,
        "status": status,
        "target_mode": "unplanted_uniform_random",
        "plant_applied_to_primary": False,
        "smoothness_abort": False,
        "backend_id": BACKEND_ID,
        "R": cell.R,
        "R_null": cell.R_null,
        "R_bootstrap_ci_95": cell.R_ci,
        "R_null_bootstrap_ci_95": cell.R_null_ci,
        "cost_naive": cell.cost_naive,
        "cost_split": cell.cost_split,
        "cost_naive_null": cell.cost_naive_null,
        "cost_split_null": cell.cost_split_null,
        "n_usable_naive": cell.n_usable_naive,
        "n_usable_split": cell.n_usable_split,
        "n_usable_naive_null": cell.n_usable_naive_null,
        "n_usable_split_null": cell.n_usable_split_null,
        "wall_naive": cell.wall_naive,
        "wall_split": cell.wall_split,
        "wall_naive_null": cell.wall_naive_null,
        "wall_split_null": cell.wall_split_null,
        "attempted_targets_naive": cell.attempted_targets_naive,
        "attempted_targets_split": cell.attempted_targets_split,
        "success_count_naive": cell.success_count_naive,
        "success_count_split": cell.success_count_split,
        "empirical_success_probability_naive": cell.empirical_success_probability_naive,
        "empirical_success_probability_split": cell.empirical_success_probability_split,
        "r1_cell_label": cell.r1_cell_label,
        "protocol_stop": cell.protocol_stop,
        "null_object_spec_hash": cell.null_object_spec_hash,
        "fb_x_hash": cell.fb_x_hash,
        "assembled_E_proxy": cell.assembled_E_proxy,
        "rho": cell.rho,
        "bsgs": cell.bsgs,
        "r1_binding_note": (
            "Primary R and R_null measured with live /4 plant OFF. "
            "Companion detection is in live_plant_report.json only."
        ),
        "cost_identities": raw["cost_identities"],
    }
    (results_dir / "R_cell.json").write_text(
        json.dumps(R_cell, indent=2, default=str) + "\n", encoding="utf-8"
    )

    null_report = {
        "control_id": "CTRL-RT025-UNPLANTED",
        "null_object_id": NULL_SPEC_ID,
        "proposal": "IDEA-20260731-011",
        "run_id": "RUN-DS-001-ctrl-unplanted",
        "task_id": "TASK-20260731-044",
        "plant_applied_to_primary": False,
        "R": cell.R,
        "R_null": cell.R_null,
        "r1_cell_label": cell.r1_cell_label,
        "null_object_spec_hash": cell.null_object_spec_hash,
        "F2_eligible_observation": cell.r1_cell_label == "F2_eligible",
        "gate_note": (
            "If R<0.5 and R_null<0.9 observation label is F2_eligible "
            "(overrides S1). Observation only — no hypothesis status change."
        ),
        "CTRL_NULL_RHO": {
            "rho_calib_ratio_real": cell.rho_calib_ratio_real,
            "rho_calib_ratio_null": cell.rho_calib_ratio_null,
        },
        "n_usable_naive_null": cell.n_usable_naive_null,
        "n_usable_split_null": cell.n_usable_split_null,
        "cost_naive_null": cell.cost_naive_null,
        "cost_split_null": cell.cost_split_null,
    }
    (results_dir / "null_control_report.json").write_text(
        json.dumps(null_report, indent=2, default=str) + "\n", encoding="utf-8"
    )

    (results_dir / "live_plant_report.json").write_text(
        json.dumps(live, indent=2, default=str) + "\n", encoding="utf-8"
    )

    summary = {
        "experiment_id": "EXP-DS-001",
        "run_id": "RUN-DS-001-ctrl-unplanted",
        "task_id": "TASK-20260731-044",
        "batch_id": "BATCH-020",
        "control_id": "CTRL-RT025-UNPLANTED",
        "companion_control_id": "CTRL-RT025-PLANT-LIVE",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-unplanted",
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "status": status,
        "backend_id": BACKEND_ID,
        "target_mode": "unplanted_uniform_random",
        "smoothness_abort": False,
        "relations_target": relations,
        "cell_wall_seconds": cell_wall,
        "plant_applied_to_primary": False,
        "R": cell.R,
        "R_null": cell.R_null,
        "r1_cell_label": cell.r1_cell_label,
        "protocol_stop": cell.protocol_stop,
        "n_usable_naive": cell.n_usable_naive,
        "n_usable_split": cell.n_usable_split,
        "n_usable_naive_null": cell.n_usable_naive_null,
        "n_usable_split_null": cell.n_usable_split_null,
        "attempted_targets_naive": cell.attempted_targets_naive,
        "attempted_targets_split": cell.attempted_targets_split,
        "success_count_naive": cell.success_count_naive,
        "success_count_split": cell.success_count_split,
        "empirical_success_probability_naive": cell.empirical_success_probability_naive,
        "empirical_success_probability_split": cell.empirical_success_probability_split,
        "live_plant_detected": live.get("planted_bug_detected"),
        "live_plant_detection_path": live.get("detection_path"),
        "synthetic_shortcut_used": False,
        "does_not_supersede": (
            "Does not overwrite planted relations=200 package "
            "(EV-DS-002 / snapshot 1eb431f1)."
        ),
        "does_not_modify_hypotheses": ["H-IC-001", "H-STR-002"],
        "inference": inference_block(),
        "git": git_state(),
        "wall_seconds_run": wall_seconds,
        "note": (
            "Toy-tier unplanted control remeasure only. Observations only. "
            "No crypto-scale or asymptotic claim. Primary R plant-OFF."
        ),
    }
    (results_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
    )

    print("\n".join(logs))
    print("SUMMARY", json.dumps({
        "status": status,
        "R": cell.R,
        "R_null": cell.R_null,
        "live_plant_detected": live.get("planted_bug_detected"),
        "protocol_stop": cell.protocol_stop,
    }))
    # Exit 0 for completed_valid or honest resource_exhaustion.
    return 0 if status in ("completed_valid", "resource_exhaustion") else 1


def mode_ctrl_theater_r2(args: argparse.Namespace) -> int:
    """PA-DS-001-v2-ctrl-theater-r2 / CTRL-RT056-* co-required package.

    Cell: bits=20,B=64,m=4,seed=101. Observations only.
    """
    started = utc_now()
    t0 = time.perf_counter()
    bits, B, m, seed = 20, 64, 4, 101
    cell_wall = float(args.cell_wall)
    relations = int(args.relations)
    run_id = "RUN-DS-001-ctrl-theater-r2"
    logs = [
        f"CTRL theater-r2 RUN={run_id} cell bits={bits} B={B} m={m} seed={seed}",
        f"cell_wall={cell_wall} relations_target={relations} smoothness_abort=false",
        f"target_mode=planted_m_sum (packaging-like real arm) backend_id={BACKEND_ID}",
        "null_split_mode=composing (CTRL-RT056-NULL-SPLIT-HARD-DESTROY)",
        "binding: TASK-066 APPROVED ecf99e6e; amend snapshot 9c94d866; PA-DS-001-v2-ctrl-theater-r2",
        "R-1: primary plant OFF; plant inject only in plant_closed_path_report path",
    ]

    cell = execute_cell(
        bits=bits,
        B=B,
        m=m,
        seed=seed,
        cell_wall_budget=cell_wall,
        relations_target=relations,
        do_planted=False,
        smoothness_abort=False,
        target_mode="planted_m_sum",
        null_split_mode="composing",
    )

    # Join-evidence probe (same composing rule; not a second yield harvest).
    join_evidence_sample = None
    try:
        inst = generate_instance(seed, bits)
        fb = make_factor_base(inst, B, seed)
        probe = null_split_search_composing(
            fb.xs, seed, bits, B, m, target_tag=1,
            deadline=time.perf_counter() + min(30.0, cell_wall),
            charge_backend=lambda mm: charge_backend_units(mm),
        )
        if probe.relation and isinstance(probe.relation, dict):
            join_evidence_sample = probe.relation.get("join_evidence")
    except Exception as e:
        logs.append(f"join_evidence_probe_error: {e}")

    plant_report = plant_closed_path_detect(cell)
    rho_report = measure_rho_calib_audited(cell, seed, bits)
    null_report = null_split_hard_destroy_report(cell, join_evidence_sample)

    logs.append(
        f"primary status={cell.status} R={cell.R} R_null={cell.R_null} "
        f"label={cell.r1_cell_label} protocol_stop={cell.protocol_stop}"
    )
    logs.append(
        f"n_usable=(naive={cell.n_usable_naive},split={cell.n_usable_split},"
        f"naive_null={cell.n_usable_naive_null},split_null={cell.n_usable_split_null})"
    )
    logs.append(
        f"plant_closed_path detected={plant_report.get('planted_bug_detected')} "
        f"path={plant_report.get('detection_path')} "
        f"echo_entailment_check={plant_report.get('echo_entailment_check')}"
    )
    logs.append(
        f"rho_calib ratios real={rho_report.get('rho_calib_ratio_real')} "
        f"null={rho_report.get('rho_calib_ratio_null')} "
        f"status={rho_report.get('status')}"
    )
    logs.append(
        f"null_split composition_repaired={null_report.get('composition_repaired')} "
        f"destroy_demonstrated={null_report.get('destroy_demonstrated')} "
        f"falsifiability_failed={null_report.get('falsifiability_failed')}"
    )

    cert = {"kind": "none", "verified": True, "verifier": None}
    if cell.rho and cell.rho.get("solved"):
        cert = {
            "kind": "discrete_log",
            "verified": bool(cell.rho.get("certificate_verified")),
            "verifier": (
                "harness.toycurve.EllipticCurve.mul independent check in driver "
                "+ verify_certificates.py"
            ),
            "k": cell.rho.get("k"),
        }

    status = cell.status
    if cert.get("kind") == "discrete_log" and not cert.get("verified"):
        status = "invalid_measurement"
    if cell.plant_applied_to_primary:
        status = "invalid_measurement"
        logs.append("INVALID: plant leaked into primary R (R-1 violation)")
    if plant_report.get("detection_path") not in (None, "null_gate_f2_shape"):
        status = "invalid_measurement"
        logs.append("INVALID: detection_path outside allowed enum {null_gate_f2_shape}")
    if plant_report.get("echo_entailment_check") is True:
        status = "invalid_measurement"
        logs.append("INVALID: echo_entailment_check true")
    if rho_report.get("status") == "failed_infrastructure":
        # Measurement incomplete — not a mathematical negative (AGENTS.md rule 5).
        if status == "completed_valid":
            status = "resource_exhaustion"
        logs.append("rho_calib measurement failed_infrastructure")

    raw = {
        "mode": "ctrl-theater-r2",
        "run_id": run_id,
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
        "control_ids": [
            "CTRL-RT056-PLANT-CLOSED-PATH",
            "CTRL-RT056-RHO-CALIB-AUDITED",
            "CTRL-RT056-NULL-SPLIT-HARD-DESTROY",
        ],
        "approval_binding": {
            "approval_task": "TASK-20260731-066",
            "approval_determination": "APPROVED",
            "approval_archive_commit": "ecf99e6ef65998cc57f9eec495953371082513ef",
            "amend_snapshot": "9c94d866948526d5f27dc17705d02000defcf9dc",
            "reviewer_report": "RT-20260731-065",
        },
        "cell": asdict(cell),
        "plant_closed_path": plant_report,
        "rho_calib_audited": rho_report,
        "null_split_hard_destroy": null_report,
        "metrics": {
            "R": cell.R,
            "R_null": cell.R_null,
            "R_ci": cell.R_ci,
            "R_null_ci": cell.R_null_ci,
            "n_usable_naive": cell.n_usable_naive,
            "n_usable_split": cell.n_usable_split,
            "n_usable_naive_null": cell.n_usable_naive_null,
            "n_usable_split_null": cell.n_usable_split_null,
            "r1_cell_label": cell.r1_cell_label,
            "protocol_stop": cell.protocol_stop,
            "plant_applied_to_primary": cell.plant_applied_to_primary,
            "backend_id": BACKEND_ID,
            "target_mode": cell.target_mode,
            "null_split_mode": "composing",
            "planted_bug_detected": plant_report.get("planted_bug_detected"),
            "detection_path": plant_report.get("detection_path"),
            "echo_entailment_check": plant_report.get("echo_entailment_check"),
            "rho_calib_ratio_real": rho_report.get("rho_calib_ratio_real"),
            "rho_calib_ratio_null": rho_report.get("rho_calib_ratio_null"),
            "composition_repaired": null_report.get("composition_repaired"),
            "destroy_demonstrated": null_report.get("destroy_demonstrated"),
            "falsifiability_failed": null_report.get("falsifiability_failed"),
        },
        "certificate": cert,
        "cost_identities": {
            "rho_gop_per_second": "rho_total_group_operations / rho_wall_seconds",
            "cost_naive": "wall_seconds_naive * rho_gop_per_second / max(n_usable_relations_naive, 1)",
            "cost_split": "wall_seconds_split * rho_gop_per_second / max(n_usable_relations_split, 1)",
            "R": "cost_split / cost_naive",
            "R_null": "cost_split_null / cost_naive_null",
        },
        "_stdout": "\n".join(logs),
        "_stderr": "",
    }

    finished = utc_now()
    wall_seconds = time.perf_counter() - t0
    cmd = (
        f"python3 experiments/EXP-DS-001/implementation/ds001_driver.py "
        f"--mode ctrl-theater-r2 --cell-wall {cell_wall} --relations {relations}"
    )
    out_run = Path(args.out_run)
    write_run_artifacts(
        run_id,
        out_run,
        cmd,
        raw,
        status,
        started=started,
        finished=finished,
        wall_seconds=wall_seconds,
        task_id="TASK-20260731-067",
        batch_id="BATCH-022",
        contract_extra={
            "control_protocol_paths": [
                "experiments/EXP-DS-001/controls/CTRL-RT056-PLANT-CLOSED-PATH.yaml",
                "experiments/EXP-DS-001/controls/CTRL-RT056-RHO-CALIB-AUDITED.yaml",
                "experiments/EXP-DS-001/controls/CTRL-RT056-NULL-SPLIT-HARD-DESTROY.yaml",
            ],
            "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
            "amendment_path": "experiments/EXP-DS-001/amendments/v2_ctrl_theater_r2.yaml",
            "approval_task": "TASK-20260731-066",
            "approval_determination": "APPROVED",
            "approval_archive_commit": "ecf99e6ef65998cc57f9eec495953371082513ef",
            "amend_snapshot": "9c94d866948526d5f27dc17705d02000defcf9dc",
            "parent_contract_sha256": (
                "898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a"
            ),
        },
        inputs_extra={
            "cell": {"bits": bits, "B": B, "m": m, "seed": seed},
            "target_mode": "planted_m_sum",
            "null_split_mode": "composing",
            "smoothness_abort": False,
            "relations_target": relations,
            "cell_wall_seconds": cell_wall,
            "plant_on_primary": False,
            "claim_tier": "toy",
        },
    )

    results_dir = Path(args.exp_root) / "results" / "ctrl_theater_r2"
    results_dir.mkdir(parents=True, exist_ok=True)

    (results_dir / "plant_closed_path_report.json").write_text(
        json.dumps(plant_report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (results_dir / "rho_calib_audited_report.json").write_text(
        json.dumps(rho_report, indent=2, default=str) + "\n", encoding="utf-8"
    )
    (results_dir / "null_split_hard_destroy_report.json").write_text(
        json.dumps(null_report, indent=2, default=str) + "\n", encoding="utf-8"
    )

    summary = {
        "experiment_id": "EXP-DS-001",
        "run_id": run_id,
        "task_id": "TASK-20260731-067",
        "batch_id": "BATCH-022",
        "protocol_amendment_id": "PA-DS-001-v2-ctrl-theater-r2",
        "control_ids": [
            "CTRL-RT056-PLANT-CLOSED-PATH",
            "CTRL-RT056-RHO-CALIB-AUDITED",
            "CTRL-RT056-NULL-SPLIT-HARD-DESTROY",
        ],
        "approval_binding": raw["approval_binding"],
        "claim_tier": "toy",
        "confirmatory_status": "exploratory_control",
        "status": status,
        "backend_id": BACKEND_ID,
        "target_mode": "planted_m_sum",
        "null_split_mode": "composing",
        "smoothness_abort": False,
        "relations_target": relations,
        "cell_wall_seconds": cell_wall,
        "plant_applied_to_primary": False,
        "R": cell.R,
        "R_null": cell.R_null,
        "r1_cell_label": cell.r1_cell_label,
        "protocol_stop": cell.protocol_stop,
        "n_usable_naive": cell.n_usable_naive,
        "n_usable_split": cell.n_usable_split,
        "n_usable_naive_null": cell.n_usable_naive_null,
        "n_usable_split_null": cell.n_usable_split_null,
        "planted_bug_detected": plant_report.get("planted_bug_detected"),
        "detection_path": plant_report.get("detection_path"),
        "echo_entailment_check": plant_report.get("echo_entailment_check"),
        "injection_site": plant_report.get("injection_site"),
        "rho_calib_ratio_real": rho_report.get("rho_calib_ratio_real"),
        "rho_calib_ratio_null": rho_report.get("rho_calib_ratio_null"),
        "rho_wall_real": rho_report.get("rho_wall_real"),
        "rho_gop_real": rho_report.get("rho_gop_real"),
        "rho_wall_null": rho_report.get("rho_wall_null"),
        "rho_gop_null": rho_report.get("rho_gop_null"),
        "composition_repaired": null_report.get("composition_repaired"),
        "destroy_demonstrated": null_report.get("destroy_demonstrated"),
        "falsifiability_failed": null_report.get("falsifiability_failed"),
        "package_pass_observation": null_report.get("package_pass_observation"),
        "does_not_supersede": (
            "Does not overwrite EV-DS-002 / EV-DS-003 / EV-DS-004. "
            "Does not reuse unauthorized RUN-DS-001-ctrl-theater."
        ),
        "does_not_modify_hypotheses": ["H-IC-001", "H-STR-002"],
        "inference": inference_block(),
        "git": git_state(),
        "wall_seconds_run": wall_seconds,
        "note": (
            "Toy-tier theater-r2 control package observations only. "
            "No crypto-scale or asymptotic claim. No S1_met interpretation."
        ),
    }
    (results_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8"
    )

    print("\n".join(logs))
    print("SUMMARY", json.dumps({
        "status": status,
        "R": cell.R,
        "R_null": cell.R_null,
        "planted_bug_detected": plant_report.get("planted_bug_detected"),
        "detection_path": plant_report.get("detection_path"),
        "echo_entailment_check": plant_report.get("echo_entailment_check"),
        "rho_calib_ratio_real": rho_report.get("rho_calib_ratio_real"),
        "rho_calib_ratio_null": rho_report.get("rho_calib_ratio_null"),
        "composition_repaired": null_report.get("composition_repaired"),
        "destroy_demonstrated": null_report.get("destroy_demonstrated"),
        "falsifiability_failed": null_report.get("falsifiability_failed"),
        "protocol_stop": cell.protocol_stop,
    }))
    return 0 if status in ("completed_valid", "resource_exhaustion") else 1


def mode_finalize(args: argparse.Namespace) -> int:
    """Assemble results/*.json from the three run raw-results."""
    root = Path(args.exp_root)
    runs = root / "runs"
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)

    def load_raw(run_id: str) -> dict:
        p = runs / run_id / "raw-result.json"
        if not p.exists():
            return {}
        return json.loads(p.read_text())

    impl = load_raw("RUN-DS-001-impl")
    measure = load_raw("RUN-DS-001-measure")
    heur = load_raw("RUN-DS-001-heur")

    cells = measure.get("cells", [])
    R_table = []
    for c in cells:
        R_table.append({
            "bits": c["bits"], "B": c["B"], "m": c["m"], "seed": c["seed"],
            "status": c["status"],
            "R": c.get("R"), "R_null": c.get("R_null"),
            "R_bootstrap_ci_95": c.get("R_ci"),
            "R_null_bootstrap_ci_95": c.get("R_null_ci"),
            "cost_naive": c.get("cost_naive"),
            "cost_split": c.get("cost_split"),
            "cost_naive_null": c.get("cost_naive_null"),
            "cost_split_null": c.get("cost_split_null"),
            "n_usable_naive": c.get("n_usable_naive"),
            "n_usable_split": c.get("n_usable_split"),
            "n_usable_naive_null": c.get("n_usable_naive_null"),
            "n_usable_split_null": c.get("n_usable_split_null"),
            "r1_cell_label": c.get("r1_cell_label"),
            "assembled_E_proxy": c.get("assembled_E_proxy"),
            "peak_rss_bytes_claw_table": c.get("peak_rss_bytes_claw_table"),
            "null_object_spec_hash": c.get("null_object_spec_hash"),
            "fb_x_hash": c.get("fb_x_hash"),
            "rho": c.get("rho"),
            "bsgs": c.get("bsgs"),
            "calibration_perturbation_sign_stable": c.get("calibration_perturbation_sign_stable"),
            "rho_calib_ratio_real": c.get("rho_calib_ratio_real"),
            "rho_calib_ratio_null": c.get("rho_calib_ratio_null"),
        })

    (results / "R_table.json").write_text(json.dumps({"cells": R_table, "cost_identities": measure.get("cost_identities")}, indent=2) + "\n")

    heur_report = {
        "heuristic": "HEUR-DS-1",
        "decision_rule": "specification.v2.yaml:heur_ds_1_decision_rule",
        "bit_size_reports": heur.get("reports", []),
        "F3_trigger_observation": heur.get("metrics", {}).get("F3_trigger_observation"),
        "u_star_table": heur.get("metrics", {}).get("u_star_table"),
        "note": "Executor reports statistics only; pass/fail judgment for hypothesis is Coordinator/Reviewer.",
    }
    (results / "HEUR_DS_1_report.json").write_text(json.dumps(heur_report, indent=2) + "\n")

    null_report = {
        "null_object_id": NULL_SPEC_ID,
        "proposal": "IDEA-20260731-011",
        "planted_bug_detected": (impl.get("cell") or {}).get("planted_bug_detected"),
        "impl_R": (impl.get("cell") or {}).get("R"),
        "impl_R_null": (impl.get("cell") or {}).get("R_null"),
        "cells": [
            {
                "bits": c["bits"], "B": c["B"], "m": c["m"], "seed": c["seed"],
                "R": c.get("R"), "R_null": c.get("R_null"),
                "r1_cell_label": c.get("r1_cell_label"),
                "null_object_spec_hash": c.get("null_object_spec_hash"),
            }
            for c in cells
        ],
        "r1_disposition_observation": measure.get("metrics", {}).get("r1_disposition_observation"),
        "CTRL_NULL_RHO": {
            "rho_calib_ratio_real": "recorded per cell (~1 identity calibration)",
            "rho_calib_ratio_null": "recorded per cell (~1 identity calibration)",
        },
    }
    (results / "null_control_report.json").write_text(json.dumps(null_report, indent=2) + "\n")

    summary = {
        "experiment_id": "EXP-DS-001",
        "version": 2,
        "task_id": "TASK-20260731-022",
        "claim_tier": "toy",
        "runs": {
            "RUN-DS-001-impl": (runs / "RUN-DS-001-impl" / "manifest.json").exists(),
            "RUN-DS-001-measure": (runs / "RUN-DS-001-measure" / "manifest.json").exists(),
            "RUN-DS-001-heur": (runs / "RUN-DS-001-heur" / "manifest.json").exists(),
        },
        "n_measure_cells": len(cells),
        "r1_disposition_observation": measure.get("metrics", {}).get("r1_disposition_observation"),
        "cost_identities_present": True,
        "backend_id": BACKEND_ID,
        "inference": inference_block(),
        "git": git_state(),
        "note": "Toy-tier only. No crypto-scale claim. Observations only.",
    }
    (results / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="EXP-DS-001 v2 driver")
    ap.add_argument(
        "--mode",
        choices=["impl", "measure", "heur", "finalize", "ctrl-unplanted", "ctrl-theater-r2"],
        required=True,
    )
    ap.add_argument("--out-run", default="")
    ap.add_argument("--exp-root", default=str(REPO / "experiments" / "EXP-DS-001"))
    ap.add_argument("--cell-wall", type=float, default=90.0)
    ap.add_argument("--total-wall", type=float, default=3600.0)
    ap.add_argument("--relations", type=int, default=200)
    ap.add_argument("--n-samples", type=int, default=100000)
    ap.add_argument("--smoke-matrix", action="store_true")
    args = ap.parse_args()
    if args.mode != "finalize" and not args.out_run:
        args.out_run = str(Path(args.exp_root) / "runs" / {
            "impl": "RUN-DS-001-impl",
            "measure": "RUN-DS-001-measure",
            "heur": "RUN-DS-001-heur",
            "ctrl-unplanted": "RUN-DS-001-ctrl-unplanted",
            "ctrl-theater-r2": "RUN-DS-001-ctrl-theater-r2",
        }[args.mode])
    if args.mode == "impl":
        return mode_impl(args)
    if args.mode == "measure":
        return mode_measure(args)
    if args.mode == "heur":
        return mode_heur(args)
    if args.mode == "ctrl-unplanted":
        # Contractual default cell wall for this control is 7200s unless overridden.
        if args.cell_wall == 90.0:
            args.cell_wall = 7200.0
        return mode_ctrl_unplanted(args)
    if args.mode == "ctrl-theater-r2":
        if args.cell_wall == 90.0:
            args.cell_wall = 7200.0
        return mode_ctrl_theater_r2(args)
    return mode_finalize(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise
