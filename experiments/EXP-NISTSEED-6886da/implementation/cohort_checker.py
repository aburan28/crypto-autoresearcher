#!/usr/bin/env python3
"""Independent fail-closed checker for future one-index ECPP observations.

This module does not import cohort_runner.  It independently rehashes every
frozen input, reconstructs the 21-row source/corpus mapping, recomputes serial
framing/body/certificate extraction, and checks custody before any accepted
censored or admitted result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPAT = ROOT / "research/nist_seed_ecpp_compat_20261024"
DATA = COMPAT / ".work/build-v4/ECPP/Ecpp/Data"
sys.path.insert(0, str(COMPAT))
from certificate_admission import admit, parse
from guest_framing import valid_frame

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

LIMITS = {"emulated_cpus": 1, "vm_ram_mib": 256, "child_address_space_mib": 128, "prover_guest_seconds": 300, "prover_host_seconds": 390, "checker_guest_seconds": 30, "checker_host_seconds": 90}
PRIMARY = {"serial": True, "full_original_data": True, "proving": True, "n_minus_1": True, "n_plus_1": True, "distributed": False, "debug": False, "fresh_vm": True, "fresh_process_rng": "original ModInitialize: srandom(1)"}
SUPERVISOR_FILES = {"launch.json", "environment.json", "command.txt", "stdout.log", "stderr.log"}
PRIOR_BOOLEANS = ("on_curve", "n_prime_pari", "n_times_point_identity", "order_certified", "n_in_hasse_interval", "hasse_interval_narrower_than_n")


class CheckFailure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise CheckFailure(message)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        fail(f"not a regular non-symlink file: {path}")
    return digest(path.read_bytes())


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"invalid JSON {path}: {error}")


def integer(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        try:
            return int(value, 0)
        except ValueError:
            pass
    fail(f"invalid integer encoding: {value!r}")


def canonical_digest(value: Any) -> str:
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def frozen() -> dict[str, str]:
    answer: dict[str, str] = {}
    for relative, expected in FROZEN.items():
        observed = sha(ROOT / relative)
        if observed != expected:
            fail(f"frozen input digest mismatch: {relative}")
        answer[relative] = observed
    return answer


def inputs() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cohort = load(COMPAT / "cohort-inputs.json")
    rows = cohort.get("rows")
    if not isinstance(rows, list) or len(rows) != 21 or len({row.get("curve_uid") for row in rows if isinstance(row, dict)}) != 21:
        fail("frozen cohort identity mismatch")
    if sum(row.get("label") == "omitted" for row in rows) != 11 or sum(row.get("label") == "published" for row in rows) != 10:
        fail("frozen cohort label mismatch")
    return rows, load(COMPAT / "runtime-bindings.json")


def independent_prior_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    assessed = load(ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json")
    traits = load(ROOT / "research/nist_seed_skipped_curves_20261016/traits.json")
    omitted = assessed.get("candidate_rows")
    published = traits.get("published_controls")
    if not isinstance(omitted, list) or len(omitted) != 11 or not isinstance(published, dict) or len(published) != 10:
        fail("canonical source collection mismatch")
    sources: dict[str, tuple[str, dict[str, Any]]] = {}
    for label, records in (("omitted", omitted), ("published", list(published.values()))):
        for record in records:
            identity = record.get("identity", {}) if isinstance(record, dict) else {}
            uid = identity.get("curve_uid")
            if not isinstance(uid, str) or uid in sources:
                fail("duplicate or malformed canonical provenance UID")
            sources[uid] = (label, record)
    corpus = [json.loads(line) for line in (ROOT / "research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl").read_text(encoding="utf-8").splitlines() if line]
    answer: dict[str, dict[str, Any]] = {}
    for row in rows:
        selected = sources.get(row["curve_uid"])
        if selected is None:
            fail("missing canonical provenance row")
        label, source = selected
        identity = source["identity"]
        curve = identity["curve"]
        field = identity["field"]
        if label != row["label"] or identity.get("curve_id") != row["curve_id"]:
            fail("canonical label/curve identity mismatch")
        if integer(field.get("characteristic")) != integer(row["p"]) or integer(curve.get("subgroup_order")) != integer(row["n"]) or curve.get("cofactor") != 1:
            fail("canonical p/n/cofactor mismatch")
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
            fail("full p/n/b/seed/index/run corpus mapping is missing or ambiguous")
        record = matches[0]
        if not all(record.get(key) is True for key in PRIOR_BOOLEANS):
            fail("prior certificate booleans are incomplete")
        answer[row["curve_uid"]] = {
            "label": label,
            "curve_id": row["curve_id"],
            "p": str(integer(row["p"])),
            "n": str(integer(row["n"])),
            "a4": str(integer(curve["a4"])),
            "a6": str(integer(curve["a6"])),
            "b": str(b),
            "cofactor": 1,
            "corpus_side": record["side"],
            "corpus_record_sha256": canonical_digest(record),
            "provenance_record_sha256": canonical_digest(source),
            "prior_booleans": {key: True for key in PRIOR_BOOLEANS},
        }
    if len(answer) != 21:
        fail("incomplete prior map")
    return answer


def serial_parts(serial: bytes) -> tuple[bytes, bytes, list[bytes]]:
    normalized = serial.replace(b"\r\n", b"\n").decode("utf-8", "replace").encode("utf-8")
    begin = b"__ECPP_GUEST_BEGIN__\n"
    exit_marker = b"\n__ECPP_CHILD_EXIT__"
    if normalized.count(begin) != 1 or normalized.count(b"__ECPP_CHILD_EXIT__ ") != 1 or normalized.count(b"__ECPP_GUEST_COMPLETE__\n") != 1:
        fail("guest serial sentinel count mismatch")
    if begin not in normalized or exit_marker not in normalized:
        fail("guest serial body delimiter mismatch")
    body = normalized.split(begin, 1)[1].split(exit_marker, 1)[0]
    certificates = re.findall(rb"__ECPP_CERTIFICATE_BEGIN__\n(.*?)\n__ECPP_CERTIFICATE_END__", normalized, re.S)
    return normalized, body, certificates


def strict_trace(serial: bytes) -> dict[str, Any]:
    raw = (DATA / "ecpp.DfD").read_bytes()
    catalog: dict[int, list[dict[str, Any]]] = {}
    grammar = re.compile(rb"^\(\((?P<factors>[0-9 ]*)\) (?P<d>-?[0-9]+) (?P<sign>-?[0-9]+)\)\r?$", re.M)
    for ordinal, match in enumerate(grammar.finditer(raw)):
        value = int(match.group("d"))
        catalog.setdefault(value, []).append({
            "file": "ecpp.DfD",
            "record": ordinal,
            "byte_offset": match.start("d"),
            "line": raw.count(b"\n", 0, match.start("d")) + 1,
            "factors": [factor.decode("ascii") for factor in match.group("factors").split()],
            "class_number_sign_code": int(match.group("sign")),
        })
    if 0 not in catalog or 1 in catalog:
        fail("DfD catalog special-route mismatch")
    patterns = (("phase", re.compile(rb"^% Starting phase (?:1: building the sequence of primes|2: proving)$")), ("proving_job", re.compile(rb"^% Starting proving job for step ([0-9]+)$")), ("recursive_N", re.compile(rb"^% N_([0-9]+)=([0-9]+)$")), ("recursive_status", re.compile(rb"^% N_([0-9]+) is (prime|not prime)$")), ("retry", re.compile(rb"^%!% Forced to retry, snif\.\.\.$")), ("catalog_D", re.compile(rb"^% next D is (-?[0-9]+)$")), ("stored_D", re.compile(rb"^% D\[\[([0-9]+)\]\]=(-?[0-9]+)$")), ("proving_route", re.compile(rb"^% (?:No N-1 test|No N\+1 test|Cofactor is 1)$")))
    events: list[dict[str, Any]] = []
    for item in re.finditer(rb"[^\n]*(?:\n|$)", serial):
        raw_line = item.group(0)
        if not raw_line:
            continue
        line = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
        if line.endswith(b"\r"):
            line = line[:-1]
        for kind, expression in patterns:
            match = expression.match(line)
            if match is None:
                continue
            event: dict[str, Any] = {"kind": kind, "printed": True, "source_offset": item.start(), "raw_utf8": line.decode("utf-8", "replace"), "raw_hex": line.hex()}
            values = [value.decode("ascii") for value in match.groups()]
            if kind in {"catalog_D", "stored_D"}:
                value = int(values[-1])
                event.update(value=value, index=int(values[0]) if kind == "stored_D" else None, catalog_positions=catalog.get(value, []), special_route="D=1 has no ecpp.DfD record; source switches D<=1 to route -1 or 1" if value == 1 else None)
            else:
                event["value"] = values or None
            events.append(event)
            break
        else:
            if line.startswith(b"%"):
                events.append({"kind": "unknown_marker", "printed": True, "source_offset": item.start(), "raw_utf8": line.decode("utf-8", "replace"), "raw_hex": line.hex()})
    return {"schema": "trace_schema.json", "raw_serial_sha256": digest(serial), "events": events, "unprinted_state": "UNOBSERVED", "inference_prohibited": "unprinted branches are not reconstructed as attempted"}


def inventory(raw: dict[str, Any], output: Path) -> dict[str, Path]:
    declared = raw.get("driver_artifacts")
    if not isinstance(declared, dict):
        fail("missing driver artifact inventory")
    root = output / "legacy-child"
    if not root.exists():
        if declared:
            fail("inventory claims an absent child directory")
        return {}
    if not root.is_dir() or root.is_symlink():
        fail("unsafe child directory")
    actual: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            fail("symlink in driver-owned inventory")
        if path.is_dir():
            continue
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            fail("unsafe driver-owned artifact")
        actual[path.relative_to(root).as_posix()] = path
    if set(actual) != set(declared):
        fail("raw artifact inventory is not exact")
    for relative, path in actual.items():
        if sha(path) != declared[relative]:
            fail(f"raw artifact digest mismatch: {relative}")
    return actual


def require_status(artifacts: dict[str, Path], prefix: str, serial: bytes, observation: dict[str, Any]) -> tuple[dict[str, Any], bytes, list[bytes]]:
    required = {f"{prefix}/started.json", f"{prefix}/result.json", f"{prefix}/serial.raw", f"{prefix}/qemu.stderr", f"{prefix}/program.stdout"}
    if not required <= set(artifacts):
        fail(f"{prefix} completion lacks required raw artifacts")
    result = load(artifacts[f"{prefix}/result.json"])
    observed = observation.get(prefix)
    if not isinstance(observed, dict):
        fail(f"observation lacks {prefix} status")
    primitives = ("qemu_exit", "child_exit", "reason", "elapsed_host_seconds", "serial_sha256", "certificate_count")
    for key in primitives:
        if observed.get(key) != result.get(key):
            fail(f"observation/{prefix} primitive status mismatch: {key}")
    if result.get("serial_sha256") != digest(serial):
        fail(f"{prefix} retained serial digest mismatch")
    normalized, body, certificates = serial_parts(serial)
    if result.get("certificate_count") != len(certificates):
        fail(f"{prefix} certificate sentinel count mismatch")
    if artifacts[f"{prefix}/program.stdout"].read_bytes() != body:
        fail(f"{prefix} program.stdout does not equal serial-extracted body")
    expected_vm_valid = valid_frame(result.get("qemu_exit"), serial, result.get("reason"))
    if observed.get("vm_valid") is not expected_vm_valid:
        fail(f"observation/{prefix} strengthened vm_valid mismatch")
    return result, body, certificates


def check(output: Path) -> dict[str, Any]:
    raw = load(output / "raw-result.json")
    observation = load(output / "observation.json")
    if raw.get("schema") != "crypto.autoresearch.nistseed_ecpp_raw_result.v5":
        fail("raw schema mismatch")
    frozen_digests = frozen()
    rows, runtime = inputs()
    index = raw.get("cohort_index")
    if type(index) is not int or not 0 <= index < 21:
        fail("cohort index mismatch")
    row = rows[index]
    if raw.get("curve") != row or observation.get("curve_uid") != row["curve_uid"]:
        fail("cohort row identity mismatch")
    if raw.get("frozen_input_sha256") != frozen_digests or raw.get("runtime_payloads") != runtime.get("artifacts") or raw.get("kernel") != runtime.get("kernel") or raw.get("original_data") != runtime.get("original_data"):
        fail("frozen/runtime/catalog/kernel/payload binding mismatch")
    if raw.get("limits") != LIMITS or raw.get("primary_configuration") != PRIMARY or raw.get("named_orders_executed") != 1:
        fail("fixed configuration or future single-index count mismatch")
    copied = output / "input-binding-manifest.json"
    if not copied.is_file() or copied.is_symlink() or raw.get("input_binding_manifest_sha256") != sha(copied):
        fail("copied binding manifest missing or mutated")
    binding = load(copied)
    if binding.get("cohort_index") != index or Path(binding.get("output_directory", "")).resolve() != output.resolve() or binding.get("frozen_input_sha256") != frozen_digests or binding.get("limits") != LIMITS or binding.get("primary_configuration") != PRIMARY:
        fail("copied binding manifest contents mismatch")
    for name in SUPERVISOR_FILES:
        if raw.get("supervisor_artifact_sha256", {}).get(name) != sha(output / name):
            fail(f"supervisor identity mismatch: {name}")
    launch = load(output / "launch.json")
    argv = json.loads((output / "command.txt").read_text(encoding="utf-8"))
    if launch.get("argv") != argv or str(index) not in argv or str(output) not in argv or raw.get("supervisor_manifest") != binding:
        fail("supervisor argv/manifest mismatch")
    expected_map = independent_prior_map(rows)
    if raw.get("prior_primality_mapping") != expected_map or observation.get("prior_primality_evidence") != expected_map[row["curve_uid"]]:
        fail("independent full 21-row prior mapping mismatch")
    artifacts = inventory(raw, output)
    classification = raw.get("classification")
    if classification not in {"INDETERMINATE", "PRIOR_PRIMALITY_EVIDENCE_REQUIRED"} or raw.get("censoring") != (classification == "INDETERMINATE") or observation.get("mathematical_classification") != classification:
        fail("classification/censoring mismatch")
    if observation.get("stage") == "bound_before_legacy_start":
        if artifacts or observation.get("legacy_execution_started") is not False or not (output / "failure.json").is_file():
            fail("early censored exception has inconsistent custody")
        return {"accepted": True, "classification": "INDETERMINATE", "censored_stage": "bound_before_legacy_start"}
    serial = artifacts.get("prover/serial.raw")
    if serial is None:
        fail("prover serial absent")
    prover, prover_body, certificates = require_status(artifacts, "prover", serial.read_bytes(), observation)
    prover_started = load(artifacts["prover/started.json"])
    payload_digest = digest((row["n"] + "\n").encode("ascii"))
    artifact_digests = {Path(item["logical_path"]).name: item["sha256"] for item in runtime["artifacts"]}
    if prover_started.get("input_sha256") != payload_digest or prover_started.get("program_sha256") != artifact_digests.get("runecpp") or prover_started.get("init_sha256") != artifact_digests.get("qemu-init") or prover_started.get("data_mode") != "full" or prover_started.get("guest_limit_seconds") != LIMITS["prover_guest_seconds"] or prover_started.get("host_limit_seconds") != LIMITS["prover_host_seconds"]:
        fail("prover fixed input/program/init/catalog/limits mismatch")
    if prover_started.get("initramfs_sha256") is None or not re.fullmatch(r"[0-9a-f]{64}", str(prover_started["initramfs_sha256"])):
        fail("prover initramfs digest absent or malformed; frozen bindings do not expose a fixed per-run image digest")
    labels = [item.decode("ascii") for item in re.findall(rb"^(?:% )?This number is (prime|composite)\b", prover_body, re.M)]
    if observation.get("legacy_labels_observation_only") != labels or observation.get("trace") != strict_trace(serial.read_bytes()) or observation.get("prover_body_sha256") != digest(prover_body) or observation.get("prover_certificate_count") != len(certificates):
        fail("prover serial-derived labels, trace, body, or certificate count mismatch")
    if observation.get("stage") == "partial_prover_observed" or not valid_frame(prover.get("qemu_exit"), serial.read_bytes(), prover.get("reason")) or prover.get("child_exit") != 0:
        if classification != "INDETERMINATE" or not (output / "failure.json").is_file():
            fail("censored prover stage mismatch")
        return {"accepted": True, "classification": "INDETERMINATE", "censored_stage": observation.get("stage")}
    if observation.get("certificate_admitted") is not True:
        if classification != "INDETERMINATE":
            fail("non-admitted observation must be censored")
        return {"accepted": True, "classification": "INDETERMINATE", "censored_stage": "admission"}
    if len(certificates) != 1 or "prover/certificate.cformat" not in artifacts or artifacts["prover/certificate.cformat"].read_bytes() != certificates[0]:
        fail("certificate raw file/sentinel mismatch")
    checker_serial = artifacts.get("checker/serial.raw")
    if checker_serial is None:
        fail("admitted observation lacks checker serial")
    checker_status, checker_body, checker_certificates = require_status(artifacts, "checker", checker_serial.read_bytes(), observation)
    if checker_certificates:
        fail("checker serial unexpectedly contains certificate envelope")
    certificate = certificates[0]
    checker_started = load(artifacts["checker/started.json"])
    if checker_started.get("input_sha256") != digest(certificate) or checker_started.get("program_sha256") != artifact_digests.get("checkcertif") or checker_started.get("init_sha256") != artifact_digests.get("qemu-init") or checker_started.get("guest_limit_seconds") != LIMITS["checker_guest_seconds"] or checker_started.get("host_limit_seconds") != LIMITS["checker_host_seconds"]:
        fail("checker fixed input/program/init/limits mismatch")
    if labels != ["prime"]:
        fail("admitted certificate conflicts with retained legacy labels")
    try:
        steps = parse(certificate, integer(row["n"]))
    except (ValueError, UnicodeError) as error:
        fail(f"certificate root/grammar mismatch: {error}")
    if not admit({**checker_status, "vm_valid": True}, checker_body, certificate, integer(row["n"])):
        fail("raw checker serial body reports rejection")
    if observation.get("certificate_steps") != steps or observation.get("certificate_sha256") != digest(certificate) or classification != "PRIOR_PRIMALITY_EVIDENCE_REQUIRED":
        fail("certificate steps/digest/classification mismatch")
    return {"accepted": True, "classification": classification, "legacy_certificate_component": "bounded legacy grammar/root/step component; not an independent general primality verifier"}


def aa_compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    required = {"fixture", "trace", "prover", "checker", "certificate", "classification", "labels", "runtime"}
    for value in (left, right):
        if not isinstance(value, dict) or set(value) != required or not isinstance(value.get("fixture"), dict):
            fail("A/A fixture schema incomplete")
        fixture = value["fixture"]
        if set(fixture) != {"id", "public_input"} or not isinstance(fixture["id"], str) or any(key in fixture for key in ("curve_uid", "n", "p")):
            fail("A/A fixture must be a complete non-cohort public fixture")
    incidental = {"elapsed_host_seconds", "started_at", "finished_at", "output_directory", "temporary_path"}
    def normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items() if key not in incidental}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        return value
    if normalize(left) != normalize(right):
        fail("A/A semantic mismatch")
    return {"mode": "A/A", "equal": True, "scope": "non-cohort engineering reproducibility control only; not an independent curve or cohort order"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--aa-left", type=Path)
    parser.add_argument("--aa-right", type=Path)
    args = parser.parse_args()
    if args.aa_left or args.aa_right:
        if not args.aa_left or not args.aa_right:
            raise SystemExit("A/A requires both fixture paths")
        result = aa_compare(load(args.aa_left), load(args.aa_right))
    elif args.output is not None:
        result = check(args.output)
    else:
        raise SystemExit("--output is required outside A/A mode")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
