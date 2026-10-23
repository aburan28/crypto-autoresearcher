"""Independently replay one completed graph arm and optional transport pair."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
ROOT = STUDY.parents[1]
PREPARED_CHECKER = STUDY / "preparation/verify_prepared_graph.py"
RANK_CHECKER = ROOT / "research/conductor_relation_yield_20261014/verify_collector.py"
WRAPPER = STUDY / "preparation/execute_graph_prepared.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def replay(command: list[str]) -> dict:
    return json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)


def canonical_collector(path: Path) -> list[str]:
    """Discard target scalars while retaining ordered per-target relations."""
    normalized = []
    for line in path.read_text().splitlines():
        fields = line.split("\t")
        if fields[0] == "target":
            if len(fields) != 7:
                raise ValueError("malformed collector target row")
            normalized.append("\t".join(fields[:2] + fields[4:]))
        else:
            normalized.append(line)
    return normalized


def check(run_dir: Path, input_path: Path, prepared_manifest: Path,
          admission: Path | None = None, control: bool = False,
          reference_run_dir: Path | None = None,
          collector: Path | None = None, count_verifier: Path | None = None) -> dict:
    run_dir, input_path, prepared_manifest = (path.resolve() for path in
                                             (run_dir, input_path, prepared_manifest))
    if control == (admission is not None):
        raise ValueError("control and admission modes differ")
    prepared = load(prepared_manifest)
    result = load(run_dir / "raw-result.json")
    manifest = load(run_dir / "manifest.yaml")
    attempt = run_dir / "attempt"
    receipt = load(attempt / "receipt.json")
    expected = "completed_control" if control else "completed_unreviewed"
    if any(record.get("status") != expected for record in (result, manifest, receipt)):
        raise ValueError("trial is incomplete")
    if (result.get("schema") != "ectd.graph-trial-result.v1" or
            manifest.get("schema") != "ectd.graph-trial-manifest.v1" or
            receipt.get("schema") != "ectd.graph-arm-execution-attempt.v1" or
            manifest.get("subprocess_return_code") != 0 or
            result.get("mode") != ("implementation_control" if control else "scientific_trial") or
            receipt.get("mode") != result["mode"]):
        raise ValueError("trial schema, mode or process result differs")
    if prepared.get("input_sha256") != sha(input_path):
        raise ValueError("prepared input differs")
    digests = result.get("digests", {})
    for name, path in (("input", input_path), ("prepared-manifest", prepared_manifest)):
        if digests.get(name + "_sha256") != sha(path) or name not in manifest["paths"]:
            raise ValueError(f"{name} binding differs")
    for name, override in (("collector", collector), ("count-verifier", count_verifier)):
        path = override or Path(manifest["paths"][name])
        if digests.get(name + "_sha256") != sha(path):
            raise ValueError(f"{name} binary differs")
    bindings = receipt.get("bindings", {})
    for key, value in (("input_sha256", sha(input_path)),
                       ("manifest_sha256", sha(prepared_manifest)),
                       ("collector_binary_sha256", digests["collector_sha256"]),
                       ("count_binary_sha256", digests["count-verifier_sha256"]),
                       ("wrapper_sha256", sha(WRAPPER))):
        if bindings.get(key) != value:
            raise ValueError(f"attempt {key} binding differs")
    if result.get("wrapper_sha256") != sha(WRAPPER):
        raise ValueError("wrapper source differs")
    if admission is not None:
        admission = admission.resolve()
        if ("admission" not in manifest["paths"] or
                digests.get("admission_sha256") != sha(admission) or
                receipt.get("admission_sha256") != sha(admission)):
            raise ValueError("admission binding differs")
        binding = load(admission)
        if (binding.get("status") != "approved" or
                any(binding.get(key) != value for key, value in receipt["bindings"].items())):
            raise ValueError("admission does not bind this attempt")
    elif "admission" in manifest["paths"] or receipt.get("admission_sha256") is not None:
        raise ValueError("control carries scientific admission")
    if (manifest.get("raw_result_sha256") != sha(run_dir / "raw-result.json") or
            manifest.get("attempt_receipt_sha256") != sha(attempt / "receipt.json") or
            result.get("attempt_receipt_sha256") != sha(attempt / "receipt.json") or
            manifest.get("driver_stdout_sha256") != sha(run_dir / "driver.stdout") or
            manifest.get("driver_stderr_sha256") != sha(run_dir / "driver.stderr")):
        raise ValueError("trial artifact digest differs")
    if result.get("prepared") != {key: prepared[key] for key in
                                  ("stratum", "index", "arm", "stage", "target_count")}:
        raise ValueError("prepared arm identity differs")
    phases = receipt.get("phases", [])
    if [phase.get("phase") for phase in phases] != ["input_verify", "collector", "count", "rank_verify"]:
        raise ValueError("phase sequence differs")
    for phase in phases:
        name = phase["phase"]
        if (phase.get("status") != "completed" or phase.get("return_code") != 0 or
                phase.get("stdout_sha256") != sha(attempt / f"{name}.stdout") or
                phase.get("stderr_sha256") != sha(attempt / f"{name}.stderr")):
            raise ValueError(f"{name} phase digest or status differs")
    independent_input = replay([sys.executable, str(PREPARED_CHECKER),
                                "--prepared", str(input_path), "--manifest", str(prepared_manifest)])
    if independent_input != result.get("input_check") or independent_input != load(attempt / "input_verify.stdout"):
        raise ValueError("prepared input replay differs")
    rank = replay([sys.executable, str(RANK_CHECKER), str(input_path),
                   str(attempt / "collector.stdout"), "--gx", str(prepared["generator"][0]),
                   "--gy", str(prepared["generator"][1]), "--qx", str(prepared["Q"][0]),
                   "--qy", str(prepared["Q"][1]), "--count-output", str(attempt / "count.stdout")])
    if (rank != result.get("rank_check") or rank != load(attempt / "rank_verify.stdout") or
            rank.get("status") != "valid" or not rank.get("independent_ordered_count_match") or
            rank.get("targets") != prepared["target_count"]):
        raise ValueError("relation, count or rank replay differs")
    if not control:
        prefixes = {min(prepared["target_count"], n) for n in (512, 2048, 8192, 32768)}
        if any(str(n) not in rank["rank_prefix"] for n in prefixes):
            raise ValueError("fixed rank prefix missing")
    if reference_run_dir is not None:
        reference = reference_run_dir.resolve()
        ref_result = load(reference / "raw-result.json")
        ref_manifest = load(reference / "manifest.yaml")
        ref_paths = ref_manifest["paths"]
        ref_input = next((path for path in (reference / "prepared.txt", reference.parent / "prepared.txt")
                          if path.is_file()), Path(ref_paths["input"]))
        ref_prepared_manifest = next((path for path in
                                      (reference / "prepared-manifest.json", reference.parent / "prepared-manifest.json")
                                      if path.is_file()), Path(ref_paths["prepared-manifest"]))
        check(reference, ref_input, ref_prepared_manifest,
              Path(ref_paths["admission"]) if "admission" in ref_paths else None,
              control, None, collector, count_verifier)
        ref_prepared = ref_result["prepared"]
        if (ref_result.get("status") != expected or
                any(ref_prepared[key] != prepared[key] for key in
                    ("stratum", "index", "stage", "target_count")) or
                (prepared["arm"], ref_prepared["arm"]) not in
                (("graph_transport", "low_x"), ("u2_transport", "low_x"))):
            raise ValueError("transport pair identity differs")
        if canonical_collector(reference / "attempt/collector.stdout") != canonical_collector(attempt / "collector.stdout"):
            raise ValueError("transported targetwise triples or multiplicities differ")
        for key in ("targets", "useful_targets", "useful_triples", "raw_unordered_triples",
                    "rank_increments", "rank_increment_targets", "rank_prefix",
                    "unique_canonical_coefficient_rows", "unique_canonical_augmented_rows"):
            if ref_result["rank_check"].get(key) != rank.get(key):
                raise ValueError(f"transported {key} differs")
    return {"status": "valid", "arm": prepared["arm"], "targets": rank["targets"],
            "useful_targets": rank["useful_targets"], "rank_increments": rank["rank_increments"],
            "transport_pair_checked": reference_run_dir is not None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--prepared-manifest", type=Path, required=True)
    parser.add_argument("--admission", type=Path)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--reference-run-dir", type=Path)
    parser.add_argument("--collector", type=Path, help="recompiled binary with the recorded SHA-256")
    parser.add_argument("--count-verifier", type=Path, help="recompiled binary with the recorded SHA-256")
    args = parser.parse_args()
    print(json.dumps(check(args.run_dir, args.input, args.prepared_manifest,
                           args.admission, args.control, args.reference_run_dir,
                           args.collector, args.count_verifier), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
