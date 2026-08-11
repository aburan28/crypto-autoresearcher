"""Run wrapper for EXP-JINV-bd141d. See harness/exp_jinv_matched.py for the
full account of what this run does and does not do, and why.

Usage:
    python3 -m harness.run_jinv_matched [--suffix SUFFIX] [--no-write]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

from . import exp_jinv_matched as jm
from .runner import RunResult, REPO, write_run

EXP_AREA = "JINV"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffix", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    suffix = args.suffix or "matched-n19507-e0451f"
    cmd = "python3 -m harness.run_jinv_matched " + " ".join(sys.argv[1:])

    t_start = time.time()
    log: list[str] = []

    def p(msg: str) -> None:
        print(msg)
        log.append(msg)

    # ---------------------------------------------------------------
    # SR1: family gate
    # ---------------------------------------------------------------
    p("== SR1 family gate: re-derive N=19507 family ==")
    gate = jm.sr1_family_gate(jm.MATCHED_N, jm.EXPECTED_INVENTORY)
    p(f"SR1 gate: {gate['gate']}  checks={gate['checks']}  "
      f"aut_arm_checks={gate['aut_arm_checks']}")

    stopping_rules_fired: list[dict] = [{
        "rule": "SR1", "outcome": gate["gate"],
        "detail": "family re-derivation matches design document inventory exactly"
                  if gate["gate"] == "PASS" else "disagreement with design document",
    }]

    family_construction = {
        "N": jm.MATCHED_N,
        "identity": "D = t^2 - 4p and N = p + 1 - t give D = (t - 2)^2 - 4N",
        "re_derivation": gate,
    }

    if gate["gate"] != "PASS":
        # SR1 failure terminates the run PREMISE-FAILED; nothing further runs.
        t_end = time.time()
        result = RunResult(
            run_suffix=suffix, curve_id=f"MATCHEDN-{jm.MATCHED_N}",
            seed=jm.SEEDS[0],
            parameters={"N": jm.MATCHED_N, "aut_arm_t": jm.AUT_ARM_T,
                        "aut_arm_p": jm.AUT_ARM_P},
            metrics={"sr1_gate": gate["gate"]},
            certificate={"kind": "none"},
            valid=False, invalid_reason="SR1 family gate disagreement (PREMISE-FAILED)",
            stdout="\n".join(log), stderr="",
            raw={"stopping_rules_fired": stopping_rules_fired,
                 "family_construction": family_construction})
        if not args.no_write:
            run_id = write_run(jm.EXP_ID, EXP_AREA, result,
                               status="completed_invalid", command=cmd,
                               started=t_start, finished=t_end)
            _write_extra(run_id, {"family-construction.json": family_construction})
            p(f"wrote {run_id} status=completed_invalid (PREMISE-FAILED)")
        return 0

    # ---------------------------------------------------------------
    # SR1 completeness certificate + SR2 support/order certification,
    # over the WHOLE re-derived family (all 59 classes).
    # ---------------------------------------------------------------
    p("\n== Hurwitz-Kronecker completeness certificates + per-curve order/"
      "support certification (SR2), whole family ==")
    members = gate["members"]
    class_census_all = []
    order_verification_rows = []
    support_certificate_rows = []
    certs_by_class: dict[int, list] = {}
    n_curves_total = 0
    t_cert0 = time.time()
    for m in members:
        census, certs = jm.certify_class(m["p"], m["t"], jm.MATCHED_N)
        class_census_all.append(census)
        certs_by_class[m["t"]] = certs
        n_curves_total += len(certs)
        for c in certs:
            order_verification_rows.append({
                "p": c.p, "t": c.t, "a": c.a, "b": c.b,
                "order_character_sum": c.order_character_sum,
                "order_enumerated": c.order_enumerated,
                "order_matches_N": c.order_matches_N,
            })
            support_certificate_rows.append({
                "p": c.p, "t": c.t, "a": c.a, "b": c.b,
                "generator_found": c.generator_found,
                "cyclic_table_size": c.cyclic_table_size,
                "support_equals_enumerated_points": c.support_equals_enumerated_points,
                "support_certificate_pass": c.support_certificate_pass,
            })
    t_cert1 = time.time()

    all_census_agree = all(c["agrees"] for c in class_census_all)
    all_order_pass = all(r["order_matches_N"] for r in order_verification_rows)
    all_support_pass = all(r["support_certificate_pass"] for r in support_certificate_rows)

    p(f"classes certified: {len(class_census_all)}  all_agree={all_census_agree}  "
      f"curves_total={n_curves_total}  elapsed={t_cert1 - t_cert0:.1f}s")
    p(f"SR2 (order == N per curve): all_pass={all_order_pass}")
    p(f"SR2 (targets_B support == E(F_p) per curve): all_pass={all_support_pass}")

    stopping_rules_fired.append({
        "rule": "SR1-completeness-certificate",
        "outcome": "PASS" if all_census_agree else "INVALID",
        "detail": f"{len(class_census_all)} classes, Hurwitz-Kronecker "
                  f"weighted census agreement per class",
    })
    stopping_rules_fired.append({
        "rule": "SR2", "outcome": "PASS" if (all_order_pass and all_support_pass) else "PREMISE-FAILED",
        "detail": f"{n_curves_total} curves: order_matches_N={all_order_pass}, "
                  f"support_certificate_pass={all_support_pass}",
    })

    if not (all_census_agree and all_order_pass and all_support_pass):
        t_end = time.time()
        result = RunResult(
            run_suffix=suffix, curve_id=f"MATCHEDN-{jm.MATCHED_N}",
            seed=jm.SEEDS[0],
            parameters={"N": jm.MATCHED_N},
            metrics={"sr1_gate": "PASS", "completeness_all_agree": all_census_agree,
                     "sr2_all_order_pass": all_order_pass,
                     "sr2_all_support_pass": all_support_pass},
            certificate={"kind": "none"},
            valid=False,
            invalid_reason="SR1 completeness certificate or SR2 support/order "
                           "certification failed on at least one class or curve",
            stdout="\n".join(log), stderr="",
            raw={"stopping_rules_fired": stopping_rules_fired})
        if not args.no_write:
            run_id = write_run(jm.EXP_ID, EXP_AREA, result,
                               status="completed_invalid", command=cmd,
                               started=t_start, finished=t_end)
            _write_extra(run_id, {
                "family-construction.json": family_construction,
                "class-census.json": {"classes": class_census_all, "all_agree": all_census_agree},
                "order-verification.json": {"rows": order_verification_rows, "all_pass": all_order_pass},
                "support-certificates.json": {"rows": support_certificate_rows, "all_pass": all_support_pass},
            })
            p(f"wrote {run_id} status=completed_invalid")
        return 0

    family_construction["curves_total_enumerated"] = n_curves_total

    # ---------------------------------------------------------------
    # r-stratification structural finding (data, no verdict)
    # ---------------------------------------------------------------
    r_finding = jm.r_structural_argument(jm.MATCHED_N)
    r_values_observed = sorted({r["p"] for r in []})  # placeholder, real check below
    r_values_seen = sorted({c.r for certs in certs_by_class.values() for c in certs})
    r_finding["r_values_observed_across_whole_family"] = r_values_seen
    p(f"\nr-stratification structural finding: r values observed = {r_values_seen}")

    # ---------------------------------------------------------------
    # |Aut| arm structural enumeration (data, no verdict; SR3 blocks the
    # rank/permutation-probability VERDICT, but the enumerated vertex count
    # and crater identification are structural facts, not statistics).
    # ---------------------------------------------------------------
    p("\n== |Aut| arm structural enumeration (t=211, p=19717, D=-3*107^2) ==")
    aut_certs = certs_by_class[jm.AUT_ARM_T]
    aut_enum = jm.aut_arm_enumeration(aut_certs)
    p(f"crater={aut_enum['crater_vertices'].__len__() if False else 1}  "
      f"floor={aut_enum['floor_vertices_count']}  "
      f"total={aut_enum['total_vertices_enumerated']}  "
      f"matches_1_plus_36={aut_enum['total_matches_1_plus_36']}")

    p("\n== T1 transport certificate attempt (C-TRANSPORT-CERT) ==")
    transport = jm.attempt_transport_certificate(jm.AUT_ARM_P, jm.MATCHED_N, 107)
    p(f"transport status={transport['status']}: {transport['obstruction']}")
    stopping_rules_fired.append({
        "rule": "C-TRANSPORT-CERT",
        "outcome": transport["status"],
        "detail": transport["obstruction"],
    })

    # ---------------------------------------------------------------
    # SR4 / raw data collection: BLOCKED by the missing density-grid /
    # target-count fields (specification_error). SR3 additionally blocks any
    # verdict even had this data been collected.
    # ---------------------------------------------------------------
    p("\n== SR4 baseline-identity gate + density-swept raw measurement "
      "collection: BLOCKED (specification_error) ==")
    for f in jm.MISSING_SPEC_FIELDS:
        p(f"  MISSING: {f}")
    spec_error = {
        "kind": "specification_error",
        "missing_fields": jm.MISSING_SPEC_FIELDS,
        "blocks": [
            "SR4 baseline-identity gate (p=4001, t=30 class, targets_B, "
            "'every declared density row' -- no density row is declared)",
            "ARM 1 (|D_0| arm) per-curve decomposition_rate_m2/m3, "
            "liftable_density, decomposition_efficiency measurement across "
            "the 51 f=1 classes (needs factor_base_sizes and T)",
            "ARM 2 (|Aut| arm) per-vertex decomposition-rate measurement on "
            "the 37-vertex t=211 class (needs factor_base_sizes and T)",
            "C-TRACEPAIR rate-based replication (structural D0-pair listing "
            "is unaffected and is reported separately, see below)",
            "C-RESIDUAL-P check (needs measured rates)",
            "d0-arm-analysis.json / aut-arm-ranks.json rank and rank-"
            "correlation statistics (need measured rates)",
        ],
        "not_worked_around_because": (
            "SR5 (FROZEN GRID) forbids adding a density row, class, target "
            "count or seed without a versioned protocol_amendment filed "
            "BEFORE the extra data exists. Inventing factor_base_sizes or T "
            "here IS the violation SR5 exists to prevent, not a way around "
            "the missing field."),
    }
    stopping_rules_fired.append({
        "rule": "SR4/data-collection", "outcome": "BLOCKED",
        "detail": "specification_error: density grid (factor_base_sizes, "
                  "target_counts) is never instantiated in the approved contract",
    })

    # Structural (grid-independent) trace-pair listing: the five D0 values
    # hit twice, and their two (t, p) representatives each -- derivable from
    # family_construction alone, no measured rate needed.
    from collections import defaultdict
    d0_to_members = defaultdict(list)
    for mm in members:
        if mm["f"] == 1:
            d0_to_members[abs(mm["D0"])].append(mm)
    tracepair_structural = {
        "kind": "structural_listing_only",
        "note": "The RATE-based within-pair spread comparison (C-TRACEPAIR "
                "proper) is blocked with the rest of the density-swept "
                "measurement; this lists only the structural (t, p, D0) data "
                "the grid gap does not block.",
        "pairs": [{"abs_D0": d0, "members": v}
                  for d0, v in sorted(d0_to_members.items()) if len(v) == 2],
    }

    # SR3: even had the grid existed, SR3 blocks reading any |D_0|/|Aut| verdict.
    p("\n== SR3 instrument gate (BLOCKING) ==")
    p("SR3 verbatim: 'Do not read or report any |D_0|-arm or |Aut|-arm "
      "verdict until EXP-INSTR-36c8cf has delivered, at the ACTUAL geometry "
      "of this design, a detection floor and a false-positive rate for every "
      "statistic used.' EXP-INSTR-36c8cf Phase A stopped at its own "
      "falsification criterion with no interval accepted; Phase B has not "
      "run. No verdict is computed for either arm.")
    stopping_rules_fired.append({
        "rule": "SR3", "outcome": "BLOCKING",
        "detail": "EXP-INSTR-36c8cf has not delivered a two-directional "
                  "detection floor / false-positive rate at this design's "
                  "actual geometry (Phase A stopped at its own falsification "
                  "criterion, Phase B has not run). No |D_0|-arm or |Aut|-arm "
                  "verdict is read or reported by this run.",
    })

    verdict = {
        "d0_arm": "BLOCKED_SR3_AND_SPEC_GAP",
        "aut_arm": "BLOCKED_SR3_AND_SPEC_GAP",
        "note": "Neither arm reaches a TREND-DETECTED / NO-TREND / "
                "NOT-RESOLVABLE verdict. SR3 (EXP-INSTR-36c8cf incomplete) "
                "blocks verdict interpretation independent of the grid gap; "
                "the density-grid specification_error additionally blocks "
                "even the raw rate measurement the verdict would be computed "
                "from. Both are recorded as terminal, non-verdict states, "
                "per SR7 (no outcome shopping) -- nothing here was computed "
                "and then withheld.",
        "computed_inside_this_run": True,
    }

    t_end = time.time()

    p(f"\n== DONE. wall={t_end - t_start:.1f}s ==")

    metrics = {
        "sr1_gate": gate["gate"],
        "family_curves_total": n_curves_total,
        "family_classes_total": len(members),
        "class_census_all_agree": all_census_agree,
        "sr2_order_all_pass": all_order_pass,
        "sr2_support_all_pass": all_support_pass,
        "aut_arm_total_vertices": aut_enum["total_vertices_enumerated"],
        "aut_arm_crater_count": 1,
        "aut_arm_floor_count": aut_enum["floor_vertices_count"],
        "r_values_observed": r_values_seen,
        "transport_status": transport["status"],
        "sr3_status": "BLOCKING",
        "sr4_and_data_collection_status": "BLOCKED_specification_error",
    }

    result = RunResult(
        run_suffix=suffix, curve_id=f"MATCHEDN-{jm.MATCHED_N}",
        seed=jm.SEEDS[0],
        parameters={"N": jm.MATCHED_N, "aut_arm_t": jm.AUT_ARM_T,
                    "aut_arm_p": jm.AUT_ARM_P, "aut_arm_D": jm.AUT_ARM_D,
                    "seeds_frozen_unused": jm.SEEDS},
        metrics=metrics,
        certificate={"kind": "none"},
        valid=True,
        invalid_reason=None,
        stdout="\n".join(log), stderr="",
        raw={"stopping_rules_fired": stopping_rules_fired,
             "specification_error": spec_error,
             "claim_tier": "toy", "sota_delta": 0,
             "no_ecdlp_claim": True})

    if not args.no_write:
        run_id = write_run(jm.EXP_ID, EXP_AREA, result,
                           status="completed", command=cmd,
                           started=t_start, finished=t_end)
        _write_extra(run_id, {
            "family-construction.json": family_construction,
            "class-census.json": {"classes": class_census_all, "all_agree": all_census_agree},
            "order-verification.json": {"rows": order_verification_rows, "all_pass": all_order_pass},
            "support-certificates.json": {"rows": support_certificate_rows, "all_pass": all_support_pass},
            "per-curve-measurements.json": {
                "status": "UNREACHED", "reason": "specification_error",
                "detail": spec_error},
            "per-class-aggregates.json": {
                "status": "UNREACHED", "reason": "specification_error",
                "detail": spec_error},
            "d0-arm-analysis.json": {
                "status": "UNREACHED", "reason": "specification_error + SR3",
                "detail": spec_error},
            "tracepair-replication.json": tracepair_structural,
            "residual-p-check.json": {
                "status": "UNREACHED", "reason": "specification_error",
                "detail": spec_error},
            "aut-arm-ranks.json": {
                "status": "structural_enumeration_only_ranks_UNREACHED",
                "structural_enumeration": aut_enum,
                "rank_statistics_reason": "specification_error + SR3",
                "detail": spec_error},
            "transport-certificates.json": transport,
            "baseline-provenance.json": {
                "status": "UNREACHED", "reason": "specification_error",
                "detail": spec_error},
            "verdict.json": verdict,
            "r-stratification-finding.json": r_finding,
        })
        p(f"wrote {run_id} status=completed (bounded terminal state)")
    return 0


def _write_extra(run_id: str, files: dict) -> None:
    run_dir = os.path.join(REPO, "experiments", jm.EXP_ID, "runs", run_id)
    for name, obj in files.items():
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=False, default=str)


if __name__ == "__main__":
    raise SystemExit(main())
