#!/usr/bin/env python3
"""Derive an immutable external_verification draft from a settled Cairn claim.

The node supplies the public record, verdict and settlement. This tool binds
them to one archived run artifact; only a Coordinator can carry the resulting
draft into an evidence record or change scientific status.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
from pathlib import Path

import yaml

from cairn_publish_objective import committed, local_node, request_json
from exp_to_objective import (BridgeError, REPO, approval, artifact, load_manifest,
                              load_spec, record_block, render, witnesses)


def receipt(repo: Path, node: str, exp_id: str, run_id: str, objective_id: str,
            claim_id: str, index: int = 0) -> dict:
    _, spec = load_spec(repo, exp_id)
    _, run = load_manifest(repo, exp_id, run_id)
    rights = approval(repo, exp_id, spec, run)
    suffix = urllib.parse.quote(objective_id, safe=":")
    obj = request_json(node + "/objective/" + suffix)
    if obj.get("id") != objective_id:
        raise BridgeError("objective response does not match requested id")
    live_objective = obj.get("record")
    if not isinstance(live_objective, dict):
        raise BridgeError("objective response has no record")
    kind = (live_objective.get("verifier") or {}).get("kind")
    expected_objective, provenance = render(repo, exp_id, run_id, kind,
                                            live_objective.get("reward"), None,
                                            "auto" if kind == "replay" else None)
    unsigned = {key: value for key, value in live_objective.items()
                if key not in ("funder", "funding_signature")}
    expected_unsigned = {key: value for key, value in expected_objective.items() if key != "funder"}
    if unsigned != expected_unsigned:
        raise BridgeError("settled objective differs from the approved experiment objective")
    paths = ["tools/exp_to_objective.py", "tools/cairn_settlement_receipt.py",
             provenance["specification"]["path"], provenance["run"]["manifest"]]
    paths += [part["path"] for part in rights.values() if isinstance(part, dict)]
    if kind == "certificate":
        paths += [provenance["base_objective"]["path"], live_objective["verifier"]["checker"]]
    else:
        paths += ["tools/cairn_replay_stage1cs.py",
                  "experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S1/raw-result.json"]
    committed(repo, paths)
    settlement = obj.get("settlement")
    if not isinstance(settlement, dict) or settlement.get("claim_id") != claim_id:
        raise BridgeError("claim has no settlement on this objective")
    claim = request_json(node + "/claim/" + urllib.parse.quote(claim_id, safe=":"))
    record = claim.get("record")
    if claim.get("id") != claim_id or not isinstance(record, dict):
        raise BridgeError("claim response does not match requested id")
    if record.get("objective_id") != objective_id:
        raise BridgeError("claim belongs to another objective")
    expected_artifact = artifact(repo, exp_id, run_id, index)
    if record.get("artifact") != expected_artifact:
        raise BridgeError("settled claim artifact differs from the archived run artifact")
    knowledge = request_json(node + "/knowledge/" + urllib.parse.quote(claim_id, safe=":"))
    if knowledge.get("claim_id") != claim_id or knowledge.get("objective_id") != objective_id:
        raise BridgeError("knowledge response does not bind the claim and objective")
    state = knowledge.get("state") or {}
    if state.get("verdict") != "accept" or state.get("standing") != "accepted":
        raise BridgeError("settled claim does not have an accepted pinned verdict")
    chain = request_json(node + "/chain")
    head = chain.get("ledger_head")
    if not isinstance(head, str) or not head:
        raise BridgeError("node did not report a ledger head")
    verifier = live_objective.get("verifier") or {}
    checker_sha = verifier.get("checker_sha256") if verifier.get("kind") == "certificate" else None
    witness = None
    if verifier.get("kind") == "certificate":
        kept = witnesses(repo, exp_id, run_id)
        if index >= len(kept) or index < 0:
            raise BridgeError("witness index is out of range")
        witness = kept[index]["source"]
    block = record_block(exp_id, run_id, objective_id, claim_id, "accept", node, head,
                         True, checker_sha, "cairn", None, witness)
    block["approval_decisions"] = list(dict.fromkeys(
        part["id"] for part in rights.values() if isinstance(part, dict)))
    block["claim_submitter"] = record.get("submitter")
    block["settlement_reward"] = settlement.get("reward")
    block["node_reported_height"] = chain.get("height")
    block["note"] = ("Node-reported settlement and verdict, bound to the archived artifact. "
                     "The Coordinator must review this draft before adding it to evidence; "
                     "it does not change scientific status.")
    return {"external_verification": [block]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--node", default="http://127.0.0.1:8081")
    parser.add_argument("--exp", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--objective", required=True)
    parser.add_argument("--claim", required=True)
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--out", type=Path, help="new YAML draft path; existing files are refused")
    args = parser.parse_args(argv)
    try:
        result = receipt(args.repo.resolve(), local_node(args.node), args.exp, args.run,
                         args.objective, args.claim, args.index)
        output = yaml.safe_dump(result, sort_keys=False)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with args.out.open("x", encoding="utf-8") as stream:
                stream.write(output)
        print(output, end="")
        return 0
    except (BridgeError, OSError, ValueError, TypeError) as error:
        print(f"cairn_settlement_receipt: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
