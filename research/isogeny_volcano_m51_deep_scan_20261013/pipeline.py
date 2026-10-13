#!/usr/bin/env python3
"""Exact, fail-closed classification for the frozen m=51 deep scan.

The scientific command consumes an indexed sieve CSV, verifies every row
against the frozen 51-bit modeled PRP, and runs all candidates in one GP
process so the degree-2295 field and base-field embedding are initialized
once. Every input row receives a sealed certificate and record. Per-candidate
certificate parse or validation errors become explicit admitted ``GP_ERROR``
records; they are never dropped or replaced. A process-level GP failure or
nonempty diagnostic stream also leaves bound ``GP_ERROR`` artifacts, but its
runtime receipt is globally failed and the outer runner treats that attempt as
retryable infrastructure failure rather than admitted classification.

``controls`` is a disjoint, non-scientific replay.  It checks the crater and
all sixteen f=271 exclusions, the pilot-fiber exclusion, a positive
f=271->crater ascent, the excluded pilot bottom->parent ascent, and the known
parent's positive rank-two certificate.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
CLASSIFIER = HERE / "classify_recover.gp"
CENSUS = HERE / "floor271_orbits.csv"

FIELD_BITS = 51
FIELD_SIZE = 1 << FIELD_BITS
FIELD_MASK = FIELD_SIZE - 1
UINT64_MASK = (1 << 64) - 1
HASSE_RADIUS = math.isqrt(4 * FIELD_SIZE)
HASSE_MIN = FIELD_SIZE + 1 - HASSE_RADIUS
HASSE_MAX = FIELD_SIZE + 1 + HASSE_RADIUS
FIELD_ORBIT_SIZES = {1, 3, 17, 51}
N_EXPECTED = 2_251_799_852_369_764
F_PI = 32_756_041
PILOT_BOTTOM_RAW_B = 675_235_026_289_400
PILOT_BOTTOM_ORBIT = 99_224_513_745_505
PILOT_PARENT_ORBIT = 7_746_411_922_983
PRP_KEY_HEX = "c6ac26c5f692baa74a02c14f38de8e93bfe40c2d2ecbdcf7231ac6e79049d7b2"
GP_BINARY_SHA256 = "35b1fc1911407f5e893f5ab6b683ac660d164d5d84223b1d38645ebc96d43379"
GP_IMAGE_ID = "sha256:7436527cbf48e6e00a4b574c31725a90d5802160fb817a8f6bd94128d95a3cd4"
CENSUS_SHA256 = "bb4b64d5e8d53b323cd7493af435c738198b90b0ba8696316bb36e8709150fbe"
CENSUS_SOURCE_REVISION = "f0bdf9f739462766a9060532c59f9bfed69d00b1"
CENSUS_SOURCE_SHA256 = "a73ef01d0cb78be9f1c3df131c5598eae394541ce85a55fab5b33efaeca8d91b"
EMBED_SEED = 6_199_165_538_745_411_260
WITNESS_COUNT = 3
MAX_WITNESS_ATTEMPTS = 4096
EXTENSION_MODULUS_DECIMAL_SHA256 = "b0772b1c800814fefedd8eaf83e67c797649334ae701518e41f93a1200986d90"
EMBEDDING_X_DECIMAL_SHA256 = "97b69f5f34d9aaaa8257a88fd5a9ca46c9a2618fc7b59145e81427175778573a"
TARGET_PAIRS = 32
GP_STACK = "2G"
MAX_CERT_DECIMAL_DIGITS = 4096
GP_CHILD_ENV = {"LANG": "C", "LC_ALL": "C", "TZ": "UTC"}

FEISTEL_KEYS = (
    0x824FED8E0FDE5218, 0x00B2A56B05421B2D, 0xFD0F52502A0D3737,
    0x78CDB4C19DD24202, 0x722CFEF7C6D0EA93, 0xE007ABB4C970F252,
    0xA56276B6D4746BED, 0x08E8F877EC4098BC, 0x02EA18FD04E1DD08,
    0xEFB6477DE16EC1DA, 0xAF1A485BBAF930E9, 0xC80FF63F19D1D47C,
)
EXPECTED_F271 = (
    623_162_416_261, 25_640_824_825_979, 30_885_819_784_827,
    57_318_330_399_736, 67_694_307_705_004, 72_881_269_935_803,
    115_635_957_935_040, 116_461_223_646_592, 116_511_665_573_478,
    121_360_481_466_206, 130_246_110_195_364, 147_686_731_444_433,
    213_718_369_432_541, 237_711_860_122_495, 360_860_333_097_189,
    370_376_419_722_289,
)

BENIGN = {
    "SIEVE_FALSE_POSITIVE_ORDER", "KNOWN_CRATER", "KNOWN_F271",
    "DIRECT_PARENT", "EXCLUDED_PILOT_ORBIT", "CERTIFIED_BOTTOM_PARENT",
}
FATAL = {
    "UNKNOWN_WITNESS_EXHAUSTED", "UNKNOWN_EMBEDDING_EXHAUSTED",
    "TARGET_RANK2_WITNESS_EXHAUSTED", "INVALID_CERTIFICATE",
    "ASCENT_FAILED", "WRONG_ORBIT_SIZE", "WRONG_PARENT_ORDER", "GP_ERROR",
}
CONTROL_ONLY = {"POSITIVE_CONTROL_F271_TO_CRATER", "POSITIVE_CONTROL_BOTTOM_PARENT"}
SEARCH_HEADER = ("global_index", "b", "x0", "x1", "x2")
CERT_SIGNED_INTEGER_FIELDS = {"class_trace", "class_discriminant", "extension_trace"}
CERT_TEXT_FIELDS = {
    "schema", "f_pi_factorization", "f271_census_sha256",
    "f271_census_source_revision", "f271_census_source_sha256",
    "direct_parent_point_1_xset", "target_rank2_point_1_xset",
    "source_conductor_derivation", "target_conductor_derivation",
    "f271_census_exclusion_role", "edge_direction",
    "edge_direction_derivation", "pilot_exclusion_scope", "pipeline_error",
    "gp_log_sha256", "status",
}


def certificate_allowed_fields() -> set[str]:
    try:
        classifier_source = CLASSIFIER.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PipelineError(f"cannot read classifier schema: {exc}") from exc
    fields = set(re.findall(r'emit\("([^"]+)"', classifier_source))
    fields.update({"pipeline_error", "gp_log_sha256"})
    fields.update(
        f"witness_{number}_{suffix}"
        for number in range(1, WITNESS_COUNT + 1)
        for suffix in (
            "attempt", "raw_x_int", "order_2712_x_int", "order_271_x_int",
            "mul_271_nonzero", "mul_2712_zero",
        )
    )
    return fields


CERT_TERMINAL_FIELDS = {"admitted_failure", "status"}
CERT_BASE_FIELDS = CERT_TERMINAL_FIELDS | {
    "schema", "global_index", "source_b", "source_a2", "source_order",
    "expected_order", "source_orbit_rep", "source_orbit_size",
    "source_to_orbit_rep_frobenius_power", "field_degree", "field_modulus_bits",
    "class_trace", "class_discriminant", "f_pi", "f_pi_factorization",
    "f_pi_factor_primality", "class_discriminant_271_valuation",
    "kernel_extension_coprime_to_271", "maximal_order_class_number",
    "f271_census_sha256", "f271_census_source_revision",
    "f271_census_source_sha256", "f271_census_complete_orbit_count", "control_mode",
}
CERT_DEEP_FIELDS = CERT_BASE_FIELDS | {
    "kernel_prime", "kernel_field_degree", "kernel_extension_degree", "kernel_twist",
    "extension_trace", "extension_group_271_valuation", "other_twist_271_valuation",
    "extension_group_cofactor", "extension_modulus_bits", "embedding_seed",
    "embedding_attempts", "embedding_x_int", "embedding_modulus_check",
    "embedded_b_int", "witness_seed", "target_witness_seed",
    "witness_count_required", "witness_attempt_cap",
}
CERT_SUMMARY_FIELDS = CERT_DEEP_FIELDS | {
    "witness_attempts_used", "witness_count_found", "witness_other_twist_skips",
    "witness_infinity_skips",
}
CERT_DETAIL_FIELDS = CERT_SUMMARY_FIELDS | {
    f"witness_{number}_{suffix}"
    for number in range(1, WITNESS_COUNT + 1)
    for suffix in (
        "attempt", "raw_x_int", "order_2712_x_int", "order_271_x_int",
        "mul_271_nonzero", "mul_2712_zero",
    )
}
CERT_DIRECT_FIELDS = CERT_SUMMARY_FIELDS | {
    "direct_parent_point_1_x_int", "direct_parent_point_2_x_int",
    "direct_parent_point_1_xset_count", "direct_parent_point_1_xset",
    "direct_parent_point_2_absent_from_point_1_subgroup", "source_f_E",
    "source_conductor_derivation",
}
CERT_FULL_FIELDS = CERT_DETAIL_FIELDS | {
    "source_f_E", "source_conductor_derivation", "f271_census_exclusion_role",
    "kernel_x_int", "kernel_mul_271_zero", "kernel_frobenius_x_multiplier_abs",
    "kernel_frobenius_stable", "kernel_sums_agree", "velu_half_kernel_sum_int",
    "velu_half_kernel_sum_frobenius_fixed", "raw_codomain_a1",
    "raw_codomain_a2", "raw_codomain_a3", "raw_codomain_a4_int",
    "raw_codomain_a6_int", "normalization_y_translation_int",
    "raw_codomain_delta_int", "raw_codomain_delta_nonzero",
    "raw_codomain_frobenius_fixed", "raw_target_b", "codomain_minpoly_bits",
    "target_b", "target_a2", "target_order", "target_orbit_rep",
    "target_orbit_size", "raw_target_to_rep_frobenius_power", "target_f_E",
    "target_rank2_attempts_used", "target_rank2_other_twist_skips",
    "target_rank2_infinity_skips", "target_rank2_point_1_x_int",
    "target_rank2_point_2_x_int", "target_rank2_point_1_mul_271_zero",
    "target_rank2_point_2_mul_271_zero", "target_rank2_point_1_xset_count",
    "target_rank2_point_1_xset",
    "target_rank2_point_2_absent_from_point_1_subgroup",
    "target_conductor_derivation", "coprime_conductor_component_preserved",
    "coprime_conductor_preservation_check", "edge_degree", "edge_separable",
    "edge_direction", "edge_direction_derivation", "map_evaluator_serialized",
    "dual_serialized", "transfer_claim_permitted",
}
CERT_GP_ERROR_FIELDS = CERT_TERMINAL_FIELDS | {
    "schema", "global_index", "source_b", "source_a2", "expected_order",
    "field_degree", "f_pi", "class_discriminant_271_valuation",
    "kernel_extension_coprime_to_271", "maximal_order_class_number",
    "f271_census_sha256", "f271_census_source_revision",
    "f271_census_source_sha256", "f271_census_complete_orbit_count",
    "control_mode", "pipeline_error", "gp_log_sha256",
}


def certificate_field_options(status: str | None, scope: str | None) -> tuple[set[str], ...]:
    if status in {"SIEVE_FALSE_POSITIVE_ORDER", "KNOWN_CRATER", "KNOWN_F271"}:
        return (CERT_BASE_FIELDS,)
    if status == "DIRECT_PARENT":
        return (CERT_DIRECT_FIELDS,)
    if status in {"CERTIFIED_BOTTOM_PARENT", "POSITIVE_CONTROL_F271_TO_CRATER"}:
        return (CERT_FULL_FIELDS,)
    if status == "POSITIVE_CONTROL_BOTTOM_PARENT":
        return (CERT_FULL_FIELDS | {"pilot_exclusion_scope"},)
    if status == "EXCLUDED_PILOT_ORBIT":
        if scope == "source-orbit":
            return (CERT_BASE_FIELDS | {"pilot_exclusion_scope"},)
        if scope == "entire-parent-fiber":
            return (CERT_FULL_FIELDS | {"pilot_exclusion_scope"},)
        return ()
    if status == "UNKNOWN_EMBEDDING_EXHAUSTED":
        return (CERT_BASE_FIELDS | {"embedding_attempts"},)
    if status == "UNKNOWN_WITNESS_EXHAUSTED":
        return (CERT_SUMMARY_FIELDS,)
    if status in {"TARGET_RANK2_WITNESS_EXHAUSTED", "ASCENT_FAILED"}:
        return (CERT_DETAIL_FIELDS,)
    if status == "INVALID_CERTIFICATE":
        return (CERT_SUMMARY_FIELDS, CERT_DETAIL_FIELDS, CERT_FULL_FIELDS)
    if status == "WRONG_ORBIT_SIZE":
        return (CERT_BASE_FIELDS, CERT_FULL_FIELDS)
    if status == "WRONG_PARENT_ORDER":
        return (CERT_DETAIL_FIELDS, CERT_FULL_FIELDS)
    if status == "GP_ERROR":
        return (CERT_GP_ERROR_FIELDS,)
    return ()


class PipelineError(RuntimeError):
    pass


@dataclass(frozen=True)
class Hit:
    global_index: int
    b: int
    x0: int
    x1: int
    x2: int

    def binding(self) -> dict[str, int]:
        return {
            "global_index": self.global_index, "b": self.b,
            "x0": self.x0, "x1": self.x1, "x2": self.x2,
        }


@dataclass(frozen=True)
class Job:
    label: str
    hit: Hit
    source_seed: int
    target_seed: int
    control_mode: int
    expected_status: str | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def write_json(path: Path, value: Any) -> None:
    write_new(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def write_jsonl(path: Path, values: Iterable[dict[str, Any]]) -> None:
    payload = b"".join(
        (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
        for value in values
    )
    write_new(path, payload)


def uint(text: str, context: str, maximum: int = UINT64_MASK) -> int:
    if (
        not text.isascii()
        or not text.isdecimal()
        or len(text) > 20
        or (text.startswith("0") and text != "0")
    ):
        raise PipelineError(f"{context}: not a canonical unsigned decimal")
    try:
        value = int(text)
    except ValueError as exc:
        raise PipelineError(f"{context}: not a bounded unsigned decimal") from exc
    if value > maximum:
        raise PipelineError(f"{context}: outside range")
    return value


def mix64(value: int) -> int:
    value &= UINT64_MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & UINT64_MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & UINT64_MASK
    return (value ^ (value >> 31)) & UINT64_MASK


def permuted_b(index: int) -> int:
    if not 0 <= index < FIELD_SIZE:
        raise PipelineError("global index outside PRP domain")
    left, right = index >> 25, index & ((1 << 25) - 1)
    left_bits, right_bits = 26, 25
    for key in FEISTEL_KEYS:
        f = mix64(right ^ key ^ (right_bits << 56)) & ((1 << left_bits) - 1)
        left, right = right, left ^ f
        left_bits, right_bits = right_bits, left_bits
    return (left << 25) | right


def load_hits(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    seen_b: set[int] = set()
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != SEARCH_HEADER:
            raise PipelineError(f"{path}: expected header {SEARCH_HEADER}")
        for line_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise PipelineError(f"{path}:{line_number}: malformed row")
            values = {name: uint(row[name], f"{path}:{line_number}:{name}", FIELD_MASK if name != "global_index" else UINT64_MASK) for name in SEARCH_HEADER}
            hit = Hit(**values)
            if hits and hit.global_index <= hits[-1].global_index:
                raise PipelineError(f"{path}:{line_number}: indices not strictly increasing")
            if hit.b == 0 or hit.b != permuted_b(hit.global_index):
                raise PipelineError(f"{path}:{line_number}: b/index PRP binding failed")
            if hit.b in seen_b:
                raise PipelineError(f"{path}:{line_number}: duplicate exact b")
            seen_b.add(hit.b)
            hits.append(hit)
    return hits


def derive_seed(domain: bytes, hit: Hit) -> int:
    h = hashlib.sha256()
    h.update(domain)
    h.update(bytes.fromhex(PRP_KEY_HEX))
    for value in (hit.global_index, hit.b, hit.x0, hit.x1, hit.x2):
        h.update(value.to_bytes(8, "big"))
    seed = int.from_bytes(h.digest()[:8], "big") & ((1 << 63) - 1)
    return seed or 1


def control_seed(label: str, target: bool) -> int:
    domain = b"m51-deep-scan/v1/control-target/" if target else b"m51-deep-scan/v1/control-source/"
    seed = int.from_bytes(hashlib.sha256(domain + label.encode()).digest()[:8], "big") & ((1 << 63) - 1)
    return seed or 1


def check_census() -> None:
    if sha256_file(CENSUS) != CENSUS_SHA256:
        raise PipelineError("f=271 census hash mismatch")
    with CENSUS.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if tuple(rows[0].keys()) != ("orbit_id", "b", "a2", "orbit_size", "f_E"):
        raise PipelineError("f=271 census schema mismatch")
    reps = tuple(int(row["b"]) for row in rows)
    if reps != EXPECTED_F271 or len(set(reps)) != 16:
        raise PipelineError("f=271 census is not the frozen complete 16-orbit set")
    for number, row in enumerate(rows, 1):
        if row != {"orbit_id": str(number), "b": str(EXPECTED_F271[number-1]), "a2": "0", "orbit_size": "17", "f_E": "271"}:
            raise PipelineError(f"f=271 census row {number} mismatch")


def parse_certificate(path: Path) -> tuple[dict[str, str], list[str]]:
    raw = path.read_text()
    if not raw or not raw.endswith("\n"):
        raise PipelineError("certificate empty or not newline terminated")
    cert: dict[str, str] = {}
    keys: list[str] = []
    for number, line in enumerate(raw.splitlines(), 1):
        if "=" not in line:
            raise PipelineError(f"certificate line {number} lacks separator")
        key, value = line.split("=", 1)
        if not key or key in cert:
            raise PipelineError(f"certificate duplicate/empty key at line {number}")
        cert[key] = value
        keys.append(key)
    if keys[-1] != "status" or keys.count("status") != 1 or keys.count("admitted_failure") != 1:
        raise PipelineError("certificate must have one terminal status and admitted_failure")
    return cert, keys


def cert_int(cert: dict[str, str], key: str) -> int:
    if key not in cert:
        raise PipelineError(f"certificate missing {key}")
    text = cert[key]
    digits = text[1:] if text.startswith("-") else text
    if (
        not digits
        or not digits.isascii()
        or not digits.isdecimal()
        or len(digits) > MAX_CERT_DECIMAL_DIGITS
        or (digits != "0" and digits.startswith("0"))
        or text == "-0"
    ):
        raise PipelineError(f"certificate {key} is not integer")
    try:
        return int(text)
    except ValueError as exc:
        raise PipelineError(f"certificate {key} is not a bounded integer") from exc


def cert_uint_vector(cert: dict[str, str], key: str, expected_length: int) -> list[int]:
    value = cert.get(key)
    if not isinstance(value, str) or not value.startswith("[") or not value.endswith("]"):
        raise PipelineError(f"certificate {key} is not a GP integer vector")
    body = value[1:-1]
    pieces = [] if not body else body.split(", ")
    if len(pieces) != expected_length:
        raise PipelineError(f"certificate {key} has wrong vector length")
    parsed: list[int] = []
    for piece in pieces:
        if (
            not piece.isascii()
            or not piece.isdecimal()
            or len(piece) > MAX_CERT_DECIMAL_DIGITS
            or (piece != "0" and piece.startswith("0"))
        ):
            raise PipelineError(f"certificate {key} has a noncanonical entry")
        try:
            parsed.append(int(piece))
        except ValueError as exc:
            raise PipelineError(
                f"certificate {key} has an unbounded integer entry"
            ) from exc
    if len(set(parsed)) != len(parsed):
        raise PipelineError(f"certificate {key} has duplicate x values")
    return parsed


def validate_codomain_minpoly_bits(value: int, target_orbit_size: int) -> None:
    if (
        value <= 0
        or value.bit_length() - 1 != target_orbit_size
        or value & 1 != 1
    ):
        raise PipelineError(
            "codomain minimal polynomial is not the canonical monic degree/orbit encoding"
        )


def validate_certificate(cert: dict[str, str], job: Job, scientific: bool) -> None:
    unknown_fields = set(cert) - certificate_allowed_fields()
    if unknown_fields:
        raise PipelineError(f"certificate has unknown fields {sorted(unknown_fields)}")
    status = cert.get("status")
    allowed = BENIGN | FATAL | (set() if scientific else CONTROL_ONLY)
    if status not in allowed:
        raise PipelineError(f"unknown or forbidden status {status!r}")
    field_options = certificate_field_options(status, cert.get("pilot_exclusion_scope"))
    if not any(set(cert) == option for option in field_options):
        closest = min(
            field_options,
            key=lambda option: len(set(cert) ^ option),
            default=set(),
        )
        raise PipelineError(
            "certificate fields differ from terminal-status schema; "
            f"missing={sorted(closest-set(cert))}, extra={sorted(set(cert)-closest)}"
        )
    admitted = cert_int(cert, "admitted_failure")
    if admitted not in (0, 1) or bool(admitted) != (status in FATAL):
        raise PipelineError("certificate status/admitted_failure mismatch")
    for key in set(cert) - CERT_TEXT_FIELDS:
        parsed = cert_int(cert, key)
        if key not in CERT_SIGNED_INTEGER_FIELDS and parsed < 0:
            raise PipelineError(f"certificate {key} is negative")
    source_b = cert_int(cert, "source_b")
    if not 1 <= source_b <= FIELD_MASK:
        raise PipelineError("source coefficient is outside nonzero GF(2^51)")
    fixed = {
        "schema": "m51-deep-endpoint-certificate/v1",
        "global_index": str(job.hit.global_index), "source_b": str(job.hit.b),
        "source_a2": "0", "expected_order": str(N_EXPECTED),
        "field_degree": "51", "f_pi": str(F_PI),
        "f271_census_sha256": CENSUS_SHA256,
        "f271_census_source_revision": CENSUS_SOURCE_REVISION,
        "f271_census_source_sha256": CENSUS_SOURCE_SHA256,
        "f271_census_complete_orbit_count": "16",
        "control_mode": str(job.control_mode),
    }
    if status != "GP_ERROR":
        fixed.update(
            field_modulus_bits=str((1 << 51) + (1 << 6) + (1 << 3) + 2 + 1),
            class_trace=str((1 << 51) + 1 - N_EXPECTED),
            class_discriminant=str(-7 * F_PI**2),
            f_pi_factorization="271*120871",
            f_pi_factor_primality="1",
        )
    for key, expected in fixed.items():
        if cert.get(key) != expected:
            raise PipelineError(f"certificate {key}={cert.get(key)!r}, expected {expected!r}")
    seed_fields = {
        "embedding_seed": EMBED_SEED,
        "witness_seed": job.source_seed,
        "target_witness_seed": job.target_seed,
        "witness_count_required": WITNESS_COUNT,
        "witness_attempt_cap": MAX_WITNESS_ATTEMPTS,
    }
    deep_seed_statuses = {
        "DIRECT_PARENT", "CERTIFIED_BOTTOM_PARENT",
        "POSITIVE_CONTROL_BOTTOM_PARENT", "POSITIVE_CONTROL_F271_TO_CRATER",
        "UNKNOWN_WITNESS_EXHAUSTED", "TARGET_RANK2_WITNESS_EXHAUSTED",
        "INVALID_CERTIFICATE", "ASCENT_FAILED", "WRONG_PARENT_ORDER",
    }
    require_seed_fields = status in deep_seed_statuses or (
        status == "EXCLUDED_PILOT_ORBIT"
        and cert.get("pilot_exclusion_scope") == "entire-parent-fiber"
    )
    if require_seed_fields or set(seed_fields) & set(cert):
        for key, expected in seed_fields.items():
            if cert.get(key) != str(expected):
                raise PipelineError(
                    f"certificate {key} is not the deterministic frozen value"
                )
    if "embedding_seed" in cert:
        for key, expected in {
            "kernel_prime": 271,
            "kernel_field_degree": 51 * 45,
            "kernel_extension_degree": 45,
            "kernel_twist": 1,
            "extension_group_271_valuation": 2,
            "other_twist_271_valuation": 0,
            "embedding_modulus_check": 1,
            "embedding_attempts": 1,
        }.items():
            if cert_int(cert, key) != expected:
                raise PipelineError(f"extension replay field {key} failed")
        q = 1 << FIELD_BITS
        base_trace = q + 1 - N_EXPECTED
        trace_previous, extension_trace = 2, base_trace
        for _ in range(2, 46):
            trace_previous, extension_trace = (
                extension_trace,
                base_trace * extension_trace - q * trace_previous,
            )
        if cert_int(cert, "extension_trace") != extension_trace:
            raise PipelineError("extension trace differs from recurrence")
        extension_order = q**45 + 1 + extension_trace
        if cert_int(cert, "extension_group_cofactor") != extension_order // (271**2):
            raise PipelineError("extension cofactor differs from trace/order")
        if hashlib.sha256(cert["extension_modulus_bits"].encode()).hexdigest() != EXTENSION_MODULUS_DECIMAL_SHA256:
            raise PipelineError("extension polynomial differs from pinned GP field")
        if hashlib.sha256(cert["embedding_x_int"].encode()).hexdigest() != EMBEDDING_X_DECIMAL_SHA256:
            raise PipelineError("base-field embedding differs from pinned replay")
        if cert_int(cert, "embedded_b_int") <= 0:
            raise PipelineError("embedded source coefficient is not positive")
    elif "embedding_attempts" in cert:
        attempts = cert_int(cert, "embedding_attempts")
        if (
            not 1 <= attempts <= MAX_WITNESS_ATTEMPTS
            or (
                status == "UNKNOWN_EMBEDDING_EXHAUSTED"
                and attempts != MAX_WITNESS_ATTEMPTS
            )
        ):
            raise PipelineError("exhausted embedding attempt count is invalid")
    for key, expected in {
        "class_discriminant_271_valuation": 2,
        "kernel_extension_coprime_to_271": 1,
        "maximal_order_class_number": 1,
    }.items():
        if cert_int(cert, key) != expected:
            raise PipelineError(f"certificate arithmetic lemma {key} failed")
    if status != "GP_ERROR":
        source_order = cert_int(cert, "source_order")
        source_rep = cert_int(cert, "source_orbit_rep")
        source_orbit_size = cert_int(cert, "source_orbit_size")
        if not HASSE_MIN <= source_order <= HASSE_MAX:
            raise PipelineError("source order is outside the exact Hasse interval")
        if source_order % 2:
            raise PipelineError("source order is odd despite rational 2-torsion")
        if not 1 <= source_rep <= FIELD_MASK:
            raise PipelineError("source orbit representative is outside GF(2^51)")
        if source_orbit_size not in FIELD_ORBIT_SIZES:
            raise PipelineError("source orbit size is not a divisor of 51")
        if status == "SIEVE_FALSE_POSITIVE_ORDER":
            if source_order == N_EXPECTED:
                raise PipelineError("in-class curve was labeled a sieve false positive")
        elif source_order != N_EXPECTED:
            raise PipelineError("non-class curve received an in-class status")
        source_power = cert_int(cert, "source_to_orbit_rep_frobenius_power")
        if source_orbit_size <= 0 or not 0 <= source_power < source_orbit_size:
            raise PipelineError("source orbit replay metadata is out of range")

    if "witness_attempts_used" in cert:
        attempts_used = cert_int(cert, "witness_attempts_used")
        count_found = cert_int(cert, "witness_count_found")
        other_skips = cert_int(cert, "witness_other_twist_skips")
        infinity_skips = cert_int(cert, "witness_infinity_skips")
        if (
            not 0 <= attempts_used <= MAX_WITNESS_ATTEMPTS
            or not 0 <= count_found <= WITNESS_COUNT
            or other_skips < 0
            or infinity_skips < 0
            or other_skips + infinity_skips > attempts_used
        ):
            raise PipelineError("source witness counters are inconsistent")
    if CERT_DETAIL_FIELDS <= set(cert):
        if cert_int(cert, "witness_count_found") != WITNESS_COUNT:
            raise PipelineError("detailed source witness set is incomplete")
        previous_attempt = 0
        for witness in range(1, WITNESS_COUNT + 1):
            attempt = cert_int(cert, f"witness_{witness}_attempt")
            if not previous_attempt < attempt <= MAX_WITNESS_ATTEMPTS:
                raise PipelineError("source witness attempt indices are not increasing")
            previous_attempt = attempt
            for suffix in ("raw_x_int", "order_2712_x_int", "order_271_x_int"):
                if cert_int(cert, f"witness_{witness}_{suffix}") < 0:
                    raise PipelineError("source witness x-coordinate is negative")
            if (
                cert_int(cert, f"witness_{witness}_mul_271_nonzero") != 1
                or cert_int(cert, f"witness_{witness}_mul_2712_zero") != 1
            ):
                raise PipelineError("source order-271^2 witness flags failed")
        if cert_int(cert, "witness_attempts_used") != previous_attempt:
            raise PipelineError("source witness attempt total differs from witness 3")
    if status == "UNKNOWN_WITNESS_EXHAUSTED" and (
        cert_int(cert, "witness_attempts_used") != MAX_WITNESS_ATTEMPTS
        or cert_int(cert, "witness_count_found") >= WITNESS_COUNT
    ):
        raise PipelineError("exhausted source witness status is inconsistent")
    if CERT_FULL_FIELDS <= set(cert):
        full_constants = {
            "source_order": N_EXPECTED,
            "source_orbit_size": 17 if job.control_mode == 2 else 51,
            "source_f_E": 271 if job.control_mode == 2 else F_PI,
            "kernel_mul_271_zero": 1,
            "kernel_frobenius_stable": 1,
            "kernel_sums_agree": 1,
            "velu_half_kernel_sum_frobenius_fixed": 1,
            "raw_codomain_a1": 1,
            "raw_codomain_a2": 0,
            "raw_codomain_a3": 0,
            "raw_codomain_delta_nonzero": 1,
            "raw_codomain_frobenius_fixed": 1,
            "target_a2": 0,
            "target_f_E": 1 if job.control_mode == 2 else 120_871,
            "target_rank2_point_1_mul_271_zero": 1,
            "target_rank2_point_2_mul_271_zero": 1,
            "target_rank2_point_1_xset_count": 135,
            "target_rank2_point_2_absent_from_point_1_subgroup": 1,
            "coprime_conductor_component_preserved": 120_871,
            "coprime_conductor_preservation_check": 1,
            "edge_degree": 271,
            "edge_separable": 1,
            "map_evaluator_serialized": 0,
            "dual_serialized": 0,
            "transfer_claim_permitted": 0,
        }
        for key, expected in full_constants.items():
            if cert_int(cert, key) != expected:
                raise PipelineError(f"full-edge fixed field {key} changed")
        unsigned_fields = (
            "kernel_x_int", "raw_codomain_a4_int", "raw_codomain_a6_int",
            "normalization_y_translation_int", "raw_codomain_delta_int", "raw_target_b",
            "codomain_minpoly_bits", "target_b", "target_a2", "target_order",
            "target_orbit_rep", "target_orbit_size",
            "raw_target_to_rep_frobenius_power", "target_rank2_attempts_used",
            "target_rank2_other_twist_skips", "target_rank2_infinity_skips",
            "target_rank2_point_1_x_int", "target_rank2_point_2_x_int",
        )
        if any(cert_int(cert, key) < 0 for key in unsigned_fields):
            raise PipelineError("full-edge certificate has a negative unsigned field")
        if (
            cert_int(cert, "raw_target_b") == 0
            or cert_int(cert, "codomain_minpoly_bits") == 0
            or cert_int(cert, "target_b") == 0
        ):
            raise PipelineError("full-edge target/minimal-polynomial evidence is zero")
        for key in ("raw_target_b", "target_b", "target_orbit_rep"):
            if not 1 <= cert_int(cert, key) <= FIELD_MASK:
                raise PipelineError(f"full-edge {key} is outside nonzero GF(2^51)")
        target_order = cert_int(cert, "target_order")
        if not HASSE_MIN <= target_order <= HASSE_MAX:
            raise PipelineError("target order is outside the exact Hasse interval")
        if target_order % 2:
            raise PipelineError("target order is odd despite rational 2-torsion")
        target_orbit_size = cert_int(cert, "target_orbit_size")
        if target_orbit_size not in FIELD_ORBIT_SIZES:
            raise PipelineError("target orbit size is not a divisor of 51")
        validate_codomain_minpoly_bits(
            cert_int(cert, "codomain_minpoly_bits"), target_orbit_size
        )
        if cert_int(cert, "kernel_x_int") != cert_int(
            cert, "witness_1_order_271_x_int"
        ):
            raise PipelineError("serialized kernel differs from witness 1")
        if not 1 <= cert_int(cert, "kernel_frobenius_x_multiplier_abs") <= 135:
            raise PipelineError("kernel Frobenius multiplier is out of range")
        velu_sum = cert_int(cert, "velu_half_kernel_sum_int")
        if (
            velu_sum < 0
            or cert_int(cert, "raw_codomain_a4_int") != velu_sum
            or cert_int(cert, "normalization_y_translation_int") != velu_sum
            or cert_int(cert, "raw_codomain_delta_int") == 0
            or cert_int(cert, "raw_codomain_a6_int")
            != (cert_int(cert, "embedded_b_int") ^ velu_sum)
        ):
            raise PipelineError("full-edge quotient replay fields are inconsistent")
        if cert_int(cert, "target_a2") != 0:
            raise PipelineError("normalized target has nonzero a2")
        if cert_int(cert, "target_orbit_rep") != cert_int(cert, "target_b"):
            raise PipelineError("target canonical representative differs from target_b")
        target_power = cert_int(cert, "raw_target_to_rep_frobenius_power")
        if target_orbit_size <= 0 or not 0 <= target_power < target_orbit_size:
            raise PipelineError("target orbit replay metadata is out of range")
        target_attempts = cert_int(cert, "target_rank2_attempts_used")
        target_other = cert_int(cert, "target_rank2_other_twist_skips")
        target_infinity = cert_int(cert, "target_rank2_infinity_skips")
        if (
            not 1 <= target_attempts <= MAX_WITNESS_ATTEMPTS
            or target_other + target_infinity > target_attempts
        ):
            raise PipelineError("target rank-two counters are inconsistent")
        target_xset = cert_uint_vector(cert, "target_rank2_point_1_xset", 135)
        if (
            cert_int(cert, "target_rank2_point_1_x_int") not in target_xset
            or cert_int(cert, "target_rank2_point_2_x_int") in target_xset
        ):
            raise PipelineError("target rank-two independence certificate failed")
        if cert_int(cert, "coprime_conductor_component_preserved") != 120_871:
            raise PipelineError("coprime conductor component changed")
        if cert.get("edge_direction") != "ascending" or cert.get(
            "edge_direction_derivation"
        ) != "depth-one-271-volcano-inert-prime-unique-order271-subgroup":
            raise PipelineError("edge direction certificate changed")
        derivations = (
            {
                "source_conductor_derivation": (
                    "control-order2712-witness-plus-frozen-source-binding"
                ),
                "f271_census_exclusion_role": "control-source-binding",
                "target_conductor_derivation": (
                    "complete-crater-binding-plus-independent-271-torsion"
                ),
            }
            if job.control_mode == 2
            else {
                "source_conductor_derivation": (
                    "exact-order2712-source-plus-Fq-stable-271-kernel-plus-"
                    "certified-f120871-target"
                ),
                "f271_census_exclusion_role": "corroborating-not-load-bearing",
                "target_conductor_derivation": (
                    "crater-exclusion-plus-independent-271-torsion"
                ),
            }
        )
        if any(cert.get(key) != value for key, value in derivations.items()):
            raise PipelineError("full-edge conductor derivation changed")

    if status == "WRONG_ORBIT_SIZE":
        if set(cert) == CERT_BASE_FIELDS:
            expected_size = 17 if job.control_mode == 2 else 51
            if cert_int(cert, "source_orbit_size") == expected_size:
                raise PipelineError("WRONG_ORBIT_SIZE has the expected source size")
        elif set(cert) == CERT_FULL_FIELDS:
            expected_size = 1 if job.control_mode == 2 else 51
            if cert_int(cert, "target_orbit_size") == expected_size:
                raise PipelineError("WRONG_ORBIT_SIZE has the expected target size")
    if status == "WRONG_PARENT_ORDER" and set(cert) == CERT_FULL_FIELDS:
        if cert_int(cert, "target_order") == N_EXPECTED and cert_int(cert, "target_a2") == 0:
            raise PipelineError("WRONG_PARENT_ORDER has the expected parent model/order")
    if status == "INVALID_CERTIFICATE" and set(cert) == CERT_FULL_FIELDS:
        target_rep = cert_int(cert, "target_orbit_rep")
        target_f = cert_int(cert, "target_f_E")
        explains_invalid = (
            (job.control_mode == 2 and (target_rep != 1 or target_f != 1))
            or (job.control_mode == 1 and target_rep != PILOT_PARENT_ORBIT)
        )
        if not explains_invalid:
            raise PipelineError("full INVALID_CERTIFICATE has no terminal contradiction")

    def validate_deep_edge(
        source_f: int, source_orbit_size: int, target_f: int, target_orbit_size: int
    ) -> None:
        required = {
            "source_order": N_EXPECTED, "source_orbit_size": source_orbit_size,
            "source_f_E": source_f, "witness_count_found": WITNESS_COUNT,
            "kernel_prime": 271, "kernel_extension_degree": 45,
            "extension_group_271_valuation": 2, "other_twist_271_valuation": 0,
            "kernel_mul_271_zero": 1, "kernel_frobenius_stable": 1,
            "kernel_sums_agree": 1,
            "velu_half_kernel_sum_frobenius_fixed": 1,
            "raw_codomain_a1": 1, "raw_codomain_a2": 0,
            "raw_codomain_a3": 0, "raw_codomain_delta_nonzero": 1,
            "raw_codomain_frobenius_fixed": 1, "target_order": N_EXPECTED,
            "target_a2": 0, "target_orbit_size": target_orbit_size,
            "target_f_E": target_f,
            "target_rank2_point_1_mul_271_zero": 1,
            "target_rank2_point_2_mul_271_zero": 1,
            "target_rank2_point_1_xset_count": 135,
            "target_rank2_point_2_absent_from_point_1_subgroup": 1,
            "coprime_conductor_preservation_check": 1,
            "coprime_conductor_component_preserved": 120_871,
            "edge_degree": 271, "edge_separable": 1,
            "map_evaluator_serialized": 0, "dual_serialized": 0,
            "transfer_claim_permitted": 0,
        }
        for key, expected in required.items():
            if cert_int(cert, key) != expected:
                raise PipelineError(f"certified pair failed {key}")
        velu_sum = cert_int(cert, "velu_half_kernel_sum_int")
        if cert_int(cert, "raw_codomain_a4_int") != velu_sum or cert_int(cert, "normalization_y_translation_int") != velu_sum or cert_int(cert, "raw_codomain_delta_int") == 0:
            raise PipelineError("certified pair raw quotient/normalization certificate failed")
        if cert_int(cert, "raw_codomain_a6_int") != (
            cert_int(cert, "embedded_b_int") ^ velu_sum
        ):
            raise PipelineError("raw quotient a6 differs from B+v")
        if cert_int(cert, "target_orbit_rep") != cert_int(cert, "target_b"):
            raise PipelineError("target canonical representative mismatch")
        if cert_int(cert, "kernel_x_int") != cert_int(cert, "witness_1_order_271_x_int"):
            raise PipelineError("serialized kernel differs from witness 1")
        frobenius_u = cert_int(cert, "kernel_frobenius_x_multiplier_abs")
        if not 1 <= frobenius_u <= 135:
            raise PipelineError("kernel Frobenius multiplier is out of range")
        target_power = cert_int(cert, "raw_target_to_rep_frobenius_power")
        if not 0 <= target_power < target_orbit_size:
            raise PipelineError("target orbit replay metadata is out of range")
        target_attempts = cert_int(cert, "target_rank2_attempts_used")
        target_other = cert_int(cert, "target_rank2_other_twist_skips")
        target_infinity = cert_int(cert, "target_rank2_infinity_skips")
        if (
            not 1 <= target_attempts <= MAX_WITNESS_ATTEMPTS
            or target_other < 0
            or target_infinity < 0
            or target_other + target_infinity > target_attempts
        ):
            raise PipelineError("target rank-two counters are inconsistent")
        target_xset = cert_uint_vector(cert, "target_rank2_point_1_xset", 135)
        if (
            cert_int(cert, "target_rank2_point_1_x_int") not in target_xset
            or cert_int(cert, "target_rank2_point_2_x_int") in target_xset
        ):
            raise PipelineError("target rank-two independence certificate failed")
        for key in (
            "raw_codomain_a6_int", "raw_target_b", "codomain_minpoly_bits",
            "target_rank2_point_1_x_int", "target_rank2_point_2_x_int",
        ):
            if cert_int(cert, key) < 0:
                raise PipelineError(f"certificate {key} is negative")
        if cert.get("edge_direction") != "ascending" or cert.get(
            "edge_direction_derivation"
        ) != "depth-one-271-volcano-inert-prime-unique-order271-subgroup":
            raise PipelineError("edge direction certificate changed")
        derivations = (
            {
                "source_conductor_derivation": (
                    "control-order2712-witness-plus-frozen-source-binding"
                ),
                "f271_census_exclusion_role": "control-source-binding",
                "target_conductor_derivation": (
                    "complete-crater-binding-plus-independent-271-torsion"
                ),
            }
            if source_f == 271
            else {
                "source_conductor_derivation": (
                    "exact-order2712-source-plus-Fq-stable-271-kernel-plus-"
                    "certified-f120871-target"
                ),
                "f271_census_exclusion_role": "corroborating-not-load-bearing",
                "target_conductor_derivation": (
                    "crater-exclusion-plus-independent-271-torsion"
                ),
            }
        )
        for key, expected in derivations.items():
            if cert.get(key) != expected:
                raise PipelineError(f"certificate {key} differs from proof contract")

    if status in {"CERTIFIED_BOTTOM_PARENT", "POSITIVE_CONTROL_BOTTOM_PARENT"}:
        validate_deep_edge(F_PI, 51, 120_871, 51)
        if status == "CERTIFIED_BOTTOM_PARENT" and cert_int(cert, "target_orbit_rep") == PILOT_PARENT_ORBIT:
            raise PipelineError("pilot parent fiber was admitted")
        if status == "POSITIVE_CONTROL_BOTTOM_PARENT" and (
            cert_int(cert, "source_orbit_rep") != PILOT_BOTTOM_ORBIT
            or cert_int(cert, "target_orbit_rep") != PILOT_PARENT_ORBIT
            or cert.get("pilot_exclusion_scope") != "entire-parent-fiber"
        ):
            raise PipelineError("pilot positive control endpoint binding failed")
    elif status == "POSITIVE_CONTROL_F271_TO_CRATER":
        validate_deep_edge(271, 17, 1, 1)
        if (
            cert_int(cert, "source_orbit_rep") != EXPECTED_F271[0]
            or cert_int(cert, "target_b") != 1
            or cert_int(cert, "target_orbit_rep") != 1
        ):
            raise PipelineError("f271 positive control endpoint binding failed")
    elif status == "KNOWN_CRATER":
        if cert_int(cert, "source_orbit_rep") != 1 or cert_int(cert, "source_orbit_size") != 1:
            raise PipelineError("KNOWN_CRATER lacks exact crater binding")
    elif status == "KNOWN_F271":
        if cert_int(cert, "source_orbit_rep") not in EXPECTED_F271 or cert_int(cert, "source_orbit_size") != 17:
            raise PipelineError("KNOWN_F271 lacks frozen census binding")
    elif status == "EXCLUDED_PILOT_ORBIT":
        scope = cert.get("pilot_exclusion_scope")
        if scope == "source-orbit":
            if (
                cert_int(cert, "source_orbit_rep") != PILOT_BOTTOM_ORBIT
                or cert_int(cert, "source_orbit_size") != 51
            ):
                raise PipelineError("source pilot exclusion lacks exact orbit binding")
        elif scope == "entire-parent-fiber":
            validate_deep_edge(F_PI, 51, 120_871, 51)
            if cert_int(cert, "target_orbit_rep") != PILOT_PARENT_ORBIT:
                raise PipelineError("pilot-fiber exclusion lacks certified parent binding")
        else:
            raise PipelineError("pilot exclusion has unknown scope")
    elif status == "DIRECT_PARENT":
        if cert_int(cert, "source_order") != N_EXPECTED or cert_int(cert, "source_orbit_size") != 51 or cert_int(cert, "source_f_E") != 120_871 or cert_int(cert, "witness_count_found") != 0 or cert_int(cert, "direct_parent_point_1_xset_count") != 135 or cert_int(cert, "direct_parent_point_2_absent_from_point_1_subgroup") != 1:
            raise PipelineError("DIRECT_PARENT lacks positive full-rank certificate")
        direct_xset = cert_uint_vector(cert, "direct_parent_point_1_xset", 135)
        direct_point_1 = cert_int(cert, "direct_parent_point_1_x_int")
        direct_point_2 = cert_int(cert, "direct_parent_point_2_x_int")
        if (
            direct_point_1 < 0
            or direct_point_2 < 0
            or direct_point_1 not in direct_xset
            or direct_point_2 in direct_xset
        ):
            raise PipelineError("DIRECT_PARENT independence certificate failed")
        if cert_int(cert, "witness_attempts_used") < 1:
            raise PipelineError("DIRECT_PARENT has no discovery attempt")
        if cert.get("source_conductor_derivation") != (
            "two-independent-order271-x-points-full-rank"
        ):
            raise PipelineError("DIRECT_PARENT conductor derivation changed")
    elif status == "GP_ERROR":
        pipeline_error = cert.get("pipeline_error")
        if (
            not isinstance(pipeline_error, str)
            or not pipeline_error.startswith("certificate_rejected:")
            or cert.get("gp_log_sha256") != hashlib.sha256(b"\0").hexdigest()
        ):
            raise PipelineError("GP_ERROR lacks the bound clean-batch rejection cause")
    if scientific and job.control_mode != 0:
        raise PipelineError("control mode forbidden in scientific classification")
    if job.expected_status is not None and status != job.expected_status:
        raise PipelineError(f"control {job.label}: got {status}, expected {job.expected_status}")


def runtime_command(args: argparse.Namespace, out: Path, driver: bytes) -> tuple[list[str], dict[str, Any]]:
    if args.gp_bin is not None:
        if args.gp_bin.is_symlink():
            raise PipelineError("--gp-bin must not be a symlink")
        gp = args.gp_bin.resolve()
        if not gp.is_file() or gp.is_symlink() or not os.access(gp, os.X_OK):
            raise PipelineError("--gp-bin is not an executable regular file")
        if sha256_file(gp) != GP_BINARY_SHA256:
            raise PipelineError("GP executable hash differs from frozen image extraction")
        command = [str(gp), "-q", "-f", "-s", GP_STACK]
        identity = {"mode": "extracted-binary", "gp_binary": str(gp), "gp_binary_sha256": GP_BINARY_SHA256, "source_image_content_id": GP_IMAGE_ID, "environment": GP_CHILD_ENV}
        return command, identity
    if args.gp_image != GP_IMAGE_ID:
        raise PipelineError("--gp-image must equal the frozen content ID")
    docker = Path(args.docker_bin).resolve()
    if not docker.is_file() or not os.access(docker, os.X_OK):
        raise PipelineError("--docker-bin is unavailable")
    study = HERE.resolve()
    command = [
        str(docker), "run", "--rm", "--interactive", "--network", "none", "--cpuset-cpus", args.gp_cpuset,
        "--memory", args.gp_memory, "--pids-limit", "128", "--read-only",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m", "--env", "HOME=/tmp",
        "--env", "LANG=C", "--env", "LC_ALL=C", "--env", "TZ=UTC",
        "--workdir", "/out", "--mount", f"type=bind,src={study},dst=/study,readonly",
        "--mount", f"type=bind,src={out.resolve()},dst=/out", GP_IMAGE_ID, "-f", "-s", GP_STACK,
    ]
    identity = {"mode": "container", "source_image_content_id": GP_IMAGE_ID, "docker": str(docker), "interactive": True, "network": "none", "cpuset": args.gp_cpuset, "memory": args.gp_memory, "pids_limit": 128, "read_only_root": True, "docker_cli_environment": GP_CHILD_ENV, "container_environment": {"HOME": "/tmp", **GP_CHILD_ENV}}
    return command, identity


def classifier_path(args: argparse.Namespace) -> str:
    return "/study/classify_recover.gp" if args.gp_bin is None else str(CLASSIFIER.resolve())


def make_driver(jobs: list[Job], cert_paths: list[Path], args: argparse.Namespace) -> bytes:
    rows = [
        [job.hit.global_index, job.hit.b, job.source_seed, job.target_seed,
         job.control_mode, cert_path.relative_to(cert_path.parents[1]).as_posix()]
        for job, cert_path in zip(jobs, cert_paths, strict=True)
    ]
    source = (
        f"EMBED_SEED={EMBED_SEED};\nWITNESS_COUNT={WITNESS_COUNT};\n"
        f"MAX_WITNESS_ATTEMPTS={MAX_WITNESS_ATTEMPTS};\n"
        f"BATCH_ROWS={json.dumps(rows, separators=(',', ':'))};\n"
        f"read({json.dumps(classifier_path(args))});\n"
    )
    return source.encode()


def failure_certificate(path: Path, job: Job, reason: str, log_hash: str) -> None:
    payload = (
        "schema=m51-deep-endpoint-certificate/v1\n"
        f"global_index={job.hit.global_index}\nsource_b={job.hit.b}\nsource_a2=0\n"
        f"expected_order={N_EXPECTED}\nfield_degree=51\nf_pi={F_PI}\n"
        "class_discriminant_271_valuation=2\n"
        "kernel_extension_coprime_to_271=1\n"
        "maximal_order_class_number=1\n"
        f"f271_census_sha256={CENSUS_SHA256}\n"
        f"f271_census_source_revision={CENSUS_SOURCE_REVISION}\n"
        f"f271_census_source_sha256={CENSUS_SOURCE_SHA256}\n"
        "f271_census_complete_orbit_count=16\n"
        f"control_mode={job.control_mode}\npipeline_error={reason}\n"
        f"gp_log_sha256={log_hash}\nadmitted_failure=1\nstatus=GP_ERROR\n"
    )
    write_new(path, payload.encode())


def execute_jobs(jobs: list[Job], out: Path, args: argparse.Namespace, *, scientific: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if out.exists() or out.is_symlink():
        raise PipelineError(f"refusing to overwrite {out}")
    out.mkdir(parents=True)
    (out / "certificates").mkdir()
    (out / "partials").mkdir()
    check_census()
    cert_paths = [out / "certificates" / f"{number:04d}-{job.label}.kv" for number, job in enumerate(jobs)]
    for path in cert_paths:
        path.touch(mode=0o600, exist_ok=False)
    driver = make_driver(jobs, cert_paths, args)
    write_new(out / "driver.gp", driver)
    command, identity = runtime_command(args, out, driver)
    if jobs:
        process = subprocess.run(command, cwd=out, input=driver, capture_output=True, check=False, env=GP_CHILD_ENV)
    else:
        process = subprocess.CompletedProcess(command, 0, b"", b"")
    write_new(out / "gp.stdout", process.stdout)
    write_new(out / "gp.stderr", process.stderr)
    log_hash = hashlib.sha256(process.stdout + b"\0" + process.stderr).hexdigest()
    global_failure = process.returncode != 0 or bool(process.stdout) or bool(process.stderr)
    records: list[dict[str, Any]] = []
    pairs: list[dict[str, Any]] = []
    for number, (job, cert_path) in enumerate(zip(jobs, cert_paths, strict=True)):
        parse_error: str | None = None
        cert: dict[str, str] | None = None
        if global_failure:
            parse_error = f"gp_exit_{process.returncode}_or_stderr"
        else:
            try:
                cert, _ = parse_certificate(cert_path)
                validate_certificate(cert, job, scientific)
            except (OSError, UnicodeError, PipelineError) as exc:
                parse_error = f"certificate_rejected:{exc}"
        if parse_error is not None:
            partial = out / "partials" / cert_path.name
            os.rename(cert_path, partial)
            failure_certificate(cert_path, job, parse_error, log_hash)
            cert, _ = parse_certificate(cert_path)
        if cert is None:
            raise PipelineError("internal certificate state is empty")
        status = cert["status"]
        relative = cert_path.relative_to(out).as_posix()
        record: dict[str, Any] = {
            "schema": "m51-deep-classification-record/v1",
            **job.hit.binding(), "source_hit": job.hit.binding(),
            "status": status, "admitted_failure": status in FATAL,
            "control_mode": job.control_mode, "certificate_path": relative,
            "certificate_sha256": sha256_file(cert_path),
            "certificate_bytes": cert_path.stat().st_size,
        }
        records.append(record)
        if status == "CERTIFIED_BOTTOM_PARENT":
            pair = {
                "schema": "m51-deep-pair/v1", "global_index": job.hit.global_index,
                "b": job.hit.b, "a2": 0, "ellcard": N_EXPECTED,
                "bottom_orbit_rep": cert_int(cert, "source_orbit_rep"),
                "bottom_orbit_size": cert_int(cert, "source_orbit_size"),
                "parent_b": cert_int(cert, "target_b"),
                "parent_a2": cert_int(cert, "target_a2"),
                "parent_orbit_rep": cert_int(cert, "target_orbit_rep"),
                "parent_orbit_size": cert_int(cert, "target_orbit_size"),
                "status": status, "source_hit": job.hit.binding(),
                "certificate_path": relative,
                "certificate_sha256": record["certificate_sha256"],
            }
            pairs.append(pair)
    runtime = {
        "schema": "m51-deep-gp-runtime/v1", **identity,
        "command": command, "exit_status": process.returncode,
        "stdout_sha256": sha256_file(out / "gp.stdout"),
        "stderr_sha256": sha256_file(out / "gp.stderr"),
        "global_failure": global_failure, "shared_extension_initialization": True,
        "gp_stack": GP_STACK, "classifier_sha256": sha256_file(CLASSIFIER),
        "census_sha256": sha256_file(CENSUS),
    }
    write_json(out / "runtime.json", runtime)
    return records, pairs, runtime


def scientific_jobs(hits: list[Hit]) -> list[Job]:
    return [
        Job(
            label=f"rank-{hit.global_index:010d}", hit=hit,
            source_seed=derive_seed(b"m51-deep-scan/v1/source-witness", hit),
            target_seed=derive_seed(b"m51-deep-scan/v1/target-rank2", hit),
            control_mode=0,
        )
        for hit in hits
    ]


def selection(records: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> dict[str, Any]:
    provisional: list[dict[str, Any]] = []
    seen_bottom: set[int] = set()
    seen_parent: set[int] = set()
    for pair in pairs:
        bottom, parent = pair["bottom_orbit_rep"], pair["parent_orbit_rep"]
        if parent == PILOT_PARENT_ORBIT or bottom == PILOT_BOTTOM_ORBIT:
            continue
        if bottom in seen_bottom or parent in seen_parent:
            continue
        provisional.append(pair)
        seen_bottom.add(bottom)
        seen_parent.add(parent)
        if len(provisional) == TARGET_PAIRS:
            break
    cutoff = provisional[-1]["global_index"] if len(provisional) == TARGET_PAIRS else None
    fatal_records = [record for record in records if record["admitted_failure"]]
    blocking = [
        record for record in fatal_records
        if cutoff is None or record["global_index"] <= cutoff
    ]
    valid = not blocking
    selected = provisional if valid else []
    return {
        "schema": "m51-deep-selection/v1", "target_pairs": TARGET_PAIRS,
        "selected_count": len(selected), "selected": selected,
        "valid": valid, "cutoff_global_index": cutoff,
        "blocking_failures": blocking,
        "provisional_selected": provisional,
        "rule": "first eligible distinct parent orbit in global-index order; no outcome backfill",
    }


def command_classify(args: argparse.Namespace) -> int:
    hits = load_hits(args.hits)
    jobs = scientific_jobs(hits)
    records, pairs, _ = execute_jobs(jobs, args.out.resolve(), args, scientific=True)
    write_jsonl(args.out / "records.jsonl", records)
    write_jsonl(args.out / "pairs.jsonl", pairs)
    write_json(args.out / "selection.json", selection(records, pairs))
    return 0


def control_jobs() -> list[Job]:
    specifications: list[tuple[str, int, int, str]] = [("crater-exclusion", 1, 0, "KNOWN_CRATER")]
    specifications.extend((f"f271-exclusion-{i:02d}", b, 0, "KNOWN_F271") for i, b in enumerate(EXPECTED_F271, 1))
    specifications.extend([
        ("pilot-source-exclusion", PILOT_BOTTOM_RAW_B, 0, "EXCLUDED_PILOT_ORBIT"),
        ("positive-f271-ascent", EXPECTED_F271[0], 2, "POSITIVE_CONTROL_F271_TO_CRATER"),
        ("positive-bottom-ascent", PILOT_BOTTOM_RAW_B, 1, "POSITIVE_CONTROL_BOTTOM_PARENT"),
        ("positive-parent-rank2", PILOT_PARENT_ORBIT, 0, "DIRECT_PARENT"),
    ])
    jobs: list[Job] = []
    for index, (label, b, mode, expected) in enumerate(specifications):
        hit = Hit(index, b, 0, 0, 0)
        jobs.append(Job(label, hit, control_seed(label, False), control_seed(label, True), mode, expected))
    return jobs


def command_controls(args: argparse.Namespace) -> int:
    jobs = control_jobs()
    records, _, runtime = execute_jobs(jobs, args.out.resolve(), args, scientific=False)
    observed = {job.label: record["status"] for job, record in zip(jobs, records, strict=True)}
    expected = {job.label: job.expected_status for job in jobs}
    passed = observed == expected and not any(record["admitted_failure"] for record in records)
    summary = {
        "schema": "m51-deep-controls/v1", "all_passed": passed,
        "control_count": len(jobs), "expected": expected, "observed": observed,
        "controls": [
            {
                "id": job.label,
                "kind": "positive" if job.label.startswith("positive-") else "negative",
                "expected": job.expected_status,
                "observed": record["status"],
                "passed": record["status"] == job.expected_status and not record["admitted_failure"],
                "certificate_path": record["certificate_path"],
                "certificate_sha256": record["certificate_sha256"],
            }
            for job, record in zip(jobs, records, strict=True)
        ],
        "positive_controls": ["positive-f271-ascent", "positive-bottom-ascent", "positive-parent-rank2"],
        "negative_controls": [job.label for job in jobs if job.label not in {"positive-f271-ascent", "positive-bottom-ascent", "positive-parent-rank2"}],
        "runtime_sha256": hashlib.sha256(json.dumps(runtime, sort_keys=True).encode()).hexdigest(),
    }
    write_jsonl(args.out / "records.jsonl", records)
    write_json(args.out / "controls.json", summary)
    if not passed:
        raise PipelineError("one or more frozen controls failed")
    return 0


def add_runtime_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gp-bin", type=Path)
    group.add_argument("--gp-image")
    parser.add_argument("--docker-bin", default=shutil.which("docker") or "docker")
    parser.add_argument("--gp-cpuset", default="0")
    parser.add_argument("--gp-memory", default="12g")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    sub = parser.add_subparsers(dest="command", required=True)
    classify = sub.add_parser("classify", allow_abbrev=False)
    classify.add_argument("--hits", type=Path, required=True)
    classify.add_argument("--out", type=Path, required=True)
    add_runtime_args(classify)
    controls = sub.add_parser("controls", allow_abbrev=False)
    controls.add_argument("--out", type=Path, required=True)
    add_runtime_args(controls)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "classify":
        return command_classify(args)
    return command_controls(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PipelineError as exc:
        print(f"pipeline: {exc}", file=sys.stderr)
        raise SystemExit(2)
