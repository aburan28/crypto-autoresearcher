from __future__ import annotations

from pathlib import Path

from tools import author_reconciliation_history as history
from tools import check_reconciliation_generated_artifacts as checker


ROOT = Path(__file__).resolve().parents[1]


def test_static_check_binds_exact_tables_and_counts():
    report = checker.check()
    assert report["pass"] and report["findings"] == []
    assert set(report["implementation_bindings"]) == {
        "checker_sha256",
        "compiler_sha256",
        "dispatcher_sha256",
    }
    assert all(
        len(digest) == 64 for digest in report["implementation_bindings"].values()
    )
    assert report["counts"]["source_occurrences"] == 100
    assert report["counts"]["reference_occurrences"] == 623
    assert report["counts"]["preservation_mappings"] == 128
    assert report["counts"]["generated_history_outputs"] == 15
    assert report["counts"]["archive_source_history_unreachable"] == 17


def test_mutated_source_and_reference_tables_fail(tmp_path):
    source = tmp_path / "source.json"
    source.write_bytes(checker.DEFAULT_SOURCE_TABLE.read_bytes() + b" ")
    report = checker.check(source_table=source)
    assert not report["pass"]
    assert report["findings"][0]["code"] == "SOURCE_TABLE_BINDING_MISMATCH"

    reference = tmp_path / "reference.json"
    reference.write_bytes(checker.DEFAULT_REFERENCE_TABLE.read_bytes() + b" ")
    report = checker.check(reference_table=reference)
    assert not report["pass"]
    assert report["findings"][0]["code"] == "REFERENCE_TABLE_BINDING_MISMATCH"


def test_candidate_positive_and_corruption_controls(tmp_path):
    compilation = history.build_compilation(ROOT)
    history.materialize_compilation(compilation, tmp_path, ROOT)
    report = checker.check(candidate_root=tmp_path)
    assert report["pass"]
    assert report["candidate_counts"] == {
        "blob_copies": 126,
        "absence_attestations": 2,
        "history_outputs": 15,
    }
    first = next(
        row for row in compilation.preservation_mappings
        if row["disposition"] == "copy_blob_verbatim"
    )
    target = tmp_path.joinpath(*Path(first["target_path"]).parts)
    target.write_bytes(target.read_bytes() + b"corruption")
    report = checker.check(candidate_root=tmp_path)
    assert not report["pass"]
    assert report["findings"][0]["code"] == "PRESERVATION_TARGET_HASH_MISMATCH"


def test_candidate_absence_empty_file_is_not_an_attestation(tmp_path):
    compilation = history.build_compilation(ROOT)
    history.materialize_compilation(compilation, tmp_path, ROOT)
    absence = next(
        row for row in compilation.preservation_mappings
        if row["disposition"] == "absence_attestation"
    )
    target = tmp_path.joinpath(*Path(absence["target_path"]).parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"")
    report = checker.check(candidate_root=tmp_path)
    assert not report["pass"]
    assert report["findings"][0]["code"] == "ABSENCE_MATERIALIZED"


def test_candidate_symlink_cannot_substitute_for_preserved_blob(tmp_path):
    compilation = history.build_compilation(ROOT)
    history.materialize_compilation(compilation, tmp_path, ROOT)
    first = next(
        row for row in compilation.preservation_mappings
        if row["disposition"] == "copy_blob_verbatim"
    )
    target = tmp_path.joinpath(*Path(first["target_path"]).parts)
    substitute = tmp_path / "substitute"
    substitute.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(substitute)
    report = checker.check(candidate_root=tmp_path)
    assert not report["pass"]
    assert report["findings"][0]["code"] == "PRESERVATION_TARGET_INVALID"
