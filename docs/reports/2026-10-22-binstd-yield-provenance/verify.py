"""Check additive citation-source corrections for the two BINSTD yield reviews."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

if not __debug__:
    raise RuntimeError("BINSTD yield verifier requires Python assertions; omit -O")

SOURCES = (
    "EV-BINSTD-0db227",
    "EV-BINSTD-9ac9c5",
)
COUNTS = (7, 9)
PANELS = (
    ("ell89", "RUN-BINSTD-43abd4", (0.4, 1.0)),
    ("ell89r1", "RUN-BINSTD-a2a24c", (0.5, 1.0)),
)


def verify(repo: Path) -> dict:
    registry = yaml.safe_load((repo / "tools/schema_supersession_registry.yaml").read_bytes())
    receipts = []
    for record_id, count in zip(SOURCES, COUNTS):
        old_rel = Path(f"ledger/evidence/{record_id}.yaml")
        new_rel = Path(
            f"ledger/corrections/schema-supersessions/20261022/"
            f"ledger__evidence__{record_id}.v2.yaml"
        )
        old_bytes = (repo / old_rel).read_bytes()
        new_bytes = (repo / new_rel).read_bytes()
        old = yaml.safe_load(old_bytes)
        new = yaml.safe_load(new_bytes)
        citations = new["evidence"]["citations"]
        assert len(citations) == count
        assert all(
            c["provenance"] == "internal"
            and c.get("verified_by", "").startswith("Codex ledger audit, 2026-10-22:")
            for c in citations
        )
        for citation in citations:
            citation.pop("verified_by")
        assert new == old, f"{record_id}: fields besides verified_by changed"
        matches = [r for r in registry["records"] if r["superseded_path"] == str(old_rel)]
        assert len(matches) == 1
        entry = matches[0]
        assert entry["superseding_path"] == str(new_rel)
        assert entry["superseded_sha256"] == hashlib.sha256(old_bytes).hexdigest()
        assert entry["superseding_sha256"] == hashlib.sha256(new_bytes).hexdigest()
        receipts.append({
            "record": record_id,
            "citations_read": count,
            "source_sha256": entry["superseded_sha256"],
            "replacement_sha256": entry["superseding_sha256"],
            "all_other_fields_equal": True,
        })
    panels = []
    base = repo / "experiments/EXP-BINSTD-8bdf86"
    for tag, run_id, expected_ratios in PANELS:
        raw = json.loads((base / "runs" / run_id / "raw-result.json").read_text())["result"]
        assert raw["status"] == "completed_valid" and raw["certificate"]["kind"] == "none"
        matrix_path = base / f"stage1-{tag}/yield-matrix.json"
        matrix_bytes = matrix_path.read_bytes()
        assert hashlib.sha256(matrix_bytes).hexdigest() == raw["artifact_sha256"]["stage1/yield-matrix.json"]
        matrix = json.loads(matrix_bytes)
        assert matrix["band"] == 1.25 and matrix["ells"] == [8, 9]
        assert matrix["solver_pin"] == "exhaustive_fb_sum_m3_stdlib_gf2"
        assert len(matrix["cells"]) == 2
        for cell, expected, summary in zip(matrix["cells"], expected_ratios, raw["cells_summary"]):
            assert cell["target_count"] == 40 and cell["hits_open"] == 40
            assert cell["hits_tau"] <= 40 and cell["hits_open"] <= 40
            ratio = cell["hits_tau"] / cell["hits_open"]
            assert ratio == expected == cell["ratio_tau_over_open"] == summary["ratio"]
            assert cell["R_tau"] == cell["hits_tau"] / 40
            assert cell["R_open"] == cell["hits_open"] / 40
            assert not cell["meets_band"] and ratio < matrix["band"]
            assert cell["cell_label"] == summary["cell_label"] == "E-TAU-NOT-RICHER"
        panels.append({
            "tag": tag,
            "stage1_run": run_id,
            "matrix_sha256": hashlib.sha256(matrix_bytes).hexdigest(),
            "ratios": list(expected_ratios),
            "all_open_arms_at_ceiling": True,
        })
    return {"schema": "binstd-yield-citation-audit-v1", "records": receipts,
            "archived_arithmetic_check": panels}


if __name__ == "__main__":
    import sys
    print(json.dumps(verify(Path(sys.argv[1]).resolve()), indent=2, sort_keys=True))
