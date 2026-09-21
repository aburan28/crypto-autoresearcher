from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFIER = REPO_ROOT / "analysis" / "semaev-conservation-monodromy" / "verify.py"


def test_semaev_monodromy_proof_dossier_verifier() -> None:
    completed = subprocess.run(
        [sys.executable, str(VERIFIER)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    report = json.loads(completed.stdout)

    assert report["s3_discriminant"]["residual"] == 0
    assert report["regular_action"]["8"]["nonidentity_number_of_2_cycles"] == 32
    assert report["s4_specializations"]["all_square"]["factor_degrees"] == [1, 1, 1, 1]
    assert report["s4_specializations"]["all_nonsquare"]["factor_degrees"] == [1, 1, 1, 1]
    assert report["s4_specializations"]["mixed_2_square"]["factor_degrees"] == [2, 2]
    assert report["s4_specializations"]["mixed_1_square"]["factor_degrees"] == [2, 2]
    assert report["finite_field_counts"]["witness_conservation"]["total_per_base"] == 1000
    assert report["finite_field_counts"]["witness_conservation"]["support_sizes"] == [77, 81]
