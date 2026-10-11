#!/usr/bin/env python3
"""Independent checker for EXP-CSIDH-f3c102 run artifacts.

Re-derives the reading row from raw-result.json, recomputes the truncation
sum and the interval deterministically, re-runs both enumerations, and
validates the manifest. Reads only; writes nothing.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qforms import (  # noqa: E402
    enumerate_orbits,
    enumerate_reduced,
    is_fundamental,
    kronecker,
    nearest_integer_gates,
)

DISC = -83
N_TERMS = 30
A_MAX = 40
C_MAX = 400
ROWS = ("instrument_failure", "match", "mismatch")


def _frac(text: str) -> Fraction:
    num, den = text.split("/")
    return Fraction(int(num), int(den))


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: check.py <run_dir>", file=sys.stderr)
        return 2
    run_dir = Path(argv[0])
    errs: list[str] = []
    try:
        raw = json.loads((run_dir / "raw-result.json").read_text(encoding="utf-8"))
        reading = yaml.safe_load((run_dir / "reading.yaml").read_text(encoding="utf-8"))
        manifest = yaml.safe_load((run_dir / "manifest.yaml").read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"unreadable artifacts: {error}", file=sys.stderr)
        return 1

    if raw.get("experiment_id") != "EXP-CSIDH-f3c102":
        errs.append("wrong experiment id in raw-result")
    if manifest.get("experiment_id") != "EXP-CSIDH-f3c102":
        errs.append("wrong experiment id in manifest")
    if manifest.get("run_id") != "RUN-CSIDH-9d743d":
        errs.append("wrong run id in manifest")
    if raw.get("terms") != N_TERMS or raw.get("discriminant") != DISC:
        errs.append("frozen cell mismatch (discriminant or term count)")
    if raw.get("attack_claimed") is not False or reading.get("attack_claimed") is not False:
        errs.append("attack_claimed must be false")

    # recompute the truncation and the interval deterministically
    from run import s_interval, truncated_sum
    l30, chi_values = truncated_sum(DISC, N_TERMS)
    lo, hi, _ls, _hs = s_interval(l30)
    recorded_l30 = raw.get("L30") or {}
    if recorded_l30.get("numerator") != l30.numerator or recorded_l30.get("denominator") != l30.denominator:
        errs.append("recomputed L30 disagrees with the recorded value")
    if raw.get("chi_values") != chi_values:
        errs.append("recomputed chi values disagree")
    interval = raw.get("interval") or {}
    try:
        rlo, rhi = _frac(interval["lo"]), _frac(interval["hi"])
    except (KeyError, ValueError):
        errs.append("interval not recorded as fractions")
        rlo = rhi = Fraction(0)
    if (rlo, rhi) != (lo, hi):
        errs.append("recomputed interval disagrees with the recorded interval")
    status, r = nearest_integer_gates(lo, hi)
    if raw.get("gate_status") != status or raw.get("r") != r:
        errs.append("recomputed gate status or r disagrees")

    # re-run both enumerations
    e1 = enumerate_reduced(DISC)
    e2 = enumerate_orbits(DISC, A_MAX, C_MAX)
    agree = sorted(e1) == sorted(e2)
    h = len(e1) if agree else None
    if raw.get("h") != h:
        errs.append("recomputed form count disagrees")
    if raw.get("controls", {}).get("enumerations_agree") is not agree:
        errs.append("enumeration agreement bit disagrees")
    if not is_fundamental(DISC) or is_fundamental(-332) or not is_fundamental(-84):
        errs.append("discriminator state is wrong for the frozen cell")
    if kronecker(DISC, 1) != 1:
        errs.append("chi(1) must be 1")

    # re-derive the reading row from the recorded fields only
    checks = raw.get("controls") or {}
    required = ("minus83_fundamental", "minus332_nonfundamental",
                "minus84_fundamental_selfcheck", "enumerations_agree",
                "chi1_equals_1", "l30_is_reduced_fraction",
                "kronecker_implementations_agree")
    for key in required:
        if key not in checks:
            errs.append(f"missing control {key}")
    if not all(bool(checks.get(k)) for k in required) or status != "ok":
        expected = "instrument_failure"
    elif r == h:
        expected = "match"
    else:
        expected = "mismatch"
    if raw.get("reading_row") != expected:
        errs.append(f"row must be {expected}, recorded {raw.get('reading_row')}")
    if raw.get("reading_row") not in ROWS:
        errs.append("unknown reading row")
    if reading.get("reading_row") != raw.get("reading_row"):
        errs.append("reading.yaml disagrees with raw-result row")
    if raw.get("reading_row") in ("match", "mismatch"):
        if raw.get("absolute_difference") != abs(r - h):
            errs.append("absolute difference inconsistent")
    if bool(raw.get("interval_length_below_half")) is not ((hi - lo) < Fraction(1, 2)):
        errs.append("interval length flag inconsistent")

    for e in errs:
        print(e, file=sys.stderr)
    if not errs:
        print(f"check ok: row {raw.get('reading_row')}, gate {status}, r {r}, h {h}")
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
