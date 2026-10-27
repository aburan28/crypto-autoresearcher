"""Deferred, fail-closed producer for the public fixed101 A/A control.

Imports and pure initramfs reconstruction do not start a VM or legacy program.
The only execution seam is ``default_legacy_boundary``, selected only by an
explicit later ``build_pair`` call with no injected boundary.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPAT = ROOT / "research/nist_seed_ecpp_compat_20261024"
RUNTIME = COMPAT / ".work/qemu-runtime"
DATA = COMPAT / ".work/build-v4/ECPP/Ecpp/Data"
FIXTURE = {"id": "public-prime101-default", "public_input": "101\n"}
INPUT = b"101\n"
LIMITS = {"emulated_cpus": 1, "vm_ram_mib": 256, "child_address_space_mib": 128,
          "prover_guest_seconds": 300, "prover_host_seconds": 390,
          "checker_guest_seconds": 30, "checker_host_seconds": 90}
PRIMARY = {"argv": ["/program", "-l", "/ecpp/", "-f", "/input", "-Fc", "-C", "/tmp/certificate"],
           "checker_argv": ["/program", "-f", "/input"], "full_original_catalog": True,
           "original_factor_parameters": True, "proving": True, "n_minus_1": True,
           "n_plus_1": True, "distributed": False, "debug": False,
           "fresh_process_rng": "original ModInitialize: srandom(1)", "fresh_vm_per_control": True}
SOURCE_HASHES = {
 "experiments/EXP-NISTSEED-6886da/implementation/cohort_runner.py": "b507cb49161238315f7294328699379b4ee2a7c19a3cf0d01bfc6f01e788e6ec",
 "experiments/EXP-NISTSEED-6886da/implementation/cohort_checker.py": "79a242bb44699888e85ac2774d606c4bc2700f65de4c296dc96df31eee02ef9a",
 "research/nist_seed_ecpp_compat_20261024/cohort_case.py": "55450647dcbfc0dd9ba37525eb876164341d7af1dc8256dece019a9b4d00e8d2",
 "research/nist_seed_ecpp_compat_20261024/qemu_controls.py": "255b415ebf5a8eaa5514a02fbd0fb9886f27a2065f8686586a2c336e9f9372e7",
 "research/nist_seed_ecpp_compat_20261024/certificate_admission.py": "6cf50c95da246c7033dbb2cda8f8d70c07e2d5e366c1f1c9f163e7b115740c68",
 "research/nist_seed_ecpp_compat_20261024/guest_framing.py": "ce4f7a8b320826c09d9b947d306883d83b695b83ebfc496ec1d3e38ca6a76bf5",
 "tools/artifact_store.py": "8518bbbd385b077f6bf5344503ebe9c0feb8f0b3bb119e8e8a7deea8f461be59",
 "research/nist_seed_ecpp_compat_20261024/runtime-bindings.json": "53363f256e28c5e3d5b579e9c1b4f8230ed107d20988c1e4584899c0edc5d6ae",
 "research/nist_seed_ecpp_compat_20261024/COHORT_PROTOCOL_DRAFT.md": "271cfe4936ef0e536508fe93583d79d840b1740dc0eeb2416e3901e21d582b93",
 "coordination/goals/GOAL-NISTSEED-ab8949/batches/BATCH-08d006/artifact-store-push-v1.json": "6338713169a0fc8919ebbe7c5f301d089221f2a8089f1d8bfccf1d2843785bf5",
}
_PURE_IMAGE_CACHE: dict[tuple[str, tuple[str, ...], bytes, str | None, int], bytes] = {}

class Refusal(RuntimeError):
    pass

def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

def read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise Refusal(f"nonregular or absent input: {path}")
    return path.read_bytes()

def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read(path).decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise Refusal(f"invalid JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise Refusal(f"JSON object required: {path}")
    return value

def resolved(path: Path) -> Path:
    candidate = path.absolute()
    for ancestor in (candidate, *candidate.parents):
        if ancestor.is_symlink():
            raise Refusal(f"symlink output ancestor: {ancestor}")
    return candidate.resolve(strict=False)

def fresh_pair(left: Path, right: Path) -> tuple[Path, Path]:
    left, right = resolved(left), resolved(right)
    if left == right or left.is_relative_to(right) or right.is_relative_to(left):
        raise Refusal("outputs are equal, nested, or aliased")
    if left.exists() or right.exists():
        raise Refusal("output directories must be nonexistent")
    return left, right

def qemu_helper():
    spec = importlib.util.spec_from_file_location("aa_frozen_qemu", COMPAT / "qemu_controls.py")
    if spec is None or spec.loader is None:
        raise Refusal("cannot load frozen qemu helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def certificate_helper():
    spec = importlib.util.spec_from_file_location("aa_certificate", COMPAT / "certificate_admission.py")
    if spec is None or spec.loader is None:
        raise Refusal("cannot load certificate helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def binding(manifest: Path) -> dict[str, Any]:
    value = load(manifest)
    if value.get("fixture") != FIXTURE or value.get("limits") != LIMITS:
        raise Refusal("fixed fixture or limits mismatch")
    if value.get("primary_configuration") != PRIMARY or value.get("input_bindings") != SOURCE_HASHES:
        raise Refusal("fixed configuration or source bindings mismatch")
    for relative, expected in SOURCE_HASHES.items():
        if sha(read(ROOT / relative)) != expected:
            raise Refusal(f"source digest mismatch: {relative}")
    runtime = load(COMPAT / "runtime-bindings.json")
    if value.get("runtime") != runtime:
        raise Refusal("runtime binding mismatch")
    for item in runtime["artifacts"]:
        payload = read(ROOT / item["logical_path"])
        if len(payload) != item["bytes"] or sha(payload) != item["sha256"]:
            raise Refusal(f"payload mismatch: {item['logical_path']}")
    if sha(read(RUNTIME / "vmlinuz-lts")) != runtime["kernel"]["kernel_sha256"]:
        raise Refusal("kernel mismatch")
    observed = {path.relative_to(DATA).as_posix(): sha(read(path)) for path in DATA.rglob("*") if path.is_file()}
    if observed != runtime["original_data"]:
        raise Refusal("original Data inventory mismatch")
    return {**value, "_manifest_sha256": sha(read(manifest))}

def exact_inventory(root: Path) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise Refusal("missing or unsafe raw root")
    answer = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            raise Refusal(f"symlink in raw custody: {path}")
        if path.is_file():
            answer[path.relative_to(root).as_posix()] = sha(read(path))
        elif not path.is_dir():
            raise Refusal(f"unsafe raw entry: {path}")
    return answer

def frame(serial: bytes) -> tuple[bytes, list[bytes]]:
    normalized = serial.replace(b"\r\n", b"\n")
    begin, done, init = b"__ECPP_GUEST_BEGIN__\n", b"__ECPP_GUEST_COMPLETE__\n", b"__ECPP_INIT_ABI__ 4 4 4\n"
    exits = list(re.finditer(rb"^__ECPP_CHILD_EXIT__ (\d+) timeout=(\d+)$", normalized, re.M))
    if normalized.count(begin) != 1 or normalized.count(done) != 1 or normalized.count(init) != 1:
        raise Refusal("incomplete framing markers")
    if len(exits) != 1 or exits[0].group(1) != b"0" or exits[0].group(2) != b"0":
        raise Refusal("invalid or duplicate child exit")
    start, stop, complete = normalized.index(begin) + len(begin), exits[0].start(), normalized.index(done)
    if not start <= stop < complete or normalized[stop - 1:stop] != b"\n" or normalized[complete - 1:complete] != b"\n":
        raise Refusal("misordered or incomplete frame")
    certificates = re.findall(rb"__ECPP_CERTIFICATE_BEGIN__\n(.*?)\n__ECPP_CERTIFICATE_END__", normalized, re.S)
    if normalized.count(b"__ECPP_CERTIFICATE_BEGIN__") != normalized.count(b"__ECPP_CERTIFICATE_END__"):
        raise Refusal("certificate sentinel mismatch")
    if len(certificates) != normalized.count(b"__ECPP_CERTIFICATE_BEGIN__"):
        raise Refusal("malformed certificate envelope")
    return normalized[start:stop - 1], certificates

def semantic_events(body: bytes) -> list[dict[str, str]]:
    events = []
    for line in body.splitlines():
        # The real public101 output also has a "% ==> Total time" footer.
        # Remove only explicit elapsed-time fields; retain unknown event text.
        if re.fullmatch(rb"% (?:Time for (?:building|proof\[\d+\]|proving|this number)\s+is|Total time is|==> Total time for the computations is)\s+\d+(?:\.\d+)?\s*s", line):
            continue
        checker = re.fullmatch(rb"\s*(\d+):\s*(-?\d+)\s+([01])(?:\s+\d+(?:\.\d+)?s)?\s*", line)
        if checker:
            line = b" ".join(checker.groups())
        if line.startswith(b"%") or checker or b"This number is " in line:
            events.append({"raw_hex": line.hex()})
    return events

def stage_expectation(output: Path, cache: Path, runtime: dict[str, Any], name: str, payload: bytes) -> dict[str, Any]:
    artifacts = {Path(item["logical_path"]).name: read(ROOT / item["logical_path"]) for item in runtime["artifacts"]}
    if name == "prover":
        program, arguments, data_mode, guest, host = "runecpp", PRIMARY["argv"][1:], "full", 300, 390
    else:
        program, arguments, data_mode, guest, host = "checkcertif", PRIMARY["checker_argv"][1:], None, 30, 90
    cache_key = (program, tuple(arguments), payload, data_mode, guest)
    image = _PURE_IMAGE_CACHE.get(cache_key)
    if image is None:
        image = qemu_helper().image(artifacts["qemu-init"], artifacts[program], arguments, payload, data_mode, guest, b"")
        _PURE_IMAGE_CACHE[cache_key] = image
    helper = qemu_helper()
    image_path = cache / "images" / (sha(image) + ".cpio.gz")
    command = [helper.QEMU, "-machine", "pc,accel=tcg", "-cpu", "max", "-m", "256", "-smp", "1",
               "-nodefaults", "-no-user-config", "-display", "none", "-serial", "stdio", "-monitor", "none",
               "-nic", "none", "-no-reboot", "-device", "isa-debug-exit,iobase=0xf4,iosize=4",
               "-kernel", str(cache / "vmlinuz-lts"), "-initrd", str(image_path),
               "-append", "console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on"]
    return {"program": program, "image": image, "image_path": image_path, "command": command,
            "data_mode": data_mode, "guest": guest, "host": host, "artifacts": artifacts}

def check_private_cache(output: Path, runtime: dict[str, Any], stages: list[dict[str, Any]]) -> None:
    cache = output / "runtime-cache"
    if cache.is_symlink() or not cache.is_dir() or sha(read(cache / "vmlinuz-lts")) != runtime["kernel"]["kernel_sha256"]:
        raise Refusal("private kernel cache mismatch")
    images = cache / "images"
    expected = {stage["image_path"].name: stage["image"] for stage in stages}
    actual = exact_inventory(images)
    if set(actual) != set(expected):
        raise Refusal("private image cache inventory mismatch")
    for name, image in expected.items():
        if sha(read(images / name)) != sha(image):
            raise Refusal("private image cache digest mismatch")

def check_started(started: dict[str, Any], status: dict[str, Any], expected: dict[str, Any]) -> None:
    if not isinstance(started.get("utc"), str) or not started["utc"]:
        raise Refusal("helper started UTC is absent")
    if started.get("command") != expected["command"] or started.get("program_sha256") != sha(expected["artifacts"][expected["program"]]):
        raise Refusal("helper command or program identity mismatch")
    if started.get("init_sha256") != sha(expected["artifacts"]["qemu-init"]) or started.get("initramfs_sha256") != sha(expected["image"]):
        raise Refusal("helper init or initramfs identity mismatch")
    if started.get("input_sha256") != sha(expected["payload"]) or started.get("stdin_sha256") != sha(b""):
        raise Refusal("helper input or stdin identity mismatch")
    if started.get("data_mode") != expected["data_mode"] or started.get("guest_limit_seconds") != expected["guest"] or started.get("host_limit_seconds") != expected["host"]:
        raise Refusal("helper data-mode or limit mismatch")
    elapsed = status.get("elapsed_host_seconds")
    if type(elapsed) not in (int, float) or isinstance(elapsed, bool) or not math.isfinite(elapsed) or elapsed < 0:
        raise Refusal("invalid elapsed host seconds")

def default_legacy_boundary(output: Path, cache: Path, payload: bytes, config: dict[str, Any]) -> None:
    """Original-default boundary for explicitly requested real controls."""
    sys.path.insert(0, str(COMPAT))
    import qemu_controls
    cache.mkdir(exist_ok=False)
    (cache / "images").mkdir()
    os.link(qemu_controls.RUNTIME / "vmlinuz-lts", cache / "vmlinuz-lts")
    original_runtime, qemu_controls.RUNTIME = qemu_controls.RUNTIME, cache
    try:
        blobs = {Path(item["logical_path"]).name: read(ROOT / item["logical_path"]) for item in config["runtime"]["artifacts"]}
        raw = output / "raw"
        raw.mkdir()
        (raw / "input.txt").write_bytes(payload)
        qemu_controls.vm(raw / "prover", blobs["qemu-init"], blobs["runecpp"], PRIMARY["argv"][1:], payload=payload, data_mode="full", cpu_limit=300, host_limit=390)
        certificate = raw / "prover/certificate.cformat"
        if certificate.is_file() and not certificate.is_symlink():
            qemu_controls.vm(raw / "checker", blobs["qemu-init"], blobs["checkcertif"], PRIMARY["checker_argv"][1:], payload=certificate.read_bytes(), cpu_limit=30, host_limit=90)
    finally:
        qemu_controls.RUNTIME = original_runtime

def document(output: Path, bound: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    raw = output / "raw"
    custody = exact_inventory(raw)
    required = {"input.txt", "prover/serial.raw", "prover/started.json", "prover/result.json", "prover/program.stdout", "prover/qemu.stderr", "prover/certificate.cformat", "checker/serial.raw", "checker/started.json", "checker/result.json", "checker/program.stdout", "checker/qemu.stderr"}
    if set(custody) != required or read(raw / "input.txt") != INPUT:
        raise Refusal("raw custody or fixed public input mismatch")
    prover_serial, checker_serial = read(raw / "prover/serial.raw"), read(raw / "checker/serial.raw")
    prover_body, certificates = frame(prover_serial)
    checker_body, checker_certificates = frame(checker_serial)
    prover, checker = load(raw / "prover/result.json"), load(raw / "checker/result.json")
    if len(certificates) != 1 or checker_certificates or read(raw / "prover/certificate.cformat") != certificates[0]:
        raise Refusal("certificate custody mismatch")
    if read(raw / "prover/program.stdout") != prover_body or read(raw / "checker/program.stdout") != checker_body:
        raise Refusal("framed program body mismatch")
    expected_status = ((prover, prover_serial, 1), (checker, checker_serial, 0))
    for status, serial, certificate_count in expected_status:
        if status.get("vm_valid") is not True or status.get("qemu_exit") != 33 or status.get("child_exit") != 0 or status.get("reason") is not None or status.get("serial_sha256") != sha(serial) or status.get("certificate_count") != certificate_count:
            raise Refusal("helper result/status mismatch")
    certificate = certificates[0]
    helper = certificate_helper()
    try:
        steps = helper.parse(certificate, 101)
    except (ValueError, UnicodeError) as error:
        raise Refusal(f"certificate grammar/root mismatch: {error}") from error
    if re.findall(rb"^(?:% )?This number is (prime|composite)\b", prover_body, re.M) != [b"prime"]:
        raise Refusal("prover labels are not exactly prime")
    if not helper.admit(checker, checker_body, certificate, 101):
        raise Refusal("checker raw body rejects certificate")
    cache = output / "runtime-cache"
    prover_expected = stage_expectation(output, cache, bound["runtime"], "prover", INPUT)
    checker_expected = stage_expectation(output, cache, bound["runtime"], "checker", certificate)
    prover_expected["payload"], checker_expected["payload"] = INPUT, certificate
    check_private_cache(output, bound["runtime"], [prover_expected, checker_expected])
    check_started(load(raw / "prover/started.json"), prover, prover_expected)
    check_started(load(raw / "checker/started.json"), checker, checker_expected)
    doc = {"fixture": FIXTURE, "trace": {"prover_events": semantic_events(prover_body), "checker_events": semantic_events(checker_body)},
           "prover": {key: prover[key] for key in ("qemu_exit", "child_exit", "reason", "elapsed_host_seconds")},
           "checker": {key: checker[key] for key in ("qemu_exit", "child_exit", "reason", "elapsed_host_seconds")},
           "certificate": {"root": 101, "steps": steps, "bytes_sha256": sha(certificate)},
           "classification": "PRIOR_PRIMALITY_EVIDENCE_REQUIRED", "labels": ["prime"],
           "runtime": {"binding_manifest_sha256": bound["_manifest_sha256"], "primary_configuration": PRIMARY, "limits": LIMITS}}
    return doc, custody

def archived_compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("aa_archived_checker", ROOT / "experiments/EXP-NISTSEED-6886da/implementation/cohort_checker.py")
    if spec is None or spec.loader is None:
        raise Refusal("cannot load archived A/A comparator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.aa_compare(left, right)

def build_pair(left_output: Path, right_output: Path, binding_manifest: Path, legacy_boundary: Callable[[Path, Path, bytes, dict[str, Any]], None] | None = None) -> dict[str, Any]:
    left, right = fresh_pair(Path(left_output), Path(right_output))
    bound = binding(Path(binding_manifest))
    boundary = default_legacy_boundary if legacy_boundary is None else legacy_boundary
    for output in (left, right):
        output.mkdir(parents=True)
        boundary(output, output / "runtime-cache", INPUT, {"fixture": FIXTURE, "limits": LIMITS, "primary_configuration": PRIMARY, "runtime": bound["runtime"]})
    left_document, left_custody = document(left, bound)
    right_document, right_custody = document(right, bound)
    return {"validity": "CONTROL_VALID", "aa": archived_compare(left_document, right_document), "left": left_document, "right": right_document, "raw_custody": {"left": left_custody, "right": right_custody}}
