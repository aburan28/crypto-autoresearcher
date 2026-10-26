import json
import shutil
import subprocess

import pytest

from research_kb.config import Settings
from research_kb.ingest import refresh
from research_kb.lean import audit_project
from research_kb.library import Library


@pytest.mark.skipif(shutil.which("lake") is None, reason="Lean toolchain not installed")
def test_real_lean_compilation_and_axiom_receipts(tmp_path):
    project = tmp_path / "proof"
    project.mkdir()
    (project / "lakefile.toml").write_text('name="proof"\n[[lean_lib]]\nname="Smoke"\n')
    (project / "Smoke.lean").write_text("""import Init
namespace Smoke
theorem symmetry (a b : Nat) (h : a = b) : b = a := h.symm
axiom assumed : False
theorem bad : False := assumed
end Smoke
""")
    config = tmp_path / "sources.toml"
    config.write_text(
        '[[sources]]\nname="proof"\nroot=' + json.dumps(str(project)) + '\ninclude=["Smoke.lean"]\n'
    )
    subprocess.run(["lake", "update"], cwd=project, check=True, capture_output=True)
    lib = Library(Settings(home=tmp_path / "state", config=config))
    assert refresh(lib)["failed"] == 0
    report = audit_project(lib, project, ["Smoke"])
    assert report["attached"] == 3
    assert report["failed_axiom_checks"] == 2
    good = lib.catalog.search_theorems("Smoke.symmetry")[0]
    bad = lib.catalog.search_theorems("Smoke.bad")[0]
    assert good["verification"] == "kernel-axiom-audited"
    assert good["receipt"]["source_sha256"] == good["source_content_hash"]
    assert bad["verification"] == "nonstandard-axioms"
    assert bad["axioms"] == ["Smoke.assumed"]
