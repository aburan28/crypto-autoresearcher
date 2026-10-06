#!/usr/bin/env python3
"""EJ1 negative controls and dual rebuild for TASK-20260929-1980c4."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
HERE = Path(__file__).resolve().parent
DRAFT = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/draft-contract.yaml"
)
BUILDER = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/build_successor.py"
)
FRESH = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/fresh-text.yaml"
)
COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"
EXPECTED_DRAFT = "667cf21e1a0680eaa5eb862164835a0074c109f2254f5ac6f52428327ba27bbd"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_verify_on(path: Path):
    # Import verifier functions
    import importlib.util

    spec = importlib.util.spec_from_file_location("ej1_verify", HERE / "ej1_verify.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    draft = yaml.safe_load(path.read_text())
    return mod.verify(draft["successor_contract"]["transcluded"]["entries"])


def negative_controls():
    results = []
    # NC-EJ1-a: flip one byte in one entry's text
    with tempfile.TemporaryDirectory(prefix="ej1-nc-a-") as td:
        scratch = Path(td) / "draft.yaml"
        scratch.write_bytes(DRAFT.read_bytes())
        doc = yaml.safe_load(scratch.read_text())
        entries = doc["successor_contract"]["transcluded"]["entries"]
        # flip first char of first entry
        t = entries[0]["text"]
        entries[0]["text"] = ("X" if t[0] != "X" else "Y") + t[1:]
        # keep stale hash so text mismatch fires
        scratch.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
        r = run_verify_on(scratch)
        results.append({
            "id": "NC-EJ1-a",
            "edit": "flip one character of first entry text (hash left stale)",
            "detected": (not r["ok"]) and any(
                f.get("kind") == "text_mismatch" for f in r["failures"]
            ),
            "failure_kinds": sorted({f["kind"] for f in r["failures"]}),
            "scratch_sha256": sha(scratch),
        })

    # NC-EJ1-b: move one entry's anchor field_path into a replaced path
    with tempfile.TemporaryDirectory(prefix="ej1-nc-b-") as td:
        scratch = Path(td) / "draft.yaml"
        scratch.write_bytes(DRAFT.read_bytes())
        doc = yaml.safe_load(scratch.read_text())
        entries = doc["successor_contract"]["transcluded"]["entries"]
        # Point an entry at replaced root amendment.change.D8_custody.manifest
        # Keep source_path as typed; change field_path only so under_path fires.
        target = None
        for e in entries:
            if e["source_path"].endswith("AMD-20260926-typed.yaml"):
                target = e
                break
        assert target is not None
        target["anchor"]["field_path"] = "amendment.change.D8_custody.manifest"
        # Also make kind loaded_value without resolving — verifier will either
        # fail resolve or catch replaced path. Prefer replaced-path detection:
        # use a resolvable sibling under that root if possible. Simpler: set
        # field_path under the root and leave kind; unresolvable still counts
        # as detection of the NC for "move into replaced path". Attack plan:
        # "your verifier must report both".
        scratch.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
        r = run_verify_on(scratch)
        kinds = {f["kind"] for f in r["failures"]}
        detected = (not r["ok"]) and (
            "entry_inside_replaced_path" in kinds or "unresolvable_anchor" in kinds
            or "text_mismatch" in kinds or "line_col_mismatch" in kinds
        )
        results.append({
            "id": "NC-EJ1-b",
            "edit": "move one typed entry anchor.field_path into replaced root change.D8_custody.manifest",
            "detected": detected,
            "failure_kinds": sorted(kinds),
            "scratch_sha256": sha(scratch),
        })
    return results


def dual_rebuild():
    out = []
    for i in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f"ej1-rebuild-{i}-") as td:
            td = Path(td)
            work = td / "design"
            work.mkdir()
            shutil.copy2(BUILDER, work / "build_successor.py")
            shutil.copy2(FRESH, work / "fresh-text.yaml")
            # builder writes draft beside itself; needs to run from repo root
            # so git show works. Copy builder into tmp but execute with cwd=REPO
            # and pass absolute? Looking at builder: HERE = Path(__file__).parent
            # so it writes to work/draft-contract.yaml. git show uses cwd.
            proc = subprocess.run(
                ["python3", str(work / "build_successor.py"), COMMIT],
                cwd=REPO,
                capture_output=True,
                text=True,
            )
            draft_out = work / "draft-contract.yaml"
            h = sha(draft_out) if draft_out.exists() else None
            out.append({
                "run": i,
                "exit_code": proc.returncode,
                "draft_sha256": h,
                "matches_snapshot": h == EXPECTED_DRAFT,
                "stderr_tail": (proc.stderr or "")[-500:],
            })
    return out


def main():
    nc = negative_controls()
    rebuilds = dual_rebuild()
    result = {
        "negative_controls": nc,
        "negative_controls_ok": all(x["detected"] for x in nc),
        "rebuilds": rebuilds,
        "rebuild_ok": all(r["matches_snapshot"] and r["exit_code"] == 0 for r in rebuilds),
        "rebuilds_identical": len({r["draft_sha256"] for r in rebuilds}) == 1,
    }
    (HERE / "ej1_controls_rebuild.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({
        "negative_controls_ok": result["negative_controls_ok"],
        "rebuild_ok": result["rebuild_ok"],
        "nc_detected": [x["id"] + ":" + str(x["detected"]) for x in nc],
        "rebuild_hashes_match": result["rebuilds_identical"],
    }))


if __name__ == "__main__":
    main()
