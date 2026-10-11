#!/usr/bin/env python3
"""EJ1 attack: rebuild draft-contract.yaml into write_scope without touching producer OUT."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
DESIGN = ROOT / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-1907cf/design/TASK-20260929-ef0945"
WRITE = Path(__file__).resolve().parent
SCRATCH = WRITE / "scratch"
EXPECTED = "894c4855b64fdd2ec63915f88d6c668dcb95f40a108eba4f07a701b12bf6ccb6"
BUILDER_SRC = DESIGN / "build_fresh_only.py"
FRESH_SRC = DESIGN / "fresh-text.yaml"
DRAFT_SRC = DESIGN / "draft-contract.yaml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_builder_in(workdir: Path, fresh_bytes: bytes | None = None) -> Path:
    """Copy builder + fresh-text into workdir; patch OUT to local draft; run."""
    workdir.mkdir(parents=True, exist_ok=True)
    builder_dst = workdir / "build_fresh_only.py"
    fresh_dst = workdir / "fresh-text.yaml"
    out_dst = workdir / "draft-contract.yaml"
    shutil.copy2(BUILDER_SRC, builder_dst)
    if fresh_bytes is None:
        shutil.copy2(FRESH_SRC, fresh_dst)
    else:
        fresh_dst.write_bytes(fresh_bytes)
    # Patch ROOT/FRESH/OUT so producer files are untouched and nesting depth is irrelevant.
    text = builder_dst.read_text()
    text = text.replace(
        "ROOT = Path(__file__).resolve().parents[7]",
        f"ROOT = Path({str(ROOT)!r})",
    )
    text = text.replace(
        'FRESH = DESIGN / "fresh-text.yaml"',
        f'FRESH = Path({str(fresh_dst)!r})',
    )
    text = text.replace(
        'OUT = DESIGN / "draft-contract.yaml"',
        f'OUT = Path({str(out_dst)!r})',
    )
    builder_dst.write_text(text)
    # Execute as a script with cwd = repo root so held amendment paths resolve.
    import subprocess

    r = subprocess.run(
        [sys.executable, str(builder_dst)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"builder failed rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
    return out_dst


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    results = {
        "expected_digest": EXPECTED,
        "producer_draft_sha256": sha256(DRAFT_SRC),
        "producer_fresh_sha256": sha256(FRESH_SRC),
        "producer_builder_sha256": sha256(BUILDER_SRC),
        "rebuilds": [],
        "negative_control": {},
        "transclusion_leaf_map": {},
        "inputs_observed": {
            "fresh_text": str(FRESH_SRC.relative_to(ROOT)),
            "held_amendments_read_by_builder": [
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
            ],
            "note": "Held amendments are build-time restatement sources disclosed in builder and semantic_lineage; not hidden.",
        },
    }

    # Dual rebuild into write_scope
    for i in (1, 2):
        wd = SCRATCH / f"rebuild_{i}"
        if wd.exists():
            shutil.rmtree(wd)
        out = run_builder_in(wd)
        digest = sha256(out)
        results["rebuilds"].append(
            {
                "run": i,
                "path": str(out.relative_to(ROOT)),
                "sha256": digest,
                "matches_expected": digest == EXPECTED,
                "byte_identical_to_producer": out.read_bytes() == DRAFT_SRC.read_bytes(),
            }
        )

    # Negative control: flip one byte in a loaded YAML value (not a comment).
    # First occurrence of the id value under `id:` is normative; header comment
    # occurrences must not be used (yaml.safe_load drops comments).
    fresh = FRESH_SRC.read_bytes()
    marker = b"\n  id: EXP-AUXIN-92dccc"
    idx = fresh.find(marker)
    assert idx >= 0, "could not find normative id flip site"
    flip_at = idx + len(b"\n  id: ")  # first char of EXP-AUXIN-92dccc value
    flipped = bytearray(fresh)
    flipped[flip_at] = flipped[flip_at] ^ 0x01  # E -> D
    assert flipped[flip_at : flip_at + 15] != b"EXP-AUXIN-92dccc"
    nc_wd = SCRATCH / "rebuild_nc"
    if nc_wd.exists():
        shutil.rmtree(nc_wd)
    nc_out = run_builder_in(nc_wd, fresh_bytes=bytes(flipped))
    nc_digest = sha256(nc_out)
    results["negative_control"] = {
        "id": "NC-EJ1-flip-fresh-byte",
        "flip_offset": flip_at,
        "flip_site": "fresh.id value (not comment)",
        "rebuild_sha256": nc_digest,
        "differs_from_expected": nc_digest != EXPECTED,
        "detected": nc_digest != EXPECTED,
    }

    # Check transclusion / leaf_map emptiness on producer draft (and rebuild 1)
    import yaml

    draft = yaml.safe_load(DRAFT_SRC.read_text())
    sc = draft["successor_contract"]
    results["transclusion_leaf_map"] = {
        "transcluded_entries_len": len(sc.get("transcluded", {}).get("entries") or []),
        "leaf_map_rows_len": len(sc.get("leaf_map", {}).get("rows") or []),
        "additions_read_together_groups_len": len(
            sc.get("additions_read_together", {}).get("groups") or []
        ),
        "empty_by_construction": (
            len(sc.get("transcluded", {}).get("entries") or []) == 0
            and len(sc.get("leaf_map", {}).get("rows") or []) == 0
        ),
    }

    all_match = all(r["matches_expected"] for r in results["rebuilds"])
    results["verdict_inputs"] = {
        "dual_rebuild_match": all_match,
        "negative_control_detected": results["negative_control"]["detected"],
        "transclusion_empty": results["transclusion_leaf_map"]["empty_by_construction"],
        "producer_matches_expected": results["producer_draft_sha256"] == EXPECTED,
    }

    out_json = WRITE / "ej1_rebuild.result.json"
    import json

    out_json.write_text(json.dumps(results, indent=2, sort_keys=False) + "\n")
    print(json.dumps(results["verdict_inputs"], indent=2))
    print("wrote", out_json)


if __name__ == "__main__":
    main()
