#!/usr/bin/env python3
"""Postprocess the sealed f50061 collection once; never launch a solver or retry.

Nine unchanged source-A public verifier slices precede the frozen C3 analysis,
export adapter and official export checker. Invalid, partial and empty streams
remain evidence; a missing report is explicitly not_run, never a passing report.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time

PROTOCOL_FILE_SHA = "37d2ee070c0b1463bbf2f080b04b6093c028ac43a772705d04a0f4d871992bc9"
PROTOCOL_SHA = "f882380374559faae1b50d86c1583c06c36738fc5dce43d2861fadaa6204b812"
SOURCE_A = "fe01ccd832832488c58abeef17548b0a8db6035f"
SOURCE_B = "de6ed88850fc8bad17ccbabfad8b66a791e478e5"
SOURCE_C = "14a97265c647e9abe4ad3f21d1b9822f1ab5c8b3"
INPUT_SHA = "080d635cd1528274d3b04901a688b8ddbfa30c5f63f87b09ed10970456f7e293"
OLD_PROTOCOL_SHA = "c2c74431575058b141bc6a49dda895e87f59a2ea2c77b9db6635960ad7c480b1"
BINARY_SHA = "0eb981311b4dd0de7da9faf51178d1d97759d48a54e4c143f2f9d44ef31d8c48"
SOURCE_MANIFEST_SHA = "9c800f5da616dca940f8e6a99a7a8c99fc1589a303f8849a0cb915943624881f"
NONCE = "59f6175a5869c64a540ec15d00e7d44b9e112ea16ba13f03821130e42bf55a32"
PREFIX = "harness/classical_ecdlp_parameter_sweep"
OLD_PREFIX = "harness/classical_ecdlp_endpoint_reuse"
PINS = {
    OLD_PREFIX + "/verification/verify_public.py": "0021862570f96616914dd5e8d3865eded2b1f89dab72acd8beaac6d9d899d9d8",
    OLD_PREFIX + "/cohort/public_inputs.py": "2577dd4568efd53e4b74150e5b8b0f0a5767d240d471f0110e0b1d178b750829",
    OLD_PREFIX + "/modal/receipts-b2/build-info.json": "9ffd564779ee543fcd064727087940e853abf8f6ecb18929a2344ae9bc7545b1",
    PREFIX + "/analysis.py": "dd803967f4f5d7cb4b573cce09c884f734d47230203bf98c3d04a7185c42771f",
    PREFIX + "/export.py": "e28ecf58492c3ac09c4f4f552dde0e8cb555895d45da3d3b0f5dc3af545705d3",
    PREFIX + "/source-manifest.json": SOURCE_MANIFEST_SHA,
    "tools/experiment_protocol.py": "0f46a2b856bb1df2d155c4a676b46c6118d82c45cf8e5cc0492315aeb45c84e4",
}
VARIANTS = ("dpminus1_cap1", "dpminus1_cap2", "dp0_cap1", "dp0_cap2", "dp0_cap4",
            "dpplus1_cap1", "dpplus1_cap2", "dpplus1_cap4", "shared")
BL_ARMS = ("static_small", "static_full", "static_filled", "harvest", "harvest_disabled")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def write_json(path, obj):
    with Path(path).open("x") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def locate_raw(path):
    path = Path(path).resolve()
    if path.is_file():
        need(path.name == "algorithm-raw-manifest.json", "expected raw manifest filename")
        return path
    candidates = [path / relative / "algorithm-raw-manifest.json" for relative in
                  (".", "raw", "tree/raw", "collected/tree/raw", "modal/collected/tree/raw")]
    found = {p.resolve() for p in candidates if p.is_file()}
    need(len(found) == 1, "expected exactly one raw manifest in bounded collection locations")
    return found.pop()


def member(root, logical):
    rel = PurePosixPath(logical)
    need(not rel.is_absolute() and ".." not in rel.parts and str(rel) == logical,
         "unsafe raw member: " + str(logical))
    path = root / logical
    need(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), "raw member escapes tree")
    return path


def checked_member(root, item):
    path = member(root, item["path"])
    need(path.is_file() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"],
         "raw member bytes/hash differ: " + str(path))
    return path.resolve()


def stream_parts(root, files, logical):
    """Return original bytes or all exact lossless parts, never selected rows."""
    if logical is None or logical not in files:
        return []
    item = files[logical]
    if member(root, logical).is_file():
        return [checked_member(root, item)]
    parts = sorted((v for k, v in files.items() if k.startswith(logical + ".parts/")),
                   key=lambda x: x["path"])
    need(parts, "logical raw stream has neither original nor parts: " + logical)
    digest, size, paths = hashlib.sha256(), 0, []
    for part in parts:
        path = checked_member(root, part)
        paths.append(path)
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1048576), b""):
                digest.update(block)
                size += len(block)
    need(size == item["bytes"] and digest.hexdigest() == item["sha256"], "logical parts do not reproduce original")
    return paths


def invoke(label, command, out, cwd):
    started = time.time()
    write_json(out / (label + ".invocation.json"), {"argv": command, "cwd": str(cwd),
               "attempts": 1, "automatic_retry": False, "started_unix_seconds": started})
    stdout, stderr = out / (label + ".stdout.txt"), out / (label + ".stderr.txt")
    with stdout.open("xb") as so, stderr.open("xb") as se:
        process = subprocess.run(command, cwd=cwd, stdout=so, stderr=se, check=False)
    record = {"argv": command, "returncode": process.returncode, "attempts": 1,
              "automatic_retry": False, "started_unix_seconds": started,
              "finished_unix_seconds": time.time(), "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)}
    write_json(out / (label + ".result.json"), record)
    return record


def public_targets(repo, public_root, out, fixtures):
    path = repo / OLD_PREFIX / "cohort/public_inputs.py"
    spec = importlib.util.spec_from_file_location("_postrun_original_public_inputs", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    cohort = module.load_inputs(public_root, INPUT_SHA)
    need(cohort.protocol_sha256 == OLD_PROTOCOL_SHA and cohort.nonce_hex == NONCE, "wrong original public cohort identity")
    manifest = read_json(public_root / "inputs-manifest.json")
    need(sha(fixtures) == sha(public_root / manifest["fixture_path"]), "collected fixture panel differs from original public cohort")
    tm = read_json(public_root / manifest["targets_manifest_path"])
    targets = out / "runtime-targets.tsv"
    # Preserve exactly the original declared target-part order and original row bytes.
    with targets.open("xb") as target:
        target.write(module.table_bytes(module.TARGET_COLUMNS, []))
        for part in tm["parts"]:
            target.write(module.public_path(public_root, part["path"]).read_bytes().split(b"\n", 1)[1])
    need(targets.stat().st_size == tm["logical_bytes"] and sha(targets) == tm["logical_sha256"],
         "assembled global public target bytes differ from original logical hash")
    return targets.resolve()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("/workspace/classical-ecdlp-validation-ready"))
    parser.add_argument("--collected", required=True, type=Path, help="Actual run directory, collected tree/raw directory or raw-manifest path")
    parser.add_argument("--public-root", required=True, type=Path, help="Unchanged original sealed public cohort directory")
    parser.add_argument("--out", required=True, type=Path, help="Fresh directory outside the sealed collection")
    parser.add_argument("--export-id", required=True)
    parser.add_argument("--verifier-workers", type=int, default=4, choices=range(1, 10))
    args = parser.parse_args()
    repo, out, public_root = args.repo_root.resolve(), args.out.resolve(), args.public_root.resolve()
    need(not out.exists(), "fresh postrun output directory required")
    protocol_path = repo / "experiments/EXP-ECDLP-f50061/protocol.json"
    need(sha(protocol_path) == PROTOCOL_FILE_SHA, "protocol exact bytes differ from frozen final source")
    protocol = read_json(protocol_path)
    body = {k: v for k, v in protocol.items() if k != "freeze"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    need(protocol["freeze"]["protocol_sha256"] == PROTOCOL_SHA and hashlib.sha256(canonical).hexdigest() == PROTOCOL_SHA,
         "frozen protocol body differs")
    for name, digest in PINS.items():
        path = repo / name
        need(not path.is_symlink() and sha(path) == digest, "source pin differs: " + name)
    build_info = read_json(repo / OLD_PREFIX / "modal/receipts-b2/build-info.json")
    need(build_info["source_revision"] == SOURCE_A and
         build_info["source_and_public_input_sha256"]["verification/verify_public.py"] == PINS[OLD_PREFIX + "/verification/verify_public.py"],
         "verifier is not the original image/source-A verifier")
    manifest_path = locate_raw(args.collected)
    root, manifest = manifest_path.parent, read_json(manifest_path)
    need(not out.is_relative_to(root.parent), "postrun output must be outside sealed collected tree")
    need(manifest.get("schema") == "classical.ecdlp.parameter-sweep.raw-manifest/v1", "wrong raw schema")
    for key, expected in {"protocol_sha256": PROTOCOL_SHA, "source_revision": SOURCE_A,
        "source_b_revision": SOURCE_B, "source_c_revision": SOURCE_C, "binary_sha256": BINARY_SHA,
        "inputs_manifest_sha256": INPUT_SHA, "source_input_protocol_sha256": OLD_PROTOCOL_SHA}.items():
        need(manifest.get(key) == expected, "raw source/protocol/input identity differs: " + key)
    files = {}
    for item in manifest["files"]:
        member(root, item["path"])
        need(item["path"] not in files, "duplicate raw manifest member")
        files[item["path"]] = item
    for logical, digest in (("launch-protocol-bytes.json", PROTOCOL_FILE_SHA),
                            ("launch-source-manifest-bytes.json", SOURCE_MANIFEST_SHA),
                            ("source-public-inputs-manifest.json", INPUT_SHA)):
        need(sha(checked_member(root, files[logical])) == digest, "launch bytes binding differs: " + logical)
    # The unchanged B2 transport seals only after supervisor-observed quiescence.
    seal = read_json(root.parent / "output-manifest.json")
    cleanup_path = root.parent / "process-cleanup.json"
    need(seal.get("schema") == "classical.ecdlp.endpoint-reuse.modal-output-manifest/v1" and
         seal.get("study_uid1000_quiescent") is True and
         seal.get("process_cleanup_sha256") == sha(cleanup_path) and read_json(cleanup_path).get("quiescent") is True,
         "collected output lacks recorded process quiescence")
    sealed_raw = [e for e in seal["files"] if e["path"] == "raw/algorithm-raw-manifest.json"]
    need(len(sealed_raw) == 1 and sealed_raw[0]["sha256"] == sha(manifest_path) and
         sealed_raw[0]["bytes"] == manifest_path.stat().st_size, "raw manifest differs from sealed transport member")
    fixtures = checked_member(root, files["panels/fixtures.tsv"])
    need(len(manifest["groups"]) == 5248, "all planned slots, including missing attempts, must remain indexed")
    out.mkdir(parents=True)
    write_json(out / "preflight.json", {"schema": "classical.ecdlp.parameter-sweep.postrun-preflight/v1",
        "raw_manifest": str(manifest_path), "raw_manifest_sha256": sha(manifest_path), "protocol_sha256": PROTOCOL_SHA,
        "protocol_file_sha256": PROTOCOL_FILE_SHA, "source_a": SOURCE_A, "source_b": SOURCE_B, "source_c": SOURCE_C,
        "source_pins": PINS, "script_sha256": sha(__file__), "scientific_solver_launches": 0,
        "automatic_retry": False, "all_clocks_wall_valid": False})
    targets = public_targets(repo, public_root, out, fixtures)
    verifier = repo / OLD_PREFIX / "verification/verify_public.py"

    def verify_slice(variant):
        settings = checked_member(root, files["panels/" + variant + "/settings.tsv"])
        arms = ("rho_reference",) if variant == "shared" else BL_ARMS
        groups = [g for g in manifest["groups"] if g["variant"] == variant]
        need(len(groups) == 128 * len(arms) and all(g["arm"] in arms for g in groups), "wrong slice schedule")
        records = []
        # Include every retained, hash-bound stream regardless of child outcome.
        # Unresolved mutable streams excluded by the engine remain explicitly absent.
        for group in groups:
            records.extend(stream_parts(root, files, group.get("raw")))
        need(len(records) == len(set(records)), "duplicate verifier raw path")
        write_json(out / ("slice-" + variant + ".json"), {"variant": variant, "planned_slots": len(groups),
            "raw_paths": [str(p) for p in records], "groups_without_hash_bound_stream": [g for g in groups if g.get("raw") not in files],
            "child_status_counts": dict(sorted(Counter(g["status"] for g in groups).items())), "no_outcome_filter": True})
        if not records:
            return {"variant": variant, "summary": None, "status": "not_run", "reason": "No retained hash-bound raw stream exists for this slice."}
        summary_dir = out / ("verification-" + variant)
        command = [sys.executable, str(verifier), "--fixtures", str(fixtures), "--targets", str(targets),
                   "--settings", str(settings), "--out", str(summary_dir)]
        for arm in arms:
            command += ["--expect-arm", arm]
        for path in records:
            command += ["--records", str(path)]
        result = invoke("verify-" + variant, command, out, repo)
        summary = summary_dir / "summary.json"
        if not summary.is_file():
            return {"variant": variant, "summary": None, "status": "not_run",
                    "reason": "Verifier was invoked once and exited %s without creating summary.json; see invocation and stream logs." % result["returncode"]}
        return {"variant": variant, "summary": str(summary.resolve()), "sha256": sha(summary),
                "observed_returncode": result["returncode"]}

    with ThreadPoolExecutor(max_workers=args.verifier_workers) as pool:
        slices = list(pool.map(verify_slice, VARIANTS))
    index = out / "verification-index.json"
    write_json(index, {"schema": "classical.ecdlp.parameter-sweep.verification-index/v1", "groups": slices})
    common = ["--protocol", str(protocol_path), "--raw-manifest", str(manifest_path),
              "--verification-index", str(index), "--targets", str(targets), "--external-nonce", NONCE]
    analysis_result = invoke("analysis", [sys.executable, str(repo / PREFIX / "analysis.py"), *common,
                                         "--out", str(out / "analysis")], out, repo)
    export_path = out / "export.json"
    export_command = [sys.executable, str(repo / PREFIX / "export.py"), "--repo-root", str(repo),
                      *common, "--export-id", args.export_id, "--out", str(export_path)]
    analysis_summary = out / "analysis/summary.json"
    if analysis_summary.is_file():
        export_command += ["--analysis-summary", str(analysis_summary)]
    export_result = invoke("export", export_command, out, repo)
    standard = None
    if export_path.is_file():
        standard = invoke("check-export", [sys.executable, str(repo / "tools/experiment_protocol.py"),
            "check-export", str(export_path), "--protocol", str(protocol_path), "--verify-files"], out, repo)
    succeeded = (all(s.get("observed_returncode") == 0 for s in slices) and analysis_result["returncode"] == 0
                 and export_result["returncode"] == 0 and standard is not None and standard["returncode"] == 0)
    write_json(out / "postrun-result.json", {"schema": "classical.ecdlp.parameter-sweep.postrun/v1",
        "operational_pipeline_status": "completed" if succeeded else "findings_or_failure",
        "verification_index_sha256": sha(index), "verifier_slices": slices,
        "analysis_returncode": analysis_result["returncode"], "export_returncode": export_result["returncode"],
        "standard_check_export_returncode": standard["returncode"] if standard else None,
        "export_sha256": sha(export_path) if export_path.is_file() else None,
        "scientific_validity": "not_assessed", "native_counter_replay_verified": False,
        "all_clocks_wall_valid": False, "scientific_solver_launches": 0, "automatic_retry": False})
    print(json.dumps({"out": str(out), "pipeline_passed": succeeded, "scientific_validity": "not_assessed"}))
    return 0 if succeeded else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "postrun_refused_or_failed", "error_type": type(error).__name__, "error": str(error)}), file=sys.stderr)
        raise SystemExit(2)
