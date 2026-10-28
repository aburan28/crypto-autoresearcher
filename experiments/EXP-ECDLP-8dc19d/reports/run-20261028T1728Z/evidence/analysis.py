#!/usr/bin/env python3
"""Mechanical, preregistered transfer summaries; never evaluate a predicate.

All successful event counts require the frozen independent verifier to pass.
Unverified producer statuses remain separately visible. No failed or zero-success
cell is dropped, and no missing operation count is replaced with measured work.
"""
from __future__ import annotations
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "classical.ecdlp.transfer-study.summary-census/v1"
ARMS = tuple([f"circuit{i}.a{a}" for i in (1, 2) for a in (1, 2, 3, 5)] +
             ["uniform_candidate", "bsgs_reference", "aa_circuit1_a1"])
Z95 = 1.959963984540054


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path):
    """Retain physical-line errors without pretending truncated rows completed."""
    path = Path(path)
    rows, findings = [], []
    if not path.is_file():
        return rows, [{"path": str(path), "error": "missing_stream"}]
    with path.open("rb") as source:
        for number, line in enumerate(source, 1):
            try:
                need(line.endswith(b"\n"), "incomplete physical JSONL line")
                need(bool(line.strip()), "blank JSONL line")
                row = json.loads(line)
                need(isinstance(row, dict), "JSON object required")
                rows.append(row)
            except (ValueError, UnicodeError) as error:
                findings.append({"path": str(path), "line": number, "error": str(error),
                                 "line_sha256": hashlib.sha256(line).hexdigest()})
    return rows, findings


def add_counts(total, values):
    need(isinstance(values, dict), "counter vector must be an object")
    for key, value in values.items():
        need(isinstance(key, str) and type(value) is int and value >= 0,
             "counter vector must contain nonnegative integers")
        total[key] += value


def merge_phases(phases):
    out = Counter()
    for vector in phases.values():
        add_counts(out, vector)
    return dict(out)


def wilson95(k, n):
    need(type(k) is int and type(n) is int and 0 <= k <= n, "invalid binomial counts")
    if n == 0:
        return None
    q = k / n
    den = 1 + Z95 * Z95 / n
    center = (q + Z95 * Z95 / (2 * n)) / den
    radius = Z95 * math.sqrt(q * (1-q) / n + Z95 * Z95 / (4*n*n)) / den
    return [max(0.0, center-radius), min(1.0, center+radius)]


def rational(numerator, denominator):
    return None if denominator == 0 else {"numerator": numerator, "denominator": denominator}


def cost_ratios(setup, online, successes):
    if successes == 0:
        return {"online_over_q": None, "batch": None, "cold": None}
    keys = setup.keys() | online.keys()
    return {"online_over_q": {k: rational(online.get(k, 0), successes) for k in keys},
            "batch": {k: rational(setup.get(k, 0) + online.get(k, 0), successes) for k in keys},
            "cold": {k: rational(successes * setup.get(k, 0) + online.get(k, 0), successes) for k in keys}}


def prefix_counts(rows_by_target):
    """All targets contribute through first verified hit or their full failure."""
    total = Counter()
    for rows in rows_by_target.values():
        for row in sorted(rows, key=lambda r: r["replicate_index"]):
            add_counts(total, merge_phases(row["result"]["counts"]))
            if row["result"]["status"] == "RECOVERED":
                break
    return dict(total)


def aggregate(cohort, attempts, setups, diagnostics, intents, report):
    fixtures = cohort.get("fixtures", [])
    fixture_by_id = {f["curve_id"]: f for f in fixtures}
    need(len(fixture_by_id) == len(fixtures), "duplicate fixture ID")
    setup_by_cell, rows_by_cell, diag_by_cell = {}, defaultdict(list), defaultdict(list)
    seen_results, seen_intents, expected, findings = set(), set(), set(), []
    for fixture in fixtures:
        for arm in ARMS:
            for target in fixture["targets"]:
                for rep in range(1 if arm == "bsgs_reference" else 4):
                    expected.add(f"{fixture['curve_id']}/{target['target_id']}/{arm}/rep{rep}")
    for row in setups:
        key = row.get("curve_id"), row.get("arm_id")
        if key in setup_by_cell or key[0] not in fixture_by_id or key[1] not in ARMS:
            findings.append({"stream": "setups", "error": "duplicate/unplanned cell", "cell": key})
            continue
        setup_by_cell[key] = row
    for row in attempts:
        identifier = row.get("attempt_id")
        key = row.get("curve_id"), row.get("arm_id")
        if identifier in seen_results or identifier not in expected or key[0] not in fixture_by_id or key[1] not in ARMS:
            findings.append({"stream": "attempts", "error": "duplicate/unplanned attempt", "attempt_id": identifier})
            continue
        seen_results.add(identifier); rows_by_cell[key].append(row)
    for row in intents:
        identifier = row.get("attempt_id")
        if identifier in seen_intents or identifier not in expected:
            findings.append({"stream": "intents", "error": "duplicate/unplanned intent", "attempt_id": identifier})
            continue
        seen_intents.add(identifier)
    for row in diagnostics:
        diag_by_cell[row.get("curve_id"), row.get("arm_id")].append(row)
    if seen_results - seen_intents:
        findings.append({"stream": "intents", "error": "result without retained pre-work intent",
                         "attempt_ids": sorted(seen_results - seen_intents)})
    verified = bool(report and report.get("pass") is True and not findings)
    verified_cells = {(r["curve_id"], r["arm_id"]): r for r in (report or {}).get("per_curve_arm_outcomes", [])}
    gate_cells = {(r["curve_id"], r["arm_id"]): r for r in (report or {}).get("small_all_r_diagnostics", [])}
    cells = []
    for fixture in fixtures:
        curve = fixture["curve_id"]
        target_ids = {t["target_id"] for t in fixture["targets"]}
        for arm in ARMS:
            key, reps = (curve, arm), (1 if arm == "bsgs_reference" else 4)
            setup, rows = setup_by_cell.get(key), rows_by_cell[key]
            planned_ids = {f"{curve}/{target}/{arm}/rep{rep}" for target in target_ids for rep in range(reps)}
            actual_ids = {r["attempt_id"] for r in rows}
            complete = setup is not None and actual_ids == planned_ids and planned_ids <= seen_intents
            setup_phases = setup["counts"] if setup else {}
            online_phases = defaultdict(Counter)
            target_rows, statuses, reported_targets = defaultdict(list), Counter(), set()
            for row in rows:
                result = row["result"]
                statuses[result["status"] + ":" + str(result.get("reason"))] += 1
                target_rows[row["target_id"]].append(row)
                if result["status"] == "RECOVERED":
                    reported_targets.add(row["target_id"])
                for phase, vector in result["counts"].items():
                    add_counts(online_phases[phase], vector)
            setup_vector = merge_phases(setup_phases)
            online_vector = merge_phases(online_phases)
            diagnostic_vector = Counter()
            for row in diag_by_cell[key]:
                add_counts(diagnostic_vector, row["counters"])
            reported_k = sum(r["result"]["status"] == "RECOVERED" for r in rows)
            independently_valid = verified and complete and key in verified_cells
            if independently_valid:
                assessed = verified_cells[key]
                need(assessed["attempts"] == len(rows) and assessed["successes"] == reported_k and
                     assessed["source_setup_counters_once"] == setup_vector and
                     assessed["source_online_counters_all_attempts"] == online_vector,
                     "independent verifier/raw event or phase accounting differs")
            k = reported_k if independently_valid else None
            ratios = cost_ratios(setup_vector, online_vector, k) if k is not None else {"online_over_q": None, "batch": None, "cold": None}
            prefix = prefix_counts(target_rows) if independently_valid else None
            gate = gate_cells.get(key)
            gate_pass = None
            if independently_valid and gate is not None:
                gate_pass = int(gate["all_r_coverage"] and gate["undefined_count"] == 0 and
                    gate["truth_mismatch_count"] == 0 and all(x == 0 for x in gate["two_pulse_residual"]))
            group = lambda mapping: mapping.get("group_add_call", 0)
            cells.append({"curve_id": curve, "arm_id": arm, "planned_attempts": len(planned_ids),
                "observed_attempts": len(rows), "planned_target_ids": len(target_ids), "replicates_per_target": reps,
                "reported_success_events": reported_k, "verified_attempt_successes": k,
                "unique_target_ids_reported_recovered": len(reported_targets),
                "unique_target_ids_recovered": len(reported_targets) if independently_valid else None,
                "attempt_status_counts": dict(statuses), "q_numerator": k,
                "q_denominator": len(rows) if independently_valid else None,
                "q_wilson95": wilson95(k, len(rows)) if independently_valid and arm != "bsgs_reference" else None,
                "small_full_bit_gate_passes": gate_pass,
                "online_group_add_calls": group(online_vector) if independently_valid else None,
                "setup_group_add_calls": group(setup_vector) if independently_valid else None,
                "online_group_work_over_q": rational(group(online_vector), k) if k is not None else None,
                "batch_work_per_success_event": rational(group(setup_vector)+group(online_vector), k) if k is not None else None,
                "cold_restart_model_group_work": rational(k*group(setup_vector)+group(online_vector), k) if k is not None else None,
                "first_success_prefix_group_work": group(prefix) if prefix is not None else None,
                "source_setup_counters_once": setup_vector, "source_online_counters_all_attempts": online_vector,
                "setup_phase_counters": setup_phases, "online_phase_counters": {p: dict(v) for p,v in online_phases.items()},
                "diagnostic_counters": dict(diagnostic_vector), "first_success_prefix_counters": prefix,
                "counter_cost_over_q": ratios["online_over_q"], "batch_counter_cost_per_success": ratios["batch"],
                "cold_restart_counter_model": ratios["cold"], "unresolved_attempts": len((seen_intents & planned_ids)-seen_results),
                "unattempted_attempts": len(planned_ids-seen_intents), "complete": complete,
                "independently_verified": independently_valid, "actual_setup_observed": setup is not None,
                "ratio_undefined_reason": "ZERO_OBSERVED_ESTIMATE_UNDEFINED" if k == 0 else "INCOMPLETE_OR_UNVERIFIED" if k is None else None,
                "q_interval_scope": "Registered pointwise Wilson95 under PRG/iid model; no familywise discovery" if arm != "bsgs_reference" else "Deterministic reference; no binomial interval",
                "zero_observed_is_not_proven_zero_probability": True})
    accounting = {"planned_attempts": len(expected), "observed_completed_result_ids": len(seen_results),
        "observed_prework_intent_ids": len(seen_intents), "unresolved_attempt_ids": sorted(seen_intents-seen_results),
        "unattempted_attempt_ids": sorted(expected-seen_intents), "result_without_intent_ids": sorted(seen_results-seen_intents)}
    return cells, accounting, findings
