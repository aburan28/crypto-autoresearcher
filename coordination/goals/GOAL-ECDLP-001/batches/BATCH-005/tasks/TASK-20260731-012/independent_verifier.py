#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent verifier for crypto.autoresearch.rank_failure_conservation_certificate
v1.0.0-review (toy / review-only activation pin).

This file is the hash-bound independent verifier artifact. Its exact bytes are
what activation packages pin as independent_verifier_artifact_sha256. If that
pin is null or missing at seal/activation check time, fail closed with
PRECOMMIT_VERIFIER_HASH_MISSING.

Deterministic. No network. No randomness. Stdlib only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

CONTRACT_SCHEMA = "crypto.autoresearch.rank_failure_conservation_certificate"
CONTRACT_VERSION = "1.0.0-review"
VERIFIER_ID = "rank-failure-conservation-independent-verifier"
VERIFIER_VERSION = "1.0.0-review-activation"

# BATCH-004 sealed digests (reuse; do not reopen unless defect found).
SEALED_FIXTURE_SHA256 = (
    "4c82f5e43efce185a2ecbf2cbcc24b6da7a1bddadd1176007427be350494c4a8"
)
SEALED_SCHEDULE_SHA256 = (
    "be41eb8d016f049d31a3f2ce5bdeda94fb60548b9108311bddca5ede9f9f2279"
)

FROZEN_GROUP_OP_TYPES = (
    "add",
    "dbl",
    "mixed_add",
    "scalar_mul_fixed_window",
    "endomorphism_apply",
    "equality_test",
    "encode_decode",
)

NINE_PLANTED_CONTROL_IDS = (
    "CTRL-OMISSION",
    "CTRL-DUPLICATE-ID",
    "CTRL-RETRY-CYCLE",
    "CTRL-FIELD-SCHEMA",
    "CTRL-SHARED-DOUBLE",
    "CTRL-SHARED-OMITTED",
    "CTRL-CERTIFICATE-ROW",
    "CTRL-WRONG-FIELD",
    "CTRL-CLEAN",
)

CONTROL_EXPECTED = {
    "CTRL-OMISSION": "BIJECTION_MISSING_RECEIPT",
    "CTRL-DUPLICATE-ID": "BIJECTION_DUPLICATE_ID",
    "CTRL-RETRY-CYCLE": "SCHEDULE_RETRY_CYCLE",
    "CTRL-FIELD-SCHEMA": "FIELD_OR_SCHEMA_MISMATCH",
    "CTRL-SHARED-DOUBLE": "SHARED_WORK_DOUBLE_COUNT",
    "CTRL-SHARED-OMITTED": "SHARED_WORK_UNOWNED",
    "CTRL-CERTIFICATE-ROW": "CERTIFICATE_ROW_MISMATCH_AND_ZERO_RANK",
    "CTRL-WRONG-FIELD": "INDEPENDENT_RANK_MISMATCH",
    "CTRL-CLEAN": "PASS_ONLY_IF_ALL_CONSERVATION_GATES_PASS",
}

SCHEDULE_REQUIRED_ROOT_FIELDS = (
    "contract_schema",
    "contract_version",
    "campaign_id",
    "public_fixture",
    "field",
    "column_schema",
    "canonical_row_format",
    "terminal_vocabulary",
    "resource_schema",
    "probability_plan",
    "attempts",
    "initial_matrix",
    "precommit",
)

PRECOMMIT_VERIFIER_HASH_MISSING = "PRECOMMIT_VERIFIER_HASH_MISSING"
PRECOMMIT_SNAPSHOT_UNVERIFIED = "PRECOMMIT_SNAPSHOT_UNVERIFIED"
PRECOMMIT_SCHEDULE_UNSEALED = "PRECOMMIT_SCHEDULE_UNSEALED"


class VerifierError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_int_key(s: str) -> bool:
    if s in ("", "-", "+"):
        return False
    if s[0] in "+-":
        body = s[1:]
    else:
        body = s
    return body.isdigit() and (body == "0" or not body.startswith("0"))


def _jcs_escape(s: str) -> str:
    out: List[str] = ['"']
    for ch in s:
        o = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif o < 0x20:
            out.append("\\u%04x" % o)
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def jcs_dumps(value: Any) -> str:
    """RFC 8785-style JSON Canonicalization Scheme (subset sufficient here)."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _jcs_escape(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        raise VerifierError("JCS_UNSUPPORTED", "float values are not accepted")
    if isinstance(value, list):
        return "[" + ",".join(jcs_dumps(v) for v in value) + "]"
    if isinstance(value, dict):
        items: List[Tuple[str, Any]] = []
        for k, v in value.items():
            if not isinstance(k, str):
                raise VerifierError("JCS_UNSUPPORTED", "non-string object keys")
            items.append((k, v))

        def sort_key(item: Tuple[str, Any]) -> Tuple[int, Any]:
            k = item[0]
            if _is_int_key(k):
                return (0, int(k))
            return (1, k.encode("utf-8"))

        items.sort(key=sort_key)
        return "{" + ",".join(_jcs_escape(k) + ":" + jcs_dumps(v) for k, v in items) + "}"
    raise VerifierError("JCS_UNSUPPORTED", f"unsupported type {type(value)!r}")


def digest_document(doc: Dict[str, Any], exclude_keys: Sequence[str]) -> str:
    filtered = {k: v for k, v in doc.items() if k not in exclude_keys}
    return sha256_hex(jcs_dumps(filtered).encode("utf-8"))


def load_json(path: Path) -> Dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise VerifierError("JSON_ROOT_NOT_OBJECT", f"{path} root must be object")
    return data


def file_sha256(path: Path) -> str:
    return sha256_hex(path.read_bytes())


def self_artifact_sha256() -> str:
    return file_sha256(Path(__file__).resolve())


def check_verifier_hash_pin(pinned: Optional[str], expected: Optional[str]) -> None:
    """Hard-fail PRECOMMIT_VERIFIER_HASH_MISSING when pin is null/empty.

    This module's exact bytes are the artifact that must be hashed and pinned.
    """
    if pinned is None or (isinstance(pinned, str) and pinned.strip() == ""):
        raise VerifierError(
            PRECOMMIT_VERIFIER_HASH_MISSING,
            "independent_verifier_artifact_sha256 is null/empty; "
            "activation fails closed until this artifact's sha256 is pinned",
        )
    if not isinstance(pinned, str) or len(pinned) != 64:
        raise VerifierError(
            PRECOMMIT_VERIFIER_HASH_MISSING,
            "independent_verifier_artifact_sha256 must be 64 lowercase hex chars",
        )
    if pinned != pinned.lower() or any(c not in "0123456789abcdef" for c in pinned):
        raise VerifierError(
            PRECOMMIT_VERIFIER_HASH_MISSING,
            "independent_verifier_artifact_sha256 must be lowercase hex",
        )
    actual = self_artifact_sha256()
    if pinned != actual:
        raise VerifierError(
            "VERIFIER_HASH_MISMATCH",
            f"pin {pinned} != sha256(this file) {actual}",
        )
    if expected is not None and pinned != expected:
        raise VerifierError(
            "VERIFIER_HASH_MISMATCH",
            f"pin {pinned} != expected activation pin {expected}",
        )


def check_fixture(fixture_path: Path, sealed_sha256: str) -> Dict[str, Any]:
    fixture = load_json(fixture_path)
    # Digest rule: JCS of document without a fixture_sha256 field.
    computed = digest_document(fixture, exclude_keys=("fixture_sha256",))
    raw = file_sha256(fixture_path)
    # Already-canonical files satisfy raw == JCS; enforce both against seal.
    if computed != sealed_sha256:
        raise VerifierError(
            "FIXTURE_DIGEST_MISMATCH",
            f"JCS digest {computed} != sealed {sealed_sha256}",
        )
    if raw != sealed_sha256:
        raise VerifierError(
            "FIXTURE_RAW_DIGEST_MISMATCH",
            f"raw file digest {raw} != sealed {sealed_sha256} "
            "(file must already be JCS-canonical)",
        )
    for key in (
        "fixture_id",
        "fixture_version",
        "curve_or_group_parameters",
        "subgroup_order",
        "factor_base_points",
    ):
        if key not in fixture:
            raise VerifierError("FIXTURE_FIELD_MISSING", f"missing {key}")
    return fixture


def check_group_op_vocabulary(schedule: Dict[str, Any]) -> None:
    rs = schedule.get("resource_schema")
    if not isinstance(rs, dict):
        raise VerifierError("GROUP_OP_VOCAB_MISSING", "resource_schema missing")
    gop = rs.get("group_operations_by_declared_type")
    if not isinstance(gop, dict):
        raise VerifierError(
            "GROUP_OP_VOCAB_MISSING",
            "resource_schema.group_operations_by_declared_type missing",
        )
    frozen = gop.get("frozen_types")
    if not isinstance(frozen, list):
        raise VerifierError("GROUP_OP_VOCAB_MISSING", "frozen_types missing")
    if tuple(frozen) != FROZEN_GROUP_OP_TYPES:
        raise VerifierError(
            "GROUP_OP_VOCAB_MISMATCH",
            f"frozen_types {frozen!r} != {list(FROZEN_GROUP_OP_TYPES)!r}",
        )


def check_empty_or_pilot_schedule(
    schedule_path: Path, sealed_sha256: str
) -> Dict[str, Any]:
    schedule = load_json(schedule_path)
    computed = digest_document(schedule, exclude_keys=("schedule_sha256",))
    raw = file_sha256(schedule_path)
    if computed != sealed_sha256:
        raise VerifierError(
            "SCHEDULE_DIGEST_MISMATCH",
            f"JCS digest {computed} != sealed {sealed_sha256}",
        )
    if raw != sealed_sha256:
        raise VerifierError(
            "SCHEDULE_RAW_DIGEST_MISMATCH",
            f"raw file digest {raw} != sealed {sealed_sha256}",
        )
    for key in SCHEDULE_REQUIRED_ROOT_FIELDS:
        if key not in schedule:
            raise VerifierError("SCHEDULE_FIELD_MISSING", f"missing {key}")
    if schedule.get("contract_schema") != CONTRACT_SCHEMA:
        raise VerifierError("CONTRACT_SCHEMA_MISMATCH", "unexpected contract_schema")
    if schedule.get("contract_version") != CONTRACT_VERSION:
        raise VerifierError("CONTRACT_VERSION_MISMATCH", "unexpected contract_version")
    mode = schedule.get("mode")
    if mode != "empty_or_pilot":
        raise VerifierError(
            "SCHEDULE_MODE_UNSUPPORTED",
            f"this activation verifier accepts only empty_or_pilot, got {mode!r}",
        )
    attempts = schedule.get("attempts")
    if not isinstance(attempts, list):
        raise VerifierError("ATTEMPTS_INVALID", "attempts must be a list")
    # empty_or_pilot permits empty attempt contents.
    check_group_op_vocabulary(schedule)
    pf = schedule.get("public_fixture")
    if not isinstance(pf, dict):
        raise VerifierError("SCHEDULE_FIXTURE_MISSING", "public_fixture missing")
    if pf.get("fixture_sha256") != SEALED_FIXTURE_SHA256:
        raise VerifierError(
            "SCHEDULE_FIXTURE_PIN_MISMATCH",
            "schedule.public_fixture.fixture_sha256 != sealed fixture digest",
        )
    # point_sha256 preimage convention (RT699-O2): sha256(UTF-8 hex string).
    for col in schedule.get("column_schema") or []:
        if not isinstance(col, dict):
            raise VerifierError("COLUMN_SCHEMA_INVALID", "non-object column")
        enc = col.get("point_encoding_hex")
        digest = col.get("point_sha256")
        if not isinstance(enc, str) or not isinstance(digest, str):
            raise VerifierError("COLUMN_SCHEMA_INVALID", "point fields missing")
        expected = sha256_hex(enc.encode("utf-8"))
        if digest != expected:
            raise VerifierError(
                "POINT_SHA256_MISMATCH",
                f"{col.get('column_id')}: {digest} != sha256(utf8_hex) {expected}",
            )
    return schedule


def check_planted_controls(protocol: Optional[Dict[str, Any]]) -> None:
    """If a protocol document supplies controls, enforce the nine-control vocab."""
    if protocol is None:
        return
    controls = protocol.get("controls")
    if controls is None and isinstance(protocol.get("toy_validation_protocol"), dict):
        controls = protocol["toy_validation_protocol"].get("controls")
    if controls is None:
        return
    if not isinstance(controls, list):
        raise VerifierError("CONTROLS_INVALID", "controls must be a list")
    ids = []
    for c in controls:
        if not isinstance(c, dict) or "id" not in c:
            raise VerifierError("CONTROLS_INVALID", "control missing id")
        cid = c["id"]
        ids.append(cid)
        expected = c.get("expected") or c.get("expected_verdict")
        if cid in CONTROL_EXPECTED and expected != CONTROL_EXPECTED[cid]:
            raise VerifierError(
                "CONTROL_EXPECTED_MISMATCH",
                f"{cid}: expected {CONTROL_EXPECTED[cid]!r}, got {expected!r}",
            )
    if sorted(ids) != sorted(NINE_PLANTED_CONTROL_IDS):
        raise VerifierError(
            "CONTROLS_VOCAB_MISMATCH",
            f"control ids {ids!r} != required nine {list(NINE_PLANTED_CONTROL_IDS)!r}",
        )


def evaluate_activation_gates(
    pinned_verifier_sha256: Optional[str],
    verified_before_execution: bool,
    snapshot_commit_sha: Optional[str],
    schedule_seal_acknowledged: bool,
) -> List[str]:
    """Return remaining activation no-go codes (empty only if fully executable).

    Pinning this artifact discharges PRECOMMIT_VERIFIER_HASH_MISSING only.
    Snapshot verification and execution sealing remain later gates.
    """
    remaining: List[str] = []
    try:
        check_verifier_hash_pin(pinned_verifier_sha256, expected=None)
    except VerifierError as exc:
        if exc.code == PRECOMMIT_VERIFIER_HASH_MISSING:
            remaining.append(PRECOMMIT_VERIFIER_HASH_MISSING)
        else:
            remaining.append(exc.code)
    if not verified_before_execution or not snapshot_commit_sha:
        remaining.append(PRECOMMIT_SNAPSHOT_UNVERIFIED)
    if not schedule_seal_acknowledged:
        remaining.append(PRECOMMIT_SCHEDULE_UNSEALED)
    return remaining


def load_yaml_lite_controls(path: Path) -> Optional[Dict[str, Any]]:
    """Minimal YAML extract for planted controls (stdlib-only; no PyYAML).

    Accepts either a JSON protocol or a tiny YAML subset with a `controls:`
    list of `{id, expected}` maps as in toy_validation_protocol.yaml.
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return load_json(path)
    controls: List[Dict[str, str]] = []
    in_controls = False
    controls_indent: Optional[int] = None
    current: Optional[Dict[str, str]] = None
    for line in text.splitlines():
        if not in_controls:
            stripped = line.lstrip(" ")
            if stripped.startswith("controls:"):
                in_controls = True
                controls_indent = len(line) - len(stripped)
                continue
            continue
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if controls_indent is not None and indent <= controls_indent:
            break
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current:
                controls.append(current)
            current = {"id": stripped.split(":", 1)[1].strip()}
        elif current is not None and stripped.startswith("expected:"):
            current["expected"] = stripped.split(":", 1)[1].strip()
    if current:
        controls.append(current)
    if not controls:
        return None
    return {"controls": controls}


def build_report(
    *,
    fixture_path: Path,
    schedule_path: Path,
    pinned_verifier_sha256: str,
    verified_before_execution: bool,
    snapshot_commit_sha: Optional[str],
    schedule_seal_acknowledged: bool,
    protocol_path: Optional[Path],
) -> Dict[str, Any]:
    check_verifier_hash_pin(pinned_verifier_sha256, expected=pinned_verifier_sha256)
    fixture = check_fixture(fixture_path, SEALED_FIXTURE_SHA256)
    schedule = check_empty_or_pilot_schedule(schedule_path, SEALED_SCHEDULE_SHA256)
    protocol_doc = None
    if protocol_path is not None:
        protocol_doc = load_yaml_lite_controls(protocol_path)
        check_planted_controls(protocol_doc)
    remaining = evaluate_activation_gates(
        pinned_verifier_sha256=pinned_verifier_sha256,
        verified_before_execution=verified_before_execution,
        snapshot_commit_sha=snapshot_commit_sha,
        schedule_seal_acknowledged=schedule_seal_acknowledged,
    )
    return {
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "independent_verifier_artifact_sha256": self_artifact_sha256(),
        "contract_schema": CONTRACT_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "fixture_path": str(fixture_path),
        "fixture_sha256": SEALED_FIXTURE_SHA256,
        "fixture_id": fixture.get("fixture_id"),
        "schedule_path": str(schedule_path),
        "schedule_sha256": SEALED_SCHEDULE_SHA256,
        "schedule_mode": schedule.get("mode"),
        "group_operation_types": list(FROZEN_GROUP_OP_TYPES),
        "planted_controls_checked": protocol_path is not None,
        "verified_before_execution": verified_before_execution,
        "activation_executable": len(remaining) == 0,
        "remaining_activation_gates": remaining,
        "authorization_note": (
            "Passing structural checks does not authorize a relation/solve "
            "campaign. Separate Coordinator ledger authorization is required."
        ),
        "status": "STRUCTURAL_OK" if PRECOMMIT_VERIFIER_HASH_MISSING not in remaining else "BLOCKED",
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Independent structural verifier for rank-failure conservation "
            "certificate v1.0.0-review (toy activation pin)."
        )
    )
    parser.add_argument("--fixture", type=Path, default=None)
    parser.add_argument("--schedule", type=Path, default=None)
    parser.add_argument(
        "--pinned-verifier-sha256",
        default=None,
        help=(
            "Concrete independent_verifier_artifact_sha256 pin. "
            "Null/empty hard-fails with PRECOMMIT_VERIFIER_HASH_MISSING. "
            "Must equal sha256 of this file's exact bytes."
        ),
    )
    parser.add_argument(
        "--protocol",
        type=Path,
        default=None,
        help="Optional protocol YAML/JSON to validate nine planted controls",
    )
    parser.add_argument(
        "--verified-before-execution",
        action="store_true",
        help="Set only after a later authorized execution seal",
    )
    parser.add_argument(
        "--snapshot-commit-sha",
        default=None,
        help="Execution-time verified snapshot commit (optional at pin time)",
    )
    parser.add_argument(
        "--schedule-seal-acknowledged",
        action="store_true",
        help="Set when Coordinator execution seal binds schedule_sha256",
    )
    parser.add_argument(
        "--print-self-sha256",
        action="store_true",
        help="Print sha256 of this file and exit",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.print_self_sha256:
        sys.stdout.write(self_artifact_sha256() + "\n")
        return 0

    if args.fixture is None or args.schedule is None:
        parser.error("--fixture and --schedule are required unless --print-self-sha256")
    if args.pinned_verifier_sha256 is None:
        # Explicit null path for the hard-fail gate documentation/check.
        args.pinned_verifier_sha256 = ""

    try:
        report = build_report(
            fixture_path=args.fixture,
            schedule_path=args.schedule,
            pinned_verifier_sha256=args.pinned_verifier_sha256,
            verified_before_execution=bool(args.verified_before_execution),
            snapshot_commit_sha=args.snapshot_commit_sha,
            schedule_seal_acknowledged=bool(args.schedule_seal_acknowledged),
            protocol_path=args.protocol,
        )
    except VerifierError as exc:
        payload = {
            "status": "FAIL",
            "code": exc.code,
            "message": exc.message,
            "independent_verifier_artifact_sha256": self_artifact_sha256(),
            "authorization_note": (
                "Failure here is not a mathematical ECDLP result."
            ),
        }
        sys.stdout.write(jcs_dumps(payload) + "\n")
        return 2

    sys.stdout.write(jcs_dumps(report) + "\n")
    # Exit 0 for structural pin OK even when later activation gates remain.
    return 0


if __name__ == "__main__":
    sys.exit(main())
