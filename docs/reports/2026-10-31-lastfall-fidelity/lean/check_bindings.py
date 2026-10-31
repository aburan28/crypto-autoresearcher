#!/usr/bin/env python3
"""Compare the immutable LastFall inputs and receipt hashes; never invokes Lean."""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = "199f3aaaa6d37d2fce59f4d8c8fe8d2eb8b50672"
PLAN = "2b0cfe1401831c9493cfe047a515955f38d037b8"
RECEIPT = "docs/reports/2026-10-31-hosted-formal-receipts/receipts/lastfall-is-max-degree-fall.json"


def blob(revision: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{revision}:{path}"], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return result.stdout if result.returncode == 0 else None


def digest(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def reconstructed_root(revision: str) -> bytes:
    """Reproduce the reviewed generator's header and sorted tracked imports."""
    module = ast.parse(blob(revision, "orchestration/formal/workspace.py"))
    header = next(ast.literal_eval(node.value) for node in module.body
                  if isinstance(node, ast.Assign)
                  and any(isinstance(name, ast.Name) and name.id == "_HEADER"
                          for name in node.targets))
    listing = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", revision,
         "formal/CryptoResearch"], cwd=ROOT, text=True,
    )
    modules = sorted(path[len("formal/"):-len(".lean")].replace("/", ".")
                     for path in listing.splitlines() if path.endswith(".lean"))
    return (header.format(library="CryptoResearch") + "\n"
            + "".join(f"import {name}\n" for name in modules)).encode()


def main() -> None:
    raw = blob(SOURCE, RECEIPT)
    assert raw is not None
    receipt = json.loads(raw)
    provenance = receipt["provenance"]
    checks = []
    for key, path in (
        ("theorem_sha256", "formal/CryptoResearch/FallDegree/LastFall.lean"),
        ("task_spec_sha256", "formal/targets/lastfall-is-max-degree-fall.yaml"),
        ("lean_toolchain_sha256", "formal/lean-toolchain"),
        ("lake_manifest_sha256", "formal/lake-manifest.json"),
    ):
        actual = digest(blob(SOURCE, path))
        checks.append({"path": path, "expected": provenance[key], "actual": actual,
                       "matches_receipt": actual == provenance[key],
                       "unchanged_at_plan": blob(SOURCE, path) == blob(PLAN, path)})
    map_checks = {}
    for key, prefix in (("workspace_inputs", "formal/"), ("verifier_inputs", "")):
        rows = []
        for path, expected in provenance[key].items():
            full_path = prefix + path
            current = digest(blob(SOURCE, full_path))
            historical = digest(blob(provenance["source_commit"], full_path))
            rows.append({"path": full_path, "expected": expected,
                         "review_source_sha256": current,
                         "receipt_source_sha256": historical,
                         "review_source_match": current == expected,
                         "receipt_source_match": historical == expected})
        map_checks[key] = rows
    out = {
        "schema": "lastfall.static_input_check/v1",
        "source_commit": SOURCE,
        "plan_commit": PLAN,
        "receipt_path": RECEIPT,
        "receipt_sha256": digest(raw),
        "receipt_source_commit": provenance["source_commit"],
        "direct_input_checks": checks,
        "input_map_checks": map_checks,
        "generated_root_reconstruction": {
            "path": "formal/CryptoResearch.lean",
            "note": "Derived from the pinned generator header and tracked module names; not a historical file readback.",
            "expected": provenance["workspace_inputs"]["CryptoResearch.lean"],
            "review_source_sha256": digest(reconstructed_root(SOURCE)),
            "receipt_source_sha256": digest(reconstructed_root(provenance["source_commit"])),
        },
        "receipt_machine_status": receipt["verification"]["status"],
        "historical_audit_log": receipt["audit_log"],
        "fresh_lean_execution": False,
        "scope": "Git content and receipt consistency only; no execution authentication or fresh kernel check.",
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
