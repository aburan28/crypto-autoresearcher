#!/usr/bin/env python3
"""Independent checker for EXP-CSIDH-906d0e run artifacts.

Re-derives the reading row from raw-result.json, rebuilds both frozen
circuits at discriminant -59 to verify the recorded widths and gate counts,
and validates the manifest. Reads only; writes nothing.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from circuits import build_F, build_I  # noqa: E402

DISC = -59
ROWS = ("instrument_failure", "too_few_forms", "ratio_below_two", "ratio_at_least_two")


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

    if raw.get("experiment_id") != "EXP-CSIDH-906d0e":
        errs.append("wrong experiment id in raw-result")
    if manifest.get("experiment_id") != "EXP-CSIDH-906d0e":
        errs.append("wrong experiment id in manifest")
    if manifest.get("run_id") != "RUN-CSIDH-760fc4":
        errs.append("wrong run id in manifest")
    if raw.get("attack_claimed") is not False or reading.get("attack_claimed") is not False:
        errs.append("attack_claimed must be false")

    form_count = raw.get("form_count")
    if form_count is None or form_count < 3:
        if raw.get("reading_row") != "too_few_forms":
            errs.append("form_count below 3 must read too_few_forms")
        _finish(errs, reading, raw)
        return 1 if errs else 0

    checks = raw.get("checks") or {}
    required = ("agreement_AB", "agreement_PP", "pp_value_check", "minus60_not_silent",
                "minus60_refused_both", "reference_agreement", "width_constancy",
                "ancilla_accounting", "no_refusal_on_frozen_pairs")
    for key in required:
        if key not in checks:
            errs.append(f"missing check {key}")
    width_F, width_I = raw.get("width_F"), raw.get("width_I")
    if not isinstance(width_F, int) or not isinstance(width_I, int) or width_F <= 0 or width_I <= 0:
        errs.append("widths must be positive integers")
        _finish(errs, reading, raw)
        return 1
    ratio = Fraction(width_I, width_F)

    # re-derive the reading row from the recorded fields only
    if not all(bool(checks.get(k)) for k in required):
        expected = "instrument_failure"
    elif ratio < 2:
        expected = "ratio_below_two"
    else:
        expected = "ratio_at_least_two"
    if raw.get("reading_row") != expected:
        errs.append(f"row must be {expected}, recorded {raw.get('reading_row')}")
    if reading.get("reading_row") != raw.get("reading_row"):
        errs.append("reading.yaml disagrees with raw-result row")
    if reading.get("width_F") != width_F or reading.get("width_I") != width_I:
        errs.append("reading.yaml widths disagree")
    if raw.get("ratio") != f"{width_I}/{width_F}":
        errs.append("ratio string inconsistent with widths")
    if bool(raw.get("ratio_at_least_two")) != (ratio >= 2):
        errs.append("ratio_at_least_two inconsistent")

    # rebuild the two frozen circuits and verify the recorded widths and gates
    a_form = tuple(raw["A"])
    b_form = tuple(raw["B"])
    rebuilt = {}
    for builder, name in ((build_F, "F"), (build_I, "I")):
        built = builder(DISC, a_form, b_form)
        rebuilt[name] = {
            "width": built.circuit.width(),
            "gate_counts": dict(built.circuit.counts),
        }
    if rebuilt["F"]["width"] != width_F or rebuilt["I"]["width"] != width_I:
        errs.append("rebuilt widths disagree with recorded widths")
    if rebuilt["F"]["gate_counts"] != raw.get("gate_counts_F"):
        errs.append("rebuilt Circuit-F gate counts disagree")
    if rebuilt["I"]["gate_counts"] != raw.get("gate_counts_I"):
        errs.append("rebuilt Circuit-I gate counts disagree")
    if rebuilt["F"]["width"] == rebuilt["I"]["width"]:
        errs.append("identical widths are suspicious for distinct circuits")

    _finish(errs, reading, raw)
    return 1 if errs else 0


def _finish(errs: list[str], reading: dict, raw: dict) -> None:
    for e in errs:
        print(e, file=sys.stderr)
    if not errs:
        print(f"check ok: row {raw.get('reading_row')}, "
              f"width_F {raw.get('width_F')}, width_I {raw.get('width_I')}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
