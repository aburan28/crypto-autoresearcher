"""Deterministic, prospective ECTD v6 arithmetic-candidate contract.

This module is static protocol infrastructure.  It does not search the frozen
0..4999 counter ranges at import time, construct a curve, access a target, or
make a scientific inference.  All integer arithmetic is exact.  Record
integers that can exceed the JSON interoperable range are decimal strings.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Mapping

CANDIDATE_SCHEMA = "crypto.autoresearch.ectd_v6_candidate.v1"
WITNESS_SCHEMA = "crypto.autoresearch.ectd_v6_arithmetic_witness.v1"
REJECTION_SCHEMA = "crypto.autoresearch.ectd_v6_rejection.v1"
ROW_TERMINAL_SCHEMA = "crypto.autoresearch.ectd_v6_row_terminal.v1"
MAP_DOMAIN = "ECTD-V6-ORDER-SEMANTIC-MAP-20260813"
EXPERIMENT_ID = "EXP-ECTD-9e4248"
AMENDMENT_ORDINAL = 6
MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991
COUNTER_FIRST = 0
COUNTER_LAST = 4_999

ROWS: tuple[dict[str, int], ...] = (
    {"slot": 0, "seed": 301, "target_N_bits": 40, "D_K": -7, "q": 29, "horizontal_ell": 2},
    {"slot": 1, "seed": 302, "target_N_bits": 43, "D_K": -8, "q": 17, "horizontal_ell": 3},
    {"slot": 2, "seed": 303, "target_N_bits": 46, "D_K": -11, "q": 31, "horizontal_ell": 3},
    {"slot": 3, "seed": 304, "target_N_bits": 49, "D_K": -8, "q": 19, "horizontal_ell": 3},
    {"slot": 4, "seed": 305, "target_N_bits": 52, "D_K": -7, "q": 23, "horizontal_ell": 2},
    {"slot": 5, "seed": 306, "target_N_bits": 55, "D_K": -11, "q": 23, "horizontal_ell": 3},
    {"slot": 6, "seed": 307, "target_N_bits": 58, "D_K": -19, "q": 23, "horizontal_ell": 5},
    {"slot": 7, "seed": 308, "target_N_bits": 60, "D_K": -7, "q": 29, "horizontal_ell": 2},
)

TRIAL_PRIMES: tuple[int, ...] = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
MILLER_RABIN_BASES: tuple[int, ...] = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)

REJECTION_PRECEDENCE: tuple[str, ...] = (
    "INPUT_SERIALIZATION_MISMATCH",
    "EMPTY_TRACE_INTERVAL",
    "NONINTEGRAL_P",
    "NONINTEGRAL_N",
    "N_BIT_LENGTH_MISMATCH",
    "P_NOT_ODD",
    "N_NOT_ODD",
    "P_COMPOSITE",
    "N_COMPOSITE",
    "HASSE_BOUND_FAILURE",
    "ORDER_IDENTITY_FAILURE",
    "DISCRIMINANT_IDENTITY_FAILURE",
    "ACCEPTED",
)

REJECTION_REGISTRY: dict[str, dict[str, tuple[str, ...] | str]] = {
    "INPUT_SERIALIZATION_MISMATCH": {"stage": "SERIALIZATION", "details": ("expected_sha256", "observed_sha256")},
    "EMPTY_TRACE_INTERVAL": {"stage": "INTERVAL", "details": ("lower_N", "upper_N_exclusive", "L", "r")},
    "NONINTEGRAL_P": {"stage": "ARITHMETIC", "details": ("p_numerator", "denominator")},
    "NONINTEGRAL_N": {"stage": "ARITHMETIC", "details": ("M", "h")},
    "N_BIT_LENGTH_MISMATCH": {"stage": "ARITHMETIC", "details": ("N", "expected_bits", "observed_bits")},
    "P_NOT_ODD": {"stage": "ARITHMETIC", "details": ("p",)},
    "N_NOT_ODD": {"stage": "ARITHMETIC", "details": ("N",)},
    "P_COMPOSITE": {"stage": "PRIMALITY", "details": ("p",)},
    "N_COMPOSITE": {"stage": "PRIMALITY", "details": ("N",)},
    "HASSE_BOUND_FAILURE": {"stage": "ARITHMETIC", "details": ("p", "t", "t_squared", "four_p")},
    "ORDER_IDENTITY_FAILURE": {"stage": "ARITHMETIC", "details": ("p", "t", "M", "h", "N")},
    "DISCRIMINANT_IDENTITY_FAILURE": {"stage": "ARITHMETIC", "details": ("p", "t", "D_K", "f_pi", "lhs", "rhs")},
}


def _assert_ascii_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise ValueError("v6 JCS objects require ASCII property names")
            _assert_ascii_keys(item)
    elif isinstance(value, list):
        for item in value:
            _assert_ascii_keys(item)
    elif isinstance(value, float):
        raise TypeError("floating-point values are outside the v6 canonical domain")
    elif isinstance(value, int) and abs(value) > MAX_SAFE_JSON_INTEGER:
        raise ValueError("unsafe JSON integers must be encoded as decimal strings")


def jcs_bytes(value: Any) -> bytes:
    """Canonical bytes for this ASCII-key, integer-only RFC 8785 subset."""
    _assert_ascii_keys(value)
    return json.dumps(
        value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decimal(value: int) -> str:
    if not isinstance(value, int):
        raise TypeError("exact integer required")
    return str(value)


def class_parameters(D_K: int, q: int) -> dict[str, int]:
    """Return the sole admitted v6 class map, independent of outcomes."""
    if D_K == -7:
        q2 = (q * q) % 16
        if q2 == 1:
            r = 0
        elif q2 == 9:
            r = 8
        else:
            raise ValueError("D_K=-7 requires odd q with q^2 mod 16 in {1,9}")
        return {"f_pi": 2 * q, "h": 8, "L": 32, "r": r}
    if D_K == -8:
        return {"f_pi": q, "h": 6, "L": 12, "r": 6}
    if D_K == -11:
        return {"f_pi": q, "h": 3, "L": 6, "r": 3}
    if D_K == -19:
        return {"f_pi": q, "h": 1, "L": 2, "r": 1}
    raise ValueError("unregistered D_K")


def frozen_row(slot: int) -> dict[str, int]:
    if not isinstance(slot, int) or not 0 <= slot < len(ROWS):
        raise ValueError("slot outside frozen range")
    return dict(ROWS[slot])


def candidate_input(row: Mapping[str, int], counter: int) -> dict[str, Any]:
    if counter < COUNTER_FIRST or counter > COUNTER_LAST:
        raise ValueError("counter outside frozen 0..4999 domain")
    params = class_parameters(row["D_K"], row["q"])
    return {
        "D_K": row["D_K"],
        "L": params["L"],
        "amendment_ordinal": AMENDMENT_ORDINAL,
        "counter": counter,
        "experiment_id": EXPERIMENT_ID,
        "f_pi": params["f_pi"],
        "h": params["h"],
        "horizontal_ell": row["horizontal_ell"],
        "map_domain": MAP_DOMAIN,
        "q": row["q"],
        "r": params["r"],
        "schema": CANDIDATE_SCHEMA,
        "seed": row["seed"],
        "slot": row["slot"],
        "target_N_bits": row["target_N_bits"],
    }


def _ceil_sqrt(n: int) -> int:
    if n <= 0:
        return 0
    root = math.isqrt(n)
    return root if root * root == n else root + 1


def _align_up(value: int, modulus: int, residue: int) -> int:
    return value + ((residue - value) % modulus)


def _align_down(value: int, modulus: int, residue: int) -> int:
    return value - ((value - residue) % modulus)


def trace_interval(row: Mapping[str, int]) -> dict[str, int] | None:
    """Exact monotone interval for target-width N; upper bound is exclusive."""
    params = class_parameters(row["D_K"], row["q"])
    h, f_pi, L, r = (params[k] for k in ("h", "f_pi", "L", "r"))
    lower_N = 1 << (row["target_N_bits"] - 1)
    upper_N = 1 << row["target_N_bits"]
    A = -(f_pi * f_pi * row["D_K"])
    low_square = max(0, 4 * h * lower_N - A)
    high_square = 4 * h * upper_N - A - 1
    if high_square < 0:
        return None
    raw_min = 2 + _ceil_sqrt(low_square)
    raw_max = 2 + math.isqrt(high_square)
    t_min = _align_up(raw_min, L, r)
    t_max = _align_down(raw_max, L, r)
    if t_min > t_max:
        return None
    count = 1 + (t_max - t_min) // L
    return {
        "L": L,
        "r": r,
        "lower_N": lower_N,
        "upper_N_exclusive": upper_N,
        "t_min": t_min,
        "t_max": t_max,
        "count": count,
    }


def _derive(row: Mapping[str, int], t: int) -> dict[str, int]:
    params = class_parameters(row["D_K"], row["q"])
    f_pi, h = params["f_pi"], params["h"]
    p_numerator = t * t - f_pi * f_pi * row["D_K"]
    p, p_remainder = divmod(p_numerator, 4)
    M = p + 1 - t
    N, N_remainder = divmod(M, h)
    return {
        **params,
        "p_numerator": p_numerator,
        "p_remainder": p_remainder,
        "p": p,
        "M": M,
        "N_remainder": N_remainder,
        "N": N,
        "t": t,
    }


def is_prime_u64(n: int) -> bool:
    """Deterministic strong Miller-Rabin on the frozen 0 <= n < 2^64 domain."""
    if not 0 <= n < (1 << 64):
        raise ValueError("primality input outside frozen u64 domain")
    if n < 2:
        return False
    for prime in TRIAL_PRIMES:
        if n == prime:
            return True
        if n % prime == 0:
            return False
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in MILLER_RABIN_BASES:
        a = base % n
        if a in (0, 1):
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def rejection_record(
    row: Mapping[str, int], counter: int, code: str, input_sha256: str,
    details: Mapping[str, Any],
) -> dict[str, Any]:
    if code not in REJECTION_REGISTRY:
        raise ValueError("unregistered arithmetic rejection code")
    entry = REJECTION_REGISTRY[code]
    expected = tuple(entry["details"])
    if tuple(sorted(details)) != tuple(sorted(expected)):
        raise ValueError("details keys do not match rejection registry")
    return {
        "code": code,
        "counter": counter,
        "details": dict(details),
        "input_sha256": input_sha256,
        "schema": REJECTION_SCHEMA,
        "seed": row["seed"],
        "slot": row["slot"],
        "stage": entry["stage"],
    }


def _large_details(values: Mapping[str, int | str]) -> dict[str, str | int]:
    out: dict[str, str | int] = {}
    for key, value in values.items():
        if isinstance(value, int) and (abs(value) > MAX_SAFE_JSON_INTEGER or key in {"p", "N", "M", "t", "lhs", "rhs", "p_numerator", "lower_N", "upper_N_exclusive", "t_squared", "four_p"}):
            out[key] = decimal(value)
        else:
            out[key] = value
    return out


def evaluate_counter(slot: int, counter: int, asserted_input_bytes: bytes | None = None) -> dict[str, Any]:
    """Evaluate exactly one counter and return one rejection or witness record."""
    row = frozen_row(slot)
    input_object = candidate_input(row, counter)
    encoded = jcs_bytes(input_object)
    input_digest = sha256_hex(encoded)
    if asserted_input_bytes is not None and asserted_input_bytes != encoded:
        return rejection_record(
            row, counter, "INPUT_SERIALIZATION_MISMATCH", input_digest,
            {"expected_sha256": input_digest, "observed_sha256": sha256_hex(asserted_input_bytes)},
        )
    interval = trace_interval(row)
    if interval is None:
        params = class_parameters(row["D_K"], row["q"])
        return rejection_record(
            row, counter, "EMPTY_TRACE_INTERVAL", input_digest,
            _large_details({
                "lower_N": 1 << (row["target_N_bits"] - 1),
                "upper_N_exclusive": 1 << row["target_N_bits"],
                "L": params["L"], "r": params["r"],
            }),
        )
    shake = hashlib.shake_256(encoded).digest(32)
    z = int.from_bytes(shake, "big", signed=False)
    t = interval["t_min"] + interval["L"] * (z % interval["count"])
    values = _derive(row, t)
    if values["p_remainder"]:
        return rejection_record(row, counter, "NONINTEGRAL_P", input_digest, _large_details({"p_numerator": values["p_numerator"], "denominator": 4}))
    if values["N_remainder"]:
        return rejection_record(row, counter, "NONINTEGRAL_N", input_digest, _large_details({"M": values["M"], "h": values["h"]}))
    if values["N"].bit_length() != row["target_N_bits"]:
        return rejection_record(row, counter, "N_BIT_LENGTH_MISMATCH", input_digest, _large_details({"N": values["N"], "expected_bits": row["target_N_bits"], "observed_bits": values["N"].bit_length()}))
    if values["p"] % 2 != 1:
        return rejection_record(row, counter, "P_NOT_ODD", input_digest, _large_details({"p": values["p"]}))
    if values["N"] % 2 != 1:
        return rejection_record(row, counter, "N_NOT_ODD", input_digest, _large_details({"N": values["N"]}))
    if not is_prime_u64(values["p"]):
        return rejection_record(row, counter, "P_COMPOSITE", input_digest, _large_details({"p": values["p"]}))
    if not is_prime_u64(values["N"]):
        return rejection_record(row, counter, "N_COMPOSITE", input_digest, _large_details({"N": values["N"]}))
    if values["t"] * values["t"] > 4 * values["p"]:
        return rejection_record(row, counter, "HASSE_BOUND_FAILURE", input_digest, _large_details({"p": values["p"], "t": values["t"], "t_squared": values["t"] * values["t"], "four_p": 4 * values["p"]}))
    if values["M"] != values["h"] * values["N"] or values["M"] != values["p"] + 1 - values["t"]:
        return rejection_record(row, counter, "ORDER_IDENTITY_FAILURE", input_digest, _large_details({"p": values["p"], "t": values["t"], "M": values["M"], "h": values["h"], "N": values["N"]}))
    lhs = values["t"] * values["t"] - 4 * values["p"]
    rhs = values["f_pi"] * values["f_pi"] * row["D_K"]
    if lhs != rhs:
        return rejection_record(row, counter, "DISCRIMINANT_IDENTITY_FAILURE", input_digest, _large_details({"p": values["p"], "t": values["t"], "D_K": row["D_K"], "f_pi": values["f_pi"], "lhs": lhs, "rhs": rhs}))
    return {
        "D_K": row["D_K"],
        "L": values["L"],
        "M": decimal(values["M"]),
        "N": decimal(values["N"]),
        "counter": counter,
        "f_pi": decimal(values["f_pi"]),
        "h": values["h"],
        "horizontal_ell": row["horizontal_ell"],
        "input_sha256": input_digest,
        "p": decimal(values["p"]),
        "q": row["q"],
        "r": values["r"],
        "schema": WITNESS_SCHEMA,
        "seed": row["seed"],
        "shake256_32_hex": shake.hex(),
        "slot": row["slot"],
        "t": decimal(values["t"]),
        "target_N_bits": row["target_N_bits"],
    }


def residue_proof_for_row(slot: int) -> dict[str, Any]:
    """Finite proof certificate for integrality, oddness, Hasse, and trial divisors."""
    row = frozen_row(slot)
    params = class_parameters(row["D_K"], row["q"])
    period = math.lcm(params["L"], 8 * params["h"])
    residue_cases: list[dict[str, Any]] = []
    for t in range(params["r"], params["r"] + period, params["L"]):
        values = _derive(row, t)
        residue_cases.append({
            "M_mod_2h": (values["p"] + 1 - t) % (2 * params["h"]),
            "N_mod_2": values["N"] % 2,
            "discriminant_identity_residual": t * t - 4 * values["p"] - params["f_pi"] * params["f_pi"] * row["D_K"],
            "order_identity_residual": values["p"] + 1 - t - params["h"] * values["N"],
            "p_mod_2": values["p"] % 2,
            "p_numerator_mod_4": values["p_numerator"] % 4,
            "t_mod_period": t % period,
        })
    if not all(c["p_numerator_mod_4"] == 0 and c["p_mod_2"] == 1 and c["M_mod_2h"] == params["h"] and c["N_mod_2"] == 1 and c["order_identity_residual"] == 0 and c["discriminant_identity_residual"] == 0 for c in residue_cases):
        raise AssertionError("finite integrality/oddness proof failed")
    trial_witnesses: list[dict[str, int]] = []
    for prime in TRIAL_PRIMES:
        for k in range(prime):
            t = params["r"] + params["L"] * k
            values = _derive(row, t)
            if values["p"] % prime != 0 and values["N"] % prime != 0:
                trial_witnesses.append({"k": k, "N_mod_s": values["N"] % prime, "p_mod_s": values["p"] % prime, "s": prime, "t_mod_Ls": t % (params["L"] * prime)})
                break
        else:
            raise AssertionError(f"trial prime {prime} universally divides p*N")
    return {
        "D_K": row["D_K"],
        "L": params["L"],
        "f_pi": params["f_pi"],
        "h": params["h"],
        "hasse_proof": "t^2-4*p=f_pi^2*D_K<0, hence t^2<4*p",
        "identity_proof": "p=(t^2-f_pi^2*D_K)/4; M=p+1-t; N=M/h; exhaustive residuals below are zero",
        "integrality_oddness_period": period,
        "q": row["q"],
        "q_squared_mod_16": row["q"] * row["q"] % 16,
        "r": params["r"],
        "residue_cases": residue_cases,
        "slot": slot,
        "trial_nondivisibility_witnesses": trial_witnesses,
    }


def fixture_record(slot: int, counter: int) -> dict[str, Any]:
    """Canonical fixture wrapper for one bounded, explicitly named counter."""
    row = frozen_row(slot)
    inp = candidate_input(row, counter)
    inp_bytes = jcs_bytes(inp)
    out = evaluate_counter(slot, counter)
    out_bytes = jcs_bytes(out)
    return {
        "counter": counter,
        "input_jcs_hex": inp_bytes.hex(),
        "input_sha256": sha256_hex(inp_bytes),
        "output_jcs_hex": out_bytes.hex(),
        "output_sha256": sha256_hex(out_bytes),
        "output_terminal": out.get("code", "ACCEPTED"),
        "slot": slot,
    }


def verify_fixture_record(record: Mapping[str, Any]) -> bool:
    regenerated = fixture_record(int(record["slot"]), int(record["counter"]))
    return dict(record) == regenerated


if __name__ == "__main__":
    raise SystemExit("static contract module: import functions explicitly; no search entry point")
