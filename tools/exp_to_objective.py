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

VERDICTS = ("accept", "reject", "unavailable", "invalid_spec")

DEFAULT_TIMEOUT_SECONDS = 600
MAX_TIMEOUT_SECONDS = 86_400


class BridgeError(Exception):
    """A refusal with a reason a person can act on. Exit 2."""


# -- reading the experiment ------------------------------------------------------


def load_spec(repo: Path, exp_id: str) -> tuple[Path, dict[str, Any]]:
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


def normalise_ts(value: Any) -> str:
    if isinstance(value, dt.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat()
    if isinstance(value, dt.date):
        return dt.datetime(value.year, value.month, value.day, tzinfo=dt.timezone.utc).isoformat()
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return text


# -- render ----------------------------------------------------------------------


def render(repo: Path, exp_id: str, run_id: str | None, kind: str | None, reward: int,
           created_at: str | None, replay_wrapper: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    """The objective and its provenance sidecar."""
    spec_path, spec = load_spec(repo, exp_id)
    run = None
    manifest_path = None
    if run_id:
        manifest_path, run = load_manifest(repo, exp_id, run_id)
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
        else f"Pinned command: {command_text!r}, wrapped by {replay_wrapper!r}, which must print "
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
    }
    return objective, provenance


# -- artifact --------------------------------------------------------------------


def artifact(repo: Path, exp_id: str, run_id: str) -> dict[str, Any]:
    """The claim a run produced, in its objective's shape."""
    _, run = load_manifest(repo, exp_id, run_id)
    run_dir = repo / "experiments" / exp_id / "runs" / run_id
    witness = certificate_kind({}, run)
    if witness in CERTIFICATE_OBJECTIVES:
        # The statement with the witness in it. harness/certificate_sidecar.py
        # writes it as certificate.json beside the manifest, when the driver
        # asked it to; a run that kept only the kind and a verified flag has
        # nothing on disk to claim.
        candidates = [run_dir / "certificate.json"]
        for path in candidates:
            if path.is_file():
                doc = json.loads(path.read_text(encoding="utf-8"))
                statement = doc.get("statement") if isinstance(doc, dict) else None
                if isinstance(statement, dict):
                    return statement
        raw = run_dir / "raw-result.json"
        if raw.is_file():
            doc = json.loads(raw.read_text(encoding="utf-8"))
            result = doc.get("result") if isinstance(doc, dict) else None
            cert = (result or {}).get("certificate") if isinstance(result, dict) else None
            if isinstance(cert, dict) and isinstance(cert.get("statement"), dict):
                return cert["statement"]
        raise BridgeError(
            f"{run_id} claims a {witness} witness but no statement is on disk "
            f"(no certificate.json beside the manifest, none in raw-result.json); a driver keeps "
            f"it with harness/certificate_sidecar.py after write_run, and a run that did not "
            f"cannot be claimed on the network without being re-run"
        )
    metrics = (run.get("result") or {}).get("metrics") or {}
    fields, _ = replay_fields(metrics if isinstance(metrics, dict) else {})
    if not fields:
        raise BridgeError(f"{run_id}: no replayable metric to claim")
    return {"results": {name: metrics[name] for name in fields}}


# -- record ----------------------------------------------------------------------


def record_block(exp_id: str, run_id: str | None, objective_id: str, claim_id: str, verdict: str,
                 node: str, log_head: str | None, settled: bool, checker_sha256: str | None,
                 network: str, recorded_at: str | None) -> dict[str, Any]:
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
    p.add_argument("--replay-wrapper", help="command that runs the driver and prints the fields as JSON")
    p.add_argument("--out", help="objective file to write (default: cairn/objectives/<EXP>[-<RUN>].json)")
    p.add_argument("--log", default="$CAIRN_LOG", help="log path to print in the post line")

    p = sub.add_parser("artifact", help="the claim artifact a run produced")
    p.add_argument("--exp", required=True)
    p.add_argument("--run", required=True)
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
            if provenance.get("replay", {}).get("replay_wrapper_required"):
                print("NOT POSTABLE YET: the pinned command needs a replay wrapper "
                      "(see --replay-wrapper); the objective says so in its statement")
            else:
                print("to post, the Coordinator runs:")
                print(f"  cairn --log {args.log} --root {repo} post {out} --identity <coordinator-identity.json>")
            return 0
        if args.command == "artifact":
            value = artifact(repo, args.exp, args.run)
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
