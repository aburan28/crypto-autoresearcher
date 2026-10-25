"""Direct native metadata only. No worksheet mathematics or scientific inference.

Used by new per-route drivers/checkers under TASK-20261018-993753. The native
supervisor creates the directory/provenance first. This module never launches
a supervisor, allocates an ID, changes a plan, or manufactures a seed/model.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import resource
import subprocess
import sys
import time

import yaml

ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = ("manifest.yaml", "raw-result.json", "certificate.yaml")


def same(actual, expected):
    """JSON type-aware equality: unlike Python equality, true is not one."""
    return json.dumps(actual,sort_keys=True,allow_nan=False) == json.dumps(expected,sort_keys=True,allow_nan=False)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def safe(name):
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError("expected repository-relative path")
    path = (ROOT / name).resolve()
    if not path.is_relative_to(ROOT) or path == ROOT:
        raise ValueError("path escapes repository")
    return path


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context(plan_path, directory, route):
    plan_path, directory = Path(plan_path).resolve(), Path(directory).resolve()
    if not plan_path.is_relative_to(ROOT) or not directory.is_relative_to(ROOT):
        raise ValueError("plan/run must be inside repository")
    plan = read_json(plan_path)
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1" or plan.get("frozen") is not True:
        raise ValueError("requires a frozen native trial plan")
    sources = plan.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("missing source closure")
    for name, expected in sources.items():
        if digest(safe(name)) != expected:
            raise ValueError(f"bound source changed: {name}")
    own = Path(__file__).resolve().relative_to(ROOT).as_posix()
    if own not in sources:
        raise ValueError("metadata helper must be source-bound")
    spec_path = safe(plan["specification"])
    if digest(spec_path) != plan["specification_sha256"]:
        raise ValueError("frozen specification changed")
    spec = yaml.safe_load(spec_path.read_text())["experiment"]
    if spec["id"] != plan["experiment_id"]:
        raise ValueError("specification identity mismatch")
    launch = read_json(directory / "launch.json")
    environment = read_json(directory / "environment.json")
    trials = [t for t in plan["trials"] if t["id"] == launch["trial_id"]]
    if len(trials) != 1:
        raise ValueError("launch does not select one trial")
    trial = trials[0]
    if trial.get("route") != route or route not in ("a", "b"):
        raise ValueError("route does not match frozen trial")
    expected_dir = ROOT / "experiments" / plan["experiment_id"] / "runs" / trial["run_id"]
    if directory != expected_dir or launch["run_id"] != trial["run_id"]:
        raise ValueError("native run path/ID mismatch")
    expand = lambda argv: [s.replace("{run_dir}", str(directory)) for s in argv]
    if (launch["plan_sha256"] != digest(plan_path)
            or launch["argv"] != expand(trial["argv"])
            or launch["check_argv"] != expand(trial["check_argv"])
            or read_json(directory / "command.txt") != launch["argv"]):
        raise ValueError("supervisor command/plan binding mismatch")
    if (not same(environment["source_sha256"], sources)
            or environment["specification_sha256"] != plan["specification_sha256"]
            or environment["commit"] != launch["authority"]["commit"]):
        raise ValueError("supervisor environment/source binding mismatch")
    commit = environment["commit"]
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("missing actual launch commit")
    if set(trial["artifacts"]) != set(OUTPUTS):
        raise ValueError("declare exactly the three driver artifacts")
    implementation = safe(f"experiments/{plan['experiment_id']}/implementation")
    for name in ("route_a.py", "route_b.py", "oracle.py", "run.py", "check.py"):
        if (implementation / name).relative_to(ROOT).as_posix() not in sources:
            raise ValueError(f"source closure omits {name}")
    return dict(plan=plan, plan_path=plan_path, directory=directory, spec=spec,
                launch=launch, environment=environment, trial=trial,
                implementation=implementation)


def compare_previous(c, measurement, witness):
    previous_id = c["trial"].get("comparison_trial_id")
    if previous_id is None:
        if c["trial"]["route"] != "a":
            raise ValueError("second route requires first-route comparison")
        return {"implementations_agree": None, "state": "awaiting_separate_route_b", "previous": None}
    earlier = [t for t in c["plan"]["trials"] if t["id"] == previous_id]
    if (len(earlier) != 1 or earlier[0].get("route") != "a"
            or c["trial"]["route"] != "b"
            or previous_id not in c["trial"].get("depends_on", [])):
        raise ValueError("comparison dependency is not the first separate route")
    path = ROOT / "experiments" / c["plan"]["experiment_id"] / "runs" / earlier[0]["run_id"] / "raw-result.json"
    old = read_json(path)
    if (old["experiment_id"] != c["plan"]["experiment_id"]
            or old["run_id"] != earlier[0]["run_id"] or old["route"] != "a"
            or old["plan_sha256"] != digest(c["plan_path"])
            or not same(old["inputs"], c["spec"]["inputs"])):
        raise ValueError("first-route comparison identity/input mismatch")
    receipt_path = path.parent / "execution-receipt.json"
    receipt = read_json(receipt_path)
    if (receipt["schema"] != "crypto.autoresearch.trial_receipt.v1"
            or receipt["status"] != "output_validated" or receipt["returncode"] != 0
            or type(receipt["returncode"]) is not int or type(receipt["check_returncode"]) is not int
            or receipt["check_returncode"] != 0 or receipt["plan_sha256"] != digest(c["plan_path"])
            or receipt["trial_id"] != previous_id or receipt["run_id"] != earlier[0]["run_id"]):
        raise ValueError("first route lacks a validated native dependency receipt")
    for name, expected in receipt["artifact_sha256"].items():
        artifact = (path.parent / name).resolve()
        if not artifact.is_relative_to(path.parent) or digest(artifact) != expected:
            raise ValueError("first-route artifact changed after its native receipt")
    if receipt["artifact_sha256"].get("raw-result.json") != digest(path):
        raise ValueError("first-route receipt does not bind its raw result")
    return {"implementations_agree": same(measurement, old["measurement"]) and same(witness, old["witness"]),
            "state": "two_separate_route_runs_compared",
            "previous": {"trial_id": previous_id, "run_id": earlier[0]["run_id"], "raw_sha256": digest(path),
                         "native_receipt_sha256": digest(receipt_path)}}


def write_once(path, data):
    with Path(path).open("x") as stream:
        stream.write(data)


def json_text(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def metadata_environment(c):
    return {"supervisor": c["environment"], "supervisor_launch_sha256": digest(c["directory"] / "launch.json"),
        "runtime": {"python": sys.version, "executable": sys.executable, "pyyaml": yaml.__version__},
        "inference": "no inference performed or attested by driver",
        "git_dirty_boundary": "actual git status after raw/witness writes, before manifest emission; may include newly produced untracked run artifacts",
        "timing_boundary": "from before argument/provenance validation through selected route, raw/witness writes and git status; excludes process startup, manifest emission and separate checker",
        "resource_boundary": "CPU delta for driver and git child; RSS maximum of their per-process lifetime peaks, not aggregate process-group RSS"}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial-plan", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--route", choices=("a", "b"), required=True)
    return parser.parse_args()


def run():
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    usage_start = resource.getrusage(resource.RUSAGE_SELF)
    children_start = resource.getrusage(resource.RUSAGE_CHILDREN)
    args = arguments()
    c = context(args.trial_plan, args.run_dir, args.route)
    directory = c["directory"]
    if any((directory / name).exists() for name in OUTPUTS):
        raise ValueError("refuse existing output: allocate a new run; retain the attempt")
    scientific = load_module(c["implementation"] / f"route_{args.route}.py", "measured_route")
    # The selected route is the only scientific route imported by this process.
    result = scientific.compute(c["spec"]["inputs"])
    measurement = result["measurement"]
    controls, prediction = scientific.assess(c["spec"]["inputs"], measurement)
    comparison = compare_previous(c, measurement, result["witness"])
    valid = all(controls.values()) and comparison["implementations_agree"] is not False
    raw = {"schema": "crypto.autoresearch.finite_worksheet.v1", "experiment_id": c["plan"]["experiment_id"],
           "run_id": c["trial"]["run_id"], "route": args.route, "inputs": c["spec"]["inputs"],
           "plan_sha256": digest(c["plan_path"]), "specification_sha256": c["plan"]["specification_sha256"],
           "measurement": measurement, "witness": result["witness"], "controls": controls,
           "prediction_comparison": prediction, "comparison": comparison, "attack_claimed": False}
    write_once(directory / "raw-result.json", json_text(raw))
    certificate = {"worksheet_witness": {"experiment_id": raw["experiment_id"], "run_id": raw["run_id"],
        "raw_result_sha256": digest(directory / "raw-result.json"), "route": args.route,
        "witness": result["witness"], "boundary": "finite worksheet transcript; not a formal proof, decomposition or discrete-log certificate"}}
    write_once(directory / "certificate.yaml", yaml.safe_dump(certificate, sort_keys=True))
    status = subprocess.run(["git", "-c", "core.preloadIndex=false", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=normal"],
                            capture_output=True, text=True, check=True)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    children = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = usage.ru_utime + usage.ru_stime - usage_start.ru_utime - usage_start.ru_stime
    cpu += children.ru_utime + children.ru_stime - children_start.ru_utime - children_start.ru_stime
    elapsed = time.monotonic() - started
    manifest = {"run": {"id": raw["run_id"], "experiment_id": raw["experiment_id"],
        "status": "completed_valid" if valid else "completed_invalid",
        "code": {"commit": c["environment"]["commit"], "dirty": bool(status.stdout),
                 "command": (directory / "command.txt").read_text().strip()},
        "environment": metadata_environment(c),
        "inputs": {"curve_id": None, "seed": None, "parameters": {"frozen_inputs": raw["inputs"],
            "seed_semantics": "deterministic frozen worksheet; no randomness or invented seed", "route": args.route,
            "trial_plan_sha256": raw["plan_sha256"], "specification_sha256": raw["specification_sha256"]}},
        "timing": {"started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(), "wall_seconds": elapsed},
        "resources": {"cpu_seconds": cpu, "peak_rss_bytes": int(max(usage.ru_maxrss, children.ru_maxrss) * (1 if sys.platform == "darwin" else 1024))},
        "result": {"metrics": {**measurement, **comparison, "prediction_comparison": prediction}, "valid": valid,
            "invalid_reason": None if valid else "worksheet control failed or separately executed routes disagree",
            "certificate": {"kind": "none", "verified": None, "verifier": None}},
        "artifacts": {name: {"sha256": digest(directory / name)} for name in OUTPUTS if name != "manifest.yaml"}}}
    write_once(directory / "manifest.yaml", yaml.safe_dump(manifest, sort_keys=True))


def check():
    args = arguments()
    c = context(args.trial_plan, args.run_dir, args.route)
    directory = c["directory"]
    raw = read_json(directory / "raw-result.json")
    oracle = load_module(c["implementation"] / "oracle.py", "independent_checker")
    expected = oracle.compute(c["spec"]["inputs"])
    controls, prediction = oracle.assess(c["spec"]["inputs"], expected["measurement"])
    comparison = compare_previous(c, expected["measurement"], expected["witness"])
    exact = {"schema": "crypto.autoresearch.finite_worksheet.v1", "experiment_id": c["plan"]["experiment_id"],
        "run_id": c["trial"]["run_id"], "route": args.route, "inputs": c["spec"]["inputs"],
        "plan_sha256": digest(c["plan_path"]), "specification_sha256": c["plan"]["specification_sha256"],
        "measurement": expected["measurement"], "witness": expected["witness"], "controls": controls,
        "prediction_comparison": prediction, "comparison": comparison, "attack_claimed": False}
    if not same(raw, exact):
        raise ValueError("raw transcript/metrics do not equal independent recomputation")
    certificate = yaml.safe_load((directory / "certificate.yaml").read_text())
    expected_certificate = {"worksheet_witness": {"experiment_id": raw["experiment_id"], "run_id": raw["run_id"],
        "raw_result_sha256": digest(directory / "raw-result.json"), "route": args.route,
        "witness": expected["witness"], "boundary": "finite worksheet transcript; not a formal proof, decomposition or discrete-log certificate"}}
    if not same(certificate, expected_certificate):
        raise ValueError("worksheet witness binding mismatch")
    manifest = yaml.safe_load((directory / "manifest.yaml").read_text())["run"]
    valid = all(controls.values()) and comparison["implementations_agree"] is not False
    if (manifest["id"] != raw["run_id"] or manifest["experiment_id"] != raw["experiment_id"]
            or manifest["code"]["commit"] != c["environment"]["commit"]
            or manifest["code"]["command"] != (directory / "command.txt").read_text().strip()
            or type(manifest["code"]["dirty"]) is not bool
            or not same(manifest["environment"], metadata_environment(c))
            or manifest["inputs"]["seed"] is not None or manifest["inputs"]["curve_id"] is not None
            or not same(manifest["inputs"]["parameters"], {"frozen_inputs": raw["inputs"],
                "seed_semantics": "deterministic frozen worksheet; no randomness or invented seed", "route": args.route,
                "trial_plan_sha256": raw["plan_sha256"], "specification_sha256": raw["specification_sha256"]})
            or not same(manifest["result"]["metrics"], {**expected["measurement"], **comparison, "prediction_comparison": prediction})
            or manifest["result"]["valid"] is not valid
            or manifest["result"]["invalid_reason"] != (None if valid else "worksheet control failed or separately executed routes disagree")
            or manifest["status"] != ("completed_valid" if valid else "completed_invalid")
            or not same(manifest["result"]["certificate"], {"kind": "none", "verified": None, "verifier": None})):
        raise ValueError("canonical metadata/result binding mismatch")
    timing, resources = manifest["timing"], manifest["resources"]
    if (datetime.fromisoformat(timing["finished_at"]) < datetime.fromisoformat(timing["started_at"])
            or type(timing["wall_seconds"]) not in (int,float)
            or not math.isfinite(timing["wall_seconds"]) or timing["wall_seconds"] < 0
            or type(resources["cpu_seconds"]) not in (int,float)
            or not math.isfinite(resources["cpu_seconds"]) or resources["cpu_seconds"] < 0
            or type(resources["peak_rss_bytes"]) is not int or resources["peak_rss_bytes"] < 0):
        raise ValueError("invalid timing/resource measurements")
    for name in ("raw-result.json", "certificate.yaml"):
        if manifest["artifacts"][name]["sha256"] != digest(directory / name):
            raise ValueError("manifest artifact digest mismatch")
    print(json_text({"output_integrity": True, "worksheet_controls_valid": valid,
        "prediction_comparison": prediction, "boundary": "independent finite recomputation; no hypothesis verdict"}), end="")
