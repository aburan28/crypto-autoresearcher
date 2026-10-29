#!/usr/bin/env python3
"""Zero-run producer for the future ``public-prime101-default`` A/A control.

``build_pair`` deliberately has no command-line entry point.  A future approved
launcher may inject the one real legacy boundary; this task exercises only an
in-process fake which writes the same retained raw-artifact layout.  In
particular, neither this module nor its tests call the cohort runner/case,
QEMU, Docker, a subprocess, or an artifact-store operation.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COMPAT = ROOT / "research/nist_seed_ecpp_compat_20261024"
DATA_ROOT = COMPAT / ".work/build-v4/ECPP/Ecpp/Data"
RUNTIME_ROOT = COMPAT / ".work/qemu-runtime"
COHORT_CHECKER = ROOT / "experiments/EXP-NISTSEED-6886da/implementation/cohort_checker.py"
sys.path.insert(0, str(COMPAT))
from certificate_admission import admit, parse  # noqa: E402
from guest_framing import valid_frame  # noqa: E402

FIXTURE = {"id": "public-prime101-default", "public_input": "101\n"}
PRIMARY = {
    "argv": ["/program", "-l", "/ecpp/", "-f", "/input", "-Fc", "-C", "/tmp/certificate"],
    "checker_argv": ["/program", "-f", "/input"], "full_original_catalog": True,
    "original_factor_parameters": True, "proving": True, "n_minus_1": True,
    "n_plus_1": True, "distributed": False, "debug": False,
    "fresh_process_rng": "original ModInitialize: srandom(1)", "fresh_vm_per_control": True,
}
LIMITS = {"emulated_cpus": 1, "vm_ram_mib": 256, "child_address_space_mib": 128,
          "prover_guest_seconds": 300, "prover_host_seconds": 390,
          "checker_guest_seconds": 30, "checker_host_seconds": 90}
BOUND_SOURCES = {
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
RAW_REQUIRED = {"started.json", "result.json", "serial.raw", "qemu.stderr", "program.stdout"}
PROVER_REQUIRED = RAW_REQUIRED | {"certificate.cformat"}
QEMU = "/opt/homebrew/bin/qemu-system-i386"


class Refusal(RuntimeError):
    """A fail-closed A/A admission refusal, never a scientific result."""


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file_sha(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise Refusal(f"required regular file missing: {path}")
    return _sha(path.read_bytes())


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refusal(f"invalid JSON: {path}: {error}") from error


def _runtime_inventory() -> tuple[dict[str, Any], dict[str, str]]:
    """Rehash hydrated payloads, kernel, and every original Data byte.

    The binding manifest supplies payload byte paths so the future launcher can
    use artifact-store's existing *read* interface without a store mutation.
    """
    binding = _json(COMPAT / "runtime-bindings.json")
    payloads: dict[str, str] = {}
    for item in binding.get("artifacts", []):
        logical = item.get("logical_path")
        expected = item.get("sha256")
        if not isinstance(logical, str) or not isinstance(expected, str):
            raise Refusal("runtime payload binding is malformed")
        candidate = ROOT / logical
        # ``read_bytes`` resolves a locally hydrated gzip/pointer and verifies
        # its content digest; it performs no upload and this task never asks it
        # to fetch a missing object.
        tools_dir = str(ROOT / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        import artifact_store
        observed = _sha(_local_payload_bytes(candidate, artifact_store))
        if observed != expected:
            raise Refusal(f"runtime payload digest mismatch: {logical}")
        payloads[logical] = observed
    kernel = binding.get("kernel", {})
    kernel_path = RUNTIME_ROOT / "vmlinuz-lts"
    if _file_sha(kernel_path) != kernel.get("kernel_sha256"):
        raise Refusal("kernel digest mismatch")
    original: dict[str, str] = {}
    for relative, expected in binding.get("original_data", {}).items():
        observed = _file_sha(DATA_ROOT / relative)
        if observed != expected:
            raise Refusal(f"original Data digest mismatch: {relative}")
        original[relative] = observed
    if not original:
        raise Refusal("empty original Data inventory")
    return binding, {**payloads, "kernel": _file_sha(kernel_path), **{f"Data/{k}": v for k, v in original.items()}}


def _local_payload_bytes(candidate: Path, artifact_store: Any) -> bytes:
    """Read only a unique local raw or gzip form; pointers are a hard refusal.

    ``artifact_store.read_bytes`` would resolve pointer forms by calling
    ``fetch``.  Inspect all public storage forms first so this zero-run task
    never attempts a remote read, even accidentally.
    """
    forms = artifact_store.candidates(candidate)
    present = [path for path in forms if path.exists() or path.is_symlink()]
    if len(present) != 1:
        raise Refusal("runtime payload must have exactly one local stored form")
    stored = present[0]
    if stored.is_symlink() or not stored.is_file():
        raise Refusal("runtime payload stored form must be a local regular file")
    if stored.name.endswith(artifact_store.POINTER):
        raise Refusal("runtime payload pointer form is forbidden: no fetch/retry")
    if stored not in (candidate, candidate.with_name(candidate.name + artifact_store.GZ)):
        raise Refusal("runtime payload stored form is not raw or gzip")
    return artifact_store.read_bytes(candidate)


def _verify_binding(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise Refusal("binding manifest must be a regular file")
    manifest = _json(path)
    if (manifest.get("schema") != "crypto.autoresearch.nistseed_aa_binding.v1"
            or manifest.get("fixture") != FIXTURE or manifest.get("primary_configuration") != PRIMARY
            or manifest.get("limits") != LIMITS or manifest.get("bound_sources") != BOUND_SOURCES):
        raise Refusal("binding manifest fixture/configuration/source identity mismatch")
    for relative, expected in BOUND_SOURCES.items():
        if _file_sha(ROOT / relative) != expected:
            raise Refusal(f"bound source digest mismatch: {relative}")
    runtime, rehashed = _runtime_inventory()
    if manifest.get("runtime_bindings") != runtime or manifest.get("rehash_inventory") != rehashed:
        raise Refusal("runtime/kernel/original-Data binding mismatch")
    return manifest


def _fresh(path: Path) -> None:
    if path.exists() or path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise Refusal(f"destination is not a distinct fresh regular-directory target: {path}")


def _load_aa_compare() -> Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]:
    spec = importlib.util.spec_from_file_location("nistseed_real_cohort_checker", COHORT_CHECKER)
    if spec is None or spec.loader is None:
        raise Refusal("cannot load archived cohort_checker.aa_compare")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.aa_compare


def _raw_tree(control: Path, name: str) -> tuple[dict[str, Any], bytes, bytes, list[bytes], dict[str, str]]:
    root = control / "legacy-child" / name
    expected = PROVER_REQUIRED if name == "prover" else RAW_REQUIRED
    if root.is_symlink() or not root.is_dir() or {p.name for p in root.iterdir()} != expected:
        raise Refusal(f"{name} retained raw artifact set is incomplete")
    paths = {item: root / item for item in expected}
    digests = {f"{name}/{item}": _file_sha(path) for item, path in paths.items()}
    status = _json(paths["result.json"])
    raw_serial = paths["serial.raw"].read_bytes()
    serial = raw_serial.replace(b"\r\n", b"\n").decode("utf-8", "replace").encode("utf-8")
    begin, exit_marker = b"__ECPP_GUEST_BEGIN__\n", b"\n__ECPP_CHILD_EXIT__"
    if (serial.count(begin) != 1 or serial.count(b"__ECPP_CHILD_EXIT__ ") != 1
            or serial.count(b"__ECPP_GUEST_COMPLETE__\n") != 1 or exit_marker not in serial):
        raise Refusal(f"{name} raw serial has invalid body framing")
    body = serial.split(begin, 1)[1].split(exit_marker, 1)[0]
    if paths["program.stdout"].read_bytes() != body:
        raise Refusal(f"{name} program.stdout is not serial-derived")
    certificates = re.findall(rb"__ECPP_CERTIFICATE_BEGIN__\n(.*?)\n__ECPP_CERTIFICATE_END__", serial, re.S)
    if status.get("serial_sha256") != _sha(raw_serial) or status.get("certificate_count") != len(certificates):
        raise Refusal(f"{name} status/raw digest inconsistency")
    expected_vm_valid = valid_frame(status.get("qemu_exit"), raw_serial, status.get("reason"))
    if type(status.get("vm_valid")) is not bool or status["vm_valid"] is not expected_vm_valid:
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {name} vm_valid/raw framing inconsistency")
    if name == "prover" and (len(certificates) != 1 or paths["certificate.cformat"].read_bytes() != certificates[0]):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: prover certificate raw file/sentinel mismatch")
    if name == "checker" and certificates:
        raise Refusal("CONTROL_INVALID/INDETERMINATE: checker serial contains certificate")
    return status, raw_serial, body, certificates, digests


def _payload_hashes(manifest: dict[str, Any]) -> dict[str, str]:
    values = manifest["runtime_bindings"].get("artifacts")
    if not isinstance(values, list):
        raise Refusal("runtime artifacts binding is malformed")
    answer = {Path(item.get("logical_path", "")).name: item.get("sha256") for item in values if isinstance(item, dict)}
    if set(answer) != {"runecpp", "checkcertif", "qemu-init", "arithmetic_vectors_v3"} or not all(isinstance(value, str) for value in answer.values()):
        raise Refusal("runtime artifact identities are incomplete")
    return answer


def _started_identity(control: Path, name: str, started: dict[str, Any], *, program_sha256: str,
                      input_bytes: bytes, data_mode: str | None, guest_limit: int, host_limit: int,
                      kernel_sha256: str, init_sha256: str) -> dict[str, str]:
    cache = control / "runtime-cache"
    kernel = cache / "vmlinuz-lts"
    images = cache / "images"
    if kernel.is_symlink() or not kernel.is_file() or _file_sha(kernel) != kernel_sha256:
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {name} private kernel identity")
    initrd = started.get("initramfs_sha256")
    if not isinstance(initrd, str) or not re.fullmatch(r"[0-9a-f]{64}", initrd):
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {name} initrd digest")
    image = images / f"{initrd}.cpio.gz"
    if images.is_symlink() or not images.is_dir() or image.is_symlink() or not image.is_file() or _file_sha(image) != initrd:
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {name} private image-cache identity")
    expected_command = [QEMU, "-machine", "pc,accel=tcg", "-cpu", "max", "-m", "256", "-smp", "1",
                        "-nodefaults", "-no-user-config", "-display", "none", "-serial", "stdio",
                        "-monitor", "none", "-nic", "none", "-no-reboot",
                        "-device", "isa-debug-exit,iobase=0xf4,iosize=4", "-kernel", str(kernel),
                        "-initrd", str(image), "-append",
                        "console=ttyS0 rdinit=/init panic=1 loglevel=3 random.trust_cpu=on"]
    expected = {"command": expected_command, "program_sha256": program_sha256, "init_sha256": init_sha256,
                "input_sha256": _sha(input_bytes), "stdin_sha256": _sha(b""), "data_mode": data_mode,
                "guest_limit_seconds": guest_limit, "host_limit_seconds": host_limit}
    if any(started.get(key) != value for key, value in expected.items()):
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {name} started identity mismatch")
    return {"kernel": _file_sha(kernel), "initrd": _file_sha(image), "input": _sha(input_bytes)}


def _portable_started(started: dict[str, Any]) -> dict[str, Any]:
    """Keep source-derived semantic identity, not unique local output paths."""
    return {key: started[key] for key in ("program_sha256", "init_sha256", "input_sha256", "stdin_sha256",
                                          "data_mode", "guest_limit_seconds", "host_limit_seconds", "initramfs_sha256")}


def _derive(control: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    prover, pserial, pbody, certs, pdigests = _raw_tree(control, "prover")
    checker, cserial, cbody, checker_certs, cdigests = _raw_tree(control, "checker")
    if (not valid_frame(prover.get("qemu_exit"), pserial, prover.get("reason"))
            or prover.get("child_exit") != 0 or not valid_frame(checker.get("qemu_exit"), cserial, checker.get("reason"))
            or checker.get("child_exit") != 0):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: framing, timeout, crash, or exit status")
    labels = [item.decode("ascii") for item in re.findall(rb"^(?:% )?This number is (prime|composite)\b", pbody, re.M)]
    if labels != ["prime"] or len(certs) != 1 or checker_certs:
        raise Refusal("CONTROL_INVALID/INDETERMINATE: labels or certificate envelope")
    certificate = certs[0]
    try:
        steps = parse(certificate, 101)
    except (ValueError, UnicodeError) as error:
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: certificate grammar/root: {error}") from error
    if not steps or steps[0].get("n") != 101 or not admit({**checker, "vm_valid": True}, cbody, certificate, 101):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: checker rejected certificate")
    input_path = control / "input" / "public-input.dec"
    certificate_path = control / "certificate" / "certificate.cformat"
    if _file_sha(input_path) != _sha(b"101\n"):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: retained public input bytes")
    certificate_path.parent.mkdir(mode=0o700)
    certificate_path.write_bytes(certificate)
    if _file_sha(certificate_path) != _sha(certificate):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: retained certificate bytes")
    custody_path = control / "custody" / "raw-artifact-sha256.json"
    custody_path.parent.mkdir(mode=0o700)
    custody = {**pdigests, **cdigests}
    custody_path.write_text(json.dumps(custody, sort_keys=True) + "\n", encoding="utf-8")
    if _json(custody_path) != custody:
        raise Refusal("CONTROL_INVALID/INDETERMINATE: retained raw artifact hashes")
    payloads, kernel = _payload_hashes(manifest), manifest["runtime_bindings"]["kernel"].get("kernel_sha256")
    if not isinstance(kernel, str):
        raise Refusal("CONTROL_INVALID/INDETERMINATE: bound kernel identity")
    pidentity = _started_identity(control, "prover", _json(control / "legacy-child/prover/started.json"),
                                  program_sha256=payloads["runecpp"], input_bytes=b"101\n", data_mode="full",
                                  guest_limit=LIMITS["prover_guest_seconds"], host_limit=LIMITS["prover_host_seconds"],
                                  kernel_sha256=kernel, init_sha256=payloads["qemu-init"])
    cidentity = _started_identity(control, "checker", _json(control / "legacy-child/checker/started.json"),
                                  program_sha256=payloads["checkcertif"], input_bytes=certificate, data_mode=None,
                                  guest_limit=LIMITS["checker_guest_seconds"], host_limit=LIMITS["checker_host_seconds"],
                                  kernel_sha256=kernel, init_sha256=payloads["qemu-init"])
    return {
        "fixture": FIXTURE,
        "trace": {"raw_prover_serial_sha256": _sha(pserial), "raw_checker_serial_sha256": _sha(cserial),
                  "unprinted_state": "UNOBSERVED"},
        "prover": {"status": prover, "body_sha256": _sha(pbody), "started": _portable_started(_json(control / "legacy-child/prover/started.json"))},
        "checker": {"status": checker, "body_sha256": _sha(cbody), "started": _portable_started(_json(control / "legacy-child/checker/started.json"))},
        "certificate": {"sha256": _sha(certificate), "root": 101, "step_count": len(steps)},
        "classification": "CONTROL_VALID",
        "labels": labels,
        "runtime": {"binding_manifest_sha256": _file_sha(control / "binding-manifest.json"),
                    "rehash_inventory": manifest["rehash_inventory"],
                    "retained_input_sha256": _file_sha(input_path), "retained_certificate_sha256": _file_sha(certificate_path),
                    "private_cache": {"prover": pidentity, "checker": cidentity}},
    }


def build_pair(left_output: Path, right_output: Path, binding_manifest: Path,
               legacy_boundary: Callable[[Path, Path], None] | None = None) -> dict[str, Any]:
    """Build and compare two fresh controls; the default real boundary is disabled.

    The caller must provide an explicitly approved future boundary.  Tests pass
    a non-subprocess writer of retained synthetic raw artifacts.
    """
    left, right, binding = Path(left_output), Path(right_output), Path(binding_manifest)
    if left.resolve(strict=False) == right.resolve(strict=False):
        raise Refusal("left and right destinations must be distinct")
    _fresh(left); _fresh(right)
    manifest = _verify_binding(binding)
    if legacy_boundary is None:
        raise Refusal("future real boundary is not authorized by this zero-run producer")
    docs: list[dict[str, Any]] = []
    for output in (left, right):
        output.mkdir(mode=0o700)
        shutil.copyfile(binding, output / "binding-manifest.json")
        (output / "runtime-cache/images").mkdir(parents=True, mode=0o700)
        (output / "input").mkdir(mode=0o700)
        (output / "input/public-input.dec").write_bytes(b"101\n")
        try:
            legacy_boundary(output, output / "runtime-cache")
            docs.append(_derive(output, manifest))
        except Exception as error:
            # Preserve the failure directory; equality is never attempted.
            raise Refusal(f"CONTROL_INVALID/INDETERMINATE: {error}") from error
    try:
        comparison = _load_aa_compare()(docs[0], docs[1])
    except Exception as error:
        raise Refusal(f"CONTROL_INVALID/INDETERMINATE: A/A equality refused: {error}") from error
    return {"comparison": comparison, "left": docs[0], "right": docs[1],
            "named_orders_executed": 0, "legacy_program_executed": False}
