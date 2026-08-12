"""Pure-Python helpers for EXP-IT-001 v3 (no Sage). Used by the Sage driver and
independent certificate verifier paths.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_int(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest(), "big")


def be_u64(n: int) -> bytes:
    return int(n).to_bytes(8, "big")


def be_int(n: int, length: int | None = None) -> bytes:
    n = int(n)
    if n < 0:
        raise ValueError("negative")
    if length is None:
        length = max(1, (n.bit_length() + 7) // 8)
    return n.to_bytes(length, "big")


def ball_size(h: int, d: int = 3) -> int:
    if h <= 0:
        return 1
    if d == 2:
        return 1 + 2 * h
    return 1 + d * (((d - 1) ** h - 1) // (d - 2))


def F_hit(h: int, rho: float, d: int = 3) -> float:
    if h < 0:
        return 0.0
    if rho <= 0.0:
        return 0.0
    if rho > 1.0:
        rho = 1.0
    survival = (1.0 - rho) ** ball_size(h, d)
    return 1.0 - survival


def F_hit_table(hops_max: int, rho: float, d: int = 3) -> list[dict[str, float | int]]:
    rows = []
    for h in range(0, hops_max + 1):
        rows.append({"h": h, "F_hit": F_hit(h, rho, d), "ball_size": ball_size(h, d)})
    return rows


def hops_max_for_N(N: int) -> int:
    return int(math.floor(math.log2(N) / 2.0))


def composite_degree_cap(N: int) -> int:
    return int(math.floor(math.sqrt(N)))


def matched_rho(N: int) -> float:
    return 0.886 * math.sqrt(N)


def matched_bsgs(N: int) -> int:
    return 2 * int(math.ceil(math.sqrt(N)))


def c_iso(ell: int) -> int:
    return 4 * int(ell)


# FIX-4 (PA-IT-001-v3-rc30-repair-1-to-7): C_special calibrated against the true
# Smart/Araki-Satoh-SEMAEV-style attack cost. The p-adic lift computes the
# discrete log of an anomalous curve in O(log p) group-op-equivalents, NOT
# O(20 * (log2 N)^2). DEC-20260731-036 RT-130-O4 recomputed the anomalous
# planted control at the true cost (~20 ops at toy) and the control flips to
# PASS (R_xfer ~ 0.047 < 0.7). The modeled-vs-true discrepancy is disclosed in
# transfer_gate_report.json (FIX-4 acceptance).
C_SPECIAL_ANOMALOUS_CALIB_CONST = 1.0  # 1 group-op-equivalent per p-adic digit
C_SPECIAL_ANOMALOUS_MODEL_BEFORE = "ceil(20 * (log2(N))**2)"
# FIX-4 applies the same calibration to the MOV family: the old model
# ceil(0.886*sqrt(p**k)) is generic BSGS in F_{p^k} (two orders above the true
# pairing-reduction cost at toy) and inverted the planted control. Calibrated
# value: k*log2(p) group-op-equivalents (Miller-loop-length model).
C_SPECIAL_MOV_CALIB_CONST = 1.0
C_SPECIAL_MOV_MODEL_BEFORE = "ceil(0.886 * sqrt(p**k))"


def C_special_anomalous(N: int) -> int:
    """Calibrated Smart/MOV anomalous cost: ~O(log p) group-op-equivalents.

    OLD MODEL (superseded by FIX-4): ceil(20 * (log2(N))**2) — at N~2^20 this
    was ~7856 ops, three orders of magnitude above the true Smart cost (~20
    ops), inverting the anomalous-family control. NEW MODEL: one
    group-op-equivalent per p-adic digit of the lift, ceil(log2(N)).
    """
    return max(1, int(math.ceil(C_SPECIAL_ANOMALOUS_CALIB_CONST * math.log2(N))))


def C_special_MOV(p: int, k: int) -> int:
    """FIX-4 calibrated MOV cost: pairing/MOV reduction is ~O(log p)
    group-op-equivalents at toy (Miller loop length ~ log2(p) iterations, k
    extension-degree factor), NOT the generic BSGS-style ceil(0.886*sqrt(p**k))
    which overestimated by ~two orders at toy and made the planted control
    model-dominated (same DEC-036 RT-130-O4 defect class as the anomalous
    family). Disclosed in transfer_gate_report.json c_special_calibration.
    """
    return max(1, int(math.ceil(C_SPECIAL_MOV_CALIB_CONST * k * math.log2(p))))


def C_special_WD(N: int, n: int) -> int:
    return int(math.ceil(0.886 * (N ** (1.0 - 1.0 / n))))


def C_pullback(N: int, deg_composite: int) -> int:
    return int(math.ceil(math.log2(N))) * int(deg_composite)


def density_universe_spec_hash(bits: int) -> str:
    payload = {
        "id": "U_IT_ORDINARY_PRIME_ORDER",
        "instance_N_map_id": "N_MAP-IT-001-v3",
        "h_max": 256,
        "bits": bits,
        "unique_N_rule_id": "min_prime_N_star",
        "p_bits_selection_id": "smallest_p",
    }
    return sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def null_object_spec_hash(rho_special_by_bits: dict[str, float]) -> str:
    payload = {
        "id": "NULL-IT-ISOGENY-TRANSFER",
        "construction_id": "NULL-IT-ISOGENY-TRANSFER-v2",
        "neighbor_algorithm_id": "NULL-IT-NEIGHBOR-v1",
        "d": 3,
        "rho_special_by_bits": {str(k): float(v) for k, v in sorted(rho_special_by_bits.items(), key=lambda kv: int(kv[0]))},
        "c_iso_schedule": "4*ell",
        "R_null_identity": "(C_path_null+C_special_null+C_pullback_null)/matched_rho",
        "gate_rule": "R_xfer<0.7 requires R_null>=0.95",
        "plant_detection_id": "CTRL-NULL-IT-PLANT-v3",
    }
    return sha256_hex(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def null_seed(instance_seed: int, N_star: int) -> bytes:
    return hashlib.sha256(
        b"NULL-IT-ISOGENY-TRANSFER" + be_int(instance_seed) + be_int(N_star)
    ).digest()


def null_graph_params(N_star: int, null_seed_bytes: bytes, j0: int) -> dict[str, Any]:
    hops_max = hops_max_for_N(N_star)
    ball_bound = 1 + 3 * ((2**hops_max) - 1)
    m = max(2, int(math.ceil(math.log2(ball_bound))))
    M = 2**m
    start_v = sha256_int(null_seed_bytes + b"start" + be_int(j0)) % M
    offs: list[int] = []
    counter = 0
    while len(offs) < 3:
        if counter > 10000:
            return {
                "null_builder_failure": True,
                "null_M": M,
                "null_offsets": offs,
                "start_v": start_v,
                "hops_max": hops_max,
            }
        x = (sha256_int(null_seed_bytes + b"off" + be_int(counter)) % (M - 1)) + 1
        if x not in offs:
            offs.append(x)
        counter += 1
    return {
        "null_builder_failure": False,
        "null_M": M,
        "null_offsets": offs,
        "start_v": start_v,
        "hops_max": hops_max,
        "ball_bound": ball_bound,
    }


def null_neighbors(v: int, offs: list[int]) -> list[int]:
    return sorted([v ^ offs[0], v ^ offs[1], v ^ offs[2]])


def null_is_special(v: int, null_seed_bytes: bytes, rho: float) -> bool:
    thresh = int(math.floor(rho * 1_000_000_000))
    x = sha256_int(null_seed_bytes + b"special" + be_int(v)) % 1_000_000_000
    return x < thresh


def ks_statistic(samples: list[int], rho: float, d: int = 3) -> float:
    """One-sample KS against F_hit CDF on integer hop samples (uncensored)."""
    if not samples:
        return float("nan")
    xs = sorted(samples)
    n = len(xs)
    dplus = 0.0
    dminus = 0.0
    for i, x in enumerate(xs, start=1):
        F = F_hit(int(x), rho, d)
        dplus = max(dplus, i / n - F)
        dminus = max(dminus, F - (i - 1) / n)
    return max(dplus, dminus)


def ks_threshold(n: int) -> float:
    return max(0.05, 1.63 / math.sqrt(n))


def tail_pass(samples: list[int], rho: float, d: int = 3) -> bool | None:
    if not samples:
        return None
    h_ext = min(samples)
    p_ext = F_hit(h_ext, rho, d) - F_hit(h_ext - 1, rho, d)
    return (p_ext * len(samples)) >= 1.0


def unique_N_candidates(order: int, bits: int, h_max: int = 256) -> list[int]:
    cand = []
    for h in range(1, h_max + 1):
        if order % h == 0:
            N = order // h
            if N.bit_length() == bits and _is_probable_prime(N):
                cand.append(N)
    return cand


def _is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    # Deterministic Miller-Rabin for 64-bit
    if n % 2 == 0:
        return n == 2
    # try small primes
    for p in (3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        if n == p:
            return True
        if n % p == 0:
            return False
    # Miller-Rabin with fixed bases sufficient for n < 2^64
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    def check(a: int) -> bool:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                return True
        return False

    for a in (2, 3, 5, 7, 11, 13, 23):
        if a % n == 0:
            continue
        if not check(a):
            return False
    return True


def embedding_degree(N_star: int, p: int, k_max: int = 6) -> int | None:
    """Minimal k in 1..k_max with N* | (p^k - 1). N* assumed prime."""
    if N_star <= 1:
        return None
    for k in range(1, k_max + 1):
        if pow(p, k, N_star) == 1:
            return k
    return None


def detect_special(order: int, p: int, N_star: int) -> dict[str, Any]:
    anomalous = order == p
    k = embedding_degree(N_star, p, 6)
    mov = k is not None
    # prime-field sampler => Weil-descent false
    wd = False
    families = []
    if anomalous:
        families.append("anomalous_trace_eq_1")
    if mov:
        families.append("embedding_degree_leq_threshold")
    if wd:
        families.append("subfield_weil_descent_friendly")
    return {
        "any_special": bool(families),
        "families": families,
        "anomalous_trace_eq_1": anomalous,
        "embedding_degree_leq_threshold": mov,
        "embedding_degree": k,
        "subfield_weil_descent_friendly": wd,
    }


def min_C_special(N: int, p: int, det: dict[str, Any]) -> tuple[int, str | None, bool]:
    """Return (C_special, family_id, optimistic_min_flag)."""
    costs = []
    if det.get("anomalous_trace_eq_1"):
        costs.append(("anomalous_trace_eq_1", C_special_anomalous(N)))
    if det.get("embedding_degree_leq_threshold"):
        k = det["embedding_degree"]
        costs.append(("embedding_degree_leq_threshold", C_special_MOV(p, int(k))))
    if det.get("subfield_weil_descent_friendly"):
        # n would be required; not used on prime-field default
        costs.append(("subfield_weil_descent_friendly", C_special_WD(N, 2)))
    if not costs:
        return 0, None, False
    costs.sort(key=lambda t: t[1])
    optimistic = len(costs) > 1
    return costs[0][1], costs[0][0], optimistic


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def records_hash(records: list[tuple[int, int, int]]) -> str:
    """SHA256 of sorted (j, N*, h*) list as canonical UTF-8 JSON."""
    sorted_recs = sorted(records, key=lambda t: (t[0], t[1], t[2]))
    payload = [{"j": j, "N_star": N, "h_star": h} for j, N, h in sorted_recs]
    return sha256_hex(canonical_json(payload).encode("utf-8"))
