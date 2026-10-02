#!/usr/bin/env python3
"""Independent checker for EXP-BINSTD-372679 run artifacts.

Recomputes ord_n(2) and stable dims without importing run.py.
Verifies raw-result.json / manifest.yaml agreement and Stage-0/1 freeze files.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

PREREG_ORD = {17: 8, 23: 11, 31: 5, 131: 130, 163: 162}
PREREG_DIMS_163 = [0, 1, 162, 163]
EXP_ROOT = Path(__file__).resolve().parents[1]


def multiplicative_order(a: int, n: int) -> int:
    if math.gcd(a, n) != 1:
        raise ValueError(f"gcd({a},{n}) != 1")
    m = n - 1
    factors: list[int] = []
    d = 2
    x = m
    while d * d <= x:
        while x % d == 0:
            factors.append(d)
            x //= d
        d += 1
    if x > 1:
        factors.append(x)
    order = m
    for p in sorted(set(factors)):
        while order % p == 0 and pow(a, order // p, n) == 1:
            order //= p
    return order


def stable_dims_from_ord(n: int, ord_n: int) -> list[int]:
    if (n - 1) % ord_n != 0:
        raise ValueError("ord does not divide n-1")
    k = (n - 1) // ord_n
    return sorted({i + j * ord_n for i in (0, 1) for j in range(k + 1)})


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

    # Independent arithmetic
    ords = {n: multiplicative_order(2, n) for n in PREREG_ORD}
    dims163 = stable_dims_from_ord(163, ords[163])
    if ords != PREREG_ORD:
        errs.append(f"independent ord mismatch: {ords} vs {PREREG_ORD}")
    if dims163 != PREREG_DIMS_163:
        errs.append(f"independent dims163 mismatch: {dims163}")

    if raw.get("claims", {}).get("break") or raw.get("claims", {}).get("exponent_move"):
        errs.append("forbidden break/exponent claim present")
    if raw.get("amazon_bedrock") not in (None, "NOT SELECTED"):
        # allow missing but if present must be NOT SELECTED
        if raw.get("amazon_bedrock") != "NOT SELECTED":
            errs.append("amazon_bedrock not NOT SELECTED")

    if stage == 0:
        for rel in ("stage0/preregistered-predictions.json", "stage0/worksheet-note.md"):
            if not (EXP_ROOT / rel).is_file():
                errs.append(f"missing freeze file {rel}")
        measured = {int(k): v for k, v in (raw.get("ord_n_of_2") or {}).items()}
        if measured != PREREG_ORD:
            errs.append(f"stage0 raw ord_n_of_2 mismatch: {measured}")
        if raw.get("preregistered_match") is not True and raw.get("outcome") != "O-ORD":
            errs.append("stage0 mismatch must yield O-ORD")
        if raw.get("preregistered_match") is True and raw.get("outcome") != "O-RELABEL-READY":
            errs.append("stage0 match must yield O-RELABEL-READY")
        prereg = json.loads((EXP_ROOT / "stage0/preregistered-predictions.json").read_text(encoding="utf-8"))
        if prereg.get("h1_prime_band_min_ratio") != 0.95:
            errs.append("prereg H1-PRIME band missing/wrong")
        if prereg.get("h2_removed") is not True:
            errs.append("prereg must record h2_removed true")

    if stage == 1:
        outcome = raw.get("outcome")
        if outcome not in ("O-RELABEL-READY", "O-ORD", "O-ARTIFACT", "O-IMPEDIMENT"):
            errs.append(f"bad stage1 outcome {outcome!r}")
        if outcome == "O-RELABEL-READY":
            for rel in ("stage1/fixture-B0.json", "stage1/curves-and-bases.json", "RESULTS.md"):
                if not (EXP_ROOT / rel).is_file():
                    errs.append(f"missing {rel}")
            fixture = raw.get("fixture_B0") or {}
            if fixture.get("pass") is not True:
                errs.append("O-RELABEL-READY requires fixture_B0.pass true")

    man = man_path.read_text(encoding="utf-8")
    if "experiment_id" not in man and "EXP-BINSTD-372679" not in man:
        errs.append("manifest missing experiment id")
    # Prefer top-level run: key when present
    if "run:" not in man and "schema:" not in man:
        errs.append("manifest missing run:/schema:")

    if errs:
        print("FAIL:", *errs, sep="\n  ")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
