"""Frozen fixtures (AMD-20260926-3479cf C-1) and their byte-for-byte reproduction."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
AMEND_DIR = EXP_DIR / "amendments"
FIXTURE_JSON = AMEND_DIR / "ic_leads_fixtures_v2.json"
FIXTURE_GEN = AMEND_DIR / "ic_leads_fixtures_v2.py"
AMENDMENT = AMEND_DIR / "AMD-20260926-3479cf.yaml"
AMENDMENT_V3 = AMEND_DIR / "AMD-20260928-7ce387.yaml"
SPECIFICATION = EXP_DIR / "specification.yaml"

FROZEN_JSON_SHA256 = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
FROZEN_GEN_SHA256 = "bde44afb3e14c34d97bf50c154456565d12f0b5a1d33d63b473f0f4124b1f3b2"
SAGE = "/usr/local/bin/sage"


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_fixtures() -> list[dict]:
    data = json.loads(FIXTURE_JSON.read_text())
    return data["EXP-SDEG-85eefd"]


def fixture(L: int, seed: int) -> dict:
    for f in load_fixtures():
        if f["L"] == L and f["seed"] == seed:
            return f
    raise KeyError((L, seed))


def fixture_id(f: dict) -> str:
    return f"L{f['L']}-s{f['seed']}"


def reproduce(out_path: Path, sage: str = SAGE, timeout: int = 3600) -> dict:
    """Re-run the frozen generator with Sage and byte-compare to the frozen JSON."""
    res = subprocess.run([sage, "-python", str(FIXTURE_GEN)], capture_output=True,
                         timeout=timeout)
    Path(out_path).write_bytes(res.stdout)
    frozen = FIXTURE_JSON.read_bytes()
    return {
        "generator_sha256": sha256_file(FIXTURE_GEN),
        "generator_sha256_matches_amendment": sha256_file(FIXTURE_GEN) == FROZEN_GEN_SHA256,
        "frozen_json_sha256": hashlib.sha256(frozen).hexdigest(),
        "reproduced_sha256": hashlib.sha256(res.stdout).hexdigest(),
        "byte_identical": res.stdout == frozen,
        "returncode": res.returncode,
        "stderr_tail": res.stderr.decode(errors="replace")[-2000:],
    }
