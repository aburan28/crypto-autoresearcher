"""The implementation note reaches search through the existing corpus rule."""

from pathlib import Path

from crypto_kb.ingest.repo_corpus import RULES, iter_staged
from crypto_kb.models import Authority, ClaimStatus, SourceType


def test_actual_control_note_stages_without_scientific_promotion(tmp_path):
    root = Path(__file__).resolve().parents[3]
    relative = "docs/lifting-representation-controls.md"
    source = root / relative
    copy = tmp_path / relative
    copy.parent.mkdir(parents=True)
    copy.write_bytes(source.read_bytes())
    docs_rule = next(rule for rule in RULES if rule.name == "docs")
    staged = list(iter_staged(tmp_path, (docs_rule,), "unit-test-revision", include={relative}))
    assert len(staged) == 1
    document = staged[0]
    assert document.data == source.read_bytes()
    assert document.metadata["source_type"] == SourceType.REPOSITORY_DOC.value
    assert document.metadata["authority"] == Authority.INTERNAL_ANALYSIS.value
    assert document.metadata["claim_status"] == ClaimStatus.PUBLISHED.value
    assert document.metadata.get("evidence_level") in (None, "none")
    assert document.metadata["git_commit"] == "unit-test-revision"
    for keyword in ("lifting residuals", "circular", "hofman", "kn-tech-73630e",
                    "kn-open-3417fc", "representation-controls"):
        assert keyword in document.data.decode().lower()
