#!/usr/bin/env python3
"""Finalize Stage 1 (g=6 infra failure + summaries) and Stage 2 for EXP-BINSTD-842864.

Does not overwrite existing non-empty run packages. Observations only.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "EXP-BINSTD-842864"
sys.path.insert(0, str(EXP / "implementation"))

import exact_targets_g56 as et  # noqa: E402
from run_stages import load_census_json, run_cmd, write_run_package  # noqa: E402

IMPL = EXP / "implementation" / "exact_targets_g56.py"


def write_g6_unfiltered_failure() -> dict:
    ck_path = EXP / "stage1" / "census-g6-unfiltered.checkpoint.json"
    live = EXP / "stage1" / "census-g6-unfiltered.live.log"
    ck = json.loads(ck_path.read_text())
    # Mark as infrastructure stop under IMP-H1-runtime-g6 (projection >> 10× modeled hours)
    ck_out = dict(ck)
    ck_out["timed_out"] = True
    ck_out["partial"] = True
    ck_out["termination_reason"] = "failed_infrastructure"
    ck_out["infrastructure_class"] = "resource_exhaustion"
    ck_out["classes_known_lmfdb"] = 164937
    ck_out["unfiltered_matches_lmfdb"] = False
    ck_out["note"] = (
        "Stopped under IMP-H1-runtime-g6: after ~5.6e6 exact tests / ~3044s wall, "
        "only 99/164937 LMFDB classes found. Naive linear-in-classes projection "
        "~1377h >> 10× HEUR-H1 modeled 'hours' and advisory 86400s wall. "
        "NOT a mathematical exclusion / outcome A."
    )
    out_json = EXP / "stage1" / "census-g6-unfiltered.json"
    payload = {
        "base_field": 2,
        "modulus": 131,
        "filtered_only": False,
        "searches": [ck_out],
        "peak_rss_bytes": None,
        "loaded_from_checkpoint": str(ck_path),
    }
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    run_id = "RUN-BINSTD-69747c"
    cmd = [
        sys.executable,
        "-u",
        str(IMPL),
        "--mode",
        "census",
        "--dims",
        "6",
        "--modulus",
        "131",
        "--json",
        str(out_json),
        "--progress-every",
        "100000",
        "--wall-limit",
        "86400",
        "--checkpoint",
        str(ck_path),
    ]
    stdout = live.read_text() if live.exists() else ""
    stdout += (
        "\n[finalize] stopped under IMP-H1-runtime-g6; checkpoint preserved; "
        "status=failed_infrastructure (not outcome A).\n"
    )
    stderr = (
        "resource_exhaustion / IMP-H1-runtime-g6: projected wall-clock from partial "
        "progress (~99 classes in 3044s) far exceeds advisory 86400s and 10× HEUR-H1 hours.\n"
    )
    # Approximate timing from checkpoint wall + process start recorded in live log header if any
    t1 = time.time()
    t0 = t1 - float(ck.get("wall_s") or 0)
    write_run_package(
        run_id,
        "1-unfiltered-g6",
        cmd,
        payload,
        stdout,
        stderr,
        t0,
        t1,
        "failed_infrastructure",
        "timeout",
        {
            "dimension": 6,
            "unfiltered_class_count": ck.get("classes_found"),
            "expected_lmfdb": 164937,
            "unfiltered_matches_lmfdb": False,
            "filtered_hit_count": ck.get("hit_count"),
            "ambiguous_count": ck.get("ambiguous_count"),
            "exact_tests_performed": ck.get("exact_tests_performed"),
            "survivors_per_level": ck.get("survivors_per_level"),
            "wall_s": ck.get("wall_s"),
            "timed_out": True,
            "partial": True,
            "measured": True,
            "infrastructure_note": ck_out["note"],
        },
        "IMP-H1-runtime-g6: g=6 unfiltered projected >> advisory wall; partial checkpoint only",
    )
    return ck_out


def write_g6_filtered_not_launched() -> None:
    """Filtered g=6 shares levels 1..5 tree cost with unfiltered; not launched."""
    run_id = "RUN-BINSTD-eb2003"
    out_json = EXP / "stage1" / "census-g6-filtered.json"
    payload = {
        "base_field": 2,
        "modulus": 131,
        "filtered_only": True,
        "searches": [
            {
                "dimension": 6,
                "modulus": 131,
                "filtered_only": True,
                "classes_found": None,
                "hit_count": None,
                "hits": [],
                "ambiguous_count": None,
                "exact_tests_performed": 0,
                "survivors_per_level": None,
                "wall_s": 0.0,
                "timed_out": True,
                "partial": True,
                "termination_reason": "failed_infrastructure",
                "note": (
                    "Not launched: IMP-H1-runtime-g6. Filtered-only still explores "
                    "levels 1..5 fully; unfiltered partial already projected >>10× "
                    "HEUR-H1 hours. Not a mathematical exclusion."
                ),
            }
        ],
        "peak_rss_bytes": None,
        "not_launched": True,
    }
    out_json.write_text(json.dumps(payload, indent=2) + "\n")
    cmd = [
        sys.executable,
        "-u",
        str(IMPL),
        "--mode",
        "census",
        "--dims",
        "6",
        "--modulus",
        "131",
        "--filtered-only",
        "--json",
        str(out_json),
        "--wall-limit",
        "86400",
    ]
    t0 = t1 = time.time()
    write_run_package(
        run_id,
        "1-filtered-g6",
        cmd,
        payload,
        "not launched\n",
        payload["searches"][0]["note"] + "\n",
        t0,
        t1,
        "failed_infrastructure",
        "timeout",
        {
            "dimension": 6,
            "filtered_hit_count": None,
            "ambiguous_count": None,
            "exact_tests_performed": 0,
            "timed_out": True,
            "not_launched": True,
            "measured": False,
        },
        "IMP-H1-runtime-g6 blocked filtered g=6 launch after unfiltered projection",
    )


def write_stage1_summaries_and_sympy() -> None:
    run_id = "RUN-BINSTD-353c72"
    out_sample = EXP / "stage1" / "dual-box-sample.json"
    # Sample g=5 fully; g=6 sample is cheap (random vectors, not full census)
    cmd = [
        sys.executable,
        str(IMPL),
        "--mode",
        "sample",
        "--dims",
        "5",
        "6",
        "--sample-size",
        "10000",
        "--json",
        str(out_sample),
    ]
    t0 = time.time()
    rc, out, err, _ = run_cmd(cmd, timeout=3600)
    t1 = time.time()
    sample = json.loads(out_sample.read_text()) if out_sample.exists() else {}

    unfiltered_rows = []
    filtered_rows = []
    for g in (5, 6):
        up = EXP / "stage1" / f"census-g{g}-unfiltered.json"
        fp = EXP / "stage1" / f"census-g{g}-filtered.json"
        if up.exists():
            unfiltered_rows.append(json.loads(up.read_text())["searches"][0])
        if fp.exists():
            filtered_rows.append(json.loads(fp.read_text())["searches"][0])

    hits_by_key = {}
    for g in (5, 6):
        for path in (
            EXP / "stage1" / f"census-g{g}-filtered.json",
            EXP / "stage1" / f"census-g{g}-unfiltered.json",
        ):
            if not path.exists():
                continue
            for h in json.loads(path.read_text())["searches"][0].get("hits") or []:
                key = (h.get("points"), tuple(h.get("h") or []))
                prev = hits_by_key.get(key)
                if prev is None or ("sympy_agreement" in h and "sympy_agreement" not in (prev or {})):
                    hits_by_key[key] = h
    all_hits = list(hits_by_key.values())

    exact_targets = {
        "base_field": 2,
        "modulus": 131,
        "lmfdb_expected_unfiltered": {"5": 14325, "6": 164937},
        "searches": [],
        "g6_status": "failed_infrastructure_partial",
    }
    for u in unfiltered_rows:
        exact_targets["searches"].append(
            {
                "dimension": u.get("dimension"),
                "unfiltered_class_count": u.get("classes_found"),
                "unfiltered_matches_lmfdb": u.get("unfiltered_matches_lmfdb"),
                "candidates_tests": u.get("exact_tests_performed"),
                "survivors_per_level": u.get("survivors_per_level"),
                "weil_polynomials_found": [
                    {
                        "points": h.get("points"),
                        "h": h.get("h"),
                        "P": h.get("P"),
                        "N_r": h.get("N_r"),
                        "a_r": h.get("a_r"),
                        "all_a_r_nonnegative": h.get("all_a_r_nonnegative"),
                        "jacobian_sufficiency_claimed": False,
                        "sympy_agreement": h.get("sympy_agreement"),
                    }
                    for h in (u.get("hits") or [])
                ],
                "ambiguous_near_boundary": u.get("ambiguous_near_boundary"),
                "ambiguous_count": u.get("ambiguous_count"),
                "wall_s": u.get("wall_s"),
                "termination_reason": u.get("termination_reason"),
                "timed_out": u.get("timed_out"),
                "partial": u.get("partial"),
            }
        )
    (EXP / "stage1" / "exact_targets_g56.json").write_text(json.dumps(exact_targets, indent=2) + "\n")

    lines = []
    for u in unfiltered_rows:
        lines.append(
            "  - dimension: {d}\n    classes_found: {c}\n    matches_lmfdb: {m}\n"
            "    ambiguous_count: {a}\n    exact_tests: {t}\n    wall_s: {w}\n"
            "    termination_reason: {tr}\n    timed_out: {to}\n    partial: {p}".format(
                d=u.get("dimension"),
                c=u.get("classes_found"),
                m=u.get("unfiltered_matches_lmfdb"),
                a=u.get("ambiguous_count"),
                t=u.get("exact_tests_performed"),
                w=u.get("wall_s"),
                tr=u.get("termination_reason"),
                to=u.get("timed_out"),
                p=u.get("partial"),
            )
        )
    (EXP / "stage1" / "unfiltered-counts.yaml").write_text(
        f"""# Stage 1 unfiltered counts — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
expected_lmfdb: {{5: 14325, 6: 164937}}
observed:
{os.linesep.join(lines)}
g6_note: >-
  g=6 unfiltered stopped under IMP-H1-runtime-g6 (failed_infrastructure).
  Partial: 99 classes after ~5.6e6 tests / ~3044s; NOT outcome A / exclusion.
measured: true
modeled_H1_runtime_prior: 'minutes g=5 / hours g=6 — not a measured column'
"""
    )

    filt_summaries = []
    for f in filtered_rows:
        filt_summaries.append(
            {
                "dimension": f.get("dimension"),
                "hit_count": f.get("hit_count"),
                "ambiguous_count": f.get("ambiguous_count"),
                "exact_tests": f.get("exact_tests_performed"),
                "wall_s": f.get("wall_s"),
                "termination_reason": f.get("termination_reason"),
                "timed_out": f.get("timed_out"),
                "not_launched": f.get("note") is not None and f.get("exact_tests_performed") == 0,
            }
        )
    (EXP / "stage1" / "filtered-hits.yaml").write_text(
        f"""# Stage 1 filtered hits modulus 131 — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
modulus: 131
filtered_pass_summaries: {json.dumps(filt_summaries)}
hit_count_total_completed_dims: {len(all_hits)}
hits: {json.dumps(all_hits)}
jacobian_note: >-
  all_a_r_nonnegative is a necessary screen only; never upgraded to 'is a Jacobian'.
g6_filtered_note: >-
  g=6 filtered not launched (IMP-H1-runtime-g6); g=5 filtered completed with 24 hits.
measured: true
"""
    )

    sympy_doc = {
        "dual_box_sample": sample,
        "hit_reverification": [
            {
                "points": h.get("points"),
                "h": h.get("h"),
                "sympy_agreement": h.get("sympy_agreement"),
                "sympy_verdict": h.get("sympy_verdict"),
                "integer_sturm_verdict": h.get("integer_sturm_verdict"),
            }
            for h in all_hits
        ],
        "all_hits_agree": all(h.get("sympy_agreement") for h in all_hits) if all_hits else True,
        "sample_all_agree": all(s.get("all_agree") for s in sample.get("samples", [])),
        "scope_note": "Hit re-verify covers completed g=5 hits only; g=6 census incomplete.",
    }
    (EXP / "stage1" / "sympy-reverification.yaml").write_text(
        f"""# Stage 1 sympy re-verification — EXP-BINSTD-842864
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
{json.dumps(sympy_doc, indent=2)}
"""
    )
    write_run_package(
        run_id,
        "1-sympy-reverify",
        cmd,
        sympy_doc,
        out,
        err,
        t0,
        t1,
        "completed_valid" if rc == 0 else "failed_infrastructure",
        "completed" if rc == 0 else "sample_failed",
        {
            "hit_count": len(all_hits),
            "all_hits_agree": sympy_doc["all_hits_agree"],
            "sample_all_agree": sympy_doc["sample_all_agree"],
        },
        None,
    )
    print("Stage 1 summaries + sympy written.", flush=True)


def run_stage2() -> None:
    run_id = "RUN-BINSTD-839c43"
    out_json = EXP / "stage2" / "nearby-object-controls-raw.json"
    cmd = [sys.executable, str(IMPL), "--mode", "controls", "--json", str(out_json)]
    t0 = time.time()
    rc, out, err, _ = run_cmd(cmd, timeout=86400)
    t1 = time.time()
    data = json.loads(out_json.read_text())
    (EXP / "stage2" / "nearby-object-controls.yaml").write_text(
        f"""# Stage 2 nearby-object controls — EXP-BINSTD-842864 / {run_id}
experiment_id: EXP-BINSTD-842864
run_id: {run_id}
mod5_g1: {json.dumps(data['mod5_g1'])}
mod1_identity:
  g1: {json.dumps(data['mod1_g1'])}
  g2: {json.dumps(data['mod1_g2'])}
  g3: {json.dumps(data['mod1_g3'])}
toy_ladder_moduli: [17, 19, 23, 29, 31, 37, 41]
toy_ladder: {json.dumps(data['toy_ladder'])}
hand_derived_expectations: {json.dumps(data['hand_derived_expectations'])}
surface_presence: {json.dumps(data['surface_presence'])}
surface_only_19_observed: {str(data['surface_only_19']).lower()}
controls_pass:
  mod5_finds_5_point: {str(data['mod5_g1']['must_find_5_point_class']).lower()}
  mod1_equals_unfiltered_g1: {str(data['mod1_g1']['hits_equal_unfiltered']).lower()}
  mod1_equals_unfiltered_g2: {str(data['mod1_g2']['hits_equal_unfiltered']).lower()}
  mod1_equals_unfiltered_g3: {str(data['mod1_g3']['hits_equal_unfiltered']).lower()}
measured: true
no_break_claim: true
"""
    )
    ok = (
        rc == 0
        and data["mod5_g1"]["must_find_5_point_class"]
        and data["mod1_g1"]["hits_equal_unfiltered"]
        and data["mod1_g2"]["hits_equal_unfiltered"]
        and data["mod1_g3"]["hits_equal_unfiltered"]
    )
    write_run_package(
        run_id,
        "2-nearby-object",
        cmd,
        data,
        out,
        err,
        t0,
        t1,
        "completed_valid" if ok else "invalid_measurement",
        "completed" if ok else "control_mismatch",
        {
            "mod5_ok": data["mod5_g1"]["must_find_5_point_class"],
            "mod1_ok": all(data[f"mod1_g{g}"]["hits_equal_unfiltered"] for g in (1, 2, 3)),
            "surface_only_19": data["surface_only_19"],
        },
        None if ok else "nearby-object control failure",
    )
    print("Stage 2 artifacts written.", flush=True)


def main() -> None:
    write_g6_unfiltered_failure()
    write_g6_filtered_not_launched()
    write_stage1_summaries_and_sympy()
    run_stage2()
    print("finalize_remaining done.", flush=True)


if __name__ == "__main__":
    main()
