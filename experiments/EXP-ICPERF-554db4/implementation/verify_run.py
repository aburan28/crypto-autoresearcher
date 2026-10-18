"""Independent replay of an admitted sorted m8 planted solver panel.

Checks every retained call and attempt, serialized CNF/XOR, point rows and
archive member. Solver-reported UNSAT remains unvalidated by this checker.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import math
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parents[1]
ORDER = ("weighted_unsorted_first", "weighted_sorted", "weighted_unsorted_repeat",
         "local_random_unsorted_first", "local_random_sorted", "local_random_unsorted_repeat")


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def old_independent_checker():
    path = ROOT / "experiments/EXP-ICPERF-018b0c/implementation/verify_run.py"
    spec = importlib.util.spec_from_file_location("icperf_prior_independent_verifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_bundle(run_dir: Path, result: dict) -> int:
    record_blob = (run_dir / "calls-manifest.json").read_bytes()
    record = json.loads(record_blob)
    tar_path = run_dir / "calls.tar.gz"
    if (record["schema"] != "icperf-binary-m8-call-tree-v1"
            or result["calls_manifest_sha256"] != sha(record_blob)
            or record["bundle_sha256"] != result["calls_bundle_sha256"]
            or sha(tar_path.read_bytes()) != record["bundle_sha256"]
            or tar_path.stat().st_size != record["bundle_size_bytes"]):
        raise ValueError("call archive binding mismatch")
    names = [row["path"] for row in record["files"]]
    if names != sorted(set(names)) or any(not name.startswith("calls/") or ".." in Path(name).parts
                                          for name in names):
        raise ValueError("invalid call archive path list")
    actual = sorted(path.relative_to(run_dir).as_posix()
                    for path in (run_dir / "calls").rglob("*") if path.is_file())
    if actual != names:
        raise ValueError("raw call tree differs from archive manifest")
    for row in record["files"]:
        blob = (run_dir / row["path"]).read_bytes()
        if len(blob) != row["size_bytes"] or sha(blob) != row["sha256"]:
            raise ValueError(f"raw call file changed: {row['path']}")
    with tarfile.open(tar_path, "r:gz") as archive:
        members = archive.getmembers()
        if [member.name for member in members] != names:
            raise ValueError("archive member list mismatch")
        for member, row in zip(members, record["files"]):
            source = archive.extractfile(member)
            if not member.isfile() or source is None or sha(source.read()) != row["sha256"]:
                raise ValueError("archive member content mismatch")
    return len(names)


def check_call(run_dir: Path, row: dict, source: dict, arm: dict, chain: dict,
               base: dict, prior) -> dict:
    name = row["name"]
    label = "local_random" if name.startswith("local_random") else "weighted"
    sorted_arm = name.endswith("_sorted")
    chosen = arm if sorted_arm else source
    packed = (ROOT / chosen["formula_path"]).read_bytes()
    expected_gzip = chosen["formula_gzip_sha256"]
    expected_raw = arm["raw_xcnf_sha256"] if sorted_arm else source["formula_raw_sha256"]
    if sha(packed) != expected_gzip:
        raise ValueError("formula gzip digest mismatch")
    raw = gzip.decompress(packed)
    if sha(raw) != expected_raw:
        raise ValueError("formula raw digest mismatch")
    host = row["host"]
    if (host["available_memory_bytes"] < 0 or host["free_disk_bytes"] < 0
            or len(host["load_average"]) != 3
            or not all(math.isfinite(value) and value >= 0 for value in host["load_average"])):
        raise ValueError("invalid host admission data")
    if row["status"] in ("host_admission_stop", "infrastructure_or_input_failure"):
        if row["status"] == "host_admission_stop" and not (
            host["available_memory_bytes"] < 10 * (1 << 30)
            or host["free_disk_bytes"] < host["declared_raw_reserve_bytes"]):
            raise ValueError("host admission was denied without declared reason")
        return {"name": name, "status": row["status"], "checked_attempts": 0}
    call_dir = run_dir / "calls" / name
    summary_blob = (call_dir / "summary.json").read_bytes()
    summary = json.loads(summary_blob)
    if (sha(summary_blob) != row["summary_sha256"] or summary["status"] != row["status"]
            or summary["input_sha256"] != sha(raw) or summary["name"] != name
            or summary["host"] != host or len(summary["attempts"]) != row["attempts"]
            or summary["limits"]["seed"] != 20261018
            or summary["limits"]["memory_bytes"] != 8 * (1 << 30)
            or summary["limits"]["max_models"] != 64
            or summary["limits"]["wall_seconds"] != 1200):
        raise ValueError("call summary mismatch")
    blocked: list[int] = []
    certified = 0
    for index, attempt in enumerate(summary["attempts"], 1):
        attempt_dir = call_dir / f"attempt-{index:04d}"
        if json.loads((attempt_dir / "attempt.json").read_bytes()) != attempt:
            raise ValueError("attempt receipt mismatch")
        exact_input = prior.add_blocks(raw, blocked)
        if (attempt["input_sha256"] != sha(exact_input)
                or (attempt_dir / "input.xcnf").read_bytes() != exact_input
                or attempt["blocked_primary"] != len(blocked)
                or attempt["command"][1:9] != ["--verb", "0", "--threads", "1",
                                              "--maxsol", "1", "--random", "20261018"]
                or attempt["command"][-1] != str(attempt_dir / "input.xcnf")):
            raise ValueError("attempt input or command mismatch")
        if attempt["outcome"] == "solver_launch_failure":
            continue
        stdout_blob = (attempt_dir / "stdout.txt").read_bytes()
        stderr_blob = (attempt_dir / "stderr.txt").read_bytes()
        process = attempt["process"]
        if sha(stdout_blob) != process["stdout_sha256"] or sha(stderr_blob) != process["stderr_sha256"]:
            raise ValueError("solver output digest mismatch")
        statuses = [line.strip() for line in stdout_blob.decode(errors="replace").splitlines()
                    if line.startswith("s ")]
        if statuses != attempt["solver_status_lines"]:
            raise ValueError("solver status mismatch")
        if process["wall_timeout"]:
            expected = "wall_censored"
        elif process["rss_watchdog_tripped"]:
            expected = "memory_censored"
        elif process["returncode"] == 20 and statuses == ["s UNSATISFIABLE"]:
            expected = "solver_reported_exhausted_unvalidated"
        elif process["returncode"] == 0 and statuses in (["s UNKNOWN"], ["s INDETERMINATE"]):
            expected = "solver_unknown_censored"
        elif process["returncode"] != 10 or statuses != ["s SATISFIABLE"]:
            expected = "solver_failure_or_unclassified"
        else:
            nvars, clauses, xors = prior.parse_xcnf(exact_input)
            values = prior.parse_sat_model(stdout_blob.decode(errors="replace"), nvars)
            prior.verify_xcnf(values, clauses, xors)
            primary = sum(1 << (j - 1) for j in range(1, 455) if values[j])
            if primary in blocked or attempt["primary_assignment_hex"] != hex(primary):
                raise ValueError("repeated or misrecorded primary model")
            cert_blob = (attempt_dir / "certificate.json").read_bytes()
            cert = json.loads(cert_blob)
            if (sha(cert_blob) != attempt["certificate_sha256"]
                    or cert["assignment_hex"] != hex(primary)
                    or cert["base_kind"] != label
                    or cert["encoding"] != ("sorted" if sorted_arm else "unsorted")):
                raise ValueError("point certificate binding mismatch")
            exact_rows = prior.exact_point_rows(primary, base, chain,
                                                {"kind": "torsion_phi", "base_dimension": 11,
                                                 "offset": 4096, "primary_variables": 454,
                                                 "target_coordinate": arm["target_coordinate"]})
            if cert["result"].get("full_point_certificates", []) != exact_rows:
                raise ValueError("independent point rows differ")
            if exact_rows:
                expected = attempt["outcome"]
                if expected not in ("point_relation_certified", "point_relation_certified_after_wall_cap"):
                    raise ValueError("certified point classified incorrectly")
                certified += 1
            else:
                expected = attempt["outcome"]
                if expected not in ("rejected_primary", "wall_censored"):
                    raise ValueError("rejected point classified incorrectly")
                blocked.append(primary)
        if attempt["outcome"] != expected:
            raise ValueError("attempt outcome differs from raw observation")
    if summary["blocked_primary_count"] != len(blocked):
        raise ValueError("blocked-model count mismatch")
    return {"name": name, "status": row["status"], "checked_attempts": len(summary["attempts"]),
            "independent_certified_attempts": certified}


def verify(run_dir: Path) -> dict:
    if sys.flags.optimize:
        raise ValueError("optimized Python disables scientific assertions")
    import yaml
    prior = old_independent_checker()
    launch, environment = [json.loads((run_dir / name).read_bytes())
                           for name in ("launch.json", "environment.json")]
    result = json.loads((run_dir / "raw-result.json").read_bytes())
    plan_blob = (HERE / "trial-plan.json").read_bytes()
    plan = json.loads(plan_blob)
    spec = yaml.safe_load((HERE / "specification.yaml").read_text())["experiment"]
    if (result["experiment_id"] != "EXP-ICPERF-554db4"
            or result["source_commit"] != environment["commit"]
            or result["plan_sha256"] != launch["plan_sha256"]
            or launch["plan_sha256"] != sha(plan_blob)
            or plan["specification_sha256"] != sha((HERE / "specification.yaml").read_bytes())
            or len(result["calls"]) != 6
            or tuple(row["name"] for row in result["calls"]) != ORDER):
        raise ValueError("run/plan/call binding mismatch")
    run_manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text())["run"]
    if run_manifest["id"] != run_dir.name or run_manifest["experiment_id"] != result["experiment_id"]:
        raise ValueError("run manifest mismatch")
    file_count = verify_bundle(run_dir, result)
    arms = json.loads((HERE / "inputs/sorted_positive_manifest.json").read_bytes())["arms"]
    source = json.loads((ROOT / "experiments/EXP-ICPERF-018b0c/inputs/positive_manifest.json").read_bytes())["controls"]
    checked = []
    for row in result["calls"]:
        label = "local_random" if row["name"].startswith("local_random") else "weighted"
        arm = arms[label]
        chain = {"gamma": 70364449406991,
                 "curve": {"b_polynomial_bits": 31, "prime_order": 576460752557211763},
                 "selected_channel": 0, "target_channels": [arm["raw_target"]] * 4,
                 "subgroup_target": arm["projected_target"]}
        base_name = "weighted" if label == "weighted" else "local_control"
        base = json.loads((ROOT / f"research/icperf_binary_torsion_k11_{base_name}_20261017/base.json").read_bytes())
        checked.append(check_call(run_dir, row, source[label], arm, chain, base, prior))
    return {"schema": "icperf-binary-m8-sorted-run-independent-check-v1",
            "experiment_id": result["experiment_id"], "run_id": run_dir.name,
            "raw_result_sha256": sha((run_dir / "raw-result.json").read_bytes()),
            "bundle_files_checked": file_count, "calls": checked,
            "source_sha256": sha(Path(__file__).read_bytes())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    result = verify(run_dir)
    with (run_dir / "independent_check.json").open("x") as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"calls_checked": len(result["calls"]),
                      "bundle_files_checked": result["bundle_files_checked"]}, sort_keys=True))


if __name__ == "__main__":
    main()
