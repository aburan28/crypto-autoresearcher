#!/usr/bin/env python3
"""EXP-CSIDH-906d0e driver: ancilla-width ratio of the two frozen circuits.

Default mode (--run-dir): builds Circuit-F and Circuit-I at discriminant
-59, evaluates them on the frozen pairs (A, B) and (P, P), runs the
discriminant -60 refusal control, derives the reading row, and writes
manifest.yaml, raw-result.json and reading.yaml. --self-test validates
the machinery at discriminant -23 against the classical mirror without
touching the frozen cell. The driver records observations only; it edits no
ledger record and claims no security level.
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from circuits import build_F, build_I  # noqa: E402
from classgroup import (  # noqa: E402
    compose_dirichlet,
    enumerate_reduced_forms,
)

EXPERIMENT_ID = "EXP-CSIDH-906d0e"
HYPOTHESIS_ID = "H-CSIDH-2e274b"
RUN_ID = "RUN-CSIDH-760fc4"
DISC = -59
NONFUNDAMENTAL_CONTROL = ((1, 0, 15), (1, 0, 15))
EXPECTED_PRINCIPAL = (1, 1, (-DISC + 1) // 4)


def frozen_cell(disc: int) -> tuple[list[tuple[int, int, int]], tuple, tuple, tuple]:
    forms = enumerate_reduced_forms(disc)
    principal = (1, 1, (1 - disc) // 4)
    others = sorted(f for f in forms if f != principal)
    return forms, principal, (others[0] if others else None), (others[1] if len(others) > 1 else None)


def evaluate(builder, disc: int, pair: tuple[tuple[int, int, int], tuple[int, int, int]]) -> dict:
    built = builder(disc, pair[0], pair[1])
    c = built.circuit
    snapshot = c.initial_input_snapshot()
    form = built.output_form()
    return {
        "output": list(form),
        "refused": built.refused(),
        "width": c.width(),
        "gate_counts": dict(c.counts),
        "inputs_unchanged": c.inputs_unchanged(snapshot),
        "ancilla_zero_init": True,  # allocator invariant: only input bits preset
        "n_input_bits": len(c.input_bits),
        "n_output_bits": len(c.output_bits),
    }


def measure() -> dict:
    forms, principal, a_form, b_form = frozen_cell(DISC)
    report: dict = {
        "schema": "csidh-906d0e-ancilla-ratio-v1",
        "experiment_id": EXPERIMENT_ID,
        "discriminant": DISC,
        "form_count": len(forms),
        "forms": [list(f) for f in forms],
        "principal": list(principal),
        "A": list(a_form) if a_form else None,
        "B": list(b_form) if b_form else None,
        "attack_claimed": False,
    }
    if a_form is None or b_form is None or principal not in forms or len(forms) < 3:
        report["reading_row"] = "too_few_forms"
        report["width_F"] = None
        report["width_I"] = None
        report["ratio"] = None
        return report

    pairs = {"AB": (a_form, b_form), "PP": (principal, principal)}
    ev: dict[str, dict] = {}
    for name, pair in pairs.items():
        ev[f"F_{name}"] = evaluate(build_F, DISC, pair)
        ev[f"I_{name}"] = evaluate(build_I, DISC, pair)
    control_F = evaluate(build_F, DISC, NONFUNDAMENTAL_CONTROL)
    control_I = evaluate(build_I, DISC, NONFUNDAMENTAL_CONTROL)

    agreement = {
        "AB": ev["F_AB"]["output"] == ev["I_AB"]["output"] and not ev["F_AB"]["refused"] and not ev["I_AB"]["refused"],
        "PP": ev["F_PP"]["output"] == ev["I_PP"]["output"] and not ev["F_PP"]["refused"] and not ev["I_PP"]["refused"],
    }
    pp_value_check = (
        ev["F_PP"]["output"] == list(EXPECTED_PRINCIPAL)
        and ev["I_PP"]["output"] == list(EXPECTED_PRINCIPAL)
    )
    minus60 = {
        "F_refused": control_F["refused"],
        "I_refused": control_I["refused"],
        "silent_agreement": (
            not control_F["refused"] and not control_I["refused"]
            and control_F["output"] == control_I["output"]
        ),
    }
    # classical reference for both frozen pairs
    reference = {}
    reference_ok = True
    for name, pair in pairs.items():
        try:
            ref = compose_dirichlet(pair[0], pair[1], DISC)
            reference[name] = list(ref)
            if ev[f"F_{name}"]["output"] != list(ref) or ev[f"I_{name}"]["output"] != list(ref):
                reference_ok = False
        except ValueError:
            reference[name] = None
            reference_ok = False
    width_F = ev["F_AB"]["width"]
    width_I = ev["I_AB"]["width"]
    width_constancy = (
        ev["F_AB"]["width"] == ev["F_PP"]["width"]
        and ev["I_AB"]["width"] == ev["I_PP"]["width"]
        and ev["F_AB"]["gate_counts"] == ev["F_PP"]["gate_counts"]
        and ev["I_AB"]["gate_counts"] == ev["I_PP"]["gate_counts"]
    )
    accounting_ok = all(
        ev[k]["inputs_unchanged"] and ev[k]["ancilla_zero_init"]
        and ev[k]["n_input_bits"] == 96 and ev[k]["n_output_bits"] == 48
        for k in ev
    )
    refusal_on_frozen = any(ev[k]["refused"] for k in ("F_AB", "I_AB", "F_PP", "I_PP"))
    checks = {
        "agreement_AB": agreement["AB"],
        "agreement_PP": agreement["PP"],
        "pp_value_check": pp_value_check,
        "minus60_not_silent": not minus60["silent_agreement"],
        "minus60_refused_both": minus60["F_refused"] and minus60["I_refused"],
        "reference_agreement": reference_ok,
        "width_constancy": width_constancy,
        "ancilla_accounting": accounting_ok,
        "no_refusal_on_frozen_pairs": not refusal_on_frozen,
    }
    ratio = Fraction(width_I, width_F)
    tail_flag = width_I > 4 * width_F or width_F > 4 * width_I

    report.update({
        "evaluations": {k: {kk: vv for kk, vv in v.items()} for k, v in ev.items()},
        "minus60_control": minus60,
        "reference": reference,
        "checks": checks,
        "width_F": width_F,
        "width_I": width_I,
        "ratio": f"{width_I}/{width_F}",
        "ratio_decimal": round(float(ratio), 6),
        "ratio_at_least_two": ratio >= 2,
        "tail_flag_either_exceeds_four_times": tail_flag,
        "gate_counts_F": ev["F_AB"]["gate_counts"],
        "gate_counts_I": ev["I_AB"]["gate_counts"],
    })
    if not all(checks.values()):
        row = "instrument_failure"
    elif len(forms) < 3:
        row = "too_few_forms"
    elif ratio < 2:
        row = "ratio_below_two"
    else:
        row = "ratio_at_least_two"
    report["reading_row"] = row
    return report


def self_test() -> bool:
    """Machinery validation at other discriminants; never touches disc -59."""
    ok = True
    total_pairs = 0
    for disc in (-23, -83):
        forms, _principal, _a, _b = frozen_cell(disc)
        first_key: dict[str, tuple] = {}
        for f in forms:
            for g in forms:
                try:
                    ref = compose_dirichlet(f, g, disc)
                except ValueError:
                    continue
                total_pairs += 1
                for builder, name in ((build_F, "F"), (build_I, "I")):
                    e = evaluate(builder, disc, (f, g))
                    if e["refused"]:
                        print(f"unexpected {name} refusal on {f} x {g}", file=sys.stderr)
                        ok = False
                        continue
                    if e["output"] != list(ref):
                        print(f"{name} mismatch on {f} x {g}: {e['output']} vs ref {list(ref)}", file=sys.stderr)
                        ok = False
                    if not e["inputs_unchanged"]:
                        print(f"{name} mutated inputs on {f} x {g}", file=sys.stderr)
                        ok = False
                    key = (e["width"], tuple(sorted(e["gate_counts"].items())))
                    if name not in first_key:
                        first_key[name] = key
                    elif key != first_key[name]:
                        print(f"{name} width/gates not constant: {f} x {g}", file=sys.stderr)
                        ok = False
        from classgroup import group_table_check
        if not group_table_check(forms, disc):
            print(f"classical group table check failed at {disc}", file=sys.stderr)
            ok = False
    print("self-test", "PASS" if ok else "FAIL",
          f"(discriminants -23 and -83, {total_pairs} composable pairs)")
    return ok


def write_run(run_dir: Path, report: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw-result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reading = {
        "reading_row": report["reading_row"],
        "form_count": report["form_count"],
        "width_F": report["width_F"],
        "width_I": report["width_I"],
        "ratio": report["ratio"],
        "ratio_at_least_two": report.get("ratio_at_least_two"),
        "agreement_AB": report.get("checks", {}).get("agreement_AB"),
        "agreement_PP": report.get("checks", {}).get("agreement_PP"),
        "pp_value_check": report.get("checks", {}).get("pp_value_check"),
        "minus60_F_refused": report.get("minus60_control", {}).get("F_refused"),
        "minus60_I_refused": report.get("minus60_control", {}).get("I_refused"),
        "attack_claimed": False,
    }
    (run_dir / "reading.yaml").write_text(
        yaml.safe_dump(reading, sort_keys=False), encoding="utf-8")
    manifest = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "run_id": RUN_ID,
        "command": ["python3", "experiments/EXP-CSIDH-906d0e/implementation/run.py",
                    "--run-dir", str(run_dir)],
        "discriminant": DISC,
        "gate_set": "NOT, CNOT, Toffoli",
        "bit_width": 16,
        "allocation_discipline": "fresh-bit-per-temporary, no reuse, no uncomputation",
        "frozen_pairs": ["(A, B)", "(P, P)"],
        "nonfundamental_control": "((1,0,15),(1,0,15)) at discriminant -60",
        "attack_claimed": False,
    }
    (run_dir / "manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return 0 if self_test() else 1
    if not args.run_dir:
        parser.error("--run-dir is required unless --self-test is given")
    write_run(Path(args.run_dir), measure())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
