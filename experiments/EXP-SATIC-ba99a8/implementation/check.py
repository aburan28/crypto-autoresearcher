#!/usr/bin/env python3
"""Independent checker for EXP-SATIC-ba99a8. Does not import run.py or s3_eval.py.

Re-derives S_3 expand vs school and the Sylvester vs product identity on the
frozen seeds. Dual meter.
Amazon Bedrock is not selected.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))
from gf2n import Field  # noqa: E402

EXPERIMENT_ID = "EXP-SATIC-ba99a8"
OUTCOMES_0 = {"O-STAGE0-OK", "O-ARTIFACT", "O-IMPEDIMENT"}
OUTCOMES_1 = {"O-SUPPORT", "O-FAIL-IDENTITY", "O-ARTIFACT", "O-IMPEDIMENT"}
MOD5, MOD17 = 37, (1 << 17) | (1 << 3) | 1


def s3_school(F: Field, x: int, y: int, z: int, B: int) -> int:
    xy = F.mul(x, y)
    xz = F.mul(x, z)
    yz = F.mul(y, z)
    return F.sqr(xy ^ xz ^ yz) ^ F.mul(xy, z) ^ B


def s3_expand(F: Field, a: int, b: int, x: int, B: int) -> int:
    s = a ^ b
    p = F.mul(a, b)
    return F.mul(F.sqr(s), F.sqr(x)) ^ F.mul(p, x) ^ F.sqr(p) ^ B


def coeffs(F: Field, a: int, b: int, B: int) -> tuple[int, int, int]:
    s = a ^ b
    p = F.mul(a, b)
    return F.sqr(s), p, F.sqr(p) ^ B


def det2(F: Field, a: int, b: int, c: int, d: int) -> int:
    return F.mul(a, d) ^ F.mul(b, c)


def det3(F: Field, a11: int, a12: int, a13: int, a21: int, a22: int, a23: int, a31: int, a32: int, a33: int) -> int:
    return (
        F.mul(a11, det2(F, a22, a23, a32, a33))
        ^ F.mul(a12, det2(F, a21, a23, a31, a33))
        ^ F.mul(a13, det2(F, a21, a22, a31, a32))
    )


def det4(F: Field, m: list[list[int]]) -> int:
    s = 0
    for j in range(4):
        minor = [[m[r][c] for c in range(4) if c != j] for r in range(1, 4)]
        s ^= F.mul(m[0][j], det3(F, *minor[0], *minor[1], *minor[2]))
    return s


def sylvester(F: Field, f: tuple[int, int, int], g: tuple[int, int, int]) -> int:
    a2, a1, a0 = f
    b2, b1, b0 = g
    return det4(F, [[a2, a1, a0, 0], [0, a2, a1, a0], [b2, b1, b0, 0], [0, b2, b1, b0]])


def roots(F: Field, A: int, lin: int, C: int) -> tuple[int, int] | None:
    if A == 0:
        if lin == 0:
            return (0, 0) if C == 0 else None
        r = F.mul(C, F.inv(lin))
        return (r, r)
    invA = F.inv(A)
    b = F.mul(lin, invA)
    c = F.mul(C, invA)
    if b == 0:
        r = F.sqrt(c)
        return (r, r)
    rhs = F.mul(c, F.inv(F.sqr(b)))
    if F.trace(rhs) != 0:
        return None
    z = F.half_trace(rhs)
    return (F.mul(b, z), F.mul(b, z ^ 1))


def identity_ok(F: Field, a: int, x2: int, x3: int, xr: int, B: int) -> bool:
    f = coeffs(F, x2, x3, B)
    g = coeffs(F, a, xr, B)
    rt = roots(F, *g)
    if rt is None:
        return False
    pre = F.sqr(F.sqr(a ^ xr))
    prod = F.mul(pre, F.mul(s3_expand(F, x2, x3, rt[0], B), s3_expand(F, x2, x3, rt[1], B)))
    if sylvester(F, f, g) != prod:
        return False
    for u in rt:
        if s3_school(F, x2, x3, u, B) != s3_expand(F, x2, x3, u, B):
            return False
    return True


def recount(n: int, mod: int, seed: int, tuples: int) -> tuple[int, int]:
    F = Field(n, mod)
    rng = random.Random(seed)
    kept = agree = 0
    tried = 0
    while kept < tuples and tried < tuples * 50:
        tried += 1
        a = rng.randrange(F.q)
        x2 = rng.randrange(F.q)
        x3 = rng.randrange(F.q)
        xr = rng.randrange(F.q)
        if a == xr:
            continue
        g = coeffs(F, a, xr, 1)
        if roots(F, *g) is None:
            continue
        kept += 1
        if identity_ok(F, a, x2, x3, xr, 1):
            agree += 1
    return kept, agree


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path, man_path = run_dir / "raw-result.json", run_dir / "manifest.yaml"
    errs: list[str] = []
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("n_ge_131"):
        errs.append("forbidden break/exponent/n>=131 claim present")
    stage = raw.get("stage")
    root = Path(__file__).resolve().parents[1]
    if stage == 0:
        if raw.get("outcome") not in OUTCOMES_0:
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
        for rel in ("stage0/cells.json", "stage0/counting.json", "stage0/n5-identity.json"):
            if not (root / rel).is_file():
                errs.append(f"missing freeze {rel}")
        cells = root / "stage0" / "cells.json"
        if cells.is_file():
            doc = json.loads(cells.read_text(encoding="utf-8"))
            rows = doc.get("rows")
            if not isinstance(rows, list) or not rows:
                errs.append("cells.json rows missing")
            elif not all(isinstance(r.get("n"), int) for r in rows):
                errs.append("cells.json n must be JSON integers")
        kept, agree = recount(5, MOD5, 2026100305, 20)
        if kept != 20 or agree != 20:
            errs.append(f"stage0 dual-meter identity {agree}/{kept} != 20/20")
    elif stage == 1:
        if raw.get("outcome") not in OUTCOMES_1:
            errs.append(f"bad stage1 outcome {raw.get('outcome')!r}")
        for rel in ("stage1/identity-panel.json", "RESULTS.md"):
            if not (root / rel).is_file():
                errs.append(f"missing {rel}")
        panel_p = root / "stage1" / "identity-panel.json"
        if panel_p.is_file():
            panel = json.loads(panel_p.read_text(encoding="utf-8"))
            rows = panel.get("rows")
            if not isinstance(rows, list) or not rows or not isinstance(rows[0].get("n"), int):
                errs.append("stage1 panel must be list rows with integer n")
        if raw.get("outcome") != "O-IMPEDIMENT":
            kept, agree = recount(17, MOD17, 2026100317, 100)
            if kept != 100:
                errs.append(f"stage1 dual-meter kept {kept} != 100")
            elif raw.get("outcome") == "O-SUPPORT" and agree != 100:
                errs.append(f"O-SUPPORT but checker identity {agree}/100")
            elif raw.get("outcome") == "O-FAIL-IDENTITY" and agree == 100:
                errs.append("O-FAIL-IDENTITY but checker saw 100/100")
    else:
        errs.append(f"bad stage {stage!r}")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
