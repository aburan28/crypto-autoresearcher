#!/usr/bin/env python3
"""Run the independent source verifier inside an audited staging root."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from typing import Any, Mapping, Sequence

STAGE_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
if STAGE_ROOT not in sys.path:
    sys.path.insert(0, STAGE_ROOT)

from run_tt_source_partition import (
    EXPECTED_ENVIRONMENT,
    RuntimeAudit,
    canonical_bytes,
    install_path_wrappers,
)


RECEIPT_PREFIX = b"TT_SOURCE_VERIFIER_RUNTIME_RECEIPT\t"
EXPECTED_STAGE_FILES = (
    "run_tt_source_partition.py",
    "run_tt_source_verifier_partition.py",
    "source-execution-matrix-v2.json",
    "source-generator-raw-result.json",
    "source-instance-manifest-v1.json",
    "verify_tt_source_advice.py",
)


def emit(value: Mapping[str, Any]) -> None:
    sys.stdout.buffer.write(canonical_bytes(value))
    sys.stdout.buffer.flush()


def emit_receipt(value: Mapping[str, Any]) -> None:
    sys.stderr.buffer.write(RECEIPT_PREFIX + canonical_bytes(value))
    sys.stderr.buffer.flush()


def parse_bootstrap_args(argv: Sequence[str]) -> tuple[list[str], str, str]:
    values: dict[str, str] = {}
    verifier_args: list[str] = []
    index = 0
    while index < len(argv):
        flag = argv[index]
        if flag in {"--expected-stage-sha256", "--static-audit-sha256"}:
            if index + 1 >= len(argv) or flag in values:
                raise ValueError(f"invalid bootstrap argument {flag}")
            values[flag] = argv[index + 1]
            index += 2
            continue
        verifier_args.append(flag)
        if flag == "--strict-preflight-development":
            index += 1
            continue
        if index + 1 >= len(argv):
            raise ValueError(f"missing verifier value for {flag}")
        verifier_args.append(argv[index + 1])
        index += 2
    required = {"--expected-stage-sha256", "--static-audit-sha256"}
    if set(values) != required:
        raise ValueError("source verifier bootstrap arguments are incomplete")
    for flag in required:
        digest = values[flag]
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError(f"{flag} is not a SHA-256 digest")
    return (
        verifier_args,
        values["--expected-stage-sha256"],
        values["--static-audit-sha256"],
    )


def main(argv: Sequence[str] | None = None) -> int:
    verifier_args, expected_stage_sha256, static_audit_sha256 = parse_bootstrap_args(
        list(sys.argv[1:] if argv is None else argv)
    )
    stage_root = STAGE_ROOT
    if os.path.normpath(os.getcwd()) != stage_root:
        raise RuntimeError("source verifier did not start in its staging root")
    observed_files = tuple(sorted(os.listdir(stage_root)))
    if observed_files != tuple(sorted(EXPECTED_STAGE_FILES)):
        raise RuntimeError("source verifier staging root differs from the allowlist")

    os.environ.clear()
    os.environ.update(EXPECTED_ENVIRONMENT)
    if dict(os.environ) != EXPECTED_ENVIRONMENT:
        raise RuntimeError("source verifier environment could not be reduced")
    if stage_root not in sys.path:
        sys.path.insert(0, stage_root)

    audit = RuntimeAudit(
        stage_root,
        expected_stage_files=EXPECTED_STAGE_FILES,
        cache_modules=("run_tt_source_partition", "verify_tt_source_advice"),
        expected_environment_events=(),
    )
    install_path_wrappers(audit)
    sys.addaudithook(audit.audit_hook)
    started_ns = time.perf_counter_ns()

    import verify_tt_source_advice as verifier

    status = 0
    try:
        arguments = verifier.parse_args(verifier_args)
        if not arguments.strict_preflight_development:
            raise ValueError("source verifier bootstrap permits only strict preflight")
        result = verifier.verify(arguments)
    except BaseException as error:
        result = verifier.failure_payload(error)
        status = 1
    receipt = audit.receipt(
        static_audit_sha256=static_audit_sha256,
        expected_stage_sha256=expected_stage_sha256,
        started_ns=started_ns,
    )
    if not receipt["valid"]:
        raise RuntimeError(
            "source verifier runtime receipt is invalid: "
            + json.dumps(
                {
                    "denied_events": receipt["denied_events"],
                    "environment_matches": receipt["environment"]
                    == EXPECTED_ENVIRONMENT,
                    "stage_digest_matches": receipt["stage_sha256"]
                    == receipt["expected_stage_sha256"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
    receipt["result_sha256"] = hashlib.sha256(canonical_bytes(result)).hexdigest()
    receipt["role"] = "verifier"
    emit_receipt(receipt)
    emit(result)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
