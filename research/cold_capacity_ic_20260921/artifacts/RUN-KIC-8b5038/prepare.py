#!/usr/bin/env python3
"""Build, test, audit, and freeze implementation artifacts for RUN-KIC-8b5038."""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any, Iterable

import control_checker

RUN_ROOT = Path(__file__).resolve().parent
PACKAGE = RUN_ROOT.parents[1]
REPO = PACKAGE.parents[1]
PARENT_PACKAGE = REPO / "research/cold_single_ic_20260921"
PARENT_RUN = PARENT_PACKAGE / "artifacts/RUN-KIC-e3dbed"
PROTOCOL = PACKAGE / "protocol.json"
PROTOCOL_SHA256 = "54ecfb35441e976675cbfe99e5c343e47bef1d6779528cbf5c779d6585bb35bc"
PARENT_SOURCE_TAR = PARENT_RUN / "candidate_source.tar.gz"
PARENT_BINARIES_TAR = PARENT_RUN / "custody/binaries.tar.gz"
PARENT_DEPENDENCIES_TAR = PARENT_RUN / "custody/dependencies.tar.gz"
PARENT_LOCK = PARENT_RUN / "custody/Cargo.lock"
SOURCE_CANDIDATE = PACKAGE / "source_candidate"
TEST_BASELINE = PACKAGE / "source_test_baseline"
TEST_CANDIDATE = PACKAGE / "source_test_candidate"
BUILD_TARGET = RUN_ROOT / "build_candidate/target"
TEST_BASELINE_TARGET = RUN_ROOT / "test_baseline_target"
TEST_CANDIDATE_TARGET = RUN_ROOT / "test_candidate_target"
CUSTODY = RUN_ROOT / "custody"
BASELINE_BINARY = CUSTODY / "baseline/koblitz_rank_fixture"
RHO_BINARY = CUSTODY / "baseline/koblitz_rho_fixture"
CANDIDATE_BINARY = CUSTODY / "candidate/koblitz_rank_fixture"
PARENT_RANK_SOURCE = CUSTODY / "parent_source/examples/koblitz_rank_fixture.rs"
EXPECTED_PARENT_SOURCE_TAR = "f81487998d9fead4428deb2b583a8d787529413b8f6233141b3247f91b26b7cb"
EXPECTED_PARENT_DIRECT = "8ceefed466427e9a36d9bd50880ff0f5073b6d0e67a93325018416c646025fe2"
EXPECTED_PARENT_RHO = "e5a2fef13fc378d9b0eef31228211b4b24c989fcbc6bdad8437eb6c7c31cf450"
EXPECTED_LOCK = "ada8f10a2f770f9859bbca76e8740372be6b7050e9c7b8f665cc7e80ca8f4ed1"
EXPECTED_DEPS = "fb561512fdd5564803fa980ae8c0efb1a01b47f5227d615a5f63ad51709f7435"
R = 21044858204113
PERMUTATIONS = (
    ("baseline", "candidate", "rho"), ("baseline", "rho", "candidate"),
    ("candidate", "baseline", "rho"), ("candidate", "rho", "baseline"),
    ("rho", "baseline", "candidate"), ("rho", "candidate", "baseline"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest_value(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True, indent=2)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, path)


def source_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and "target" not in path.relative_to(root).parts and ".git" not in path.relative_to(root).parts)


def tree_manifest(root: Path) -> list[dict[str, Any]]:
    return [{"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)} for path in source_files(root)]


def normalized_tar(paths: Iterable[tuple[Path, str]], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    with temporary.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for path, arcname in sorted(paths, key=lambda item: item[1]):
                    info = archive.gettarinfo(str(path), arcname=arcname)
                    info.uid = info.gid = 0; info.uname = info.gname = ""; info.mtime = 0
                    with path.open("rb") as source:
                        archive.addfile(info, source)
        raw.flush(); os.fsync(raw.fileno())
    os.replace(temporary, destination)


def run_wait4(name: str, argv: list[str], cwd: Path, env: dict[str, str], stdout_path: Path, stderr_path: Path) -> dict[str, Any]:
    require(not stdout_path.exists() and not stderr_path.exists(), f"build log already exists for {name}")
    start = time.monotonic_ns()
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        process = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, close_fds=True)
        _, status, usage = os.wait4(process.pid, 0)
        reaped = time.monotonic_ns(); process.returncode = os.waitstatus_to_exitcode(status)
        stdout.flush(); stderr.flush(); os.fsync(stdout.fileno()); os.fsync(stderr.fileno())
    return {
        "name": name, "argv": argv, "cwd": str(cwd), "exit_code": process.returncode,
        "wall_seconds": (reaped - start) / 1e9, "user_cpu_seconds": usage.ru_utime,
        "system_cpu_seconds": usage.ru_stime, "wait4_ru_maxrss": usage.ru_maxrss,
        "wait4_ru_maxrss_unit": "bytes" if platform.system() == "Darwin" else "platform-dependent",
        "stdout": stdout_path.name, "stdout_sha256": sha256_file(stdout_path),
        "stderr": stderr_path.name, "stderr_sha256": sha256_file(stderr_path),
    }


def extract_parent_binaries() -> None:
    require(sha256_file(PARENT_BINARIES_TAR) == "65b84c5eb87fd1f0b544a6a78ed60b26baea2af2476eff410b9c69c8d0e2b4a1", "parent binaries tar changed")
    CUSTODY.mkdir(parents=True, exist_ok=True)
    with tarfile.open(PARENT_BINARIES_TAR, "r:gz") as archive:
        members = {
            "binaries/candidate/koblitz_rank_fixture": BASELINE_BINARY,
            "binaries/baseline/koblitz_rho_fixture": RHO_BINARY,
        }
        for member_name, destination in members.items():
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member_name)
            require(source is not None, f"parent binary missing: {member_name}")
            with destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            destination.chmod(0o755)
    require(sha256_file(BASELINE_BINARY) == EXPECTED_PARENT_DIRECT, "parent direct binary hash mismatch")
    require(sha256_file(RHO_BINARY) == EXPECTED_PARENT_RHO, "parent rho binary hash mismatch")


def extract_parent_rank_source() -> None:
    PARENT_RANK_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(PARENT_SOURCE_TAR, "r:gz") as archive:
        source = archive.extractfile("source_arm_allocation/examples/koblitz_rank_fixture.rs")
        require(source is not None, "parent rank source absent from immutable tar")
        with PARENT_RANK_SOURCE.open("wb") as output:
            shutil.copyfileobj(source, output)


def candidate_patch_bytes() -> bytes:
    left = PARENT_RANK_SOURCE
    right = SOURCE_CANDIDATE / "examples/koblitz_rank_fixture.rs"
    result = subprocess.run(["git", "diff", "--no-index", "--", str(left), str(right)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(result.returncode == 1, "candidate must differ from baseline")
    normalized = []
    for line in result.stdout.splitlines(keepends=True):
        if line.startswith(b"diff --git "):
            line = b"diff --git a/examples/koblitz_rank_fixture.rs b/examples/koblitz_rank_fixture.rs\n"
        elif line.startswith(b"--- "):
            line = b"--- a/examples/koblitz_rank_fixture.rs\n"
        elif line.startswith(b"+++ "):
            line = b"+++ b/examples/koblitz_rank_fixture.rs\n"
        normalized.append(line)
    return b"".join(normalized)


def parse_semantic_stdout(path: Path) -> dict[str, Any]:
    matches = []
    for line in path.read_text(errors="replace").splitlines():
        if "cold_capacity_semantic_control" not in line:
            continue
        start = line.find("{")
        if start >= 0:
            try:
                value = json.loads(line[start:])
            except json.JSONDecodeError:
                continue
            if value.get("kind") == "cold_capacity_semantic_control":
                matches.append(value)
    require(len(matches) == 1, f"expected one semantic-control JSON in {path}, found {len(matches)}")
    return matches[0]


def build() -> None:
    require(sha256_file(PROTOCOL) == PROTOCOL_SHA256, "protocol hash mismatch")
    require(sha256_file(PARENT_SOURCE_TAR) == EXPECTED_PARENT_SOURCE_TAR, "parent source tar mismatch")
    require(sha256_file(PARENT_LOCK) == EXPECTED_LOCK, "parent lock mismatch")
    require(sha256_file(PARENT_DEPENDENCIES_TAR) == EXPECTED_DEPS, "parent dependencies mismatch")
    for source in (SOURCE_CANDIDATE, TEST_BASELINE, TEST_CANDIDATE):
        require(source.is_dir(), f"source directory absent: {source}")
        require(sha256_file(source / "Cargo.lock") == EXPECTED_LOCK, f"source lock mismatch: {source}")
    extract_parent_binaries()
    extract_parent_rank_source()
    patch = candidate_patch_bytes()
    added_lines = [line for line in patch.splitlines() if line.startswith(b"+") and not line.startswith(b"+++")]
    require(added_lines == [b"+        let capacity = if x_only { capacity * 2 } else { capacity };"], "production delta is not the sole capacity expression")
    (RUN_ROOT / "candidate.patch").write_bytes(patch)
    normalized_tar([(path, f"source_candidate/{path.relative_to(SOURCE_CANDIDATE).as_posix()}") for path in source_files(SOURCE_CANDIDATE)], RUN_ROOT / "candidate_source.tar.gz")
    env = dict(os.environ)
    build_receipts = []
    candidate_env = {**env, "CARGO_TARGET_DIR": str(BUILD_TARGET)}
    build_receipts.append(run_wait4(
        "candidate_release_build",
        ["cargo", "build", "--offline", "--locked", "--release", "--jobs", "2", "--example", "koblitz_rank_fixture"],
        SOURCE_CANDIDATE, candidate_env, RUN_ROOT / "candidate_build.stdout", RUN_ROOT / "candidate_build.stderr",
    ))
    require(build_receipts[-1]["exit_code"] == 0, "candidate release build failed")
    built = BUILD_TARGET / "release/examples/koblitz_rank_fixture"
    CANDIDATE_BINARY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(built, CANDIDATE_BINARY); CANDIDATE_BINARY.chmod(0o755)
    baseline_test_env = {**env, "CARGO_TARGET_DIR": str(TEST_BASELINE_TARGET)}
    candidate_test_env = {**env, "CARGO_TARGET_DIR": str(TEST_CANDIDATE_TARGET)}
    test_name = "cold_capacity_semantic_control_tests::n13_signed_expanded_x_domain_and_witnesses_are_exact"
    build_receipts.append(run_wait4(
        "baseline_structural_control",
        ["cargo", "test", "--offline", "--locked", "--release", "--jobs", "2", "--example", "koblitz_rank_fixture", test_name, "--", "--nocapture"],
        TEST_BASELINE, baseline_test_env, RUN_ROOT / "baseline_test.stdout", RUN_ROOT / "baseline_test.stderr",
    ))
    build_receipts.append(run_wait4(
        "candidate_full_tests",
        ["cargo", "test", "--offline", "--locked", "--release", "--jobs", "2", "--example", "koblitz_rank_fixture", "--", "--nocapture"],
        TEST_CANDIDATE, candidate_test_env, RUN_ROOT / "candidate_test.stdout", RUN_ROOT / "candidate_test.stderr",
    ))
    require(all(receipt["exit_code"] == 0 for receipt in build_receipts), "test build/control failed")
    baseline_semantic = parse_semantic_stdout(RUN_ROOT / "baseline_test.stdout")
    candidate_semantic = parse_semantic_stdout(RUN_ROOT / "candidate_test.stdout")
    semantic = {
        "schema": "crypto.autoresearch.cold_capacity_semantic_controls.v1",
        "method": "cfg(test)-only exhaustive n13 x-domain and returned-witness group checks; excluded from release sources",
        "baseline": baseline_semantic,
        "candidate": candidate_semantic,
        "test_source_sha256": {
            "baseline": sha256_file(TEST_BASELINE / "examples/koblitz_rank_fixture.rs"),
            "candidate": sha256_file(TEST_CANDIDATE / "examples/koblitz_rank_fixture.rs"),
        },
    }
    control_checker.validate_semantic_controls(semantic)
    semantic["valid"] = True
    atomic_json(RUN_ROOT / "semantic_controls.json", semantic)
    atomic_json(RUN_ROOT / "build_execution.json", {
        "schema": "crypto.autoresearch.cold_capacity_build_execution.v1",
        "recorded_at": utc_now(), "scope": "offline build and cfg(test) controls only; no solver process",
        "receipts": build_receipts,
        "candidate_binary_sha256": sha256_file(CANDIDATE_BINARY),
    })


def derive_case_manifest() -> dict[str, Any]:
    protocol = json.loads(PROTOCOL.read_text())
    parent_protocol = json.loads((PARENT_PACKAGE / "protocol.json").read_text())
    parent_scalars = set(parent_protocol["frozen_cases"]["calibration"]["scalars"] + parent_protocol["frozen_cases"]["heldout"]["scalars"])
    cases, scalars = [], []
    ordinal = 0
    for index in range(1, 25):
        case_label = f"CSIC53-CAPACITY-v1-case-{index:02d}"
        scalar = 1 + int.from_bytes(hashlib.sha256(case_label.encode()).digest(), "little") % (R - 1)
        direct_label = f"CSIC53-CAPACITY-v1-direct-seed-{index:02d}"
        rho_label = f"CSIC53-CAPACITY-v1-rho-seed-{index:02d}"
        direct_seed = int.from_bytes(hashlib.sha256(direct_label.encode()).digest()[:8], "little")
        rho_seed = int.from_bytes(hashlib.sha256(rho_label.encode()).digest()[:8], "little")
        order = PERMUTATIONS[(index - 1) % 6]
        scalars.append(scalar)
        for position, arm in enumerate(order, 1):
            ordinal += 1
            cases.append({
                "ordinal": ordinal, "case_index": index, "position": position, "arm": arm,
                "id": f"case-{index:02d}-p{position}-{arm}", "scalar_label": case_label, "scalar": scalar,
                "seed_label": rho_label if arm == "rho" else direct_label,
                "seed": rho_seed if arm == "rho" else direct_seed,
                "eta_denominator": None if arm == "rho" else 256,
                "factor_base_k": None if arm == "rho" else 75,
            })
    require(len(set(scalars)) == 24, "derived scalars are not distinct")
    require(not (set(scalars) & parent_scalars), "derived scalars overlap parent")
    position_counts = {arm: [sum(row["arm"] == arm and row["position"] == position for row in cases) for position in (1, 2, 3)] for arm in ("baseline", "candidate", "rho")}
    require(all(counts == [8, 8, 8] for counts in position_counts.values()), "position balance failed")
    return {
        "schema": "crypto.autoresearch.cold_capacity_case_manifest.v1", "experiment_id": "RUN-KIC-8b5038",
        "protocol_sha256": PROTOCOL_SHA256, "cases": cases, "scalars": scalars,
        "freshness": {"pairwise_distinct": True, "parent_disjoint": True, "parent_scalar_count": len(parent_scalars)},
        "counts": {"targets": 24, "children": 72, "per_arm": 24}, "position_counts": position_counts,
        "derivation_digest": digest_value({"scalars": scalars, "cases": cases}),
        "protocol_order_digest": digest_value(protocol["frozen_targets_and_order"]),
    }


def git_blob_matches_head(path: Path) -> bool:
    relative = path.relative_to(REPO).as_posix()
    result = subprocess.run(["git", "show", f"HEAD:{relative}"], cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.returncode == 0 and result.stdout == path.read_bytes()


def freeze() -> None:
    acceptance = PACKAGE / "parent_review_acceptance.json"
    require(acceptance.is_file() and git_blob_matches_head(acceptance), "committed parent acceptance absent")
    acceptance_record = json.loads(acceptance.read_text())
    require(acceptance_record.get("status") == "parent_prerequisite_satisfied", "parent acceptance status not accepted")
    required_code = [RUN_ROOT / name for name in ("runner.py", "analyze.py", "prepare.py", "control_checker.py")]
    for path in required_code + [RUN_ROOT / "semantic_controls.json", RUN_ROOT / "build_execution.json", CANDIDATE_BINARY, BASELINE_BINARY, RHO_BINARY]:
        require(path.is_file(), f"freeze input absent: {path}")
    extract_parent_rank_source()
    corrected_patch = candidate_patch_bytes()
    added_lines = [line for line in corrected_patch.splitlines() if line.startswith(b"+") and not line.startswith(b"+++")]
    removed_lines = [line for line in corrected_patch.splitlines() if line.startswith(b"-") and not line.startswith(b"---")]
    require(added_lines == [b"+        let capacity = if x_only { capacity * 2 } else { capacity };"] and not removed_lines, "corrected production diff is not the sole capacity addition")
    (RUN_ROOT / "candidate.patch").write_bytes(corrected_patch)
    atomic_json(RUN_ROOT / "case_manifest.json", derive_case_manifest())
    parent_review = json.loads((PARENT_PACKAGE / "review/report.json").read_text())
    atomic_json(RUN_ROOT / "parent_review_readback.json", {
        "schema": "crypto.autoresearch.parent_review_readback.v1", "accepted": True,
        "acceptance_path": acceptance.relative_to(REPO).as_posix(), "acceptance_sha256": sha256_file(acceptance),
        "parent_report_sha256": sha256_file(PARENT_PACKAGE / "review/report.json"),
        "parent_validation_id": parent_review["validation_report"]["id"],
        "read_boundary": "parent finite validation and committed Coordinator acceptance; no reuse of parent timings",
    })
    baseline_tree = tree_manifest(TEST_BASELINE)
    test_candidate_tree = tree_manifest(TEST_CANDIDATE)
    candidate_tree = tree_manifest(SOURCE_CANDIDATE)
    atomic_json(RUN_ROOT / "source_delta_audit.json", {
        "schema": "crypto.autoresearch.cold_capacity_source_delta_audit.v1", "valid": True,
        "parent_source_tar_sha256": sha256_file(PARENT_SOURCE_TAR), "candidate_patch_sha256": sha256_file(RUN_ROOT / "candidate.patch"),
        "production_changed_paths": ["examples/koblitz_rank_fixture.rs"],
        "functional_delta": "capacity is doubled only when x_only=true; filter_bits continues to use original expected",
        "test_harness_scope": "identical cfg(test)-only appendix in separate test copies; absent from production baseline/candidate",
        "forbidden_changes_found": [],
    })
    atomic_json(RUN_ROOT / "source_closure.json", {
        "schema": "crypto.autoresearch.cold_capacity_source_closure.v1", "protocol_sha256": PROTOCOL_SHA256,
        "parent": {"source_tar_sha256": sha256_file(PARENT_SOURCE_TAR), "baseline_binary_sha256": sha256_file(BASELINE_BINARY),
                   "rho_binary_sha256": sha256_file(RHO_BINARY), "cargo_lock_sha256": sha256_file(PARENT_LOCK),
                   "dependencies_tar_sha256": sha256_file(PARENT_DEPENDENCIES_TAR)},
        "candidate": {"source_files": len(candidate_tree), "source_bytes": sum(row["bytes"] for row in candidate_tree),
                      "tree_digest": digest_value(candidate_tree), "source_tar_sha256": sha256_file(RUN_ROOT / "candidate_source.tar.gz"),
                      "binary_sha256": sha256_file(CANDIDATE_BINARY)},
        "test_baseline_tree_digest": digest_value(baseline_tree),
        "test_candidate_tree_digest": digest_value(test_candidate_tree),
        "test_source_files": {"baseline": len(baseline_tree), "candidate": len(test_candidate_tree)},
    })
    tools = {}
    for name, argv in {"rustc": ["rustc", "--version", "--verbose"], "cargo": ["cargo", "--version", "--verbose"], "uname": ["uname", "-a"], "sw_vers": ["sw_vers"]}.items():
        result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        tools[name] = {"argv": argv, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    build_execution = json.loads((RUN_ROOT / "build_execution.json").read_text())
    atomic_json(RUN_ROOT / "build_toolchain.json", {
        "schema": "crypto.autoresearch.cold_capacity_build_toolchain.v1", "tools": tools,
        "build_execution_sha256": sha256_file(RUN_ROOT / "build_execution.json"), "build_receipts": build_execution["receipts"],
        "host": {"platform": platform.platform(), "machine": platform.machine(), "python": sys.version},
    })
    code_hashes = {path.name: sha256_file(path) for path in required_code}
    atomic_json(RUN_ROOT / "analyzer_closure.json", {
        "schema": "crypto.autoresearch.cold_capacity_analyzer_closure.v1",
        "code_sha256": code_hashes, "bootstrap_seed": "CSIC53-CAPACITY-BOOT-v1", "bootstrap_resamples": 10000,
        "primary_arm": "candidate", "control_arms": ["baseline", "rho"], "no_selection": True,
    })
    atomic_json(RUN_ROOT / "runner_preflight.json", {
        "schema": "crypto.autoresearch.cold_capacity_runner_preflight.v1", "status": "READY_FOR_UNTIMED_CONTROLS_ONLY",
        "protocol_sha256": PROTOCOL_SHA256, "code_sha256": code_hashes,
        "case_manifest_sha256": sha256_file(RUN_ROOT / "case_manifest.json"),
        "source_closure_sha256": sha256_file(RUN_ROOT / "source_closure.json"),
        "source_delta_audit_sha256": sha256_file(RUN_ROOT / "source_delta_audit.json"),
        "semantic_controls_sha256": sha256_file(RUN_ROOT / "semantic_controls.json"),
        "analyzer_closure_sha256": sha256_file(RUN_ROOT / "analyzer_closure.json"),
        "parent_review_readback_sha256": sha256_file(RUN_ROOT / "parent_review_readback.json"),
        "binary_sha256": {"baseline": sha256_file(BASELINE_BINARY), "candidate": sha256_file(CANDIDATE_BINARY), "rho": sha256_file(RHO_BINARY)},
        "science_hold": "explicit committed measurement admission plus explicit root sole-launch assignment still required",
        "model": {"resolved_model_id": "gpt-5.6-sol", "reasoning_effort": "high", "fallback_used": False,
                  "degraded_requirements": [], "model_verified": False, "note": "static adapter resolution; no serving probe"},
    })


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--phase", choices=("build", "freeze"), required=True); args = parser.parse_args()
    build() if args.phase == "build" else freeze()


if __name__ == "__main__":
    main()
