#!/usr/bin/env python3
"""Fidelity check of the manifest_v2.yaml records written by PR #2497
(DEC-20261023-5c9671) against the archived bytes they cite.

Sheriff case SHF-20261028-0f3f64, B7 ledger reader. Read-only over the repo;
writes one JSON file (argv[1]).

For each record:
  1. every sha256 the record cites (derived_from, source_sha256,
     raw_result_sha256, prior_manifest_sha256, specification_sha256_at_launch)
     is recomputed from the file it names (at HEAD, and for launch-time source
     hashes also at the recorded launch commit);
  2. the run's tools/run_supersession_registry.yaml entry is re-hashed;
  3. every leaf value is traced to the archived run files (all files in the
     run directory except manifest_v2.yaml itself) plus the experiment's
     specification.yaml. A value is 'sourced' when it equals a parsed scalar
     (or list) of one of those files, or occurs verbatim in their text.
     Annotation leaves (source/ruling/basis notes, the completion block, the
     supersedes block, interpretation) are listed separately: they are the
     completer's words, not transcribed values, and are judged by reading.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[6]
RECORDS = [
    "experiments/EXP-AES-14352a/runs/RUN-AES-0739d9/manifest_v2.yaml",
    "experiments/EXP-AES-14352a/runs/RUN-AES-a36d0b/manifest_v2.yaml",
    "experiments/EXP-ECDLP-15534c/runs/RUN-ECDLP-b927d1/manifest_v2.yaml",
    "experiments/EXP-ECDLP-2535ec/runs/RUN-ECDLP-d214b6/manifest_v2.yaml",
    "experiments/EXP-ECDLP-6dacdb/runs/RUN-ECDLP-393d10/manifest_v2.yaml",
    "experiments/EXP-ECDLP-6dacdb/runs/RUN-ECDLP-c770f6/manifest_v2.yaml",
    "experiments/EXP-ICPERF-9cd390/runs/RUN-ICPERF-caa0c1/manifest_v2.yaml",
]
ANNOTATION_KEYS = {"source", "note_source", "status_source", "identity_source",
                   "commit_source", "hypothesis_id_source", "query_counts_source",
                   "interpretation", "execution_source_custody", "kind_basis",
                   "recorded_at", "observations_are_in"}
ANNOTATION_SUFFIXES = ("_ruling", "_source", "_basis")
ANNOTATION_BLOCKS = ("run.schema_completion", "run.supersedes")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha(commit: str, rel: str) -> str | None:
    try:
        data = subprocess.check_output(["git", "-C", str(REPO), "show", f"{commit}:{rel}"],
                                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    return hashlib.sha256(data).hexdigest()


def leaves(obj, prefix):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}.{k}")
    elif isinstance(obj, list) and obj and all(not isinstance(x, (dict, list)) for x in obj):
        yield prefix, obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


def scalars(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            scalars(v, out)
    elif isinstance(obj, list):
        out.append(("list", json.dumps(obj, sort_keys=True)))
        for v in obj:
            scalars(v, out)
    else:
        out.append(("scalar", json.dumps(obj, sort_keys=True)))
    return out


def corpus_for(run_dir: Path, spec: Path):
    texts, parsed = {}, {}
    files = [p for p in sorted(run_dir.iterdir()) if p.is_file() and p.name != "manifest_v2.yaml"]
    if spec.is_file():
        files.append(spec)
    for p in files:
        if p.stat().st_size > 2_000_000:   # large raw outputs: hash-checked, not searched
            texts[p.name] = None
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        texts[str(p.relative_to(REPO))] = text
        try:
            doc = json.loads(text) if p.suffix == ".json" else yaml.safe_load(text)
        except Exception:  # noqa: BLE001 -- logs are text only
            doc = None
        if doc is not None:
            parsed[str(p.relative_to(REPO))] = {v for _, v in scalars(doc, [])}
    return texts, parsed


def is_annotation(path: str) -> bool:
    last = path.rsplit(".", 1)[-1].split("[")[0]
    return (last in ANNOTATION_KEYS or last.endswith(ANNOTATION_SUFFIXES)
            or path.startswith(ANNOTATION_BLOCKS) or ".interpretation" in path)


def trace(value, texts, parsed):
    key = json.dumps(value, sort_keys=True)
    hits = [name for name, vals in parsed.items() if key in vals]
    if hits:
        return hits
    needles = []
    if isinstance(value, str):
        needles = [value]
    elif isinstance(value, bool) or value is None:
        needles = []
    elif isinstance(value, (int, float)):
        needles = [repr(value), str(value)]
    elif isinstance(value, list):
        needles = [json.dumps(value), " ".join(map(str, value))]
    found = [name for name, text in texts.items()
             if text is not None and any(n and n in text for n in needles)]
    if not found and isinstance(value, list):
        # every element sourced, possibly from different places
        per = [trace(v, texts, parsed) for v in value]
        if all(per):
            return ["elements:" + ",".join(sorted({h for hs in per for h in hs}))]
    return found


def main():
    registry = yaml.safe_load((REPO / "tools/run_supersession_registry.yaml").read_text())
    entries = registry.get("records") or registry.get("supersessions") or registry
    report = []
    for rel in RECORDS:
        path = REPO / rel
        run_dir = path.parent
        doc = yaml.safe_load(path.read_text())
        run = doc["run"]
        spec = run_dir.parent.parent / "specification.yaml"
        rec = {"record": rel, "sha256": sha(path), "hash_checks": [], "registry": None,
               "unsourced_values": [], "sourced_values": 0, "annotations": []}
        # 1. hash checks
        derived = (run.get("schema_completion") or {}).get("derived_from") or {}
        for f, recorded in derived.items():
            rec["hash_checks"].append({"file": f, "recorded": recorded,
                                       "recomputed": sha(REPO / f) if (REPO / f).is_file() else None})
        code = run.get("code") or {}
        launch_commit = code.get("commit")
        for f, recorded in (code.get("source_sha256") or {}).items():
            rec["hash_checks"].append({
                "file": f, "recorded": recorded,
                "recomputed": sha(REPO / f) if (REPO / f).is_file() else None,
                "at_launch_commit": git_sha(launch_commit, f) if launch_commit else None})
        result = run.get("result") or {}
        if result.get("raw_result_sha256"):
            f = result["raw_result"]
            rec["hash_checks"].append({"file": f, "recorded": result["raw_result_sha256"],
                                       "recomputed": sha(REPO / f)})
        sup = run.get("supersedes") or {}
        if sup.get("prior_manifest_sha256"):
            f = sup["prior_manifest_path"]
            rec["hash_checks"].append({"file": f, "recorded": sup["prior_manifest_sha256"],
                                       "recomputed": sha(REPO / f)})
        inputs = run.get("inputs") or {}
        if inputs.get("specification_sha256_at_launch"):
            f = inputs["specification"]
            rec["hash_checks"].append({"file": f, "recorded": inputs["specification_sha256_at_launch"],
                                       "recomputed_head": sha(REPO / f),
                                       "at_launch_commit": git_sha(launch_commit, f)})
        for h in rec["hash_checks"]:
            vals = [h.get(k) for k in ("recomputed", "at_launch_commit", "recomputed_head") if h.get(k)]
            h["match"] = h["recorded"] in vals
        # 2. registry entry
        superseded = str(path.parent.relative_to(REPO) / "manifest.yaml")
        for e in entries if isinstance(entries, list) else []:
            if isinstance(e, dict) and e.get("superseded_path") == superseded:
                rec["registry"] = {
                    "superseding_path_ok": e.get("superseding_path") == rel,
                    "superseded_sha256_ok": e.get("superseded_sha256") == sha(REPO / superseded),
                    "superseding_sha256_ok": e.get("superseding_sha256") == rec["sha256"],
                    "decision_id": e.get("decision_id")}
        # 3. value trace
        texts, parsed = corpus_for(run_dir, spec)
        for p, v in leaves(run, "run"):
            if is_annotation(p):
                rec["annotations"].append(p)
                continue
            hits = trace(v, texts, parsed)
            if hits:
                rec["sourced_values"] += 1
            else:
                rec["unsourced_values"].append({"field": p, "value": v})
        report.append(rec)
    out = Path(sys.argv[1])
    out.write_text(json.dumps(report, indent=2, default=str) + "\n")
    for r in report:
        bad = [h["file"] for h in r["hash_checks"] if not h["match"]]
        print(f"{r['record']}: hashes {len(r['hash_checks']) - len(bad)}/{len(r['hash_checks'])} "
              f"match{' MISMATCH ' + str(bad) if bad else ''}; registry {r['registry']}; "
              f"values sourced {r['sourced_values']}, unsourced {len(r['unsourced_values'])}, "
              f"annotations {len(r['annotations'])}")
        for u in r["unsourced_values"]:
            print(f"    UNSOURCED {u['field']} = {str(u['value'])[:110]}")


if __name__ == "__main__":
    main()
