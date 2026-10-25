#!/usr/bin/env python3
"""Check four additive prior-art corrections against frozen sources and gate logs."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REGISTRY = ROOT / "tools/schema_supersession_registry.yaml"
IDS = {
    "486aa2": ("0741cf7be81d4baba9c0f36e7308d5054dd1348c6f979f991b6ecfa5ed913d77", "d9d1674238aa1c276b2bb8f196b76288d91813418dc686e59693799496186805", 7),
    "839ced": ("66308757a31a3269401d38a33b792cbb4d118306c2af0b39cf2929f4a3415114", "92e9bef6da292a34953673cf28ed89a72ed561acbe18055852b287033af954a5", 7),
    "8f4f02": ("0addd3c820567481c907e3b56aa214c76155772b6a1afcf756323e57a9508594", "fc101161be2402c453d5a821cca811823f5a8d86504fda3dd4744a812027fa03", 7),
    "ef3939": ("5c415a3e4302d76fe3f4fc581e5acbffa0fe4d3b8261c2a66fb8ee87186c2223", "15b85b2e7d9e999f247ede9304dc4abb8c968fc89ae6362a3de190dc9e17181e", 9),
}
CARDS = {
    "KR-IC-f5c584": ("index-calculus", "e32899f1aa3acf0bcd8060d06f4c0bc40456022d627c9041ff290c2690a8f61f"),
    "KR-IC-fbdb61": ("index-calculus", "18ce0bacbbf6b1e520f3e8fa227d3b10ff0439cbe0cf02f43cbc346708ee4723"),
    "KR-IC-889857": ("index-calculus", "eee3952b0fafa3f392eb1ac0ae2ae8490d3b3307d228a2e560bad485ccaaf0f1"),
    "KR-IC-73db3f": ("index-calculus", "fbf68621acd0ab862e3698899feaf1885468cc42a177b9f308fbca5847bebf43"),
    "KR-IC-1fcdbc": ("index-calculus", "e734c97f8aee9fd0ce7229075f0daaab53abf2839dbac7032336379ec6304b76"),
    "KR-RHO-825bca": ("generic-rho", "786494e90e46be71a3672ed05e07c75af34792c6e688a0a566d12d513f152e52"),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def error_lines(path: Path) -> set[str]:
    return {line for line in path.read_text().splitlines() if line.startswith("  - ")}


def main() -> None:
    registry = yaml.safe_load(REGISTRY.read_text())
    require(registry.get("schema") == "schema-supersession-registry-v1", "registry schema changed")
    by_path = {row["superseded_path"]: row for row in registry["records"]}
    checked = []
    used_cards = set()
    for suffix, (old_sha, new_sha, expected_removed) in IDS.items():
        name = f"IDEA-20261006-{suffix}"
        old_rel = f"ledger/proposals/{name}.yaml"
        new_rel = f"ledger/corrections/schema-supersessions/20261023/ledger__proposals__{name}.v2.yaml"
        old_path, new_path = ROOT / old_rel, ROOT / new_rel
        require(digest(old_path) == old_sha, f"original source changed: {name}")
        require(digest(new_path) == new_sha, f"replacement source changed: {name}")
        entry = by_path.get(old_rel)
        require(entry is not None and entry.get("kind") == "ledger", f"unregistered source: {name}")
        require(entry.get("superseded_sha256") == old_sha and entry.get("superseding_sha256") == new_sha, f"registry hash mismatch: {name}")
        require(entry.get("superseding_path") == new_rel, f"registry path mismatch: {name}")
        old, new = yaml.safe_load(old_path.read_text()), yaml.safe_load(new_path.read_text())
        old_rest, new_rest = copy.deepcopy(old), copy.deepcopy(new)
        old_prior = old_rest["idea"].pop("prior_art")
        new_prior = new_rest["idea"].pop("prior_art")
        require(old_rest == new_rest, f"non-prior-art fields changed: {name}")
        require(old_prior["frontier_map"] == "knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim 2026-10-06)", f"unexpected archived frontier: {name}")
        require(new_prior["frontier_map"] == "knowledge/frontiers/ecdlp/index-calculus", f"invalid replacement frontier: {name}")
        require((ROOT / new_prior["frontier_map"]).is_dir(), f"frontier absent: {name}")
        old_rows, new_rows = old_prior.pop("nearest"), new_prior.pop("nearest")
        old_prior.pop("frontier_map")
        new_prior.pop("frontier_map")
        require(old_prior == new_prior, f"other prior-art fields changed: {name}")
        require(len(old_rows) == len(new_rows) and len(old_rows) > 0, f"nearest count changed: {name}")
        for original, corrected in zip(old_rows, new_rows):
            ref = original["ref"]
            require(ref in CARDS, f"unreviewed nearest source: {ref}")
            require(corrected == {"ref": ref, "provenance": "kb", "relation": "adjacent", "relation_detail": original["relation"], "delta": original["delta"]}, f"nearest meaning changed: {name}/{ref}")
            used_cards.add(ref)
        for ref in new_prior["rows_checked"]:
            area = "generic-rho" if ref.startswith("KR-RHO-") else "index-calculus"
            require((ROOT / "knowledge/frontiers/ecdlp" / area / f"{ref}.yaml").is_file(), f"missing listed prior-art card: {name}/{ref}")
        checked.append({"id": name, "original_sha256": old_sha, "replacement_sha256": new_sha, "nearest_count": len(new_rows), "listed_prior_art_rows": len(new_prior["rows_checked"]), "removed_gate_errors": expected_removed})
    require(used_cards == set(CARDS), "source card set changed")
    for ref, (area, sha) in CARDS.items():
        path = ROOT / "knowledge/frontiers/ecdlp" / area / f"{ref}.yaml"
        require(digest(path) == sha, f"source card changed: {ref}")
        require(yaml.safe_load(path.read_text()).get("id") == ref, f"card ID mismatch: {ref}")
    parent_path, after_path = HERE / "validator-parent.log", HERE / "validator.log"
    before, after = error_lines(parent_path), error_lines(after_path)
    removed, added = before - after, after - before
    require(len(before) == 118 and len(after) == 88, "validator totals differ")
    before_paths = {line.split(":", 1)[0] for line in before}
    after_paths = {line.split(":", 1)[0] for line in after}
    require(len(before_paths) == 36 and len(after_paths) == 32, "validator path totals differ")
    require(len(removed) == 30 and not added, "unexpected validator delta")
    for row in checked:
        count = sum(line.startswith(f"  - ledger/proposals/{row['id']}.yaml:") for line in removed)
        require(count == row["removed_gate_errors"], f"wrong gate delta for {row['id']}")
    output = {"schema": "prior-art-correction-audit/v1", "base_commit": "9fc0685a5fd51e5fe66a80d42124f1d522f7c8f5", "proposals": checked, "reviewed_cards_sha256": {ref: sha for ref, (_, sha) in CARDS.items()}, "validator_before": len(before), "validator_after": len(after), "paths_before": len(before_paths), "paths_after": len(after_paths), "removed_errors": sorted(removed), "added_errors": sorted(added), "parent_log_sha256": digest(parent_path), "corrected_log_sha256": digest(after_path), "claim_limit": "metadata and KB source reading only; no measurement or theorem changed"}
    (HERE / "validation.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"{len(checked)} source-bound corrections; ledger errors {len(before)} -> {len(after)}; {len(added)} added")


if __name__ == "__main__":
    main()
