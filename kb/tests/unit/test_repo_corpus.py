from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from crypto_kb.ingest.repo_corpus import RULES, iter_staged
from crypto_kb.ingest.schema_supersession import (
    SchemaSupersessionError,
    load_schema_supersessions,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _registry(repo: Path, records: list[dict[str, str]]) -> None:
    path = repo / "tools/schema_supersession_registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {"schema": "schema-supersession-registry-v1", "records": records},
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _rule(name: str):
    return next(rule for rule in RULES if rule.name == name)


def test_registered_replacement_is_staged_with_canonical_id_and_provenance(tmp_path: Path) -> None:
    source_rel = "ledger/evidence/EV-LEGACY.yaml"
    replacement_rel = (
        "ledger/corrections/schema-supersessions/20260811/"
        "ledger__evidence__EV-LEGACY.v2.yaml"
    )
    source = b"evidence: [legacy-invalid\n"
    replacement = b"evidence:\n  id: EV-TEST-abcdef\n  direction: neutral\n"
    _write(tmp_path / source_rel, source)
    _write(tmp_path / replacement_rel, replacement)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": source_rel,
            "superseded_sha256": _sha(source),
            "superseding_path": replacement_rel,
            "superseding_sha256": _sha(replacement),
            "defect": "legacy fixture",
            "registered": "2026-08-11",
            "replacement_id": "EV-TEST-abcdef",
        }],
    )

    documents = list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))

    assert len(documents) == 1
    assert documents[0].data == replacement
    assert documents[0].metadata["source_id"] == "evidence:EV-TEST-abcdef"
    assert documents[0].metadata["supersedes"] == ["EV-LEGACY"]
    assert documents[0].metadata["verification_artifacts"] == sorted([
        f"{source_rel}@sha256:{_sha(source)}",
        f"{replacement_rel}@sha256:{_sha(replacement)}",
    ])


@pytest.mark.parametrize("mutated", ["source", "replacement"])
def test_registered_hash_drift_fails_closed(tmp_path: Path, mutated: str) -> None:
    source_rel = "ledger/evidence/EV-OLD.yaml"
    replacement_rel = (
        "ledger/corrections/schema-supersessions/20260811/"
        "ledger__evidence__EV-OLD.v2.yaml"
    )
    source = b"evidence:\n  id: EV-OLD\n"
    replacement = b"evidence:\n  id: EV-NEW-abcdef\n"
    _write(tmp_path / source_rel, source)
    _write(tmp_path / replacement_rel, replacement)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": source_rel,
            "superseded_sha256": _sha(source),
            "superseding_path": replacement_rel,
            "superseding_sha256": _sha(replacement),
            "defect": "fixture",
            "registered": "2026-08-11",
            "replacement_id": "EV-NEW-abcdef",
        }],
    )
    target = tmp_path / (source_rel if mutated == "source" else replacement_rel)
    target.write_bytes(target.read_bytes() + b"# drift\n")

    with pytest.raises(SchemaSupersessionError, match="hash mismatch"):
        list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))


def test_registry_path_escape_fails_closed(tmp_path: Path) -> None:
    source_rel = "ledger/evidence/EV-OLD.yaml"
    source = b"evidence:\n  id: EV-OLD\n"
    _write(tmp_path / source_rel, source)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": source_rel,
            "superseded_sha256": _sha(source),
            "superseding_path": "../outside.yaml",
            "superseding_sha256": "0" * 64,
            "defect": "fixture",
            "registered": "2026-08-11",
        }],
    )

    with pytest.raises(SchemaSupersessionError, match="confined POSIX path"):
        load_schema_supersessions(tmp_path)


@pytest.mark.parametrize(
    ("kind", "replacement_rel", "redirect_id", "message"),
    [
        ("experiment", "ledger/corrections/schema-supersessions/x.v2.yaml", None,
         "does not match discovered source kind"),
        ("ledger", "experiments/EXP-NEW/specification.yaml", "EV-NEW-abcdef",
         "redirect target kind"),
        ("ledger", "ledger/evidence/EV-NEW-abcdef.yaml", None,
         "replacement must live below"),
    ],
)
def test_registry_kind_and_discovery_mismatches_fail_closed(
    tmp_path: Path,
    kind: str,
    replacement_rel: str,
    redirect_id: str | None,
    message: str,
) -> None:
    source_rel = "ledger/evidence/EV-OLD.yaml"
    source = b"evidence:\n  id: EV-OLD\n"
    replacement = b"evidence:\n  id: EV-NEW-abcdef\n"
    _write(tmp_path / source_rel, source)
    _write(tmp_path / replacement_rel, replacement)
    record = {
        "kind": kind,
        "superseded_path": source_rel,
        "superseded_sha256": _sha(source),
        "superseding_path": replacement_rel,
        "superseding_sha256": _sha(replacement),
        "defect": "fixture",
        "registered": "2026-08-11",
    }
    if redirect_id:
        record["redirect_id"] = redirect_id
    _registry(tmp_path, [record])

    with pytest.raises(SchemaSupersessionError, match=message):
        load_schema_supersessions(tmp_path)


def test_registered_replacement_id_mismatch_fails_closed(tmp_path: Path) -> None:
    source_rel = "ledger/evidence/EV-OLD.yaml"
    replacement_rel = (
        "ledger/corrections/schema-supersessions/20260811/"
        "ledger__evidence__EV-OLD.v2.yaml"
    )
    source = b"evidence:\n  id: EV-OLD\n"
    replacement = b"evidence:\n  id: EV-ACTUAL-abcdef\n"
    _write(tmp_path / source_rel, source)
    _write(tmp_path / replacement_rel, replacement)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": source_rel,
            "superseded_sha256": _sha(source),
            "superseding_path": replacement_rel,
            "superseding_sha256": _sha(replacement),
            "defect": "fixture",
            "registered": "2026-08-11",
            "replacement_id": "EV-EXPECTED-abcdef",
        }],
    )

    with pytest.raises(SchemaSupersessionError, match="declares identifier"):
        list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))


def test_registered_unparseable_replacement_fails_closed(tmp_path: Path) -> None:
    source_rel = "ledger/evidence/EV-OLD.yaml"
    replacement_rel = (
        "ledger/corrections/schema-supersessions/20260811/"
        "ledger__evidence__EV-OLD.v2.yaml"
    )
    source = b"evidence:\n  id: EV-OLD\n"
    replacement = b"evidence: [invalid\n"
    _write(tmp_path / source_rel, source)
    _write(tmp_path / replacement_rel, replacement)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": source_rel,
            "superseded_sha256": _sha(source),
            "superseding_path": replacement_rel,
            "superseding_sha256": _sha(replacement),
            "defect": "fixture",
            "registered": "2026-08-11",
            "replacement_id": "EV-NEW-abcdef",
        }],
    )

    with pytest.raises(SchemaSupersessionError, match="is not parseable"):
        list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))


def test_redirect_alias_is_not_staged_twice(tmp_path: Path) -> None:
    old_rel = "ledger/evidence/EV-OLD.yaml"
    new_rel = "ledger/evidence/EV-NEW-abcdef.yaml"
    old = b"evidence:\n  id: EV-OLD\n"
    new = b"evidence:\n  id: EV-NEW-abcdef\n"
    _write(tmp_path / old_rel, old)
    _write(tmp_path / new_rel, new)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": old_rel,
            "superseded_sha256": _sha(old),
            "superseding_path": new_rel,
            "superseding_sha256": _sha(new),
            "defect": "duplicate alias fixture",
            "registered": "2026-08-11",
            "redirect_id": "EV-NEW-abcdef",
        }],
    )

    documents = list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))

    assert [item.metadata["source_id"] for item in documents] == [
        "evidence:EV-NEW-abcdef"
    ]


def test_redirect_target_identifier_mismatch_fails_closed(tmp_path: Path) -> None:
    old_rel = "ledger/evidence/EV-OLD.yaml"
    new_rel = "ledger/evidence/EV-NEW-abcdef.yaml"
    old = b"evidence:\n  id: EV-OLD\n"
    new = b"evidence:\n  id: EV-DIFFERENT-abcdef\n"
    _write(tmp_path / old_rel, old)
    _write(tmp_path / new_rel, new)
    _registry(
        tmp_path,
        [{
            "kind": "ledger",
            "superseded_path": old_rel,
            "superseded_sha256": _sha(old),
            "superseding_path": new_rel,
            "superseding_sha256": _sha(new),
            "defect": "duplicate alias fixture",
            "registered": "2026-08-11",
            "redirect_id": "EV-NEW-abcdef",
        }],
    )

    with pytest.raises(SchemaSupersessionError, match="declares identifier"):
        list(iter_staged(tmp_path, (_rule("evidence"),), "deadbeef"))


def test_typed_decisions_are_staged_once(tmp_path: Path) -> None:
    _write(
        tmp_path / "ledger/decisions/DEC-20260811-abcdef.yaml",
        b"coordinator_decision:\n  id: DEC-20260811-abcdef\n  decision: continue\n",
    )

    documents = list(
        iter_staged(
            tmp_path,
            (_rule("decisions"), _rule("decisions-root")),
            "deadbeef",
        )
    )

    assert [item.metadata["source_id"] for item in documents] == [
        "decision:DEC-20260811-abcdef"
    ]


def test_repository_dreg_replacements_stage_exact_ids() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    include = {
        "experiments/EXP-DREG-001/specification.yaml",
        "ledger/evidence/EV-GOAL-DREG-001-B003.yaml",
        "ledger/decisions/DEC-GOAL-DREG-001-B003.yaml",
    }
    rules = (
        _rule("experiments"),
        _rule("evidence"),
        _rule("decisions"),
    )

    documents = list(iter_staged(repo_root, rules, "test-commit", include=include))

    assert {item.metadata["source_id"] for item in documents} == {
        "experiment:EXP-DREG-001",
        "evidence:EV-DREG-7597cb",
        "decision:DEC-20260811-e77b9d",
    }
