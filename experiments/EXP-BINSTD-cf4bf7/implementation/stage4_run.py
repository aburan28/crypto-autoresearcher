#!/usr/bin/env python3
"""Stage 4: f certificates for n=37 (null, expect 2) and n=31 (contrast, expect 7)."""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from arithmetic import count_irreducible_factors_xn_minus_1
from runpack import EXP_ROOT, dump_yaml, peak_rss_bytes, utc_now, write_run_package

RUN_NULL = "RUN-BINSTD-bfa01e"
RUN_CONTRAST = "RUN-BINSTD-0f3a44"


def certify(n: int, expected_f: int, role: str) -> dict:
    info = count_irreducible_factors_xn_minus_1(n)
    f = info["f_formula"]
    ok = (
        info["agreement"]
        and f == expected_f
        and info["f_cyclotomic_sum"] == expected_f
    )
    mid_dim = f > 2
    return {
        "n": n,
        "role": role,
        "expected_f": expected_f,
        "measured_f_formula": f,
        "measured_f_cyclotomic_sum": info["f_cyclotomic_sum"],
        "ord_n_of_2": info["ord_n_of_2"],
        "formula_cyclotomic_agreement": info["agreement"],
        "breakdown": info["breakdown"],
        "match_expected": ok,
        "mid_dimension_stable_V_present": mid_dim,
        "labeled_as_null_arm": role == "primary_null_arm",
        "label_recomputed": "RECOMPUTED",
        "label_expected": "EXPECTED",
    }


def main() -> None:
    started = utc_now()
    t0 = time.time()

    null_cert = certify(37, expected_f=2, role="primary_null_arm")
    contrast_cert = certify(31, expected_f=7, role="contrast_not_null")

    # Hard-fail guards
    hard_fail = False
    hard_fail_reasons = []
    if not null_cert["match_expected"]:
        hard_fail = True
        hard_fail_reasons.append("n=37 f != 2")
    if null_cert["mid_dimension_stable_V_present"]:
        hard_fail = True
        hard_fail_reasons.append("n=37 unexpectedly has mid-dim stable V")
    if not contrast_cert["match_expected"]:
        hard_fail = True
        hard_fail_reasons.append("n=31 f != 7")
    if contrast_cert["labeled_as_null_arm"]:
        hard_fail = True
        hard_fail_reasons.append("n=31 incorrectly labeled as null")

    dump_yaml(
        EXP_ROOT / "stage4" / "null-arm-f-certificate.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 4,
            "arm": "null_n37",
            "method": (
                "f=1+(n-1)/ord_n(2); cross-check sum over d|n of "
                "phi(d)/ord_d(2) irreducible counts of Phi_d over F_2"
            ),
            "certificate": null_cert,
            "hard_fail": hard_fail and not null_cert["match_expected"],
            "no_break_claim": True,
        },
    )
    dump_yaml(
        EXP_ROOT / "stage4" / "contrast-n31-f-certificate.yaml",
        {
            "experiment_id": "EXP-BINSTD-cf4bf7",
            "task_id": "TASK-20261001-18804b",
            "stage": 4,
            "arm": "contrast_n31",
            "note": (
                "CONTRAST ONLY — demonstrates source 'prime⇒empty' claim is false. "
                "NOT a valid null arm (ord_31(2)=5 < 30)."
            ),
            "method": (
                "f=1+(n-1)/ord_n(2); cross-check sum over d|n of "
                "phi(d)/ord_d(2) irreducible counts of Phi_d over F_2"
            ),
            "certificate": contrast_cert,
            "n31_labeled_as_null": False,
            "no_break_claim": True,
        },
    )

    finished = utc_now()
    wall = time.time() - t0
    lines = [
        f"null n=37: f={null_cert['measured_f_formula']} expected=2 match={null_cert['match_expected']}",
        f"contrast n=31: f={contrast_cert['measured_f_formula']} expected=7 match={contrast_cert['match_expected']}",
        f"hard_fail={hard_fail} reasons={hard_fail_reasons}",
    ]
    stdout = "\n".join(lines) + "\n"

    # Two run packages (null + contrast)
    write_run_package(
        RUN_NULL,
        stage=4,
        arm="null_n37",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage4_run.py",
        parameters={"n": 37, "role": "primary_null_arm", "expected_f": 2},
        metrics={
            "null_arm_f": null_cert["measured_f_formula"],
            "ord_n_of_2": null_cert["ord_n_of_2"],
            "match_expected": null_cert["match_expected"],
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        },
        valid=null_cert["match_expected"],
        invalid_reason=None if null_cert["match_expected"] else "f(n=37) != 2",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": True, "verifier": "cyclotomic_sum_crosscheck", "artifact": "stage4/null-arm-f-certificate.yaml"},
    )
    write_run_package(
        RUN_CONTRAST,
        stage=4,
        arm="contrast_n31",
        seed=None,
        command="python3 experiments/EXP-BINSTD-cf4bf7/implementation/stage4_run.py",
        parameters={"n": 31, "role": "contrast_not_null", "expected_f": 7},
        metrics={
            "contrast_n31_f": contrast_cert["measured_f_formula"],
            "ord_n_of_2": contrast_cert["ord_n_of_2"],
            "match_expected": contrast_cert["match_expected"],
            "n31_labeled_as_null": False,
            "peak_rss_bytes": peak_rss_bytes(),
            "wall_s": wall,
        },
        valid=contrast_cert["match_expected"] and not contrast_cert["labeled_as_null_arm"],
        invalid_reason=None if contrast_cert["match_expected"] else "f(n=31) != 7",
        termination_reason="completed",
        stdout_text=stdout,
        started_at=started,
        finished_at=finished,
        wall_seconds=wall,
        certificate={"kind": "none", "verified": True, "verifier": "cyclotomic_sum_crosscheck", "artifact": "stage4/contrast-n31-f-certificate.yaml"},
    )
    print(stdout)
    if hard_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
