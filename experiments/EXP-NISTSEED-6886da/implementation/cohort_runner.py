#!/usr/bin/env python3
"""Fail-closed, one-index future ECPP compatibility trial driver.

No bulk/cohort CLI is exposed.  ``run_trial`` accepts one frozen cohort index,
a supervisor-created output directory, and an exact external binding manifest.
Tests inject a whole-boundary fake; production imports the frozen legacy library
only after every static binding has passed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPAT = ROOT / "research/nist_seed_ecpp_compat_20261024"
DATA = COMPAT / ".work/build-v4/ECPP/Ecpp/Data"

FROZEN = {
    "research/nist_seed_ecpp_compat_20261024/COHORT_PROTOCOL_DRAFT.md": "271cfe4936ef0e536508fe93583d79d840b1740dc0eeb2416e3901e21d582b93",
    "research/nist_seed_ecpp_compat_20261024/cohort_case.py": "55450647dcbfc0dd9ba37525eb876164341d7af1dc8256dece019a9b4d00e8d2",
    "research/nist_seed_ecpp_compat_20261024/cohort-inputs.json": "93ac4774b993a994a17d9327df92e0f2b287e66755cd933fdc683015fec1d545",
    "research/nist_seed_ecpp_compat_20261024/runtime-bindings.json": "53363f256e28c5e3d5b579e9c1b4f8230ed107d20988c1e4584899c0edc5d6ae",
    "research/nist_seed_ecpp_compat_20261024/runtime-summary.json": "fdf08f1fdd5ef81bc6bd440057c768c6c5aed394127dfdfc9f0a86f8f26123d8",
    "research/nist_seed_ecpp_compat_20261024/cohort-library-check.json": "e193a3b78c6dec50de1a1ec71566af4e1fae20d70e28a375cf3d0c201fa64bbb",
    "research/nist_seed_ecpp_compat_20261024/certificate_admission.py": "6cf50c95da246c7033dbb2cda8f8d70c07e2d5e366c1f1c9f163e7b115740c68",
    "research/nist_seed_ecpp_compat_20261024/guest_framing.py": "ce4f7a8b320826c09d9b947d306883d83b695b83ebfc496ec1d3e38ca6a76bf5",
    "research/nist_seed_ecpp_compat_20261024/qemu_controls.py": "255b415ebf5a8eaa5514a02fbd0fb9886f27a2065f8686586a2c336e9f9372e7",
    "tools/artifact_store.py": "8518bbbd385b077f6bf5344503ebe9c0feb8f0b3bb119e8e8a7deea8f461be59",
    "research/nist_seed_ecpp_source_20261024/REPLAY_REQUIREMENTS.md": "00c33929044b269b225ec5bf360fd09e2acde16813a98ca349379d8ad5a1a4d9",
    "research/nist_seed_ecpp_compat_20261024/BUILD_SCOPE.md": "b22f254a99a34aca73e1b1c31c387b6f8ff8fc166f893e59add21800f0561df0",
    "research/nist_seed_ecpp_compat_20261024/CONTROL_PROTOCOL.md": "d5471b0ea9ea9a5656ceb230f509048aca1545596fc14c3e0e1351bec998a7e3",
    "research/nist_seed_ecpp_compat_20261024/CONTROL_AMENDMENT.md": "4a8584e5439b424fa0a315a5a972f489d0fb5bf8c98fd426845c75de94eaa4ec",
    "research/nist_seed_ecpp_compat_20261024/QEMU_CONTROL_PROTOCOL.md": "f5e40459ce9fffdaaec3486d3e38939e877959f324209c725d54fac97f2daaa3",
    "research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl": "7902083817b988f00d562dc55f5c9bf5e0fa822fc0400618e6738acfb4990fb2",
    "research/nist_seed_skipped_curves_20261016/assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "research/nist_seed_skipped_curves_20261016/traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}

LIMITS = {
    "emulated_cpus": 1,
    "vm_ram_mib": 256,
    "child_address_space_mib": 128,
    "prover_guest_seconds": 300,
    "prover_host_seconds": 390,
    "checker_guest_seconds": 30,
    "checker_host_seconds": 90,
}

PRIMARY = {
    "serial": True,
    "full_original_data": True,
    "proving": True,
    "n_minus_1": True,
    "n_plus_1": True,
    "distributed": False,
    "debug": False,
    "fresh_vm": True,
    "fresh_process_rng": "original ModInitialize: srandom(1)",
}

SUPERVISOR_FILES = {"launch.json", "environment.json", "command.txt", "stdout.log", "stderr.log"}
PRIOR_BOOLEANS = (
    "on_curve",
    "n_prime_pari",
    "n_times_point_identity",
    "order_certified",
    "n_in_hasse_interval",
    "hasse_interval_narrower_than_n",
)


class Refusal(RuntimeError):
    pass


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise Refusal(f"not a regular non-symlink file: {path}")
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refusal(f"invalid JSON {path}: {error}") from error


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def integer(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError as error:
            raise Refusal(f"invalid integer encoding: {value!r}") from error
    raise Refusal(f"not an integer encoding: {value!r}")


def canonical_digest(value: Any) -> str:
    return sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def verify_frozen() -> dict[str, str]:
    actual: dict[str, str] = {}
    mismatches: dict[str, dict[str, str]] = {}
    for relative, expected in FROZEN.items():
        observed = sha_file(ROOT / relative)
        actual[relative] = observed
        if observed != expected:
            mismatches[relative] = {"expected": expected, "observed": observed}
    if mismatches:
        raise Refusal("frozen input digest mismatch: " + json.dumps(mismatches, sort_keys=True))
    return actual


def load_cohort() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cohort = read_json(COMPAT / "cohort-inputs.json")
    rows = cohort.get("rows")
    required = {"curve_uid", "curve_id", "label", "n", "p", "ordinal", "seed_hex", "timestamp"}
    if not isinstance(rows, list) or len(rows) != 21:
        raise Refusal("cohort does not have exactly 21 rows")
    if any(not isinstance(row, dict) or set(row) != required for row in rows):
        raise Refusal("cohort row schema mismatch")
    if len({row["curve_uid"] for row in rows}) != 21:
        raise Refusal("cohort UID duplication")
    if sum(row["label"] == "omitted" for row in rows) != 11 or sum(row["label"] == "published" for row in rows) != 10:
        raise Refusal("cohort label count mismatch")
    return rows, read_json(COMPAT / "runtime-bindings.json")


def canonical_sources() -> dict[str, tuple[str, dict[str, Any]]]:
    assessed = read_json(ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json")
    traits = read_json(ROOT / "research/nist_seed_skipped_curves_20261016/traits.json")
    omitted = assessed.get("candidate_rows")
    published = traits.get("published_controls")
    if not isinstance(omitted, list) or len(omitted) != 11:
        raise Refusal("assessed.candidate_rows is not the canonical 11-row omitted source")
    if not isinstance(published, dict) or len(published) != 10:
        raise Refusal("traits.published_controls is not the canonical named 10-row published source")
    answer: dict[str, tuple[str, dict[str, Any]]] = {}
    for label, records in (("omitted", omitted), ("published", list(published.values()))):
        for record in records:
            identity = record.get("identity") if isinstance(record, dict) else None
            uid = identity.get("curve_uid") if isinstance(identity, dict) else None
            if not isinstance(uid, str) or uid in answer:
                raise Refusal("duplicate or malformed canonical provenance UID")
            answer[uid] = (label, record)
    if len(answer) != 21:
        raise Refusal("canonical provenance collections do not yield exactly 21 UIDs")
    return answer


def prior_mapping(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    sources = canonical_sources()
    corpus_path = ROOT / "research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl"
    corpus = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line]
    mapped: dict[str, dict[str, Any]] = {}
    for row in rows:
        selected = sources.get(row["curve_uid"])
        if selected is None:
            raise Refusal(f"missing canonical source row: {row['curve_uid']}")
        label, source = selected
        identity = source.get("identity", {})
        curve = identity.get("curve", {})
        field = identity.get("field", {})
        if label != row["label"] or identity.get("curve_id") != row["curve_id"]:
            raise Refusal(f"canonical label or curve_id mismatch: {row['curve_uid']}")
        if integer(field.get("characteristic")) != integer(row["p"]):
            raise Refusal(f"canonical field parameter mismatch: {row['curve_uid']}")
        if integer(curve.get("subgroup_order")) != integer(row["n"]) or curve.get("cofactor") != 1:
            raise Refusal(f"canonical order/cofactor mismatch: {row['curve_uid']}")
        a4 = integer(curve.get("a4"))
        a6 = integer(curve.get("a6"))
        b = integer(source.get("b_hex"))
        matches = [
            item
            for item in corpus
            if item.get("record") == "certificate"
            and integer(item.get("p")) == integer(row["p"])
            and integer(item.get("n")) == integer(row["n"])
            and integer(item.get("b")) == b
            and item.get("index") == row["ordinal"]
            and item.get("run") == row["timestamp"]
            and str(item.get("seed", "")).lower() == row["seed_hex"].lower()
        ]
        if len(matches) != 1:
            raise Refusal(f"full p/n/b/seed/index/run prior corpus mapping is not unique: {row['curve_uid']}")
        corpus_record = matches[0]
        if not all(corpus_record.get(key) is True for key in PRIOR_BOOLEANS):
            raise Refusal(f"prior certificate booleans incomplete: {row['curve_uid']}")
        mapped[row["curve_uid"]] = {
            "label": label,
            "curve_id": row["curve_id"],
            "p": str(integer(row["p"])),
            "n": str(integer(row["n"])),
            "a4": str(a4),
            "a6": str(a6),
            "b": str(b),
            "cofactor": 1,
            "corpus_side": corpus_record["side"],
            "corpus_record_sha256": canonical_digest(corpus_record),
            "provenance_record_sha256": canonical_digest(source),
            "prior_booleans": {key: True for key in PRIOR_BOOLEANS},
        }
    if set(mapped) != {row["curve_uid"] for row in rows}:
        raise Refusal("prior map does not cover the exact 21-row cohort")
    return mapped


def parse_dfd(data_path: Path) -> dict[int, list[dict[str, Any]]]:
    raw = (data_path / "ecpp.DfD").read_bytes()
    grammar = re.compile(rb"^\(\((?P<factors>[0-9 ]*)\) (?P<d>-?[0-9]+) (?P<sign>-?[0-9]+)\)\r?$", re.M)
    answer: dict[int, list[dict[str, Any]]] = {}
    for ordinal, match in enumerate(grammar.finditer(raw)):
        d = int(match.group("d"))
        answer.setdefault(d, []).append({
            "file": "ecpp.DfD",
            "record": ordinal,
            "byte_offset": match.start("d"),
            "line": raw.count(b"\n", 0, match.start("d")) + 1,
            "factors": [factor.decode("ascii") for factor in match.group("factors").split()],
            "class_number_sign_code": int(match.group("sign")),
        })
    if 0 not in answer or 1 in answer:
        raise Refusal("ecpp.DfD source special-route expectations changed")
    return answer


def trace(serial: bytes, data_path: Path | None = None) -> dict[str, Any]:
    catalog = parse_dfd(DATA if data_path is None else data_path)
    grammars = (
        ("phase", re.compile(rb"^% Starting phase (?:1: building the sequence of primes|2: proving)$")),
        ("proving_job", re.compile(rb"^% Starting proving job for step ([0-9]+)$")),
        ("recursive_N", re.compile(rb"^% N_([0-9]+)=([0-9]+)$")),
        ("recursive_status", re.compile(rb"^% N_([0-9]+) is (prime|not prime)$")),
        ("retry", re.compile(rb"^%!% Forced to retry, snif\.\.\.$")),
        ("catalog_D", re.compile(rb"^% next D is (-?[0-9]+)$")),
        ("stored_D", re.compile(rb"^% D\[\[([0-9]+)\]\]=(-?[0-9]+)$")),
        ("proving_route", re.compile(rb"^% (?:No N-1 test|No N\+1 test|Cofactor is 1)$")),
    )
    events: list[dict[str, Any]] = []
    for found_line in re.finditer(rb"[^\n]*(?:\n|$)", serial):
        raw_line = found_line.group(0)
        if not raw_line:
            continue
        line = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
        if line.endswith(b"\r"):
            line = line[:-1]
        for kind, grammar in grammars:
            match = grammar.match(line)
            if match is None:
                continue
            event: dict[str, Any] = {
                "kind": kind,
                "printed": True,
                "source_offset": found_line.start(),
                "raw_utf8": line.decode("utf-8", "replace"),
                "raw_hex": line.hex(),
            }
            values = [group.decode("ascii") for group in match.groups()]
            if kind in {"catalog_D", "stored_D"}:
                value = int(values[-1])
                event["value"] = value
                event["index"] = int(values[0]) if kind == "stored_D" else None
                event["catalog_positions"] = catalog.get(value, [])
                event["special_route"] = "D=1 has no ecpp.DfD record; source switches D<=1 to route -1 or 1" if value == 1 else None
            else:
                event["value"] = values or None
            events.append(event)
            break
        else:
            if line.startswith(b"%"):
                events.append({
                    "kind": "unknown_marker",
                    "printed": True,
                    "source_offset": found_line.start(),
                    "raw_utf8": line.decode("utf-8", "replace"),
                    "raw_hex": line.hex(),
                })
    return {
        "schema": "trace_schema.json",
        "raw_serial_sha256": sha_bytes(serial),
        "events": events,
        "unprinted_state": "UNOBSERVED",
        "inference_prohibited": "unprinted branches are not reconstructed as attempted",
    }


def guest_parts(serial: bytes) -> tuple[bytes, bytes, list[bytes]]:
    text = serial.replace(b"\r\n", b"\n").decode("utf-8", "replace")
    encoded = text.encode("utf-8")
    begin = b"__ECPP_GUEST_BEGIN__\n"
    exit_marker = b"\n__ECPP_CHILD_EXIT__"
    if encoded.count(begin) != 1 or encoded.count(b"__ECPP_CHILD_EXIT__ ") != 1:
        raise Refusal("serial does not have exactly one guest begin/child exit sentinel")
    if begin not in encoded or exit_marker not in encoded:
        raise Refusal("serial does not expose a complete guest body")
    body = encoded.split(begin, 1)[1].split(exit_marker, 1)[0]
    certificates = re.findall(rb"__ECPP_CERTIFICATE_BEGIN__\n(.*?)\n__ECPP_CERTIFICATE_END__", encoded, re.S)
    return encoded, body, certificates


def recover_retained_prover_status(child: Path, serial: bytes, certificates: list[bytes]) -> dict[str, Any]:
    """Recover only a complete, serial-consistent status left by the boundary.

    Exception handling may observe a child which wrote raw output before the
    frozen library returned its observation.  The raw result is evidence only
    when it is a regular JSON record with the primitive fields the independent
    checker will reconcile; otherwise the censored envelope records recovery
    failure and remains rejectable by that checker.
    """
    result_path = child / "prover" / "result.json"
    result = read_json(result_path)
    if not isinstance(result, dict):
        raise Refusal("retained prover result is not an object")
    required = {
        "vm_valid",
        "qemu_exit",
        "child_exit",
        "reason",
        "elapsed_host_seconds",
        "serial_sha256",
        "certificate_count",
    }
    if not required <= set(result):
        raise Refusal("retained prover result lacks primitive status fields")
    if result["serial_sha256"] != sha_bytes(serial):
        raise Refusal("retained prover result serial digest mismatch")
    if type(result["certificate_count"]) is not int or result["certificate_count"] != len(certificates):
        raise Refusal("retained prover result certificate count mismatch")
    if type(result["vm_valid"]) is not bool:
        raise Refusal("retained prover result vm_valid is not boolean")
    return result


def verify_supervisor(output: Path, binding: Path, index: int, frozen: dict[str, str]) -> dict[str, Any]:
    if not output.is_dir() or output.is_symlink() or not binding.is_file() or binding.is_symlink():
        raise Refusal("supervisor directory or external manifest is unsafe")
    if {entry.name for entry in output.iterdir()} != SUPERVISOR_FILES:
        raise Refusal("fresh supervisor directory must contain exactly its five provenance files")
    manifest = read_json(binding)
    if manifest.get("schema") != "crypto.autoresearch.nistseed_ecpp_trial_binding.v1":
        raise Refusal("binding manifest schema mismatch")
    if manifest.get("cohort_index") != index or Path(manifest.get("output_directory", "")).resolve() != output.resolve():
        raise Refusal("binding manifest identity mismatch")
    if manifest.get("frozen_input_sha256") != frozen or manifest.get("limits") != LIMITS or manifest.get("primary_configuration") != PRIMARY:
        raise Refusal("binding manifest frozen/configuration mismatch")
    launch = read_json(output / "launch.json")
    argv = json.loads((output / "command.txt").read_text(encoding="utf-8"))
    if not isinstance(argv, list) or not all(isinstance(item, str) for item in argv):
        raise Refusal("command.txt is not a JSON argv list")
    if launch.get("argv") != argv or str(index) not in argv or str(output) not in argv or str(binding) not in argv:
        raise Refusal("supervisor argv identity mismatch")
    if not isinstance(launch.get("authority"), dict) or not isinstance(read_json(output / "environment.json"), dict):
        raise Refusal("supervisor provenance incomplete")
    return manifest


def owned_inventory(root: Path) -> dict[str, str]:
    if not root.is_dir() or root.is_symlink():
        raise Refusal("driver-owned child directory is missing or unsafe")
    answer: dict[str, str] = {}
    resolved = root.resolve()
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise Refusal(f"symlink in driver-owned artifact tree: {path}")
        if path.is_dir():
            continue
        if not path.is_file() or not path.resolve().is_relative_to(resolved):
            raise Refusal(f"unsafe driver-owned artifact path: {path}")
        answer[path.relative_to(root).as_posix()] = sha_file(path)
    if not answer:
        raise Refusal("driver-owned artifact inventory is empty")
    return answer


def emit(output: Path, raw: dict[str, Any], observation: dict[str, Any], failure: dict[str, Any] | None) -> dict[str, Any]:
    write_json(output / "observation.json", observation)
    if failure is not None:
        write_json(output / "failure.json", failure)
    raw["driver_artifacts"] = owned_inventory(output / "legacy-child") if (output / "legacy-child").exists() else {}
    write_json(output / "raw-result.json", raw)
    (output / "manifest.yaml").write_text(
        "run:\n  attack_claimed: false\n  result:\n    raw_result: raw-result.json\n  status_note: legacy behavior observation only; no primality, historical, curve-security, or ECDLP conclusion\n",
        encoding="utf-8",
    )
    return raw


def _default_legacy_call(index: int, child: Path, cache: Path) -> dict[str, Any]:
    sys.path.insert(0, str(COMPAT))
    import cohort_case
    import qemu_controls

    frozen_runtime = qemu_controls.RUNTIME
    cache.mkdir(mode=0o700)
    kernel = frozen_runtime / "vmlinuz-lts"
    if not kernel.is_file() or kernel.is_symlink():
        raise Refusal("frozen kernel unavailable for private cache")
    os.link(kernel, cache / "vmlinuz-lts")
    (cache / "images").mkdir(mode=0o700)
    qemu_controls.RUNTIME = cache
    try:
        return cohort_case.execute_case(index, child)
    finally:
        qemu_controls.RUNTIME = frozen_runtime


def run_trial(index: int, output: Path, binding: Path, legacy_call: Callable[[int, Path, Path], dict[str, Any]] | None = None) -> dict[str, Any]:
    if type(index) is not int or not 0 <= index < 21:
        raise Refusal("cohort index outside [0,20]")
    frozen = verify_frozen()
    rows, runtime = load_cohort()
    external_manifest = verify_supervisor(output, binding, index, frozen)
    mapping = prior_mapping(rows)
    row = rows[index]
    copied = output / "input-binding-manifest.json"
    shutil.copyfile(binding, copied)
    if copied.read_bytes() != binding.read_bytes():
        raise Refusal("copied input-binding manifest byte mismatch")
    child = output / "legacy-child"
    cache = output / "runtime-cache"
    if child.exists() or cache.exists():
        raise Refusal("reused child destination or private cache")
    raw: dict[str, Any] = {
        "schema": "crypto.autoresearch.nistseed_ecpp_raw_result.v5",
        "cohort_index": index,
        "curve": row,
        "input_binding_manifest_sha256": sha_file(copied),
        "external_binding_manifest_sha256": sha_file(binding),
        "frozen_input_sha256": frozen,
        "runtime_payloads": runtime["artifacts"],
        "kernel": runtime["kernel"],
        "original_data": runtime["original_data"],
        "limits": LIMITS,
        "primary_configuration": PRIMARY,
        "supervisor_artifact_sha256": {name: sha_file(output / name) for name in SUPERVISOR_FILES},
        "supervisor_manifest": external_manifest,
        "prior_primality_mapping": mapping,
        "named_orders_executed": 1,
    }
    observation: dict[str, Any] = {
        "curve_uid": row["curve_uid"],
        "prior_primality_evidence": mapping[row["curve_uid"]],
        "mathematical_classification": "INDETERMINATE",
        "legacy_labels_observation_only": [],
        "stage": "bound_before_legacy_start",
        "unprinted_state": "UNOBSERVED",
        "legacy_execution_started": False,
    }
    try:
        result = (legacy_call or _default_legacy_call)(index, child, cache)
        if not isinstance(result, dict):
            raise Refusal("legacy boundary did not return an observation object")
        observation.update(result)
        serial_path = child / "prover" / "serial.raw"
        if serial_path.is_file() and not serial_path.is_symlink():
            serial = serial_path.read_bytes()
            _, body, certificates = guest_parts(serial)
            observation["legacy_execution_started"] = True
            observation["legacy_labels_observation_only"] = [item.decode("ascii") for item in re.findall(rb"^(?:% )?This number is (prime|composite)\b", body, re.M)]
            observation["trace"] = trace(serial)
            observation["stage"] = "prover_observed"
            observation["prover_body_sha256"] = sha_bytes(body)
            observation["prover_certificate_count"] = len(certificates)
        admitted = observation.get("certificate_admitted") is True
        observation["mathematical_classification"] = "PRIOR_PRIMALITY_EVIDENCE_REQUIRED" if admitted else "INDETERMINATE"
        raw["classification"] = observation["mathematical_classification"]
        raw["censoring"] = not admitted
        prover = observation.get("prover")
        failed_prover_status = (
            isinstance(prover, dict)
            and (
                prover.get("qemu_exit") != 33
                or prover.get("reason") is not None
                or prover.get("child_exit") != 0
            )
        )
        failure = None
        if not admitted and failed_prover_status:
            failure = {
                "stage": "prover",
                "reason": "retained invalid/watchdog prover status",
                "classification": "INDETERMINATE",
            }
        return emit(output, raw, observation, failure)
    except BaseException as error:
        raw["classification"] = "INDETERMINATE"
        raw["censoring"] = True
        raw["exception"] = {"type": type(error).__name__, "message": str(error)}
        serial_path = child / "prover" / "serial.raw"
        if serial_path.is_file() and not serial_path.is_symlink():
            serial = serial_path.read_bytes()
            _, body, certificates = guest_parts(serial)
            observation["legacy_execution_started"] = True
            observation["legacy_labels_observation_only"] = [item.decode("ascii") for item in re.findall(rb"^(?:% )?This number is (prime|composite)\b", body, re.M)]
            observation["trace"] = trace(serial)
            observation["prover_body_sha256"] = sha_bytes(body)
            observation["prover_certificate_count"] = len(certificates)
            observation["stage"] = "partial_prover_observed"
            try:
                observation["prover"] = recover_retained_prover_status(child, serial, certificates)
            except Refusal as recovery_error:
                observation["prover_status_recovery_error"] = str(recovery_error)
        observation["censor_reason"] = f"{type(error).__name__}: {error}"
        return emit(output, raw, observation, raw["exception"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input-binding-manifest", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_trial(args.index, args.output, args.input_binding_manifest), sort_keys=True))


if __name__ == "__main__":
    main()
