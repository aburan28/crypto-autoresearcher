"""Closed, typed record semantics for the ECTD v7 verifier-first package.

This module performs deterministic replay only.  It never searches a counter
range, constructs a scheduled curve, accesses a target, runs a meter, or makes
a scientific decision.  The immutable v6 arithmetic streams are accepted only
as inputs and are recomputed record by record under their original v6 map.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

REGISTRY_SCHEMA = "crypto.autoresearch.ectd_v7_terminal_registry.v1"
TERMINAL_SCHEMA = "crypto.autoresearch.ectd_v7_terminal.v1"
CONSTRUCTION_SCHEMA = "crypto.autoresearch.ectd_v7_construction_record.v1"
V6_CANDIDATE_SCHEMA = "crypto.autoresearch.ectd_v6_candidate.v1"
V6_WITNESS_SCHEMA = "crypto.autoresearch.ectd_v6_arithmetic_witness.v1"
V6_REJECTION_SCHEMA = "crypto.autoresearch.ectd_v6_rejection.v1"
V6_ROW_TERMINAL_SCHEMA = "crypto.autoresearch.ectd_v6_row_terminal.v1"
MAP_DOMAIN = "ECTD-V6-ORDER-SEMANTIC-MAP-20260813"
EXPERIMENT_ID = "EXP-ECTD-9e4248"
AMENDMENT_ORDINAL = 6
MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991
COUNTER_FIRST = 0
COUNTER_LAST = 4_999
TRIAL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
MILLER_RABIN_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


class RecordError(ValueError):
    """A stable first-failure code plus a non-authoritative explanation."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _pairs_no_duplicates(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise RecordError("DUPLICATE_JSON_KEY", f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise RecordError("NONFINITE_JSON_NUMBER", f"non-finite JSON number: {value}")


def strict_json_loads(text: str) -> Any:
    if not isinstance(text, str):
        raise RecordError("JSON_TEXT_REQUIRED", "strict parser requires text")
    try:
        return json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_constant=_reject_constant,
        )
    except RecordError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RecordError("MALFORMED_JSON", str(exc)) from exc


def strict_json_file(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _assert_canonical_domain(value: Any, pointer: str = "") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str) or not key.isascii():
                raise RecordError("NONASCII_PROPERTY", f"non-ASCII property at {pointer}")
            if unicodedata.normalize("NFC", key) != key:
                raise RecordError("NONNFC_STRING", f"non-NFC property at {pointer}")
            _assert_canonical_domain(item, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_canonical_domain(item, f"{pointer}/{index}")
    elif isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise RecordError("NONNFC_STRING", f"non-NFC string at {pointer}")
    elif isinstance(value, bool) or value is None:
        return
    elif isinstance(value, float):
        raise RecordError("FLOAT_OUTSIDE_JCS_PROFILE", f"float at {pointer}")
    elif isinstance(value, int):
        if abs(value) > MAX_SAFE_JSON_INTEGER:
            raise RecordError(
                "UNSAFE_JSON_INTEGER",
                f"integer outside interoperable range at {pointer}; use decimal text",
            )
    else:
        raise RecordError("UNSUPPORTED_JSON_TYPE", f"unsupported type at {pointer}")


def jcs_bytes(value: Any) -> bytes:
    """RFC 8785 subset used by v6/v7: NFC, ASCII keys, no floats."""
    _assert_canonical_domain(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], code: str) -> None:
    actual = set(value)
    wanted = set(expected)
    if actual != wanted:
        raise RecordError(
            code,
            f"keys differ: missing={sorted(wanted - actual)}, extra={sorted(actual - wanted)}",
        )


def load_registry(package_dir: Path | None = None) -> dict[str, Any]:
    base = package_dir or Path(__file__).resolve().parent
    registry = strict_json_file(base / "terminal-registry.json")
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise RecordError("REGISTRY_SCHEMA_MISMATCH", "wrong registry schema")
    terminals = registry.get("terminals")
    if not isinstance(terminals, list) or not terminals:
        raise RecordError("EMPTY_TERMINAL_REGISTRY", "terminal registry is empty")
    codes: set[str] = set()
    tuples: set[tuple[Any, ...]] = set()
    for entry in terminals:
        _exact_keys(entry, ("code", "stage", "class", "detail_keys"), "REGISTRY_ENTRY_KEYS")
        code = entry["code"]
        if code in codes:
            raise RecordError("DUPLICATE_TERMINAL_CODE", str(code))
        detail_keys = entry["detail_keys"]
        if not isinstance(detail_keys, list) or len(detail_keys) != len(set(detail_keys)):
            raise RecordError("DUPLICATE_DETAIL_KEY", str(code))
        row = (code, entry["stage"], entry["class"], tuple(sorted(detail_keys)))
        if row in tuples:
            raise RecordError("DUPLICATE_TERMINAL_TUPLE", str(code))
        codes.add(code)
        tuples.add(row)
    validator_errors = registry.get("validator_errors")
    if not isinstance(validator_errors, list) or not validator_errors:
        raise RecordError("EMPTY_TERMINAL_REGISTRY", "validator error registry is empty")
    for entry in validator_errors:
        _exact_keys(entry, ("code", "stage", "class", "detail_keys"), "REGISTRY_ENTRY_KEYS")
        code = entry["code"]
        if code in codes:
            raise RecordError("DUPLICATE_TERMINAL_CODE", str(code))
        detail_keys = entry["detail_keys"]
        if not isinstance(detail_keys, list) or len(detail_keys) != len(set(detail_keys)):
            raise RecordError("DUPLICATE_DETAIL_KEY", str(code))
        row = (code, entry["stage"], entry["class"], tuple(sorted(detail_keys)))
        if row in tuples:
            raise RecordError("DUPLICATE_TERMINAL_TUPLE", str(code))
        codes.add(code)
        tuples.add(row)
    precedence = registry.get("candidate_precedence")
    if not isinstance(precedence, list) or precedence[-1:] != ["ACCEPTED"]:
        raise RecordError("PRECEDENCE_INVALID", "candidate precedence must end in ACCEPTED")
    if precedence[:-1] != [e["code"] for e in terminals[:12]]:
        raise RecordError("PRECEDENCE_REGISTRY_DRIFT", "arithmetic precedence drift")
    rows = registry.get("frozen_rows")
    if not isinstance(rows, list) or [r.get("slot") for r in rows] != list(range(8)):
        raise RecordError("FROZEN_ROW_REGISTRY_INVALID", "expected slots 0..7")
    return registry


def registry_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {entry["code"]: entry for entry in registry["terminals"]}


def validate_terminal(record: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a closed v7 terminal; no stage/class/detail caller truth survives."""
    if not isinstance(record, Mapping):
        raise RecordError("TERMINAL_OBJECT_REQUIRED", "terminal must be an object")
    _exact_keys(record, ("schema", "code", "stage", "class", "details"), "TERMINAL_KEYS")
    if record["schema"] != TERMINAL_SCHEMA:
        raise RecordError("TERMINAL_SCHEMA_MISMATCH", str(record["schema"]))
    entry = registry_map(registry).get(record["code"])
    if entry is None:
        raise RecordError("UNKNOWN_TERMINAL_CODE", str(record["code"]))
    if record["stage"] != entry["stage"] or record["class"] != entry["class"]:
        raise RecordError("TERMINAL_TUPLE_MISMATCH", str(record["code"]))
    details = record["details"]
    if not isinstance(details, Mapping):
        raise RecordError("TERMINAL_DETAILS_OBJECT_REQUIRED", str(record["code"]))
    if set(details) != set(entry["detail_keys"]):
        raise RecordError("TERMINAL_DETAIL_KEYS_MISMATCH", str(record["code"]))
    jcs_bytes(record)
    return dict(record)


def terminal_from_code(
    code: str,
    details: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    entry = registry_map(registry).get(code)
    if entry is None:
        raise RecordError("UNKNOWN_TERMINAL_CODE", code)
    result = {
        "schema": TERMINAL_SCHEMA,
        "code": code,
        "stage": entry["stage"],
        "class": entry["class"],
        "details": dict(details),
    }
    return validate_terminal(result, registry)


def frozen_row(slot: int, registry: Mapping[str, Any]) -> dict[str, int]:
    if isinstance(slot, bool) or not isinstance(slot, int) or not 0 <= slot < 8:
        raise RecordError("SLOT_OUTSIDE_FROZEN_RANGE", str(slot))
    return dict(registry["frozen_rows"][slot])


def validate_frozen_row(row: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, int]:
    if not isinstance(row, Mapping):
        raise RecordError("ROW_OBJECT_REQUIRED", "row must be object")
    expected_keys = {
        "slot", "seed", "target_N_bits", "D_K", "q", "horizontal_ell",
        "f_pi", "h", "L", "r",
    }
    _exact_keys(row, expected_keys, "ROW_KEYS")
    expected = frozen_row(row.get("slot"), registry)
    if dict(row) != expected:
        raise RecordError("FRANKENSTEIN_ROW", "row fields do not match one frozen tuple")
    return expected


def _candidate_row(slot: int, registry: Mapping[str, Any]) -> dict[str, int]:
    row = frozen_row(slot, registry)
    return {k: row[k] for k in ("slot", "seed", "target_N_bits", "D_K", "q", "horizontal_ell")}


def candidate_input(row: Mapping[str, int], counter: int, registry: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(counter, bool) or not isinstance(counter, int) or not COUNTER_FIRST <= counter <= COUNTER_LAST:
        raise RecordError("COUNTER_OUTSIDE_FROZEN_RANGE", str(counter))
    full = frozen_row(row["slot"], registry)
    for key in ("slot", "seed", "target_N_bits", "D_K", "q", "horizontal_ell"):
        if row.get(key) != full[key]:
            raise RecordError("FRANKENSTEIN_ROW", key)
    return {
        "D_K": full["D_K"],
        "L": full["L"],
        "amendment_ordinal": AMENDMENT_ORDINAL,
        "counter": counter,
        "experiment_id": EXPERIMENT_ID,
        "f_pi": full["f_pi"],
        "h": full["h"],
        "horizontal_ell": full["horizontal_ell"],
        "map_domain": MAP_DOMAIN,
        "q": full["q"],
        "r": full["r"],
        "schema": V6_CANDIDATE_SCHEMA,
        "seed": full["seed"],
        "slot": full["slot"],
        "target_N_bits": full["target_N_bits"],
    }


def _ceil_sqrt(value: int) -> int:
    if value <= 0:
        return 0
    root = math.isqrt(value)
    return root if root * root == value else root + 1


def trace_interval(row: Mapping[str, int], registry: Mapping[str, Any]) -> dict[str, int] | None:
    full = frozen_row(row["slot"], registry)
    lower_n = 1 << (full["target_N_bits"] - 1)
    upper_n = 1 << full["target_N_bits"]
    offset = -(full["f_pi"] * full["f_pi"] * full["D_K"])
    low_square = max(0, 4 * full["h"] * lower_n - offset)
    high_square = 4 * full["h"] * upper_n - offset - 1
    if high_square < 0:
        return None
    raw_min = 2 + _ceil_sqrt(low_square)
    raw_max = 2 + math.isqrt(high_square)
    t_min = raw_min + ((full["r"] - raw_min) % full["L"])
    t_max = raw_max - ((raw_max - full["r"]) % full["L"])
    if t_min > t_max:
        return None
    return {
        "L": full["L"],
        "r": full["r"],
        "lower_N": lower_n,
        "upper_N_exclusive": upper_n,
        "t_min": t_min,
        "t_max": t_max,
        "count": 1 + (t_max - t_min) // full["L"],
    }


def is_prime_u64(value: int) -> bool:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < (1 << 64):
        raise RecordError("PRIMALITY_DOMAIN", "expected 0 <= n < 2^64")
    if value < 2:
        return False
    for prime in TRIAL_PRIMES:
        if value == prime:
            return True
        if value % prime == 0:
            return False
    d = value - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in MILLER_RABIN_BASES:
        a = base % value
        if a in (0, 1):
            continue
        x = pow(a, d, value)
        if x in (1, value - 1):
            continue
        for _ in range(s - 1):
            x = x * x % value
            if x == value - 1:
                break
        else:
            return False
    return True


def _record_int(value: int, key: str) -> str | int:
    force_text = {
        "p", "N", "M", "t", "lhs", "rhs", "p_numerator", "lower_N",
        "upper_N_exclusive", "t_squared", "four_p",
    }
    return str(value) if abs(value) > MAX_SAFE_JSON_INTEGER or key in force_text else value


def _large_details(values: Mapping[str, int]) -> dict[str, str | int]:
    return {key: _record_int(value, key) for key, value in values.items()}


def _v6_rejection(
    row: Mapping[str, int],
    counter: int,
    code: str,
    input_digest: str,
    details: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, Any]:
    entry = registry_map(registry).get(code)
    if entry is None or entry["class"] not in {"arithmetic_rejection", "resource_incomplete"}:
        raise RecordError("UNKNOWN_ARITHMETIC_TERMINAL", code)
    if set(details) != set(entry["detail_keys"]):
        raise RecordError("TERMINAL_DETAIL_KEYS_MISMATCH", code)
    return {
        "code": code,
        "counter": counter,
        "details": dict(details),
        "input_sha256": input_digest,
        "schema": V6_REJECTION_SCHEMA,
        "seed": row["seed"],
        "slot": row["slot"],
        "stage": entry["stage"],
    }


def evaluate_counter(slot: int, counter: int, registry: Mapping[str, Any]) -> dict[str, Any]:
    """Replay exactly one pre-existing v6 candidate.  This function never searches."""
    row = _candidate_row(slot, registry)
    full = frozen_row(slot, registry)
    encoded = jcs_bytes(candidate_input(row, counter, registry))
    input_digest = sha256_hex(encoded)
    interval = trace_interval(row, registry)
    if interval is None:
        return _v6_rejection(
            row, counter, "EMPTY_TRACE_INTERVAL", input_digest,
            _large_details({
                "lower_N": 1 << (full["target_N_bits"] - 1),
                "upper_N_exclusive": 1 << full["target_N_bits"],
                "L": full["L"], "r": full["r"],
            }), registry,
        )
    shake = hashlib.shake_256(encoded).digest(32)
    z = int.from_bytes(shake, "big", signed=False)
    t = interval["t_min"] + full["L"] * (z % interval["count"])
    p_numerator = t * t - full["f_pi"] * full["f_pi"] * full["D_K"]
    p, p_remainder = divmod(p_numerator, 4)
    M = p + 1 - t
    N, n_remainder = divmod(M, full["h"])
    common = {"p": p, "t": t, "M": M, "N": N}
    if p_remainder:
        return _v6_rejection(row, counter, "NONINTEGRAL_P", input_digest, _large_details({"p_numerator": p_numerator, "denominator": 4}), registry)
    if n_remainder:
        return _v6_rejection(row, counter, "NONINTEGRAL_N", input_digest, _large_details({"M": M, "h": full["h"]}), registry)
    if N.bit_length() != full["target_N_bits"]:
        return _v6_rejection(row, counter, "N_BIT_LENGTH_MISMATCH", input_digest, _large_details({"N": N, "expected_bits": full["target_N_bits"], "observed_bits": N.bit_length()}), registry)
    if p % 2 != 1:
        return _v6_rejection(row, counter, "P_NOT_ODD", input_digest, _large_details({"p": p}), registry)
    if N % 2 != 1:
        return _v6_rejection(row, counter, "N_NOT_ODD", input_digest, _large_details({"N": N}), registry)
    if not is_prime_u64(p):
        return _v6_rejection(row, counter, "P_COMPOSITE", input_digest, _large_details({"p": p}), registry)
    if not is_prime_u64(N):
        return _v6_rejection(row, counter, "N_COMPOSITE", input_digest, _large_details({"N": N}), registry)
    if t * t > 4 * p:
        return _v6_rejection(row, counter, "HASSE_BOUND_FAILURE", input_digest, _large_details({"p": p, "t": t, "t_squared": t * t, "four_p": 4 * p}), registry)
    if M != full["h"] * N or M != p + 1 - t:
        return _v6_rejection(row, counter, "ORDER_IDENTITY_FAILURE", input_digest, _large_details({"p": p, "t": t, "M": M, "h": full["h"], "N": N}), registry)
    lhs = t * t - 4 * p
    rhs = full["f_pi"] * full["f_pi"] * full["D_K"]
    if lhs != rhs:
        return _v6_rejection(row, counter, "DISCRIMINANT_IDENTITY_FAILURE", input_digest, _large_details({"p": p, "t": t, "D_K": full["D_K"], "f_pi": full["f_pi"], "lhs": lhs, "rhs": rhs}), registry)
    return {
        "D_K": full["D_K"], "L": full["L"], "M": str(M), "N": str(N),
        "counter": counter, "f_pi": str(full["f_pi"]), "h": full["h"],
        "horizontal_ell": full["horizontal_ell"], "input_sha256": input_digest,
        "p": str(p), "q": full["q"], "r": full["r"],
        "schema": V6_WITNESS_SCHEMA, "seed": full["seed"],
        "shake256_32_hex": shake.hex(), "slot": slot, "t": str(t),
        "target_N_bits": full["target_N_bits"],
    }


def validate_v6_rejection(record: Mapping[str, Any], registry: Mapping[str, Any]) -> None:
    _exact_keys(
        record,
        ("code", "counter", "details", "input_sha256", "schema", "seed", "slot", "stage"),
        "V6_REJECTION_KEYS",
    )
    if record["schema"] != V6_REJECTION_SCHEMA:
        raise RecordError("V6_REJECTION_SCHEMA_MISMATCH", str(record["schema"]))
    entry = registry_map(registry).get(record["code"])
    if entry is None:
        raise RecordError("UNKNOWN_TERMINAL_CODE", str(record["code"]))
    if record["stage"] != entry["stage"]:
        raise RecordError("TERMINAL_TUPLE_MISMATCH", str(record["code"]))
    if not isinstance(record["details"], Mapping) or set(record["details"]) != set(entry["detail_keys"]):
        raise RecordError("TERMINAL_DETAIL_KEYS_MISMATCH", str(record["code"]))


def replay_candidate_record(record: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, Any]:
    schema = record.get("schema")
    if schema == V6_REJECTION_SCHEMA:
        validate_v6_rejection(record, registry)
    elif schema != V6_WITNESS_SCHEMA:
        raise RecordError("UNKNOWN_CANDIDATE_RECORD_SCHEMA", str(schema))
    slot = record.get("slot")
    counter = record.get("counter")
    expected = evaluate_counter(slot, counter, registry)
    if dict(record) != expected:
        raise RecordError("CANDIDATE_SEMANTIC_MISMATCH", f"slot={slot} counter={counter}")
    return expected


def replay_candidate_fixture(fixture: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "slot", "counter", "input", "input_jcs_utf8", "input_sha256",
        "output", "output_jcs_utf8", "output_sha256",
    }
    _exact_keys(fixture, required, "CANDIDATE_FIXTURE_KEYS")
    row = _candidate_row(fixture["slot"], registry)
    expected_input = candidate_input(row, fixture["counter"], registry)
    if fixture["input"] != expected_input:
        raise RecordError("CANDIDATE_INPUT_MISMATCH", "fixture input object")
    input_bytes = jcs_bytes(expected_input)
    if fixture["input_jcs_utf8"].encode("utf-8") != input_bytes:
        raise RecordError("CANDIDATE_INPUT_JCS_MISMATCH", "fixture input bytes")
    if fixture["input_sha256"] != sha256_hex(input_bytes):
        raise RecordError("CANDIDATE_INPUT_HASH_MISMATCH", "fixture input hash")
    output = replay_candidate_record(fixture["output"], registry)
    output_bytes = jcs_bytes(output)
    if fixture["output_jcs_utf8"].encode("utf-8") != output_bytes:
        raise RecordError("CANDIDATE_OUTPUT_JCS_MISMATCH", "fixture output bytes")
    if fixture["output_sha256"] != sha256_hex(output_bytes):
        raise RecordError("CANDIDATE_OUTPUT_HASH_MISMATCH", "fixture output hash")
    return output


def validate_row_terminal(
    terminal: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    _exact_keys(
        terminal,
        ("accepted_witness", "counters_evaluated", "details", "last_counter", "rejection_census", "schema", "slot", "status"),
        "ROW_TERMINAL_KEYS",
    )
    if terminal["schema"] != V6_ROW_TERMINAL_SCHEMA or terminal["status"] != "first_accepted":
        raise RecordError("ROW_TERMINAL_STATUS", "expected first_accepted")
    if not candidates:
        raise RecordError("EMPTY_ROW_STREAM", "row has no candidates")
    accepted = [x for x in candidates if x.get("schema") == V6_WITNESS_SCHEMA]
    if len(accepted) != 1 or accepted[0] is not candidates[-1]:
        raise RecordError("FIRST_ACCEPTED_SEMANTICS", "exactly one final witness required")
    first_counter = candidates[0]["counter"]
    last_counter = candidates[-1]["counter"]
    if [x["counter"] for x in candidates] != list(range(first_counter, last_counter + 1)):
        raise RecordError("COUNTER_ORDER", "counters must be contiguous and ascending")
    if first_counter != 0:
        raise RecordError("FIRST_COUNTER_NOT_ZERO", str(first_counter))
    census = Counter(
        x["code"] for x in candidates if x.get("schema") == V6_REJECTION_SCHEMA
    )
    witness_bytes = jcs_bytes(accepted[0])
    expected_ref = {
        "artifact_sha256": sha256_hex(witness_bytes),
        "kind": V6_WITNESS_SCHEMA,
        "replay_check": True,
    }
    if terminal["accepted_witness"] != expected_ref:
        raise RecordError("ACCEPTED_WITNESS_REFERENCE", "terminal witness reference mismatch")
    if terminal["counters_evaluated"] != len(candidates):
        raise RecordError("COUNTER_COUNT", "terminal count mismatch")
    if terminal["last_counter"] != last_counter:
        raise RecordError("LAST_COUNTER", "terminal last counter mismatch")
    if terminal["rejection_census"] != dict(sorted(census.items())):
        raise RecordError("REJECTION_CENSUS", "terminal rejection census mismatch")
    if terminal["details"] != {
        "first_counter": 0,
        "last_counter": last_counter,
        "reason": "first_accepted_witness",
    }:
        raise RecordError("ROW_TERMINAL_DETAILS", "terminal details mismatch")
    if terminal["slot"] != accepted[0]["slot"]:
        raise RecordError("ROW_TERMINAL_SLOT", "slot mismatch")
    return dict(terminal)


def replay_ndjson_stream(data: bytes, registry: Mapping[str, Any]) -> dict[str, Any]:
    if not data.endswith(b"\n") or data.startswith(b"\xef\xbb\xbf"):
        raise RecordError("NDJSON_FRAMING", "one final LF and no BOM required")
    lines = data[:-1].split(b"\n")
    if not lines or any(not line for line in lines):
        raise RecordError("NDJSON_EMPTY_LINE", "empty NDJSON record")
    records: list[dict[str, Any]] = []
    for line in lines:
        try:
            text = line.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise RecordError("NDJSON_UTF8", str(exc)) from exc
        value = strict_json_loads(text)
        if not isinstance(value, dict) or jcs_bytes(value) != line:
            raise RecordError("NDJSON_NOT_CANONICAL", "record is not canonical JCS")
        records.append(value)
    terminal = records[-1]
    candidates = records[:-1]
    for record in candidates:
        replay_candidate_record(record, registry)
    validate_row_terminal(terminal, candidates)
    return {
        "slot": terminal["slot"],
        "candidate_records": len(candidates),
        "accepted_counter": candidates[-1]["counter"],
        "stream_sha256": sha256_hex(data),
        "stream_size_bytes": len(data),
    }


def replay_bound_streams(
    arithmetic_manifest: Mapping[str, Any],
    repository_root: Path,
    registry: Mapping[str, Any],
) -> list[dict[str, Any]]:
    streams = arithmetic_manifest.get("immutable_v6_streams")
    if not isinstance(streams, list) or len(streams) != 8:
        raise RecordError("STREAM_SET", "exactly eight immutable streams required")
    receipts: list[dict[str, Any]] = []
    for expected_slot, binding in enumerate(streams):
        if binding.get("slot") != expected_slot:
            raise RecordError("STREAM_SLOT_ORDER", str(expected_slot))
        source = repository_root / binding["path"]
        data = source.read_bytes()
        if len(data) != binding["size_bytes"] or sha256_hex(data) != binding["sha256"]:
            raise RecordError("STREAM_CUSTODY", binding["path"])
        replay = replay_ndjson_stream(data, registry)
        if replay["slot"] != expected_slot:
            raise RecordError("STREAM_SLOT", binding["path"])
        receipts.append(replay)
    return receipts


def _reject_opaque_authority(value: Any, pointer: str = "") -> None:
    if isinstance(value, Mapping):
        forbidden = {"replay_check", "verified", "valid", "success", "passed"}
        found = forbidden.intersection(value)
        if found:
            raise RecordError("CALLER_TRUTH_FORBIDDEN", f"{pointer}: {sorted(found)}")
        for key, item in value.items():
            _reject_opaque_authority(item, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_opaque_authority(item, f"{pointer}/{index}")


def validate_construction_record(
    record: Mapping[str, Any],
    registry: Mapping[str, Any],
    certificate_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    control_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    _exact_keys(
        record,
        ("schema", "record_id", "row", "terminal", "certificate", "control_triplet"),
        "CONSTRUCTION_RECORD_KEYS",
    )
    if record["schema"] != CONSTRUCTION_SCHEMA:
        raise RecordError("CONSTRUCTION_SCHEMA", str(record["schema"]))
    validate_frozen_row(record["row"], registry)
    terminal = validate_terminal(record["terminal"], registry)
    _reject_opaque_authority(record["certificate"], "/certificate")
    _reject_opaque_authority(record["control_triplet"], "/control_triplet")
    if terminal["code"] == "CONSTRUCTION_COMPLETE":
        if certificate_verifier is None or control_verifier is None:
            raise RecordError("SEMANTIC_VERIFIER_REQUIRED", "complete records require both verifiers")
        certificate_receipt = certificate_verifier(record["certificate"])
        control_receipt = control_verifier(record["control_triplet"])
        if certificate_receipt.get("status") != "accepted" or control_receipt.get("status") != "accepted":
            raise RecordError("COUNTERFEIT_CONSTRUCTION_COMPLETE", "typed replay did not accept")
    else:
        if record["certificate"] is not None or record["control_triplet"] is not None:
            raise RecordError("NONCOMPLETE_PAYLOAD", "rejection must not carry completion payload")
    return {
        "schema": "crypto.autoresearch.ectd_v7_construction_replay.v1",
        "record_id": record["record_id"],
        "terminal_code": terminal["code"],
        "status": "accepted",
    }


def validate_record(
    record: Mapping[str, Any],
    registry: Mapping[str, Any],
    *,
    certificate_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    control_verifier: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    row_candidates: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Closed public dispatcher: every admitted schema has one semantic path."""
    if not isinstance(record, Mapping):
        raise RecordError("RECORD_OBJECT_REQUIRED", "record must be an object")
    schema = record.get("schema")
    if schema in {V6_REJECTION_SCHEMA, V6_WITNESS_SCHEMA}:
        replay = replay_candidate_record(record, registry)
        return {"schema": schema, "status": "accepted", "record_sha256": sha256_hex(jcs_bytes(replay))}
    if schema == V6_ROW_TERMINAL_SCHEMA:
        if row_candidates is None:
            raise RecordError("ROW_CANDIDATES_REQUIRED", "row terminal requires its candidate stream")
        replay = validate_row_terminal(record, row_candidates)
        return {"schema": schema, "status": "accepted", "record_sha256": sha256_hex(jcs_bytes(replay))}
    if schema == TERMINAL_SCHEMA:
        replay = validate_terminal(record, registry)
        return {"schema": schema, "status": "accepted", "record_sha256": sha256_hex(jcs_bytes(replay))}
    if schema == CONSTRUCTION_SCHEMA:
        return validate_construction_record(
            record,
            registry,
            certificate_verifier=certificate_verifier,
            control_verifier=control_verifier,
        )
    raise RecordError("UNKNOWN_RECORD_SCHEMA", str(schema))


if __name__ == "__main__":
    raise SystemExit("static semantic library; downstream Executor owns conformance")
