#!/usr/bin/env python3
"""Validate design artifacts and immutable inputs. Does not execute an experiment."""
import argparse
import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    plan = json.loads((out / "plan.json").read_text())
    boundary = json.loads((out / "measurement-boundary.json").read_text())
    provenance = json.loads((out / "design-provenance.json").read_text())
    assert not plan["official_ledger_registration"]
    assert plan["status"] == "proposed_design_not_executed"
    assert plan["main_prime_sample"]["blocks"] == 36
    assert plan["main_prime_sample"]["total_moduli"] == 108
    assert plan["exact_anchor_cohort"]["total_moduli"] == 18
    assert plan["curve_sampling"]["population_models_per_modulus"] == 32
    assert plan["curve_sampling"]["matched_candidate_models_per_modulus"] == 512
    assert boundary["primary_value"] == "min(search_group_calls/sqrt(ell),20)"
    assert "supersede" in boundary["precedence"]
    checks = []
    for record in provenance["sources"]:
        assert sha(repo / record["path"]) == record["sha256"]
        checks.append({"path": record["path"], "sha256": record["sha256"], "unchanged": True})
    identities = out / "inputs/historical-curve-identities.csv"
    assert sha(identities) == provenance["sources"][1]["sha256"]
    with identities.open() as handle:
        curves = list(csv.DictReader(handle))
    assert len(curves) == 6
    assert len({r["curve_uid"] for r in curves}) == 6
    for row in curves:
        assert int(row["group_order"]) == int(row["subgroup_order"]) * int(row["cofactor"])
    for path in out.rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    for path in out.rglob("*.json"):
        json.loads(path.read_text())
    for path in out.glob("*.svg"):
        ET.parse(path)
    for label, target in re.findall(r"\[([^\]]*)\]\(([^)]*)\)", (out / "protocol.md").read_text()):
        assert (out / target).exists(), (label, target)
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1")
    tracked = subprocess.check_output(["git", "ls-files", "experiments/EXP-ECDLP-4c6a09/reports"], cwd=repo, env=env, text=True).splitlines()
    history = []
    for rel in tracked:
        if rel.startswith(str(out.relative_to(repo)) + "/"):
            continue
        if Path(rel).suffix not in {".pdf", ".svg", ".typ", ".py"}:
            continue
        expected = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=repo, env=env)
        assert (repo / rel).read_bytes() == expected, rel
        history.append({"path": rel, "sha256": sha(repo / rel), "matches_committed_bytes": True})
    frontier = subprocess.check_output(["git", "ls-files", "knowledge/frontiers/ecdlp"], cwd=repo, env=env, text=True).splitlines()
    changed = subprocess.check_output(["git", "diff", "HEAD", "--name-only", "--", "knowledge/frontiers/ecdlp"], cwd=repo, env=env, text=True).splitlines()
    assert changed == []
    record = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "design_only": True, "new_attack_results": None,
        "checks": {"json_python_svg_syntax": "pass", "internal_markdown_links": "pass",
                   "sample_accounting": "pass", "cap_addendum_precedence": "pass",
                   "historical_identity_copy": "byte-identical", "primary_rho_maximum": 36 * 3 * 8 * 4 * 4,
                   "primary_bsgs_maximum": 36 * 3 * 8 * 4},
        "immutable_evidence": checks, "historical_graphs_and_sources": history,
        "frontier_check": {"indexed_paths": frontier, "modified_paths": changed,
                           "scope": "Inventory and unchanged status; not a full sealed-bound audit",
                           "reason_no_update": "A proposed experiment adds no verified finding or frontier claim"},
        "new_figures": ["comparison-design.svg", "historical-subgroup-confounding.svg"],
        "independent_scientific_review": None,
    }
    (out / "design-checks.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": "pass_design_checks", "historical_graph_files_unchanged": len(history),
                      "new_attack_trials": 0}))


if __name__ == "__main__":
    main()
