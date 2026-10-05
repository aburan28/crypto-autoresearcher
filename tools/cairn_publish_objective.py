#!/usr/bin/env python3
"""Prepare or publish a Coordinator-approved EXP objective to a live Cairn node.

Only the signer sees the funding key. Cairn signs the canonical record without
opening the node's locked log; the HTTP node queues it and decides admission.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

from exp_to_objective import (BridgeError, REPO, approval, check, infer_kind,
                              load_manifest, load_spec, pinned_replay_command,
                              render, sha256_of)


def local_node(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise BridgeError("publication requires a loopback HTTP Cairn node")
    if parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query:
        raise BridgeError("node URL must be a bare loopback origin")
    return url.rstrip("/")


def committed(repo: Path, paths: list[str]) -> None:
    for path in sorted(set(paths)):
        if Path(path).is_absolute() or ".." in Path(path).parts:
            raise BridgeError(f"unsafe provenance path {path!r}")
        tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", path],
                                 capture_output=True, text=True, timeout=10)
        clean = subprocess.run(["git", "-C", str(repo), "diff", "HEAD", "--quiet", "--", path],
                               capture_output=True, timeout=10)
        if tracked.returncode != 0 or clean.returncode != 0:
            raise BridgeError(f"{path}: must be committed and unchanged before publication")


def funding(repo: Path, exp_id: str, reward: int, decision_id: str | None,
            funder: str | None) -> str | None:
    if reward < 0:
        raise BridgeError("reward cannot be negative")
    if reward == 0:
        return None
    if not decision_id or not funder:
        raise BridgeError("positive reward requires --funding-decision and --funder")
    if not decision_id.startswith("DEC-") or "/" in decision_id or ".." in decision_id:
        raise BridgeError("malformed funding decision id")
    path = repo / "ledger" / "decisions" / f"{decision_id}.yaml"
    if not path.is_file():
        raise BridgeError(f"funding decision {decision_id} is missing")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    dec = doc.get("coordinator_decision") if isinstance(doc, dict) else None
    budget = dec.get("cairn_funding") if isinstance(dec, dict) else None
    targets = dec.get("target_ids") if isinstance(dec, dict) else None
    if (not isinstance(budget, dict) or dec.get("id") != decision_id
            or dec.get("decided_by") != "coordinator" or dec.get("decision") != "approve"
            or not isinstance(targets, list) or exp_id not in targets
            or type(budget.get("reward")) is not int or budget["reward"] != reward
            or budget.get("funder") != funder):
        raise BridgeError(f"{decision_id}: does not authorize reward {reward} from {funder}")
    committed(repo, [str(path.relative_to(repo))])
    return sha256_of(path)


def request_json(url: str, body: dict | None = None) -> dict:
    data = json.dumps(body, sort_keys=True, separators=(",", ":")).encode() if body is not None else None
    request = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        message = error.read(4096).decode("utf-8", errors="replace")
        raise BridgeError(f"Cairn HTTP {error.code}: {message}") from error
    if not isinstance(result, dict):
        raise BridgeError("Cairn returned a non-object response")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--exp", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--kind", choices=("certificate", "replay"))
    parser.add_argument("--reward", type=int, default=0)
    parser.add_argument("--funding-decision")
    parser.add_argument("--funder", help="public key authorized by the funding decision")
    parser.add_argument("--cairn-bin", type=Path)
    parser.add_argument("--identity", type=Path)
    parser.add_argument("--node", default="http://127.0.0.1:8081")
    parser.add_argument("--publish", action="store_true", help="sign and queue the objective")
    args = parser.parse_args(argv)
    try:
        repo = args.repo.resolve()
        node = local_node(args.node)
        _, spec = load_spec(repo, args.exp)
        _, run = load_manifest(repo, args.exp, args.run)
        rights = approval(repo, args.exp, spec, run)
        kind = args.kind or infer_kind(spec, run)
        wrapper = "auto" if kind == "replay" else None
        objective, provenance = render(repo, args.exp, args.run, kind, args.reward, None, wrapper)
        issues = check(objective, repo)
        if issues:
            raise BridgeError("objective fails shape check: " + "; ".join(issues))
        paths = ["tools/cairn_publish_objective.py", "tools/exp_to_objective.py",
                 provenance["specification"]["path"], provenance["run"]["manifest"]]
        paths += [part["path"] for part in rights.values() if isinstance(part, dict)]
        if kind == "certificate":
            paths += [provenance["base_objective"]["path"], objective["verifier"]["checker"]]
        else:
            command = pinned_replay_command(repo, args.exp, args.run)
            if command != objective["verifier"]["command"]:
                raise BridgeError("replay command changed after rendering")
            paths += [command[1], "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S1/raw-result.json"]
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True, timeout=30, check=True)
            observed = json.loads(result.stdout)
            expected = objective["artifact_schema"]["example"]["results"]
            if observed != expected or type(observed) is not dict:
                raise BridgeError("read-only replay disagrees with archived exact metrics")
        committed(repo, paths)
        funding_hash = funding(repo, args.exp, args.reward, args.funding_decision, args.funder)
        prepared = {"objective": objective, "provenance": provenance,
                    "funding_decision_sha256": funding_hash, "status": "prepared"}
        if not args.publish:
            print(json.dumps(prepared, indent=2, sort_keys=True))
            return 0
        if not args.cairn_bin or not args.identity:
            raise BridgeError("--publish requires --cairn-bin and --identity")
        with tempfile.TemporaryDirectory(prefix="cairn-objective-") as temp:
            draft = Path(temp) / "draft.json"
            draft.write_text(json.dumps(objective, sort_keys=True, separators=(",", ":")))
            signed = subprocess.run([str(args.cairn_bin), "sign-objective", str(draft),
                                     "--identity", str(args.identity)], capture_output=True,
                                    text=True, timeout=30, check=True)
            record = json.loads(signed.stdout)
        if args.reward and record.get("funder") != args.funder:
            raise BridgeError("signing identity differs from Coordinator funding decision")
        queued = request_json(node + "/submit?kind=objective", record)
        objective_id = queued.get("queued")
        if not isinstance(objective_id, str):
            raise BridgeError(f"node did not return a queued objective id: {queued}")
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                admitted = request_json(node + "/objective/" + urllib.parse.quote(objective_id, safe=":"))
            except BridgeError as error:
                if "HTTP 404" not in str(error):
                    raise
                time.sleep(1)
                continue
            if admitted.get("record") != record:
                raise BridgeError("admitted objective differs from signed record")
            print(json.dumps({"objective_id": objective_id, "status": "admitted",
                              "provenance": provenance}, indent=2, sort_keys=True))
            return 0
        print(json.dumps({"objective_id": objective_id, "status": "queued_not_yet_admitted",
                          "provenance": provenance}, indent=2, sort_keys=True))
        return 3
    except (BridgeError, OSError, ValueError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired) as error:
        print(f"cairn_publish_objective: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
