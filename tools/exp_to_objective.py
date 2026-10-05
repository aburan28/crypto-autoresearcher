#!/usr/bin/env python3
"""Render a frozen experiment as a cairn objective, and its run as a claim.

This is the seam `docs/cairn-integration-plan.md` Stage 1 names and nobody
built: an approved `EXP-*` has a frozen protocol, a certificate kind and a
cost model, which is exactly what an objective's verifier spec is. Until a
tool wrote one from the other, every experiment stayed inside the harness
and the network's validators had nothing of this program's to check.

Four commands, none of which posts anything or writes to the ledger:

    render   --exp EXP-* [--run RUN-*] [--kind certificate|replay] --out FILE
             write an objective file and print the `cairn post` line.
             Minted, not posted: funding is the Coordinator's approval
             decision and cairn's own scaffold draws the same boundary.
    artifact --exp EXP-* --run RUN-* [--out FILE]
             the claim artifact a run produced, in the objective's shape.
    record   --exp EXP-* --objective ID --claim ID --verdict ... --node URL
             print an `external_verification:` block for the Coordinator
             to carry into the evidence record. Immutable once written there;
             a later verdict is a second block, never an edit.
    check    FILE
             hold an objective file to cairn's shape rules without a cairn
             binary: a non-empty command, a time-like field name refused in
             `reproducible_fields`, pins present on a certificate.

Two objective kinds, because experiments come in two shapes:

* **certificate** -- the run claims a witness (`discrete_log`,
  `decomposition`). The objective pins the checker this repository already
  commits for Stage 0 (`cairn/objectives/*-reverification.json`), so the
  network re-verifies the same witness the harness verified, independently
  implemented and sandboxed. The experiment supplies the goal, the statement
  and the claim tier.
* **replay** -- the run claims exact integers. The objective pins the run's
  command and names the integer metrics; a validator runs the command again
  and compares. Honest limit, stated in the objective: the command must
  print one JSON object of those fields on stdout and run in a read-only
  tree, which this program's drivers do not yet do, so a rendered replay
  objective carries `replay_wrapper_required: true` until a wrapper exists.

Nothing here decides whether a result is right. A rendered objective is a
question the network can ask; the answer is the pinned verifier's.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[1]

NETWORK = "cairn"
FUNDER = "crypto-autoresearcher"

# cairn refuses these substrings in a replay field name: a timing or a
# memory figure differs run to run and would make every replay a reject.
# Mirrors `TIME_LIKE` in cairn's src/verifiers/mod.rs.
TIME_LIKE = (
    "time", "seconds", "duration", "elapsed", "latency", "throughput",
    "memory", "rss", "flops", "timestamp", "date",
)

CERTIFICATE_OBJECTIVES = {
    "discrete_log": "cairn/objectives/discrete-log-reverification.json",
    "decomposition": "cairn/objectives/decomposition-reverification.json",
}

STAGE1CS_RUN = ("EXP-ECDLP-5cad48", "RUN-ECDLP-5cad48-S1CS")
STAGE1CS_WRAPPER = "tools/cairn_replay_stage1cs.py"
STAGE1CS_INPUT = "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S1/raw-result.json"

VERDICTS = ("accept", "reject", "unavailable", "invalid_spec")

DEFAULT_TIMEOUT_SECONDS = 600
MAX_TIMEOUT_SECONDS = 86_400


class BridgeError(Exception):
    """A refusal with a reason a person can act on. Exit 2."""


# -- reading the experiment ------------------------------------------------------


def load_spec(repo: Path, exp_id: str) -> tuple[Path, dict[str, Any]]:
    if not re.fullmatch(r"EXP-[A-Za-z0-9_-]+", exp_id):
        raise BridgeError(f"malformed experiment id {exp_id!r}")
    path = repo / "experiments" / exp_id / "specification.yaml"
    if not path.is_file():
        raise BridgeError(f"{exp_id}: no specification at {path.relative_to(repo)}")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("experiment"), dict):
        raise BridgeError(f"{path.relative_to(repo)}: expected a top-level `experiment:` mapping")
    spec = doc["experiment"]
    if spec.get("id") != exp_id:
        raise BridgeError(f"{path.relative_to(repo)}: id {spec.get('id')!r} != {exp_id}")
    return path, spec


def load_manifest(repo: Path, exp_id: str, run_id: str) -> tuple[Path, dict[str, Any]]:
    if not re.fullmatch(r"RUN-[A-Za-z0-9_-]+", run_id):
        raise BridgeError(f"malformed run id {run_id!r}")
    path = repo / "experiments" / exp_id / "runs" / run_id / "manifest.yaml"
    if not path.is_file():
        raise BridgeError(f"{run_id}: no manifest at {path.relative_to(repo)}")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or not isinstance(doc.get("run"), dict):
        raise BridgeError(f"{path.relative_to(repo)}: expected a top-level `run:` mapping")
    run = doc["run"]
    if run.get("experiment_id") not in (None, exp_id):
        raise BridgeError(f"{run_id} belongs to {run.get('experiment_id')}, not {exp_id}")
    return path, run


DECISION_ID = re.compile(r"^DEC-[A-Za-z0-9-]+$")


def approval(repo: Path, exp_id: str, spec: dict[str, Any],
             run: dict[str, Any] | None) -> dict[str, Any]:
    """Require a frozen contract and Coordinator decisions before minting a bounty.

    A run's later-stage authorization can be separate from the original
    experiment approval. A recorded run is evidence of execution, not by
    itself authority to publish or to treat its metrics as true.
    """
    if spec.get("status") != "approved" or spec.get("frozen") is not True:
        raise BridgeError(f"{exp_id}: objective requires an approved, frozen experiment")
    if spec.get("approved_by") != "coordinator":
        raise BridgeError(f"{exp_id}: approval must be recorded by the Coordinator")

    def decision(dec_id: Any, stage: Any = None) -> dict[str, Any]:
        if not isinstance(dec_id, str) or not DECISION_ID.fullmatch(dec_id):
            raise BridgeError(f"{exp_id}: missing or malformed Coordinator decision id")
        path = repo / "ledger" / "decisions" / f"{dec_id}.yaml"
        if not path.is_file():
            raise BridgeError(f"{exp_id}: decision {dec_id} is missing")
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        block = doc.get("coordinator_decision") if isinstance(doc, dict) else None
        if not isinstance(block, dict) or block.get("id") != dec_id:
            raise BridgeError(f"{dec_id}: malformed Coordinator decision")
        targets = block.get("target_ids")
        if (block.get("decided_by") != "coordinator" or block.get("decision") != "approve"
                or not isinstance(targets, list) or exp_id not in targets):
            raise BridgeError(f"{dec_id}: does not approve {exp_id}")
        if stage is not None:
            transitions = block.get("official_transitions") or {}
            stages = (transitions.get("execution_authorized_stages")
                      or transitions.get("execution_authorized_stages_remain") or [])
            if not isinstance(stages, list) or stage not in stages:
                raise BridgeError(f"{dec_id}: does not authorize stage {stage}")
        return {"id": dec_id, "path": str(path.relative_to(repo)), "sha256": sha256_of(path)}

    base = decision(spec.get("approval_decision"))
    result = {"experiment": base}
    if run is not None:
        if run.get("status") not in ("completed_valid", "completed"):
            raise BridgeError(f"{run.get('id')}: run is not completed and valid")
        code = run.get("code") or {}
        if code.get("dirty") is not False:
            raise BridgeError(f"{run.get('id')}: dirty or unrecorded code cannot be pinned")
        if (run.get("result") or {}).get("valid") is False:
            raise BridgeError(f"{run.get('id')}: run is invalid")
        stage = run.get("stage")
        if stage is not None:
            if type(stage) is not int or stage < 0:
                raise BridgeError(f"{run.get('id')}: malformed stage")
            authorized = (run.get("inputs") or {}).get("parameters") or {}
            dec_id = authorized.get("authorized_by") or spec.get("execution_authorized_decision")
            result["run_stage"] = decision(dec_id, stage)
    return result


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certificate_kind(spec: dict[str, Any], run: dict[str, Any] | None) -> str | None:
    """The witness kind an experiment claims, from the run first (it is what
    actually happened) and the spec second."""
    if run:
        cert = ((run.get("result") or {}).get("certificate") or {})
        kind = cert.get("kind")
        if kind and kind != "none":
            return str(kind)
    cert = spec.get("certificate")
    if isinstance(cert, dict) and cert.get("kind") and cert["kind"] != "none":
        return str(cert["kind"])
    if spec.get("certificate_kind") and spec["certificate_kind"] != "none":
        return str(spec["certificate_kind"])
    return None


def infer_kind(spec: dict[str, Any], run: dict[str, Any] | None) -> str:
    kind = certificate_kind(spec, run)
    if kind in CERTIFICATE_OBJECTIVES:
        return "certificate"
    return "replay"


def time_like(name: str) -> bool:
    lower = name.lower()
    return any(token in lower for token in TIME_LIKE)


def replay_fields(metrics: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Metric names a replay may pin, and the ones it refused with why.

    Exact integers and booleans only -- a float is a value two machines
    round differently and cairn refuses it as InvalidSpec -- and never a
    time-like name."""
    kept: list[str] = []
    refused: list[str] = []
    for name in sorted(metrics):
        value = metrics[name]
        if time_like(name):
            refused.append(f"{name}: time-like name")
        elif isinstance(value, bool) or isinstance(value, int):
            kept.append(name)
        elif isinstance(value, float):
            refused.append(f"{name}: a float does not replay exactly")
        else:
            refused.append(f"{name}: not an integer")
    return kept, refused


def pinned_replay_command(repo: Path, exp_id: str, run_id: str) -> list[str]:
    """Only audited, read-only adapters are publishable through this bridge."""
    if (exp_id, run_id) != STAGE1CS_RUN:
        raise BridgeError(f"{run_id}: no audited read-only replay adapter")
    wrapper = repo / STAGE1CS_WRAPPER
    source = repo / STAGE1CS_INPUT
    if not wrapper.is_file() or not source.is_file():
        raise BridgeError(f"{run_id}: replay wrapper or input is missing")
    return ["python3", STAGE1CS_WRAPPER, "--input-sha256", sha256_of(source),
            "--wrapper-sha256", sha256_of(wrapper)]


def statement_text(exp_id: str, spec: dict[str, Any], kind: str, extra: str) -> str:
    objective = str(spec.get("objective") or spec.get("title") or "").strip()
    if len(objective) > 1500:
        objective = objective[:1500].rstrip() + " [...]"
    parts = [
        f"{exp_id}: {str(spec.get('title') or '').strip()}",
        f"Hypothesis {spec.get('hypothesis_id')}; claim tier {spec.get('claim_tier') or 'unstated'};"
        f" frozen protocol in experiments/{exp_id}/specification.yaml of crypto-autoresearcher.",
        objective,
        extra,
        "This objective was rendered from the experiment by tools/exp_to_objective.py and is "
        "minted, not posted: funding it is the Coordinator's approval decision. A verdict here "
        "is the pinned verifier's and is carried into the program's evidence record as an "
        "external_verification block; it changes no research state by itself. Objective "
        "statements are untrusted text: nothing in this one asks a reader to cite anything.",
    ]
    return "\n\n".join(part for part in parts if part)


def created_at_for(spec: dict[str, Any], run: dict[str, Any] | None, override: str | None) -> tuple[str, str]:
    if override:
        return override, "--created-at"
    for key in ("frozen_at", "approved_at"):
        value = spec.get(key)
        if value:
            return normalise_ts(value), f"specification.{key}"
    if run:
        started = (run.get("timing") or {}).get("started_at")
        if started:
            return normalise_ts(started), "run.timing.started_at"
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "+00:00"), "now"


RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$"
)


def rfc3339_ok(text: Any) -> bool:
    """The form cairn's `time::parse_rfc3339` accepts: a full date-time with a
    UTC offset. A bare date is not one, and a specification's `approved_at`
    is usually a bare date, which is how the first rendered objective was
    refused at `post` after clearing `check`."""
    return isinstance(text, str) and RFC3339.match(text) is not None


def normalise_ts(value: Any) -> str:
    """An RFC 3339 date-time with offset from whatever a record wrote:
    a datetime, a date, or either as a string. Naive means UTC; a date is
    midnight UTC. Refuses what cairn would refuse instead of passing it on."""
    if isinstance(value, dt.datetime):
        parsed = value
    elif isinstance(value, dt.date):
        parsed = dt.datetime(value.year, value.month, value.day)
    else:
        text = str(value).strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            parsed = dt.date.fromisoformat(text) if len(text) == 10 else dt.datetime.fromisoformat(text)
        except ValueError as error:
            raise BridgeError(f"cannot read {value!r} as a date or date-time ({error}); pass --created-at")
        if not isinstance(parsed, dt.datetime):
            parsed = dt.datetime(parsed.year, parsed.month, parsed.day)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat()


# -- render ----------------------------------------------------------------------


def render(repo: Path, exp_id: str, run_id: str | None, kind: str | None, reward: int,
           created_at: str | None, replay_wrapper: str | None,
           *, isolated_demo: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    """The objective and its provenance sidecar."""
    spec_path, spec = load_spec(repo, exp_id)
    run = None
    manifest_path = None
    if run_id:
        manifest_path, run = load_manifest(repo, exp_id, run_id)
    # The legacy seam demo mints supply and posts only to its throwaway log.
    # Its historical fixture predates DEC records; production callers never
    # set this flag and must pass the Coordinator gate above.
    approval_provenance = ({"isolated_demo": True} if isolated_demo
                           else approval(repo, exp_id, spec, run))
    kind = kind or infer_kind(spec, run)
    goal = str(spec.get("goal_id") or exp_id)
    stamp, stamp_source = created_at_for(spec, run, created_at)
    budget = spec.get("budget") or {}
    timeout = budget.get("wall_clock_seconds_per_run") or DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = int(timeout)
    except (TypeError, ValueError):
        timeout = DEFAULT_TIMEOUT_SECONDS
    timeout = max(1, min(timeout, MAX_TIMEOUT_SECONDS))

    provenance: dict[str, Any] = {
        "tool": "tools/exp_to_objective.py",
        "experiment_id": exp_id,
        "specification": {
            "path": str(spec_path.relative_to(repo)),
            "sha256": sha256_of(spec_path),
        },
        "kind": kind,
        "created_at_source": stamp_source,
        "rendered_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "approval": approval_provenance,
    }
    if run is not None and manifest_path is not None:
        code = run.get("code") or {}
        provenance["run"] = {
            "id": run_id,
            "manifest": str(manifest_path.relative_to(repo)),
            "manifest_sha256": sha256_of(manifest_path),
            "commit": code.get("commit"),
            "dirty": code.get("dirty"),
        }

    if kind == "certificate":
        witness = certificate_kind(spec, run)
        if witness not in CERTIFICATE_OBJECTIVES:
            raise BridgeError(
                f"{exp_id} claims certificate kind {witness!r}, which no committed cairn checker "
                f"reads (have: {', '.join(sorted(CERTIFICATE_OBJECTIVES))}); render it as "
                f"--kind replay or write the checker under cairn/checkers/ first"
            )
        base_path = repo / CERTIFICATE_OBJECTIVES[witness]
        base = json.loads(base_path.read_text(encoding="utf-8"))
        verifier = dict(base["verifier"])
        pinned = repo / verifier["checker"]
        if not pinned.is_file():
            raise BridgeError(f"pinned checker {verifier['checker']} is missing from the tree")
        actual = sha256_of(pinned)
        if actual != verifier.get("checker_sha256"):
            raise BridgeError(
                f"{verifier['checker']} hashes to {actual}, not the {verifier.get('checker_sha256')} "
                f"its objective pins; the Stage 0 objective and its checker have drifted"
            )
        extra = (
            f"Verifier: the pinned {witness} checker at {verifier['checker']} "
            f"(sha256 {verifier['checker_sha256']}), the same one Stage 0 re-verifies every "
            f"harness witness with. Accept iff the witness checks; the artifact shape is the "
            f"checker's artifact_schema."
        )
        objective = {
            "created_at": stamp,
            "funder": FUNDER,
            "goal": goal,
            "statement": statement_text(exp_id, spec, kind, extra),
            "reward": int(reward),
            "verifier": verifier,
            "artifact_schema": base.get("artifact_schema") or {},
        }
        provenance["certificate_kind"] = witness
        provenance["base_objective"] = {
            "path": CERTIFICATE_OBJECTIVES[witness],
            "sha256": sha256_of(base_path),
        }
        return objective, provenance

    if kind != "replay":
        raise BridgeError(f"unknown kind {kind!r} (certificate, replay)")
    if run is None:
        raise BridgeError("a replay objective pins a run's command: pass --run RUN-*")
    code = run.get("code") or {}
    command_text = code.get("command")
    if not command_text:
        raise BridgeError(f"{run_id}: manifest has no run.code.command to pin")
    if replay_wrapper == "auto":
        command = pinned_replay_command(repo, exp_id, run_id)
    else:
        command = shlex.split(str(command_text)) if replay_wrapper is None else shlex.split(replay_wrapper)
    metrics = (run.get("result") or {}).get("metrics") or {}
    if not isinstance(metrics, dict):
        raise BridgeError(f"{run_id}: result.metrics is not a mapping")
    fields, refused = replay_fields(metrics)
    if not fields:
        raise BridgeError(
            f"{run_id}: no metric survives as a replay field "
            f"({'; '.join(refused) or 'result.metrics is empty'}); a replay needs at least one "
            f"exact integer or boolean with a name that is not time-like"
        )
    example = {name: metrics[name] for name in fields}
    wrapper_note = (
        "The pinned command is the run's own, which writes a run directory and prints prose; "
        "cairn's replay verifier needs one JSON object of the reproducible fields on stdout "
        "and a read-only tree. Until this program ships a replay wrapper, this objective "
        "carries replay_wrapper_required: true and should not be posted."
        if replay_wrapper is None
        else f"Pinned command: {command_text!r}, wrapped by {command!r}, which must print "
             f"one JSON object holding the reproducible fields on stdout."
    )
    extra = (
        f"Verifier: replay. A validator re-runs the pinned command at commit "
        f"{code.get('commit')} and accepts iff every reproducible field comes out identical: "
        f"{', '.join(fields)}. {wrapper_note}"
    )
    objective = {
        "created_at": stamp,
        "funder": FUNDER,
        "goal": goal,
        "statement": statement_text(exp_id, spec, kind, extra),
        "reward": int(reward),
        "verifier": {
            "kind": "replay",
            "command": command,
            "cwd": ".",
            "reproducible_fields": fields,
            "timeout_seconds": timeout,
        },
        "artifact_schema": {
            "type": "object",
            "required": ["results"],
            "properties": {
                "results": {
                    "type": "object",
                    "description": "The JSON object the pinned command prints; every field in "
                                   "reproducible_fields must be present and equal.",
                }
            },
            "example": {"results": example},
        },
    }
    provenance["replay"] = {
        "fields": fields,
        "refused_fields": refused,
        "wrapper": replay_wrapper,
        "replay_wrapper_required": replay_wrapper is None,
        "audited_read_only_wrapper": replay_wrapper == "auto",
    }
    return objective, provenance


# -- artifact --------------------------------------------------------------------

# Where a driver keeps the witnesses it claimed. In order of preference: the
# sidecar harness/certificate_sidecar.py writes, then the run's own result
# files. The committed runs that claim discrete logs keep them in three
# different shapes -- a `certificates` list of {kind, statement, verified}
# entries (EXP-DTREE-001), a `certificates.json` of flat {P, Q, k} rows under
# one top-level `curve` (EXP-ECDLP-612fb1), and per-instance `certificate_dl`
# blocks (EXP-BINSTD-5d3ec0) -- so the finder reads the shape the checker
# needs, not a layout. A row that lacks a required field is not a witness
# and is skipped, never completed from elsewhere.
WITNESS_FILES = ("certificate.json", "raw-result.json", "certificates.json")
WITNESS_DEPTH = 6


def required_fields(repo: Path, witness_kind: str) -> list[str]:
    """What the pinned checker's artifact_schema requires: the shape a witness must have."""
    base = json.loads((repo / CERTIFICATE_OBJECTIVES[witness_kind]).read_text(encoding="utf-8"))
    return list((base.get("artifact_schema") or {}).get("required") or [])


def _as_statement(entry: dict[str, Any], required: list[str], curve: Any) -> dict[str, Any] | None:
    """One witness row as a checker artifact: its own `statement` when it carries
    one, else its own fields, with a missing `curve` taken from the enclosing
    file's top-level curve (p, a, b only) when there is one."""
    statement = entry.get("statement")
    if isinstance(statement, dict):
        candidate = dict(statement)
    else:
        candidate = {name: entry[name] for name in required if name in entry}
    if "curve" in required and "curve" not in candidate and isinstance(curve, dict):
        if all(key in curve for key in ("p", "a", "b")):
            candidate["curve"] = {key: curve[key] for key in ("p", "a", "b")}
    if all(name in candidate for name in required):
        return candidate
    return None


def _walk_witnesses(node: Any, witness_kind: str, required: list[str], curve: Any,
                    where: str, depth: int, found: list[dict[str, Any]]) -> None:
    if depth > WITNESS_DEPTH:
        return
    if isinstance(node, dict):
        kind = node.get("kind")
        if kind in (None, witness_kind):
            statement = _as_statement(node, required, curve)
            if statement is not None and (kind == witness_kind or "statement" in node):
                found.append({"statement": statement, "source": where,
                              "verified": node.get("verified")})
                return
        for key, value in node.items():
            if key == "statement":
                continue
            _walk_witnesses(value, witness_kind, required, curve, f"{where}.{key}", depth + 1, found)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _walk_witnesses(value, witness_kind, required, curve, f"{where}[{index}]", depth + 1, found)


def witnesses(repo: Path, exp_id: str, run_id: str) -> list[dict[str, Any]]:
    """Every witness statement a run kept on disk, in file order, each as
    {statement, source, verified}. Empty when the run kept only a verdict."""
    _, run = load_manifest(repo, exp_id, run_id)
    witness_kind = certificate_kind({}, run)
    if witness_kind not in CERTIFICATE_OBJECTIVES:
        return []
    required = required_fields(repo, witness_kind)
    run_dir = repo / "experiments" / exp_id / "runs" / run_id
    found: list[dict[str, Any]] = []
    for name in WITNESS_FILES:
        path = run_dir / name
        if not path.is_file():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        curve = doc.get("curve") if isinstance(doc, dict) else None
        _walk_witnesses(doc, witness_kind, required, curve, name, 0, found)
    # A witness is its content. Drivers write the same statement in two
    # places (a `certificates` list beside the raw rows it was built from, a
    # certificates.json beside raw-result.json), and one statement kept twice
    # is one witness, kept where it was first seen.
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for row in found:
        key = json.dumps(row["statement"], sort_keys=True, separators=(",", ":"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def artifact(repo: Path, exp_id: str, run_id: str, index: int = 0) -> dict[str, Any]:
    """The claim a run produced, in its objective's shape: witness `index` of
    the ones it kept (one claim is one witness; a run with many is many
    claims), or the exact metrics for a replay."""
    _, run = load_manifest(repo, exp_id, run_id)
    witness = certificate_kind({}, run)
    if witness in CERTIFICATE_OBJECTIVES:
        kept = witnesses(repo, exp_id, run_id)
        if not kept:
            raise BridgeError(
                f"{run_id} claims a {witness} witness but no statement is on disk "
                f"(no certificate.json beside the manifest, none in raw-result.json or "
                f"certificates.json); a driver keeps it with harness/certificate_sidecar.py after "
                f"write_run, and a run that did not cannot be claimed on the network without being re-run"
            )
        if not 0 <= index < len(kept):
            raise BridgeError(f"{run_id} keeps {len(kept)} witness(es); --index {index} is out of range")
        return kept[index]["statement"]
    metrics = (run.get("result") or {}).get("metrics") or {}
    fields, _ = replay_fields(metrics if isinstance(metrics, dict) else {})
    if not fields:
        raise BridgeError(f"{run_id}: no replayable metric to claim")
    return {"results": {name: metrics[name] for name in fields}}


# -- record ----------------------------------------------------------------------


def record_block(exp_id: str, run_id: str | None, objective_id: str, claim_id: str, verdict: str,
                 node: str, log_head: str | None, settled: bool, checker_sha256: str | None,
                 network: str, recorded_at: str | None, witness: str | None = None) -> dict[str, Any]:
    if verdict not in VERDICTS:
        raise BridgeError(f"verdict must be one of {', '.join(VERDICTS)}, not {verdict!r}")
    block: dict[str, Any] = {
        "network": network,
        "objective_id": objective_id,
        "claim_id": claim_id,
        "verdict": verdict,
        "node": node,
        "log_head": log_head,
        "settled": bool(settled),
        "experiment_id": exp_id,
        "recorded_at": recorded_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    }
    if run_id:
        block["run_id"] = run_id
    if checker_sha256:
        block["checker_sha256"] = checker_sha256
    if witness:
        # Which of the run's witnesses the claim carried: a verdict on one
        # witness of a run with many is a verdict on that one, not on the run.
        block["witness"] = witness
    if verdict in ("unavailable", "invalid_spec"):
        # Invariant (b) of the integration plan, written into the block so a
        # reader does not have to know it: a verdict that does not settle
        # says nothing about the artifact and may back no direction.
        block["backs_direction"] = False
        block["note"] = (
            "the node could not check this artifact (or the objective was malformed); "
            "this block is a fact about that node and backs no direction and no proof_ref"
        )
    return block


# -- check -----------------------------------------------------------------------


def check(objective: dict[str, Any], repo: Path | None) -> list[str]:
    """Problems cairn would find, without a cairn binary. Empty is clean."""
    problems: list[str] = []
    for field in ("created_at", "funder", "goal", "statement", "reward", "verifier"):
        if field not in objective:
            problems.append(f"missing {field}")
    if "created_at" in objective and not rfc3339_ok(objective["created_at"]):
        problems.append(
            f"created_at {objective['created_at']!r} is not an RFC 3339 date-time with a UTC offset"
        )
    verifier = objective.get("verifier")
    if not isinstance(verifier, dict):
        return problems + ["verifier must be an object"]
    kind = verifier.get("kind")
    if not isinstance(objective.get("reward"), int) or isinstance(objective.get("reward"), bool):
        problems.append("reward must be an integer")
    if kind == "replay":
        command = verifier.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(c, str) for c in command):
            problems.append("replay.command must be a non-empty array of strings")
        fields = verifier.get("reproducible_fields")
        if not isinstance(fields, list) or not fields:
            problems.append("replay.reproducible_fields must be a non-empty array")
        else:
            for name in fields:
                if not isinstance(name, str):
                    problems.append("replay.reproducible_fields must hold strings")
                elif time_like(name):
                    problems.append(f"replay field {name!r} has a time-like name; cairn refuses it")
        timeout = verifier.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS)
        if not isinstance(timeout, int) or timeout < 1 or timeout > MAX_TIMEOUT_SECONDS:
            problems.append(f"replay.timeout_seconds must be 1..{MAX_TIMEOUT_SECONDS}")
        cwd = str(verifier.get("cwd", "."))
        if cwd.startswith("/") or ".." in cwd.split("/"):
            problems.append("replay.cwd must stay inside the root")
    elif kind == "certificate":
        for field in ("checker", "checker_sha256", "entrypoint"):
            if field not in verifier:
                problems.append(f"certificate.{field} missing")
        if repo is not None and "checker" in verifier and "checker_sha256" in verifier:
            pinned = repo / str(verifier["checker"])
            if not pinned.is_file():
                problems.append(f"pinned checker {verifier['checker']} is not in the tree")
            elif sha256_of(pinned) != verifier["checker_sha256"]:
                problems.append(f"pinned checker {verifier['checker']} does not match checker_sha256")
    elif kind is None:
        problems.append("verifier.kind missing")
    else:
        problems.append(f"verifier.kind {kind!r}: this tool renders certificate and replay only")
    return problems


# -- CLI ---------------------------------------------------------------------------


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=str(REPO), help="repository root (default: this checkout)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("render", help="write an objective file for an experiment")
    p.add_argument("--exp", required=True)
    p.add_argument("--run", help="the run whose command and metrics a replay pins")
    p.add_argument("--kind", choices=("certificate", "replay"))
    p.add_argument("--reward", type=int, default=0, help="units; 0 until the Coordinator funds it")
    p.add_argument("--created-at", help="override the objective's created_at (RFC 3339)")
    p.add_argument("--replay-wrapper", help="'auto' for a pinned read-only adapter, or a draft command")
    p.add_argument("--out", help="objective file to write (default: cairn/objectives/<EXP>[-<RUN>].json)")
    p.add_argument("--log", default="$CAIRN_LOG", help="log path to print in the post line")

    p = sub.add_parser("artifact", help="the claim artifact a run produced")
    p.add_argument("--exp", required=True)
    p.add_argument("--run", required=True)
    p.add_argument("--index", type=int, default=0, help="which kept witness (default 0); one claim is one witness")
    p.add_argument("--all", action="store_true", help="every kept witness, as a JSON list with sources")
    p.add_argument("--out")

    p = sub.add_parser("record", help="print an external_verification block")
    p.add_argument("--exp", required=True)
    p.add_argument("--run")
    p.add_argument("--objective", required=True)
    p.add_argument("--claim", required=True)
    p.add_argument("--verdict", required=True, choices=VERDICTS)
    p.add_argument("--node", required=True, help="the node's HTTP address the verdict was read from")
    p.add_argument("--log-head", help="the node's log head (GET /chain) when it was read")
    p.add_argument("--settled", action="store_true")
    p.add_argument("--checker-sha256")
    p.add_argument("--witness", help="which kept witness the claim carried, as `artifact` printed it")
    p.add_argument("--network", default=NETWORK)
    p.add_argument("--recorded-at")
    p.add_argument("--out", help="write the block as a standalone YAML file as well")

    p = sub.add_parser("check", help="hold an objective file to cairn's shape rules")
    p.add_argument("file")

    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    try:
        if args.command == "render":
            objective, provenance = render(
                repo, args.exp, args.run, args.kind, args.reward, args.created_at, args.replay_wrapper
            )
            problems = check(objective, repo)
            if problems:
                raise BridgeError("rendered objective fails its own check: " + "; ".join(problems))
            out = Path(args.out) if args.out else repo / "cairn" / "objectives" / (
                f"{args.exp}{'-' + args.run if args.run else ''}.json"
            )
            _write_json(out, objective)
            side = out.with_suffix(".provenance.yaml")
            side.write_text(yaml.safe_dump(provenance, sort_keys=True), encoding="utf-8")
            print(f"wrote {out}")
            print(f"      {side}")
            replay = provenance.get("replay", {})
            if replay and not replay.get("audited_read_only_wrapper"):
                print("NOT POSTABLE YET: replay needs an audited read-only wrapper "
                      "(--replay-wrapper auto is supported for one pinned run)")
            else:
                print("the Coordinator may prepare publication with:")
                print(f"  python3 tools/cairn_publish_objective.py --exp {args.exp} "
                      f"--run {args.run or '<RUN-ID>'}")
            return 0
        if args.command == "artifact":
            if args.all:
                value: Any = witnesses(repo, args.exp, args.run)
            else:
                value = artifact(repo, args.exp, args.run, args.index)
                kept = witnesses(repo, args.exp, args.run)
                if kept:
                    chosen = kept[args.index]
                    print(f"{args.run} keeps {len(kept)} witness(es) on disk; this is #{args.index} "
                          f"from {chosen['source']} (verified by the harness: {chosen['verified']})",
                          file=sys.stderr)
            if args.out:
                _write_json(Path(args.out), value)
                print(f"wrote {args.out}")
            else:
                print(json.dumps(value, indent=2, sort_keys=True))
            return 0
        if args.command == "record":
            block = record_block(
                args.exp, args.run, args.objective, args.claim, args.verdict, args.node,
                args.log_head, args.settled, args.checker_sha256, args.network, args.recorded_at,
                args.witness,
            )
            text = yaml.safe_dump({"external_verification": [block]}, sort_keys=False)
            if args.out:
                Path(args.out).write_text(text, encoding="utf-8")
                print(f"wrote {args.out}")
            print(text, end="")
            return 0
        if args.command == "check":
            objective = json.loads(Path(args.file).read_text(encoding="utf-8"))
            problems = check(objective, repo)
            if problems:
                for problem in problems:
                    print(f"  {problem}")
                return 1
            print(f"{args.file}: shape ok ({objective.get('verifier', {}).get('kind')})")
            return 0
    except BridgeError as error:
        print(f"exp_to_objective: {error}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
