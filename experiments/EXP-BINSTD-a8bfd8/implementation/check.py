#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-a8bfd8 Stage 0-1 run artifacts.

Recomputes one irreducible modulus and one m=7 tensor distinct-quadratic
count without importing run.py stage drivers. Verifies raw-result.json /
manifest.yaml agreement and Bedrock/claim hygiene.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

EXPERIMENT_ID = "EXP-BINSTD-a8bfd8"
STAGE0_OK = {"S0-FREEZE-OK", "O-A-FALSE"}
STAGE1_OK = {
    "O-STAGES-0-1-COMPLETE",
    "O-A-FALSE",
    "O-B-FALSE",
    "O-IMPEDIMENT",
    "O-ARTIFACT",
}


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> bool:
    n = mod.bit_length() - 1
    x = 2
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2 and pgcd(mod, cur ^ x) != 1:
            ok = False
    return ok and cur == x


def find_irreducible(m: int, weight: int) -> int:
    head = 1 << m
    if weight == 3:
        for k in range(1, m):
            cand = head | (1 << k) | 1
            if is_irreducible(cand):
                return cand
    else:
        for k3 in range(3, m):
            for k2 in range(2, k3):
                for k1 in range(1, k2):
                    cand = head | (1 << k3) | (1 << k2) | (1 << k1) | 1
                    if is_irreducible(cand):
                        return cand
    raise ArithmeticError("not found")


def distinct_quadratic(m: int, mod: int) -> int:
    """Incidence total: sum over outputs of nonzero (i<=j) contributions."""
    total = 0
    for k in range(m):
        for i in range(m):
            for j in range(i, m):
                prod = pmod(clmul(1 << i, 1 << j), mod)
                if (prod >> k) & 1:
                    total += 1
    return total


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(sys.argv[1])
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.yaml"
    errs: list[str] = []
    if not raw_path.is_file() or raw_path.stat().st_size == 0:
        errs.append("missing/empty raw-result.json")
    if not man_path.is_file() or man_path.stat().st_size == 0:
        errs.append("missing/empty manifest.yaml")
    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1

    raw: dict[str, Any] = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("experiment_id") != EXPERIMENT_ID:
        errs.append("experiment_id mismatch")
    if raw.get("amazon_bedrock") not in ("NOT_USED", "NOT SELECTED"):
        errs.append("Bedrock marker missing/invalid")
    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("attack"):
        errs.append("forbidden break/exponent/attack claim present")

    result = raw.get("result") or {}
    status = result.get("status")
    if status not in ("completed_valid", "failed_infrastructure"):
        errs.append(f"unexpected status {status!r}")
    stage = result.get("stage", raw.get("stage"))
    outcome = result.get("outcome")
    root = Path(__file__).resolve().parents[1]

    # Independent pins: m=7 first trinomial/pentanomial and tensor counts.
    tri7 = find_irreducible(7, 3)
    pent7 = find_irreducible(7, 5)
    if tri7 != 0x83 or pent7 != 0x8F:
        errs.append(f"independent m=7 moduli pin failed: {hex(tri7)}/{hex(pent7)}")
    if not is_irreducible(tri7) or not is_irreducible(pent7):
        errs.append("independent irreducibility pin failed")
    d_tri = distinct_quadratic(7, tri7)
    d_pent = distinct_quadratic(7, pent7)
    if d_pent <= d_tri:
        # Not a hard fail of the checker when science says O-A-FALSE; just pin
        # that the recomputation is deterministic and positive.
        pass
    if d_tri < 1 or d_pent < 1:
        errs.append("independent tensor distinct counts non-positive")

    man = man_path.read_text(encoding="utf-8")
    if EXPERIMENT_ID not in man:
        errs.append("manifest missing experiment_id")
    if f"outcome: {outcome}" not in man and f"outcome: {outcome}" not in man.replace("'", ""):
        if f"outcome: {outcome}" not in man:
            errs.append("manifest/raw outcome mismatch")

    if stage == 0:
        if outcome not in STAGE0_OK:
            errs.append(f"unexpected stage0 outcome {outcome!r}")
        for name in (
            "preregistered-predictions.json",
            "tensor-census.json",
            "derivations-note.md",
        ):
            path = root / "stage0" / name
            if not path.is_file() or path.stat().st_size == 0:
                errs.append(f"missing stage0/{name}")
        census_path = root / "stage0" / "tensor-census.json"
        if census_path.is_file():
            census = json.loads(census_path.read_text(encoding="utf-8"))
            cell7 = next((c for c in census.get("cells", []) if c.get("m") == 7), None)
            if cell7 is None:
                errs.append("stage0 census missing m=7 cell")
            else:
                if cell7["trinomial"]["distinct_quadratic_monomials"] != d_tri:
                    errs.append("stage0 m=7 tri distinct mismatch vs independent recompute")
                if cell7["pentanomial"]["distinct_quadratic_monomials"] != d_pent:
                    errs.append("stage0 m=7 pent distinct mismatch vs independent recompute")
    elif stage == 1:
        if outcome not in STAGE1_OK:
            errs.append(f"unexpected stage1 outcome {outcome!r}")
        if outcome != "O-IMPEDIMENT":
            support = root / "stage1" / "support-census.json"
            if not support.is_file() or support.stat().st_size == 0:
                if outcome not in {"O-A-FALSE"}:  # SR-2 may skip support file
                    errs.append("missing stage1/support-census.json")
        results = root / "RESULTS.md"
        if not results.is_file() or results.stat().st_size == 0:
            errs.append("missing RESULTS.md")
        elif outcome and outcome not in results.read_text(encoding="utf-8"):
            errs.append("RESULTS.md does not name the outcome")
    else:
        errs.append(f"unexpected stage {stage!r}")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "stage": stage,
                "outcome": outcome,
                "independent_m7": {
                    "tri": hex(tri7),
                    "pent": hex(pent7),
                    "d_tri": d_tri,
                    "d_pent": d_pent,
                },
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
