#!/usr/bin/env python3
"""Metadata only. Scientific observations come from two non-importing C++ routes.

This adapter has no stand-alone worksheet mode. The native supervisor must
provide the actual launch, environment and command. It never admits trials,
allocates IDs, modifies frozen inputs, or promotes a scientific interpretation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
SELF = Path(__file__).resolve().relative_to(ROOT).as_posix()
ARTIFACTS = ["raw-result.json", "primary-output.json", "native-primary.json",
             "independent-check.json", "certificate.yaml", "manifest.yaml"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    result = strict_json(Path(path).read_text())
    if not isinstance(result, dict):
        raise ValueError(f"expected JSON object: {path}")
    return result


def strict_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")
    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("nonfinite JSON float")
        return parsed
    return json.loads(data, object_pairs_hook=unique, parse_constant=bad_constant, parse_float=finite_float)


def typed_equal(left, right):
    return json.dumps(left, sort_keys=True, separators=(",", ":"), allow_nan=False) == json.dumps(right, sort_keys=True, separators=(",", ":"), allow_nan=False)


def write(path, value):
    # JSON is valid YAML; no YAML loader or third-party arithmetic dependency.
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def safe(name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("expected a repository-relative source path")
    path = ROOT / name
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"unsafe source: {name}")
    return path


def same_hash(path, expected):
    if not isinstance(expected, str) or digest(path) != expected:
        raise ValueError(f"bound file changed: {path}")


def expanded(argv, directory):
    return [x.replace("{run_dir}", str(directory)) for x in argv]


def invocation_equal(actual, expected):
    return (len(actual) == len(expected)
            and Path(actual[0]).resolve() == Path(expected[0]).resolve()
            and actual[1:] == expected[1:])


def context(args):
    directory = Path(args.out).resolve()
    plan_path = Path(args.plan).resolve()
    if not directory.is_relative_to(ROOT) or not plan_path.is_relative_to(ROOT):
        raise ValueError("plan and output must be inside this checkout")
    plan = read(plan_path)
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1" or plan.get("frozen") is not True:
        raise ValueError("requires a frozen native trial plan")
    launch, environment = read(directory / "launch.json"), read(directory / "environment.json")
    same_hash(plan_path, launch.get("plan_sha256"))
    candidates = [t for t in plan["trials"] if t["id"] == launch["trial_id"]]
    if len(candidates) != 1:
        raise ValueError("actual supervisor trial is not unique")
    trial = candidates[0]
    if trial["run_id"] != launch["run_id"] or directory.name != trial["run_id"]:
        raise ValueError("actual supervisor run identity mismatch")
    if directory != ROOT / "experiments" / plan["experiment_id"] / "runs" / trial["run_id"]:
        raise ValueError("output is not the exact native run directory")
    if set(trial["artifacts"]) != set(ARTIFACTS):
        raise ValueError("prospectively declare every worksheet artifact, exactly")
    if trial.get("memory_mb", 0) > 1024 or trial.get("memory_mb", 0) <= 0:
        raise ValueError("one-GiB frozen memory maximum")
    if trial.get("watchdog_seconds") is None:
        raise ValueError("requires a prospectively justified finite process watchdog")
    block = trial.get("finite_worksheet", {})
    if block.get("route") != args.route or args.route not in ("a", "b"):
        raise ValueError("route must match the frozen trial")
    config_path = safe(block["implementation"])
    config = read(config_path)
    if config["experiment_id"] != plan["experiment_id"]:
        raise ValueError("implementation/experiment identity mismatch")
    if block.get("input_seed", "missing") is not None or config["seed"] is not None:
        raise ValueError("deterministic exhaustive worksheets use honest seed:null")
    sources = plan["source_sha256"]
    required = {SELF, config_path.relative_to(ROOT).as_posix(), *config["source_dependencies"]}
    if not required <= set(sources):
        raise ValueError("trial plan does not bind the complete implementation/source closure")
    for name, expected in sources.items():
        same_hash(safe(name), expected)
    if environment["source_sha256"] != sources:
        raise ValueError("actual supervisor source closure mismatch")
    same_hash(safe(plan["specification"]), plan["specification_sha256"])
    if environment["specification_sha256"] != plan["specification_sha256"]:
        raise ValueError("actual supervisor specification mismatch")
    if plan["specification"] != config["specification"]:
        raise ValueError("wrong scientific specification")
    for key, mode in (("argv", "run"), ("check_argv", "check")):
        expected = expanded(trial[key], directory)
        if launch[key] != expected:
            raise ValueError("actual launch command differs from the frozen plan")
        if mode == args.mode and not invocation_equal([sys.executable, *sys.argv], expected):
            raise ValueError("current invocation differs from the actual supervisor command")
    if strict_json((directory / "command.txt").read_text()) != launch["argv"]:
        raise ValueError("actual command.txt differs from launch.json")
    actual_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if actual_commit != environment["commit"] or actual_commit != launch["authority"]["commit"]:
        raise ValueError("actual launch/source commit mismatch")
    compiler = Path(config["compiler"]["path"])
    same_hash(compiler, config["compiler"]["sha256"])
    for dependency in config["compiler"]["system_dependencies"]:
        same_hash(Path(dependency["path"]), dependency["sha256"])
    if config.get("interpretation_required"):
        interpretation = block.get("interpretation")
        if not isinstance(interpretation, dict) or not interpretation.get("admitted_by"):
            raise ValueError("c9c5a4 requires Coordinator admission of the additive two-convention protocol")
        path = safe(interpretation["path"])
        same_hash(path, interpretation["sha256"])
        if sources.get(interpretation["path"]) != interpretation["sha256"]:
            raise ValueError("interpretation protocol is not in the native source closure")
    provenance = {name: digest(directory / name)
                  for name in ("launch.json", "environment.json", "command.txt")}
    return directory, plan, trial, block, config, launch, environment, provenance


def subprocess_receipt(argv):
    """wait4 observes this exact process, not a guessed or cumulative child RSS."""
    started, tick = stamp(), time.monotonic()
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        child = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                 stdout=stdout, stderr=stderr)
        _, status, usage = os.wait4(child.pid, 0)
        child.returncode = os.waitstatus_to_exitcode(status)
        stdout.seek(0)
        stderr.seek(0)
        out, err = stdout.read(), stderr.read()
    rss_scale = 1 if sys.platform == "darwin" else 1024
    return {"argv": argv, "started_at": started, "finished_at": stamp(),
            "wall_seconds": time.monotonic() - tick,
            "returncode": child.returncode,
            "cpu_seconds": usage.ru_utime + usage.ru_stime,
            "peak_rss_bytes": usage.ru_maxrss * rss_scale,
            "stdout": out.decode("utf-8", errors="strict"),
            "stderr": err.decode("utf-8", errors="strict")}


def native(config, route, directory):
    # Intermediate binary is removed before any success/failure return. Its exact
    # source/compiler/flags, byte digest, diagnostics and resources are retained.
    path = directory / (".worksheet-" + route)
    if path.exists():
        raise ValueError("native intermediate already exists; never reuse it")
    compiler = config["compiler"]
    receipt = {"route": route, "source": config["routes"][route],
               "source_sha256": digest(safe(config["routes"][route])),
               "compiler": compiler}
    try:
        receipt["compile"] = subprocess_receipt(
            [compiler["path"], *compiler["flags"], config["routes"][route], "-o", str(path)])
        if receipt["compile"]["returncode"]:
            raise ValueError("native compilation failed")
        receipt["binary_sha256"] = digest(path)
        receipt["synthetic_control"] = subprocess_receipt([str(path), "--self-test"])
        if receipt["synthetic_control"]["returncode"]:
            raise ValueError("native synthetic controls failed")
        receipt["worksheet"] = subprocess_receipt([str(path)])
        if receipt["worksheet"]["returncode"]:
            raise ValueError("native worksheet failed")
        output = receipt["worksheet"]["stdout"].encode("utf-8")
        observations = strict_json(output)
        if not isinstance(observations, dict):
            raise ValueError("native worksheet did not emit a JSON object")
        return receipt, output, observations
    except BaseException as error:
        receipt["error"] = str(error)
        # Failures are retained, never made into an arithmetic observation.
        name = "native-primary.json" if route == config["primary_route"] else "independent-check.json"
        if not (directory / name).exists():
            write(directory / name, {"native_failure": receipt})
        raise
    finally:
        path.unlink(missing_ok=True)


def field(value, path):
    for key in path.split("."):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def nonnegative(value, label, integer=False):
    if (isinstance(value, bool) or not isinstance(value, int if integer else (int, float))
            or value < 0 or not math.isfinite(value)):
        raise ValueError(f"invalid actual resource/timing field: {label}")


def validate_primary(primary, config, route, directory, output):
    source = config["routes"][route]
    if (primary["route"] != route or primary["source"] != source
            or primary["source_sha256"] != digest(safe(source))
            or primary["compiler"] != config["compiler"]):
        raise ValueError("primary native source/route/compiler identity mismatch")
    binary = str(directory / (".worksheet-" + route))
    commands = {
        "compile": [config["compiler"]["path"], *config["compiler"]["flags"], source, "-o", binary],
        "synthetic_control": [binary, "--self-test"],
        "worksheet": [binary],
    }
    child_cpu = 0
    for name, argv in commands.items():
        record = primary[name]
        if record["argv"] != argv or type(record["returncode"]) is not int or record["returncode"] != 0:
            raise ValueError("primary compile/control/worksheet command or status mismatch")
        if datetime.fromisoformat(record["finished_at"]) < datetime.fromisoformat(record["started_at"]):
            raise ValueError("primary subprocess timestamps are reversed")
        for key in ("wall_seconds", "cpu_seconds"):
            nonnegative(record[key], f"{name}.{key}")
        nonnegative(record["peak_rss_bytes"], f"{name}.peak_rss_bytes", integer=True)
        child_cpu += record["cpu_seconds"]
    if primary["worksheet"]["stdout"].encode("utf-8") != output:
        raise ValueError("primary native receipt stdout differs from preserved output bytes")
    control = strict_json(primary["synthetic_control"]["stdout"])
    if control != {"synthetic_control": True, "frozen_worksheet_executed": False}:
        raise ValueError("primary synthetic control receipt is malformed")
    for key in ("wall_seconds", "wrapper_cpu_seconds", "total_child_cpu_seconds"):
        nonnegative(primary[key], key)
    nonnegative(primary["wrapper_peak_rss_bytes"], "wrapper_peak_rss_bytes", integer=True)
    nonnegative(primary["total_child_peak_rss_bytes"], "total_child_peak_rss_bytes", integer=True)
    if primary["total_child_cpu_seconds"] + 1e-8 < child_cpu:
        raise ValueError("primary total child CPU omits a recorded native subprocess")
    if datetime.fromisoformat(primary["finished_at"]) < datetime.fromisoformat(primary["started_at"]):
        raise ValueError("primary wrapper timestamps are reversed")
    binary_digest = primary["binary_sha256"]
    if not isinstance(binary_digest, str) or len(binary_digest) != 64 or any(x not in "0123456789abcdef" for x in binary_digest):
        raise ValueError("primary native binary digest malformed")


def predecessor(directory, plan, trial, plan_sha256, config):
    """Bind a finished predecessor's identity and every supervisor-retained byte."""
    receipt = read(directory / "execution-receipt.json")
    if (receipt["schema"] != "crypto.autoresearch.trial_receipt.v1"
            or receipt["plan_sha256"] != plan_sha256
            or receipt["trial_id"] != trial["id"] or receipt["run_id"] != trial["run_id"]
            or receipt["status"] != "output_validated"
            or type(receipt["returncode"]) is not int or receipt["returncode"] != 0
            or type(receipt["check_returncode"]) is not int or receipt["check_returncode"] != 0):
        raise ValueError("predecessor native execution receipt is not a validated exact trial")
    generated = {"launch.json", "environment.json", "command.txt", "stdout.log",
                 "stderr.log", "check.stdout.log", "check.stderr.log"}
    expected = set(trial["artifacts"]) | generated
    if set(receipt["artifact_sha256"]) != expected:
        raise ValueError("predecessor receipt does not bind exactly all declared/generated artifacts")
    for name, expected_hash in receipt["artifact_sha256"].items():
        path = directory / name
        if path.is_symlink() or path.parent != directory:
            raise ValueError("unsafe predecessor artifact")
        same_hash(path, expected_hash)
    raw = read(directory / "raw-result.json")
    checked = read(directory / "independent-check.json")
    manifest = read(directory / "manifest.yaml")["run"]
    prior_launch = read(directory / "launch.json")
    prior_environment = read(directory / "environment.json")
    if (prior_launch["plan_sha256"] != plan_sha256
            or prior_launch["trial_id"] != trial["id"] or prior_launch["run_id"] != trial["run_id"]
            or not typed_equal(prior_launch["argv"], expanded(trial["argv"], directory))
            or not typed_equal(prior_launch["check_argv"], expanded(trial["check_argv"], directory))
            or not typed_equal(strict_json((directory / "command.txt").read_text()), prior_launch["argv"])
            or prior_environment["commit"] != receipt["authority"]["commit"]
            or manifest["code"]["commit"] != prior_environment["commit"]
            or prior_environment["specification_sha256"] != plan["specification_sha256"]
            or not typed_equal(prior_environment["source_sha256"], plan["source_sha256"])):
        raise ValueError("predecessor actual supervisor metadata/command/source mismatch")
    prior_provenance = {name: digest(directory / name)
                        for name in ("launch.json", "environment.json", "command.txt")}
    if (raw["schema"] != "finite-worksheet.raw.v1"
            or raw["experiment_id"] != plan["experiment_id"] or raw["run_id"] != trial["run_id"]
            or raw["route"] != trial["finite_worksheet"]["route"]
            or raw["plan_sha256"] != plan_sha256
            or raw["specification_sha256"] != plan["specification_sha256"]
            or not typed_equal(raw["source_sha256"], plan["source_sha256"])
            or raw["scope"] != config["scope"] or raw["seed"] is not None
            or not typed_equal(raw["supervisor_provenance_sha256"], prior_provenance)):
        raise ValueError("predecessor raw identity/source/scope/provenance mismatch")
    same_hash(directory / "primary-output.json", raw["primary_output_sha256"])
    if not typed_equal(strict_json((directory / "primary-output.json").read_bytes()), raw["observations"]):
        raise ValueError("predecessor native output bytes disagree with raw observations")
    if (checked["schema"] != "finite-worksheet.independent-check.v1"
            or checked["measurement_valid"] is not True or checked["route_agreement"] is not True
            or checked["primary_route"] != raw["route"]
            or checked["plan_sha256"] != plan_sha256
            or not typed_equal(checked["source_sha256"], plan["source_sha256"])
            or not typed_equal(checked["supervisor_provenance_sha256"], prior_provenance)
            or manifest["id"] != trial["run_id"] or manifest["experiment_id"] != plan["experiment_id"]
            or manifest["status"] != "completed_valid" or manifest["result"]["valid"] is not True
            or not typed_equal(manifest["result"]["metrics"]["observations"], raw["observations"])):
        raise ValueError("predecessor independent check/manifest does not bind a valid measurement")
    return raw, checked, digest(directory / "execution-receipt.json")


def compare(observations, criteria):
    details = []
    for criterion in criteria:
        actual = field(observations, criterion["field"])
        expected = criterion["value"]
        op = criterion.get("operator", "equals")
        if op == "equals":
            passed = typed_equal(actual, expected)
        elif op == "not_equals":
            passed = not typed_equal(actual, expected)
        elif op == "not_equals_field":
            expected = field(observations, expected)
            passed = not typed_equal(actual, expected)
        elif op == "all_equals":
            passed = isinstance(actual, list) and all(typed_equal(x, expected) for x in actual)
        else:
            raise ValueError("unimplemented criterion operator")
        details.append({**criterion, "actual": actual, "passed": passed})
    return details


def execute(args):
    started, tick = stamp(), time.monotonic()
    own_before = resource.getrusage(resource.RUSAGE_SELF)
    directory, plan, trial, block, config, launch, environment, provenance = context(args)
    config["primary_route"] = args.route
    if args.mode == "run":
        for name in ARTIFACTS:
            if (directory / name).exists():
                raise ValueError("driver output already exists; no-overwrite execution")
        receipt, output, observations = native(config, args.route, directory)
        with (directory / "primary-output.json").open("xb") as stream:
            stream.write(output)
        raw = {"schema": "finite-worksheet.raw.v1", "experiment_id": plan["experiment_id"],
               "run_id": trial["run_id"], "route": args.route, "seed": None,
               "observations": observations, "primary_output_sha256": digest(directory / "primary-output.json"),
               "plan_sha256": launch["plan_sha256"], "specification_sha256": plan["specification_sha256"],
               "source_sha256": plan["source_sha256"], "supervisor_provenance_sha256": provenance,
               "scope": config["scope"]}
        write(directory / "raw-result.json", raw)
        own = resource.getrusage(resource.RUSAGE_SELF)
        receipt.update(started_at=started, finished_at=stamp(), wall_seconds=time.monotonic()-tick,
                       wrapper_cpu_seconds=own.ru_utime+own.ru_stime-own_before.ru_utime-own_before.ru_stime,
                       wrapper_peak_rss_bytes=own.ru_maxrss*(1 if sys.platform=="darwin" else 1024),
                       total_child_cpu_seconds=resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,
                       total_child_peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*(1 if sys.platform=="darwin" else 1024),
                       supervisor_provenance_sha256=provenance,
                       resource_boundary="primary wrapper context/source verification, compilation, synthetic control, worksheet and raw-output writes; receipt write excluded")
        write(directory / "native-primary.json", receipt)
        return
    raw, primary = read(directory / "raw-result.json"), read(directory / "native-primary.json")
    if (raw["schema"] != "finite-worksheet.raw.v1" or raw["scope"] != config["scope"]
            or raw["experiment_id"] != plan["experiment_id"] or raw["run_id"] != trial["run_id"]
            or raw["route"] != args.route or raw["source_sha256"] != plan["source_sha256"]
            or raw["supervisor_provenance_sha256"] != provenance or raw["seed"] is not None):
        raise ValueError("raw primary metadata changed or is not bound to this trial")
    if raw["plan_sha256"] != launch["plan_sha256"] or raw["specification_sha256"] != plan["specification_sha256"]:
        raise ValueError("raw plan/specification identity mismatch")
    if primary["supervisor_provenance_sha256"] != provenance:
        raise ValueError("primary receipt supervisor provenance mismatch")
    same_hash(directory / "primary-output.json", raw["primary_output_sha256"])
    output = (directory / "primary-output.json").read_bytes()
    if not typed_equal(strict_json(output), raw["observations"]):
        raise ValueError("raw observations do not preserve the primary native output")
    validate_primary(primary, config, args.route, directory, output)
    other = "b" if args.route == "a" else "a"
    independent, _, observed = native(config, other, directory)
    route_agreement = typed_equal(observed, raw["observations"])
    controls = compare(observed, config["controls"])
    predictions = compare(observed, config["predictions"])
    predecessors = []
    for dependency in trial.get("depends_on", []):
        matches = [t for t in plan["trials"] if t["id"] == dependency]
        if len(matches) != 1:
            raise ValueError("nonunique predecessor")
        prior_dir = ROOT / "experiments" / plan["experiment_id"] / "runs" / matches[0]["run_id"]
        prior, prior_check, execution_hash = predecessor(
            prior_dir, plan, matches[0], launch["plan_sha256"], config)
        if prior["route"] == args.route:
            raise ValueError("predecessor is invalid or duplicates this primary route")
        agree = typed_equal(prior["observations"], observed)
        route_agreement &= agree
        predecessors.append({"run_id": prior["run_id"], "raw_sha256": digest(prior_dir / "raw-result.json"),
                             "check_sha256": digest(prior_dir / "independent-check.json"),
                             "execution_receipt_sha256": execution_hash, "agree": agree})
    valid = route_agreement and all(c["passed"] for c in controls)
    prediction_match = all(p["passed"] for p in predictions)
    check = {"schema": "finite-worksheet.independent-check.v1", "primary_route": args.route,
             "independent_route": other, "native": independent, "route_agreement": route_agreement,
             "controls": controls, "prediction_comparisons": predictions,
             "prediction_scope": config["prediction_scope"], "prediction_match": prediction_match,
             "measurement_valid": valid, "predecessors": predecessors,
             "source_sha256": plan["source_sha256"], "plan_sha256": launch["plan_sha256"],
             "supervisor_provenance_sha256": provenance}
    write(directory / "independent-check.json", check)
    witness = {"worksheet_witness": {"experiment_id": plan["experiment_id"], "run_id": trial["run_id"],
               "kind": "finite_arithmetic_recomputation_only", "formal_proof": False,
               "ecdlp_certificate": False, "scope": config["scope"], "route_agreement": route_agreement,
               "measurement_valid": valid, "prediction_match": prediction_match,
               "prediction_scope": config["prediction_scope"], "raw_sha256": digest(directory / "raw-result.json"),
               "independent_check_sha256": digest(directory / "independent-check.json")}}
    write(directory / "certificate.yaml", witness)
    artifacts = {name: digest(directory / name) for name in ARTIFACTS if name != "manifest.yaml"}
    own = resource.getrusage(resource.RUSAGE_SELF)
    records = [primary[k] for k in ("compile", "synthetic_control", "worksheet")]
    records += [independent[k] for k in ("compile", "synthetic_control", "worksheet")]
    peak = max([r["peak_rss_bytes"] for r in records]+[primary["wrapper_peak_rss_bytes"], primary["total_child_peak_rss_bytes"], resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*(1 if sys.platform=="darwin" else 1024), own.ru_maxrss*(1 if sys.platform=="darwin" else 1024)])
    cpu = primary["total_child_cpu_seconds"]+resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime+primary["wrapper_cpu_seconds"]+own.ru_utime+own.ru_stime-own_before.ru_utime-own_before.ru_stime
    manifest = {"run": {"id": trial["run_id"], "experiment_id": plan["experiment_id"],
                "status": "completed_valid" if valid else "completed_invalid",
                "code": {"commit": environment["commit"],
                         "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
                         "command": (directory / "command.txt").read_text().strip()},
                "environment": {**environment, "driver_python_executable": sys.executable,
                                "driver_python_version": sys.version, "compiler": config["compiler"],
                                "supervisor_provenance_sha256": provenance,
                                "resource_boundary": "both primary/checker wrappers and their compilation/synthetic/worksheet processes through core-artifact hashing; final manifest serialization excluded"},
                "inputs": {"curve_id": config["curve_id"], "seed": None,
                           "parameters": {"deterministic": True, "route": args.route,
                                          "source_bindings": config["bindings"],
                                          "specification_sha256": plan["specification_sha256"],
                                          "plan_sha256": launch["plan_sha256"],
                                          "interpretation": block.get("interpretation")}},
                "timing": {"started_at": primary["started_at"], "finished_at": stamp(),
                           "wall_seconds": (datetime.now(timezone.utc)-datetime.fromisoformat(primary["started_at"])).total_seconds()},
                "resources": {"peak_rss_bytes": peak, "cpu_seconds": cpu},
                "result": {"metrics": {"implementations_agree": route_agreement, "measurement_valid": valid,
                                       "prediction_match": prediction_match, "observations": observed},
                           "valid": valid, "invalid_reason": None if valid else "independent routes or explicit frozen controls disagree",
                           "certificate": {"kind": "none", "verified": None, "verifier": None}},
                "artifacts": artifacts}}
    write(directory / "manifest.yaml", manifest)
    if not valid:
        raise ValueError("measurement invalid; outputs and both independent observations retained")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "check"))
    parser.add_argument("--plan", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--route", choices=("a", "b"), required=True)
    args = parser.parse_args()
    try:
        execute(args)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
