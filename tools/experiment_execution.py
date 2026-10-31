#!/usr/bin/env python3
"""Run frozen trial plans inside an already-authorized, claimed executor task.

This is an execution adapter, not another Coordinator or claim service. It
never approves work, releases claims, commits artifacts, or interprets results.
Every process launch reuses research_dispatch.py's current claim/authority view.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import copy
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import yaml

try:  # libyaml, with the pure loader's errors (orchestration/fast_yaml.py)
    import fast_yaml
except ImportError:  # imported as tools.<name>, the repository root importable
    from orchestration import fast_yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sparse_checkout  # noqa: E402
import artifact_store  # noqa: E402

PLAN_SCHEMA = "crypto.autoresearch.trial_plan.v1"
RECEIPT_SCHEMA = "crypto.autoresearch.trial_receipt.v1"
REPO = Path(__file__).resolve().parents[1]
GENERATED = ("launch.json", "execution-receipt.json", "command.txt",
             "environment.json", "stdout.log", "stderr.log", "check.stdout.log",
             "check.stderr.log")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RUN_ID = re.compile(r"RUN-[A-Za-z0-9]+-[0-9a-f]{6}\Z")


class ExecutionError(ValueError):
    """An operational or protocol impediment; never negative scientific evidence."""


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExecutionError(f"{path}: expected a JSON object")
    return value


def safe_path(root: Path, relative: str) -> Path:
    """Require canonical relative paths and reject symlinks in every component."""
    if not isinstance(relative, str) or not relative or any(c in relative for c in "\x00\n\r\t\\"):
        raise ExecutionError(f"unsafe path: {relative!r}")
    rel = PurePosixPath(relative)
    if (rel.is_absolute() or ".." in rel.parts or rel.as_posix() != relative
            or relative in (".", "")):
        raise ExecutionError(f"unsafe path: {relative!r}")
    current = root.resolve()
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ExecutionError(f"symlink not allowed: {current}")
    return current


def write_once(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def positive(value: Any, field: str) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0):
        raise ExecutionError(f"{field}: expected a finite positive number")


def load_plan(root: Path, path: Path, *, allow_preapproval_candidate: bool = False) -> dict[str, Any]:
    path = path.absolute()
    try:
        safe_path(root, path.relative_to(root.resolve()).as_posix())
    except ValueError as error:
        raise ExecutionError("trial plan must be inside the checkout") from error
    plan = read_json(path)
    if plan.get("schema") != PLAN_SCHEMA or plan.get("frozen") is not True:
        raise ExecutionError("trial plan must use the supported schema and be frozen")
    if ("stop_on_invalid_output" in plan and
            not isinstance(plan["stop_on_invalid_output"], bool)):
        raise ExecutionError("stop_on_invalid_output must be Boolean when present")
    for field in ("experiment_id", "task_id", "specification", "queue"):
        if not isinstance(plan.get(field), str) or not plan[field].strip():
            raise ExecutionError(f"missing {field}")
    if allow_preapproval_candidate:
        if (plan.get("candidate_only") is not True or
                plan.get("approval_required") is not True or
                plan.get("approved_by") not in (None, "")):
            raise ExecutionError("preapproval readiness requires a candidate-only plan with no approver")
    else:
        if plan.get("candidate_only") is True:
            raise ExecutionError("candidate-only trial plans cannot execute; rebuild after Coordinator approval")
        if not isinstance(plan.get("approved_by"), str) or not plan["approved_by"].strip():
            raise ExecutionError("missing approved_by")
    spec_path = safe_path(root, plan["specification"])
    if spec_path.parent.name != plan["experiment_id"]:
        raise ExecutionError("specification/experiment ID mismatch")
    if not SHA256.fullmatch(str(plan.get("specification_sha256", ""))):
        raise ExecutionError("missing specification_sha256")
    if sha256(spec_path) != plan["specification_sha256"]:
        raise ExecutionError("specification hash changed; use an additive amendment")
    try:
        document = fast_yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ExecutionError(f"malformed specification: {error}") from error
    if not isinstance(document, dict):
        raise ExecutionError("specification is not a mapping")
    spec = document.get("experiment", document)
    # Expand after a Stages 0-1 package review may leave status=running while
    # further execution_authorized stages remain runnable (DEC expand).
    # Expand after Stages 0-1 review leaves status=running while further
    # execution_authorized stages remain runnable (DEC expand / standing auth).
    if allow_preapproval_candidate:
        if (not isinstance(spec, dict) or spec.get("id") != plan["experiment_id"]
                or spec.get("status") != "review_required"
                or spec.get("frozen") is not True
                or spec.get("approved_by") not in (None, "")
                or spec.get("execution_authorized") is not False):
            raise ExecutionError("candidate readiness requires an unapproved frozen review_required specification")
    elif (not isinstance(spec, dict) or spec.get("id") != plan["experiment_id"]
            or spec.get("status") not in ("approved", "running")
            or spec.get("frozen") is not True
            or not spec.get("approved_by") or spec.get("execution_authorized") is False):
        raise ExecutionError("specification is not approved/running, frozen and execution-authorized")
    safe_path(root, plan["queue"])
    sources = plan.get("source_sha256")
    if not isinstance(sources, dict) or not sources:
        raise ExecutionError("source_sha256 must bind the driver, checker and dependencies")
    for source, digest in sources.items():
        safe_path(root, source)
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ExecutionError(f"invalid source hash: {source}")
    trials = plan.get("trials")
    if not isinstance(trials, list) or not trials:
        raise ExecutionError("trials must explicitly enumerate the frozen protocol; no empty plans")
    ids: set[str] = set()
    runs: set[str] = set()
    for trial in trials:
        if not isinstance(trial, dict):
            raise ExecutionError("trial must be an object")
        tid, rid = trial.get("id"), trial.get("run_id")
        if not isinstance(tid, str) or not tid.strip() or tid in ids:
            raise ExecutionError("trial IDs must be nonempty and unique")
        if not isinstance(rid, str) or not RUN_ID.fullmatch(rid) or rid in runs:
            raise ExecutionError("run IDs must be unique, allocated random-suffix RUN IDs")
        ids.add(tid)
        runs.add(rid)
        for field in ("argv", "check_argv"):
            argv = trial.get(field)
            if (not isinstance(argv, list) or not argv or not all(
                    isinstance(arg, str) and arg and "\x00" not in arg for arg in argv)):
                raise ExecutionError(f"{tid}.{field}: expected argv array, never a shell string")
            # A hash-bound source must occur literally in both commands. Commands
            # and the complete source closure are still reviewed as part of the plan.
            if any("bedrock" in arg.lower() for arg in argv):
                raise ExecutionError("Bedrock is prohibited")
            if not any(source in argv for source in sources):
                raise ExecutionError(f"{tid}.{field}: no hash-bound source")
        artifacts = trial.get("artifacts")
        if (not isinstance(artifacts, list) or not artifacts
                or not all(isinstance(name, str) and name for name in artifacts)
                or len(set(artifacts)) != len(artifacts)
                or "manifest.yaml" not in artifacts or "raw-result.json" not in artifacts):
            raise ExecutionError(f"{tid}: require manifest.yaml and raw-result.json artifacts")
        for name in artifacts:
            safe_path(run_root(root, plan, trial), name)
            if name in GENERATED:
                raise ExecutionError(f"{tid}: reserved artifact name {name}")
        allow_empty = trial.get("allow_empty_artifacts", [])
        if (not isinstance(allow_empty, list)
                or not all(isinstance(name, str) and name for name in allow_empty)
                or len(set(allow_empty)) != len(allow_empty)):
            raise ExecutionError(f"{tid}.allow_empty_artifacts: expected unique artifact names")
        for name in allow_empty:
            safe_path(run_root(root, plan, trial), name)
            if name in GENERATED or name not in artifacts:
                raise ExecutionError(f"{tid}.allow_empty_artifacts: undeclared or reserved artifact {name}")
            if name in ("manifest.yaml", "raw-result.json"):
                # An empty run record would pass a schema gate that has nothing
                # to read (SHF-20261028-0f3f64, LGN-3).
                raise ExecutionError(f"{tid}.allow_empty_artifacts: {name} is a run record "
                                     "and may never be empty")
        positive(trial.get("memory_mb"), f"{tid}.memory_mb")
        watchdog = trial.get("watchdog_seconds")
        if watchdog is not None:
            positive(watchdog, f"{tid}.watchdog_seconds")
            if not isinstance(trial.get("watchdog_reason"), str) or not trial["watchdog_reason"].strip():
                raise ExecutionError("watchdog requires an explicit machine-protection reason")
    # Dependencies must refer to earlier declared trials: this is a frozen,
    # deterministic topological order, not an adaptive search/stopping policy.
    earlier: set[str] = set()
    for trial in trials:
        dependencies = trial.get("depends_on", [])
        if (not isinstance(dependencies, list) or not all(isinstance(x, str) for x in dependencies)
                or len(set(dependencies)) != len(dependencies) or not set(dependencies) <= earlier):
            raise ExecutionError("trial dependencies must be unique IDs of earlier trials")
        earlier.add(trial["id"])
    return plan


def manifest_schema_errors(manifest: Path) -> list[str]:
    """Run-schema defects in a trial's manifest.yaml, as tools/validate_ledger.py
    reports them. A manifest that fails the schema is a ledger error the day it
    is committed (RUN-SEMBIN-9ecb77 entered main this way, sheriff case
    SHF-20261017-e4d7f6 M2-R), so it is invalid output, never a validated run.
    Schema only: cross-record references are the full validator's job."""
    import validate_ledger  # noqa: PLC0415 -- heavy; only after a trial succeeds
    ctx = validate_ledger.Ctx(set())
    validate_ledger.check_run(str(manifest), ctx)
    return [error.split(": ", 1)[-1] for error in ctx.errors]


COMPLETION_SCHEMA = "crypto.autoresearch.run_envelope_completion.v1"


class EnvelopeRefused(ExecutionError):
    """A driver manifest the supervisor may not complete or publish."""


def _same(left: Any, right: Any) -> bool:
    """Type-strict, recursive equality: 1.0, True and "1" are not 1."""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_same(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(map(_same, left, right))
    return left == right


def _conflicts(driver: Any, fact: Any) -> bool:
    """A driver value contradicts a fact. Mappings conflict only on keys both
    state (a driver may record derived extras, or fewer keys); everything
    else is compared type-strictly."""
    if isinstance(driver, dict) and isinstance(fact, dict):
        return any(_conflicts(driver[key], fact[key]) for key in driver.keys() & fact.keys())
    return not _same(driver, fact)


def _agree(body: dict[str, Any], field: str, value: Any, where: str,
           source: str = "the frozen plan") -> None:
    if field in body and _conflicts(body[field], value):
        raise EnvelopeRefused(f"driver manifest {where}{field}={body[field]!r} contradicts "
                              f"{source}'s {value!r}")


def _instant(value: Any, field: str) -> datetime:
    if isinstance(value, datetime):
        moment = value
    elif isinstance(value, str):
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise EnvelopeRefused(f"driver manifest {field}={value!r} is not an ISO 8601 "
                                  "time and cannot be checked against the supervisor clock") from error
    else:
        raise EnvelopeRefused(f"driver manifest {field}={value!r} is not a time")
    if moment.tzinfo is None:
        raise EnvelopeRefused(f"driver manifest {field}={value!r} has no time zone and "
                              "cannot be checked against the supervisor clock")
    return moment


LAUNCH_ENVIRONMENT_FACTS = ("commit", "source_sha256", "specification_sha256",
                            "runtime_lock", "runtime_lock_sha256")


def _same_interpreter(program: str) -> bool:
    """True when the driver was launched with the supervisor's own Python."""
    found = shutil.which(program)
    try:
        return bool(found) and os.path.samefile(found, sys.executable)
    except OSError:
        return False


# A driver's own clock reads inside the supervisor's interval, possibly
# truncated to whole seconds; anything further outside is a contradiction.
CLOCK_SLACK_SECONDS = 1.0


def _check_driver_facts(body: dict[str, Any], plan: dict[str, Any], plan_relative: str,
                        plan_hash: str, trial: dict[str, Any], authority: dict[str, Any],
                        environment: dict[str, Any], argv: list[str], checker: list[str],
                        started: str, driver_finished: str, raw: Any) -> None:
    """Refuse every driver value that contradicts a fact the supervisor holds.

    Facts: the frozen plan and trial, the launch authority, environment.json,
    the launched argv and the supervisor's clock, plus the driver's own
    raw-result.json. A key the driver omitted is not checked here (completion
    supplies it); a key with no publish-time source is the driver's own and is
    kept as written. Nothing is ever overwritten (SHF-20261028-0f3f64, LGN-2).
    """
    for alias in ("id", "run_id"):
        _agree(body, alias, trial["run_id"], "run.")
    _agree(body, "experiment_id", plan["experiment_id"], "run.")
    _agree(body, "task_id", plan["task_id"], "run.")
    _agree(body, "trial_id", trial["id"], "run.", "the frozen trial")
    _agree(body, "approved_by", plan["approved_by"], "run.")
    if isinstance(plan.get("hypothesis_id"), str) and plan["hypothesis_id"].strip():
        _agree(body, "hypothesis_id", plan["hypothesis_id"], "run.")
    code = body.get("code", {})
    _agree(code, "commit", authority["commit"], "run.code.", "the launch authority")
    for field, launched in (("command", argv), ("check_command", checker)):
        # The launched argv, as a JSON array (what completion writes), as that
        # array itself, or shell-quoted. Any other value names another command.
        # A driver records its own interpreter as sys.executable, which is the
        # absolute path of a bare `python3` in the frozen argv; when the two
        # resolve to the same file that spelling is the same command, not a
        # contradiction.
        forms = (json.dumps(launched), launched, shlex.join(launched),
                 shlex.join([sys.executable, *launched[1:]]))
        if field in code and not any(_same(code[field], form) for form in forms):
            raise EnvelopeRefused(f"driver manifest run.code.{field}={code[field]!r} "
                                  f"contradicts the launched argv {json.dumps(launched)}")
    _agree(code, "command_file", "command.txt", "run.code.", "the supervisor")
    driver_environment = body.get("environment", {})
    _agree(driver_environment, "file", "environment.json", "run.environment.", "the supervisor")
    # environment.json binds the launch (commit, hashed sources, runtime lock)
    # and also describes the SUPERVISOR's own process (python, platform). Only
    # the binding is a fact about the driver: a driver may run under another
    # interpreter and may describe its platform differently (sys.platform vs
    # platform.platform(), EXP-ICPERF-018b0c), so those strings are its own.
    for key in LAUNCH_ENVIRONMENT_FACTS:
        if key in environment:
            _agree(driver_environment, key, environment[key], "run.environment.",
                   "environment.json")
    if ("python" in driver_environment and isinstance(environment.get("python"), str)
            and _same_interpreter(argv[0])):
        # Same interpreter: the driver's Python must at least name its version.
        version = environment["python"].split()[0] if environment["python"].split() else ""
        if version not in str(driver_environment["python"]):
            raise EnvelopeRefused(f"driver manifest run.environment.python="
                                  f"{driver_environment['python']!r} contradicts the "
                                  f"launched interpreter's Python {version}")
    inputs = body.get("inputs", {})
    _agree(inputs, "trial_plan", plan_relative, "run.inputs.")
    _agree(inputs, "plan_sha256", plan_hash, "run.inputs.", "the frozen plan file")
    _agree(inputs, "trial_id", trial["id"], "run.inputs.", "the frozen trial")
    for key in ("parameters", "seed", "curve_id"):
        if key in trial:
            _agree(inputs, key, trial[key], "run.inputs.", "the frozen trial")
    timing = body.get("timing", {})
    start, finish = datetime.fromisoformat(started), datetime.fromisoformat(driver_finished)
    wall = (finish - start).total_seconds()
    for key in ("started_at", "finished_at"):
        if key in timing:
            moment = _instant(timing[key], f"run.timing.{key}")
            if not (start.timestamp() - CLOCK_SLACK_SECONDS <= moment.timestamp()
                    <= finish.timestamp() + CLOCK_SLACK_SECONDS):
                raise EnvelopeRefused(f"driver manifest run.timing.{key}={timing[key]!r} "
                                      f"contradicts the supervisor's driver interval "
                                      f"{started} .. {driver_finished}")
    if "wall_seconds" in timing:
        seconds = timing["wall_seconds"]
        if (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
                or not math.isfinite(seconds) or seconds < 0
                or seconds > wall + CLOCK_SLACK_SECONDS):
            raise EnvelopeRefused(f"driver manifest run.timing.wall_seconds={seconds!r} "
                                  f"contradicts the supervisor's {wall} s around the driver")
    result = body.get("result", {})
    if "metrics" in body and "metrics" in result and not _same(body["metrics"], result["metrics"]):
        raise EnvelopeRefused(f"driver manifest run.result.metrics={result['metrics']!r} "
                              f"contradicts run.metrics={body['metrics']!r}")
    _agree(result, "raw_result", "raw-result.json", "run.result.", "the trial's artifacts")
    if (isinstance(raw, dict) and "attack_claimed" in raw and "attack_claimed" in body
            and not _same(body["attack_claimed"], raw["attack_claimed"])):
        raise EnvelopeRefused(f"driver manifest run.attack_claimed={body['attack_claimed']!r} "
                              f"contradicts raw-result.json's {raw['attack_claimed']!r}")


# Where each key completion may add comes from (SHF-20261028-0f3f64, LGN-4).
_LATER = "supervisor constant; the supervisor writes this file after completion"
ADDED_FIELD_SOURCES = {
    "run.id": "frozen trial run_id",
    "run.experiment_id": "frozen plan experiment_id",
    "run.hypothesis_id": "frozen plan hypothesis_id",
    "run.task_id": "frozen plan task_id",
    "run.trial_id": "frozen trial id",
    "run.approved_by": "frozen plan approved_by",
    "run.status": "derived: the driver exited 0",
    "run.status_note": "supervisor constant explaining run.status",
    "run.code.commit": "launch authority commit",
    "run.code.commit_meaning": "supervisor constant",
    "run.code.command_file": "supervisor constant (command.txt, written at launch)",
    "run.code.command": "launched argv, equal to command.txt",
    "run.code.check_command": "launched checker argv",
    "run.environment": "environment.json, plus file: environment.json",
    "run.inputs": "frozen plan path and hash, frozen trial id, seed, parameters, curve_id",
    "run.timing": "supervisor clock around the driver process",
    "run.result.raw_result": "supervisor constant (raw-result.json exists)",
    "run.result.metrics": "copy of the driver's run.metrics",
    "run.result.certificate": "derived: attack_claimed false in the driver's own files",
    "run.result.executor_receipt": _LATER,
    "run.artifacts": "supervisor constant; stdout.log and stderr.log exist, "
                     "check.stdout.log and check.stderr.log are written after completion",
}
REPRESENTATION_NOTE = ("published manifest.yaml is a yaml.safe_dump re-serialisation of the "
                       "driver's values plus the added keys: comments and source formatting "
                       "are not kept; the driver's exact bytes are in the execution receipt's "
                       "manifest_completion.driver_manifest_text, hashed in "
                       "driver_manifest_sha256")


def complete_manifest(directory: Path, plan: dict[str, Any], plan_relative: str,
                      plan_hash: str, trial: dict[str, Any], authority: dict[str, Any],
                      argv: list[str], checker: list[str], started: str,
                      driver_finished: str) -> dict[str, Any]:
    """Give a driver's manifest.yaml the run envelope tools/validate_ledger.py
    requires, from facts the supervisor holds at publish time, then gate it.

    Frozen drivers write partial envelopes: RUN-SEMBIN-9ecb77, -a818df,
    RUN-ECDLP-3d61b8 and -06bb83 were published with only run_id, experiment_id,
    attack_claimed and metrics (11 validate_ledger errors each, DEC-20261017-0fab25),
    and older ones were flat. The driver's own values are never changed: a key
    the driver wrote is kept as written, and one that contradicts a publish-time
    fact (plan, trial, launch authority, environment.json, launched argv, the
    supervisor's clock, run.metrics, raw-result.json's attack_claimed) is a
    refusal, compared type-strictly (_check_driver_facts). Only missing keys are
    added, and envelope_completion.sources names each one's source (ADDED_FIELD_SOURCES):
    a publish-time fact, a value derived from one (status from exit code 0,
    certificate.kind none from the driver's attack_claimed false), or a
    supervisor constant. Nothing else is inferred, so a manifest that still fails
    check_run after completion is refused (EnvelopeRefused), never published.
    The published file is a YAML re-serialisation; the driver's exact bytes are
    kept in the receipt's completion record (SHF-20261028-0f3f64, LGN-4/LGN-5).
    """
    path = safe_path(directory, "manifest.yaml")
    original = path.read_bytes()
    import validate_ledger  # noqa: PLC0415 -- heavy; only after a trial succeeds
    try:
        document = fast_yaml.safe_load(original.decode("utf-8"))
        # A repeated key is the driver contradicting itself; the loader would
        # silently keep the last value (SHF-20261028-0f3f64, LGN-5).
        validate_ledger.load_yaml_unique_keys(original.decode("utf-8"), "driver manifest.yaml")
    except (UnicodeDecodeError, yaml.YAMLError) as error:
        raise EnvelopeRefused(f"driver manifest.yaml is not YAML: {error}") from error
    except ValueError as error:
        raise EnvelopeRefused(str(error)) from error
    if not isinstance(document, dict):
        raise EnvelopeRefused("driver manifest.yaml is not a mapping")
    if "run" in document:
        if set(document) != {"run"} or not isinstance(document["run"], dict):
            raise EnvelopeRefused("driver manifest.yaml mixes a run: envelope with top-level keys")
        body, shape = dict(document["run"]), "nested"
    else:
        body, shape = dict(document), "flat"  # legacy flat shape: wrap, never rename
    for block in ("code", "result", "inputs", "environment", "timing"):
        if block in body and not isinstance(body[block], dict):
            raise EnvelopeRefused(f"driver manifest run.{block} is not a mapping")
    certificate = body.get("result", {}).get("certificate")
    if certificate is not None and not isinstance(certificate, dict):
        raise EnvelopeRefused("driver manifest run.result.certificate is not a mapping")
    raw_path = safe_path(directory, "raw-result.json")
    raw = None
    if raw_path.is_file():
        try:
            raw = json.loads(raw_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raw = None
    environment = read_json(safe_path(directory, "environment.json"))
    command_file = safe_path(directory, "command.txt")
    if command_file.is_file():
        recorded = command_file.read_text(encoding="utf-8").strip()
        if recorded != json.dumps(argv):
            raise EnvelopeRefused(f"command.txt {recorded!r} disagrees with the launched argv "
                                  f"{json.dumps(argv)}")
    # Schema validity does not bind an envelope to the frozen trial. Check
    # every publish-time fact even when no completion would otherwise be needed.
    _check_driver_facts(body, plan, plan_relative, plan_hash, trial, authority, environment,
                        argv, checker, started, driver_finished, raw)
    claims = {where: value["attack_claimed"] for where, value in
              (("manifest.yaml", body), ("raw-result.json", raw))
              if isinstance(value, dict) and "attack_claimed" in value}
    if any(type(value) is not bool for value in claims.values()):
        raise EnvelopeRefused("driver attack_claimed must be a boolean")
    if any(claims.values()) and (not certificate or certificate.get("kind") == "none"):
        raise EnvelopeRefused(f"driver attack_claimed is {claims}; a claim needs the "
                              "driver's own verified certificate, which the supervisor "
                              "cannot supply")
    if not manifest_schema_errors(path):
        return {"schema": COMPLETION_SCHEMA, "action": "unchanged",
                "driver_manifest_sha256": hashlib.sha256(original).hexdigest()}
    added: list[str] = []

    def put(target: dict[str, Any], key: str, value: Any, name: str) -> None:
        if key not in target:
            target[key] = value
            added.append(name)

    started_at = datetime.fromisoformat(started)
    finished_at = datetime.fromisoformat(driver_finished)
    wall_seconds = (finished_at - started_at).total_seconds()
    if wall_seconds < 0:
        raise EnvelopeRefused("supervisor clock moved backwards; duration cannot be completed")
    put(body, "id", trial["run_id"], "run.id")
    put(body, "experiment_id", plan["experiment_id"], "run.experiment_id")
    if isinstance(plan.get("hypothesis_id"), str) and plan["hypothesis_id"].strip():
        put(body, "hypothesis_id", plan["hypothesis_id"], "run.hypothesis_id")
    put(body, "task_id", plan["task_id"], "run.task_id")
    put(body, "trial_id", trial["id"], "run.trial_id")
    put(body, "approved_by", plan["approved_by"], "run.approved_by")
    put(body, "status", "completed", "run.status")
    if "run.status" in added:
        put(body, "status_note", "Written by tools/experiment_execution.py: the driver exited 0. "
            "Completed is not a validity ruling.", "run.status_note")
    for block in ("code", "result"):
        if not isinstance(body.setdefault(block, {}), dict):
            raise EnvelopeRefused(f"driver manifest run.{block} is not a mapping")
    code, result = body["code"], body["result"]
    put(code, "commit", authority["commit"], "run.code.commit")
    put(code, "commit_meaning", "launch authority commit (launch.json, environment.json)",
        "run.code.commit_meaning")
    put(code, "command_file", "command.txt", "run.code.command_file")
    put(code, "command", json.dumps(argv), "run.code.command")
    put(code, "check_command", json.dumps(checker), "run.code.check_command")
    put(body, "environment", {"file": "environment.json", **environment}, "run.environment")
    inputs: dict[str, Any] = {"trial_plan": plan_relative, "plan_sha256": plan_hash,
                              "trial_id": trial["id"]}
    for key in ("parameters", "seed", "curve_id"):
        if key in trial:  # only what the frozen plan declares; never a default
            inputs[key] = trial[key]
    put(body, "inputs", inputs, "run.inputs")
    put(body, "timing", {"started_at": started, "finished_at": driver_finished,
                         "wall_seconds": wall_seconds,
                         "source": "supervisor clock around the driver process"}, "run.timing")
    if raw_path.is_file():
        put(result, "raw_result", "raw-result.json", "run.result.raw_result")
    if isinstance(body.get("metrics"), dict):
        put(result, "metrics", copy.deepcopy(body["metrics"]), "run.result.metrics")
    if "certificate" not in result and claims:
        if set(map(repr, claims.values())) != {"False"}:
            raise EnvelopeRefused(f"driver attack_claimed is {claims}; a claim needs the "
                                  "driver's own verified certificate, which the supervisor "
                                  "cannot supply")
        put(result, "certificate", {
            "kind": "none", "verified": None,
            "note": "attack_claimed false in " + " and ".join(sorted(claims))
                    + "; no discrete_log, decomposition or key_recovery claim"},
            "run.result.certificate")
    put(result, "executor_receipt", "execution-receipt.json", "run.result.executor_receipt")
    put(body, "artifacts", {"stdout": "stdout.log", "stderr": "stderr.log",
                            "check_stdout": "check.stdout.log",
                            "check_stderr": "check.stderr.log"}, "run.artifacts")
    record = {"schema": COMPLETION_SCHEMA, "action": "completed", "driver_shape": shape,
              "driver_manifest_sha256": hashlib.sha256(original).hexdigest(),
              "completed_by": "tools/experiment_execution.py", "added": added,
              "sources": {name: ADDED_FIELD_SOURCES[name] for name in added},
              "representation": REPRESENTATION_NOTE}
    body["envelope_completion"] = record
    completed = yaml.safe_dump({"run": body}, sort_keys=False, allow_unicode=True)
    # Gate the candidate before replacing the driver's bytes, beside the run's
    # capture artifacts: a refusal leaves the driver's manifest as written.
    candidate = safe_path(directory, ".manifest.candidate.yaml")
    try:
        candidate.write_text(completed, encoding="utf-8")
        errors = manifest_schema_errors(candidate)
        if not errors:
            os.replace(candidate, path)
    finally:
        candidate.unlink(missing_ok=True)
    if errors:
        raise EnvelopeRefused("manifest.yaml fails the run schema (tools/validate_ledger.py) "
                              "and cannot be completed from publish-time facts: "
                              + "; ".join(errors))
    return {**record, "driver_manifest_text": original.decode("utf-8")}


def run_root(root: Path, plan: dict[str, Any], trial: dict[str, Any]) -> Path:
    parent = PurePosixPath(plan["specification"]).parent
    return safe_path(root, f"{parent}/runs/{trial['run_id']}")


def trial_state(root: Path, plan: dict[str, Any], trial: dict[str, Any], plan_hash: str) -> str:
    directory = run_root(root, plan, trial)
    if not directory.exists():
        # A sparse checkout can leave a committed run off disk: unknown, never planned.
        relative = directory.relative_to(root.resolve()).as_posix() + "/"
        return "not_materialized" if sparse_checkout.tracked_absent(root, relative) else "planned"
    # Mere existence is NOT completion and is NOT permission to launch again.
    try:
        receipt = read_json(safe_path(directory, "execution-receipt.json"))
        if (receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("plan_sha256") != plan_hash
                or receipt.get("trial_id") != trial["id"] or receipt.get("run_id") != trial["run_id"]):
            return "needs_reconciliation"
        if (receipt.get("status") != "output_validated" or receipt.get("returncode") != 0
                or receipt.get("check_returncode") != 0):
            return "needs_reconciliation"
        expected = set(trial["artifacts"]) | (set(GENERATED) - {"execution-receipt.json"})
        hashes = receipt.get("artifact_sha256")
        if not isinstance(hashes, dict) or set(hashes) != expected:
            return "needs_reconciliation"
        # artifact_sha256 binds content; a large artifact may be stored compressed or
        # as a blob-store pointer (tools/artifact_store.py), checked by its own digest.
        storage = receipt.get("artifact_storage") or {}
        if not isinstance(storage, dict) or not set(storage) <= set(hashes):
            return "needs_reconciliation"
        for name, digest in hashes.items():
            if name in storage:
                if not artifact_store.stored_matches(directory, name, storage[name], digest):
                    return "needs_reconciliation"
            elif sha256(safe_path(directory, name)) != digest:
                return "needs_reconciliation"
        return "output_validated"
    except (OSError, ValueError, TypeError):
        return "needs_reconciliation"


def coverage(root: Path, path: Path, *, allow_preapproval_candidate: bool = False) -> dict[str, Any]:
    plan = load_plan(root, path, allow_preapproval_candidate=allow_preapproval_candidate)
    digest = sha256(path)
    states = {t["id"]: trial_state(root, plan, t, digest) for t in plan["trials"]}
    for trial in plan["trials"]:
        if states[trial["id"]] == "planned" and any(
                states[dep] != "output_validated" for dep in trial.get("depends_on", [])):
            states[trial["id"]] = "waiting_on_dependencies"
    counts = Counter(states.values())
    return {"experiment_id": plan["experiment_id"], "plan_sha256": digest,
            "required": len(states), "output_validated": counts["output_validated"],
            "remaining": len(states) - counts["output_validated"],
            "planned": counts["planned"], "waiting_on_dependencies": counts["waiting_on_dependencies"],
            "needs_reconciliation": counts["needs_reconciliation"],
            "not_materialized": counts["not_materialized"],
            "measurement_complete": counts["output_validated"] == len(states),
            "publication_verified": False, "scientific_review_verified": False,
            "trials": states}


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ExecutionError(f"git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def committed(root: Path, path: Path) -> None:
    relative = path.relative_to(root.resolve()).as_posix()
    result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{relative}"],
                            capture_output=True, check=False)
    if result.returncode or result.stdout != path.read_bytes():
        raise ExecutionError(f"uncommitted or changed input: {relative}")


def authorize(root: Path, path: Path, plan: dict[str, Any], owner: str, epoch: int) -> dict[str, Any]:
    """Re-render the existing dispatcher, including its archive and claims gates."""
    for relative in (plan["specification"], plan["queue"], *plan["source_sha256"]):
        file = safe_path(root, relative)
        committed(root, file)
        if relative in plan["source_sha256"] and sha256(file) != plan["source_sha256"][relative]:
            raise ExecutionError(f"source hash changed: {relative}")
    committed(root, path)
    committed(root, root / "tools/research_dispatch.py")
    # Recheck authorization fields immediately before launching, not just on selection.
    load_plan(root, path)
    with tempfile.TemporaryDirectory(prefix="execution-dispatch-") as temporary:
        output, report = Path(temporary) / "plan.json", Path(temporary) / "plan.md"
        result = subprocess.run(
            [sys.executable, str(root / "tools/research_dispatch.py"), str(root / plan["queue"]),
             "--repo-root", str(root), "--claims", "refs", "--now", datetime.now(timezone.utc).isoformat(),
             "--output", str(output), "--report", str(report)],
            cwd=root, capture_output=True, text=True, check=False)
        if result.returncode:
            raise ExecutionError(f"dispatcher refused execution: {result.stderr.strip()}")
        dispatch = read_json(output)
    gates = dispatch.get("gates")
    if (dispatch.get("schema") != "crypto.autoresearch.dispatch_plan.v1"
            or not isinstance(gates, dict) or not gates or any(v is not True for v in gates.values())):
        raise ExecutionError("dispatcher gates failed")
    task = next((t for t in dispatch.get("dispatches", []) if t.get("id") == plan["task_id"]), None)
    if not task or task.get("role") != "executor" or task.get("state") != "running":
        raise ExecutionError("execution mode requires an admitted, claimed executor task")
    claim = task.get("claim") or {}
    if claim.get("status") != "live" or claim.get("owner") != owner or claim.get("epoch") != epoch:
        raise ExecutionError("missing live claim or wrong owner/epoch; claim through goal_lanes.py")
    expires = datetime.fromisoformat(claim["expires_at"].replace("Z", "+00:00"))
    if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
        raise ExecutionError("claim is expired or has no timezone")
    claim_file = safe_path(root, str(PurePosixPath(plan["queue"]).parent /
                                   "claims" / f"{plan['task_id']}.{epoch}.claim.json"))
    committed(root, claim_file)
    claim_relative = claim_file.relative_to(root).as_posix()
    claim_commit = git(root, "log", "-1", "--format=%H", "--", claim_relative)
    if not claim_commit or not git(root, "for-each-ref", f"--contains={claim_commit}",
                                   "--format=%(refname)", "refs/remotes/origin/"):
        raise ExecutionError("claim is not visible in origin tracking refs; publish/fetch before launch")
    handoff = task.get("handoff") or {}
    binding = handoff.get("execution") or {}
    required_binding = {"mode": "experiments", "kind": "run", "experiment_id": plan["experiment_id"],
                        "trial_plan": path.relative_to(root).as_posix(), "trial_plan_sha256": sha256(path),
                        "approved_by": plan["approved_by"]}
    if binding != required_binding:
        raise ExecutionError("handoff must bind this exact execution-only plan and approval")
    budget = handoff.get("budget") or {}
    if any(budget.get(key) == 0 for key in ("maximum_runs", "experiment_maximum_runs")):
        raise ExecutionError("zero-run task cannot execute trials")
    paths = set(task.get("artifact_paths") or [])
    for trial in plan["trials"]:
        directory = run_root(root, plan, trial)
        for name in (*GENERATED, *trial["artifacts"]):
            relative = (directory / name).relative_to(root).as_posix()
            if relative not in paths:
                raise ExecutionError(f"handoff archive coverage missing: {relative}")
        # The trial guard is RLIMIT_AS on Linux or sampled group RSS on macOS.
        if budget.get("memory_gb") is not None and trial["memory_mb"] > float(budget["memory_gb"]) * 1024:
            raise ExecutionError("trial memory exceeds handoff protection")
    return {"owner": owner, "epoch": epoch, "expires_at": expires.isoformat(),
            "dispatch_plan_sha256": dispatch.get("plan_sha256"), "commit": git(root, "rev-parse", "HEAD")}


def materialized(root: Path, plan: dict[str, Any]) -> None:
    """Refuse a launch a sparse checkout would make unsafe or unpublishable.

    A committed run left off disk reads as not_materialized, so coverage cannot
    say whether it is done; and `git add` refuses a new run directory outside
    the sparse rules, so its records could never be published. A full checkout
    passes trivially.
    """
    runs = [run_root(root, plan, t).relative_to(root.resolve()).as_posix() for t in plan["trials"]]
    absent = [r for r in runs if sparse_checkout.tracked_absent(root, r + "/")]
    outside = sparse_checkout.outside_definition(root, [f"{r}/execution-receipt.json" for r in runs])
    if absent or outside:
        raise ExecutionError(
            f"sparse checkout leaves run directories of {plan['experiment_id']} off disk; "
            f"run `{sparse_checkout.materialize_hint(plan['experiment_id'])}` and retry")


@contextmanager
def task_lock(root: Path, task_id: str):
    """Same-host, cross-worktree exclusion; claims remain the cross-host authority."""
    import fcntl
    common = Path(git(root, "rev-parse", "--git-common-dir"))
    if not common.is_absolute():
        common = root / common
    directory = common / "experiment-execution-locks"
    directory.mkdir(exist_ok=True)
    name = hashlib.sha256(task_id.encode()).hexdigest() + ".lock"
    with (directory / name).open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ExecutionError(f"task already has a local supervisor: {task_id}") from error
        yield stream.fileno()


def terminate_group(process: subprocess.Popen) -> None:
    # Kill the group even if the leader exited; detached descendants are forbidden.
    if (sys.platform == "darwin" and process.poll() is not None
            and _darwin_group_member_count(process.pid) == 0):
        process.wait()
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError as error:
        # Darwin can report EPERM while a just-exited leader is being reaped.
        # Only ignore it when the group has actually disappeared; a live group
        # we cannot kill remains an infrastructure error.
        if sys.platform != "darwin":
            raise error
        try:
            process.wait(timeout=0.1)
        except subprocess.TimeoutExpired:
            raise error
        if _darwin_group_member_count(process.pid) != 0:
            raise error
    process.wait()


@lru_cache(maxsize=1)
def _darwin_proc_api() -> tuple[Any, Any]:
    """Read process-group members and resident sizes through macOS libproc."""
    import ctypes
    lib = ctypes.CDLL("/usr/lib/libproc.dylib")
    group = lib.proc_listpgrppids
    group.argtypes = (ctypes.c_int, ctypes.c_void_p, ctypes.c_int)
    group.restype = ctypes.c_int
    info = lib.proc_pidinfo
    info.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                     ctypes.c_void_p, ctypes.c_int)
    info.restype = ctypes.c_int
    return group, info


def _darwin_group_member_count(pgid: int) -> int:
    import ctypes
    group, _ = _darwin_proc_api()
    pids = ctypes.create_string_buffer(4096 * ctypes.sizeof(ctypes.c_int))
    count = group(pgid, pids, len(pids))
    if count < 0 or count >= 4096:
        raise ExecutionError(f"cannot enumerate process group {pgid}")
    return count


def darwin_group_rss_bytes(pgid: int) -> int:
    """Sum resident bytes across a launched group; fail if it cannot be read."""
    import ctypes
    import struct
    group, info = _darwin_proc_api()
    # proc_listpgrppids returns a PID count, unlike proc_listpids (bytes).
    pids = ctypes.create_string_buffer(4096 * ctypes.sizeof(ctypes.c_int))
    count = group(pgid, pids, len(pids))
    if count <= 0 or count >= 4096:
        raise ExecutionError(f"cannot enumerate process group {pgid} for memory guard")
    total = 0
    measured = 0
    for (pid,) in struct.iter_unpack("i", pids.raw[:count * ctypes.sizeof(ctypes.c_int)]):
        task = ctypes.create_string_buffer(96)  # proc_taskinfo, first two uint64s
        if info(pid, 4, 0, task, len(task)) < 16:  # PROC_PIDTASKINFO
            remaining = ctypes.create_string_buffer(len(pids))
            current_count = group(pgid, remaining, len(remaining))
            if 0 <= current_count < 4096 and pid not in (
                member[0] for member in struct.iter_unpack(
                    "i", remaining.raw[:current_count * ctypes.sizeof(ctypes.c_int)])):
                continue  # exited between enumeration and measurement
            raise ExecutionError(f"cannot read resident memory for process {pid}")
        total += struct.unpack_from("Q", task.raw, 8)[0]
        measured += 1
    if not measured:
        raise ExecutionError(f"cannot read resident memory for process group {pgid}")
    return total


def read_darwin_rss_during_transition(process: subprocess.Popen[Any],
                                      grace_seconds: float = 1.0) -> int | None:
    """Retry a short libproc exit/exec race, but fail on persistent monitor loss.

    A group member may still be listed after its task info becomes unreadable.
    ``None`` means the supervised leader exited during this transition.
    """
    deadline = time.monotonic() + grace_seconds
    first_error = None
    while True:
        try:
            return darwin_group_rss_bytes(process.pid)
        except ExecutionError as error:
            if first_error is None:
                first_error = error
            if process.poll() is not None:
                return None
            if time.monotonic() >= deadline:
                raise first_error
            time.sleep(0.02)


def run_process(argv: list[str], root: Path, directory: Path, prefix: str, trial: dict[str, Any],
                authority: dict[str, Any], lock_fd: int) -> tuple[str, int | None]:
    import resource
    ceiling = int(trial["memory_mb"] * 1024 * 1024)
    def limits() -> None:
        resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))
    # macOS rejects RLIMIT_AS with EINVAL even for an ordinary finite limit.
    # Monitor the new process group instead, retaining a bounded memory guard.
    darwin = sys.platform == "darwin"
    started = time.monotonic()
    expiry = datetime.fromisoformat(authority["expires_at"])
    watchdog = trial.get("watchdog_seconds")
    process = None
    with (directory / f"{prefix}stdout.log").open("xb") as stdout, (directory / f"{prefix}stderr.log").open("xb") as stderr:
        try:
            process = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL, stdout=stdout,
                                       stderr=stderr, start_new_session=True,
                                       preexec_fn=None if darwin else limits,
                                       pass_fds=(lock_fd,))
            while process.poll() is None:
                if darwin:
                    rss = read_darwin_rss_during_transition(process)
                    if rss is None:
                        return "exited", process.returncode
                    if rss > ceiling:
                        return "memory_limit_exceeded", None
                if datetime.now(timezone.utc) >= expiry:
                    return "claim_expired", None
                if watchdog is not None and time.monotonic() - started >= watchdog:
                    return "watchdog_expired", None
                time.sleep(0.05)
            return "exited", process.returncode
        finally:
            if process is not None:
                terminate_group(process)


def execute_trial(root: Path, path: Path, plan: dict[str, Any], trial: dict[str, Any],
                  authority: dict[str, Any], lock_fd: int) -> str:
    directory = run_root(root, plan, trial)
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir()  # exclusive; even an empty interrupted attempt is never reused
    digest = sha256(path)
    argv = [arg.replace("{run_dir}", str(directory)) for arg in trial["argv"]]
    checker = [arg.replace("{run_dir}", str(directory)) for arg in trial["check_argv"]]
    started = datetime.now(timezone.utc).isoformat()
    write_once(directory / "launch.json", {"plan_sha256": digest, "trial_id": trial["id"],
               "run_id": trial["run_id"], "started_at": started, "authority": authority,
               "argv": argv, "check_argv": checker, "supervisor_pid": os.getpid()})
    with (directory / "command.txt").open("x") as stream:
        stream.write(json.dumps(argv) + "\n")
    write_once(directory / "environment.json", {"python": sys.version, "platform": sys.platform,
               "source_sha256": plan["source_sha256"], "specification_sha256": plan["specification_sha256"],
               "commit": authority["commit"], "runtime_lock": plan.get("runtime_lock"),
               "runtime_lock_sha256": plan.get("runtime_lock_sha256")})  # never dump credential-bearing environment variables
    status, returncode, check_returncode = "infrastructure_error", None, None
    detail = None
    completion = None
    interrupted = False
    try:
        state, returncode = run_process(argv, root, directory, "", trial, authority, lock_fd)
        driver_finished = datetime.now(timezone.utc).isoformat()
        if state != "exited":
            status = state
        elif returncode != 0:
            status = "infrastructure_error"
        else:
            # Before the checker, so it validates the bytes that get published.
            manifest = safe_path(directory, "manifest.yaml")
            if manifest.is_file():  # an empty one is refused, never skipped
                completion = complete_manifest(
                    directory, plan, path.relative_to(root).as_posix(), digest, trial,
                    authority, argv, checker, started, driver_finished)
            state, check_returncode = run_process(checker, root, directory, "check.", trial, authority, lock_fd)
            status = (state if state != "exited" else
                      "output_validated" if check_returncode == 0 else "invalid_output")
        if status == "output_validated":
            allow_empty = set(trial.get("allow_empty_artifacts", []))
            for name in trial["artifacts"]:
                file = safe_path(directory, name)
                if not file.is_file() or (file.stat().st_size == 0 and name not in allow_empty):
                    raise ExecutionError(f"missing/empty required artifact: {name}")
            schema = manifest_schema_errors(safe_path(directory, "manifest.yaml"))
            if schema:
                raise ExecutionError("manifest.yaml fails the run schema (tools/validate_ledger.py): "
                                     + "; ".join(schema))
    except KeyboardInterrupt:
        status, interrupted = "interrupted", True
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        status, detail = "invalid_output" if returncode == 0 else "infrastructure_error", str(error)
        if isinstance(error, EnvelopeRefused) or "fails the run schema" in detail:
            # Loud, not only in the receipt: this run must not be published.
            print(f"experiment_execution: {trial['run_id']}: refused: {detail}", file=sys.stderr)
    # Failed launches/checks still get all declared log paths, never invented output.
    for name in ("stdout.log", "stderr.log", "check.stdout.log", "check.stderr.log"):
        target = safe_path(directory, name)
        if not target.exists():
            target.touch(exist_ok=False)
    names = (*trial["artifacts"], *(n for n in GENERATED if n != "execution-receipt.json"))
    # After the checker has read every output as written: store large ones compressed,
    # and offload the largest when CRYPTO_AR_BLOBSTORE names a store
    # (docs/artifact-storage.md). Receipts still bind each artifact's content digest.
    storage: dict[str, dict[str, Any]] = {}
    store = None
    try:
        store = artifact_store.store_from_env()
    except artifact_store.StoreError as error:
        detail = "; ".join(filter(None, (detail, f"artifact storage: {error}")))
    for name in names:
        try:
            safe_path(directory, name)
            storage.update(artifact_store.compact(directory, [name], store))
        except (OSError, ValueError) as error:
            detail = "; ".join(filter(None, (detail, f"artifact storage: {name}: {error}")))
    artifacts = {}
    for name in names:
        try:
            if name in storage:
                artifacts[name] = storage[name]["content_sha256"]
                continue
            file = safe_path(directory, name)
            if file.is_file():
                artifacts[name] = sha256(file)
        except (OSError, ValueError):
            status = "invalid_output"
    write_once(directory / "execution-receipt.json", {
        "schema": RECEIPT_SCHEMA, "plan_sha256": digest, "trial_id": trial["id"],
        "run_id": trial["run_id"], "status": status, "returncode": returncode,
        "check_returncode": check_returncode, "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(), "detail": detail,
        "artifact_sha256": artifacts, "artifact_storage": storage, "authority": authority,
        "manifest_completion": completion,
        "scientific_conclusion": None, "published": False})
    if interrupted:
        raise KeyboardInterrupt
    return status


def run_plan(root: Path, path: Path, owner: str, epoch: int, *,
             gate: Callable[..., dict[str, Any]] = authorize) -> dict[str, Any]:
    root, path = root.resolve(), path.absolute()
    if os.name != "posix":
        raise ExecutionError("process-group and address-space guards require POSIX")
    plan = load_plan(root, path)
    materialized(root, plan)
    with task_lock(root, plan["task_id"]) as fd:
        digest = sha256(path)
        for trial in plan["trials"]:
            if coverage(root, path)["trials"][trial["id"]] != "planned":
                continue
            authority = gate(root, path, plan, owner, epoch)
            if sha256(path) != digest:
                raise ExecutionError("trial plan changed during execution")
            status = execute_trial(root, path, plan, trial, authority, fd)
            if plan.get("stop_on_invalid_output") is True and status == "invalid_output":
                break
    return coverage(root, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("status", "run"))
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--owner")
    parser.add_argument("--epoch", type=int)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    path = args.plan if args.plan.is_absolute() else root / args.plan
    def interrupt(*_: Any) -> None:
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        if args.command == "status":
            report = coverage(root, path)
        else:
            if not args.owner or not args.epoch or args.epoch < 1:
                raise ExecutionError("run requires the published claim's --owner and positive --epoch")
            report = run_plan(root, path, args.owner, args.epoch)
        print(json.dumps(report, indent=2))
        return 0 if report["measurement_complete"] or args.command == "status" else 3
    except KeyboardInterrupt:
        print("execution interrupted; preserve attempts and reconcile ownership", file=sys.stderr)
        return 130
    except (OSError, ValueError, TypeError) as error:
        print(f"execution impediment: {error}", file=sys.stderr)
        return 2
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
