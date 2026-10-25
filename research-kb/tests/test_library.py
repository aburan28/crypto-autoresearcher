import io
import json
import tarfile

import pytest

from research_kb.config import Settings
from research_kb.ingest import bundle, import_bundle, refresh
from research_kb.library import Library


def test_unified_search_and_ambiguous_legacy_ids(populated):
    lib, _, _ = populated
    result = lib.search("KN-LIT-001")
    assert {r["origin_repositories"][0] for r in result["results"]} == {"crypto", "cryptanalysis"}
    scoped = lib.search("KN-LIT-001", repo="crypto")
    assert all(r["origin_repositories"] == ["crypto"] for r in scoped["results"])
    assert lib.source("KN-LIT-001")["ambiguous"]
    assert lib.source("crypto:KN-LIT-001")["found"]


def test_pdf_dedup_preserves_origins_pages_and_original(populated):
    lib, a, _ = populated
    rows = lib.search("PageTwoBeta", source_type="paper")["results"]
    assert rows
    row = rows[0]
    assert row["origin_repositories"] == ["cryptanalysis", "crypto"]
    assert row["page_start"] <= 2 <= row["page_end"]
    assert lib.original(row["source_id"]).read_bytes() == (a / "paper.pdf").read_bytes()
    with lib.catalog.connect() as db:
        assert db.execute("SELECT COUNT(*) FROM documents WHERE kind='paper'").fetchone()[0] == 1


def test_source_updates_preserve_old_context_and_remove_missing(populated):
    lib, a, _ = populated
    original = lib.search("Semaev", repo="crypto")["results"][0]
    (a / "note.md").write_text(
        "# Replacement\n\nA replacement note about birational representations and distinct assumptions.\n"
    )
    refresh(lib)
    assert not lib.search("Semaev", repo="crypto", source_type="internal-note")["results"]
    assert lib.catalog.context(original["chunk_id"])["found"]
    assert lib.catalog.context(original["chunk_id"])["chunk"]["origins"][0]["path"] == "note.md"
    (a / "note.md").unlink()
    refresh(lib)
    assert not lib.search("birational")["results"]


def test_identical_notes_still_have_distinct_repository_identities(populated):
    lib, a, b = populated
    (b / "copy.md").write_bytes((a / "note.md").read_bytes())
    refresh(lib)
    rows = lib.search("KN-LIT-001")["results"]
    assert len({r["source_id"] for r in rows}) == 3


def test_supersession_and_untrusted_fts_input(populated):
    lib, _, _ = populated
    assert not lib.search("obsoletequartz")["results"]
    assert lib.search("obsoletequartz", include_superseded=True)["results"]
    assert isinstance(lib.search('" OR *; DROP TABLE documents; --')["results"], list)
    assert lib.catalog.status()["ready"]


def test_source_only_theorem_not_upgraded_by_proof_syntax(populated):
    lib, _, _ = populated
    rows = lib.catalog.search_theorems("CryptoLean.Semaev.sample")
    assert len(rows) == 1
    assert rows[0]["verification"] == "source-only"
    assert "(h : x = y)" in rows[0]["statement"]
    assert "[Field K]" in rows[0]["statement"]
    assert rows[0]["module"] == "Theorems"
    assert rows[0]["lean_environment"]["toolchain"] == "leanprover/lean4:v4.35.0"
    assert not lib.catalog.search_theorems("fake")


def test_bundle_roundtrip_and_hash_validation(populated, tmp_path):
    lib, _, _ = populated
    archive = tmp_path / "sources.tar.gz"
    assert bundle(lib.settings, archive)["unique_objects"] == 5
    hosted = Library(Settings(home=tmp_path / "hosted"))
    report = import_bundle(hosted, archive)
    assert report["indexed"] == 6
    assert {r["source_id"] for r in lib.search("KN-LIT-001")["results"]} == {
        r["source_id"] for r in hosted.search("KN-LIT-001")["results"]
    }
    assert hosted.catalog.search_theorems("CryptoLean.Semaev.sample")[0]["verification"] == "source-only"
    broken = tmp_path / "broken.tar.gz"
    with tarfile.open(broken, "w:gz") as tar:
        manifest = json.dumps(
            {"schema": 1, "sources": [{"repo": "x", "path": "a.md", "sha256": "bad"}]}
        ).encode()
        for name, data in [("manifest.json", manifest), ("objects/bad", b"tampered")]:
            item = tarfile.TarInfo(name)
            item.size = len(data)
            tar.addfile(item, io.BytesIO(data))
    with pytest.raises(ValueError, match="hash"):
        import_bundle(hosted, broken)


def test_bundle_cannot_traverse(populated, tmp_path):
    lib, _, _ = populated
    broken = tmp_path / "traversal.tar.gz"
    with tarfile.open(broken, "w:gz") as tar:
        entry = tarfile.TarInfo("../outside")
        entry.size = 1
        tar.addfile(entry, io.BytesIO(b"x"))
    with pytest.raises(ValueError, match="unsafe"):
        import_bundle(lib, broken)
    assert not (tmp_path / "outside").exists()


def test_empty_is_unavailable_and_backup_restores(populated, tmp_path):
    empty = Library(Settings(home=tmp_path / "empty"))
    with pytest.raises(RuntimeError, match="no active sources"):
        empty.search("anything")
    lib, _, _ = populated
    path = tmp_path / "backup.sqlite"
    lib.catalog.backup(path)
    from research_kb.catalog import Catalog

    assert Catalog(path).search("conductor")


def test_hybrid_publication_and_stale_revision(populated, tmp_path):
    lib, a, _ = populated
    lib.settings.qdrant_url = str(tmp_path / "qdrant")
    pointer = lib.index()
    result = lib.search("summation polynomials", mode="hybrid")
    assert result["results"]
    assert lib.status()["active_index"]["collection"] == pointer["collection"]
    (a / "new.md").write_text("# Fresh\n\nA fresh document about torsion over finite fields.\n")
    refresh(lib)
    with pytest.raises(RuntimeError, match="stale"):
        lib.search("torsion", mode="hybrid")
