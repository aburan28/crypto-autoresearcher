#!/usr/bin/env python3
"""EJ1 attack: rebuild draft-contract.yaml into write_scope without touching producer OUT."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
DESIGN = (
    ROOT
    / "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/design/TASK-20260929-d519f6"
)
WRITE = Path(__file__).resolve().parent
SCRATCH = WRITE / "scratch"
EXPECTED = "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc"
BUILDER_SRC = DESIGN / "build_successor.py"
FRESH_SRC = DESIGN / "fresh-text.yaml"
DRAFT_SRC = DESIGN / "draft-contract.yaml"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_builder_in(workdir: Path, fresh_bytes: bytes | None = None) -> Path:
    """Copy builder + fresh-text into workdir; patch OUT to local draft; run."""
    workdir.mkdir(parents=True, exist_ok=True)
    builder_dst = workdir / "build_successor.py"
    fresh_dst = workdir / "fresh-text.yaml"
    out_dst = workdir / "draft-contract.yaml"
    shutil.copy2(BUILDER_SRC, builder_dst)
    if fresh_bytes is None:
        shutil.copy2(FRESH_SRC, fresh_dst)
    else:
        fresh_dst.write_bytes(fresh_bytes)
    text = builder_dst.read_text()
    text = text.replace(
        "ROOT = Path(__file__).resolve().parents[7]",
        f"ROOT = Path({str(ROOT)!r})",
    )
    text = text.replace(
        'FRESH = DESIGN / "fresh-text.yaml"',
        f"FRESH = Path({str(fresh_dst)!r})",
    )
    text = text.replace(
        'OUT = DESIGN / "draft-contract.yaml"',
        f"OUT = Path({str(out_dst)!r})",
    )
    builder_dst.write_text(text)
    r = subprocess.run(
        [sys.executable, str(builder_dst)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"builder failed rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
        )
    return out_dst


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    results = {
        "joint": "EJ1",
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
            "note": (
                "Held amendments are build-time restatement sources disclosed in "
                "builder and semantic_lineage; not hidden."
            ),
        },
    }

    for i in (1, 2):
        wd = SCRATCH / f"rebuild_{i}"
        if wd.exists():
            shutil.rmtree(wd)
        out = run_builder_in(wd)
        digest = sha256(out)
        results["rebuilds"].append(
            {
                "run": i,
                "out": str(out.relative_to(ROOT)),
                "sha256": digest,
                "matches_expected": digest == EXPECTED,
                "byte_equal_producer": out.read_bytes() == DRAFT_SRC.read_bytes(),
            }
        )

    # Negative control: flip one normative byte of fresh text (not a YAML comment).
    # Prefer a non-id field so the builder's EXP_ID stop does not mask the
    # digest-diff check; also record an id-flip STOP as a second NC.
    import yaml

    fresh = yaml.safe_load(FRESH_SRC.read_text())
    auth = fresh["fresh"]["authorization"]
    assert isinstance(auth, str) and len(auth) > 8
    auth_b = list(auth.encode())
    auth_b[4] ^= 0x01
    fresh["fresh"]["authorization"] = bytes(auth_b).decode("latin-1")
    nc_bytes = yaml.safe_dump(fresh, sort_keys=False, allow_unicode=True).encode()
    wd_nc = SCRATCH / "rebuild_nc"
    if wd_nc.exists():
        shutil.rmtree(wd_nc)
    try:
        out_nc = run_builder_in(wd_nc, fresh_bytes=nc_bytes)
        nc_digest = sha256(out_nc)
        nc_primary = {
            "id": "NC-EJ1-flip-fresh-authorization-byte",
            "edit": "XOR one byte of loaded fresh.authorization (not a YAML comment)",
            "rebuild_sha256": nc_digest,
            "builder_rc": 0,
            "differs_from_expected": nc_digest != EXPECTED,
            "detected": nc_digest != EXPECTED,
        }
    except RuntimeError as e:
        nc_primary = {
            "id": "NC-EJ1-flip-fresh-authorization-byte",
            "edit": "XOR one byte of loaded fresh.authorization (not a YAML comment)",
            "builder_rc": 1,
            "error_prefix": str(e)[:240],
            "differs_from_expected": True,
            "detected": True,
        }

    # Secondary: flip fresh.id; builder stop on EXP_ID mismatch is also detection.
    fresh2 = yaml.safe_load(FRESH_SRC.read_text())
    oid = fresh2["fresh"]["id"]
    fb = list(oid.encode())
    fb[0] ^= 0x01
    fresh2["fresh"]["id"] = bytes(fb).decode("latin-1")
    nc2_bytes = yaml.safe_dump(fresh2, sort_keys=False, allow_unicode=True).encode()
    wd_nc2 = SCRATCH / "rebuild_nc_id"
    if wd_nc2.exists():
        shutil.rmtree(wd_nc2)
    try:
        out_nc2 = run_builder_in(wd_nc2, fresh_bytes=nc2_bytes)
        nc2 = {
            "id": "NC-EJ1-flip-fresh-id-byte",
            "edit": "XOR one byte of loaded fresh.id",
            "rebuild_sha256": sha256(out_nc2),
            "builder_rc": 0,
            "differs_from_expected": sha256(out_nc2) != EXPECTED,
            "detected": sha256(out_nc2) != EXPECTED,
        }
    except RuntimeError as e:
        nc2 = {
            "id": "NC-EJ1-flip-fresh-id-byte",
            "edit": "XOR one byte of loaded fresh.id",
            "builder_rc": 1,
            "error_prefix": str(e)[:240],
            "differs_from_expected": True,
            "detected": True,
            "note": "Builder STOP on EXP_ID mismatch; rebuild did not reproduce digest.",
        }

    results["negative_control"] = nc_primary
    results["negative_control_id_flip"] = nc2

    # Transclusion / leaf_map emptiness on producer draft.
    draft = yaml.safe_load(DRAFT_SRC.read_text())
    sc = draft["successor_contract"]
    te = (sc.get("transcluded") or {}).get("entries")
    lm = (sc.get("leaf_map") or {}).get("rows")
    art = (sc.get("additions_read_together") or {}).get("groups")
    results["transclusion_leaf_map"] = {
        "transcluded.entries": te,
        "transcluded.entries_empty": te == [] or te is None,
        "leaf_map.rows": lm,
        "leaf_map.rows_empty": lm == [] or lm is None,
        "additions_read_together.groups": art,
        "additions_read_together.groups_empty": art == [] or art is None,
    }

    results["verdict_candidate"] = (
        all(r["matches_expected"] and r["byte_equal_producer"] for r in results["rebuilds"])
        and results["negative_control"]["detected"]
        and results["negative_control_id_flip"]["detected"]
        and results["transclusion_leaf_map"]["transcluded.entries_empty"]
        and results["transclusion_leaf_map"]["leaf_map.rows_empty"]
    )

    out_json = WRITE / "ej1_rebuild.result.json"
    out_json.write_text(json.dumps(results, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"wrote": str(out_json), "verdict_candidate": results["verdict_candidate"]}, indent=2))


if __name__ == "__main__":
    main()
