#!/usr/bin/env python3
"""Independent source verifier for EXP-ECDLP-TT-SOURCE-COMPILER-001.

The verifier is a one-file, standard-library-only closure.  It does
not import the producer runtime or compiler.  Its runtime data inputs are the
target-redacted source manifest, the target-free source execution matrix, and
the producer's canonical raw JSON result. Strict development preflight also
requires the harness-supplied SHA-256 of the validated static-closure report,
but never reads that target-hash-bearing report. No control, target, mutation,
or prior-artifact path is accepted by the CLI.

CLI
---

Strict development preflight::

    python3 verify_tt_source_advice.py \
      --manifest source-instance-manifest-v1.json \
      --execution-matrix source-execution-matrix-v2.json \
      --raw-result source-generator-raw-result.json \
      --expected-static-closure-audit-sha256 DIGEST \
      --strict-preflight-development

``--describe-schema`` emits the machine-readable input/output schema without
reading experiment inputs.  ``--self-test`` runs deterministic local checks.

The producer raw result is canonical JSON: UTF-8, sorted object keys, compact
separators, ASCII escaping, no NaN/Infinity, and exactly one trailing newline.
Its top-level schema is ``tt-source-compiler-raw-v1``.  Required fields are
described by ``--describe-schema`` and enforced below.  Tensor cores may use
the verifier's flat records or the producer's independently validated
``exact-fp-tt-v1`` wrapper; both carry flat row-major core values.

Success and failure both write exactly one canonical JSON object to stdout.
Failures have ``valid:false`` and return a nonzero process status.  Because the
experiment has no execution plan, successful development modes emit audits and
candidate digests only; they never emit or freeze advice objects.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import resource
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


PROTOCOL = "EXP-ECDLP-TT-SOURCE-COMPILER-001"
RAW_SCHEMA = "tt-source-compiler-raw-v1"
OUTPUT_SCHEMA = "tt-source-verification-v1"
ADVICE_SCHEMA = "frozen-source-advice-v1"
CONTROL_CERTIFICATE_SCHEMA = "frozen-source-control-certificates-v1"
RECEIPT_SCHEMA = "source-advice-receipt-v1"
SOURCE_MANIFEST_ID = "EXP-ECDLP-TT-SOURCE-COMPILER-001-SOURCE-INPUT-V1"
SOURCE_MATRIX_ID = "EXP-ECDLP-TT-SOURCE-COMPILER-001-SOURCE-MATRIX-V2"
SOURCE_MANIFEST_SHA256 = (
    "524110579d7334dccf46a7d9c1231710956ba04bc001754983ebaab5a8777a52"
)
SOURCE_MATRIX_SHA256 = (
    "daaa47eb48d1e5e661b27d7561bb61b276743deb3b32bf1a94d27287d3f2cd40"
)
RCB_GATE_TEXT_SHA256 = (
    "14072c7d7345d9a742a5701ac924eaf3b3fdcf0f771664860604b0cb9fdada02"
)
MODE_ORDER = ("P1", "P2", "P3", "P4", "P5")
ADDITION_TREE = "Add(Add(Add(Add(P1,P2),P3),P4),P5)"
TENSOR_NAMES = ("X", "Y", "Z", "X2", "XZ", "Z2", "XY", "YZ", "Y2")
RETAINED_NAMES = ("X2", "XZ", "Z2", "YZ", "Y2")
OPERATION_VECTOR_KEYS = (
    "adds",
    "subs",
    "muls",
    "squares",
    "inversions",
    "reductions",
    "comparisons",
    "hash_bytes",
    "copied_words",
)
SOURCE_VERIFIER_CAP = {
    "adds": 5_000_000_000,
    "subs": 5_000_000_000,
    "muls": 5_000_000_000,
    "squares": 1_000_000_000,
    "inversions": 1_000_000,
    "reductions": 15_000_000_000,
    "comparisons": 5_000_000_000,
    "hash_bytes": 1_000_000_000,
    "copied_words": 50_000_000_000,
}
SOURCE_GENERATOR_CAP = {
    "adds": 20_000_000_000,
    "subs": 20_000_000_000,
    "muls": 20_000_000_000,
    "squares": 1_000_000_000,
    "inversions": 2_000_000,
    "reductions": 45_000_000_000,
    "comparisons": 10_000_000_000,
    "hash_bytes": 1_000_000_000,
    "copied_words": 200_000_000_000,
}
VERIFIER_TRAFFIC_CAP = 50_000_000_000
MAX_WALL_SECONDS = 3_600
MAX_CPU_SECONDS = 12 * 3_600
MAX_RSS_BYTES = 2 * 1024**3
MAX_LOCAL_MATRIX_WORDS = 1_000_000
MAX_TT_WORDS = 1_000_000
MAX_LIVE_WORDS = 500_000
MAX_RAW_RESULT_BYTES = 256 * 1024**2
ACCEPTED_IR_KINDS = (
    "input_coordinate",
    "scale",
    "direct_sum",
    "stage_a_contract",
    "stage_b_contract",
    "rank_factor",
    "absorb_left",
    "absorb_right",
    "emit",
    "free",
)
SOURCE_TRAFFIC_BUCKETS = (
    "registry_input",
    "allocation_zero_fill",
    "direct_sum_copy",
    "stage_a_input",
    "stage_a_output",
    "stage_b_input",
    "stage_b_output",
    "factor_input_copy",
    "pivot_scan",
    "row_normalization",
    "elimination",
    "factor_output",
    "transfer_propagation",
    "sweep_absorption",
    "core_emit",
    "advice_serialize",
    "digest_read",
    "artifact_serialize",
)
VERIFIER_TRAFFIC_BUCKETS = (
    "registry_input",
    "digest_read",
    "verifier_materialization",
    "advice_serialize",
    "artifact_serialize",
)
PRIMARY_CELL_ORDER = (
    "C08:random_unique",
    "C08:x_interval",
    "C10:random_unique",
    "C10:x_interval",
    "C12:random_unique",
    "C12:x_interval",
)
CONTROL_CELL_ID = "C08:random_unique:MODEWISE_RESCALED"
ALL_CELL_ORDER = PRIMARY_CELL_ORDER + (CONTROL_CELL_ID,)
EXPECTED_SOURCE_COUNTS = {
    "primary_source_cells": 6,
    "control_source_cells": 1,
    "source_cells": 7,
    "source_tensor_records": 63,
    "retained_advice_tensors": 30,
    "source_rcb_calls": 28,
    "source_hadamard_gates": 378,
    "source_scalar_gates": 140,
    "source_addition_gates": 476,
    "source_subtraction_gates": 168,
    "source_normalization_calls_upper_bound": 1022,
    "source_streamed_prefix_factorizations_upper_bound": 1512,
    "source_two_sweep_factorizations_upper_bound": 8176,
    "source_total_rank_factorizations_upper_bound": 9688,
    "source_diagnostic_tuples": 35,
    "source_diagnostic_rcb_calls": 140,
}
EXPECTED_SHAPE_CEILING = {
    "normalized_tt_words": 4425,
    "binary_dense_direct_sum_words": 17600,
    "streamed_local_matrix_words": 78125,
    "streamed_transfer_words": 78125,
    "stage_a_intermediate_words": 15625,
    "stage_b_output_slice_words": 15625,
    "provisional_streamed_tt_words": 32025,
    "prohibited_full_raw_hadamard_tt_words": 2109625,
}
EXPECTED_SAMPLES = {
    "C08": (
        (0, 0, 0, 0, 0),
        (2, 2, 2, 2, 2),
        (1, 1, 0, 2, 2),
        (2, 2, 2, 0, 0),
        (1, 0, 2, 2, 2),
    ),
    "C10": (
        (0, 0, 0, 0, 0),
        (3, 3, 3, 3, 3),
        (0, 3, 2, 0, 2),
        (2, 3, 3, 2, 3),
        (1, 1, 2, 1, 0),
    ),
    "C12": (
        (0, 0, 0, 0, 0),
        (4, 4, 4, 4, 4),
        (2, 2, 3, 3, 2),
        (4, 3, 1, 1, 3),
        (1, 1, 0, 0, 4),
    ),
}


class VerificationError(Exception):
    """A deterministic verifier rejection."""

    def __init__(self, code: str, message: str, path: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.path = path


def reject(code: str, message: str, path: str = "") -> None:
    raise VerificationError(code, message, path)


_ACTIVE_OPERATION_VECTOR: dict[str, int] | None = None


def charge_hash_bytes(amount: int) -> None:
    if _ACTIVE_OPERATION_VECTOR is not None:
        _ACTIVE_OPERATION_VECTOR["hash_bytes"] += amount


def canonical_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        reject("noncanonical_json_value", str(error))


def emit(value: Mapping[str, Any]) -> None:
    sys.stdout.buffer.write(canonical_bytes(dict(value)))
    sys.stdout.buffer.flush()


def _duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            reject("duplicate_json_key", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _reject_float(value: str) -> Any:
    reject("json_float_forbidden", f"floating JSON value is forbidden: {value}")


def _reject_constant(value: str) -> Any:
    reject("json_constant_forbidden", f"non-finite JSON value is forbidden: {value}")


def parse_json_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        reject("json_not_utf8", f"{label}: {error}")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_duplicate_rejecting_object,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except VerificationError:
        raise
    except json.JSONDecodeError as error:
        reject("json_parse_error", f"{label}: {error.msg} at {error.pos}")
    if not isinstance(value, dict):
        reject("json_top_level_not_object", f"{label}: top level must be an object")
    return value


def read_json(path: Path, label: str, maximum_bytes: int | None = None) -> tuple[dict[str, Any], bytes]:
    try:
        size = path.stat().st_size
    except OSError as error:
        reject("input_stat_failed", f"{label}: {error}", str(path))
    if maximum_bytes is not None and size > maximum_bytes:
        reject(
            "input_size_gate",
            f"{label}: {size} bytes exceeds {maximum_bytes}",
            str(path),
        )
    try:
        data = path.read_bytes()
    except OSError as error:
        reject("input_read_failed", f"{label}: {error}", str(path))
    return parse_json_bytes(data, label), data


def sha256_bytes(data: bytes) -> str:
    charge_hash_bytes(len(data))
    return hashlib.sha256(data).hexdigest()


def sha256_value(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def lexical_path_within(path: str, root: str) -> bool:
    return path == root or path.startswith(root + os.sep)


def compact_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        reject("noncanonical_json_value", str(error))


def exact_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        reject("type_object", f"{path} must be an object", path)
    return value


def exact_list(value: Any, path: str, length: int | None = None) -> list[Any]:
    if not isinstance(value, list):
        reject("type_array", f"{path} must be an array", path)
    if length is not None and len(value) != length:
        reject("array_length", f"{path} must contain {length} entries", path)
    return value


def exact_int(
    value: Any,
    path: str,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if type(value) is not int:
        reject("type_integer", f"{path} must be an exact integer", path)
    if minimum is not None and value < minimum:
        reject("integer_minimum", f"{path} must be at least {minimum}", path)
    if maximum is not None and value > maximum:
        reject("integer_maximum", f"{path} must be at most {maximum}", path)
    return value


def exact_bool(value: Any, path: str) -> bool:
    if type(value) is not bool:
        reject("type_boolean", f"{path} must be a boolean", path)
    return value


def exact_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        reject("type_string", f"{path} must be a string", path)
    return value


def require_equal(actual: Any, expected: Any, path: str, code: str = "value_mismatch") -> None:
    if actual != expected:
        reject(code, f"{path}: {actual!r} != {expected!r}", path)


def require_keys(
    value: Mapping[str, Any],
    required: Iterable[str],
    path: str,
    allowed: Iterable[str] | None = None,
) -> None:
    required_set = set(required)
    missing = sorted(required_set - set(value))
    if missing:
        reject("missing_keys", f"{path}: missing keys {missing}", path)
    if allowed is not None:
        extra = sorted(set(value) - set(allowed))
        if extra:
            reject("unexpected_keys", f"{path}: unexpected keys {extra}", path)


def validate_hex_digest(value: Any, path: str) -> str:
    digest = exact_string(value, path)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        reject("invalid_sha256", f"{path} must be lowercase SHA-256 hex", path)
    return digest


def product(values: Iterable[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


@dataclass
class Meter:
    operations: dict[str, int] = field(default_factory=dict)
    traffic: dict[str, dict[str, int]] = field(default_factory=dict)
    peak_live_field_words: int = 0

    def __post_init__(self) -> None:
        if not self.operations:
            self.operations = {key: 0 for key in OPERATION_VECTOR_KEYS}
        if not self.traffic:
            self.traffic = {
                key: {"reads": 0, "writes": 0}
                for key in VERIFIER_TRAFFIC_BUCKETS
            }

    def add_operation(self, key: str, amount: int = 1) -> None:
        if key not in self.operations or amount < 0:
            reject("internal_meter_error", f"invalid operation meter update {key}:{amount}")
        self.operations[key] += amount

    def add_traffic(
        self,
        bucket: str,
        *,
        reads: int = 0,
        writes: int = 0,
        copied: bool = False,
    ) -> None:
        if bucket not in self.traffic or reads < 0 or writes < 0:
            reject(
                "internal_meter_error",
                f"invalid traffic meter update {bucket}:{reads}:{writes}",
            )
        self.traffic[bucket]["reads"] += reads
        self.traffic[bucket]["writes"] += writes
        if copied:
            self.operations["copied_words"] += reads + writes

    def observe_live(self, words: int) -> None:
        if words < 0:
            reject("internal_meter_error", "negative live field words")
        self.peak_live_field_words = max(self.peak_live_field_words, words)

    def check_caps(self) -> None:
        for key, cap in SOURCE_VERIFIER_CAP.items():
            if self.operations[key] > cap:
                reject(
                    "verifier_operation_cap",
                    f"source_verifier.{key}={self.operations[key]} exceeds {cap}",
                )
        observed_traffic = traffic_total(self.traffic)
        if observed_traffic > VERIFIER_TRAFFIC_CAP:
            reject(
                "verifier_traffic_cap",
                f"source verifier traffic {observed_traffic} exceeds {VERIFIER_TRAFFIC_CAP}",
            )
        if self.peak_live_field_words > MAX_LIVE_WORDS:
            reject(
                "verifier_live_word_cap",
                f"source verifier live words {self.peak_live_field_words} exceeds {MAX_LIVE_WORDS}",
            )


@dataclass(frozen=True)
class Core:
    left: int
    physical: int
    right: int
    values: tuple[int, ...]

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.left, self.physical, self.right

    @property
    def words(self) -> int:
        return len(self.values)

    def at(self, left: int, physical: int, right: int) -> int:
        return self.values[(left * self.physical + physical) * self.right + right]


@dataclass(frozen=True)
class Tensor:
    name: str
    p: int
    B: int
    tag: str
    ranks: tuple[int, ...]
    cores: tuple[Core, ...]

    @property
    def words(self) -> int:
        return sum(core.words for core in self.cores)

    def canonical_record(self) -> dict[str, Any]:
        return {
            "B": self.B,
            "cores": [
                {"shape": list(core.shape), "values": list(core.values)}
                for core in self.cores
            ],
            "name": self.name,
            "p": self.p,
            "ranks": list(self.ranks),
            "tag": self.tag,
        }


def parse_tensor(value: Any, path: str, name: str, p: int, B: int) -> Tensor:
    record = exact_object(value, path)
    required = {"name", "p", "B", "tag", "ranks", "cores", "core_digest_sha256"}
    allowed = required | {
        "producer_tt_digest_sha256",
        "word_count",
    }
    require_keys(record, required, path, allowed)
    require_equal(record["name"], name, f"{path}.name")
    require_equal(exact_int(record["p"], f"{path}.p"), p, f"{path}.p")
    require_equal(exact_int(record["B"], f"{path}.B"), B, f"{path}.B")
    tag = exact_string(record["tag"], f"{path}.tag")
    ranks_list = [
        exact_int(item, f"{path}.ranks[{index}]", 0)
        for index, item in enumerate(exact_list(record["ranks"], f"{path}.ranks", 4))
    ]
    core_records = exact_list(record["cores"], f"{path}.cores")
    if tag == "canonical_zero":
        require_equal(ranks_list, [0, 0, 0, 0], f"{path}.ranks")
        require_equal(core_records, [], f"{path}.cores")
        tensor = Tensor(name, p, B, tag, (0, 0, 0, 0), ())
    elif tag == "tt":
        if len(core_records) != 5:
            reject("tt_core_count", f"{path}: nonzero TT requires five cores", path)
        boundaries = (1, *ranks_list, 1)
        cores: list[Core] = []
        for mode, raw_core in enumerate(core_records):
            core_path = f"{path}.cores[{mode}]"
            core_record = exact_object(raw_core, core_path)
            require_keys(core_record, {"shape", "values"}, core_path, {"shape", "values", "digest_sha256"})
            shape = tuple(
                exact_int(item, f"{core_path}.shape[{index}]", 1)
                for index, item in enumerate(exact_list(core_record["shape"], f"{core_path}.shape", 3))
            )
            expected_shape = (boundaries[mode], B, boundaries[mode + 1])
            require_equal(shape, expected_shape, f"{core_path}.shape", "tt_shape_mismatch")
            values = tuple(
                exact_int(item, f"{core_path}.values[{index}]", 0, p - 1)
                for index, item in enumerate(exact_list(core_record["values"], f"{core_path}.values"))
            )
            if len(values) != product(shape):
                reject("tt_value_count", f"{core_path}: value count does not match shape", core_path)
            if "digest_sha256" in core_record:
                expected_digest = sha256_value({"shape": list(shape), "values": list(values)})
                require_equal(
                    validate_hex_digest(core_record["digest_sha256"], f"{core_path}.digest_sha256"),
                    expected_digest,
                    f"{core_path}.digest_sha256",
                    "core_digest_mismatch",
                )
            cores.append(Core(shape[0], shape[1], shape[2], values))
        tensor = Tensor(name, p, B, tag, tuple(ranks_list), tuple(cores))
        ambient = (B, B * B, B * B, B)
        for cut, (rank, cap) in enumerate(zip(tensor.ranks, ambient), 1):
            if rank < 1 or rank > cap:
                reject(
                    "tt_rank_ambient_bound",
                    f"{path}.ranks[{cut - 1}]={rank} outside [1,{cap}]",
                    path,
                )
    else:
        reject("tt_tag", f"{path}.tag must be 'tt' or 'canonical_zero'", path)
    core_digest = sha256_value(tensor.canonical_record())
    require_equal(
        validate_hex_digest(record["core_digest_sha256"], f"{path}.core_digest_sha256"),
        core_digest,
        f"{path}.core_digest_sha256",
        "tensor_core_digest_mismatch",
    )
    if "word_count" in record:
        require_equal(
            exact_int(record["word_count"], f"{path}.word_count", 0),
            tensor.words,
            f"{path}.word_count",
        )
    if "producer_tt_digest_sha256" in record:
        validate_hex_digest(
            record["producer_tt_digest_sha256"],
            f"{path}.producer_tt_digest_sha256",
        )
    if tensor.words > MAX_TT_WORDS:
        reject("tt_object_word_gate", f"{path}: {tensor.words} words exceeds gate", path)
    return tensor


def normalize_native_tensor_record(
    value: Any, path: str, expected_name: str, p: int, B: int
) -> dict[str, Any]:
    wrapper = exact_object(value, path)
    if "tensor" in wrapper:
        require_keys(
            wrapper,
            {"tensor"},
            path,
            {"name", "tensor_name", "tensor", "retained_advice", "certificate"},
        )
        require_equal(
            wrapper.get("name", wrapper.get("tensor_name")),
            expected_name,
            f"{path}.name",
        )
        if "retained_advice" in wrapper:
            exact_bool(wrapper["retained_advice"], f"{path}.retained_advice")
        if "certificate" in wrapper:
            exact_object(wrapper["certificate"], f"{path}.certificate")
        native = exact_object(wrapper["tensor"], f"{path}.tensor")
        native_path = f"{path}.tensor"
    else:
        native = wrapper
        native_path = path
    if native.get("encoding") != "exact-fp-tt-v1":
        return wrapper
    required = {
        "encoding",
        "field_modulus",
        "physical_mode_count",
        "physical_mode_size",
        "tag",
        "ranks",
        "field_words",
        "canonical_bytes_per_field_word",
        "value_digest_sha256",
        "cores",
        "record_sha256",
    }
    require_keys(native, required, native_path, required)
    require_equal(native["field_modulus"], p, f"{native_path}.field_modulus")
    require_equal(native["physical_mode_count"], 5, f"{native_path}.physical_mode_count")
    require_equal(native["physical_mode_size"], B, f"{native_path}.physical_mode_size")
    require_equal(
        native["canonical_bytes_per_field_word"],
        encoded_width(p),
        f"{native_path}.canonical_bytes_per_field_word",
    )
    validate_hex_digest(native["value_digest_sha256"], f"{native_path}.value_digest_sha256")
    record_without_digest = dict(native)
    record_digest = record_without_digest.pop("record_sha256")
    require_equal(
        validate_hex_digest(record_digest, f"{native_path}.record_sha256"),
        sha256_bytes(compact_json_bytes(record_without_digest)),
        f"{native_path}.record_sha256",
        "producer_tensor_record_digest_mismatch",
    )
    tag = native["tag"]
    if tag not in ("nonzero", "canonical_zero"):
        reject("producer_tensor_tag", f"{native_path}.tag is invalid")
    normalized_cores: list[dict[str, Any]] = []
    for index, core_value in enumerate(exact_list(native["cores"], f"{native_path}.cores")):
        core_path = f"{native_path}.cores[{index}]"
        core = exact_object(core_value, core_path)
        require_keys(core, {"shape", "values", "value_digest_sha256"}, core_path, {"shape", "values", "value_digest_sha256"})
        shape = [
            exact_int(item, f"{core_path}.shape[{axis}]", 1)
            for axis, item in enumerate(exact_list(core["shape"], f"{core_path}.shape", 3))
        ]
        values = [
            exact_int(item, f"{core_path}.values[{offset}]", 0, p - 1)
            for offset, item in enumerate(
                exact_list(core["values"], f"{core_path}.values", product(shape))
            )
        ]
        core_digest_state = hashlib.sha256()
        width = encoded_width(p)
        for item in values:
            encoded = item.to_bytes(width, "big")
            charge_hash_bytes(len(encoded))
            core_digest_state.update(encoded)
        require_equal(
            validate_hex_digest(core["value_digest_sha256"], f"{core_path}.value_digest_sha256"),
            core_digest_state.hexdigest(),
            f"{core_path}.value_digest_sha256",
            "producer_core_value_digest_mismatch",
        )
        normalized_cores.append({"shape": shape, "values": values})
    normalized = {
        "B": B,
        "cores": normalized_cores,
        "name": expected_name,
        "p": p,
        "producer_tt_digest_sha256": native["value_digest_sha256"],
        "ranks": native["ranks"],
        "tag": "tt" if tag == "nonzero" else "canonical_zero",
        "word_count": native["field_words"],
    }
    core_record = {
        "B": B,
        "cores": normalized_cores,
        "name": expected_name,
        "p": p,
        "ranks": native["ranks"],
        "tag": normalized["tag"],
    }
    normalized["core_digest_sha256"] = sha256_value(core_record)
    return normalized


def evaluate_tensor(tensor: Tensor, indices: Sequence[int], meter: Meter | None = None) -> int:
    if len(indices) != 5:
        reject("tuple_arity", "TT evaluation requires five physical indices")
    if tensor.tag == "canonical_zero":
        return 0
    vector = [1]
    for mode, (core, physical) in enumerate(zip(tensor.cores, indices)):
        if physical < 0 or physical >= tensor.B:
            reject("tuple_index", f"mode {mode} index {physical} outside [0,{tensor.B})")
        output = [0] * core.right
        for right in range(core.right):
            total = 0
            for left in range(core.left):
                total += vector[left] * core.at(left, physical, right)
            output[right] = total % tensor.p
        if meter is not None:
            meter.add_operation("muls", core.left * core.right)
            meter.add_operation("adds", max(core.left - 1, 0) * core.right)
            meter.add_operation("reductions", core.right)
            meter.add_traffic(
                "verifier_materialization",
                reads=core.left * core.right + core.left,
                writes=core.right,
            )
        vector = output
    if len(vector) != 1:
        reject("tt_boundary", "TT evaluation did not end at right boundary one")
    return vector[0]


def iter_five_tuples_independent(B: int) -> Iterator[tuple[int, int, int, int, int]]:
    """Enumerate in reverse-mode, descending traversal, unlike producer samples."""
    for i5 in range(B - 1, -1, -1):
        for i4 in range(B - 1, -1, -1):
            for i3 in range(B - 1, -1, -1):
                for i2 in range(B - 1, -1, -1):
                    for i1 in range(B - 1, -1, -1):
                        yield i1, i2, i3, i4, i5


def linear_index(indices: Sequence[int], B: int) -> int:
    result = 0
    for value in indices:
        result = result * B + value
    return result


def encoded_width(p: int) -> int:
    return max(1, (p.bit_length() + 7) // 8)


def value_digest(values: Sequence[int], p: int, meter: Meter | None = None) -> str:
    width = encoded_width(p)
    digest = hashlib.sha256()
    for value in values:
        encoded = value.to_bytes(width, "big")
        charge_hash_bytes(len(encoded))
        digest.update(encoded)
    if meter is not None:
        meter.add_traffic("digest_read", reads=len(values))
    return digest.hexdigest()


def exact_rank_rows(rows: Sequence[Sequence[int]], p: int, meter: Meter | None = None) -> int:
    if not rows:
        return 0
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        reject("rank_matrix_shape", "rank matrix rows have unequal lengths")
    matrix = [[entry % p for entry in row] for row in rows]
    if meter is not None:
        meter.add_traffic(
            "verifier_materialization",
            reads=len(matrix) * width,
            writes=len(matrix) * width,
            copied=True,
        )
        meter.observe_live(len(matrix) * width)
    pivot_row = 0
    for column in range(width):
        candidate = pivot_row
        while candidate < len(matrix):
            if meter is not None:
                meter.add_operation("comparisons")
                meter.add_traffic("verifier_materialization", reads=1)
            if matrix[candidate][column] != 0:
                break
            candidate += 1
        if candidate == len(matrix):
            continue
        if candidate != pivot_row:
            matrix[pivot_row], matrix[candidate] = matrix[candidate], matrix[pivot_row]
            if meter is not None:
                meter.add_traffic(
                    "verifier_materialization",
                    reads=0,
                    writes=0,
                )
        inverse = pow(matrix[pivot_row][column], -1, p)
        if meter is not None:
            meter.add_operation("inversions")
            meter.add_operation("reductions")
            meter.add_traffic("verifier_materialization", reads=1)
        for j in range(column, width):
            matrix[pivot_row][j] = matrix[pivot_row][j] * inverse % p
        if meter is not None:
            count = width - column
            meter.add_operation("muls", count)
            meter.add_operation("reductions", count)
            meter.add_traffic(
                "verifier_materialization", reads=count, writes=count
            )
        for row_index in range(len(matrix)):
            if row_index == pivot_row:
                continue
            factor = matrix[row_index][column]
            if meter is not None:
                meter.add_operation("comparisons")
                meter.add_traffic("verifier_materialization", reads=1)
            if factor == 0:
                continue
            for j in range(column, width):
                matrix[row_index][j] = (matrix[row_index][j] - factor * matrix[pivot_row][j]) % p
            if meter is not None:
                count = width - column
                meter.add_operation("muls", count)
                meter.add_operation("subs", count)
                meter.add_operation("reductions", count)
                meter.add_traffic(
                    "verifier_materialization",
                    reads=3 * count,
                    writes=count,
                )
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row


def unfolding_rank(values: Sequence[int], B: int, cut: int, p: int, meter: Meter | None = None) -> int:
    if cut < 1 or cut > 4:
        reject("rank_cut", "unfolding cut must be in 1..4")
    rows = B**cut
    columns = B ** (5 - cut)
    if len(values) != rows * columns:
        reject("rank_value_count", "tensor value count does not match B^5")
    if rows <= columns:
        matrix = [list(values[row * columns : (row + 1) * columns]) for row in range(rows)]
    else:
        matrix = [
            [values[row * columns + column] for row in range(rows)]
            for column in range(columns)
        ]
    return exact_rank_rows(matrix, p, meter)


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd = value - 1
    powers = 0
    while odd % 2 == 0:
        odd //= 2
        powers += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        residue = pow(base, odd, value)
        if residue in (1, value - 1):
            continue
        for _ in range(powers - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


Point = tuple[int, int] | None
Projective = tuple[int, int, int]


def projective_on_curve(point: Projective, p: int, a: int, b: int) -> bool:
    x, y, z = point
    if x == 0 and y == 0 and z == 0:
        return False
    return (y * y * z - x * x * x - a * x * z * z - b * z * z * z) % p == 0


def projective_to_affine(point: Projective, p: int) -> Point:
    x, y, z = point
    if z % p == 0:
        return None
    inverse = pow(z % p, -1, p)
    return x * inverse % p, y * inverse % p


def affine_add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def affine_mul(scalar: int, point: Point, p: int, a: int) -> Point:
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = affine_add(result, addend, p, a)
        scalar >>= 1
        if scalar:
            addend = affine_add(addend, addend, p, a)
    return result


def curve_order(p: int, a: int, b: int) -> int:
    result = 1
    exponent = (p - 1) // 2
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            result += 1
        elif pow(rhs, exponent, p) == 1:
            result += 2
    return result


def rcb_add_independent(
    left: Projective,
    right: Projective,
    p: int,
    a: int,
    b: int,
    meter: Meter | None = None,
) -> Projective:
    """Literal 40-gate RCB Algorithm 1 scalar replay."""
    x1, y1, z1 = left
    x2, y2, z2 = right
    b3 = 3 * b % p
    t0 = x1 * x2 % p
    t1 = y1 * y2 % p
    t2 = z1 * z2 % p
    t3 = (x1 + y1) % p
    t4 = (x2 + y2) % p
    t3 = t3 * t4 % p
    t4 = (t0 + t1) % p
    t3 = (t3 - t4) % p
    t4 = (x1 + z1) % p
    t5 = (x2 + z2) % p
    t4 = t4 * t5 % p
    t5 = (t0 + t2) % p
    t4 = (t4 - t5) % p
    t5 = (y1 + z1) % p
    x3 = (y2 + z2) % p
    t5 = t5 * x3 % p
    x3 = (t1 + t2) % p
    t5 = (t5 - x3) % p
    z3 = a * t4 % p
    x3 = b3 * t2 % p
    z3 = (x3 + z3) % p
    x3 = (t1 - z3) % p
    z3 = (t1 + z3) % p
    y3 = x3 * z3 % p
    t1 = (t0 + t0) % p
    t1 = (t1 + t0) % p
    t2 = a * t2 % p
    t4 = b3 * t4 % p
    t1 = (t1 + t2) % p
    t2 = (t0 - t2) % p
    t2 = a * t2 % p
    t4 = (t4 + t2) % p
    t0 = t1 * t4 % p
    y3 = (y3 + t0) % p
    t0 = t5 * t4 % p
    x3 = t3 * x3 % p
    x3 = (x3 - t0) % p
    t0 = t3 * t1 % p
    z3 = t5 * z3 % p
    z3 = (z3 + t0) % p
    if meter is not None:
        meter.add_operation("muls", 18)
        meter.add_operation("adds", 17)
        meter.add_operation("subs", 6)
        meter.add_operation("reductions", 41)
        meter.add_traffic("verifier_materialization", reads=82, writes=41)
    return x3, y3, z3


def sum_five_rcb_independent(
    points: Sequence[Projective], p: int, a: int, b: int, meter: Meter | None = None
) -> Projective:
    if len(points) != 5:
        reject("point_count", "five projective points are required")
    value = rcb_add_independent(points[0], points[1], p, a, b, meter)
    value = rcb_add_independent(value, points[2], p, a, b, meter)
    value = rcb_add_independent(value, points[3], p, a, b, meter)
    return rcb_add_independent(value, points[4], p, a, b, meter)


def nine_source_values(point: Projective, p: int, meter: Meter | None = None) -> dict[str, int]:
    x, y, z = point
    values = {
        "X": x,
        "Y": y,
        "Z": z,
        "X2": x * x % p,
        "XZ": x * z % p,
        "Z2": z * z % p,
        "XY": x * y % p,
        "YZ": y * z % p,
        "Y2": y * y % p,
    }
    if meter is not None:
        meter.add_operation("squares", 3)
        meter.add_operation("muls", 3)
        meter.add_operation("reductions", 6)
        meter.add_traffic("verifier_materialization", reads=9, writes=6)
    return values


@dataclass(frozen=True)
class CellSpec:
    cell_id: str
    curve_id: str
    registry: str
    p: int
    a: int
    b: int
    B: int
    points: tuple[Projective, ...]
    primary: bool
    mode_scalars: tuple[int, ...]


def parse_projective(value: Any, path: str, p: int) -> Projective:
    raw = exact_list(value, path, 3)
    point = tuple(
        exact_int(item, f"{path}[{index}]", 0, p - 1)
        for index, item in enumerate(raw)
    )
    return point  # type: ignore[return-value]


def audit_source_manifest(
    record: dict[str, Any], raw_bytes: bytes, meter: Meter
) -> tuple[dict[str, CellSpec], dict[str, Any]]:
    digest = sha256_bytes(raw_bytes)
    require_equal(digest, SOURCE_MANIFEST_SHA256, "source manifest SHA-256", "source_manifest_binding")
    manifest = exact_object(record.get("source_manifest"), "source_manifest")
    require_equal(manifest.get("id"), SOURCE_MANIFEST_ID, "source_manifest.id")
    require_equal(manifest.get("version"), 1, "source_manifest.version")
    require_equal(manifest.get("status"), "approved_for_implementation", "source_manifest.status")
    require_equal(manifest.get("mode_order"), list(MODE_ORDER), "source_manifest.mode_order")
    require_equal(manifest.get("addition_tree"), ADDITION_TREE, "source_manifest.addition_tree")

    redaction = exact_object(manifest.get("redaction_invariant"), "source_manifest.redaction_invariant")
    for key in ("target_records", "target_coordinates", "target_digests", "target_labels"):
        require_equal(redaction.get(key), 0, f"source_manifest.redaction_invariant.{key}")

    law = exact_object(manifest.get("addition_law"), "source_manifest.addition_law")
    require_equal(law.get("name"), "Renes-Costello-Batina Algorithm 1", "source_manifest.addition_law.name")
    require_equal(law.get("gate_count"), 40, "source_manifest.addition_law.gate_count")
    require_equal(law.get("b3"), "3*b mod p", "source_manifest.addition_law.b3")
    gates = [
        exact_string(item, f"source_manifest.addition_law.normalized_gate_text[{index}]")
        for index, item in enumerate(
            exact_list(law.get("normalized_gate_text"), "source_manifest.addition_law.normalized_gate_text", 40)
        )
    ]
    gate_payload = "\n".join(gates).encode("ascii")
    gate_digest = sha256_bytes(gate_payload)
    require_equal(gate_digest, RCB_GATE_TEXT_SHA256, "source_manifest.addition_law gate digest")
    require_equal(law.get("normalized_gate_text_sha256"), gate_digest, "source_manifest.addition_law.normalized_gate_text_sha256")

    instances = exact_list(manifest.get("instances"), "source_manifest.instances", 3)
    expected_curves = ("C08", "C10", "C12")
    expected_sizes = {"C08": 3, "C10": 4, "C12": 5}
    expected_bits = {"C08": 8, "C10": 10, "C12": 12}
    cells: dict[str, CellSpec] = {}
    curve_summaries: list[dict[str, Any]] = []
    primary_points_by_cell: dict[str, tuple[Projective, ...]] = {}
    for instance_index, instance_value in enumerate(instances):
        path = f"source_manifest.instances[{instance_index}]"
        instance = exact_object(instance_value, path)
        curve_id = exact_string(instance.get("curve_id"), f"{path}.curve_id")
        require_equal(curve_id, expected_curves[instance_index], f"{path}.curve_id")
        require_equal(instance.get("bits"), expected_bits[curve_id], f"{path}.bits")
        field_record = exact_object(instance.get("field"), f"{path}.field")
        require_equal(field_record.get("type"), "prime", f"{path}.field.type")
        p = exact_int(field_record.get("p"), f"{path}.field.p", 5)
        if not is_prime(p):
            reject("field_not_prime", f"{curve_id}: p={p} is not prime", path)
        curve = exact_object(instance.get("curve"), f"{path}.curve")
        a = exact_int(curve.get("a"), f"{path}.curve.a", 0, p - 1)
        b = exact_int(curve.get("b"), f"{path}.curve.b", 0, p - 1)
        q = exact_int(curve.get("group_order"), f"{path}.curve.group_order", 3)
        if not is_prime(q):
            reject("subgroup_order_not_prime", f"{curve_id}: q={q} is not prime", path)
        require_equal(curve.get("cofactor"), 1, f"{path}.curve.cofactor")
        require_equal(curve.get("model"), "short_weierstrass_projective", f"{path}.curve.model")
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            reject("singular_curve", f"{curve_id}: singular curve", path)
        observed_order = curve_order(p, a, b)
        require_equal(observed_order, q, f"{path}.curve.group_order", "curve_order_mismatch")
        subgroup = exact_object(instance.get("subgroup"), f"{path}.subgroup")
        require_equal(subgroup.get("q"), q, f"{path}.subgroup.q")
        require_equal(subgroup.get("generator_fixed"), True, f"{path}.subgroup.generator_fixed")
        generator = parse_projective(subgroup.get("generator_projective"), f"{path}.subgroup.generator_projective", p)
        if not projective_on_curve(generator, p, a, b):
            reject("generator_off_curve", f"{curve_id}: generator is off curve", path)
        if affine_mul(q, projective_to_affine(generator, p), p, a) is not None:
            reject("generator_order_mismatch", f"{curve_id}: q*G is nonidentity", path)
        B = exact_int(instance.get("factor_base_size_B"), f"{path}.factor_base_size_B", 2)
        require_equal(B, expected_sizes[curve_id], f"{path}.factor_base_size_B")
        registries = exact_object(instance.get("registries"), f"{path}.registries")
        require_equal(set(registries), {"random_unique", "x_interval"}, f"{path}.registries")
        for family in ("random_unique", "x_interval"):
            entries = exact_list(registries.get(family), f"{path}.registries.{family}", B)
            points: list[Projective] = []
            point_ids: list[str] = []
            for point_index, entry_value in enumerate(entries):
                entry_path = f"{path}.registries.{family}[{point_index}]"
                entry = exact_object(entry_value, entry_path)
                point_id = exact_string(entry.get("point_id"), f"{entry_path}.point_id")
                point = parse_projective(entry.get("projective"), f"{entry_path}.projective", p)
                if not projective_on_curve(point, p, a, b):
                    reject("registry_point_off_curve", f"{point_id}: point is off curve", entry_path)
                points.append(point)
                point_ids.append(point_id)
            if len(set(points)) != B or len(set(point_ids)) != B:
                reject("registry_duplicate", f"{curve_id}:{family}: duplicate point or ID", path)
            cell_id = f"{curve_id}:{family}"
            point_tuple = tuple(points)
            primary_points_by_cell[cell_id] = point_tuple
            cells[cell_id] = CellSpec(
                cell_id=cell_id,
                curve_id=curve_id,
                registry=family,
                p=p,
                a=a,
                b=b,
                B=B,
                points=point_tuple,
                primary=True,
                mode_scalars=(1, 1, 1, 1, 1),
            )
        curve_summaries.append(
            {"B": B, "a": a, "b": b, "curve_id": curve_id, "group_order": q, "p": p}
        )

    require_equal(tuple(cells), PRIMARY_CELL_ORDER, "source manifest primary cell order")
    control = exact_object(manifest.get("control_source_cell"), "source_manifest.control_source_cell")
    require_equal(control.get("id"), CONTROL_CELL_ID, "source_manifest.control_source_cell.id")
    require_equal(control.get("base_cell"), "C08:random_unique", "source_manifest.control_source_cell.base_cell")
    scalars = tuple(
        exact_int(item, f"source_manifest.control_source_cell.mode_scalars[{index}]", 1)
        for index, item in enumerate(
            exact_list(control.get("mode_scalars"), "source_manifest.control_source_cell.mode_scalars", 5)
        )
    )
    require_equal(scalars, (2, 3, 4, 5, 6), "source_manifest.control_source_cell.mode_scalars")
    require_equal(control.get("source_multidegree"), [16, 16, 8, 4, 2], "source_manifest.control_source_cell.source_multidegree")
    require_equal(control.get("coordinate_scale"), 124, "source_manifest.control_source_cell.coordinate_scale")
    require_equal(control.get("quadratic_scale"), 80, "source_manifest.control_source_cell.quadratic_scale")
    require_equal(control.get("retained_advice"), False, "source_manifest.control_source_cell.retained_advice")
    base = cells["C08:random_unique"]
    cells[CONTROL_CELL_ID] = CellSpec(
        cell_id=CONTROL_CELL_ID,
        curve_id=base.curve_id,
        registry=base.registry,
        p=base.p,
        a=base.a,
        b=base.b,
        B=base.B,
        points=primary_points_by_cell["C08:random_unique"],
        primary=False,
        mode_scalars=scalars,
    )
    return cells, {
        "curve_summaries": curve_summaries,
        "gate_text_sha256": gate_digest,
        "source_manifest_sha256": digest,
        "valid": True,
    }


def audit_source_matrix(
    record: dict[str, Any], raw_bytes: bytes, source_manifest_digest: str, meter: Meter
) -> dict[str, Any]:
    digest = sha256_bytes(raw_bytes)
    require_equal(digest, SOURCE_MATRIX_SHA256, "source execution matrix SHA-256", "source_matrix_binding")
    matrix = exact_object(record.get("source_execution_matrix"), "source_execution_matrix")
    require_equal(matrix.get("id"), SOURCE_MATRIX_ID, "source_execution_matrix.id")
    require_equal(matrix.get("protocol_version"), 5, "source_execution_matrix.protocol_version")
    require_equal(matrix.get("status"), "approved_for_implementation", "source_execution_matrix.status")
    require_equal(matrix.get("interpretation"), "TARGET_BLIND_TOY_SOURCE_COMPILATION", "source_execution_matrix.interpretation")
    bindings = exact_object(matrix.get("bindings"), "source_execution_matrix.bindings")
    require_equal(bindings.get("source_manifest"), "source-instance-manifest-v1.json", "source_execution_matrix.bindings.source_manifest")
    require_equal(bindings.get("source_manifest_sha256"), source_manifest_digest, "source_execution_matrix.bindings.source_manifest_sha256")
    require_equal(bindings.get("rcb_gate_count"), 40, "source_execution_matrix.bindings.rcb_gate_count")
    require_equal(bindings.get("rcb_gate_text_sha256"), RCB_GATE_TEXT_SHA256, "source_execution_matrix.bindings.rcb_gate_text_sha256")
    require_equal(bindings.get("mode_order"), list(MODE_ORDER), "source_execution_matrix.bindings.mode_order")
    require_equal(bindings.get("addition_tree"), ADDITION_TREE, "source_execution_matrix.bindings.addition_tree")

    source_cells = exact_list(matrix.get("source_cells"), "source_execution_matrix.source_cells", 6)
    observed_cell_ids: list[str] = []
    for index, value in enumerate(source_cells):
        row = exact_object(value, f"source_execution_matrix.source_cells[{index}]")
        cell_id = f"{row.get('curve_id')}:{row.get('registry')}"
        observed_cell_ids.append(cell_id)
    require_equal(tuple(observed_cell_ids), PRIMARY_CELL_ORDER, "source_execution_matrix.source_cells")
    controls = exact_list(matrix.get("control_source_cells"), "source_execution_matrix.control_source_cells", 1)
    require_equal(exact_object(controls[0], "source_execution_matrix.control_source_cells[0]").get("id"), CONTROL_CELL_ID, "source_execution_matrix.control_source_cells[0].id")
    require_equal(matrix.get("emitted_source_tensors"), list(TENSOR_NAMES), "source_execution_matrix.emitted_source_tensors")
    require_equal(matrix.get("retained_trace_zero_advice"), list(RETAINED_NAMES), "source_execution_matrix.retained_trace_zero_advice")
    samples = exact_object(matrix.get("producer_samples"), "source_execution_matrix.producer_samples")
    require_equal(
        samples.get("derivation"),
        "two endpoints followed by distinct SHA256(EXP-ECDLP-TT-SOURCE-COMPILER-001|SOURCE-SAMPLE|curve_id|k|mode) residues modulo B",
        "source_execution_matrix.producer_samples.derivation",
    )
    for curve_id, expected in EXPECTED_SAMPLES.items():
        require_equal(samples.get(curve_id), [list(row) for row in expected], f"source_execution_matrix.producer_samples.{curve_id}")
    require_equal(matrix.get("source_partition_counts"), EXPECTED_SOURCE_COUNTS | {"scope": "source_generator_only; excludes every target specialization"}, "source_execution_matrix.source_partition_counts")
    require_equal(matrix.get("shape_ceiling_at_B5"), EXPECTED_SHAPE_CEILING, "source_execution_matrix.shape_ceiling_at_B5")
    require_equal(matrix.get("operation_vector_order"), list(OPERATION_VECTOR_KEYS), "source_execution_matrix.operation_vector_order")
    require_equal(matrix.get("source_partition_operation_cap"), SOURCE_GENERATOR_CAP, "source_execution_matrix.source_partition_operation_cap")
    require_equal(matrix.get("traffic_bucket_order"), list(SOURCE_TRAFFIC_BUCKETS), "source_execution_matrix.traffic_bucket_order")

    gates = exact_object(matrix.get("resource_gates"), "source_execution_matrix.resource_gates")
    expected_gates = {
        "wall_clock_seconds": MAX_WALL_SECONDS,
        "peak_rss_bytes": MAX_RSS_BYTES,
        "predicted_peak_live_field_words": MAX_LIVE_WORDS,
        "maximum_local_matrix_words": MAX_LOCAL_MATRIX_WORDS,
        "maximum_tt_object_words": MAX_TT_WORDS,
        "maximum_logical_traffic_words": 200_000_000_000,
        "maximum_int64_dot_length": 150,
        "maximum_int64_accumulator_bound": 2_335_637_400,
        "signed_int64_maximum": 9_223_372_036_854_775_807,
        "raw_result_bytes": MAX_RAW_RESULT_BYTES,
        "counters_may_reset": False,
    }
    require_equal(gates, expected_gates, "source_execution_matrix.resource_gates")
    accepted = exact_object(matrix.get("accepted_operation_ir"), "source_execution_matrix.accepted_operation_ir")
    require_equal(accepted.get("node_kinds"), list(ACCEPTED_IR_KINDS), "source_execution_matrix.accepted_operation_ir.node_kinds")
    require_equal(accepted.get("single_physical_mode_and_slice_per_primitive"), True, "source_execution_matrix.accepted_operation_ir.single_physical_mode_and_slice_per_primitive")
    require_equal(accepted.get("linear_physical_table_index_allowed"), False, "source_execution_matrix.accepted_operation_ir.linear_physical_table_index_allowed")
    require_equal(accepted.get("radix_decode_allowed"), False, "source_execution_matrix.accepted_operation_ir.radix_decode_allowed")
    require_equal(accepted.get("every_allocation_has_one_ir_producer"), True, "source_execution_matrix.accepted_operation_ir.every_allocation_has_one_ir_producer")
    require_equal(accepted.get("complete_runtime_ir_trace_required"), True, "source_execution_matrix.accepted_operation_ir.complete_runtime_ir_trace_required")

    boundary = exact_object(matrix.get("source_capability_boundary"), "source_execution_matrix.source_capability_boundary")
    require_equal(boundary.get("data_read_allowlist"), ["source-instance-manifest-v1.json", "source-execution-matrix-v2.json"], "source_execution_matrix.source_capability_boundary.data_read_allowlist")
    require_equal(boundary.get("target_or_mutation_digest_available"), False, "source_execution_matrix.source_capability_boundary.target_or_mutation_digest_available")
    require_equal(boundary.get("maximum_ndarray_dimensions"), 3, "source_execution_matrix.source_capability_boundary.maximum_ndarray_dimensions")
    for key in ("dynamic_imports_allowed", "dynamic_code_allowed", "child_process_allowed", "network_allowed"):
        require_equal(boundary.get(key), False, f"source_execution_matrix.source_capability_boundary.{key}")
    firewall = exact_object(matrix.get("claim_firewall"), "source_execution_matrix.claim_firewall")
    for key in ("full_tuple_enumeration_allowed", "target_specialization_claim_allowed", "breakthrough_claim", "locator_claim", "ECDLP_improvement_claim"):
        require_equal(firewall.get(key), False, f"source_execution_matrix.claim_firewall.{key}")
    return {
        "source_execution_matrix_sha256": digest,
        "source_partition_counts": EXPECTED_SOURCE_COUNTS,
        "valid": True,
    }


def audit_source_control_profile() -> dict[str, Any]:
    """Bind only the source-safe control expectations compiled into this closure."""

    return {
        "external_control_input_read": False,
        "source_control_profile_sha256": sha256_value(CONTROL_EXPECTATIONS),
        "valid": True,
    }


RAW_TOP_LEVEL_KEYS = {
    "schema",
    "protocol",
    "partition",
    "valid",
    "interpretation",
    "claim_boundary",
    "inputs",
    "provenance",
    "backend_attestation",
    "capability_audit",
    "cells",
    "controls",
    "ir_events",
    "allocation_events",
    "operation_ledger",
    "gate_rank_ledger",
    "gate_transcript",
    "accounting",
    "summary",
}


def closure_digest(
    files: Sequence[Mapping[str, Any]], path: str, *, allow_parent: bool = False
) -> str:
    rows: list[tuple[str, str]] = []
    for index, row_value in enumerate(files):
        row = exact_object(row_value, f"{path}[{index}]")
        require_keys(row, {"path", "sha256"}, f"{path}[{index}]", {"path", "sha256", "bytes"})
        relative = exact_string(row["path"], f"{path}[{index}].path")
        digest = validate_hex_digest(row["sha256"], f"{path}[{index}].sha256")
        if (
            not relative
            or relative.startswith("/")
            or (not allow_parent and ".." in Path(relative).parts)
        ):
            reject("closure_path", f"{path}[{index}]: path must be safe and relative", path)
        rows.append((relative, digest))
    if len(set(relative for relative, _ in rows)) != len(rows):
        reject("closure_duplicate_path", f"{path}: duplicate closure path", path)
    digest_state = hashlib.sha256()
    for relative, digest in sorted(rows):
        relative_bytes = relative.encode("utf-8")
        digest_bytes = bytes.fromhex(digest)
        charge_hash_bytes(len(relative_bytes) + 1 + len(digest_bytes))
        digest_state.update(relative_bytes)
        digest_state.update(b"\0")
        digest_state.update(digest_bytes)
    return digest_state.hexdigest()


def audit_raw_header(
    raw: dict[str, Any],
    source_manifest_digest: str,
    source_matrix_digest: str,
) -> dict[str, Any]:
    require_keys(raw, RAW_TOP_LEVEL_KEYS, "raw_result", RAW_TOP_LEVEL_KEYS)
    require_equal(raw.get("schema"), RAW_SCHEMA, "raw_result.schema")
    require_equal(raw.get("protocol"), PROTOCOL, "raw_result.protocol")
    require_equal(raw.get("partition"), "source_generator", "raw_result.partition")
    require_equal(exact_bool(raw.get("valid"), "raw_result.valid"), True, "raw_result.valid")
    require_equal(raw.get("interpretation"), "TARGET_BLIND_TOY_SOURCE_COMPILATION", "raw_result.interpretation")
    firewall = exact_object(raw.get("claim_boundary"), "raw_result.claim_boundary")
    expected_firewall = {
        "breakthrough_claim": False,
        "ecdlp_improvement_claim": False,
        "index_calculus_claim": False,
        "locator_claim": False,
        "target_specialization_claim": False,
        "toy_restricted_model_bound": True,
    }
    require_equal(firewall, expected_firewall, "raw_result.claim_boundary")

    inputs = exact_object(raw.get("inputs"), "raw_result.inputs")
    require_keys(
        inputs,
        {"source_manifest", "source_manifest_sha256", "source_execution_matrix", "source_execution_matrix_sha256"},
        "raw_result.inputs",
        {"source_manifest", "source_manifest_sha256", "source_execution_matrix", "source_execution_matrix_sha256"},
    )
    require_equal(inputs["source_manifest"], "source-instance-manifest-v1.json", "raw_result.inputs.source_manifest")
    require_equal(inputs["source_manifest_sha256"], source_manifest_digest, "raw_result.inputs.source_manifest_sha256")
    require_equal(inputs["source_execution_matrix"], "source-execution-matrix-v2.json", "raw_result.inputs.source_execution_matrix")
    require_equal(inputs["source_execution_matrix_sha256"], source_matrix_digest, "raw_result.inputs.source_execution_matrix_sha256")

    provenance = exact_object(raw.get("provenance"), "raw_result.provenance")
    require_keys(
        provenance,
        {
            "source_manifest_sha256",
            "source_execution_matrix_sha256",
            "rcb_gate_text_sha256",
            "local_source_files",
            "local_source_closure_sha256",
            "data_reads",
        },
        "raw_result.provenance",
        {
            "source_manifest_sha256",
            "source_execution_matrix_sha256",
            "rcb_gate_text_sha256",
            "local_source_files",
            "local_source_closure_sha256",
            "data_reads",
            "runtime_receipt_sha256",
        },
    )
    require_equal(provenance["source_manifest_sha256"], source_manifest_digest, "raw_result.provenance.source_manifest_sha256")
    require_equal(provenance["source_execution_matrix_sha256"], source_matrix_digest, "raw_result.provenance.source_execution_matrix_sha256")
    require_equal(provenance["rcb_gate_text_sha256"], RCB_GATE_TEXT_SHA256, "raw_result.provenance.rcb_gate_text_sha256")
    source_files = exact_list(provenance["local_source_files"], "raw_result.provenance.local_source_files")
    if len(source_files) < 1:
        reject("source_closure_empty", "producer local source closure is empty")
    source_paths: list[str] = []
    for index, row_value in enumerate(source_files):
        row = exact_object(row_value, f"raw_result.provenance.local_source_files[{index}]")
        source_path = exact_string(row.get("path"), f"raw_result.provenance.local_source_files[{index}].path")
        lowered = source_path.lower()
        if any(token in lowered for token in ("verify_tt_source_advice", "target", "mutation", "raw-result", "prior")):
            reject("source_closure_forbidden_path", f"forbidden producer closure path {source_path!r}")
        source_paths.append(source_path)
    observed_closure_digest = closure_digest(source_files, "raw_result.provenance.local_source_files")
    require_equal(provenance["local_source_closure_sha256"], observed_closure_digest, "raw_result.provenance.local_source_closure_sha256")
    data_reads = exact_list(provenance["data_reads"], "raw_result.provenance.data_reads", 2)
    expected_reads = {
        "source-instance-manifest-v1.json": source_manifest_digest,
        "source-execution-matrix-v2.json": source_matrix_digest,
    }
    observed_reads: dict[str, str] = {}
    for index, value in enumerate(data_reads):
        row = exact_object(value, f"raw_result.provenance.data_reads[{index}]")
        require_keys(row, {"path", "sha256"}, f"raw_result.provenance.data_reads[{index}]", {"path", "sha256", "bytes"})
        path = exact_string(row["path"], f"raw_result.provenance.data_reads[{index}].path")
        observed_reads[Path(path).name] = validate_hex_digest(row["sha256"], f"raw_result.provenance.data_reads[{index}].sha256")
    require_equal(observed_reads, expected_reads, "raw_result.provenance.data_reads", "data_read_allowlist")

    summary = exact_object(raw.get("summary"), "raw_result.summary")
    expected_summary = {
        "completed": True,
        "primary_source_cells": 6,
        "control_source_cells": 1,
        "source_cells": 7,
        "source_tensor_records": 63,
        "retained_advice_tensors": 30,
        "semantic_mismatches": 0,
        "full_tuple_enumerations": 0,
    }
    for key, expected in expected_summary.items():
        require_equal(summary.get(key), expected, f"raw_result.summary.{key}")
    return {
        "local_source_closure_sha256": observed_closure_digest,
        "local_source_files": sorted(source_paths),
        "valid": True,
    }


def scaled_points_for_cell(
    spec: CellSpec, meter: Meter
) -> tuple[tuple[Projective, ...], ...]:
    if spec.primary:
        return tuple(spec.points for _ in range(5))
    per_mode: list[tuple[Projective, ...]] = []
    for scalar in spec.mode_scalars:
        per_mode.append(
            tuple(
                tuple(scalar * coordinate % spec.p for coordinate in point)  # type: ignore[misc]
                for point in spec.points
            )
        )
    words = 5 * spec.B * 3
    meter.add_operation("muls", words)
    meter.add_operation("reductions", words)
    meter.add_traffic("registry_input", reads=words)
    meter.add_traffic("verifier_materialization", writes=words)
    return tuple(per_mode)


def tensor_artifact_record(
    tensor: Tensor, value_digest_sha256: str
) -> dict[str, Any]:
    record = tensor.canonical_record()
    record["core_digest_sha256"] = sha256_value(tensor.canonical_record())
    record["value_digest_sha256"] = value_digest_sha256
    record["word_count"] = tensor.words
    return record


def verify_source_cells(
    raw_cells_value: Any,
    specs: Mapping[str, CellSpec],
    meter: Meter,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    raw_cells = exact_list(raw_cells_value, "raw_result.cells", 7)
    cell_map: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(raw_cells):
        row = exact_object(value, f"raw_result.cells[{index}]")
        cell_id = exact_string(row.get("cell_id"), f"raw_result.cells[{index}].cell_id")
        if cell_id in cell_map:
            reject("duplicate_cell", f"duplicate source cell {cell_id!r}")
        cell_map[cell_id] = row
    require_equal(tuple(cell_map), ALL_CELL_ORDER, "raw_result.cells order")

    advice_cells: list[dict[str, Any]] = []
    xy_certificates: list[dict[str, Any]] = []
    control_cell_artifact: dict[str, Any] | None = None
    cell_reports: list[dict[str, Any]] = []
    exhaustive_tuple_count = 0
    exhaustive_tensor_checks = 0
    cached_values: dict[str, dict[str, list[int]]] = {}

    for cell_id in ALL_CELL_ORDER:
        spec = specs[cell_id]
        cell = cell_map[cell_id]
        path = f"raw_result.cells[{cell_id}]"
        required = {
            "cell_id",
            "kind",
            "curve_id",
            "registry",
            "p",
            "B",
            "mode_scalars",
            "retained_advice",
            "tensors",
            "diagnostic_samples",
            "summary",
        }
        require_keys(cell, required, path, required | {"cell_digest_sha256"})
        if "cell_digest_sha256" in cell:
            cell_payload = dict(cell)
            claimed_cell_digest = cell_payload.pop("cell_digest_sha256")
            require_equal(
                validate_hex_digest(claimed_cell_digest, f"{path}.cell_digest_sha256"),
                sha256_value(cell_payload),
                f"{path}.cell_digest_sha256",
                "cell_digest_mismatch",
            )
        require_equal(cell["curve_id"], spec.curve_id, f"{path}.curve_id")
        require_equal(cell["registry"], spec.registry, f"{path}.registry")
        require_equal(cell["p"], spec.p, f"{path}.p")
        require_equal(cell["B"], spec.B, f"{path}.B")
        require_equal(cell["kind"], "primary" if spec.primary else "modewise_rescaled_control", f"{path}.kind")
        require_equal(cell["mode_scalars"], list(spec.mode_scalars), f"{path}.mode_scalars")
        require_equal(cell["retained_advice"], spec.primary, f"{path}.retained_advice")
        tensor_rows = exact_list(cell["tensors"], f"{path}.tensors", 9)
        tensor_row_map: dict[str, dict[str, Any]] = {}
        tensors: dict[str, Tensor] = {}
        for tensor_index, tensor_value in enumerate(tensor_rows):
            tensor_record = exact_object(tensor_value, f"{path}.tensors[{tensor_index}]")
            tensor_name = exact_string(
                tensor_record.get("name", tensor_record.get("tensor_name")),
                f"{path}.tensors[{tensor_index}].name",
            )
            if tensor_name in tensor_row_map:
                reject("duplicate_tensor", f"{cell_id}: duplicate tensor {tensor_name}")
            tensor_row_map[tensor_name] = tensor_record
        require_equal(tuple(tensor_row_map), TENSOR_NAMES, f"{path}.tensors order")
        for tensor_name in TENSOR_NAMES:
            normalized_tensor_record = normalize_native_tensor_record(
                tensor_row_map[tensor_name],
                f"{path}.tensors[{tensor_name}]",
                tensor_name,
                spec.p,
                spec.B,
            )
            tensors[tensor_name] = parse_tensor(
                normalized_tensor_record,
                f"{path}.tensors[{tensor_name}]",
                tensor_name,
                spec.p,
                spec.B,
            )
            if tensors[tensor_name].tag != "tt":
                reject("unexpected_zero_source", f"{cell_id}:{tensor_name} is canonical zero")

        core_words = sum(tensor.words for tensor in tensors.values())
        meter.add_traffic(
            "verifier_materialization",
            reads=core_words,
            writes=core_words,
            copied=True,
        )

        mode_points = scaled_points_for_cell(spec, meter)
        values = {name: [0] * (spec.B**5) for name in TENSOR_NAMES}
        meter.add_traffic(
            "verifier_materialization", writes=9 * spec.B**5
        )
        meter.observe_live(10 * spec.B**5 + core_words)
        mismatch: dict[str, Any] | None = None
        for indices in iter_five_tuples_independent(spec.B):
            meter.add_traffic("registry_input", reads=15)
            points = [mode_points[mode][indices[mode]] for mode in range(5)]
            expected_point = sum_five_rcb_independent(points, spec.p, spec.a, spec.b, meter)
            expected = nine_source_values(expected_point, spec.p, meter)
            offset = linear_index(indices, spec.B)
            for tensor_name in TENSOR_NAMES:
                observed = evaluate_tensor(tensors[tensor_name], indices, meter)
                values[tensor_name][offset] = observed
                exhaustive_tensor_checks += 1
                if observed != expected[tensor_name] and mismatch is None:
                    mismatch = {
                        "cell_id": cell_id,
                        "expected": expected[tensor_name],
                        "indices": list(indices),
                        "observed": observed,
                        "tensor": tensor_name,
                    }
            exhaustive_tuple_count += 1
        if mismatch is not None:
            reject("source_semantic_mismatch", canonical_bytes(mismatch).decode("ascii").strip(), cell_id)

        tensor_reports: list[dict[str, Any]] = []
        artifact_tensors: dict[str, dict[str, Any]] = {}
        for tensor_name in TENSOR_NAMES:
            observed_digest = value_digest(values[tensor_name], spec.p, meter)
            exact_ranks = tuple(
                unfolding_rank(values[tensor_name], spec.B, cut, spec.p, meter)
                for cut in range(1, 5)
            )
            require_equal(
                tensors[tensor_name].ranks,
                exact_ranks,
                f"{path}.tensors[{tensor_name}].ranks",
                "exact_rank_mismatch",
            )
            artifact_tensors[tensor_name] = tensor_artifact_record(
                tensors[tensor_name], observed_digest
            )
            tensor_reports.append(
                {
                    "core_digest_sha256": artifact_tensors[tensor_name]["core_digest_sha256"],
                    "exact_ranks": list(exact_ranks),
                    "name": tensor_name,
                    "value_digest_sha256": observed_digest,
                    "word_count": tensors[tensor_name].words,
                }
            )

        raw_samples = exact_list(cell["diagnostic_samples"], f"{path}.diagnostic_samples", 5)
        expected_sample_indices = EXPECTED_SAMPLES[spec.curve_id]
        for sample_index, (raw_sample_value, indices) in enumerate(zip(raw_samples, expected_sample_indices)):
            sample_path = f"{path}.diagnostic_samples[{sample_index}]"
            sample = exact_object(raw_sample_value, sample_path)
            require_keys(sample, {"indices", "values"}, sample_path, {"indices", "values"})
            require_equal(sample["indices"], list(indices), f"{sample_path}.indices")
            sample_values = exact_object(sample["values"], f"{sample_path}.values")
            require_equal(set(sample_values), set(TENSOR_NAMES), f"{sample_path}.values keys")
            offset = linear_index(indices, spec.B)
            for tensor_name in TENSOR_NAMES:
                require_equal(
                    sample_values[tensor_name],
                    values[tensor_name][offset],
                    f"{sample_path}.values.{tensor_name}",
                    "diagnostic_sample_mismatch",
                )

        summary = exact_object(cell["summary"], f"{path}.summary")
        expected_cell_summary = {
            "diagnostic_sample_count": 5,
            "emitted_tensor_count": 9,
            "rcb_calls": 4,
            "semantic_mismatches": 0,
        }
        for key, expected in expected_cell_summary.items():
            require_equal(summary.get(key), expected, f"{path}.summary.{key}")

        cached_values[cell_id] = values
        cell_metadata = {
            "B": spec.B,
            "cell_id": cell_id,
            "curve_id": spec.curve_id,
            "p": spec.p,
            "registry": spec.registry,
        }
        if spec.primary:
            advice_cells.append(
                cell_metadata
                | {
                    "tensors": [artifact_tensors[name] for name in RETAINED_NAMES],
                }
            )
            xy_certificates.append(
                cell_metadata | {"tensor": artifact_tensors["XY"]}
            )
        else:
            control_cell_artifact = cell_metadata | {
                "mode_scalars": list(spec.mode_scalars),
                "tensors": [artifact_tensors[name] for name in TENSOR_NAMES],
            }
        cell_reports.append(
            cell_metadata
            | {
                "diagnostic_samples_verified": 5,
                "exhaustive_tuple_count": spec.B**5,
                "tensors": tensor_reports,
                "valid": True,
            }
        )

    if control_cell_artifact is None:
        reject("control_cell_missing", "modewise-rescaled source control is missing")
    base_values = cached_values["C08:random_unique"]
    scaled_values = cached_values[CONTROL_CELL_ID]
    for name in ("X", "Y", "Z"):
        for index, (base, scaled) in enumerate(zip(base_values[name], scaled_values[name])):
            if scaled != 124 * base % 239:
                reject(
                    "coordinate_rescaling_mismatch",
                    f"{name}[{index}]: {scaled} != 124*{base} mod 239",
                    CONTROL_CELL_ID,
                )
    for name in ("X2", "XZ", "Z2", "XY", "YZ", "Y2"):
        for index, (base, scaled) in enumerate(zip(base_values[name], scaled_values[name])):
            if scaled != 80 * base % 239:
                reject(
                    "quadratic_rescaling_mismatch",
                    f"{name}[{index}]: {scaled} != 80*{base} mod 239",
                    CONTROL_CELL_ID,
                )

    advice = {
        "cells": advice_cells,
        "retained_tensor_count": 30,
        "retained_tensor_names": list(RETAINED_NAMES),
        "schema": ADVICE_SCHEMA,
        "source_execution_matrix_sha256": SOURCE_MATRIX_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
    }
    controls = {
        "modewise_rescaled_source_cell": control_cell_artifact,
        "schema": CONTROL_CERTIFICATE_SCHEMA,
        "source_control_profile_sha256": sha256_value(CONTROL_EXPECTATIONS),
        "source_execution_matrix_sha256": SOURCE_MATRIX_SHA256,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "xy_certificates": xy_certificates,
    }
    return advice, controls, {
        "cells": cell_reports,
        "exhaustive_tensor_checks": exhaustive_tensor_checks,
        "exhaustive_tuple_count": exhaustive_tuple_count,
        "valid": True,
    }


CONTROL_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "CTL-RANK1-B3": {"exact_ranks": [1, 1, 1, 1], "ir_counts": {"emit": 1, "input_coordinate": 5}},
    "CTL-RANK1-ADD-PRODUCT-B3": {
        "product_exact_ranks": [1, 1, 1, 1],
        "product_ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 12,
            "stage_a_contract": 15,
            "stage_b_contract": 15,
        },
        "sum_exact_ranks": [2, 2, 2, 2],
        "sum_ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
        },
    },
    "CTL-ASYMMETRIC-B4": {
        "exact_ranks": [1, 2, 3, 4],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 8,
        },
        "value_digest_sha256": "068fcfffdf9aed9cb9a56e9601bec7e52c4799b7362f07e43fe6ac6b550a6977",
    },
    "CTL-COMMON-PREFIX-SUM-B3": {
        "exact_ranks": [1, 2, 2, 2],
        "raw_bonds": [2, 2, 2, 2],
        "right_only_wrong_bonds": [2, 2, 2, 2],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
        },
    },
    "CTL-CANCEL-TO-ZERO-B3": {
        "early_zero_phase": "right_sweep_mode_5",
        "exact_ranks": [0, 0, 0, 0],
        "ir_counts": {
            "absorb_left": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 5,
            "scale": 1,
        },
        "tag": "canonical_zero",
    },
    "CTL-CANCEL-TO-S-B3": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "direct_sum": 1,
            "emit": 1,
            "rank_factor": 8,
            "scale": 1,
        },
        "raw_bonds": [3, 3, 3, 3],
    },
    "CTL-INFLATED-PRODUCT-B3": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {
            "absorb_left": 4,
            "absorb_right": 4,
            "emit": 1,
            "rank_factor": 12,
            "stage_a_contract": 15,
            "stage_b_contract": 15,
        },
        "raw_product_bonds": [16, 16, 16, 16],
    },
    "CTL-GAUGE-B3": {"equal_to_source": True, "exact_ranks": [1, 1, 1, 1]},
    "CTL-B17-TRIPWIRE": {
        "exact_ranks": [1, 1, 1, 1],
        "ir_counts": {"emit": 1, "input_coordinate": 5},
        "maximum_physical_loop_trip_count": 17,
        "observed_full_tuple_traversals": 0,
    },
    "CTL-CUMULATIVE-REFUSAL": {
        "reason": "cumulative_component_cap",
        "stopped_before_operation_index": 2,
    },
    "CTL-ZERO-CLOSURE": {
        "zero_results": [True, True, False, False, True, True, True]
    },
    "CTL-TARGET-BLIND-DIGEST": {
        "source_cells": 7,
        "target_manifest_available_during_source_phase": False,
        "target_order_invariant_by_construction": True,
    },
}


def audit_control_certificates(raw_controls_value: Any) -> dict[str, Any]:
    rows = exact_list(raw_controls_value, "raw_result.controls", len(CONTROL_EXPECTATIONS))
    observed_ids: list[str] = []
    reports: list[dict[str, Any]] = []
    for index, row_value in enumerate(rows):
        path = f"raw_result.controls[{index}]"
        row = exact_object(row_value, path)
        require_keys(row, {"id", "status", "observed", "certificate_sha256"}, path, {"id", "status", "observed", "certificate_sha256"})
        control_id = exact_string(row["id"], f"{path}.id")
        observed_ids.append(control_id)
        if control_id not in CONTROL_EXPECTATIONS:
            reject("unknown_control", f"unknown source control {control_id!r}", path)
        require_equal(row["status"], "pass", f"{path}.status")
        observed = exact_object(row["observed"], f"{path}.observed")
        require_equal(observed, CONTROL_EXPECTATIONS[control_id], f"{path}.observed", "control_mismatch")
        certificate_payload = {"id": control_id, "observed": observed, "status": "pass"}
        certificate_digest = sha256_value(certificate_payload)
        require_equal(
            validate_hex_digest(row["certificate_sha256"], f"{path}.certificate_sha256"),
            certificate_digest,
            f"{path}.certificate_sha256",
            "control_certificate_digest_mismatch",
        )
        reports.append({"certificate_sha256": certificate_digest, "id": control_id, "valid": True})
    require_equal(observed_ids, list(CONTROL_EXPECTATIONS), "raw_result.controls order")
    return {"controls": reports, "source_phase_control_count": len(reports), "valid": True}


EXPECTED_BACKEND = {
    "python_executable": "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
    "python_executable_sha256": "20c9c2144a9f5202177620417e67643fb551aa31586e5d3c1361627b920cadb0",
    "python_version": "3.13.1 (v3.13.1:06714517797, Dec 3 2024, 14:00:22), Clang 15.0.0",
    "platform": "macOS-15.6-arm64-arm-64bit-Mach-O",
    "machine": "arm64",
    "numpy_version": "2.4.0",
    "numpy_distribution_file_count": 1320,
    "numpy_installed_closure_sha256": "8a802a5be64dbec34c009c0fb7b76c3b2da97c2b92ec1ee9e66796ad6dcace94",
    "numpy_multiarray_umath_sha256": "aa5ff97ea536db1e8ffba077c980842f501dc7567a2c290d7500d4c7383172e5",
    "dtype": "int64",
    "array_order": "C",
    "thread_count": 1,
}


def audit_backend_attestation(value: Any) -> dict[str, Any]:
    record = exact_object(value, "raw_result.backend_attestation")
    if record.get("protocol") == "EXP-ECDLP-TT-SOURCE-COMPILER-001-BACKEND-ATTESTATION-V1":
        return audit_native_backend_attestation(record)
    required = set(EXPECTED_BACKEND) | {
        "numpy_distribution_files",
        "loaded_extensions",
        "os_loader_dependencies",
        "standard_library_reads",
        "thread_environment",
        "maximum_observed_dot_length",
        "maximum_observed_accumulator_bound",
        "canonical_input_assertions",
        "overflow_assertions",
        "immediate_modular_reductions",
        "forbidden_dense_kernel_calls",
        "floating_point_events",
        "approximate_rank_events",
    }
    require_keys(record, required, "raw_result.backend_attestation", required)
    for key, expected in EXPECTED_BACKEND.items():
        require_equal(record.get(key), expected, f"raw_result.backend_attestation.{key}")
    distribution_files = exact_list(
        record["numpy_distribution_files"],
        "raw_result.backend_attestation.numpy_distribution_files",
        1320,
    )
    observed_closure = closure_digest(
        distribution_files,
        "raw_result.backend_attestation.numpy_distribution_files",
        allow_parent=True,
    )
    require_equal(
        observed_closure,
        EXPECTED_BACKEND["numpy_installed_closure_sha256"],
        "raw_result.backend_attestation.numpy_distribution_files closure",
        "numpy_closure_mismatch",
    )
    loaded_extensions = exact_list(
        record["loaded_extensions"], "raw_result.backend_attestation.loaded_extensions"
    )
    multiarray_matches = []
    for index, row_value in enumerate(loaded_extensions):
        row = exact_object(row_value, f"raw_result.backend_attestation.loaded_extensions[{index}]")
        require_keys(row, {"path", "sha256"}, f"raw_result.backend_attestation.loaded_extensions[{index}]", {"path", "sha256"})
        path = exact_string(row["path"], f"raw_result.backend_attestation.loaded_extensions[{index}].path")
        digest = validate_hex_digest(row["sha256"], f"raw_result.backend_attestation.loaded_extensions[{index}].sha256")
        if "_multiarray_umath" in path:
            multiarray_matches.append(digest)
    require_equal(multiarray_matches, [EXPECTED_BACKEND["numpy_multiarray_umath_sha256"]], "raw_result.backend_attestation loaded _multiarray_umath")
    require_equal(
        record["os_loader_dependencies"],
        [
            "/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate",
            "/usr/lib/libc++.1.dylib",
            "/usr/lib/libSystem.B.dylib",
        ],
        "raw_result.backend_attestation.os_loader_dependencies",
    )
    standard_library_reads = exact_list(
        record["standard_library_reads"], "raw_result.backend_attestation.standard_library_reads"
    )
    for index, row_value in enumerate(standard_library_reads):
        row = exact_object(row_value, f"raw_result.backend_attestation.standard_library_reads[{index}]")
        require_keys(row, {"path", "sha256"}, f"raw_result.backend_attestation.standard_library_reads[{index}]", {"path", "sha256", "bytes"})
        exact_string(row["path"], f"raw_result.backend_attestation.standard_library_reads[{index}].path")
        validate_hex_digest(row["sha256"], f"raw_result.backend_attestation.standard_library_reads[{index}].sha256")
    thread_environment = exact_object(record["thread_environment"], "raw_result.backend_attestation.thread_environment")
    require_equal(
        set(thread_environment),
        {"PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"},
        "raw_result.backend_attestation.thread_environment keys",
    )
    for key, setting in thread_environment.items():
        expected = "0" if key == "PYTHONHASHSEED" else "1"
        require_equal(setting, expected, f"raw_result.backend_attestation.thread_environment.{key}")
    maximum_dot = exact_int(record["maximum_observed_dot_length"], "raw_result.backend_attestation.maximum_observed_dot_length", 0, 150)
    maximum_bound = exact_int(record["maximum_observed_accumulator_bound"], "raw_result.backend_attestation.maximum_observed_accumulator_bound", 0, 2_335_637_400)
    require_equal(record["forbidden_dense_kernel_calls"], 0, "raw_result.backend_attestation.forbidden_dense_kernel_calls")
    require_equal(record["floating_point_events"], 0, "raw_result.backend_attestation.floating_point_events")
    require_equal(record["approximate_rank_events"], 0, "raw_result.backend_attestation.approximate_rank_events")
    for key in ("canonical_input_assertions", "overflow_assertions", "immediate_modular_reductions"):
        if exact_int(record[key], f"raw_result.backend_attestation.{key}", 1) < 1:
            reject("backend_assertion_missing", f"raw_result.backend_attestation.{key} must be positive")
    return {
        "maximum_observed_accumulator_bound": maximum_bound,
        "maximum_observed_dot_length": maximum_dot,
        "numpy_installed_closure_sha256": observed_closure,
        "valid": True,
    }


def audit_native_backend_attestation(record: Mapping[str, Any]) -> dict[str, Any]:
    path = "raw_result.backend_attestation"
    require_equal(exact_bool(record.get("valid"), f"{path}.valid"), True, f"{path}.valid")
    matrix = exact_object(record.get("source_execution_matrix"), f"{path}.source_execution_matrix")
    require_equal(matrix.get("path"), "source-execution-matrix-v2.json", f"{path}.source_execution_matrix.path")
    require_equal(matrix.get("sha256"), SOURCE_MATRIX_SHA256, f"{path}.source_execution_matrix.sha256")
    checks = exact_list(record.get("checks"), f"{path}.checks", 14)
    check_map: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(checks):
        row = exact_object(value, f"{path}.checks[{index}]")
        require_keys(row, {"field", "expected", "observed", "match"}, f"{path}.checks[{index}]", {"field", "expected", "observed", "match"})
        field_name = exact_string(row["field"], f"{path}.checks[{index}].field")
        if field_name in check_map:
            reject("backend_duplicate_check", f"duplicate backend check {field_name!r}")
        require_equal(exact_bool(row["match"], f"{path}.checks[{index}].match"), True, f"{path}.checks[{index}].match")
        require_equal(row["observed"], row["expected"], f"{path}.checks[{index}]")
        check_map[field_name] = row
    require_equal(
        set(check_map),
        {
            "python_executable",
            "python_executable_sha256",
            "python_version",
            "platform",
            "machine",
            "numpy_version",
            "numpy_distribution_file_count",
            "numpy_installed_closure_sha256",
            "numpy_multiarray_umath_sha256",
            "os_loader_dependencies_loaded",
            "python_hash_seed_deterministic",
            "thread_count",
            "dtype_contract",
            "array_order_contract",
        },
        f"{path}.checks fields",
    )
    for key in (
        "python_executable",
        "python_executable_sha256",
        "python_version",
        "platform",
        "machine",
        "numpy_version",
        "numpy_distribution_file_count",
        "numpy_installed_closure_sha256",
        "numpy_multiarray_umath_sha256",
    ):
        require_equal(check_map[key]["observed"], EXPECTED_BACKEND[key], f"{path}.checks.{key}")
    require_equal(check_map["thread_count"]["observed"], 1, f"{path}.checks.thread_count")
    require_equal(check_map["dtype_contract"]["observed"], "int64", f"{path}.checks.dtype_contract")
    require_equal(check_map["array_order_contract"]["observed"], "C", f"{path}.checks.array_order_contract")
    observed = exact_object(record.get("observed"), f"{path}.observed")
    members = exact_list(observed.get("numpy_distribution_members"), f"{path}.observed.numpy_distribution_members", 1320)
    closure = closure_digest(
        members,
        f"{path}.observed.numpy_distribution_members",
        allow_parent=True,
    )
    require_equal(closure, EXPECTED_BACKEND["numpy_installed_closure_sha256"], f"{path}.observed.numpy_installed_closure_sha256")
    require_equal(observed.get("numpy_installed_closure_sha256"), closure, f"{path}.observed.numpy_installed_closure_sha256")
    multiarray = exact_object(observed.get("numpy_multiarray_umath"), f"{path}.observed.numpy_multiarray_umath")
    require_equal(multiarray.get("sha256"), EXPECTED_BACKEND["numpy_multiarray_umath_sha256"], f"{path}.observed.numpy_multiarray_umath.sha256")
    loaded_extensions = exact_list(observed.get("loaded_numpy_extensions"), f"{path}.observed.loaded_numpy_extensions")
    matches = [
        row.get("sha256")
        for row in loaded_extensions
        if isinstance(row, dict) and "_multiarray_umath" in str(row.get("path"))
    ]
    require_equal(matches, [EXPECTED_BACKEND["numpy_multiarray_umath_sha256"]], f"{path}.observed.loaded_numpy_extensions")
    loaders = [
        "/System/Library/Frameworks/Accelerate.framework/Versions/A/Accelerate",
        "/usr/lib/libc++.1.dylib",
        "/usr/lib/libSystem.B.dylib",
    ]
    require_equal(observed.get("expected_os_loader_dependencies"), loaders, f"{path}.observed.expected_os_loader_dependencies")
    loaded_images = exact_list(observed.get("loaded_os_images"), f"{path}.observed.loaded_os_images")
    for loader in loaders:
        if loader not in loaded_images:
            reject("backend_loader_missing", f"required loader {loader!r} is absent")
    environment = exact_object(observed.get("thread_environment"), f"{path}.observed.thread_environment")
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        require_equal(environment.get(key), "1", f"{path}.observed.thread_environment.{key}")
    if environment.get("PYTHONHASHSEED") in (None, "random"):
        reject("backend_hash_seed", "PYTHONHASHSEED is not deterministic")
    return {
        "attestation_schema": record.get("protocol"),
        "numpy_installed_closure_sha256": closure,
        "valid": True,
    }


def audit_runtime_receipt_digest(
    receipt_value: Any,
    raw_provenance_value: Any,
) -> str:
    receipt = exact_object(receipt_value, "raw_result.capability_audit.runtime_receipt")
    runtime_receipt_digest = sha256_value(receipt)
    raw_provenance = exact_object(raw_provenance_value, "raw_result.provenance")
    require_equal(
        validate_hex_digest(
            raw_provenance.get("runtime_receipt_sha256"),
            "raw_result.provenance.runtime_receipt_sha256",
        ),
        runtime_receipt_digest,
        "raw_result.provenance.runtime_receipt_sha256",
        "runtime_receipt_digest_mismatch",
    )
    return runtime_receipt_digest


def audit_staging_runtime_receipt(
    value: Any,
    *,
    expected_static_closure_audit_sha256: str,
    raw_provenance_value: Any,
    manifest_bytes: bytes,
    matrix_bytes: bytes,
) -> dict[str, Any]:
    path = "raw_result.capability_audit.runtime_receipt"
    receipt = exact_object(value, path)
    required = {
        "denied_event_count",
        "denied_events",
        "directory_paths",
        "environment",
        "environment_events",
        "event_counts",
        "expected_stage_sha256",
        "filesystem_event_names",
        "finished_ns",
        "read_file_count",
        "read_files",
        "runtime_files",
        "runtime_roots",
        "schema",
        "stage_file_count",
        "stage_files",
        "stage_root",
        "stage_root_basename",
        "stage_sha256",
        "stage_started_ns",
        "static_closure_audit_sha256",
        "valid",
    }
    require_keys(receipt, required, path, required)
    require_equal(
        receipt["schema"],
        "tt-source-staging-runtime-receipt-v1",
        f"{path}.schema",
    )
    require_equal(exact_bool(receipt["valid"], f"{path}.valid"), True, f"{path}.valid")
    require_equal(receipt["denied_event_count"], 0, f"{path}.denied_event_count")
    require_equal(receipt["denied_events"], [], f"{path}.denied_events")
    expected_environment = {
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
        "VECLIB_MAXIMUM_THREADS": "1",
    }
    require_equal(receipt["environment"], expected_environment, f"{path}.environment")
    expected_environment_events = [
        {"event": "os.putenv", "key": "OPENBLAS_MAIN_FREE", "value": "1"},
        {"event": "os.putenv", "key": "GOTOBLAS_MAIN_FREE", "value": "1"},
        {"event": "os.unsetenv", "key": "OPENBLAS_MAIN_FREE", "value": None},
        {"event": "os.unsetenv", "key": "GOTOBLAS_MAIN_FREE", "value": None},
    ]
    require_equal(
        receipt["environment_events"],
        expected_environment_events,
        f"{path}.environment_events",
    )
    require_equal(
        receipt["filesystem_event_names"],
        ["open", "stat", "lstat", "listdir", "scandir", "glob", "readlink", "chdir"],
        f"{path}.filesystem_event_names",
    )
    event_counts = exact_object(receipt["event_counts"], f"{path}.event_counts")
    expected_event_keys = {
        "open", "stat", "lstat", "listdir", "scandir", "glob", "readlink", "chdir",
        "compile", "ctypes_dlopen", "exec", "import",
    }
    require_equal(set(event_counts), expected_event_keys, f"{path}.event_counts keys")
    for key in expected_event_keys:
        exact_int(event_counts[key], f"{path}.event_counts.{key}", 0)

    expected_stage_names = {
        "attest_tt_backend.py",
        "compile_tt_source_advice.py",
        "run_tt_source_partition.py",
        "source-execution-matrix-v2.json",
        "source-instance-manifest-v1.json",
        "tt_source_runtime.py",
    }
    stage_files = exact_list(receipt["stage_files"], f"{path}.stage_files", 6)
    normalized_stage_files: list[dict[str, Any]] = []
    for index, row_value in enumerate(stage_files):
        row_path = f"{path}.stage_files[{index}]"
        row = exact_object(row_value, row_path)
        require_keys(row, {"bytes", "path", "sha256"}, row_path, {"bytes", "path", "sha256"})
        name = exact_string(row["path"], f"{row_path}.path")
        normalized_stage_files.append(
            {
                "bytes": exact_int(row["bytes"], f"{row_path}.bytes", 1),
                "path": name,
                "sha256": validate_hex_digest(row["sha256"], f"{row_path}.sha256"),
            }
        )
    stage_by_name = {item["path"]: item for item in normalized_stage_files}
    require_equal(set(stage_by_name), expected_stage_names, f"{path}.stage_files names")
    require_equal(
        stage_by_name["source-execution-matrix-v2.json"],
        {
            "bytes": len(matrix_bytes),
            "path": "source-execution-matrix-v2.json",
            "sha256": sha256_bytes(matrix_bytes),
        },
        f"{path}.stage_files source execution matrix",
    )
    require_equal(
        stage_by_name["source-instance-manifest-v1.json"],
        {
            "bytes": len(manifest_bytes),
            "path": "source-instance-manifest-v1.json",
            "sha256": sha256_bytes(manifest_bytes),
        },
        f"{path}.stage_files source manifest",
    )
    raw_provenance = exact_object(raw_provenance_value, "raw_result.provenance")
    producer_rows = exact_list(
        raw_provenance.get("local_source_files"),
        "raw_result.provenance.local_source_files",
        3,
    )
    for index, row_value in enumerate(producer_rows):
        row_path = f"raw_result.provenance.local_source_files[{index}]"
        row = exact_object(row_value, row_path)
        name = exact_string(row.get("path"), f"{row_path}.path")
        require_equal(
            stage_by_name.get(name),
            {
                "bytes": exact_int(row.get("bytes"), f"{row_path}.bytes", 1),
                "path": name,
                "sha256": validate_hex_digest(row.get("sha256"), f"{row_path}.sha256"),
            },
            row_path,
            "staging_producer_identity_mismatch",
        )
    require_equal(receipt["stage_file_count"], 6, f"{path}.stage_file_count")
    computed_stage_digest = closure_digest(normalized_stage_files, f"{path}.stage_files")
    stage_digest_value = validate_hex_digest(receipt["stage_sha256"], f"{path}.stage_sha256")
    require_equal(stage_digest_value, computed_stage_digest, f"{path}.stage_sha256")
    require_equal(
        validate_hex_digest(receipt["expected_stage_sha256"], f"{path}.expected_stage_sha256"),
        stage_digest_value,
        f"{path}.expected_stage_sha256",
    )
    static_audit_digest = validate_hex_digest(
        receipt["static_closure_audit_sha256"], f"{path}.static_closure_audit_sha256"
    )
    require_equal(
        static_audit_digest,
        expected_static_closure_audit_sha256,
        f"{path}.static_closure_audit_sha256",
        "stale_static_closure_audit",
    )
    stage_root = exact_string(receipt["stage_root"], f"{path}.stage_root")
    if not os.path.isabs(stage_root) or os.path.normpath(stage_root) != stage_root:
        reject("staging_root_path", f"{path}: staging root must be normalized and absolute")
    stage_basename = exact_string(receipt["stage_root_basename"], f"{path}.stage_root_basename")
    if not stage_basename.startswith("tt-source-partition-"):
        reject("staging_root_name", f"{path}: unexpected staging root basename")
    require_equal(os.path.basename(stage_root), stage_basename, f"{path}.stage_root_basename")
    runtime_roots = [
        exact_string(item, f"{path}.runtime_roots[{index}]")
        for index, item in enumerate(exact_list(receipt["runtime_roots"], f"{path}.runtime_roots"))
    ]
    expected_runtime_roots = [
        str(Path(EXPECTED_BACKEND["python_executable"]).parent.parent),
    ]
    require_equal(runtime_roots, expected_runtime_roots, f"{path}.runtime_roots")
    runtime_files = [
        exact_string(item, f"{path}.runtime_files[{index}]")
        for index, item in enumerate(exact_list(receipt["runtime_files"], f"{path}.runtime_files"))
    ]
    expected_runtime_files = [
        "/System/Library/CoreServices/SystemVersion.plist",
    ]
    require_equal(runtime_files, expected_runtime_files, f"{path}.runtime_files")
    read_files = exact_list(receipt["read_files"], f"{path}.read_files")
    require_equal(receipt["read_file_count"], len(read_files), f"{path}.read_file_count")
    read_paths: set[str] = set()
    stage_read_names: set[str] = set()
    for index, row_value in enumerate(read_files):
        row_path = f"{path}.read_files[{index}]"
        row = exact_object(row_value, row_path)
        require_keys(row, {"path", "sha256"}, row_path, {"path", "sha256"})
        read_path = exact_string(row["path"], f"{row_path}.path")
        if (
            not os.path.isabs(read_path)
            or os.path.normpath(read_path) != read_path
            or read_path in read_paths
        ):
            reject("runtime_read_path", f"{row_path}: path must be unique, normalized, and absolute")
        stage_relative: str | None = None
        if lexical_path_within(read_path, stage_root):
            stage_relative = os.path.relpath(read_path, stage_root)
            if stage_relative not in expected_stage_names:
                reject("runtime_stage_read", f"{row_path}: unexpected staged read {stage_relative!r}")
            stage_read_names.add(stage_relative)
        elif read_path not in runtime_files and not any(
            lexical_path_within(read_path, root) for root in runtime_roots
        ):
            reject("runtime_read_outside_allowlist", f"{row_path}: read is outside the runtime allowlist")
        read_paths.add(read_path)
        observed_digest = validate_hex_digest(row["sha256"], f"{row_path}.sha256")
        if stage_relative is not None:
            require_equal(
                observed_digest,
                stage_by_name[stage_relative]["sha256"],
                f"{row_path}.sha256",
                "runtime_stage_read_digest_mismatch",
            )
    require_equal(
        {
            "attest_tt_backend.py",
            "compile_tt_source_advice.py",
            "source-execution-matrix-v2.json",
            "source-instance-manifest-v1.json",
            "tt_source_runtime.py",
        }
        - stage_read_names,
        set(),
        f"{path}.read_files",
        "runtime_required_stage_read_missing",
    )
    directory_paths = [
        exact_string(item, f"{path}.directory_paths[{index}]")
        for index, item in enumerate(exact_list(receipt["directory_paths"], f"{path}.directory_paths"))
    ]
    require_equal(directory_paths, sorted(set(directory_paths)), f"{path}.directory_paths order")
    for directory_path in directory_paths:
        if not os.path.isabs(directory_path) or os.path.normpath(directory_path) != directory_path:
            reject("runtime_directory_path", f"{path}: directory paths must be normalized and absolute")
        if directory_path != stage_root and not any(
            lexical_path_within(directory_path, root) for root in runtime_roots
        ):
            reject("runtime_directory_outside_allowlist", f"{path}: directory is outside the allowlist")
    started_ns = exact_int(receipt["stage_started_ns"], f"{path}.stage_started_ns", 0)
    finished_ns = exact_int(receipt["finished_ns"], f"{path}.finished_ns", started_ns)
    runtime_receipt_digest = audit_runtime_receipt_digest(
        receipt,
        raw_provenance_value,
    )
    return {
        "environment_event_count": len(expected_environment_events),
        "event_counts": event_counts,
        "finished_ns": finished_ns,
        "read_file_count": len(read_files),
        "stage_file_count": 6,
        "stage_sha256": stage_digest_value,
        "stage_started_ns": started_ns,
        "static_closure_audit_sha256": static_audit_digest,
        "runtime_receipt_sha256": runtime_receipt_digest,
        "valid": True,
    }


def audit_capability(
    value: Any,
    *,
    expected_static_closure_audit_sha256: str,
    raw_provenance_value: Any,
    manifest_bytes: bytes,
    matrix_bytes: bytes,
) -> dict[str, Any]:
    record = exact_object(value, "raw_result.capability_audit")
    exact_zero_keys = (
        "full_tuple_enumerations",
        "full_tuple_values_read",
        "prior_artifact_reads",
        "target_manifest_reads_in_source_phase",
        "mutation_manifest_reads_in_source_or_target_phase",
        "dynamic_code_events",
        "dynamic_import_events",
        "child_processes",
        "network_events",
        "forbidden_kernel_calls",
        "linear_physical_table_index_events",
        "radix_decode_events",
        "five_dimensional_array_events",
    )
    required = set(exact_zero_keys) | {
        "maximum_live_mode_indices_outside_tt_kernels",
        "diagnostic_sample_count",
        "maximum_ndarray_dimensions",
        "filesystem_audit_passed",
        "environment_audit_passed",
        "ast_call_graph_audit_passed",
        "closed_ir_audit_passed",
        "isolated_staging_root",
        "repository_git_metadata_present",
        "target_or_mutation_files_present",
        "stdout_only_output",
        "runtime_receipt",
    }
    require_keys(record, required, "raw_result.capability_audit", required)
    for key in exact_zero_keys:
        require_equal(record[key], 0, f"raw_result.capability_audit.{key}")
    maximum_modes = exact_int(
        record["maximum_live_mode_indices_outside_tt_kernels"],
        "raw_result.capability_audit.maximum_live_mode_indices_outside_tt_kernels",
        0,
        1,
    )
    require_equal(record["diagnostic_sample_count"], 35, "raw_result.capability_audit.diagnostic_sample_count")
    maximum_dimensions = exact_int(record["maximum_ndarray_dimensions"], "raw_result.capability_audit.maximum_ndarray_dimensions", 0, 3)
    for key in ("filesystem_audit_passed", "environment_audit_passed", "ast_call_graph_audit_passed", "closed_ir_audit_passed", "isolated_staging_root", "stdout_only_output"):
        require_equal(exact_bool(record[key], f"raw_result.capability_audit.{key}"), True, f"raw_result.capability_audit.{key}")
    for key in ("repository_git_metadata_present", "target_or_mutation_files_present"):
        require_equal(exact_bool(record[key], f"raw_result.capability_audit.{key}"), False, f"raw_result.capability_audit.{key}")
    runtime_receipt = audit_staging_runtime_receipt(
        record["runtime_receipt"],
        expected_static_closure_audit_sha256=expected_static_closure_audit_sha256,
        raw_provenance_value=raw_provenance_value,
        manifest_bytes=manifest_bytes,
        matrix_bytes=matrix_bytes,
    )
    return {
        "diagnostic_sample_count": 35,
        "maximum_live_mode_indices_outside_tt_kernels": maximum_modes,
        "maximum_ndarray_dimensions": maximum_dimensions,
        "runtime_receipt": runtime_receipt,
        "valid": True,
    }


def audit_capability_development(value: Any) -> dict[str, Any]:
    """Validate intrinsic counters while preserving external attestation failures."""

    record = exact_object(value, "raw_result.capability_audit")
    exact_zero_keys = (
        "full_tuple_enumerations",
        "full_tuple_values_read",
        "prior_artifact_reads",
        "target_manifest_reads_in_source_phase",
        "mutation_manifest_reads_in_source_or_target_phase",
        "dynamic_code_events",
        "dynamic_import_events",
        "child_processes",
        "network_events",
        "forbidden_kernel_calls",
        "linear_physical_table_index_events",
        "radix_decode_events",
        "five_dimensional_array_events",
    )
    boolean_keys = (
        "filesystem_audit_passed",
        "environment_audit_passed",
        "ast_call_graph_audit_passed",
        "closed_ir_audit_passed",
        "isolated_staging_root",
        "repository_git_metadata_present",
        "target_or_mutation_files_present",
        "stdout_only_output",
    )
    required = set(exact_zero_keys) | set(boolean_keys) | {
        "maximum_live_mode_indices_outside_tt_kernels",
        "diagnostic_sample_count",
        "maximum_ndarray_dimensions",
        "runtime_receipt",
    }
    require_keys(record, required, "raw_result.capability_audit", required)
    for key in exact_zero_keys:
        require_equal(record[key], 0, f"raw_result.capability_audit.{key}")
    maximum_modes = exact_int(
        record["maximum_live_mode_indices_outside_tt_kernels"],
        "raw_result.capability_audit.maximum_live_mode_indices_outside_tt_kernels",
        0,
        1,
    )
    require_equal(
        record["diagnostic_sample_count"],
        35,
        "raw_result.capability_audit.diagnostic_sample_count",
    )
    maximum_dimensions = exact_int(
        record["maximum_ndarray_dimensions"],
        "raw_result.capability_audit.maximum_ndarray_dimensions",
        0,
        3,
    )
    reported = {
        key: exact_bool(record[key], f"raw_result.capability_audit.{key}")
        for key in boolean_keys
    }
    runtime_receipt = exact_object(
        record["runtime_receipt"],
        "raw_result.capability_audit.runtime_receipt",
    )
    require_equal(
        runtime_receipt,
        {
            "schema": "tt-source-staging-runtime-receipt-v1",
            "status": "unattested_development",
            "valid": False,
        },
        "raw_result.capability_audit.runtime_receipt",
    )
    return {
        "artifact_freeze_authorized": False,
        "diagnostic_sample_count": 35,
        "external_attestations_pending": [
            "filesystem_audit",
            "environment_audit",
            "ast_call_graph_audit",
            "isolated_staging_audit",
        ],
        "maximum_live_mode_indices_outside_tt_kernels": maximum_modes,
        "maximum_ndarray_dimensions": maximum_dimensions,
        "reported_external_flags": reported,
        "structural_valid": True,
        "valid": False,
    }


def exact_operation_vector(value: Any, path: str) -> dict[str, int]:
    record = exact_object(value, path)
    require_equal(set(record), set(OPERATION_VECTOR_KEYS), f"{path} keys")
    return {
        key: exact_int(record[key], f"{path}.{key}", 0)
        for key in OPERATION_VECTOR_KEYS
    }


def vector_add(left: Mapping[str, int], right: Mapping[str, int]) -> dict[str, int]:
    return {key: left[key] + right[key] for key in OPERATION_VECTOR_KEYS}


def exact_traffic_vector(
    value: Any, path: str, buckets: Sequence[str]
) -> dict[str, dict[str, int]]:
    record = exact_object(value, path)
    require_equal(set(record), set(buckets), f"{path} keys")
    result: dict[str, dict[str, int]] = {}
    for bucket in buckets:
        row = exact_object(record[bucket], f"{path}.{bucket}")
        require_keys(row, {"reads", "writes"}, f"{path}.{bucket}", {"reads", "writes"})
        result[bucket] = {
            "reads": exact_int(row["reads"], f"{path}.{bucket}.reads", 0),
            "writes": exact_int(row["writes"], f"{path}.{bucket}.writes", 0),
        }
    return result


def traffic_total(value: Mapping[str, Mapping[str, int]]) -> int:
    return sum(row["reads"] + row["writes"] for row in value.values())


def audit_accounting(value: Any) -> dict[str, Any]:
    record = exact_object(value, "raw_result.accounting")
    required = {
        "operation_vector",
        "traffic_buckets",
        "logical_traffic_words",
        "normalization_calls",
        "streamed_prefix_factorizations",
        "two_sweep_factorizations",
        "total_rank_factorizations",
        "maximum_local_matrix_words",
        "maximum_tt_object_words",
        "peak_live_field_words",
        "peak_rss_bytes",
        "wall_clock_ns",
        "cpu_ns",
        "counters_reset",
    }
    require_keys(record, required, "raw_result.accounting", required | {"serialized_raw_result_bytes"})
    operations = exact_operation_vector(record["operation_vector"], "raw_result.accounting.operation_vector")
    for key, cap in SOURCE_GENERATOR_CAP.items():
        if operations[key] > cap:
            reject("producer_operation_cap", f"producer {key}={operations[key]} exceeds {cap}")
    traffic_values = exact_traffic_vector(
        record["traffic_buckets"],
        "raw_result.accounting.traffic_buckets",
        SOURCE_TRAFFIC_BUCKETS,
    )
    observed_traffic_total = traffic_total(traffic_values)
    require_equal(record["logical_traffic_words"], observed_traffic_total, "raw_result.accounting.logical_traffic_words")
    if observed_traffic_total > 200_000_000_000:
        reject("producer_traffic_cap", f"producer logical traffic {observed_traffic_total} exceeds cap")
    census_caps = {
        "normalization_calls": 1022,
        "streamed_prefix_factorizations": 1512,
        "two_sweep_factorizations": 8176,
        "total_rank_factorizations": 9688,
    }
    census: dict[str, int] = {}
    for key, cap in census_caps.items():
        census[key] = exact_int(record[key], f"raw_result.accounting.{key}", 0, cap)
    require_equal(
        census["streamed_prefix_factorizations"] + census["two_sweep_factorizations"],
        census["total_rank_factorizations"],
        "raw_result.accounting factorization reconciliation",
    )
    maximum_matrix = exact_int(record["maximum_local_matrix_words"], "raw_result.accounting.maximum_local_matrix_words", 0, MAX_LOCAL_MATRIX_WORDS)
    maximum_tt = exact_int(record["maximum_tt_object_words"], "raw_result.accounting.maximum_tt_object_words", 0, MAX_TT_WORDS)
    peak_live = exact_int(record["peak_live_field_words"], "raw_result.accounting.peak_live_field_words", 0, MAX_LIVE_WORDS)
    peak_rss = exact_int(record["peak_rss_bytes"], "raw_result.accounting.peak_rss_bytes", 0, MAX_RSS_BYTES)
    wall_ns = exact_int(record["wall_clock_ns"], "raw_result.accounting.wall_clock_ns", 0, MAX_WALL_SECONDS * 1_000_000_000)
    cpu_ns = exact_int(record["cpu_ns"], "raw_result.accounting.cpu_ns", 0, MAX_CPU_SECONDS * 1_000_000_000)
    require_equal(exact_bool(record["counters_reset"], "raw_result.accounting.counters_reset"), False, "raw_result.accounting.counters_reset")
    return {
        "census": census,
        "cpu_ns": cpu_ns,
        "logical_traffic_words": observed_traffic_total,
        "maximum_local_matrix_words": maximum_matrix,
        "maximum_tt_object_words": maximum_tt,
        "operation_vector": operations,
        "peak_live_field_words": peak_live,
        "peak_rss_bytes": peak_rss,
        "traffic_buckets": traffic_values,
        "valid": True,
        "wall_clock_ns": wall_ns,
    }


@dataclass(frozen=True)
class DenseArray:
    shape: tuple[int, ...]
    values: tuple[int, ...]

    @property
    def words(self) -> int:
        return len(self.values)

    def at2(self, row: int, column: int) -> int:
        if len(self.shape) != 2:
            reject("transcript_array_rank", "two-dimensional array required")
        return self.values[row * self.shape[1] + column]

    def at3(self, first: int, second: int, third: int) -> int:
        if len(self.shape) != 3:
            reject("transcript_array_rank", "three-dimensional array required")
        return self.values[(first * self.shape[1] + second) * self.shape[2] + third]

    def record(self) -> dict[str, Any]:
        return {"shape": list(self.shape), "values": list(self.values)}


def parse_dense_array(value: Any, path: str, p: int) -> DenseArray:
    record = exact_object(value, path)
    require_keys(record, {"shape", "values", "digest_sha256"}, path, {"shape", "values", "digest_sha256"})
    shape = tuple(
        exact_int(item, f"{path}.shape[{index}]", 0)
        for index, item in enumerate(exact_list(record["shape"], f"{path}.shape"))
    )
    if not 1 <= len(shape) <= 3:
        reject("transcript_array_dimensions", f"{path}: array must have one to three dimensions")
    words = product(shape)
    if words > MAX_LOCAL_MATRIX_WORDS:
        reject("transcript_array_word_gate", f"{path}: {words} words exceeds local gate")
    values = tuple(
        exact_int(item, f"{path}.values[{index}]", 0, p - 1)
        for index, item in enumerate(exact_list(record["values"], f"{path}.values", words))
    )
    array = DenseArray(shape, values)
    require_equal(
        validate_hex_digest(record["digest_sha256"], f"{path}.digest_sha256"),
        sha256_value(array.record()),
        f"{path}.digest_sha256",
        "transcript_array_digest_mismatch",
    )
    return array


def array_record(array: DenseArray) -> dict[str, Any]:
    record = array.record()
    record["digest_sha256"] = sha256_value(record)
    return record


def assert_array_equal(actual: DenseArray, expected: DenseArray, path: str) -> None:
    if actual != expected:
        reject(
            "transcript_arithmetic_mismatch",
            f"{path}: output does not equal independent replay",
            path,
        )


def matrix_product(left: DenseArray, right: DenseArray, p: int) -> DenseArray:
    if len(left.shape) != 2 or len(right.shape) != 2 or left.shape[1] != right.shape[0]:
        reject("transcript_matmul_shape", "matrix-product payload shapes do not join")
    rows, inner, columns = left.shape[0], left.shape[1], right.shape[1]
    output: list[int] = []
    for row in range(rows):
        for column in range(columns):
            total = 0
            for cursor in range(inner):
                total += left.at2(row, cursor) * right.at2(cursor, column)
            output.append(total % p)
    return DenseArray((rows, columns), tuple(output))


def independent_rank_factor(array: DenseArray, p: int) -> tuple[DenseArray, DenseArray, list[int], dict[str, int]]:
    if len(array.shape) != 2:
        reject("rank_factor_shape", "rank-factor input must be a matrix")
    rows, columns = array.shape
    work = [list(array.values[row * columns : (row + 1) * columns]) for row in range(rows)]
    pivots: list[int] = []
    pivot_rows: list[int] = []
    used_rows: set[int] = set()
    operations = {key: 0 for key in OPERATION_VECTOR_KEYS}
    operations["copied_words"] = rows * columns
    for column in range(columns):
        chosen: int | None = None
        for candidate in range(rows):
            if candidate in used_rows:
                continue
            operations["comparisons"] += 1
            if work[candidate][column] != 0:
                chosen = candidate
                break
        if chosen is None:
            continue
        inverse = pow(work[chosen][column], -1, p)
        operations["inversions"] += 1
        operations["reductions"] += 1
        operations["comparisons"] += 1
        for cursor in range(columns):
            work[chosen][cursor] = work[chosen][cursor] * inverse % p
        operations["muls"] += columns
        operations["reductions"] += columns
        for row in range(rows):
            if row == chosen:
                continue
            operations["comparisons"] += 1
            factor = work[row][column]
            if factor == 0:
                continue
            for cursor in range(columns):
                product_value = factor * work[chosen][cursor] % p
                work[row][cursor] = (work[row][cursor] - product_value) % p
            operations["muls"] += columns
            operations["subs"] += columns
            operations["reductions"] += 2 * columns
        used_rows.add(chosen)
        pivots.append(column)
        pivot_rows.append(chosen)
    rank = len(pivots)
    c_values = tuple(array.at2(row, column) for row in range(rows) for column in pivots)
    f_values = tuple(
        work[source_row][column]
        for source_row in pivot_rows
        for column in range(columns)
    )
    operations["copied_words"] += len(c_values) + len(f_values)
    return (
        DenseArray((rows, rank), c_values),
        DenseArray((rank, columns), f_values),
        pivots,
        operations,
    )


def replay_direct_sum(inputs: Sequence[DenseArray], position: str, p: int) -> DenseArray:
    if len(inputs) < 2 or any(len(array.shape) != 3 for array in inputs):
        reject("direct_sum_payload", "direct-sum payload requires at least two rank-three cores")
    physical = inputs[0].shape[1]
    if any(array.shape[1] != physical for array in inputs):
        reject("direct_sum_payload", "direct-sum physical dimensions differ")
    if position == "first":
        if any(array.shape[0] != 1 for array in inputs):
            reject("direct_sum_payload", "first-core direct sum requires left boundary one")
        right = sum(array.shape[2] for array in inputs)
        output = [0] * (physical * right)
        offset = 0
        for array in inputs:
            for physical_index in range(physical):
                for column in range(array.shape[2]):
                    output[physical_index * right + offset + column] = array.at3(0, physical_index, column)
            offset += array.shape[2]
        return DenseArray((1, physical, right), tuple(output))
    if position == "last":
        if any(array.shape[2] != 1 for array in inputs):
            reject("direct_sum_payload", "last-core direct sum requires right boundary one")
        left = sum(array.shape[0] for array in inputs)
        output = [0] * (left * physical)
        offset = 0
        for array in inputs:
            for row in range(array.shape[0]):
                for physical_index in range(physical):
                    output[(offset + row) * physical + physical_index] = array.at3(row, physical_index, 0)
            offset += array.shape[0]
        return DenseArray((left, physical, 1), tuple(output))
    if position != "middle":
        reject("direct_sum_payload", f"unknown direct-sum position {position!r}")
    left = sum(array.shape[0] for array in inputs)
    right = sum(array.shape[2] for array in inputs)
    output = [0] * (left * physical * right)
    left_offset = 0
    right_offset = 0
    for array in inputs:
        for row in range(array.shape[0]):
            for physical_index in range(physical):
                for column in range(array.shape[2]):
                    destination = ((left_offset + row) * physical + physical_index) * right + right_offset + column
                    output[destination] = array.at3(row, physical_index, column)
        left_offset += array.shape[0]
        right_offset += array.shape[2]
    return DenseArray((left, physical, right), tuple(value % p for value in output))


def reshape_dense(array: DenseArray, shape_value: Any, path: str) -> DenseArray:
    shape = tuple(
        exact_int(item, f"{path}[{index}]", 0)
        for index, item in enumerate(exact_list(shape_value, path))
    )
    if not 1 <= len(shape) <= 3 or product(shape) != array.words:
        reject("transcript_view_shape", f"{path}: invalid view shape")
    return DenseArray(shape, array.values)


def resolve_transcript_object(
    objects: Mapping[str, DenseArray], value: Any, path: str
) -> DenseArray:
    object_id = exact_string(value, path)
    if object_id not in objects:
        reject("transcript_object_missing", f"{path}: unknown object {object_id!r}")
    return objects[object_id]


def physical_slice(array: DenseArray, index: int, path: str) -> DenseArray:
    if len(array.shape) != 3 or index < 0 or index >= array.shape[1]:
        reject("transcript_physical_slice", f"{path}: invalid physical slice")
    left, _, right = array.shape
    values = tuple(
        array.at3(row, index, column)
        for row in range(left)
        for column in range(right)
    )
    return DenseArray((left, right), values)


def replay_weighted_direct_sum(
    inputs: Sequence[DenseArray],
    coefficients: Sequence[int],
    position: str,
    p: int,
) -> tuple[DenseArray, dict[str, int]]:
    if len(inputs) != len(coefficients):
        reject("direct_sum_payload", "direct-sum coefficient count differs from inputs")
    operations = {key: 0 for key in OPERATION_VECTOR_KEYS}
    scaled: list[DenseArray] = []
    for array, coefficient in zip(inputs, coefficients):
        if coefficient == 0:
            reject("direct_sum_payload", "zero coefficient must be omitted before direct sum")
        if coefficient == 1:
            scaled.append(array)
            continue
        scaled.append(
            DenseArray(array.shape, tuple(coefficient * item % p for item in array.values))
        )
        if coefficient == p - 1:
            operations["subs"] += array.words
        else:
            operations["muls"] += array.words
        operations["reductions"] += array.words
    if len(scaled) == 1:
        return scaled[0], operations
    return replay_direct_sum(scaled, position, p), operations


def replay_transcript_payload(
    kind: str,
    value: Any,
    spec: CellSpec,
    path: str,
    live_objects: Mapping[str, DenseArray],
) -> tuple[dict[str, int], dict[str, DenseArray]]:
    payload = exact_object(value, path)
    require_keys(payload, {"outputs", "semantic"}, path, {"outputs", "semantic"})
    p = spec.p
    output_objects: dict[str, DenseArray] = {}
    for index, row_value in enumerate(exact_list(payload["outputs"], f"{path}.outputs")):
        row_path = f"{path}.outputs[{index}]"
        row = exact_object(row_value, row_path)
        require_keys(row, {"array", "object_id"}, row_path, {"array", "object_id"})
        object_id = exact_string(row["object_id"], f"{row_path}.object_id")
        if object_id in live_objects or object_id in output_objects:
            reject("transcript_object_redefinition", f"{row_path}: object redefined")
        output_objects[object_id] = parse_dense_array(
            row["array"], f"{row_path}.array", p
        )
    objects = dict(live_objects)
    objects.update(output_objects)
    semantic = exact_object(payload["semantic"], f"{path}.semantic")
    operations = {key: 0 for key in OPERATION_VECTOR_KEYS}

    if kind == "input_coordinate":
        required = {"mode", "output_object_ids", "variant"}
        require_keys(semantic, required, f"{path}.semantic", required)
        mode = exact_int(semantic["mode"], f"{path}.semantic.mode", 0, 4)
        output_ids = [
            exact_string(item, f"{path}.semantic.output_object_ids[{index}]")
            for index, item in enumerate(
                exact_list(semantic["output_object_ids"], f"{path}.semantic.output_object_ids")
            )
        ]
        require_equal(set(output_ids), set(output_objects), f"{path}.semantic.output_object_ids")
        variant = exact_string(semantic["variant"], f"{path}.semantic.variant")
        if variant == "coordinate_leaf":
            require_equal(len(output_ids), 5, f"{path}.semantic.output_object_ids")
            for core_mode, object_id in enumerate(output_ids):
                array = objects[object_id]
                if len(array.shape) != 3 or array.shape[0] != 1 or array.shape[2] != 1:
                    reject("coordinate_leaf_shape", f"{path}: coordinate core shape is invalid")
                if core_mode != mode and any(item != 1 for item in array.values):
                    reject("coordinate_leaf_value", f"{path}: inactive coordinate core is not one")
        elif variant != "rank_one_vector":
            reject("transcript_variant", f"{path}: unsupported input variant {variant!r}")

    elif kind == "scale":
        variant = exact_string(semantic.get("variant"), f"{path}.semantic.variant")
        if variant == "scalar_formation":
            required = {"input", "multiplier", "output", "variant"}
            require_keys(semantic, required, f"{path}.semantic", required)
            input_value = exact_int(semantic["input"], f"{path}.semantic.input", 0, p - 1)
            multiplier = exact_int(semantic["multiplier"], f"{path}.semantic.multiplier", 0, p - 1)
            output_value = exact_int(semantic["output"], f"{path}.semantic.output", 0, p - 1)
            require_equal(output_value, input_value * multiplier % p, f"{path}.semantic.output")
            operations["muls"] = 1
            operations["reductions"] = 1
        elif variant == "tensor_scale":
            required = {"operations", "variant"}
            require_keys(semantic, required, f"{path}.semantic", required)
            used_outputs: set[str] = set()
            for index, row_value in enumerate(exact_list(semantic["operations"], f"{path}.semantic.operations")):
                row_path = f"{path}.semantic.operations[{index}]"
                row = exact_object(row_value, row_path)
                keys = {
                    "input_object_id",
                    "input_view_shape",
                    "method",
                    "output_object_id",
                    "scalar",
                }
                require_keys(row, keys, row_path, keys)
                source = reshape_dense(
                    resolve_transcript_object(
                        objects,
                        row["input_object_id"],
                        f"{row_path}.input_object_id",
                    ),
                    row["input_view_shape"],
                    f"{row_path}.input_view_shape",
                )
                output_id = exact_string(row["output_object_id"], f"{row_path}.output_object_id")
                output = resolve_transcript_object(objects, output_id, f"{row_path}.output_object_id")
                scalar = exact_int(row["scalar"], f"{row_path}.scalar", 0, p - 1)
                method = exact_string(row["method"], f"{row_path}.method")
                if method == "copy":
                    require_equal(scalar, 1, f"{row_path}.scalar")
                    expected = source
                elif method == "multiply":
                    expected = DenseArray(source.shape, tuple(scalar * item % p for item in source.values))
                    operations["muls"] += source.words
                    operations["reductions"] += source.words
                else:
                    reject("transcript_scale_method", f"{row_path}: unsupported method")
                assert_array_equal(output, expected, row_path)
                used_outputs.add(output_id)
            require_equal(used_outputs, set(output_objects), f"{path}.semantic scale outputs")
        else:
            reject("transcript_variant", f"{path}: unsupported scale variant {variant!r}")

    elif kind == "direct_sum":
        keys = {"cores", "variant"}
        require_keys(semantic, keys, f"{path}.semantic", keys)
        require_equal(semantic["variant"], "direct_sum", f"{path}.semantic.variant")
        used_outputs: set[str] = set()
        for index, row_value in enumerate(exact_list(semantic["cores"], f"{path}.semantic.cores")):
            row_path = f"{path}.semantic.cores[{index}]"
            row = exact_object(row_value, row_path)
            row_keys = {
                "coefficients",
                "input_object_ids",
                "input_view_shapes",
                "output_object_id",
                "position",
            }
            require_keys(row, row_keys, row_path, row_keys)
            input_ids = exact_list(row["input_object_ids"], f"{row_path}.input_object_ids")
            input_shapes = exact_list(
                row["input_view_shapes"],
                f"{row_path}.input_view_shapes",
                len(input_ids),
            )
            inputs = [
                reshape_dense(
                    resolve_transcript_object(
                        objects,
                        item,
                        f"{row_path}.input_object_ids[{item_index}]",
                    ),
                    input_shapes[item_index],
                    f"{row_path}.input_view_shapes[{item_index}]",
                )
                for item_index, item in enumerate(input_ids)
            ]
            coefficients = [
                exact_int(item, f"{row_path}.coefficients[{item_index}]", 0, p - 1)
                for item_index, item in enumerate(exact_list(row["coefficients"], f"{row_path}.coefficients", len(inputs)))
            ]
            position = exact_string(row["position"], f"{row_path}.position")
            output_id = exact_string(row["output_object_id"], f"{row_path}.output_object_id")
            output = resolve_transcript_object(objects, output_id, f"{row_path}.output_object_id")
            expected, row_operations = replay_weighted_direct_sum(inputs, coefficients, position, p)
            assert_array_equal(output, expected, row_path)
            operations = vector_add(operations, row_operations)
            used_outputs.add(output_id)
        require_equal(used_outputs, set(output_objects), f"{path}.semantic direct-sum outputs")

    elif kind == "stage_a_contract":
        keys = {
            "operand_a_object_id", "operand_a_view_shape", "output_object_id",
            "physical_slice", "transfer_object_id", "transfer_view_shape", "variant",
        }
        require_keys(semantic, keys, f"{path}.semantic", keys)
        require_equal(semantic["variant"], "stage_a_contract", f"{path}.semantic.variant")
        transfer = reshape_dense(
            resolve_transcript_object(objects, semantic["transfer_object_id"], f"{path}.semantic.transfer_object_id"),
            semantic["transfer_view_shape"],
            f"{path}.semantic.transfer_view_shape",
        )
        operand_core = reshape_dense(
            resolve_transcript_object(objects, semantic["operand_a_object_id"], f"{path}.semantic.operand_a_object_id"),
            semantic["operand_a_view_shape"],
            f"{path}.semantic.operand_a_view_shape",
        )
        slice_index = exact_int(semantic["physical_slice"], f"{path}.semantic.physical_slice", 0, operand_core.shape[1] - 1)
        operand = physical_slice(operand_core, slice_index, f"{path}.semantic.operand_a")
        output = resolve_transcript_object(objects, semantic["output_object_id"], f"{path}.semantic.output_object_id")
        if len(transfer.shape) != 3 or transfer.shape[1] != operand.shape[0]:
            reject("stage_a_shape", f"{path}: stage-A shapes do not join")
        s, la, lb = transfer.shape
        ra = operand.shape[1]
        values: list[int] = []
        for alpha in range(s):
            for b_left in range(lb):
                for a_right in range(ra):
                    total = 0
                    for a_left in range(la):
                        total += transfer.at3(alpha, a_left, b_left) * operand.at2(a_left, a_right)
                    values.append(total % p)
        assert_array_equal(output, DenseArray((s, lb, ra), tuple(values)), path)
        operations["muls"] = s * lb * ra * la
        operations["adds"] = s * lb * ra * max(la - 1, 0)
        operations["reductions"] = s * lb * ra
        operations["comparisons"] = 4 * lb

    elif kind == "stage_b_contract":
        keys = {
            "local_matrix_object_id", "operand_b_object_id", "operand_b_view_shape",
            "output_object_id", "physical_slice", "slice_object_ids",
            "stage_a_object_id", "variant",
        }
        require_keys(semantic, keys, f"{path}.semantic", keys)
        require_equal(semantic["variant"], "stage_b_contract", f"{path}.semantic.variant")
        stage_a = resolve_transcript_object(objects, semantic["stage_a_object_id"], f"{path}.semantic.stage_a_object_id")
        operand_core = reshape_dense(
            resolve_transcript_object(objects, semantic["operand_b_object_id"], f"{path}.semantic.operand_b_object_id"),
            semantic["operand_b_view_shape"],
            f"{path}.semantic.operand_b_view_shape",
        )
        slice_index = exact_int(semantic["physical_slice"], f"{path}.semantic.physical_slice", 0, operand_core.shape[1] - 1)
        operand = physical_slice(operand_core, slice_index, f"{path}.semantic.operand_b")
        output = resolve_transcript_object(objects, semantic["output_object_id"], f"{path}.semantic.output_object_id")
        if len(stage_a.shape) != 3 or stage_a.shape[1] != operand.shape[0]:
            reject("stage_b_shape", f"{path}: stage-B shapes do not join")
        s, lb, ra = stage_a.shape
        rb = operand.shape[1]
        values: list[int] = []
        for alpha in range(s):
            for a_right in range(ra):
                for b_right in range(rb):
                    total = 0
                    for b_left in range(lb):
                        total += stage_a.at3(alpha, b_left, a_right) * operand.at2(b_left, b_right)
                    values.append(total % p)
        assert_array_equal(output, DenseArray((s, ra, rb), tuple(values)), path)
        operations["muls"] = s * ra * rb * lb
        operations["adds"] = s * ra * rb * max(lb - 1, 0)
        operations["reductions"] = s * ra * rb
        operations["comparisons"] = 4 * ra
        matrix_id = semantic["local_matrix_object_id"]
        slice_ids = exact_list(semantic["slice_object_ids"], f"{path}.semantic.slice_object_ids")
        if matrix_id is None:
            require_equal(slice_ids, [], f"{path}.semantic.slice_object_ids")
        else:
            matrix = resolve_transcript_object(objects, matrix_id, f"{path}.semantic.local_matrix_object_id")
            slices = [
                resolve_transcript_object(objects, item, f"{path}.semantic.slice_object_ids[{index}]")
                for index, item in enumerate(slice_ids)
            ]
            if not slices or any(item.shape != output.shape for item in slices):
                reject("stage_b_matrix_slices", f"{path}: local-matrix slices differ")
            assembled = [0] * (s * len(slices) * ra * rb)
            columns = ra * rb
            for physical_index, item in enumerate(slices):
                for alpha in range(s):
                    source_start = alpha * columns
                    destination_start = (alpha * len(slices) + physical_index) * columns
                    assembled[destination_start : destination_start + columns] = item.values[source_start : source_start + columns]
            assert_array_equal(matrix, DenseArray((s * len(slices), columns), tuple(assembled)), f"{path}.semantic.local_matrix")

    elif kind == "rank_factor":
        keys = {
            "left_factor_object_id", "matrix_object_id", "matrix_view_shape",
            "pivot_columns", "rank", "right_factor_object_id", "variant",
        }
        require_keys(semantic, keys, f"{path}.semantic", keys)
        require_equal(semantic["variant"], "rank_factor", f"{path}.semantic.variant")
        matrix = reshape_dense(
            resolve_transcript_object(objects, semantic["matrix_object_id"], f"{path}.semantic.matrix_object_id"),
            semantic["matrix_view_shape"],
            f"{path}.semantic.matrix_view_shape",
        )
        left = resolve_transcript_object(objects, semantic["left_factor_object_id"], f"{path}.semantic.left_factor_object_id")
        right = resolve_transcript_object(objects, semantic["right_factor_object_id"], f"{path}.semantic.right_factor_object_id")
        expected_left, expected_right, pivots, expected_operations = independent_rank_factor(matrix, p)
        rank = exact_int(semantic["rank"], f"{path}.semantic.rank", 0)
        require_equal(rank, len(pivots), f"{path}.semantic.rank")
        require_equal(semantic["pivot_columns"], pivots, f"{path}.semantic.pivot_columns")
        assert_array_equal(left, expected_left, f"{path}.semantic.left_factor")
        assert_array_equal(right, expected_right, f"{path}.semantic.right_factor")
        assert_array_equal(matrix_product(left, right, p), matrix, f"{path}.semantic.factor_identity")
        operations = expected_operations

    elif kind in ("absorb_left", "absorb_right"):
        keys = {
            "left_object_id", "left_view_shape", "output_object_id",
            "right_object_id", "right_view_shape", "variant",
        }
        require_keys(semantic, keys, f"{path}.semantic", keys)
        require_equal(semantic["variant"], kind, f"{path}.semantic.variant")
        left = reshape_dense(
            resolve_transcript_object(objects, semantic["left_object_id"], f"{path}.semantic.left_object_id"),
            semantic["left_view_shape"],
            f"{path}.semantic.left_view_shape",
        )
        right = reshape_dense(
            resolve_transcript_object(objects, semantic["right_object_id"], f"{path}.semantic.right_object_id"),
            semantic["right_view_shape"],
            f"{path}.semantic.right_view_shape",
        )
        output = resolve_transcript_object(objects, semantic["output_object_id"], f"{path}.semantic.output_object_id")
        expected = matrix_product(left, right, p)
        assert_array_equal(reshape_dense(output, [left.shape[0], right.shape[1]], f"{path}.semantic.output_view"), expected, path)
        rows, inner, columns = left.shape[0], left.shape[1], right.shape[1]
        operations["muls"] = rows * inner * columns
        operations["adds"] = rows * columns * max(inner - 1, 0)
        operations["reductions"] = rows * columns
        operations["comparisons"] = 4

    elif kind == "emit":
        variant = exact_string(semantic.get("variant"), f"{path}.semantic.variant")
        if variant in ("tensor_emit", "serialization"):
            required = (
                {"core_object_ids", "core_view_shapes", "object_digest_sha256", "variant"}
                if variant == "tensor_emit"
                else {"core_object_ids", "core_view_shapes", "record_sha256", "variant"}
            )
            require_keys(semantic, required, f"{path}.semantic", required)
            core_ids = exact_list(semantic["core_object_ids"], f"{path}.semantic.core_object_ids")
            shapes = exact_list(semantic["core_view_shapes"], f"{path}.semantic.core_view_shapes", len(core_ids))
            for index, object_id in enumerate(core_ids):
                reshape_dense(
                    resolve_transcript_object(objects, object_id, f"{path}.semantic.core_object_ids[{index}]"),
                    shapes[index],
                    f"{path}.semantic.core_view_shapes[{index}]",
                )
            digest_key = "object_digest_sha256" if variant == "tensor_emit" else "record_sha256"
            validate_hex_digest(semantic[digest_key], f"{path}.semantic.{digest_key}")
        elif variant == "tt_sample":
            required = {"core_object_ids", "core_view_shapes", "sample", "value", "variant"}
            require_keys(semantic, required, f"{path}.semantic", required)
            core_ids = exact_list(semantic["core_object_ids"], f"{path}.semantic.core_object_ids", 5)
            shapes = exact_list(semantic["core_view_shapes"], f"{path}.semantic.core_view_shapes", 5)
            sample = [
                exact_int(item, f"{path}.semantic.sample[{index}]", 0, spec.B - 1)
                for index, item in enumerate(exact_list(semantic["sample"], f"{path}.semantic.sample", 5))
            ]
            accumulator = [1]
            for mode, object_id in enumerate(core_ids):
                core = reshape_dense(
                    resolve_transcript_object(objects, object_id, f"{path}.semantic.core_object_ids[{mode}]"),
                    shapes[mode],
                    f"{path}.semantic.core_view_shapes[{mode}]",
                )
                left, _, right = core.shape
                require_equal(len(accumulator), left, f"{path}.semantic.core_join[{mode}]")
                next_accumulator: list[int] = []
                for right_bond in range(right):
                    total = 0
                    for left_bond in range(left):
                        term = accumulator[left_bond] * core.at3(left_bond, sample[mode], right_bond) % p
                        operations["muls"] += 1
                        operations["reductions"] += 1
                        if left_bond == 0:
                            total = term
                        else:
                            total = (total + term) % p
                            operations["adds"] += 1
                            operations["reductions"] += 1
                    next_accumulator.append(total)
                accumulator = next_accumulator
            require_equal(len(accumulator), 1, f"{path}.semantic.sample_result")
            require_equal(semantic["value"], accumulator[0], f"{path}.semantic.value")
        elif variant == "scalar_rcb":
            required = {"a", "b", "left", "output", "p", "right", "variant"}
            require_keys(semantic, required, f"{path}.semantic", required)
            require_equal(semantic["p"], spec.p, f"{path}.semantic.p")
            require_equal(semantic["a"], spec.a, f"{path}.semantic.a")
            require_equal(semantic["b"], spec.b, f"{path}.semantic.b")
            left = parse_projective(semantic["left"], f"{path}.semantic.left", p)
            right = parse_projective(semantic["right"], f"{path}.semantic.right", p)
            output = parse_projective(semantic["output"], f"{path}.semantic.output", p)
            require_equal(output, rcb_add_independent(left, right, p, spec.a, spec.b), f"{path}.semantic.output")
            operations["adds"] = 17
            operations["subs"] = 6
            operations["muls"] = 18
            operations["reductions"] = 41
        else:
            reject("transcript_variant", f"{path}: unsupported emit variant {variant!r}")

    elif kind == "free":
        require_equal(semantic, {}, f"{path}.semantic")
        require_equal(output_objects, {}, f"{path}.outputs")
    else:
        reject("transcript_kind", f"unsupported transcript kind {kind!r}", path)

    operations["comparisons"] += 2 * sum(
        array.words for array in output_objects.values()
    )
    return operations, output_objects


def parse_ir_output(value: Any, path: str) -> dict[str, Any]:
    row = exact_object(value, path)
    require_keys(row, {"object_id", "shape", "words", "digest_sha256"}, path, {"object_id", "shape", "words", "digest_sha256", "object_kind"})
    object_id = exact_string(row["object_id"], f"{path}.object_id")
    shape = [
        exact_int(item, f"{path}.shape[{index}]", 0)
        for index, item in enumerate(exact_list(row["shape"], f"{path}.shape"))
    ]
    if not 1 <= len(shape) <= 3:
        reject("ir_array_dimensions", f"{path}: IR arrays must have one to three dimensions")
    words = exact_int(row["words"], f"{path}.words", 0, MAX_LOCAL_MATRIX_WORDS)
    require_equal(words, product(shape), f"{path}.words")
    digest = validate_hex_digest(row["digest_sha256"], f"{path}.digest_sha256")
    return {"digest_sha256": digest, "object_id": object_id, "shape": shape, "words": words}


def audit_ir_and_allocations(
    ir_value: Any,
    allocation_value: Any,
    transcript_value: Any,
    operation_ledger_value: Any,
    specs: Mapping[str, CellSpec],
    producer_accounting: Mapping[str, Any],
) -> dict[str, Any]:
    events = exact_list(ir_value, "raw_result.ir_events")
    if not events:
        reject("ir_empty", "raw_result.ir_events must not be empty")
    transcript_rows = exact_list(transcript_value, "raw_result.gate_transcript")
    transcript_map: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(transcript_rows):
        path = f"raw_result.gate_transcript[{index}]"
        row = exact_object(value, path)
        require_keys(row, {"node_id", "payload", "payload_digest_sha256"}, path, {"node_id", "payload", "payload_digest_sha256"})
        node_id = exact_string(row["node_id"], f"{path}.node_id")
        if node_id in transcript_map:
            reject("duplicate_transcript_node", f"duplicate transcript node {node_id!r}")
        payload_digest = sha256_value(row["payload"])
        require_equal(
            validate_hex_digest(row["payload_digest_sha256"], f"{path}.payload_digest_sha256"),
            payload_digest,
            f"{path}.payload_digest_sha256",
            "transcript_payload_digest_mismatch",
        )
        transcript_map[node_id] = row

    running_operations = {key: 0 for key in OPERATION_VECTOR_KEYS}
    running_traffic = {
        key: {"reads": 0, "writes": 0} for key in SOURCE_TRAFFIC_BUCKETS
    }
    live: dict[str, dict[str, Any]] = {}
    all_objects: set[str] = set()
    node_ids: set[str] = set()
    current_live_words = 0
    peak_live_words = 0
    expected_allocation_rows: list[dict[str, Any]] = []
    required_transcript_nodes: list[str] = []
    replayed_transcript_nodes = 0
    replay_objects: dict[str, DenseArray] = {}

    required_event_keys = {
        "sequence",
        "node_id",
        "kind",
        "cell_id",
        "gate",
        "mode",
        "physical_slice",
        "input_object_ids",
        "outputs",
        "freed_object_ids",
        "operation_vector",
        "traffic",
        "cumulative_operation_vector",
        "cumulative_traffic_words",
        "predicted_words",
        "observed_words",
        "live_words_before",
        "live_words_after",
        "peak_live_words",
        "payload_digest_sha256",
    }
    for sequence, value in enumerate(events):
        path = f"raw_result.ir_events[{sequence}]"
        event = exact_object(value, path)
        require_keys(event, required_event_keys, path, required_event_keys)
        require_equal(event["sequence"], sequence, f"{path}.sequence")
        node_id = exact_string(event["node_id"], f"{path}.node_id")
        if node_id in node_ids:
            reject("duplicate_ir_node", f"duplicate IR node {node_id!r}")
        node_ids.add(node_id)
        kind = exact_string(event["kind"], f"{path}.kind")
        if kind not in ACCEPTED_IR_KINDS:
            reject("ir_kind", f"{path}: unaccepted IR kind {kind!r}")
        cell_id = exact_string(event["cell_id"], f"{path}.cell_id")
        if cell_id not in specs and not cell_id.startswith("CTL-") and cell_id != "GLOBAL":
            reject("ir_cell", f"{path}: unknown IR cell {cell_id!r}")
        exact_string(event["gate"], f"{path}.gate")
        mode = event["mode"]
        if mode is not None:
            exact_int(mode, f"{path}.mode", 0, 4)
        physical_slice = event["physical_slice"]
        if physical_slice is not None:
            maximum = specs[cell_id].B - 1 if cell_id in specs else 16
            exact_int(physical_slice, f"{path}.physical_slice", 0, maximum)
        if kind in ("stage_a_contract", "stage_b_contract"):
            if mode is None or physical_slice is None:
                reject("ir_physical_scope", f"{path}: contraction requires one mode and slice")
        inputs = [
            exact_string(item, f"{path}.input_object_ids[{index}]")
            for index, item in enumerate(exact_list(event["input_object_ids"], f"{path}.input_object_ids"))
        ]
        for object_id in inputs:
            if object_id not in live:
                reject("ir_input_not_live", f"{path}: input object {object_id!r} is not live")
        outputs = [
            parse_ir_output(item, f"{path}.outputs[{index}]")
            for index, item in enumerate(exact_list(event["outputs"], f"{path}.outputs"))
        ]
        output_ids = [row["object_id"] for row in outputs]
        if len(set(output_ids)) != len(output_ids):
            reject("ir_duplicate_output", f"{path}: duplicate output object")
        for output in outputs:
            if output["object_id"] in all_objects:
                reject("ir_object_redefinition", f"{path}: object {output['object_id']!r} redefined")
        freed = [
            exact_string(item, f"{path}.freed_object_ids[{index}]")
            for index, item in enumerate(exact_list(event["freed_object_ids"], f"{path}.freed_object_ids"))
        ]
        if len(set(freed)) != len(freed):
            reject("ir_duplicate_free", f"{path}: duplicate free")
        for object_id in freed:
            if object_id not in live:
                reject("ir_free_not_live", f"{path}: freed object {object_id!r} is not live")

        event_operations = exact_operation_vector(event["operation_vector"], f"{path}.operation_vector")
        running_operations = vector_add(running_operations, event_operations)
        require_equal(
            exact_operation_vector(event["cumulative_operation_vector"], f"{path}.cumulative_operation_vector"),
            running_operations,
            f"{path}.cumulative_operation_vector",
            "ir_cumulative_operation_mismatch",
        )
        traffic = exact_traffic_vector(
            event["traffic"], f"{path}.traffic", SOURCE_TRAFFIC_BUCKETS
        )
        for bucket in SOURCE_TRAFFIC_BUCKETS:
            running_traffic[bucket]["reads"] += traffic[bucket]["reads"]
            running_traffic[bucket]["writes"] += traffic[bucket]["writes"]
        require_equal(
            event["cumulative_traffic_words"],
            traffic_total(running_traffic),
            f"{path}.cumulative_traffic_words",
            "ir_cumulative_traffic_mismatch",
        )

        output_words = sum(row["words"] for row in outputs)
        predicted_words = exact_int(event["predicted_words"], f"{path}.predicted_words", 0)
        observed_words = exact_int(event["observed_words"], f"{path}.observed_words", 0)
        require_equal(predicted_words, output_words, f"{path}.predicted_words")
        require_equal(observed_words, output_words, f"{path}.observed_words")
        require_equal(event["live_words_before"], current_live_words, f"{path}.live_words_before")
        intermediate_live = current_live_words + output_words
        peak_live_words = max(peak_live_words, intermediate_live)
        for output in outputs:
            live[output["object_id"]] = output
            all_objects.add(output["object_id"])
            expected_allocation_rows.append(
                {
                    "digest_sha256": output["digest_sha256"],
                    "event": "allocate",
                    "node_id": node_id,
                    "object_id": output["object_id"],
                    "shape": output["shape"],
                    "words": output["words"],
                }
            )
        for object_id in freed:
            prior = live.pop(object_id)
            intermediate_live -= prior["words"]
            expected_allocation_rows.append(
                {
                    "digest_sha256": prior["digest_sha256"],
                    "event": "free",
                    "node_id": node_id,
                    "object_id": object_id,
                    "shape": prior["shape"],
                    "words": prior["words"],
                }
            )
        current_live_words = intermediate_live
        require_equal(event["live_words_after"], current_live_words, f"{path}.live_words_after")
        require_equal(event["peak_live_words"], peak_live_words, f"{path}.peak_live_words")
        if peak_live_words > MAX_LIVE_WORDS:
            reject("ir_live_word_cap", f"{path}: peak live words exceeds {MAX_LIVE_WORDS}")

        payload_digest = event["payload_digest_sha256"]
        if cell_id == "C08:random_unique":
            required_transcript_nodes.append(node_id)
            if node_id not in transcript_map:
                reject("missing_c08_transcript", f"{path}: missing C08 payload")
        if node_id in transcript_map:
            transcript = transcript_map[node_id]
            observed_payload_digest = validate_hex_digest(
                transcript["payload_digest_sha256"],
                f"raw_result.gate_transcript[{node_id}].payload_digest_sha256",
            )
            require_equal(payload_digest, observed_payload_digest, f"{path}.payload_digest_sha256")
            replay_operations, transcript_outputs = replay_transcript_payload(
                kind,
                transcript["payload"],
                specs[cell_id],
                f"raw_result.gate_transcript[{node_id}].payload",
                replay_objects,
            )
            require_equal(
                set(transcript_outputs),
                set(output_ids),
                f"{path}.transcript output object ids",
                "transcript_output_set_mismatch",
            )
            output_map = {row["object_id"]: row for row in outputs}
            for object_id, array in transcript_outputs.items():
                output_row = output_map[object_id]
                require_equal(
                    output_row["shape"],
                    list(array.shape),
                    f"{path}.outputs[{object_id}].shape",
                    "transcript_output_shape_mismatch",
                )
                require_equal(
                    output_row["digest_sha256"],
                    sha256_value(array.record()),
                    f"{path}.outputs[{object_id}].digest_sha256",
                    "transcript_output_digest_mismatch",
                )
                replay_objects[object_id] = array
            for key in ("adds", "subs", "muls", "squares", "inversions", "reductions", "comparisons"):
                require_equal(
                    event_operations[key],
                    replay_operations[key],
                    f"{path}.operation_vector.{key}",
                    "transcript_operation_count_mismatch",
                )
            replayed_transcript_nodes += 1
        elif payload_digest is not None:
            reject("orphan_payload_digest", f"{path}: payload digest has no transcript row")
        for object_id in freed:
            replay_objects.pop(object_id, None)

    require_equal(set(transcript_map), set(required_transcript_nodes), "raw_result.gate_transcript node set")
    if live:
        reject("ir_live_objects_at_end", f"{len(live)} IR objects remain live after final event")
    if replay_objects:
        reject(
            "transcript_live_objects_at_end",
            f"{len(replay_objects)} replay objects remain live after final event",
        )
    require_equal(running_operations, producer_accounting["operation_vector"], "IR/accounting operation reconciliation")
    require_equal(running_traffic, producer_accounting["traffic_buckets"], "IR/accounting traffic reconciliation")
    require_equal(peak_live_words, producer_accounting["peak_live_field_words"], "IR/accounting peak-live reconciliation")

    allocation_rows = exact_list(allocation_value, "raw_result.allocation_events", len(expected_allocation_rows))
    for sequence, (raw_row_value, expected) in enumerate(zip(allocation_rows, expected_allocation_rows)):
        path = f"raw_result.allocation_events[{sequence}]"
        row = exact_object(raw_row_value, path)
        require_keys(
            row,
            {"sequence", "event", "node_id", "object_id", "shape", "words", "digest_sha256"},
            path,
            {"sequence", "event", "node_id", "object_id", "shape", "words", "digest_sha256"},
        )
        require_equal(row["sequence"], sequence, f"{path}.sequence")
        for key, expected_value in expected.items():
            require_equal(row.get(key), expected_value, f"{path}.{key}", "allocation_trace_mismatch")

    operation_ledger = exact_object(operation_ledger_value, "raw_result.operation_ledger")
    require_keys(
        operation_ledger,
        {"event_count", "ir_events_sha256", "operation_vector", "traffic_buckets"},
        "raw_result.operation_ledger",
        {"event_count", "ir_events_sha256", "operation_vector", "traffic_buckets"},
    )
    require_equal(operation_ledger["event_count"], len(events), "raw_result.operation_ledger.event_count")
    require_equal(
        validate_hex_digest(operation_ledger["ir_events_sha256"], "raw_result.operation_ledger.ir_events_sha256"),
        sha256_value(events),
        "raw_result.operation_ledger.ir_events_sha256",
    )
    require_equal(
        exact_operation_vector(operation_ledger["operation_vector"], "raw_result.operation_ledger.operation_vector"),
        running_operations,
        "raw_result.operation_ledger.operation_vector",
    )
    ledger_traffic = exact_traffic_vector(
        operation_ledger["traffic_buckets"],
        "raw_result.operation_ledger.traffic_buckets",
        SOURCE_TRAFFIC_BUCKETS,
    )
    require_equal(ledger_traffic, running_traffic, "raw_result.operation_ledger.traffic_buckets")
    return {
        "allocation_event_count": len(allocation_rows),
        "ir_event_count": len(events),
        "ir_events_sha256": sha256_value(events),
        "peak_live_field_words": peak_live_words,
        "replayed_c08_transcript_nodes": replayed_transcript_nodes,
        "valid": True,
    }


def audit_gate_rank_ledger(value: Any, cell_report: Mapping[str, Any]) -> dict[str, Any]:
    ledger = exact_object(value, "raw_result.gate_rank_ledger")
    require_keys(
        ledger,
        {"tensor_record_count", "records", "records_sha256"},
        "raw_result.gate_rank_ledger",
        {"tensor_record_count", "records", "records_sha256"},
    )
    expected_records: list[dict[str, Any]] = []
    for cell in cell_report["cells"]:
        for tensor in cell["tensors"]:
            expected_records.append(
                {
                    "cell_id": cell["cell_id"],
                    "core_digest_sha256": tensor["core_digest_sha256"],
                    "exact_ranks": tensor["exact_ranks"],
                    "name": tensor["name"],
                    "word_count": tensor["word_count"],
                }
            )
    require_equal(len(expected_records), 63, "independent gate-rank record count")
    require_equal(ledger["tensor_record_count"], 63, "raw_result.gate_rank_ledger.tensor_record_count")
    require_equal(ledger["records"], expected_records, "raw_result.gate_rank_ledger.records", "gate_rank_ledger_mismatch")
    require_equal(
        validate_hex_digest(ledger["records_sha256"], "raw_result.gate_rank_ledger.records_sha256"),
        sha256_value(expected_records),
        "raw_result.gate_rank_ledger.records_sha256",
    )
    return {"records_sha256": sha256_value(expected_records), "tensor_record_count": 63, "valid": True}


def rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def schema_description() -> dict[str, Any]:
    return {
        "strict_preflight_development_cli": [
            "--manifest PATH",
            "--execution-matrix PATH",
            "--raw-result PATH",
            "--expected-static-closure-audit-sha256 DIGEST",
            "--strict-preflight-development",
        ],
        "artifact_freeze_available": False,
        "canonical_json": {
            "allow_nan": False,
            "ascii_escaping": True,
            "duplicate_keys": "rejected",
            "floating_values": "rejected",
            "object_keys": "sorted",
            "separators": [",", ":"],
            "trailing_bytes": "exactly one newline",
            "utf8": True,
        },
        "development_cli": [
            "--describe-schema",
            "--self-test",
            "--semantic-only-development",
            "--implementation-audit-development",
            "--strict-preflight-development",
        ],
        "source_phase_data_read_allowlist": [
            "--manifest PATH",
            "--execution-matrix PATH",
            "--raw-result PATH",
        ],
        "strict_preflight_scalar_binding":
            "--expected-static-closure-audit-sha256 DIGEST",
        "control_manifest_cli_accepted": False,
        "output": {
            "failure": {
                "error": {"code": "string", "message": "string", "path": "string"},
                "partition": "source_verifier",
                "protocol": PROTOCOL,
                "schema": OUTPUT_SCHEMA,
                "valid": False,
            },
            "success_artifacts": None,
            "success_keys": [
                "artifact_freeze_authorized",
                "audits",
                "boundary",
                "candidate_artifact_digests",
                "partition",
                "protocol",
                "raw_result_sha256",
                "schema",
                "valid",
                "verifier_accounting",
            ],
        },
        "producer_raw_result": {
            "accounting": {
                "operation_vector_keys": list(OPERATION_VECTOR_KEYS),
                "traffic_bucket_keys": list(SOURCE_TRAFFIC_BUCKETS),
                "traffic_entry": {
                    "reads": "nonnegative integer",
                    "writes": "nonnegative integer",
                },
                "required_keys": [
                    "operation_vector",
                    "traffic_buckets",
                    "logical_traffic_words",
                    "normalization_calls",
                    "streamed_prefix_factorizations",
                    "two_sweep_factorizations",
                    "total_rank_factorizations",
                    "maximum_local_matrix_words",
                    "maximum_tt_object_words",
                    "peak_live_field_words",
                    "peak_rss_bytes",
                    "wall_clock_ns",
                    "cpu_ns",
                    "counters_reset",
                ],
            },
            "allocation_event_required_keys": [
                "digest_sha256",
                "event",
                "node_id",
                "object_id",
                "sequence",
                "shape",
                "words",
            ],
            "cell_order": list(ALL_CELL_ORDER),
            "cell_required_keys": [
                "B",
                "cell_id",
                "curve_id",
                "diagnostic_samples",
                "kind",
                "mode_scalars",
                "p",
                "registry",
                "retained_advice",
                "summary",
                "tensors",
            ],
            "cell_summary_exact_values": {
                "diagnostic_sample_count": 5,
                "emitted_tensor_count": 9,
                "rcb_calls": 4,
                "semantic_mismatches": 0,
            },
            "claim_boundary_exact": {
                "breakthrough_claim": False,
                "ecdlp_improvement_claim": False,
                "index_calculus_claim": False,
                "locator_claim": False,
                "target_specialization_claim": False,
                "toy_restricted_model_bound": True,
            },
            "control_certificate_row_required_keys": [
                "certificate_sha256",
                "id",
                "observed",
                "status",
            ],
            "control_ids_in_order": list(CONTROL_EXPECTATIONS),
            "diagnostic_sample_row_required_keys": ["indices", "values"],
            "gate_rank_ledger_required_keys": [
                "tensor_record_count",
                "records",
                "records_sha256",
            ],
            "gate_transcript_row_required_keys": [
                "node_id",
                "payload",
                "payload_digest_sha256",
            ],
            "header_exact_values": {
                "interpretation": "TARGET_BLIND_TOY_SOURCE_COMPILATION",
                "partition": "source_generator",
                "protocol": PROTOCOL,
                "schema": RAW_SCHEMA,
                "valid": True,
            },
            "input_basenames": [
                "source-instance-manifest-v1.json",
                "source-execution-matrix-v2.json",
            ],
            "ir_event_required_keys": [
                "cell_id",
                "cumulative_operation_vector",
                "cumulative_traffic_words",
                "freed_object_ids",
                "gate",
                "input_object_ids",
                "kind",
                "live_words_after",
                "live_words_before",
                "mode",
                "node_id",
                "observed_words",
                "operation_vector",
                "outputs",
                "payload_digest_sha256",
                "peak_live_words",
                "physical_slice",
                "predicted_words",
                "sequence",
                "traffic",
            ],
            "ir_sequence_origin": 0,
            "operation_ledger_required_keys": [
                "event_count",
                "ir_events_sha256",
                "operation_vector",
                "traffic_buckets",
            ],
            "provenance_required_keys_development_base": [
                "source_manifest_sha256",
                "source_execution_matrix_sha256",
                "rcb_gate_text_sha256",
                "local_source_files",
                "local_source_closure_sha256",
                "data_reads",
            ],
            "provenance_strict_preflight_additional_required_keys": [
                "runtime_receipt_sha256",
            ],
            "schema": RAW_SCHEMA,
            "tensor_core": {
                "digest_sha256": "sha256(canonical({shape,values})) optional",
                "shape": ["left_bond", "B", "right_bond"],
                "values": "flat C-order canonical residues",
            },
            "native_tensor_wrapper": {
                "required": ["name", "tensor"],
                "tensor_encoding": "exact-fp-tt-v1",
                "producer_value_digest_semantics": "representation digest only",
                "verifier_value_digest_semantics": "exhaustive B^5 field-value digest",
            },
            "tensor_required_keys": [
                "B",
                "core_digest_sha256",
                "cores",
                "name",
                "p",
                "ranks",
                "tag",
            ],
            "tensor_order": list(TENSOR_NAMES),
            "retained_tensor_order": list(RETAINED_NAMES),
            "top_level_keys": sorted(RAW_TOP_LEVEL_KEYS),
            "transcript_payloads": {
                "absorb_left|absorb_right": ["left", "right", "output"],
                "direct_sum": ["inputs", "position", "output"],
                "emit": ["object_digest_sha256"],
                "free": [],
                "input_coordinate": ["output"],
                "rank_factor": ["matrix", "left_factor", "right_factor", "pivot_columns", "rank"],
                "scale": ["input", "scalar", "output"],
                "stage_a_contract": ["transfer", "operand_a_slice", "output"],
                "stage_b_contract": ["stage_a", "operand_b_slice", "output"],
            },
        },
        "protocol": PROTOCOL,
        "schema": "tt-source-verifier-schema-description-v1",
        "valid": True,
    }


def run_self_test() -> dict[str, Any]:
    p = 239
    vectors = (
        (1, 2, 4),
        (3, 5, 7),
        (11, 13, 17),
        (19, 23, 29),
        (31, 37, 41),
    )
    tensor = Tensor(
        name="self_test_rank_one",
        p=p,
        B=3,
        tag="tt",
        ranks=(1, 1, 1, 1),
        cores=tuple(Core(1, 3, 1, tuple(vector)) for vector in vectors),
    )
    values = [0] * (3**5)
    for indices in iter_five_tuples_independent(3):
        expected = math.prod(vectors[mode][indices[mode]] for mode in range(5)) % p
        observed = evaluate_tensor(tensor, indices)
        require_equal(observed, expected, f"self_test.tensor[{indices}]")
        values[linear_index(indices, 3)] = observed
    ranks = [unfolding_rank(values, 3, cut, p) for cut in range(1, 5)]
    require_equal(ranks, [1, 1, 1, 1], "self_test.rank_one_ranks")

    points: tuple[Projective, ...] = (
        (146, 120, 1),
        (231, 218, 1),
        (97, 122, 1),
        (146, 120, 1),
        (231, 218, 1),
    )
    rcb_sum = sum_five_rcb_independent(points, p, 40, 78)
    affine_sum: Point = None
    for point in points:
        affine_sum = affine_add(affine_sum, projective_to_affine(point, p), p, 40)
    require_equal(projective_to_affine(rcb_sum, p), affine_sum, "self_test.rcb_affine_sum")
    registry = points[:3]
    for indices in iter_five_tuples_independent(3):
        selected = [registry[index] for index in indices]
        rcb_value = projective_to_affine(
            sum_five_rcb_independent(selected, p, 40, 78), p
        )
        affine_value: Point = None
        for point in selected:
            affine_value = affine_add(
                affine_value, projective_to_affine(point, p), p, 40
            )
        require_equal(
            rcb_value,
            affine_value,
            f"self_test.rcb_exhaustive[{indices}]",
        )

    matrix = DenseArray((3, 4), (1, 2, 3, 4, 2, 4, 6, 8, 1, 0, 1, 0))
    left, right, pivots, _ = independent_rank_factor(matrix, p)
    require_equal(pivots, [0, 1], "self_test.rank_factor_pivots")
    assert_array_equal(matrix_product(left, right, p), matrix, "self_test.rank_factor_identity")
    for rows, columns in ((1, 1), (3, 5), (5, 3), (4, 4)):
        deterministic = DenseArray(
            (rows, columns),
            tuple(
                (17 * row + 29 * column + 7 * row * column + 3) % p
                for row in range(rows)
                for column in range(columns)
            ),
        )
        factor_left, factor_right, factor_pivots, _ = independent_rank_factor(
            deterministic, p
        )
        assert_array_equal(
            matrix_product(factor_left, factor_right, p),
            deterministic,
            f"self_test.rank_factor_grid[{rows},{columns}]",
        )
        expected_rank = exact_rank_rows(
            [
                deterministic.values[row * columns : (row + 1) * columns]
                for row in range(rows)
            ],
            p,
        )
        require_equal(
            len(factor_pivots),
            expected_rank,
            f"self_test.rank_factor_grid_rank[{rows},{columns}]",
        )
    zero_matrix = DenseArray((3, 4), (0,) * 12)
    zero_left, zero_right, zero_pivots, _ = independent_rank_factor(zero_matrix, p)
    require_equal(zero_pivots, [], "self_test.zero_rank_factor_pivots")
    assert_array_equal(
        matrix_product(zero_left, zero_right, p),
        zero_matrix,
        "self_test.zero_rank_factor_identity",
    )
    canonical = canonical_bytes({"b": 2, "a": 1})
    require_equal(canonical, b'{"a":1,"b":2}\n', "self_test.canonical_json")
    require_equal(parse_json_bytes(canonical, "self_test"), {"a": 1, "b": 2}, "self_test.json_parse")

    native_cores: list[dict[str, Any]] = []
    for vector in vectors:
        digest = hashlib.sha256()
        for item in vector:
            digest.update(item.to_bytes(1, "big"))
        native_cores.append(
            {
                "shape": [1, 3, 1],
                "value_digest_sha256": digest.hexdigest(),
                "values": list(vector),
            }
        )
    native_record = {
        "canonical_bytes_per_field_word": 1,
        "cores": native_cores,
        "encoding": "exact-fp-tt-v1",
        "field_modulus": p,
        "field_words": 15,
        "physical_mode_count": 5,
        "physical_mode_size": 3,
        "ranks": [1, 1, 1, 1],
        "tag": "nonzero",
        "value_digest_sha256": "0" * 64,
    }
    native_record["record_sha256"] = sha256_bytes(compact_json_bytes(native_record))
    normalized = normalize_native_tensor_record(
        {"name": "self_test_rank_one", "tensor": native_record},
        "self_test.native_tensor",
        "self_test_rank_one",
        p,
        3,
    )
    parsed_native = parse_tensor(
        normalized, "self_test.native_tensor", "self_test_rank_one", p, 3
    )
    require_equal(parsed_native, tensor, "self_test.native_tensor_adapter")
    return {
        "checks": [
            "canonical_json",
            "exact_rank_factor",
            "exact_rank_factor_grid_and_zero",
            "literal_rcb_exhaustive_c08_b3",
            "literal_rcb_vs_affine",
            "native_producer_tensor_adapter",
            "rank_one_tt_exhaustive",
            "unfolding_ranks",
        ],
        "partition": "source_verifier_development_self_test",
        "protocol": PROTOCOL,
        "rank_one_value_digest_sha256": value_digest(values, p),
        "schema": OUTPUT_SCHEMA,
        "valid": True,
    }


class CanonicalArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        reject("argument_error", message)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = CanonicalArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--execution-matrix", type=Path)
    parser.add_argument("--raw-result", type=Path)
    parser.add_argument("--expected-static-closure-audit-sha256")
    parser.add_argument("--describe-schema", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--semantic-only-development", action="store_true")
    parser.add_argument("--implementation-audit-development", action="store_true")
    parser.add_argument("--strict-preflight-development", action="store_true")
    parser.add_argument("--help", action="store_true")
    args = parser.parse_args(argv)
    special = sum(bool(item) for item in (args.describe_schema, args.self_test, args.help))
    if special > 1:
        reject("argument_error", "choose only one of --describe-schema, --self-test, or --help")
    if special:
        if any(
            (
                args.manifest,
                args.execution_matrix,
                args.raw_result,
                args.expected_static_closure_audit_sha256,
            )
        ):
            reject("argument_error", "schema/help/self-test modes do not accept experiment inputs")
        return args
    missing = [
        flag
        for flag, value in (
            ("--manifest", args.manifest),
            ("--execution-matrix", args.execution_matrix),
            ("--raw-result", args.raw_result),
        )
        if value is None
    ]
    if missing:
        reject("argument_error", f"missing required arguments: {', '.join(missing)}")
    development_modes = sum(
        bool(item)
        for item in (
            args.semantic_only_development,
            args.implementation_audit_development,
            args.strict_preflight_development,
        )
    )
    if development_modes > 1:
        reject(
            "argument_error",
            "choose only one development verification mode",
        )
    if development_modes == 0:
        reject(
            "execution_not_authorized",
            "artifact freeze is unavailable because the experiment has no execution_plan",
        )
    if (
        args.strict_preflight_development
        and args.expected_static_closure_audit_sha256 is None
    ):
        reject(
            "argument_error",
            "--strict-preflight-development requires "
            "--expected-static-closure-audit-sha256",
        )
    if args.expected_static_closure_audit_sha256 is not None:
        validate_hex_digest(
            args.expected_static_closure_audit_sha256,
            "--expected-static-closure-audit-sha256",
        )
    if (
        not args.strict_preflight_development
        and args.expected_static_closure_audit_sha256 is not None
    ):
        reject(
            "argument_error",
            "--expected-static-closure-audit-sha256 is accepted only by strict "
            "development preflight",
        )
    return args


def verify_semantic_development(args: argparse.Namespace) -> dict[str, Any]:
    """Replay source semantics/ranks without authorizing artifact freeze or a run."""

    global _ACTIVE_OPERATION_VECTOR
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    meter = Meter()
    _ACTIVE_OPERATION_VECTOR = meter.operations
    manifest_record, manifest_bytes = read_json(args.manifest, "source manifest")
    matrix_record, matrix_bytes = read_json(args.execution_matrix, "source execution matrix")
    raw, raw_bytes = read_json(args.raw_result, "producer raw result", MAX_RAW_RESULT_BYTES)
    if raw_bytes != canonical_bytes(raw):
        reject(
            "raw_result_not_canonical",
            "producer raw result is not exact canonical JSON with one trailing newline",
            str(args.raw_result),
        )
    raw_digest = sha256_bytes(raw_bytes)
    specs, manifest_audit = audit_source_manifest(manifest_record, manifest_bytes, meter)
    matrix_audit = audit_source_matrix(
        matrix_record,
        matrix_bytes,
        manifest_audit["source_manifest_sha256"],
        meter,
    )
    source_control_profile_audit = audit_source_control_profile()
    raw_header_audit = audit_raw_header(
        raw,
        manifest_audit["source_manifest_sha256"],
        matrix_audit["source_execution_matrix_sha256"],
    )
    backend_audit = audit_backend_attestation(raw["backend_attestation"])
    advice, controls, semantic_audit = verify_source_cells(raw["cells"], specs, meter)
    control_audit = audit_control_certificates(raw["controls"])
    gate_rank_audit = audit_gate_rank_ledger(raw["gate_rank_ledger"], semantic_audit)
    meter.check_caps()
    wall_ns = time.perf_counter_ns() - wall_start
    cpu_ns = time.process_time_ns() - cpu_start
    observed_rss = rss_bytes()
    result = {
        "artifact_freeze_authorized": False,
        "audits": {
            "backend": backend_audit,
            "source_control_profile": source_control_profile_audit,
            "controls": control_audit,
            "gate_rank_ledger": gate_rank_audit,
            "manifest": manifest_audit,
            "matrix": matrix_audit,
            "provenance": raw_header_audit,
            "semantics_and_ranks": semantic_audit,
        },
        "boundary": (
            "Development-only exhaustive source semantic and exact-rank replay. "
            "Capability, allocation, C08 transcript, accounting, phase-firewall, "
            "and run-authorization gates were not evaluated."
        ),
        "partition": "source_verifier_development",
        "protocol": PROTOCOL,
        "raw_result_sha256": raw_digest,
        "schema": "tt-source-semantic-development-verification-v1",
        "source_artifact_digests": {
            "control_certificates_sha256": sha256_value(controls),
            "retained_advice_sha256": sha256_value(advice),
        },
        "valid": True,
        "verifier_accounting": {
            "cpu_ns": cpu_ns,
            "logical_traffic_words": traffic_total(meter.traffic),
            "operation_vector": meter.operations,
            "peak_live_field_words": meter.peak_live_field_words,
            "peak_rss_bytes": observed_rss,
            "traffic_buckets": meter.traffic,
            "wall_clock_ns": wall_ns,
        },
    }
    _ACTIVE_OPERATION_VECTOR = None
    return result


def verify(args: argparse.Namespace) -> dict[str, Any]:
    global _ACTIVE_OPERATION_VECTOR
    wall_start = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    meter = Meter()
    _ACTIVE_OPERATION_VECTOR = meter.operations
    manifest_record, manifest_bytes = read_json(args.manifest, "source manifest")
    matrix_record, matrix_bytes = read_json(args.execution_matrix, "source execution matrix")
    raw, raw_bytes = read_json(args.raw_result, "producer raw result", MAX_RAW_RESULT_BYTES)
    if raw_bytes != canonical_bytes(raw):
        reject(
            "raw_result_not_canonical",
            "producer raw result is not exact canonical JSON with one trailing newline",
            str(args.raw_result),
        )
    raw_digest = sha256_bytes(raw_bytes)

    specs, manifest_audit = audit_source_manifest(manifest_record, manifest_bytes, meter)
    matrix_audit = audit_source_matrix(
        matrix_record, matrix_bytes, manifest_audit["source_manifest_sha256"], meter
    )
    source_control_profile_audit = audit_source_control_profile()
    raw_header_audit = audit_raw_header(
        raw,
        manifest_audit["source_manifest_sha256"],
        matrix_audit["source_execution_matrix_sha256"],
    )
    backend_audit = audit_backend_attestation(raw["backend_attestation"])
    development_audit = bool(args.implementation_audit_development)
    strict_preflight = bool(args.strict_preflight_development)
    source_phase_binding_audit: dict[str, Any] | None = None
    if strict_preflight:
        expected_static_digest = validate_hex_digest(
            args.expected_static_closure_audit_sha256,
            "--expected-static-closure-audit-sha256",
        )
        capability_audit = audit_capability(
            raw["capability_audit"],
            expected_static_closure_audit_sha256=expected_static_digest,
            raw_provenance_value=raw["provenance"],
            manifest_bytes=manifest_bytes,
            matrix_bytes=matrix_bytes,
        )
        source_phase_binding_audit = {
            "expected_static_closure_audit_sha256": expected_static_digest,
            "valid": True,
        }
    elif development_audit:
        capability_audit = audit_capability_development(raw["capability_audit"])
    else:
        reject("execution_not_authorized", "artifact freeze mode is unavailable")
    producer_accounting = audit_accounting(raw["accounting"])
    advice, controls, semantic_audit = verify_source_cells(raw["cells"], specs, meter)
    control_audit = audit_control_certificates(raw["controls"])
    gate_rank_audit = audit_gate_rank_ledger(raw["gate_rank_ledger"], semantic_audit)
    ir_audit = audit_ir_and_allocations(
        raw["ir_events"],
        raw["allocation_events"],
        raw["gate_transcript"],
        raw["operation_ledger"],
        specs,
        producer_accounting,
    )

    advice_bytes = canonical_bytes(advice)
    controls_bytes = canonical_bytes(controls)
    advice_words = sum(
        tensor["word_count"] for cell in advice["cells"] for tensor in cell["tensors"]
    )
    control_words = sum(
        row["tensor"]["word_count"] for row in controls["xy_certificates"]
    ) + sum(
        tensor["word_count"]
        for tensor in controls["modewise_rescaled_source_cell"]["tensors"]
    )
    meter.add_traffic(
        "advice_serialize",
        reads=advice_words + control_words,
        copied=True,
    )
    advice_digest = sha256_bytes(advice_bytes)
    controls_digest = sha256_bytes(controls_bytes)
    receipt = {
        "control_certificate_sha256": controls_digest,
        "primary_source_cell_count": 6,
        "raw_result_sha256": raw_digest,
        "rescaled_control_tensor_count": 9,
        "retained_advice_sha256": advice_digest,
        "retained_tensor_count": 30,
        "schema": RECEIPT_SCHEMA,
        "source_execution_matrix_sha256": matrix_audit["source_execution_matrix_sha256"],
        "source_manifest_sha256": manifest_audit["source_manifest_sha256"],
        "xy_certificate_count": 6,
    }
    receipt_bytes = canonical_bytes(receipt)
    receipt_digest = sha256_bytes(receipt_bytes)
    meter.check_caps()
    wall_ns = time.perf_counter_ns() - wall_start
    cpu_ns = time.process_time_ns() - cpu_start
    observed_rss = rss_bytes()
    if wall_ns > MAX_WALL_SECONDS * 1_000_000_000:
        reject("verifier_wall_clock_cap", "source verifier exceeded wall-clock cap")
    if cpu_ns > MAX_CPU_SECONDS * 1_000_000_000:
        reject("verifier_cpu_cap", "source verifier exceeded CPU cap")
    if observed_rss > MAX_RSS_BYTES:
        reject("verifier_rss_cap", "source verifier exceeded RSS cap")
    verifier_accounting = {
        "cpu_ns": cpu_ns,
        "logical_traffic_words": traffic_total(meter.traffic),
        "operation_vector": meter.operations,
        "peak_live_field_words": meter.peak_live_field_words,
        "peak_rss_bytes": observed_rss,
        "traffic_buckets": meter.traffic,
        "wall_clock_ns": wall_ns,
    }
    source_verification = {
        "audits": {
            "backend": backend_audit,
            "capability": capability_audit,
            "source_control_profile": source_control_profile_audit,
            "controls": control_audit,
            "gate_rank_ledger": gate_rank_audit,
            "ir_and_allocations": ir_audit,
            "manifest": manifest_audit,
            "matrix": matrix_audit,
            "producer_accounting": producer_accounting,
            "provenance": raw_header_audit,
            "semantics_and_ranks": semantic_audit,
        },
        "control_certificate_sha256": controls_digest,
        "raw_result_sha256": raw_digest,
        "receipt_sha256": receipt_digest,
        "retained_advice_sha256": advice_digest,
        "schema": "source-verification-record-v1",
        "valid": True,
        "verifier_accounting": verifier_accounting,
    }
    if source_phase_binding_audit is not None:
        source_verification["audits"]["source_phase_binding"] = source_phase_binding_audit
    if development_audit:
        result = {
            "artifact_freeze_authorized": False,
            "audits": source_verification["audits"],
            "boundary": (
                "Development-only complete source implementation audit. External "
                "filesystem, environment, call-graph, and isolated-staging "
                "attestations remain pending; no source artifact is emitted or frozen."
            ),
            "candidate_artifact_digests": {
                "control_certificate_sha256": controls_digest,
                "retained_advice_sha256": advice_digest,
            },
            "partition": "source_verifier_implementation_development",
            "protocol": PROTOCOL,
            "raw_result_sha256": raw_digest,
            "schema": "tt-source-implementation-development-verification-v1",
            "valid": True,
            "verifier_accounting": verifier_accounting,
        }
        _ACTIVE_OPERATION_VECTOR = None
        return result
    if strict_preflight:
        result = {
            "artifact_freeze_authorized": False,
            "audits": source_verification["audits"],
            "boundary": (
                "Development-only strict source preflight with external static-closure, "
                "filesystem, environment, staging, IR, allocation, accounting, semantic, "
                "and rank checks. The experiment has no execution_plan, so no source "
                "artifact is emitted or frozen."
            ),
            "candidate_artifact_digests": {
                "control_certificate_sha256": controls_digest,
                "retained_advice_sha256": advice_digest,
                "source_advice_receipt_sha256": receipt_digest,
            },
            "partition": "source_verifier_strict_preflight_development",
            "protocol": PROTOCOL,
            "raw_result_sha256": raw_digest,
            "schema": "tt-source-strict-preflight-development-verification-v1",
            "valid": True,
            "verifier_accounting": verifier_accounting,
        }
        _ACTIVE_OPERATION_VECTOR = None
        return result
    reject("execution_not_authorized", "artifact freeze mode is unavailable")


def failure_payload(error: BaseException) -> dict[str, Any]:
    if isinstance(error, VerificationError):
        code = error.code
        message = error.message
        path = error.path
    else:
        code = "internal_error"
        message = f"{type(error).__name__}: {error}"
        path = ""
    return {
        "error": {"code": code, "message": message, "path": path},
        "partition": "source_verifier",
        "protocol": PROTOCOL,
        "schema": OUTPUT_SCHEMA,
        "valid": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if args.describe_schema or args.help:
            result = schema_description()
        elif args.self_test:
            result = run_self_test()
        elif args.semantic_only_development:
            result = verify_semantic_development(args)
        else:
            result = verify(args)
        emit(result)
        return 0
    except BaseException as error:
        emit(failure_payload(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
