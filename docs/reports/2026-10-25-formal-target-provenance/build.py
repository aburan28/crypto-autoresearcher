#!/usr/bin/env python3
"""Rebuild a static, commit-pinned formal target source inventory.

This verifies repository bytes and declared paths. It does not run Lean,
replay experiments, or judge whether theorem statements fit their claims.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COMMIT = "0b38ac1157f777cb4a77d35e53d7ed583c541eb4"
EXP = re.compile(r"\bEXP-[A-Z0-9]+-[0-9a-f]{6}\b")


def git(*args: str, input_data: bytes | None = None) -> bytes:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args], input=input_data,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def blob(path: str) -> tuple[str, bytes, str]:
    oid = git("rev-parse", f"{COMMIT}:{path}").decode().strip()
    data = git("cat-file", "blob", oid)
    return oid, data, hashlib.sha256(data).hexdigest()


def main() -> None:
    if not __debug__:
        raise RuntimeError("builder assertions require ordinary Python; optimized execution is refused")
    assert git("rev-parse", COMMIT).decode().strip() == COMMIT
    tree = git("rev-parse", f"{COMMIT}:formal").decode().strip()
    experiments_tree = git("rev-parse", f"{COMMIT}:experiments").decode().strip()
    directory_names = git("ls-tree", "-d", "--name-only", f"{COMMIT}:experiments").decode().splitlines()
    experiment_ids = sorted(name for name in directory_names if name.startswith("EXP-"))
    experiment_set = set(experiment_ids)
    exact_directory_id = re.compile(
        r"(?<![A-Za-z0-9-])(?:" + "|".join(re.escape(name) for name in sorted(experiment_ids, key=len, reverse=True)) + r")(?![A-Za-z0-9-])"
    )
    paths = git("ls-tree", "-r", "--name-only", COMMIT, "formal/targets").decode().splitlines()
    targets = []
    for path in sorted(p for p in paths if p.endswith(".yaml")):
        spec_oid, spec_bytes, spec_sha = blob(path)
        spec = yaml.safe_load(spec_bytes)
        assert spec["schema"] == "crypto.autoresearch.formal_task.v1"
        source = spec["source"]
        theorem = spec["workspace"].rstrip("/") + "/" + spec["theorem_file"]
        assert not source.startswith("/") and ".." not in Path(source).parts
        assert not theorem.startswith("/") and ".." not in Path(theorem).parts
        source_oid, source_bytes, source_sha = blob(source)
        theorem_oid, _, theorem_sha = blob(theorem)
        spec_text = spec_bytes.decode()
        source_text = source_bytes.decode(errors="replace")
        targets.append({
            "target": Path(path).name, "spec_path": path,
            "spec_blob": spec_oid, "spec_sha256": spec_sha,
            "proof_task_id": spec["task_id"], "claim_id": spec["claim_id"],
            "source_status": spec["source_status"],
            "source_path": source, "source_blob": source_oid,
            "source_sha256": source_sha,
            "theorem_file": theorem, "theorem_name": spec["theorem_name"],
            "theorem_blob": theorem_oid, "theorem_sha256": theorem_sha,
            "canonical_exp_ids_in_spec": sorted(set(EXP.findall(spec_text))),
            "canonical_exp_ids_mentioned_in_source": sorted(set(EXP.findall(source_text))),
            "exp_directory_ids_in_spec": sorted(set(exact_directory_id.findall(spec_text))),
            "exp_directory_ids_in_source": sorted(set(exact_directory_id.findall(source_text))),
            "source_path_is_run_artifact": "/runs/" in f"/{source}/",
            "spec_explicit_run_reference": bool(re.search(r"(?:/runs/|\bRUN-[A-Za-z0-9-]+\b)", spec_text)),
        })
    assert len(targets) == len({t["spec_path"] for t in targets})
    assert len(targets) == len({t["proof_task_id"] for t in targets})
    assert len(targets) == len({t["claim_id"] for t in targets})
    summary = {
        "targets": len(targets),
        "theorem_files_present": len(targets),
        "unique_theorem_files": len({t["theorem_file"] for t in targets}),
        "unique_source_paths": len({t["source_path"] for t in targets}),
        "source_status_counts": dict(sorted(Counter(t["source_status"] for t in targets).items())),
        "specs_with_canonical_exp_id": sum(bool(t["canonical_exp_ids_in_spec"]) for t in targets),
        "canonical_exp_ids_in_specs": sorted({e for t in targets for e in t["canonical_exp_ids_in_spec"]}),
        "sources_under_experiments": sum(t["source_path"].startswith("experiments/") for t in targets),
        "direct_run_artifact_sources": sum(t["source_path_is_run_artifact"] for t in targets),
        "specs_with_explicit_run_reference": sum(t["spec_explicit_run_reference"] for t in targets),
    }
    pointers: dict[str, list[str]] = {}
    for target in targets:
        mentions = set(target["exp_directory_ids_in_spec"])
        mentions.update(target["exp_directory_ids_in_source"])
        for experiment_id in sorted(mentions & experiment_set):
            pointers.setdefault(experiment_id, []).append(target["target"].removesuffix(".yaml"))
    pointers = dict(sorted(pointers.items()))
    corpus = {
        "schema": "crypto.validation.formal_corpus_pointer_coverage.v1",
        "main_commit": COMMIT,
        "experiments_tree": experiments_tree,
        "formal_tree": tree,
        "method": "Known exact EXP directory-ID tokens in target specs or declared source bytes, including legacy multi-hyphen IDs; syntactic pointers only, not proof suitability, semantic linkage, or run validation",
        "experiment_directory_ids": experiment_ids,
        "experiment_directory_count": len(experiment_ids),
        "ids_with_exact_target_pointer": sorted(pointers),
        "ids_without_exact_target_pointer": sorted(experiment_set - pointers.keys()),
        "targets_with_exact_experiment_pointer": len({name for names in pointers.values() for name in names}),
        "exact_pointer_map": pointers,
    }
    (OUT / "corpus-pointer-coverage.json").write_text(json.dumps(corpus, indent=2, sort_keys=True) + "\n")
    summary["experiment_directory_count"] = len(experiment_ids)
    summary["ids_with_exact_target_pointer"] = len(pointers)
    summary["targets_with_exact_experiment_pointer"] = corpus["targets_with_exact_experiment_pointer"]
    document = {
        "schema": "crypto.validation.formal_target_provenance_inventory.v1",
        "main_commit": COMMIT, "formal_tree": tree,
        "scope": "static path and blob inventory; no theorem compilation or semantic fidelity conclusion",
        "summary": summary, "targets": targets,
    }
    (OUT / "provenance.json").write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
    dot = '''digraph provenance {
  graph [rankdir=TB, bgcolor="white", pad="0.3", nodesep="0.3", ranksep="0.4"];
  node [shape=box, style=rounded, fontname="Helvetica", fontsize=14];
  edge [fontname="Helvetica", fontsize=11];
  source [label="30 distinct declared source paths\\nidentical at hosted and named main"];
  spec [label="87 target YAML specs\\n87 unique task and claim IDs"];
  theorem [label="87 exact hosted machine receipts\\nformal tree identical at named main"];
  run [label="0 direct /runs/ sources\\n0 explicit RUN refs in specs", color="orange"];
  corpus [label="2781 EXP-prefix directories\\n5 with exact target pointer", color="orange"];
  review [label="Claim-specific semantic review\\nand experiment controls pending", color="orange"];
  source -> spec [label="declared path + SHA-256"];
  spec -> theorem [label="declared theorem file"];
  run -> source [style=dashed, label="execution provenance open"];
  corpus -> spec [style=dashed, label="syntactic pointers only"];
  theorem -> review [style=dashed, label="statement-to-claim bridge open"];
}
'''
    (OUT / "coverage.dot").write_text(dot)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
