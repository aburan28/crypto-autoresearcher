import json

import pymupdf
import pytest

from research_kb.auth import token_digest
from research_kb.config import Settings
from research_kb.ingest import refresh
from research_kb.library import Library


@pytest.fixture
def populated(tmp_path):
    a, b = tmp_path / "crypto", tmp_path / "cryptanalysis"
    a.mkdir()
    b.mkdir()
    (a / "note.md").write_text(
        "---\nid: KN-LIT-001\ntitle: Semaev decomposition\n---\n\n# Summation polynomials\n\nSemaev decomposition over prime fields is a reported research mechanism. The source does not establish a practical speedup.\n"
    )
    (b / "other.md").write_text(
        "---\nid: KN-LIT-001\ntitle: Distinct legacy entry\n---\n\n# Curve conductor\n\nThe endomorphism ring conductor is not the Frobenius conductor; preserve the distinction in isogeny audits.\n"
    )
    (a / "old.md").write_text(
        "---\nid: KN-FIND-OLD\nsuperseded_by: KN-FIND-NEW\n---\n\n# Superseded\n\nThis obsoletequartz conclusion was replaced by a later review.\n"
    )
    (a / "lean-toolchain").write_text("leanprover/lean4:v4.35.0\n")
    (a / "lakefile.toml").write_text('name = "Proof"\n')
    (a / "Theorems.lean").write_text("""import Mathlib
namespace CryptoLean.Semaev
variable {K : Type*} [Field K]
/- theorem fake : False := by sorry -/
/-- A scoped identity with an explicit hypothesis. -/
theorem sample (x y : K) (h : x = y) : y = x := by
  exact h.symm
end CryptoLean.Semaev
""")
    doc = pymupdf.open()
    for word in ("PageOneAlpha", "PageTwoBeta"):
        page = doc.new_page()
        page.insert_text((72, 72), word + " preserved original PDF source " * 8)
    pdf = doc.tobytes()
    doc.close()
    (a / "paper.pdf").write_bytes(pdf)
    (b / "duplicate.pdf").write_bytes(pdf)
    config = tmp_path / "sources.toml"
    config.write_text(
        f'[[sources]]\nname="crypto"\nroot={json.dumps(str(a))}\n\n[[sources]]\nname="cryptanalysis"\nroot={json.dumps(str(b))}\n'
    )
    auth = tmp_path / "auth.json"
    auth.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "tokens": {
                    "codex-cloud": token_digest("test-codex-secret"),
                    "claude-cloud": token_digest("test-claude-secret"),
                },
            }
        )
    )
    settings = Settings(
        home=tmp_path / "state",
        config=config,
        auth_file=auth,
        allowed_hosts=["testserver", "localhost", "127.0.0.1"],
    )
    lib = Library(settings)
    report = refresh(lib)
    assert report["failed"] == 0, report
    return lib, a, b
