"""EXP-IT-001 v3 helpers (pure Python): hashes, F_hit, null graph, KS/TAIL.

Sage-facing driver imports these for frozen decision-rule arithmetic that must
match the Validator recomputation. No isogeny algebra here.
"""
from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any


D_REG = 3
H_MAX_COFACTOR = 256
SEED_DENSITY = 2026073199
SEEDS = [2026073101, 2026073102, 2026073103]
BITS = [20, 24, 28]
C_ISO_ELL = lambda ell: 4 * int(ell)

NULL_ID = "NULL-IT-ISOGENY-TRANSFER"
NULL_CONSTRUCTION_ID = "NULL-IT-ISOGENY-TRANSFER-v2"
NULL_NEIGHBOR_ID = "NULL-IT-NEIGHBOR-v1"
PLANT_DETECTION_ID = "CTRL-NULL-IT-PLANT-v3"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_int(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def be_u64(n: int) -> bytes:
    return int(n).to_bytes(8, "big", signed=False)


def be_int(n: int, length: int | None = None) -> bytes:
    n = int(n)
    if n < 0:
        raise ValueError("be_int requires non-negative")
    if length is None:
        length = max(1, (n.bit_length() + 7) // 8)
    return n.to_bytes(length, "big", signed=False)


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def density_universe_spec_hash() -> str:
    obj = {
        "id": "U_IT_ORDINARY_PRIME_ORDER",
        "instance_N_map_id": "N_MAP-IT-001-v3",
        "h_max": H_MAX_COFACTOR,
        "bits": BITS,
        "unique_N_rule_id": "min_prime_N_star",
        "p_bits_selection_id": "smallest_p",
    }
    return sha256_hex(canonical_json(obj))


def null_object_spec_hash(rho_special_by_bits: dict[str, float]) -> str:
    obj = {
        "id": NULL_ID,
        "construction_id": NULL_CONSTRUCTION_ID,
        "neighbor_algorithm_id": NULL_NEIGHBOR_ID,
        "d": D_REG,
        "rho_special_by_bits": {str(k): float(v) for k, v in sorted(rho_special_by_bits.items(), key=lambda kv: int(kv[0]))},
        "c_iso_schedule": "4*ell",
        "R_null_identity": "(C_path_null+C_special_null+C_pullback_null)/matched_rho",
        "gate_rule": "R_xfer<0.7 => R_null>=0.95 else artifact",
        "plant_detection_id": PLANT_DETECTION_ID,
    }
    return sha256_hex(canonical_json(obj))


def ball_size(h: int, d: int = D_REG) -> int:
    h = int(h)
    d = int(d)
    if h <= 0:
        return 1
    if d == 2:
        return 1 + 2 * h
    return 1 + d * (((d - 1) ** h - 1) // (d - 2))


def F_hit(h: int, rho: float, d: int = D_REG) -> float:
    if h < 0:
        return 0.0
    rho = float(rho)
    if rho <= 0:
        rho = 1e-300
    if rho > 1:
        rho = 1.0
    return 1.0 - (1.0 - rho) ** ball_size(h, d)


def F_hit_table(hops_max: int, rho: float, d: int = D_REG) -> list[dict[str, float | int]]:
    return [{"h": h, "F_hit": F_hit(h, rho, d)} for h in range(0, int(hops_max) + 1)]


def hops_max_for_N(N: int) -> int:
    return int(math.floor(math.log2(N) / 2.0))


def matched_rho(N: int) -> float:
    return 0.886 * math.sqrt(float(N))


def matched_bsgs(N: int) -> int:
    return 2 * int(math.ceil(math.sqrt(float(N))))


def C_special_anomalous(N: int) -> int:
    return int(math.ceil(20 * (math.log2(N) ** 2)))


def C_special_MOV(p: int, k: int) -> int:
    return int(math.ceil(0.886 * math.sqrt(float(p) ** int(k))))


def C_special_WD(N: int, n: int) -> int:
    return int(math.ceil(0.886 * (float(N) ** (1.0 - 1.0 / float(n)))))


def C_pullback(N: int, deg_composite: int) -> int:
    return int(math.ceil(math.log2(N)) * int(deg_composite))


def bitlength(n: int) -> int:
    return int(n).bit_length()


def unique_N_star(order: int, bits: int, h_max: int = H_MAX_COFACTOR) -> tuple[int, int] | None:
    """Return (N*, h*) under min-prime N* rule, or None if excluded."""
    cand: list[int] = []
    # Factor-aware scan: try cofactors 1..h_max
    for h in range(1, h_max + 1):
        if order % h != 0:
            continue
        N = order // h
        if bitlength(N) == bits and _is_probable_prime(N):
            cand.append(N)
    if not cand:
        return None
    Nstar = min(cand)
    return Nstar, order // Nstar


def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    # deterministic Miller-Rabin for 64-bit
    if n < 2**64:
        return _miller_rabin(n, [2, 3, 5, 7, 11, 13, 23])
    return _miller_rabin(n, [2, 3, 5, 7, 11, 13, 23, 29, 31, 37])


def _miller_rabin(n: int, bases: list[int]) -> bool:
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        skip = False
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                skip = True
                break
        if skip:
            continue
        return False
    return True


def ks_statistic(samples: list[int], rho: float, d: int = D_REG) -> float:
    """One-sample KS vs discrete CDF F_hit on integer hops."""
    if not samples:
        return float("nan")
    xs = sorted(int(x) for x in samples)
    n = len(xs)
    dstat = 0.0
    # Evaluate at sample points and just below
    for i, x in enumerate(xs):
        Fn = (i + 1) / n
        F = F_hit(x, rho, d)
        dstat = max(dstat, abs(Fn - F))
        Fn_prev = i / n
        F_prev = F_hit(x - 1, rho, d)
        dstat = max(dstat, abs(Fn_prev - F_prev))
    return float(dstat)


def ks_threshold(n: int) -> float:
    if n <= 0:
        return float("inf")
    return max(0.05, 1.63 / math.sqrt(float(n)))


def tail_pass(samples: list[int], rho: float, d: int = D_REG) -> tuple[bool, dict[str, Any]]:
    if not samples:
        return False, {"reason": "no_uncensored_samples"}
    h_ext = min(int(x) for x in samples)
    p_ext = F_hit(h_ext, rho, d) - F_hit(h_ext - 1, rho, d)
    n = len(samples)
    ok = (p_ext * n) >= 1.0
    return ok, {"h_ext": h_ext, "p_ext": p_ext, "n": n, "p_ext_times_n": p_ext * n}


# ---- NULL-IT-NEIGHBOR-v1 -------------------------------------------------

def null_seed(instance_seed: int, Nstar: int) -> bytes:
    return hashlib.sha256(
        b"NULL-IT-ISOGENY-TRANSFER" + be_int(instance_seed) + be_int(Nstar)
    ).digest()


def null_graph_params(null_seed_bytes: bytes, Nstar: int) -> dict[str, Any]:
    hops_max = hops_max_for_N(Nstar)
    ball_bound = 1 + 3 * ((2**hops_max) - 1)
    m = max(2, int(math.ceil(math.log2(ball_bound))))
    M = 2**m
    offs: list[int] = []
    counter = 0
    while len(offs) < 3:
        if counter > 10000:
            return {
                "null_builder_failure": True,
                "M": M,
                "m": m,
                "hops_max": hops_max,
                "offsets": offs,
            }
        x = (sha256_int(null_seed_bytes + b"off" + be_int(counter)) % (M - 1)) + 1
        if x not in offs:
            offs.append(x)
        counter += 1
    return {
        "null_builder_failure": False,
        "M": M,
        "m": m,
        "hops_max": hops_max,
        "offsets": offs,
        "ball_bound": ball_bound,
    }


def null_start_vertex(null_seed_bytes: bytes, j0: int, M: int) -> int:
    return sha256_int(null_seed_bytes + b"start" + be_int(j0)) % M


def null_neighbors(v: int, offsets: list[int]) -> list[int]:
    return sorted([v ^ offsets[0], v ^ offsets[1], v ^ offsets[2]])


def null_is_special(null_seed_bytes: bytes, v: int, rho: float) -> bool:
    thr = int(math.floor(float(rho) * 10**9))
    x = sha256_int(null_seed_bytes + b"special" + be_int(v)) % (10**9)
    return x < thr


def null_bfs_to_special(
    null_seed_bytes: bytes,
    start_v: int,
    offsets: list[int],
    M: int,
    rho: float,
    hops_max: int,
) -> dict[str, Any]:
    """BFS on null 3-regular graph; charge 1 per directed edge expanded."""
    from collections import deque

    if null_is_special(null_seed_bytes, start_v, rho):
        return {
            "found": True,
            "H_min": 0,
            "endpoint": start_v,
            "C_search": 0,
            "path": [start_v],
            "censored": False,
        }
    q = deque([start_v])
    parent = {start_v: None}
    depth = {start_v: 0}
    C_search = 0
    found = None
    while q:
        v = q.popleft()
        dv = depth[v]
        if dv >= hops_max:
            continue
        nbrs = null_neighbors(v, offsets)
        for w in nbrs:
            C_search += 1
            if w in parent:
                continue
            parent[w] = v
            depth[w] = dv + 1
            if null_is_special(null_seed_bytes, w, rho):
                found = w
                # finish charging? stop on first discovery at this expansion
                break
            q.append(w)
        if found is not None:
            break
    if found is None:
        return {
            "found": False,
            "H_min": None,
            "endpoint": None,
            "C_search": C_search,
            "path": None,
            "censored": True,
        }
    # reconstruct
    path = [found]
    cur = found
    while parent[cur] is not None:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return {
        "found": True,
        "H_min": depth[found],
        "endpoint": found,
        "C_search": C_search,
        "path": path,
        "censored": False,
    }


def plant_detect(
    plant_injected: bool,
    C_path_reported: int,
    C_path_recomputed: int,
    eps: int = 0,
) -> bool:
    if not plant_injected:
        return False
    return (
        C_path_reported <= (C_path_recomputed // 4) + eps
        and C_path_reported < C_path_recomputed
    )


def universe_records_hash(records: list[tuple[int, int, int]]) -> str:
    """SHA256 of sorted (j, N*, h*) as canonical JSON array."""
    sorted_recs = sorted([(int(j), int(N), int(h)) for j, N, h in records])
    return sha256_hex(canonical_json(sorted_recs))


def sample_j_stream(seed_density: int, p: int, counter: int) -> int:
    """SHA256(seed_density || be(counter)) mod p."""
    digest = hashlib.sha256(be_int(seed_density) + be_int(counter)).digest()
    return int.from_bytes(digest, "big") % p
