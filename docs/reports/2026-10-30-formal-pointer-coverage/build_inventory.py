#!/usr/bin/env python3
"""Count literal EXP-ID pointers in registered formal targets at one Git commit.

This is navigation metadata. It does not inspect theorem meaning or validate runs.
Run from any checkout with: python3 build_inventory.py REPO COMMIT > inventory.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import yaml


def git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), *args])


def blob(repo: Path, commit: str, path: str) -> bytes | None:
    try:
        return subprocess.check_output(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def main(repo: Path, revision: str) -> dict:
    commit = git(repo, "rev-parse", f"{revision}^{{commit}}").decode().strip()
    paths = git(repo, "ls-tree", "-r", "--name-only", commit, "--", "experiments").decode().splitlines()
    experiments = sorted({p.split("/")[1] for p in paths if p.startswith("experiments/EXP-") and len(p.split("/")) > 2})
    experiment_set = set(experiments)
    targets = [p for p in git(repo, "ls-tree", "-r", "--name-only", commit, "--", "formal/targets").decode().splitlines() if p.endswith((".yaml", ".yml"))]
    # Match the actual directory names, including legacy IDs such as EXP-NCP-001.
    pattern = re.compile(r"(?<![A-Za-z0-9_-])(" + "|".join(
        re.escape(name) for name in sorted(experiments, key=len, reverse=True)) +
        r")(?![A-Za-z0-9_-])")
    witnesses: list[dict] = []
    missing_sources: list[dict] = []
    parse_errors: list[dict] = []
    for target in targets:
        raw = blob(repo, commit, target)
        if raw is None:
            parse_errors.append({"target": target, "error": "target blob missing"})
            continue
        try:
            spec = yaml.safe_load(raw)
            if not isinstance(spec, dict):
                raise ValueError("target YAML is not a mapping")
        except (yaml.YAMLError, ValueError) as exc:
            parse_errors.append({"target": target, "error": str(exc)})
            continue
        refs = [("target_spec", target, raw)]
        for kind, path in (("declared_source", spec.get("source")), ("theorem_source", spec.get("theorem_file"))):
            if not isinstance(path, str) or not path:
                missing_sources.append({"target": target, "kind": kind, "path": path})
                continue
            if kind == "theorem_source":
                workspace = spec.get("workspace")
                if not isinstance(workspace, str) or not workspace.startswith("formal"):
                    missing_sources.append({"target": target, "kind": kind,
                                            "path": path, "reason": "missing formal workspace"})
                    continue
                path = workspace.rstrip("/") + "/" + path.lstrip("/")
            data = blob(repo, commit, path)
            if data is None:
                missing_sources.append({"target": target, "kind": kind, "path": path})
                continue
            refs.append((kind, path, data))
        for kind, path, data in refs:
            for exp_id in sorted(set(pattern.findall(data.decode("utf-8", "replace"))) & experiment_set):
                witnesses.append({"experiment_id": exp_id, "target": target, "kind": kind,
                                  "path": path, "source_sha256": hashlib.sha256(data).hexdigest()})
    linked_ids = sorted({w["experiment_id"] for w in witnesses})
    linked_targets = sorted({w["target"] for w in witnesses})
    return {"schema": "crypto.validation.formal_pointer_inventory/v1", "source_commit": commit,
            "method": "Exact EXP-ID tokens in registered target YAML, its declared source, and theorem source; Git blobs at one commit.",
            "experiment_directories": len(experiments), "formal_targets": len(targets),
            "targets_with_exact_pointer": len(linked_targets), "experiment_ids_with_exact_pointer": len(linked_ids),
            "experiment_ids_without_exact_pointer": len(experiments) - len(linked_ids),
            "experiments_tree": git(repo, "rev-parse", f"{commit}:experiments").decode().strip(),
            "formal_targets_tree": git(repo, "rev-parse", f"{commit}:formal/targets").decode().strip(),
            "experiment_paths_sha256": hashlib.sha256(("\n".join(paths) + "\n").encode()).hexdigest(),
            "linked_experiment_ids": linked_ids, "linked_targets": linked_targets, "witnesses": witnesses,
            "missing_sources": missing_sources, "parse_errors": parse_errors,
            "limitation": "Syntactic navigation only. No theorem, historical run, empirical result, claim fidelity, or absence of a relevant theorem is certified."}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: build_inventory.py REPO COMMIT")
    print(json.dumps(main(Path(sys.argv[1]).resolve(), sys.argv[2]), indent=2, sort_keys=True))
