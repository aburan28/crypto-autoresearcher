from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

import pytest
import yaml

from crypto_kb.config import SOURCE_PREFIX
from crypto_kb.ingest.repo_corpus import (
    RULES,
    StagingDiagnostics,
    iter_staged,
    stage_repository,
)
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
    assert documents[0].metadata["supersedes"] == ["EV-OLD"]
    assert documents[0].metadata["verification_artifacts"] == sorted([
        f"{old_rel}@sha256:{_sha(old)}",
        f"{new_rel}@sha256:{_sha(new)}",
    ])


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

    by_id = {item.metadata["source_id"]: item for item in documents}
    assert set(by_id) == {
        "experiment:EXP-DREG-001",
        "evidence:EV-DREG-7597cb",
        "decision:DEC-20260811-e77b9d",
    }
    assert by_id["experiment:EXP-DREG-001"].metadata.get("supersedes", []) == []
    assert by_id["experiment:EXP-DREG-001"].metadata["verification_artifacts"] == [
        "experiments/EXP-DREG-001/specification.yaml@sha256:"
        "44fe37a126e5998054cb9788e1208b13d15ee87448c78737bddd1666e2cf5c8b",
        "ledger/corrections/schema-supersessions/20260811/"
        "experiments__EXP-DREG-001__specification.v2.yaml@sha256:"
        "fa056f97306ad46e21077c46794dfab371a85f695551b13c51acaa1e6de486b2",
    ]
    assert by_id["evidence:EV-DREG-7597cb"].metadata["supersedes"] == [
        "EV-GOAL-DREG-001-B003"
    ]
    assert by_id["decision:DEC-20260811-e77b9d"].metadata["supersedes"] == [
        "DEC-GOAL-DREG-001-B003"
    ]


def test_repository_full_dry_stage_has_complete_modern_coverage_and_disclosed_debt() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    diagnostics = StagingDiagnostics()

    class DrySink:
        def __init__(self) -> None:
            self.keys: list[str] = []

        def put(self, key: str, data: bytes, content_type: str | None = None) -> None:
            del data, content_type
            self.keys.append(key)

    sink = DrySink()
    documents = stage_repository(repo_root, sink, diagnostics=diagnostics)
    source_ids = [item.metadata["source_id"] for item in documents]
    source_keys = [item.source_key for item in documents]

    # Corpus size is not a property of the staging code. Every research batch
    # commits new ledger records, and `parents[3]` is a different corpus in
    # every concurrent worktree, so an exact document count fails on branches
    # that changed nothing about staging. It also decays quietly: the exact
    # pin here (10,922, from the independently reviewed BATCH-bac554 snapshot
    # plus its neutral PASS archive) was maintained while three sibling pins
    # went stale unnoticed at 76 / 75 / 103 against a live 80 / 79 / 105.
    #
    # What this test defends is the staging *schema*: every rule family still
    # reaches the corpus, ids and keys stay one-to-one with documents, and the
    # disclosed debt further down stays exactly as disclosed. The floors below
    # are ratchets, not measurements. Each sits roughly a tenth under the count
    # observed at commit b444f393d -- below the reviewed BATCH-bac554 snapshot,
    # so a branch forked before recent records landed still passes -- and moves
    # only when a reviewer deliberately raises it. They are sized to catch a
    # family collapsing, not to track a few percent of drift; the precision
    # lives in the exact debt sets and the supersession shape further down.
    assert len(documents) >= 10_500
    assert len(set(source_ids)) == len(documents)
    assert len(set(source_keys)) == len(documents)
    assert len(sink.keys) == 2 * len(documents)
    assert len(set(sink.keys)) == 2 * len(documents)
    assert {
        "evidence:EV-DREG-39e13d",
        "decision:DEC-20260812-a987b8",
    } <= set(source_ids)

    # No staging rule may silently match nothing, and growth in one family
    # must not hide a family that collapsed to zero. Destinations are read
    # back off RULES, so adding a rule without giving it a floor fails here
    # rather than staging an unwatched family.
    minimum_per_destination = {
        "papers/literature-notes": 7_500,
        "papers/vendored": 1,
        "internal-notes/techniques": 80,
        "internal-notes/findings": 55,
        "internal-notes/open-problems": 28,
        "ledgers/evidence": 370,
        "ledgers/hypotheses": 270,
        "ledgers/questions": 100,
        "ledgers/proposals": 680,
        "ledgers/goals": 64,
        "ledgers/goal-checkpoints": 95,
        "ledgers/subgoals": 1,
        "ledgers/decisions": 510,
        "experiments/specifications": 430,
        "experiments/analyses": 145,
        "repository-docs": 24,
    }
    assert set(minimum_per_destination) == {rule.destination for rule in RULES}
    staged_per_destination = Counter(
        key.removeprefix(SOURCE_PREFIX).rsplit("/", 1)[0] for key in source_keys
    )
    assert {
        destination: staged_per_destination[destination]
        for destination, floor in minimum_per_destination.items()
        if staged_per_destination[destination] < floor
    } == {}

    # Registered supersessions are immutable and write-once, so the registry
    # only ever grows; a shrink means a correction was dropped. The binding
    # that matters is not the registry's size but its shape: every registration
    # resolves to exactly one staged document, except a suppressed redirect,
    # whose lineage merges into a target carrying its own registration.
    assert len(diagnostics.registered_source_paths) >= 70
    assert diagnostics.matched_registered_source_paths == diagnostics.registered_source_paths
    assert diagnostics.unmatched_registered_source_paths == []
    assert sum(bool(item.metadata.get("verification_artifacts")) for item in documents) == (
        len(diagnostics.registered_source_paths) - len(diagnostics.redirect_suppressions)
    )

    # The debt stays exact where the counts became floors. Disclosed debt is
    # closed, never grown: a new unparseable record, a new colliding id, or a
    # new suppressed redirect is a regression, not corpus growth, so each of
    # these sets is pinned by membership and any addition fails the test.
    expected_unparseable = {
        "ledger/H-BKKMV-001.yaml",
        "ledger/H-DREG-001.yaml",
        "ledger/H-EQJ-001.yaml",
        "ledger/H-FB3-001.yaml",
        "ledger/H-ICI-001.yaml",
        "ledger/H-R6-001.yaml",
        "ledger/H-REP-001.yaml",
        "ledger/H-SIG-001.yaml",
        "ledger/RQ-DREG-001.yaml",
        "ledger/RQ-FB3-001.yaml",
        "ledger/RQ-ISO-001.yaml",
        "ledger/RQ-R6-001.yaml",
        "ledger/RQ-SIG-001.yaml",
        "ledger/RQ-TTN-001.yaml",
        "experiments/EXP-DREG-002/specification.yaml",
        "experiments/EXP-EQJ-001/specification.yaml",
        "experiments/EXP-FB-001/specification.yaml",
        "experiments/EXP-FB3-001/specification.yaml",
        "experiments/EXP-ICI-001/specification.yaml",
        "experiments/EXP-REP-001/specification.yaml",
        "experiments/EXP-REP-002/specification.yaml",
        "experiments/EXP-SIG-001/specification.yaml",
        "experiments/EXP-SIG-004/specification.yaml",
        "experiments/EXP-SIG-005/specification.yaml",
    }
    assert {item.path for item in diagnostics.unparseable_sources} == expected_unparseable

    # Two registries disclose this debt from different angles, and they must
    # not drift apart. `tools/merge_hygiene_baseline.txt` grandfathers every
    # file that fails to parse on disk anywhere in the repository; the set
    # above holds only what a staging rule matched and no registered
    # supersession routes around. So it is a subset and never an equal --
    # `experiments/EXP-DREG-001/specification.yaml` sits in the baseline but
    # not here, because staging reads its registered replacement instead.
    #
    # Containment is what makes the two lists one policy. A newly broken
    # record silenced by editing only this test would pass every check but
    # this one, and it cannot be legalised from the other side either: the
    # baseline's own header says lines may only ever be REMOVED.
    baseline_path = repo_root / "tools" / "merge_hygiene_baseline.txt"
    hygiene_baseline = {
        line.strip()
        for line in baseline_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    assert expected_unparseable - hygiene_baseline == set()

    assert {item.source_id for item in diagnostics.duplicate_source_ids} == {
        f"decision:DEC-20260722-{number:03d}" for number in range(1, 6)
    }
    assert all(
        item.kept_path.startswith("ledger/decisions/")
        and item.skipped_path.startswith("ledger/DEC-")
        and not item.identical_bytes
        for item in diagnostics.duplicate_source_ids
    )
    assert [item.source_path for item in diagnostics.redirect_suppressions] == [
        "ledger/hypotheses/H-XOR-YIELD.yaml"
    ]

    # Count is already floored above as `ledgers/goal-checkpoints`; what these
    # pin is the shard addressing scheme -- goal directory plus filename, so a
    # batch that closes under a dated suffix keeps its own immutable address.
    checkpoint_ids = {item for item in source_ids if item.startswith("goal-checkpoint:")}
    assert "goal-checkpoint:GOAL-ECDLP-001:BATCH-ef31ab" in checkpoint_ids
    assert (
        "goal-checkpoint:GOAL-ECDLP-001:BATCH-ef31ab-close-20260808"
        in checkpoint_ids
    )

    xor_documents = [
        item for item in documents if item.metadata["source_id"] == "hypothesis:H-XOR-d1a480"
    ]
    assert len(xor_documents) == 1
    assert _sha(xor_documents[0].data) == (
        "b9876d58c71699b5332039d8a7dc618c007a65907649e433f03e871d2e4519a8"
    )
    assert xor_documents[0].metadata["supersedes"] == ["H-XOR-YIELD"]
    assert xor_documents[0].metadata["verification_artifacts"] == [
        "ledger/corrections/schema-supersessions/20260808/"
        "ledger__hypotheses__H-XOR-d1a480.v2.yaml@sha256:"
        "b9876d58c71699b5332039d8a7dc618c007a65907649e433f03e871d2e4519a8",
        "ledger/hypotheses/H-XOR-YIELD.yaml@sha256:"
        "541bda542e20b161d3bdd606cd88c18ee65cb857f8fcd5ae6d39d459962b0ac7",
        "ledger/hypotheses/H-XOR-d1a480.yaml@sha256:"
        "655c01aa05986f760b2a348ba5e3cfdb1103cdb1af4eb27f97610db9217cd1f8",
    ]
