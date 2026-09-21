#!/usr/bin/env python3
"""AM-1 self-consistency pass for PA-ECDLP-6ac801-v2-to-v3-r2.

Five mechanical checks named by DEC-20260907-de6b71 carried item 3.
Reads the live revision files. Writes am1_report.json beside this script.
Does not approve, freeze, or execute anything.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
SPEC = REPO / "experiments/EXP-ECDLP-6ac801/specification.v3.yaml"
AMEND = REPO / "experiments/EXP-ECDLP-6ac801/amendments/v2_to_v3.yaml"
INSTR = REPO / "experiments/EXP-ECDLP-612fb1/source_v2/instrument.py"
OUT = Path(__file__).with_name("am1_report.json")

CONTROLS_11 = ["a", "b", "d", "e", "f", "g", "h", "i", "k", "l", "m"]
SELF_LETTERS = ["c", "o"]
DIAG_LETTERS = ["j", "n"]
SELF_PREDICATES = ["c", "o1", "o2", "o3"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load() -> tuple[dict, dict]:
    spec = yaml.safe_load(SPEC.read_text())
    amend = yaml.safe_load(AMEND.read_text())
    return spec["experiment"]["v3_r2_addendum"], amend["protocol_amendment"]["v3_r2_addendum"]


def check_item_set(spec_add: dict, amend_add: dict) -> dict:
    items = amend_add["control_falsifiability_r2"]["items"]
    letters = [it["spec_letter"] for it in items]
    kinds = {it["spec_letter"]: it["kind"] for it in items}
    controls = [L for L, k in kinds.items() if k == "control"]
    selfs = [L for L, k in kinds.items() if k == "structural self-check"]
    diags = [L for L, k in kinds.items() if k == "diagnostic"]
    ok = (
        letters == list("abcdefghijklmno")
        and controls == CONTROLS_11
        and selfs == SELF_LETTERS
        and diags == DIAG_LETTERS
    )
    return {
        "name": "item-set identity",
        "pass": ok,
        "letters": letters,
        "controls": controls,
        "self_check_letters": selfs,
        "diagnostic_letters": diags,
    }


def check_partition(amend_add: dict) -> dict:
    items = amend_add["control_falsifiability_r2"]["items"]
    n = len(items)
    n_ctrl = sum(1 for it in items if it["kind"] == "control")
    n_self = sum(1 for it in items if it["kind"] == "structural self-check")
    n_diag = sum(1 for it in items if it["kind"] == "diagnostic")
    letter_ok = n == 15 and n_ctrl + n_self + n_diag == 15 and (n_ctrl, n_self, n_diag) == (11, 2, 2)
    pred_ok = n_ctrl + len(SELF_PREDICATES) + n_diag == 17
    return {
        "name": "partition arithmetic",
        "pass": letter_ok and pred_ok,
        "letter_partition": {"n": n, "controls": n_ctrl, "self_check_letters": n_self, "diagnostics": n_diag},
        "predicate_partition": {
            "controls": n_ctrl,
            "self_check_predicates": len(SELF_PREDICATES),
            "diagnostics": n_diag,
            "total": n_ctrl + len(SELF_PREDICATES) + n_diag,
        },
    }


def check_quantifier(spec_add: dict) -> dict:
    arts = spec_add["required_artifacts_r2"]
    joined = "\n".join(arts)
    names_eleven = all(f"({L})" in arts[0] for L in CONTROLS_11)
    forbidden_in_control_report = all(f"({L})" not in arts[0].split("MUST NOT")[0] or L in CONTROLS_11 for L in "c j n o".split())
    has_self = "SELF-CHECK REPORT" in arts[1] and all(p in arts[1] for p in ("(c)", "(o1)", "(o2)", "(o3)"))
    has_diag = "DIAGNOSTIC REPORT" in arts[2] and "(j)" in arts[2] and "(n)" in arts[2]
    no_fired_for_self_diag = "FIRED or NOT FIRED" not in arts[1] and "FIRED or NOT FIRED" not in arts[2]
    return {
        "name": "quantifier range",
        "pass": names_eleven and has_self and has_diag and no_fired_for_self_diag and "MUST NOT appear" in arts[0],
        "control_report_names_eleven": names_eleven,
        "self_check_entry_present": has_self,
        "diagnostic_entry_present": has_diag,
        "fired_status_confined_to_controls": no_fired_for_self_diag,
        "forbidden_note": forbidden_in_control_report,
        "n_artifact_entries": len(arts),
        "joined_len": len(joined),
    }


def check_xref(spec_add: dict, amend_add: dict) -> dict:
    spec_table = spec_add["cr1_condition_table"]
    amend_table = amend_add["cr1_conditions_operative"]
    expected = {
        "COND-1": "second arm",
        "COND-2": "success_criterion",
        "COND-3": "control (e)",
        "COND-4": "blind_rederivation",
    }
    spec_ok = all(any(tok in spec_table[k] for tok in v.split()) for k, v in expected.items())
    # looser: key presence and quoted_from on all four
    amend_ok = (
        set(amend_table) == set(expected)
        and all("condition_quoted_from" in amend_table[k] for k in expected)
        and "success_criterion" in amend_table["COND-2"]["requirement"]
        and "control (e)" in amend_table["COND-3"]["requirement"]
        and "blind_rederivation" in amend_table["COND-4"]["requirement"]
    )
    return {
        "name": "cross-reference resolution",
        "pass": spec_ok and amend_ok,
        "spec_table": spec_table,
        "amend_quoted_from": {k: amend_table[k]["condition_quoted_from"] for k in expected},
    }


def check_pointer() -> dict:
    text = INSTR.read_text().splitlines()
    line81 = text[80] if len(text) >= 81 else ""
    line84 = text[83] if len(text) >= 84 else ""
    k_on_81 = "self.K = mix64_int(0x9E3779B97F4A7C15 + self.seed)" in line81
    bits_on_84 = "self.bits_entry" in line84
    return {
        "name": "pointer freshness",
        "pass": k_on_81 and bits_on_84,
        "instrument_line_81": line81.strip(),
        "instrument_line_84": line84.strip(),
        "k_is_line_81": k_on_81,
        "bits_entry_is_line_84": bits_on_84,
    }


def main() -> int:
    spec_add, amend_add = load()
    checks = [
        check_item_set(spec_add, amend_add),
        check_partition(amend_add),
        check_quantifier(spec_add),
        check_xref(spec_add, amend_add),
        check_pointer(),
    ]
    report = {
        "task_id": "TASK-20260907-b1b54b",
        "batch_id": "BATCH-d7e987",
        "revision_id": "PA-ECDLP-6ac801-v2-to-v3-r2",
        "spec_sha256": sha256(SPEC),
        "amendment_sha256": sha256(AMEND),
        "instrument_sha256": sha256(INSTR),
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "n_checks": len(checks),
        "asserts_nothing_about": "the ECDLP; this is a document-consistency pass",
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"all_pass": report["all_pass"], "checks": [c["name"] for c in checks if c["pass"]]}, indent=2))
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
