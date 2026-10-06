"""Frozen fixtures (AMD-20260926-a7d25d C-1), derived parameters (C-2, C-3)
and byte-for-byte reproduction of the frozen fixture JSON."""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
REPO_ROOT = EXP_DIR.parent.parent
SPECIFICATION = EXP_DIR / "specification.yaml"
AMENDMENT = EXP_DIR / "amendments" / "AMD-20260926-a7d25d.yaml"
FIXTURE_DIR = REPO_ROOT / "experiments" / "EXP-SDEG-85eefd" / "amendments"
FIXTURE_JSON = FIXTURE_DIR / "ic_leads_fixtures_v2.json"
FIXTURE_GEN = FIXTURE_DIR / "ic_leads_fixtures_v2.py"

EXP_ID = "EXP-RELN-c5a377"
FROZEN_JSON_SHA256 = "543f49ca5304f4e61085305ca2ea01ccc0085298db26368d7362f96b1b6a5a45"
FROZEN_GEN_SHA256 = "bde44afb3e14c34d97bf50c154456565d12f0b5a1d33d63b473f0f4124b1f3b2"
SAGE_CANDIDATES = ("/usr/local/bin/sage", str(Path.home() / ".local/bin/sage"))


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_fixtures() -> list[dict]:
    return json.loads(FIXTURE_JSON.read_text())[EXP_ID]


def fixture(bits: int, seed: int) -> dict:
    for f in load_fixtures():
        if f["bits"] == bits and f["seed"] == seed:
            return f
    raise KeyError((bits, seed))


def fixture_id(f: dict) -> str:
    return f"b{f['bits']}-s{f['seed']}"


def iroot_ceil(n: int, num: int, den: int) -> int:
    """Exact ceil(n^{num/den}) for positive integers: least B with B^den >= n^num."""
    target = n ** num
    b = max(1, int(round(n ** (num / den))))
    while b ** den < target:
        b += 1
    while b > 1 and (b - 1) ** den >= target:
        b -= 1
    return b


def params(f: dict) -> dict:
    """C-2 bounds and C-3 attempt budgets, exact integer arithmetic."""
    p, q = f["p"], f["N"]
    return {"B": iroot_ceil(p, 1, 5), "B2": iroot_ceil(p, 2, 5),
            "A1": iroot_ceil(q, 1, 2), "A2": iroot_ceil(q, 3, 5),
            "sqrt_q": math.sqrt(q)}


def find_sage() -> str | None:
    for s in SAGE_CANDIDATES:
        if Path(s).exists():
            return s
    return None


def reproduce(out_path: Path, sage: str | None = None, timeout: int = 7200) -> dict:
    """Re-run the frozen generator with Sage; byte-compare to the frozen JSON
    (whole file and the EXP-RELN-c5a377 entries)."""
    sage = sage or find_sage()
    if sage is None:
        return {"byte_identical": False, "error": "sage not found"}
    env = dict(os.environ)
    tmp = env.get("TMPDIR", "/Volumes/SSD990/.tmp-agent")
    env.setdefault("DOT_SAGE", str(Path(tmp) / "dot_sage"))
    res = subprocess.run([sage, "-python", str(FIXTURE_GEN)], capture_output=True,
                         timeout=timeout, env=env)
    Path(out_path).write_bytes(res.stdout)
    frozen = FIXTURE_JSON.read_bytes()
    try:
        entries_equal = (json.loads(res.stdout)[EXP_ID] == json.loads(frozen)[EXP_ID])
    except (ValueError, KeyError):
        entries_equal = False
    return {
        "sage": sage,
        "generator_sha256": sha256_file(FIXTURE_GEN),
        "generator_sha256_matches_amendment": sha256_file(FIXTURE_GEN) == FROZEN_GEN_SHA256,
        "frozen_json_sha256": hashlib.sha256(frozen).hexdigest(),
        "frozen_json_sha256_matches_amendment": hashlib.sha256(frozen).hexdigest() == FROZEN_JSON_SHA256,
        "reproduced_sha256": hashlib.sha256(res.stdout).hexdigest(),
        "byte_identical": res.stdout == frozen,
        "reln_entries_identical": entries_equal,
        "returncode": res.returncode,
        "stderr_tail": res.stderr.decode(errors="replace")[-2000:],
    }
