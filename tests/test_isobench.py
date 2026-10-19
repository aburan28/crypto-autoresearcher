"""isobench: every arm of the C benchmark reproduces k P on a small run (correctness, not timing)."""
import shutil
from pathlib import Path

import pytest

pytest.importorskip("flint")
if shutil.which("cc") is None:
    pytest.skip("no C compiler", allow_module_level=True)

from harness.endosweep.isobench import isobench as IB  # noqa: E402

ROWS = Path(__file__).resolve().parents[1] / "experiments/EXP-ENDO-25ad84/runs/RUN-ENDO-d7cb69/raw-result.json"


@pytest.mark.parametrize("curve", ["other/BADA55-VPR-224", "control+: 3-isogenous neighbour of NIST P-256"])
def test_bench_outputs_match_reference(tmp_path, curve):
    rc = IB.main(["--rows", str(ROWS), "--curve", curve, "--out-dir", str(tmp_path),
                  "--points", "3", "--reps", "1", "--bootstrap", "10", "--cflags=-O1"])
    assert rc == 0
