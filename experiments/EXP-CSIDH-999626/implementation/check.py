#!/usr/bin/env python3
"""Independent checker for EXP-CSIDH-999626 Stage 0-1 run artifacts.

Recomputes reduced-form census of disc=-419 and the probe formulas without
importing run.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-CSIDH-999626"
DISC = -419
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {
    "O-SEPARATES",
    "O-NO-BIND",
    "O-BLIND-MOVED",
    "O-G-NOT-COMMON",
    "O-N1-GAP",
    "O-MISMATCH",
    "O-WRONG-DISC",
    "O-IMPEDIMENT",
}


def is_reduced(a: int, b: int, c: int) -> bool:
    if a <= 0:
        return False
    if abs(b) > a or a > c:
        return False
    if abs(b) == a or a == c:
        return b >= 0
    return True


def enumerate_forms(disc: int) -> list[tuple[int, int, int]]:
    forms: list[tuple[int, int, int]] = []
    a_max = int(math.isqrt((-disc) // 3)) + 2
    for a in range(1, a_max + 1):
        for b in range(-a, a + 1):
            num = b * b - disc
            den = 4 * a
            if num % den != 0:
                continue
            c = num // den
            if is_reduced(a, b, c) and (b * b - 4 * a * c) == disc:
                forms.append((a, b, c))
    return sorted(forms)


def probe(g: int, m: int, n: int, m_free: int) -> int:
    return g * (2 ** math.ceil(math.sqrt(n))) * math.ceil(m_free / m)


def load_yaml_outcome(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("outcome:"):
            return line.split(":", 1)[1].strip()
    raise ValueError("no outcome")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1]).resolve()
    raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        print("experiment_id mismatch", file=sys.stderr)
        return 1
    if raw.get("amazon_bedrock") != "NOT SELECTED":
        print("amazon_bedrock must be NOT SELECTED", file=sys.stderr)
        return 1
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("attack") or claims.get("exponent_move"):
        print("forbidden claim flag", file=sys.stderr)
        return 1
    stage = (raw.get("result") or {}).get("stage")
    outcome = (raw.get("result") or {}).get("outcome")
    if outcome != load_yaml_outcome(run_dir / "manifest.yaml"):
        print("manifest/raw outcome mismatch", file=sys.stderr)
        return 1
    exp_root = run_dir.parents[1]
    if stage == 0:
        if outcome not in STAGE0_OK:
            print("bad stage0 outcome", file=sys.stderr)
            return 1
        freeze = json.loads((exp_root / "stage0" / "protocol-freeze.json").read_text())
        if freeze.get("pinned", {}).get("disc") != DISC:
            print("frozen disc mismatch", file=sys.stderr)
            return 1
        print("check.py PASS stage 0", outcome)
        return 0
    if stage != 1 or outcome not in STAGE1_OK:
        print("bad stage1 outcome", file=sys.stderr)
        return 1
    census = json.loads((exp_root / "stage1" / "census.json").read_text())
    forms = enumerate_forms(DISC)
    n_cls = len(forms)
    if census.get("N") != n_cls:
        print(f"N mismatch checker={n_cls} census={census.get('N')}", file=sys.stderr)
        return 1
    n = max(1, math.ceil(math.log2(max(n_cls, 2))))
    m_free = 2 ** math.ceil(math.sqrt(n))
    if census.get("M_free") != m_free:
        print("M_free mismatch", file=sys.stderr)
        return 1
    ratio = probe(1, 2, n, m_free) / probe(1, m_free, n, m_free)
    if abs(float(census["G1"]["ratio"]) - ratio) > 1e-12:
        print("ratio mismatch", file=sys.stderr)
        return 1
    control = json.loads((exp_root / "stage1" / "control-table.json").read_text())
    if control.get("wrong_disc", {}).get("used_as_N") is not False:
        print("wrong disc used as N", file=sys.stderr)
        return 1
    n1_n = max(1, math.ceil(math.log2(2)))
    n1_mf = 2 ** math.ceil(math.sqrt(n1_n))
    n1_ratio = probe(1, 2, n1_n, n1_mf) / probe(1, n1_mf, n1_n, n1_mf)
    if n1_ratio != 1 and outcome not in {"O-N1-GAP", "O-IMPEDIMENT"}:
        print("N=1 control should be 1", file=sys.stderr)
        return 1
    print("check.py PASS stage 1", outcome)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
