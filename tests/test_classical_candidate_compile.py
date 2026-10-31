"""Exercise the compiler and self-test path that failed in RUN-ECDLP-9f18c9.

This checks current source only. It does not repair or reinterpret that run.
"""

import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "harness/classical_ecdlp_solver_validation/admission/batch-config.json"


def test_archived_candidate_build_and_self_test() -> None:
    config = json.loads(CONFIG.read_text())
    candidate = next(module for module in config["modules"]
                     if module["name"] == "candidate_0")
    with tempfile.TemporaryDirectory(prefix="classical-decoder-") as temp:
        binary = Path(temp) / "candidate"
        build = subprocess.run(
            ["g++", *config["compiler_flags"], candidate["source"], "-o", str(binary)],
            cwd=ROOT, capture_output=True, text=True, timeout=180, check=False,
        )
        assert build.returncode == 0, build.stdout + build.stderr
        check = subprocess.run(
            [str(binary), "--self-test"], cwd=ROOT,
            capture_output=True, text=True, timeout=120, check=False,
        )
        assert check.returncode == 0, check.stdout + check.stderr
