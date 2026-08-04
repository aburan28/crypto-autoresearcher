from __future__ import annotations

from pathlib import Path

import pytest

from tools import research_dispatch as dispatch


def assert_nonaut(error: pytest.ExceptionInfo[dispatch.DispatchError]) -> None:
    assert dispatch.NONAUTHORITATIVE_ERROR in str(error.value)


def test_both_variant_roots_reject_before_document_parsing(tmp_path):
    for variant in dispatch.RECONCILIATION_VARIANT_ROOTS:
        path = tmp_path.joinpath(*Path(variant).parts, "batch", "dispatch_queue.json")
        path.parent.mkdir(parents=True)
        path.write_text("not json")
        with pytest.raises(dispatch.DispatchError) as error:
            dispatch.enforce_reconciliation_queue_authority(path, tmp_path)
        assert_nonaut(error)


def test_all_five_inherited_queue_paths_reject(tmp_path):
    for relative in dispatch.RECONCILIATION_PROTECTED_QUEUES:
        path = tmp_path.joinpath(*Path(relative).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
        with pytest.raises(dispatch.DispatchError) as error:
            dispatch.enforce_reconciliation_queue_authority(path, tmp_path)
        assert_nonaut(error)


def test_symlink_alias_into_variant_rejects(tmp_path):
    target = tmp_path.joinpath(
        *Path(dispatch.RECONCILIATION_VARIANT_ROOTS[0]).parts,
        "dispatch_queue.json",
    )
    target.parent.mkdir(parents=True)
    target.write_text("{}")
    alias = tmp_path / "alias.json"
    alias.symlink_to(target)
    with pytest.raises(dispatch.DispatchError) as error:
        dispatch.enforce_reconciliation_queue_authority(alias, tmp_path)
    assert_nonaut(error)


def test_history_schema_and_nonaut_envelope_reject():
    with pytest.raises(dispatch.DispatchError) as error:
        dispatch.enforce_reconciliation_document_authority(
            {"schema": "crypto.autoresearch.reconciliation_history_index.v1"}
        )
    assert_nonaut(error)
    with pytest.raises(dispatch.DispatchError) as error:
        dispatch.enforce_reconciliation_document_authority(
            {"schema": dispatch.SCHEMA, "authority": {"dispatch_authority": "NONAUT"}}
        )
    assert_nonaut(error)


def test_ordinary_queue_path_and_document_remain_eligible(tmp_path):
    path = tmp_path / "coordination/goals/GOAL-ECDLP-001/batches/BATCH-031/dispatch_queue.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    dispatch.enforce_reconciliation_queue_authority(path, tmp_path)
    dispatch.enforce_reconciliation_document_authority({"schema": dispatch.SCHEMA})
