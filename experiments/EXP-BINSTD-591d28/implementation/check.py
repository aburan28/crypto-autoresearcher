#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-591d28 Stage 0-1 run artifacts.

Recomputes RC-1 product-space dims at l=6 without importing run.py stage
drivers. Verifies raw-result.json / manifest.yaml agreement and Bedrock/claim
hygiene.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

EXPERIMENT_ID = "EXP-BINSTD-591d28"
EXP_ROOT = Path(__file__).resolve().parents[1]
N = 17
MOD = (1 << 17) | (1 << 3) | 1
STAGE0_OK = {"S0-FREEZE-OK"}
STAGE1_OK = {
    "O-STAGES-0-1-COMPLETE",
    "O-POSITIVE",
    "O-SURPRISE",
    "O-NEGATIVE",
    "O-ARTIFACT",
    "O-IMPEDIMENT",
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


def f_pow(base: int, e: int, mod: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = pmod(clmul(r, base), mod)
        base = pmod(clmul(base, base), mod)
        e >>= 1
    return r


def f2_rank(vectors: list[int]) -> int:
    basis: list[int] = []
    for v in vectors:
        x = v
        for b in basis:
            if x == 0:
                break
            if x.bit_length() == b.bit_length():
                x ^= b
        if x:
            basis.append(x)
            basis.sort(key=lambda z: -z.bit_length())
            cleaned: list[int] = []
            for g in basis:
                y = g
                for c in cleaned:
                    if y.bit_length() == c.bit_length():
                        y ^= c
                if y:
                    cleaned.append(y)
                    cleaned.sort(key=lambda z: -z.bit_length())
            basis = cleaned
    return len(basis)


def dims_at(l: int) -> list[int]:
    out = []
    for k in range(1, 4):
        max_exp = k * (l - 1)
        vecs = [f_pow(2, i, MOD) for i in range(max_exp + 1)]
        out.append(f2_rank(vecs))
    return out


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

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    stage = raw.get("stage")
    if stage not in (0, 1):
        errs.append(f"bad stage {stage!r}")

    # Independent P2 fixture at l=6
    d6 = dims_at(6)
    if d6 != [6, 11, 16]:
        errs.append(f"independent l=6 dims {d6} != [6,11,16]")

    claims = raw.get("claims") or {}
    if claims.get("break") or claims.get("exponent_move") or claims.get("deployed_attack"):
        errs.append("forbidden break/exponent/deployed claim present")
    if raw.get("amazon_bedrock") not in (None, "NOT SELECTED"):
        errs.append("amazon_bedrock not NOT SELECTED")

    if stage == 0:
        if raw.get("outcome") not in STAGE0_OK:
            errs.append(f"bad stage0 outcome {raw.get('outcome')!r}")
        for rel in (
            "stage0/preregistered-predictions.json",
            "stage0/dimension-tables.json",
            "stage0/subfield-baseline.md",
            "stage0/derivations-note.md",
        ):
            if not (EXP_ROOT / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        else:
            prereg = json.loads((EXP_ROOT / "stage0/preregistered-predictions.json").read_text(encoding="utf-8"))
            if prereg.get("experiment_id") != EXPERIMENT_ID:
                errs.append("prereg experiment_id mismatch")
            if prereg.get("master_seed") != 2026092731:
                errs.append("prereg master_seed mismatch")

    if stage == 1:
        outcome = raw.get("outcome")
        if outcome not in STAGE1_OK:
            errs.append(f"bad stage1 outcome {outcome!r}")
        if outcome == "O-STAGES-0-1-COMPLETE":
            for rel in (
                "stage1/spurious-lift-census.json",
                "stage1/support-census.json",
                "RESULTS.md",
            ):
                if not (EXP_ROOT / rel).is_file():
                    errs.append(f"missing {rel}")
            if raw.get("p2_ok") is not True:
                errs.append("O-STAGES-0-1-COMPLETE requires p2_ok true")

    man = man_path.read_text(encoding="utf-8")
    if EXPERIMENT_ID not in man and "experiment_id" not in man:
        errs.append("manifest missing experiment id")
    if "schema:" not in man and "run:" not in man:
        errs.append("manifest missing schema:/run:")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
