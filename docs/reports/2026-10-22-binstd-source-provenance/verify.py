"""Check the BINSTD evidence supersession without changing its frozen source."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml


def verify(repo: Path) -> dict:
    old_rel = Path("ledger/evidence/EV-BINSTD-030b4e.yaml")
    new_rel = Path("ledger/corrections/schema-supersessions/20261022/ledger__evidence__EV-BINSTD-030b4e.v2.yaml")
    old_bytes = (repo / old_rel).read_bytes()
    new_bytes = (repo / new_rel).read_bytes()
    old = yaml.safe_load(old_bytes)
    new = yaml.safe_load(new_bytes)
    citations = new["evidence"]["citations"]
    assert len(citations) == 5
    assert all(c["provenance"] == "internal" and c.get("verified_by") for c in citations)
    assert citations[-1]["ref"] == "AGENTS.md core rule 5"
    for citation in citations:
        citation.pop("verified_by")
    new["evidence"]["infrastructure_run_note"] = new["evidence"]["infrastructure_run_note"].replace(
        "AGENTS.md core rule 5", "AGENTS.md rule 3")
    new["evidence"]["boundaries"] = [
        item.replace("AGENTS.md core rule 5", "AGENTS.md rule 3")
        for item in new["evidence"]["boundaries"]
    ]
    citations[-1]["ref"] = "AGENTS.md rule 3"
    assert new == old, "the replacement changes fields beyond source readings and rule attribution"
    registry = yaml.safe_load((repo / "tools/schema_supersession_registry.yaml").read_bytes())
    matches = [r for r in registry["records"] if r["superseded_path"] == str(old_rel)]
    assert len(matches) == 1
    entry = matches[0]
    assert entry["superseding_path"] == str(new_rel)
    assert entry["superseded_sha256"] == hashlib.sha256(old_bytes).hexdigest()
    assert entry["superseding_sha256"] == hashlib.sha256(new_bytes).hexdigest()
    return {
        "schema": "binstd-source-provenance-audit-v1",
        "source_sha256": entry["superseded_sha256"],
        "replacement_sha256": entry["superseding_sha256"],
        "citations_read": 5,
        "substantive_differences": ["corrected AGENTS core rule reference from 3 to 5"],
        "other_fields_equal": True,
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(verify(Path(sys.argv[1]).resolve()), indent=2, sort_keys=True))
