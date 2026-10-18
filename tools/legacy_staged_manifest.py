#!/usr/bin/env python3
"""Metadata-only wrapper for an unchanged two-stage legacy instrument.

A prospectively frozen native plan supplies ``legacy_staged`` and two stage
trials. Each invocation copies the bound legacy source/spec/plan into a fresh
workspace, runs the exact old argv/CWD, and retains every actual file in a tar.
Stage 1 imports only the validated Stage 0 globals into its own workspace.
This is not an arithmetic verifier: the old checker is preserved with its
vocabulary/file-presence limitation. Admission/publication remain native gates.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SELF = "tools/legacy_staged_manifest.py"
OUTPUTS = ("manifest.yaml", "raw-result.json", "legacy-execution.json", "legacy-workspace.tar")
PROVENANCE = ("launch.json", "environment.json", "command.txt")
GENERATED = (*PROVENANCE, "stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log")
CHECKER_SCOPE = "Unchanged legacy checker validates outcome vocabulary and file presence only; no independent arithmetic verification."
FORMAT = "crypto.autoresearch.legacy_staged_execution.v1"


class StagedError(ValueError):
    pass


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def same(a: Any, b: Any) -> bool:
    return json_text(a) == json_text(b)


def parse_json(data: bytes | str, *, object_only: bool = True) -> Any:
    def unique(items):
        result = {}
        for k, v in items:
            if k in result:
                raise StagedError(f"duplicate JSON key: {k}")
            result[k] = v
        return result
    value = json.loads(data, object_pairs_hook=unique, parse_constant=lambda x: (_ for _ in ()).throw(StagedError(f"nonfinite JSON: {x}")))
    if object_only and not isinstance(value, dict):
        raise StagedError("expected JSON object")
    return value


def read_json(path: Path) -> dict[str, Any]:
    return parse_json(path.read_bytes())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(name: str) -> str:
    if (not isinstance(name, str) or not name or "\\" in name or "\x00" in name
            or PurePosixPath(name).is_absolute() or str(PurePosixPath(name)) != name
            or any(p in ("..", ".") for p in PurePosixPath(name).parts)):
        raise StagedError(f"noncanonical relative path: {name!r}")
    return name


def inside(root: Path, name: str) -> Path:
    p = root / canonical(name)
    if p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
        raise StagedError(f"path escapes workspace: {name}")
    return p


def checked_hash(path: Path, expected: Any) -> None:
    if (not isinstance(expected, str) or len(expected) != 64
            or any(c not in "0123456789abcdef" for c in expected)
            or path.is_symlink() or not path.is_file() or sha(path) != expected):
        raise StagedError(f"bound file changed/missing: {path}")


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def expand(argv: Any, directory: Path) -> list[str]:
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x or "\x00" in x for x in argv):
        raise StagedError("expected nonempty argv string array")
    return [x.replace("{run_dir}", str(directory)) for x in argv]


@dataclass
class Context:
    root: Path
    path: Path
    directory: Path
    plan: dict[str, Any]
    trial: dict[str, Any]
    block: dict[str, Any]
    stage: dict[str, Any]
    old_plan: dict[str, Any]
    old_trial: dict[str, Any]
    old_spec: dict[str, Any]
    copies: dict[str, str]
    environment: dict[str, Any]
    provenance: dict[str, str]


def context(root: Path, path: Path, directory: Path) -> Context:
    root, path, directory = root.resolve(), path.resolve(), directory.resolve()
    if not path.is_relative_to(root) or not directory.is_relative_to(root):
        raise StagedError("plan/run outside checkout")
    plan = read_json(path)
    b = plan.get("legacy_staged")
    if plan.get("schema") != "crypto.autoresearch.trial_plan.v1" or plan.get("frozen") is not True or not isinstance(b, dict):
        raise StagedError("requires frozen native plan with legacy_staged block")
    required = {"trial_plan", "trial_plan_sha256", "experiment_id", "input_seed", "input_seed_semantics", "curve_id", "checker_scope", "stages"}
    if set(b) != required or type(b["input_seed"]) is not int or not isinstance(b["input_seed_semantics"], str) or not b["input_seed_semantics"].strip() or b["checker_scope"] != CHECKER_SCOPE:
        raise StagedError("incomplete legacy staging/seed/checker contract")
    if b["curve_id"] is not None and not isinstance(b["curve_id"], str):
        raise StagedError("curve_id must be exact ID or null")
    op = inside(root, b["trial_plan"])
    checked_hash(op, b["trial_plan_sha256"])
    old = read_json(op)
    if old.get("frozen") is not True or old.get("experiment_id") != b["experiment_id"]:
        raise StagedError("legacy plan identity/freeze mismatch")
    specpath = inside(root, old["specification"])
    checked_hash(specpath, old["specification_sha256"])
    spec = yaml.safe_load(specpath.read_text())["experiment"]
    if spec.get("id") != b["experiment_id"] or not same(spec.get("inputs", {}).get("seeds", {}).get("null_seed"), b["input_seed"]):
        raise StagedError("legacy specification identity/fixed seed mismatch")
    copies = {**old["source_sha256"], b["trial_plan"]: b["trial_plan_sha256"], old["specification"]: old["specification_sha256"]}
    sources = plan.get("source_sha256", {})
    if SELF not in sources or any(sources.get(n) != h for n, h in copies.items()):
        raise StagedError("new closure does not bind adapter and every legacy dependency")
    for n, h in sources.items():
        checked_hash(inside(root, n), h)
    checked_hash(inside(root, plan["specification"]), plan["specification_sha256"])
    newspec = yaml.safe_load(inside(root, plan["specification"]).read_text())["experiment"]
    if newspec.get("id") != plan["experiment_id"] or plan["experiment_id"] == b["experiment_id"]:
        raise StagedError("requires correctly identified new outer experiment")
    stages = b["stages"]
    if (not isinstance(stages, list) or len(stages) != 2 or not same([s.get("stage") for s in stages], [0, 1])
            or len({s.get("trial_id") for s in stages}) != 2):
        raise StagedError("requires two distinct ordered native stage trials")
    old_trial_ids = set()
    all_globals = set()
    for s in stages:
        if set(s) != {"stage", "trial_id", "legacy_trial_id", "global_outputs", "outcomes", "optional_globals_outcomes"}:
            raise StagedError("incomplete stage contract")
        matches = [t for t in old["trials"] if t["id"] == s["legacy_trial_id"]]
        newmatches = [t for t in plan["trials"] if t["id"] == s["trial_id"]]
        if len(matches) != 1 or len(newmatches) != 1 or matches[0]["id"] in old_trial_ids:
            raise StagedError("stages must select distinct old/native trials")
        old_trial_ids.add(matches[0]["id"])
        ot = matches[0]
        if ot.get("artifacts") != ["manifest.yaml", "raw-result.json", "RESULTS.md"]:
            raise StagedError("expected unchanged three-output legacy run contract")
        av = ot["argv"]
        checkav = ot["check_argv"]
        if (len(av) != 8 or len(checkav) != 3 or av[2:] != ["--stage", str(s["stage"]), "--trial-plan", b["trial_plan"], "--run-dir", "{run_dir}"]
                or checkav[2] != "{run_dir}"):
            raise StagedError("legacy argv stage/plan/run interface mismatch")
        for entrypoint in (av[1], checkav[1]):
            canonical(entrypoint)
            if entrypoint not in old["source_sha256"] or not entrypoint.startswith(f"experiments/{b['experiment_id']}/implementation/"):
                raise StagedError("legacy entrypoint must be an exact copied source-bound file")
        if not isinstance(s["global_outputs"], list) or not s["global_outputs"] or len(set(s["global_outputs"])) != len(s["global_outputs"]):
            raise StagedError("requires explicit unique prospective global paths")
        for n in s["global_outputs"]:
            canonical(n)
            if n in copies or n in all_globals or not n.startswith(f"experiments/{b['experiment_id']}/"):
                raise StagedError("global path overlap/outside legacy experiment")
            all_globals.add(n)
        if (not isinstance(s["outcomes"], list) or not s["outcomes"] or any(not isinstance(x, str) for x in s["outcomes"])
                or not isinstance(s["optional_globals_outcomes"], list) or not set(s["optional_globals_outcomes"]) <= set(s["outcomes"])):
            raise StagedError("invalid frozen outcome/optional global vocabulary")
    if stages[0]["optional_globals_outcomes"] or stages[1]["optional_globals_outcomes"] != ["O-IMPEDIMENT"]:
        raise StagedError("only stage1 O-IMPEDIMENT may omit globals")
    launch = read_json(directory / "launch.json")
    matches = [t for t in plan["trials"] if t["id"] == launch.get("trial_id")]
    if len(matches) != 1:
        raise StagedError("supervisor must select one native trial")
    t = matches[0]
    stages_match = [s for s in stages if s["trial_id"] == t["id"]]
    if len(stages_match) != 1:
        raise StagedError("native trial is not a legacy stage")
    s = stages_match[0]
    ot = next(t for t in old["trials"] if t["id"] == s["legacy_trial_id"])
    expected_depends = [] if s["stage"] == 0 else [stages[0]["trial_id"]]
    if t.get("depends_on", []) != expected_depends or t["run_id"] in {x["run_id"] for x in old["trials"]}:
        raise StagedError("requires new native run IDs and exact stage dependency")
    if len({t["run_id"] for t in plan["trials"]}) != 2 or len(plan["trials"]) != 2:
        raise StagedError("requires exactly two distinct native RUNs")
    if directory != root / "experiments" / plan["experiment_id"] / "runs" / t["run_id"] or launch.get("run_id") != t["run_id"]:
        raise StagedError("native run path/identity mismatch")
    expected_argv = [sys.executable, SELF, "run", "--trial-plan", str(path.relative_to(root)), "--run-dir", "{run_dir}"]
    expected_check = [*expected_argv]; expected_check[2] = "check"
    if not same(t["argv"], expected_argv) or not same(t["check_argv"], expected_check):
        raise StagedError("native adapter command must use actual declared runtime and exact interface")
    if (launch.get("plan_sha256") != sha(path) or not same(launch.get("argv"), expand(t["argv"], directory))
            or not same(launch.get("check_argv"), expand(t["check_argv"], directory))
            or not same(parse_json((directory / "command.txt").read_bytes(), object_only=False), launch["argv"])):
        raise StagedError("supervisor command/plan provenance mismatch")
    env = read_json(directory / "environment.json")
    if (not same(env.get("source_sha256"), sources) or env.get("specification_sha256") != plan["specification_sha256"]
            or env.get("commit") != launch.get("authority", {}).get("commit")):
        raise StagedError("supervisor environment/source binding mismatch")
    commit = env.get("commit")
    if not isinstance(commit, str) or len(commit) != 40 or any(x not in "0123456789abcdef" for x in commit):
        raise StagedError("missing actual execution commit")
    if t.get("artifacts") != list(OUTPUTS):
        raise StagedError("declare exact four staged adapter outputs")
    for v in (ot["argv"][0], ot["check_argv"][0]):
        executable = shutil.which(v)
        if executable is None or not os.path.samefile(executable, sys.executable):
            raise StagedError("legacy interpreter must resolve to actual adapter runtime")
    return Context(root, path, directory, plan, t, b, s, old, ot, spec, copies, env, {n: sha(directory / n) for n in PROVENANCE})


def archive_files(path: Path) -> dict[str, bytes]:
    files = {}
    with tarfile.open(path, "r:") as archive:
        for member in archive:
            n = canonical(member.name)
            if n in files or not member.isfile():
                raise StagedError("archive duplicate/nonregular member")
            stream = archive.extractfile(member)
            assert stream is not None
            files[n] = stream.read()
    return files


def snapshot(workspace: Path, archive_path: Path) -> dict[str, str]:
    with archive_path.open("xb") as stream:
        with tarfile.open(fileobj=stream, mode="w:", format=tarfile.PAX_FORMAT, dereference=False) as archive:
            for p in sorted(workspace.rglob("*")):
                if p.is_dir() and not p.is_symlink():
                    continue
                archive.add(p, arcname=p.relative_to(workspace).as_posix(), recursive=False)
        stream.flush(); os.fsync(stream.fileno())
    files = archive_files(archive_path)
    actual = {p.relative_to(workspace).as_posix(): p.read_bytes() for p in workspace.rglob("*") if p.is_file() and not p.is_symlink()}
    if not same({n: hashlib.sha256(d).hexdigest() for n, d in files.items()}, {n: hashlib.sha256(d).hexdigest() for n, d in actual.items()}):
        raise StagedError("durable archive differs from actual staged files")
    return {n: hashlib.sha256(d).hexdigest() for n, d in files.items()}


def legacy_run(c: Context, workspace: Path) -> Path:
    return workspace / "experiments" / c.block["experiment_id"] / "runs" / c.old_trial["run_id"]


def expected_paths(c: Context) -> list[str]:
    prefix = f"experiments/{c.block['experiment_id']}/runs/{c.old_trial['run_id']}/"
    previous = c.block["stages"][0]["global_outputs"] if c.stage["stage"] == 1 else []
    return sorted(set(c.copies) | {prefix + n for n in c.old_trial["artifacts"]}
                  | set(previous) | set(c.stage["global_outputs"]))


def validate_files(c: Context, files: dict[str, bytes], predecessor: dict[str, Any] | None) -> dict[str, Any]:
    prefix = f"experiments/{c.block['experiment_id']}/runs/{c.old_trial['run_id']}/"
    run_names = {prefix + n for n in c.old_trial["artifacts"]}
    previous_names = set(c.block["stages"][0]["global_outputs"]) if c.stage["stage"] == 1 else set()
    allowed = set(expected_paths(c))
    if not set(files) <= allowed or not (set(c.copies) | run_names | previous_names) <= set(files):
        raise StagedError("archive has undeclared files or misses required sources/local/dependency outputs")
    for n, h in c.copies.items():
        if hashlib.sha256(files[n]).hexdigest() != h:
            raise StagedError(f"staged source copy changed: {n}")
    raw = parse_json(files[prefix + "raw-result.json"])
    oldmanifest = yaml.safe_load(files[prefix + "manifest.yaml"])
    if (not same(raw.get("stage"), c.stage["stage"]) or raw.get("outcome") not in c.stage["outcomes"]
            or not same(raw.get("claims"), {"attack": False, "break": False, "exponent_move": False})
            or not isinstance(oldmanifest, dict) or oldmanifest.get("experiment_id") != c.block["experiment_id"]
            or not same(oldmanifest.get("stage"), c.stage["stage"]) or oldmanifest.get("outcome") != raw["outcome"]):
        raise StagedError("legacy result/manifest stage/outcome/no-claim identity mismatch")
    if raw["outcome"] not in c.stage["optional_globals_outcomes"] and not set(c.stage["global_outputs"]) <= set(files):
        raise StagedError("required legacy global output missing")
    if predecessor is not None:
        if not same({n: hashlib.sha256(files[n]).hexdigest() for n in previous_names}, predecessor["stage0_global_sha256"]):
            raise StagedError("stage0 globals changed in stage1 workspace")
    return raw


def child(argv: list[str], cwd: Path) -> dict[str, Any]:
    if not hasattr(os, "wait4"):
        raise StagedError("POSIX wait4 required for per-child resources")
    start = datetime.now(timezone.utc).isoformat(); before = time.monotonic()
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        _, status, usage = os.wait4(process.pid, 0)
        process.returncode = os.waitstatus_to_exitcode(status)
    except BaseException:
        process.terminate(); process.wait(); raise
    return {"argv": argv, "cwd": str(cwd), "resolved_executable": str(Path(shutil.which(argv[0])).resolve()),
            "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"}, "returncode": process.returncode,
            "started_at": start, "finished_at": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic() - before,
            "cpu_seconds": usage.ru_utime + usage.ru_stime,
            "peak_rss_bytes": usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024)}


def predecessor(c: Context) -> tuple[dict[str, Any] | None, dict[str, bytes]]:
    if c.stage["stage"] == 0:
        return None, {}
    first = next(t for t in c.plan["trials"] if t["id"] == c.block["stages"][0]["trial_id"])
    directory = c.root / "experiments" / c.plan["experiment_id"] / "runs" / first["run_id"]
    native = read_json(directory / "execution-receipt.json")
    expected = {"schema": "crypto.autoresearch.trial_receipt.v1", "plan_sha256": sha(c.path), "trial_id": first["id"],
                "run_id": first["run_id"], "status": "output_validated", "returncode": 0, "check_returncode": 0}
    if any(not same(native.get(k), v) for k, v in expected.items()):
        raise StagedError("stage1 requires validated native stage0 receipt")
    hashes = native.get("artifact_sha256")
    if not isinstance(hashes, dict) or set(hashes) != set(OUTPUTS) | set(GENERATED):
        raise StagedError("stage0 native receipt artifact coverage incomplete")
    for n, h in hashes.items():
        checked_hash(inside(directory, n), h)
    pc = context(c.root, c.path, directory)
    validate_saved(pc, None)
    files = archive_files(directory / "legacy-workspace.tar")
    selected = {n: files[n] for n in c.block["stages"][0]["global_outputs"]}
    binding = {"trial_id": first["id"], "run_id": first["run_id"], "native_receipt_sha256": sha(directory / "execution-receipt.json"),
               "workspace_archive_sha256": sha(directory / "legacy-workspace.tar"), "stage0_global_sha256": {n: hashlib.sha256(d).hexdigest() for n, d in selected.items()}}
    return binding, selected


def canonical_manifest(c: Context, r: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    return {"run": {"id": c.trial["run_id"], "experiment_id": c.plan["experiment_id"], "status": "completed_valid",
        "code": {"commit": c.environment["commit"], "dirty": r["dirty"], "command": (c.directory / "command.txt").read_text().strip()},
        "environment": {"supervisor": c.environment, "supervisor_sha256": c.provenance, "adapter_runtime": r["runtime"],
            "working_directory": str(c.root), "legacy_working_directory": r["workspace"], "checker_scope": CHECKER_SCOPE,
            "timing_boundary": "Before workspace creation through exact source/dependency copies, legacy driver/checker, durable archive equality check and pre-envelope validation; excludes context/git/predecessor validation, envelope emission and separate native checker.",
            "resource_boundary": "Sum of legacy driver/checker per-child CPU, maximum of their per-process RSS peaks; excludes adapter/archive/checker replay and is not aggregate process-group RSS.",
            "inference": "No inference performed or attested by adapter."},
        "inputs": {"curve_id": c.block["curve_id"], "seed": c.block["input_seed"], "parameters": {"legacy_staged": c.block,
            "legacy_stage": c.stage, "legacy_trial_run_id": c.old_trial["run_id"], "legacy_inputs": c.old_spec.get("inputs"), "predecessor": r["predecessor"]}},
        "timing": r["timing"], "resources": {"cpu_seconds": sum(p["cpu_seconds"] for p in r["phases"]), "peak_rss_bytes": max(p["peak_rss_bytes"] for p in r["phases"])},
        "result": {"metrics": {"legacy_stage": raw["stage"], "legacy_outcome": raw["outcome"], "legacy_raw_result": raw}, "valid": True,
                   "invalid_reason": None, "certificate": {"kind": "none", "verified": None, "verifier": None}},
        "artifacts": {n: {"sha256": sha(c.directory / n)} for n in OUTPUTS if n != "manifest.yaml"}}}


def execute(path: Path, directory: Path, *, root: Path = ROOT) -> None:
    c = context(root, path, directory)
    if any((c.directory / n).exists() for n in OUTPUTS) or any(c.directory.glob("legacy-staged-*")):
        raise StagedError("consumed outputs/workspace exist; preserve attempt and allocate new RUN")
    dependency, previous_files = predecessor(c)
    status = subprocess.run(["git", "-C", str(c.root), "status", "--porcelain", "--untracked-files=normal"], text=True, capture_output=True, check=True)
    r = {"schema": FORMAT, "experiment_id": c.plan["experiment_id"], "run_id": c.trial["run_id"], "plan_sha256": sha(c.path),
         "source_sha256": c.plan["source_sha256"], "supervisor_sha256": c.provenance, "legacy_staged": c.block, "stage": c.stage,
         "predecessor": dependency, "runtime": {"python": sys.version, "executable": sys.executable, "pyyaml": yaml.__version__},
         "dirty": bool(status.stdout), "dirty_boundary": "whole worktree after context/dependency validation and before isolated workspace creation, including supervisor files",
         "checker_scope": CHECKER_SCOPE, "phases": [], "workspace_file_sha256": {},
         "workspace_expected_paths": expected_paths(c), "workspace_absent_paths": [], "status": "started"}
    start = datetime.now(timezone.utc).isoformat(); before = time.monotonic()
    workspace = Path(tempfile.mkdtemp(prefix="legacy-staged-", dir=c.directory)); r["workspace"] = str(workspace)
    error = None; raw = None
    try:
        for n in c.copies:
            write_once(inside(workspace, n), inside(c.root, n).read_bytes())
        for n, data in previous_files.items():
            write_once(inside(workspace, n), data)
        rd = legacy_run(c, workspace); rd.mkdir(parents=True, exist_ok=False)
        for kind, argv in (("legacy_driver", c.old_trial["argv"]), ("legacy_checker", c.old_trial["check_argv"])):
            phase = child(expand(argv, rd), workspace); r["phases"].append({"kind": kind, **phase})
            if phase["returncode"] != 0:
                raise StagedError(f"{kind} failed: {phase['returncode']}")
    except BaseException as exc:
        error = exc
    finally:
        try:
            r["workspace_file_sha256"] = snapshot(workspace, c.directory / "legacy-workspace.tar")
            r["workspace_absent_paths"] = sorted(set(expected_paths(c)) - set(r["workspace_file_sha256"]))
            shutil.rmtree(workspace)
            files = archive_files(c.directory / "legacy-workspace.tar")
            rawname = f"experiments/{c.block['experiment_id']}/runs/{c.old_trial['run_id']}/raw-result.json"
            if rawname in files:
                write_once(c.directory / "raw-result.json", files[rawname])
            if error is None:
                raw = validate_files(c, files, dependency)
                refreshed = context(c.root, c.path, c.directory)
                if not same(refreshed.provenance, c.provenance) or not same(predecessor(c)[0], dependency):
                    raise StagedError("supervisor/dependency provenance changed during execution")
                r["status"] = "legacy_instrument_checked"
        except BaseException as exc:
            if error is None: error = exc
        if error is not None:
            r["status"] = "failed"; r["error"] = {"type": type(error).__name__, "message": str(error)}
        r["timing"] = {"started_at": start, "finished_at": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic() - before}
        r["output_sha256"] = {n: sha(c.directory / n) for n in ("legacy-workspace.tar", "raw-result.json") if (c.directory / n).is_file()}
        write_once(c.directory / "legacy-execution.json", json_text(r).encode())
    if error is not None:
        raise StagedError(str(error)) from error
    write_once(c.directory / "manifest.yaml", yaml.safe_dump(canonical_manifest(c, r, raw), sort_keys=False).encode())


def measured(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_saved(c: Context, dependency: dict[str, Any] | None) -> dict[str, Any]:
    r = read_json(c.directory / "legacy-execution.json")
    expected = {"schema": FORMAT, "experiment_id": c.plan["experiment_id"], "run_id": c.trial["run_id"], "plan_sha256": sha(c.path),
                "source_sha256": c.plan["source_sha256"], "supervisor_sha256": c.provenance, "legacy_staged": c.block, "stage": c.stage,
                "predecessor": dependency, "checker_scope": CHECKER_SCOPE, "workspace_expected_paths": expected_paths(c),
                "dirty_boundary": "whole worktree after context/dependency validation and before isolated workspace creation, including supervisor files",
                "status": "legacy_instrument_checked"}
    if any(not same(r.get(k), v) for k, v in expected.items()) or type(r.get("dirty")) is not bool:
        raise StagedError("saved execution/provenance binding mismatch")
    workspace = Path(r.get("workspace", ""))
    if workspace.parent != c.directory or not workspace.name.startswith("legacy-staged-") or workspace.exists():
        raise StagedError("invalid/unconsumed isolated workspace")
    phases = r.get("phases", [])
    if [p.get("kind") for p in phases] != ["legacy_driver", "legacy_checker"]:
        raise StagedError("requires actual original driver and checker phases")
    adapter_start = datetime.fromisoformat(r["timing"]["started_at"])
    adapter_finish = datetime.fromisoformat(r["timing"]["finished_at"])
    if adapter_start.tzinfo is None or adapter_finish.tzinfo is None or adapter_finish < adapter_start:
        raise StagedError("adapter timestamp interval invalid")
    previous_finish = adapter_start
    for p, av in zip(phases, (c.old_trial["argv"], c.old_trial["check_argv"])):
        expected_phase = {"argv": expand(av, legacy_run(c, workspace)), "cwd": str(workspace), "resolved_executable": str(Path(shutil.which(av[0])).resolve()),
                          "environment_overrides": {"PYTHONDONTWRITEBYTECODE": "1"}, "returncode": 0}
        if any(not same(p.get(k), v) for k, v in expected_phase.items()) or any(not measured(p.get(n)) for n in ("wall_seconds", "cpu_seconds", "peak_rss_bytes")):
            raise StagedError("original child command/resource binding mismatch")
        phase_start = datetime.fromisoformat(p["started_at"])
        phase_finish = datetime.fromisoformat(p["finished_at"])
        if (phase_start.tzinfo is None or phase_finish.tzinfo is None or not previous_finish <= phase_start <= phase_finish <= adapter_finish):
            raise StagedError("phase timestamp interval outside measured adapter boundary")
        previous_finish = phase_finish
    if not measured(r.get("timing", {}).get("wall_seconds")):
        raise StagedError("invalid measured adapter wall time")
    for n in ("started_at", "finished_at"):
        if datetime.fromisoformat(r["timing"][n]).tzinfo is None: raise StagedError("timing timezone missing")
    if not same(r.get("runtime"), {"python": sys.version, "executable": sys.executable, "pyyaml": yaml.__version__}):
        raise StagedError("runtime mismatch")
    if set(r.get("output_sha256", {})) != {"legacy-workspace.tar", "raw-result.json"}:
        raise StagedError("output hash coverage incomplete")
    for n, h in r["output_sha256"].items(): checked_hash(c.directory / n, h)
    files = archive_files(c.directory / "legacy-workspace.tar")
    if not same({n: hashlib.sha256(d).hexdigest() for n, d in files.items()}, r["workspace_file_sha256"]):
        raise StagedError("archive inventory hashes changed")
    if not same(r.get("workspace_absent_paths"), sorted(set(expected_paths(c)) - set(files))):
        raise StagedError("archive absent-path inventory mismatch")
    raw = validate_files(c, files, dependency)
    n = f"experiments/{c.block['experiment_id']}/runs/{c.old_trial['run_id']}/raw-result.json"
    if (c.directory / "raw-result.json").read_bytes() != files[n]:
        raise StagedError("raw legacy bytes differ from archive")
    if not same(yaml.safe_load((c.directory / "manifest.yaml").read_bytes()), canonical_manifest(c, r, raw)):
        raise StagedError("native envelope differs from original bytes/provenance")
    return files


def check(path: Path, directory: Path, *, root: Path = ROOT) -> None:
    c = context(root, path, directory)
    dependency, _ = predecessor(c)
    files = validate_saved(c, dependency)
    # Reconstitute exact bytes, never extract paths/links using tar.extractall.
    with tempfile.TemporaryDirectory(prefix="legacy-staged-check-") as temporary:
        scratch = Path(temporary)
        for n, data in files.items(): write_once(inside(scratch, n), data)
        completed = subprocess.run(expand(c.old_trial["check_argv"], legacy_run(c, scratch)), cwd=scratch, stdin=subprocess.DEVNULL,
                                   env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), check=False)
        if completed.returncode != 0:
            raise StagedError(f"preserved unchanged checker rejected archive: {completed.returncode}")
    print(CHECKER_SCOPE)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("run", "check")); p.add_argument("--trial-plan", type=Path, required=True); p.add_argument("--run-dir", type=Path, required=True)
    a = p.parse_args()
    try:
        (execute if a.action == "run" else check)(a.trial_plan, a.run_dir)
    except (OSError, ValueError, subprocess.SubprocessError, yaml.YAMLError) as exc:
        print(f"legacy staged adapter refused: {exc}", file=sys.stderr); return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
