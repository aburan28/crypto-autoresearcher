from __future__ import annotations

import copy
from pathlib import Path

import pytest

from tools import author_reconciliation_history as history


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def compilation():
    return history.build_compilation(ROOT)


def codes(error: pytest.ExceptionInfo[history.HistoryCompilerError]) -> str:
    return error.value.code


def test_bound_compilation_has_exact_census(compilation):
    assert compilation.summary() == {
        "schema": "crypto.autoresearch.reconciliation_history_compilation_summary.v1",
        "reconciliation_id": "RECON-20260802-001",
        "task_id": "TASK-20260803-003",
        "contract_snapshot_commit": history.SNAPSHOT_COMMIT,
        "contract_sha256": history.CONTRACT_SHA256,
        "source_occurrence_rows": 100,
        "reference_occurrence_rows": 623,
        "preservation_mapping_rows": 128,
        "preservation_blob_copies": 126,
        "preservation_absence_attestations": 2,
        "generated_history_outputs": 15,
        "authority": "NONAUT",
    }
    assert compilation.source_occurrences["summary"] == {
        "row_count": 100,
        "original_id_count": 91,
        "state_counts": {"blocked": 5, "cancelled": 10, "completed": 78, "queued": 7},
        "identity_id_counts": {"shared_conflicting": 8, "shared_identical": 1, "unique": 82},
        "archive_entry_count": 44,
        "archive_hash_bound_count": 35,
        "archive_unbound_count": 9,
        "archive_source_history_unreachable_count": 17,
    }


def test_outputs_are_deterministic_and_non_authorizing(compilation):
    second = history.build_compilation(ROOT)
    assert compilation.generated_outputs == second.generated_outputs
    assert len(compilation.generated_outputs) == 15
    for path, content in compilation.generated_outputs.items():
        assert b'"dispatch_authority": "NONAUT"' in content or b"Authority: `NONAUT`" in content
        if path.endswith("dispatch_queue.json"):
            assert b"crypto.autoresearch.dispatch_queue.v1" not in content


def test_contract_coordinated_drift_fails_before_parse():
    raw = history.GitObjects(ROOT).blob(history.SNAPSHOT_COMMIT, history.CONTRACT_PATH)
    mutated = raw.replace(b"local-a9664afb", b"local-coordinated-drift")
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_contract_bytes(mutated)
    assert codes(error) == "IMMUTABLE_BINDING_MISMATCH"


def test_source_row_omission_and_completion_copy_fail(compilation):
    table = copy.deepcopy(compilation.source_occurrences)
    table["rows"].pop()
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_source_occurrence_table(table, compilation.contract)
    assert codes(error) == "SOURCE_OCCURRENCE_COUNT_MISMATCH"

    table = copy.deepcopy(compilation.source_occurrences)
    table["rows"][0]["successor_reference"]["completion_or_receipt_inherited"] = True
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_source_occurrence_table(table, compilation.contract)
    assert codes(error) == "COPIED_COMPLETION_FORBIDDEN"


def test_reanchor_batch_023_order_is_frozen(compilation):
    table = copy.deepcopy(compilation.source_occurrences)
    rows = [
        row for row in table["rows"]
        if row["side"] == "reanchor" and row["batch"] == "BATCH-023"
    ]
    rows[4]["source_task_id"], rows[5]["source_task_id"] = (
        rows[5]["source_task_id"], rows[4]["source_task_id"]
    )
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_source_occurrence_table(table, compilation.contract)
    assert codes(error) == "SOURCE_OCCURRENCE_ORDER_MISMATCH"


def test_reference_unclassified_and_duplicate_fail(compilation):
    table = copy.deepcopy(compilation.reference_occurrences)
    table["rows"][0]["disposition"] = "unclassified"
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_reference_occurrence_table(table, compilation.contract)
    assert codes(error) == "REFERENCE_UNCLASSIFIED"

    table = copy.deepcopy(compilation.reference_occurrences)
    table["rows"].append(copy.deepcopy(table["rows"][0]))
    with pytest.raises(history.HistoryCompilerError) as error:
        history.validate_reference_occurrence_table(table, compilation.contract)
    assert codes(error) == "REFERENCE_OCCURRENCE_DUPLICATE"


def test_materialization_is_temp_only_and_byte_exact(compilation, tmp_path):
    written = history.materialize_compilation(compilation, tmp_path, ROOT)
    assert len(written) == 141
    assert not any("TASK-20260803-003" in path for path in written)
    with pytest.raises(history.HistoryCompilerError) as error:
        history.materialize_compilation(compilation, tmp_path, ROOT)
    assert codes(error) == "OUTPUT_ALREADY_EXISTS"


def test_absences_remain_absent(compilation, tmp_path):
    absence = next(
        row for row in compilation.preservation_mappings
        if row["disposition"] == "absence_attestation"
    )
    target = tmp_path.joinpath(*Path(absence["target_path"]).parts)
    target.parent.mkdir(parents=True)
    target.write_bytes(b"")
    with pytest.raises(history.HistoryCompilerError) as error:
        history.materialize_compilation(compilation, tmp_path, ROOT)
    assert codes(error) == "ABSENCE_MATERIALIZED"
