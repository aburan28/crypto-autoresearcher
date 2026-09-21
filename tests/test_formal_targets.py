"""Frozen formal task specs, and the dispatch stanzas generated from them.

The point of the stanza generator is that formal work needs no new role and no
dispatcher change.  That claim is only worth making if the generated stanza
actually satisfies the dispatcher, so these tests run the dispatcher's own
validators over it rather than eyeballing the JSON.
"""
from pathlib import Path
import importlib.util
import sys

import pytest

from orchestration.formal.targets import (
    SCHEMA_FORMAL_TASK_V1,
    TargetError,
    dispatch_stanza,
    load_spec,
    task_from_spec,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGETS = sorted((REPO_ROOT / "formal" / "targets").glob("*.yaml"))
ARTIFACT_DIR = "coordination/goals/GOAL-NCP-001/batches/BATCH-fa11ed/tasks"


def dispatcher():
    """Import tools/research_dispatch.py, which is a script, not a module."""

    spec = importlib.util.spec_from_file_location(
        "research_dispatch", REPO_ROOT / "tools" / "research_dispatch.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("research_dispatch", module)
    spec.loader.exec_module(module)
    return module


def test_there_are_targets_to_run() -> None:
    assert TARGETS, "formal/targets/ has no specs"


@pytest.mark.parametrize("path", TARGETS, ids=lambda p: p.stem)
def test_every_committed_target_builds_a_bounded_task(path: Path) -> None:
    spec = load_spec(path)
    task = task_from_spec(spec)

    assert task.claim.strip()
    assert task.theorem_file.endswith(".lean")
    # A claim has to be traceable to something somebody actually asserted.
    source = REPO_ROOT / spec["source"]
    assert source.is_file(), f"{path.name} cites a source that does not exist: {spec['source']}"


@pytest.mark.parametrize("path", TARGETS, ids=lambda p: p.stem)
def test_generated_stanza_passes_the_dispatchers_own_task_validation(path: Path) -> None:
    """Everything the dispatcher checks per task, checked here per target.

    Batch-level structure -- every producer assigned to an archive task -- is
    deliberately NOT asserted: an archive stanza carries real commit SHAs and
    path hashes, which only exist once the Coordinator actually archives.
    """

    dispatch = dispatcher()
    stanza = dispatch_stanza(load_spec(path), spec_path=str(path.relative_to(REPO_ROOT)), artifact_dir=ARTIFACT_DIR)
    location = "tasks[0]"

    assert stanza["role"] in dispatch.ROLES
    assert stanza["state"] in dispatch.STATES
    assert isinstance(stanza["review_required"], bool)
    assert 0 <= stanza["priority"] <= 100

    for field in ("read_scope", "write_scope"):
        for entry in stanza[field]:
            dispatch.validate_scope(entry, f"{location}.{field}")
    for entry in stanza["artifact_paths"]:
        dispatch.validate_artifact_path(entry, f"{location}.artifact_paths")
    assert dispatch.paths_within_scopes(stanza["artifact_paths"], stanza["write_scope"])

    dispatch.validate_handoff(stanza, location)


@pytest.mark.parametrize("path", TARGETS, ids=lambda p: p.stem)
def test_stanza_keeps_the_lane_advisory(path: Path) -> None:
    """A formal task must not acquire authority the formal lane does not have."""

    stanza = dispatch_stanza(load_spec(path), spec_path=str(path.relative_to(REPO_ROOT)), artifact_dir=ARTIFACT_DIR)

    # Not the coordinator: only the coordinator may change official state, and
    # a formalization is an executor running a frozen command.
    assert stanza["role"] == "executor"
    assert stanza["review_required"] is True
    assert "archive" not in stanza
    # Nothing outside its own task directory is writable.
    assert stanza["write_scope"] == [f"{ARTIFACT_DIR}/{stanza['id']}"]

    constraints = " ".join(stanza["handoff"]["constraints"]).lower()
    assert "untrusted" in constraints
    assert "never negative evidence" in constraints
    assert "semantic-fidelity review" in constraints


def test_a_spec_with_the_wrong_schema_is_refused(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema: something.else.v1\ntask_id: TASK-1\n")

    with pytest.raises(TargetError, match=SCHEMA_FORMAL_TASK_V1):
        load_spec(bad)


def test_a_spec_missing_its_source_is_refused(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        f"schema: {SCHEMA_FORMAL_TASK_V1}\n"
        "task_id: TASK-1\nclaim_id: C-1\nkind: formalize_claim\n"
        "claim: something\ntheorem_name: foo\ntheorem_file: Foo.lean\n"
    )

    with pytest.raises(TargetError, match="source"):
        load_spec(bad)


def test_an_absolute_spec_path_is_refused(tmp_path: Path) -> None:
    """A stanza carrying a machine-local path means something else elsewhere."""

    spec = load_spec(TARGETS[0])

    with pytest.raises(TargetError, match="repository-relative"):
        dispatch_stanza(spec, spec_path=str(TARGETS[0]), artifact_dir=ARTIFACT_DIR)
