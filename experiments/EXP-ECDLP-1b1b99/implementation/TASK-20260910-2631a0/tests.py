"""Artificial controls for TASK-20260910-2631a0; draft, not executed.

No arithmetic workload, RUN, private material or fixture child process is used.
Coverage and the invocation journal must be frozen before invoking this file.
"""
from __future__ import annotations

import copy
import hashlib
import io
from fractions import Fraction
from itertools import product
from typing import Any

from costs import (CostContract, CostError, CostLedger, CostCheckpoint, CostCancelled,
                   canonical_json, strict_json_loads, validate_raw_semantics,
                   actual_campaign_accounting, iter_operation_totals, pinned_dependency_projection,
                   compare_manifest_bindings, compare_companion_bytes)
from allocations import (AllocationContext, FIXTURES, ENDPOINTS, COORDINATES, SEEDS, QS,
                         expected_groups, edges_from_groups, validate_allocation_edges, iter_expected_edges)
from reducers import (BlockEstimate, TimingIndex, parse_timing_fact, panel_cost_outputs,
                      statistical_branch, compare_cost_projection, q_star_from_ladder,
                      select_candidates, decode_fraction, supplied_hard_prerequisites,
                      AllocationReduction, reduce_cost_component, compare_manifest_costs)


def require(value: bool, detail: str) -> None:
    if value is not True:
        raise AssertionError(detail)


def refuses(function: Any, code: str | None = None) -> None:
    try:
        function()
    except CostError as error:
        if code is not None and error.code != code:
            raise AssertionError("unexpected typed refusal: " + error.code) from error
        return
    raise AssertionError("known-invalid artificial input was accepted")


def context_data(partition: int = 0) -> dict[str, Any]:
    pairs = ((["K0", "K1"], ["K2", "K3"]), (["K0", "K2"], ["K1", "K3"]),
             (["K0", "K3"], ["K1", "K2"]))[partition]
    return {
        "record_type": "cm_cost_context",
        "candidate_origins": {"I0": 1, "I1": 3, "I2": 5},
        "candidate_trace": [{"interval": "I" + str(i), "event_ordinal": 1 + 2*i + f,
                             "outcome": "accepted"} for i in range(3) for f in range(2)],
        "class_memberships": {fixture: {"C0": list(pairs[0]), "C1": list(pairs[1])} for fixture in FIXTURES},
        "frozen_winners": [{"interval": "I" + str(i), "coordinate": u, "arm": 2}
                           for i in range(3) for u in COORDINATES],
    }


def raw_record(component: str = "scalar_multiplication", scope: str = "block_repetition",
               phase: str = "evaluation", arm: int = 2, plane: str = "main",
               ordinal: int = 1) -> dict[str, Any]:
    row = {
        "record_type": "raw_cost", "raw_cost_row_id": "synthetic-row-" + str(ordinal),
        "physical_event_id": "synthetic-event-" + str(ordinal), "event_ordinal": ordinal,
        "component": component, "phase": phase, "status": "complete",
        "CPU_nanoseconds": 17, "CPU_unavailable_reason": None,
        "wall_nanoseconds": 19, "wall_unavailable_reason": None,
        "process_group_peak_RSS_bytes": 31, "RSS_unavailable_reason": None,
        "operation_counts": None, "operation_counts_unavailable_reason": "uninstrumented_backend",
        "capture_interval": {"stream_id": "synthetic-stream", "process_group_id": 1,
            "cpu_started_ns": ordinal*1000, "cpu_finished_ns": ordinal*1000+17,
            "wall_started_ns": ordinal*1000, "wall_finished_ns": ordinal*1000+19, "reason": None},
        "charge_kind": "exclusive_leaf", "source_leaf_ids": [], "scope": scope,
    }
    if scope in ("interval", "selection_stratum"):
        row["interval"] = "I0"
    if scope not in ("global", "interval", "selection_stratum", "scaffolding"):
        row["fixture"] = "I0F0"
    if scope == "kernel":
        row["kernel"] = "K0"
    if scope == "class":
        row["class"] = "C0"
    if scope in ("endpoint_coordinate", "arm_workload", "timing_block", "block_repetition"):
        row.update(endpoint="K0", coordinate=1)
    if scope == "selection_stratum":
        row["coordinate"] = 1
    if scope in ("arm_workload", "timing_block", "block_repetition"):
        row.update(plane=plane, arm=arm, seed=606101 if plane == "selection" else 606103,
                   q=256 if plane == "selection" else 4096)
    if scope in ("timing_block", "block_repetition"):
        row["block"] = 0
    if scope == "block_repetition":
        row["repetition"] = 1
    if scope == "scaffolding":
        row.update(scaffold_kind=component, owner={"scope": "global"})
        if component in ("top_level_control", "identity_transport_control"):
            row["owner"] = {"scope": "control_workload", "fixture": "I0F0", "coordinate": 1,
                "plane": "top_control" if component == "top_level_control" else "identity_control",
                "arm": "direct_3_iota" if component == "top_level_control" else "identity_iota_identity",
                "seed": 606101, "q": 1}
    if component in ("level_and_multiplicity_certificate", "all_six_algorithm_selection_trials"):
        row.update(charge_kind="derived_rollup", source_leaf_ids=["synthetic-child"],
                   CPU_nanoseconds=None, CPU_unavailable_reason="derived_rollup",
                   wall_nanoseconds=None, wall_unavailable_reason="derived_rollup")
    return row


def timing_record(block: int = 0) -> dict[str, Any]:
    return {"record_type": "cm_timing_block", "plane": "main", "fixture": "I0F0",
            "endpoint": "K0", "coordinate": 1, "seed": 606103, "q": 4096,
            "arm": 2, "block": block, "status": "complete", "repetitions": 1,
            "cumulative_group_CPU_nanoseconds": [100000000],
            "replay_verified": True, "resource_accounted": True}


def panel_estimates(scalar: int = 12, transport: int = 10) -> dict[tuple[Any, ...], BlockEstimate]:
    return {(view, f, e, u, seed, q): BlockEstimate(0, (Fraction(value),)*7, None)
            for view, value in (("scalar", scalar), ("transport", transport))
            for f, e, u, seed, q in product(FIXTURES, ENDPOINTS, COORDINATES, SEEDS, QS)}


def crosswalk_control(contract: CostContract, parameters: dict[str, Any]) -> None:
    row = raw_record(**parameters["record"])
    mutation = parameters["mutation"]
    if mutation is None:
        checked = validate_raw_semantics(contract, row)
        require(checked == row, "valid explicit crosswalk row must remain unchanged")
    else:
        row.update(mutation)
        refuses(lambda: validate_raw_semantics(contract, row))


def candidate_control(parameters: dict[str, Any]) -> None:
    data = context_data(parameters.get("partition", 0))
    action = parameters["action"]
    if action == "global_origins":
        context = AllocationContext(data)
        require(context.candidate_fixture("I1", 3) == "I1F0", "global ordinal3 joins I1F0")
        require(context.candidate_fixture("I2", 6) == "I2F1", "global ordinal6 joins I2F1")
        refuses(lambda: context.candidate_fixture("I1", 0), "missing_candidate_join")
    elif action == "rejected_prefix":
        data["candidate_trace"] = [{"interval": "I0", "event_ordinal": 1, "outcome": "rejected"},
            {"interval": "I0", "event_ordinal": 2, "outcome": "accepted"},
            {"interval": "I0", "event_ordinal": 3, "outcome": "accepted"}]
        data["class_memberships"] = {f: value for f, value in data["class_memberships"].items() if f.startswith("I0")}
        data["frozen_winners"] = []
        context = AllocationContext(data)
        require(context.candidate_fixture("I0", 1) == "I0F0", "rejected prefix charged to eventual F0")
        require(context.candidate_fixture("I0", 3) == "I0F1", "second accepted candidate joins F1")
    elif action == "gap":
        data["candidate_trace"][1]["event_ordinal"] = 3
        refuses(lambda: AllocationContext(data), "candidate_prefix_missing_or_duplicate")
    elif action == "missing_origin":
        data["candidate_origins"]["I1"] = None
        refuses(lambda: AllocationContext(data), "candidate_trace_without_declared_origin")
    elif action == "partition":
        context = AllocationContext(data)
        require(context.fixtures_complete, "all three two-pair partitions are permitted")
        require(len(context.class_labels("I0F0", "C0")) == 2, "class retains two labels")
    else:
        raise AssertionError("unregistered candidate action")


def panel_control(parameters: dict[str, Any]) -> None:
    context = AllocationContext(context_data())
    expected = panel_cost_outputs(context, panel_estimates(parameters["scalar"]))
    require(len(expected["R_cells"]) == 288 and len(expected["R_global"]) == 8 and len(expected["q_star"]) == 36,
            "exact complete output identity sets")
    require(statistical_branch(expected["R_cells"], True) == parameters["branch"], "exact full and LOO branch")
    altered = copy.deepcopy(expected)
    for row in altered["R_cells"]:
        row["leave_one_out"].reverse()
    compare_cost_projection(expected, altered)
    altered["R_cells"][0] = copy.deepcopy(altered["R_cells"][1])
    refuses(lambda: compare_cost_projection(expected, altered), "duplicate_cell")


def timing_control(parameters: dict[str, Any]) -> None:
    row = timing_record()
    row.update(parameters["mutation"])
    if parameters.get("refusal"):
        refuses(lambda: parse_timing_fact(row), parameters["refusal"])
    else:
        fact = parse_timing_fact(row)
        require(fact.reason == parameters["reason"], "timing uncertainty must be preserved")


def json_control(parameters: dict[str, Any]) -> None:
    if parameters["action"] == "roundtrip":
        value = parameters["value"]
        require(strict_json_loads(canonical_json(value)) == value, "strict canonical roundtrip")
    elif parameters["action"] == "parse_refusal":
        source = bytes.fromhex(parameters["hex"])
        refuses(lambda: strict_json_loads(source), parameters.get("code"))
    elif parameters["action"] == "encode_refusal":
        value = {"float": 1.0, "bool_key": {True: 1}, "surrogate": "\ud800"}[parameters["fixture"]]
        refuses(lambda: canonical_json(value))
    elif parameters["action"] == "large_integer":
        value = 10**5000 + 17
        require(strict_json_loads(canonical_json(value)) == value, "arbitrary precision integer carrier")
    else:
        raise AssertionError("unregistered JSON action")


def csv_control(contract: CostContract, parameters: dict[str, Any]) -> None:
    row = raw_record()
    stream = io.StringIO()
    contract.write_cost_csv([row], stream)
    text = stream.getvalue()
    action = parameters["action"]
    if action == "roundtrip":
        require(list(contract.iter_cost_csv(io.StringIO(text))) == [row], "CSV decoded record roundtrip")
    elif action == "header":
        refuses(lambda: list(contract.iter_cost_csv(io.StringIO(text.replace("record_type,record_json", "type,json", 1)))), "cost_csv_header_mismatch")
    elif action == "type_column":
        refuses(lambda: list(contract.iter_cost_csv(io.StringIO(text.replace("\nraw_cost,", "\nallocation_edge,", 1)))), "cost_csv_record_type_mismatch")
    elif action == "crlf":
        refuses(lambda: list(contract.iter_cost_csv(io.StringIO(text.replace("\n", "\r\n")))), "csv_requires_lf_text_lines")
    else:
        raise AssertionError("unregistered CSV action")


def ledger_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    row = raw_record()
    action = parameters["action"]
    if action == "valid_rollup":
        row = raw_record("level_source_certificate", "fixture", "setup")
    with CostLedger(contract, scratch) as ledger:
        ledger.add(row)
        if action == "valid_rollup":
            summary = raw_record("level_and_multiplicity_certificate", "fixture", "setup", ordinal=2)
            summary["source_leaf_ids"] = [row["raw_cost_row_id"]]
            ledger.add(summary)
            ledger.finalize()
            require(actual_campaign_accounting(ledger)["CPU_nanoseconds"] == 17, "rollup does not add a physical charge")
            groups, issues = expected_groups(contract, summary, AllocationContext(context_data()))
            require(groups == () and issues == (), "derived summary has no allocation edges")
            return
        if action == "duplicate_row":
            refuses(lambda: ledger.add(copy.deepcopy(row)), "duplicate_ledger_identity")
            return
        if action == "duplicate_physical":
            other = raw_record(ordinal=2)
            other["physical_event_id"] = row["physical_event_id"]
            refuses(lambda: ledger.add(other), "duplicate_ledger_identity")
            return
        if action == "overlap":
            other = raw_record(ordinal=2)
            other["capture_interval"] = copy.deepcopy(row["capture_interval"])
            other["capture_interval"]["stream_id"] = "other-stream"
            refuses(lambda: ledger.add(other), "overlapping_exclusive_capture")
            return
        if action == "unknown_rollup_leaf":
            other = raw_record("level_and_multiplicity_certificate", "fixture", "setup", ordinal=2)
            ledger.add(other)
            refuses(ledger.finalize, "rollup_reference_is_not_exclusive_leaf")
            return
        ledger.finalize()
        inventory = [{"raw_cost_row_id": row["raw_cost_row_id"], "canonical_record_sha256": hashlib.sha256(canonical_json(row)).hexdigest()}]
        if action == "inventory_omission":
            refuses(lambda: ledger.compare_capture_inventory([]), "capture_inventory_mismatch")
        elif action == "inventory_digest":
            inventory[0]["canonical_record_sha256"] = "0"*64
            refuses(lambda: ledger.compare_capture_inventory(inventory), "capture_inventory_mismatch")
        elif action == "actual_once":
            ledger.compare_capture_inventory(inventory)
            accounting = actual_campaign_accounting(ledger)
            require(accounting["CPU_nanoseconds"] == 17 and accounting["wall_nanoseconds"] == 19,
                    "one physical leaf is counted once")
            require(accounting["peak_observed_RSS_bytes"] == 31, "RSS is an observed maximum")
        else:
            raise AssertionError("unregistered ledger action")


def allocation_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    context = AllocationContext(context_data())
    row = raw_record(**parameters["record"])
    row = validate_raw_semantics(contract, row)
    with CostLedger(contract, scratch) as ledger:
        ledger.add(row)
        ledger.finalize()
        groups, issues = expected_groups(contract, row, context)
        require(not issues, "complete artificial allocation context")
        edges = list(edges_from_groups(row, groups))
        action = parameters["action"]
        if action == "complete":
            result = validate_allocation_edges(ledger, context, iter(edges))
            require(result["edges_checked"] == parameters["expected_edges"], "exact edge count")
            for group in groups:
                selected = [edge for edge in edges if edge["strategy_view"] == group.view and edge["scenario"] == group.scenario]
                require(sum(edge["allocated_CPU_nanoseconds"] for edge in selected) == 17, "integer reconciliation per alternative group")
        elif action == "missing_group":
            first = groups[0]
            altered = [edge for edge in edges if not (edge["strategy_view"] == first.view and edge["scenario"] == first.scenario)]
            refuses(lambda: validate_allocation_edges(ledger, context, iter(altered)))
        elif action == "extra_edge":
            refuses(lambda: validate_allocation_edges(ledger, context, iter(edges + [copy.deepcopy(edges[-1])])) )
        elif action == "integer_remainder":
            require(len(groups[0].targets) > 1, "remainder control has multiple targets")
            require(edges[0]["allocated_CPU_nanoseconds"] >= edges[len(groups[0].targets)-1]["allocated_CPU_nanoseconds"], "remainder belongs to earliest canonical targets")
            altered = copy.deepcopy(edges)
            altered[0]["allocated_CPU_nanoseconds"] += 1
            altered[1]["allocated_CPU_nanoseconds"] -= 1
            refuses(lambda: validate_allocation_edges(ledger, context, iter(altered)))
        else:
            raise AssertionError("unregistered allocation action")


def selection_control(parameters: dict[str, Any]) -> None:
    estimates = {(f, e, u, arm): BlockEstimate(0, (Fraction(arm),)*7, None)
                 for f, e, u, arm in product(FIXTURES, ENDPOINTS, COORDINATES, range(2, 8))}
    action = parameters["action"]
    if action == "tie":
        estimates = {key: BlockEstimate(0, (Fraction(10),)*7, None) for key in estimates}
    elif action == "normalization_reversal":
        # Arm7 has higher actual repeated spend but a lower exact normalized
        # score. The full retained-row connection gets a separate control.
        estimates = {key: BlockEstimate(0, (Fraction(7, 10) if key[-1] == 7 else Fraction(key[-1]),)*7, None)
                     for key in estimates}
    elif action == "missing":
        del estimates[("I0F0", "K0", 1, 2)]
    elif action == "invalid":
        estimates[("I0F0", "K0", 1, 2)] = BlockEstimate(0, None, "below_resolution")
    elif action != "complete":
        raise AssertionError("unregistered selection action")
    rows = select_candidates(estimates)
    require(len(rows) == 9, "nine selection strata")
    if action in ("missing", "invalid"):
        require(rows[0]["winner"] is None, "no candidate is silently discarded")
        require(all(row["winner"] == 2 for row in rows[1:]), "unaffected strata retain their winner")
    else:
        winner = 7 if action == "normalization_reversal" else 2
        require(all(row["winner"] == winner for row in rows), "exact score and tie winner")


def reduction_edge_control(parameters: dict[str, Any]) -> None:
    action = parameters["action"]
    if action == "median6":
        estimate = BlockEstimate(5, tuple(Fraction(x) for x in (1, 2, 3, 4, 8, 9, 20)), None)
        require(estimate.total() == Fraction(9), "Med7 fourth order statistic plus setup")
        require(estimate.total(6) == Fraction(17, 2), "Med6 mean of third and fourth plus fixed setup")
    elif action == "invalid_omitted":
        estimate = BlockEstimate(0, (Fraction(1),)*6 + (None,), None)
        refuses(lambda: estimate.total(6), "invalid_original_normalized_block")
    elif action == "fraction":
        refuses(lambda: decode_fraction(parameters["value"]))
    elif action == "q_star":
        ratios = {q: {"kind": "value", "value": {"numerator": n, "denominator": d}}
                  for q, (n, d) in zip(QS, parameters["values"])}
        if parameters.get("unknown") is not None:
            ratios[parameters["unknown"]] = {"kind": "unavailable", "reason": "missing_input"}
        require(q_star_from_ladder(ratios) == parameters["expected"], "exact resolved prefix crossover")
    else:
        raise AssertionError("unregistered reduction edge action")


def hard_control(contract: CostContract, parameters: dict[str, Any]) -> None:
    result = supplied_hard_prerequisites(contract, parameters["values"])
    require(result["supplied_conjunction"] is parameters["expected"], "fixed hard prerequisite conjunction")


def resource_control(contract: CostContract, parameters: dict[str, Any]) -> None:
    row = raw_record()
    row.update(parameters["mutation"])
    if parameters["accepted"]:
        require(validate_raw_semantics(contract, row) == row, "explicit partial observation preserved")
    else:
        refuses(lambda: validate_raw_semantics(contract, row))


def owner_control(contract: CostContract, parameters: dict[str, Any]) -> None:
    component = parameters["component"]
    row = raw_record(component, "scaffolding", "control" if component in ("top_level_control", "identity_transport_control") else "preparation")
    row["owner"] = copy.deepcopy(parameters["owner"])
    if parameters["accepted"]:
        require(validate_raw_semantics(contract, row) == row, "explicit tagged owner remains intact")
    else:
        refuses(lambda: validate_raw_semantics(contract, row))


def operation_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    first, second = raw_record(ordinal=1), raw_record(ordinal=2)
    first.update(operation_counts={"multiply": 10**100 + 7}, operation_counts_unavailable_reason=None)
    if parameters["action"] == "complete":
        second.update(operation_counts={"multiply": 9}, operation_counts_unavailable_reason=None)
    elif parameters["action"] == "omitted_name":
        second.update(operation_counts={"add": 9}, operation_counts_unavailable_reason=None)
    elif parameters["action"] != "unknown":
        raise AssertionError("unregistered operation action")
    with CostLedger(contract, scratch) as ledger:
        ledger.add(first)
        ledger.add(second)
        ledger.finalize()
        rows = {row["operation"]: row for row in iter_operation_totals(ledger)}
        multiplication = rows["multiply"]
        if parameters["action"] == "complete":
            require(multiplication["total"] == 10**100 + 16, "arbitrary integer operation total")
            require(multiplication["unavailable_or_omitted_row_count"] == 0, "complete named operation observations")
        else:
            require(multiplication["total"] is None, "missing operation observation is not zero")
            require(multiplication["known_lower_bound"] == 10**100 + 7, "known operation contribution retained")
            require(multiplication["unavailable_or_omitted_row_count"] == 1, "missing-name row count retained")


def checkpoint_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    token = CostCheckpoint()
    with CostLedger(contract, scratch, checkpoint=token) as ledger:
        ledger.add(raw_record())
        token.request_stop()
        if parameters["action"] == "add":
            refuses(lambda: ledger.add(raw_record(ordinal=2)), "cooperative_checkpoint_stop")
        elif parameters["action"] == "iterate":
            # Finalize has no joins for this one exclusive leaf; the next
            # documented row iteration boundary must observe cancellation.
            ledger.finalize()
            refuses(lambda: list(ledger.iter_rows()), "cooperative_checkpoint_stop")
        else:
            raise AssertionError("unregistered checkpoint action")
        require(token.snapshot()["stop_requested"], "requested stop is retained")


def joint_control(parameters: dict[str, Any]) -> None:
    context = AllocationContext(context_data())
    estimates = panel_estimates()
    action = parameters["action"]
    if action == "label_value_swap":
        estimates = {key: (BlockEstimate(0, tuple(Fraction(x) for x in (10,11,12,13,14,15,16)), None)
                          if key[0] == "scalar" else value) for key, value in estimates.items()}
        original = panel_cost_outputs(context, estimates)
        changed = copy.deepcopy(original)
        row = next(row for row in changed["R_cells"] if row["seed"] == 606103 and row["q"] == 4096)
        row["leave_one_out"][0]["omitted_block"] = 6
        row["leave_one_out"][6]["omitted_block"] = 0
        refuses(lambda: compare_cost_projection(original, changed), "cell_projection_disagrees_with_retained_costs")
    elif action in ("unstable", "original_vector_stable"):
        values = (10,11,11,12,12,13,14) if action == "unstable" else (10,11,12,12,12,13,14)
        estimates = {key: (BlockEstimate(0, tuple(Fraction(x) for x in values), None)
                          if key[0] == "scalar" else value) for key, value in estimates.items()}
        outputs = panel_cost_outputs(context, estimates)
        expected_branch = "inconclusive" if action == "unstable" else "finite_panel_signal_only"
        require(statistical_branch(outputs["R_cells"], True) == expected_branch, "hand-derived original or boundary-crossing joint medians")
    elif action == "ratio_of_sums":
        for key in estimates:
            view, fixture, endpoint, coordinate, seed, q = key
            if endpoint in ("K0", "K1"):
                value = 100 if (view == "scalar") == (endpoint == "K0") else 1
                estimates[key] = BlockEstimate(0, (Fraction(value),)*7, None)
        outputs = panel_cost_outputs(context, estimates)
        require(all(row["ratio"]["value"] == {"numerator": 1, "denominator": 1} for row in outputs["R_cells"] if row["class"] == "C0"), "ratio of sums, not mean of endpoint ratios")
    elif action == "global_cannot_override":
        estimates[("scalar", "I0F0", "K0", 1, 606103, 4096)] = BlockEstimate(0, (Fraction(1),)*7, None)
        outputs = panel_cost_outputs(context, estimates)
        require(statistical_branch(outputs["R_cells"], True) == "inconclusive", "one nonconforming cell defeats all-cell success")
    elif action == "missing_original":
        estimates[("scalar", "I0F0", "K0", 1, 606103, 4096)] = BlockEstimate(0, None, "below_resolution")
        outputs = panel_cost_outputs(context, estimates)
        row = next(row for row in outputs["R_cells"] if (row["fixture"], row["class"], row["coordinate"], row["seed"], row["q"]) == ("I0F0", "C0", 1, 606103, 4096))
        require(row["ratio"]["kind"] == "unavailable" and all(item["kind"] == "unavailable" for item in row["leave_one_out"]), "invalid original cannot be rescued by any omission")
    else:
        raise AssertionError("unregistered joint-reduction action")


def connected_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    """One artificial stratum through all six candidates and both main views.

    This is a finite accounting fragment, not a complete scientific campaign.
    Other strata and timing alternatives are intentionally absent and must
    remain unavailable in the resulting full-identity projection.
    """
    action = parameters["action"]
    if action not in ("complete", "normalization_reversal", "missing_evaluator", "missing_warmup",
                      "manifest_projection", "manifest_ratio_mismatch", "manifest_coverage_mismatch"):
        raise AssertionError("unregistered connection action")
    winner = 7 if action == "normalization_reversal" else 2
    data = context_data()
    data["frozen_winners"][0]["arm"] = winner
    context = AllocationContext(data)
    rows, timings = [], []
    ordinal = 0

    def append(component: str, phase: str, plane: str, fixture: str, endpoint: str,
               arm: int, *, block: int | None = None, repetition: int | None = None,
               cpu: int = 17) -> None:
        nonlocal ordinal
        ordinal += 1
        row = raw_record(component, "arm_workload" if block is None else "block_repetition",
                         phase, arm, plane, ordinal)
        row.update(fixture=fixture, endpoint=endpoint, CPU_nanoseconds=cpu, wall_nanoseconds=cpu+2)
        row["capture_interval"]["cpu_finished_ns"] = row["capture_interval"]["cpu_started_ns"] + cpu
        row["capture_interval"]["wall_finished_ns"] = row["capture_interval"]["wall_started_ns"] + cpu + 2
        if block is not None:
            row.update(block=block, repetition=repetition)
        rows.append(row)

    for plane in ("selection", "main"):
        arms = range(2, 8) if plane == "selection" else (1, winner)
        for fixture, endpoint, arm in product(("I0F0", "I0F1"), ENDPOINTS, arms):
            append("transport_warmup" if arm == 1 else "scalar_warmup", "warmup", plane, fixture, endpoint, arm)
            append("warmup_verification", "verification", plane, fixture, endpoint, arm)
            components = ["psi_evaluation", "iota_evaluation", "phi_evaluation"] if arm == 1 else ["scalar_multiplication"]
            components += ["query_serialization", "output_verification"]
            if arm in (3, 4, 5, 6):
                components += ["every_per_point_table"]
            repeats = 2 if plane == "selection" and arm == 7 and winner == 7 else 1
            cpu = 1 if repeats == 2 else arm*5
            for block in range(7):
                timing = timing_record(block)
                timing.update(plane=plane, fixture=fixture, endpoint=endpoint, arm=arm,
                              seed=606101 if plane == "selection" else 606103,
                              q=256 if plane == "selection" else 4096,
                              repetitions=repeats,
                              cumulative_group_CPU_nanoseconds=[50000000, 100000000] if repeats == 2 else [100000000])
                timings.append(timing)
                for repetition, component in product(range(1, repeats+1), components):
                    append(component, "verification" if component == "output_verification" else "evaluation",
                           plane, fixture, endpoint, arm, block=block, repetition=repetition, cpu=cpu)
    if action in ("missing_evaluator", "missing_warmup"):
        component = "scalar_multiplication" if action == "missing_evaluator" else "scalar_warmup"
        remove = next(i for i, row in enumerate(rows) if row["plane"] == "main" and row["arm"] == 2 and
                      row["fixture"] == "I0F0" and row["endpoint"] == "K0" and row["component"] == component)
        rows.pop(remove)
    with CostLedger(contract, scratch) as ledger:
        for row in rows:
            ledger.add(row)
        ledger.finalize()
        ledger.compare_capture_inventory({"raw_cost_row_id": row["raw_cost_row_id"],
                                          "canonical_record_sha256": hashlib.sha256(canonical_json(row)).hexdigest()} for row in rows)
        reduction = AllocationReduction(ledger, context, TimingIndex(timings), iter_expected_edges(ledger, context))
        outputs = reduction.outputs()
        selection = outputs["selection"][0]
        require(selection["winner"] == winner, "retained allocation/timing selection winner")
        winning_score = next(item["score"]["value"] for item in selection["scores"] if item["arm"] == winner)
        require(winning_score == {"numerator": 37 if winner == 7 else 64, "denominator": 1}, "hand-derived normalized candidate score")
        projected = outputs["cost_projection"]
        cell = next(row for row in projected["R_cells"] if (row["fixture"], row["class"], row["coordinate"], row["seed"], row["q"]) == ("I0F0", "C0", 1, 606103, 4096))
        if action in ("missing_evaluator", "missing_warmup"):
            require(cell["ratio"]["kind"] == "unavailable", "missing required physical work cannot become free work")
            require(all(item["kind"] == "unavailable" for item in cell["leave_one_out"]), "no omission rescues missing required work")
        else:
            expected_ratio = Fraction(3115 if winner == 7 else 3733, 59)
            require(cell["ratio"]["value"] == {"numerator": expected_ratio.numerator, "denominator": expected_ratio.denominator},
                    "actual selection spend remains fixed in the hand-derived scalar cold total")
        require(any(row["ratio"]["kind"] == "unavailable" for row in projected["R_cells"] if row["fixture"] == "I2F0"),
                "absent stratum remains unavailable")
        if action.startswith("manifest_"):
            manifest = manifest_data(scratch.parent.parent / "inputs")
            metrics = manifest["run"]["result"]["metrics"]
            metrics.update(copy.deepcopy(projected))
            metrics["coverage"].update(accepted_fixtures=6, resolved_primary_cells=4,
                                        main_block_rows=112, selection_block_rows=336)
            if action == "manifest_ratio_mismatch":
                metrics["R_global"][0]["ratio"] = {"kind": "value", "value": {"numerator": 0, "denominator": 1}}
                refuses(lambda: compare_manifest_costs(contract, manifest, reduction, {}), "cost_projection_disagrees_with_retained_data")
            elif action == "manifest_coverage_mismatch":
                metrics["coverage"]["main_block_rows"] = 111
                refuses(lambda: compare_manifest_costs(contract, manifest, reduction, {}), "manifest_timing_coverage_mismatch")
            else:
                result = compare_manifest_costs(contract, manifest, reduction, {})
                require(result["conditional_branch"] == "inconclusive" and not result["whole_manifest_validated"],
                        "matching partial cost projection does not become whole-run validity")


def partial_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    row = raw_record("construct_supplied_public_source_curve", "fixture", "setup")
    data = context_data()
    action = parameters["action"]
    if action == "missing_target":
        data["class_memberships"] = {}
        data["frozen_winners"] = []
    elif action in ("missing_cpu", "invented_zero"):
        row.update(status="partial", CPU_nanoseconds=None, CPU_unavailable_reason="capture_failed")
    else:
        raise AssertionError("unregistered partial allocation action")
    context = AllocationContext(data)
    with CostLedger(contract, scratch) as ledger:
        ledger.add(row)
        ledger.finalize()
        ledger.compare_capture_inventory([{"raw_cost_row_id": row["raw_cost_row_id"],
                                           "canonical_record_sha256": hashlib.sha256(canonical_json(row)).hexdigest()}])
        edges = list(iter_expected_edges(ledger, context))
        require(len(edges) == 1 and edges[0]["strategy_view"] == "actual_only_scaffolding", "unresolved row retained once as actual-only")
        require(edges[0]["weight"] == {"numerator": 1, "denominator": 1}, "actual-only copy weight")
        if action == "invented_zero":
            edges[0].update(allocated_CPU_nanoseconds=0, allocated_CPU_unavailable_reason=None)
            refuses(lambda: reduce_cost_component(ledger, context, TimingIndex([]), iter(edges)))
        else:
            output = reduce_cost_component(ledger, context, TimingIndex([]), iter(edges))
            require(output["state"] == "partial_projection" and output["cost_projection"] is None, "partial input supplies no invented ratio")
            expected = 17 if action == "missing_target" else None
            require(output["actual_accounting"]["CPU_nanoseconds"] == expected, "actual known or unknown CPU preserved")


def selection_rollup_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    first = raw_record(plane="selection", ordinal=1)
    second = raw_record(plane="selection", ordinal=2)
    second["arm"] = 3
    summary = raw_record("all_six_algorithm_selection_trials", "selection_stratum", "selection", ordinal=3)
    summary["source_leaf_ids"] = [first["raw_cost_row_id"], second["raw_cost_row_id"]]
    action = parameters["action"]
    if action == "omitted_leaf":
        summary["source_leaf_ids"].pop()
    elif action == "wrong_owner":
        second["coordinate"] = 2
    elif action != "complete_retained_subset":
        raise AssertionError("unregistered selection rollup action")
    with CostLedger(contract, scratch) as ledger:
        for row in (first, second, summary):
            ledger.add(row)
        if action == "omitted_leaf":
            refuses(ledger.finalize, "selection_rollup_omits_retained_trial_leaf")
        elif action == "wrong_owner":
            refuses(ledger.finalize, "selection_rollup_wrong_owner")
        else:
            ledger.finalize()
            require(actual_campaign_accounting(ledger)["CPU_nanoseconds"] == 34, "all retained selection leaves counted once")
            # This is only a summary of the retained fragment. Two observed
            # arms are not a complete six-candidate scientific selection.


def dependency_control(parameters: dict[str, Any], inputs: Any) -> None:
    runtime = (inputs / "runtime-binding.json").read_bytes()
    public = (inputs / "launch-public.pem").read_bytes()
    action = parameters["action"]
    if action == "runtime_tamper":
        refuses(lambda: pinned_dependency_projection(runtime+b" ", public), "runtime_binding_bytes_mismatch")
    elif action == "public_tamper":
        refuses(lambda: pinned_dependency_projection(runtime, public+b" "), "public_trust_bytes_mismatch")
    elif action == "metadata":
        projection = pinned_dependency_projection(runtime, public)
        require(projection["runtime_version:python"]["version"] == "3.14.3", "pinned future runtime version is not the checker version")
        require(projection["runtime_version:python"]["sha256"] is None, "version metadata is not a binary hash")
        require(any(key.startswith("public_key:") and item["sha256"] == "fa31ffa49bb6f0b464d1b3dd8085d771f77e553985596ff6f7266cc1575b7d0d" for key, item in projection.items()), "fixed public bytes are bound")
    else:
        raise AssertionError("unregistered dependency action")


def manifest_data(inputs: Any) -> dict[str, Any]:
    """Artificial carrier only: the RUN-shaped string is not an allocated ID."""
    runtime = (inputs / "runtime-binding.json").read_bytes()
    public = (inputs / "launch-public.pem").read_bytes()
    contract_hash = "2a7ec3075a59055404a33ceefe0b5531a63e464ed31e1d2a9cb736d584187237"
    schema_hash = "62060930e01b80306a7458623399555dedc80c61f6c77761f72ec2ee7884db3a"
    return {"run": {
        "id": "RUN-ECDLP-000000", "experiment_id": "EXP-ECDLP-1b1b99", "status": "partial_inconclusive",
        "code": {"commit": "a"*40, "dirty": False, "command": "synthetic serialized command; never executed",
                 "dirty_diff_sha256": None, "source_sha256": {"synthetic.py": "b"*64}},
        "inference": {"requested_policy": "executor-mechanical", "canonical_policy": "executor-mechanical",
            "backend": None, "provider": None, "resolved_model_id": None, "model_provenance": "not-applicable",
            "model_verified": True, "requested_reasoning_effort": None, "reasoning_effort": None,
            "fallback_used": False, "fallback_reason": None, "degraded_requirements": [],
            "independent_session": False, "adapter_version": None, "config_digest": None,
            "note": "Artificial deterministic-writer carrier; no model invocation or serving claim."},
        "environment": {"operating_system": "Darwin", "architecture": "arm64", "sage_version": "10.9",
            "python_version": "3.14.3", "dependencies": pinned_dependency_projection(runtime, public),
            "runtime_binding_sha256": "b4919db935d24e7ec756daaf9c59cbbf2e663407f2c621b3e752d2b25bded27f"},
        "inputs": {"curve_id": None, "seed": None, "fixture_artifact": "fixtures.json", "parameters": {
            "fixture_ids": list(FIXTURES), "endpoint_ids": list(ENDPOINTS), "coordinate_values": list(COORDINATES),
            "seed_values": list(SEEDS), "q_values": list(QS), "arm_values": list(range(1,8)),
            "timing_block_values": list(range(7)), "primary_seed": 606103, "primary_q": 4096,
            "required_primary_cells": 36, "effective_contract_sha256": contract_hash}},
        "timing": {"started_at": "2026-01-01T00:00:00Z", "finished_at": "2026-01-01T00:00:01+00:00",
                   "wall_seconds": 1.0, "wall_nanoseconds": 1000000000},
        "resources": {"peak_rss_bytes": 0, "peak_rss_unavailable_reason": None, "cpu_seconds": 0.0,
            "cpu_nanoseconds": 0, "cpu_unavailable_reason": None, "measurement_scope": "whole_process_group"},
        "result": {"metrics": {"R_cells": [], "R_global": [], "q_star": [], "branch": "inconclusive",
            "coverage": {"accepted_fixtures": 0, "resolved_primary_cells": 0, "main_block_rows": 0,
                "selection_block_rows": 0, "top_block_rows": 0, "identity_block_rows": 0, "all_controls_passed": False}},
            "valid": False, "invalid_reason": "MATRIX_INCOMPLETE", "reason_code": "MATRIX_INCOMPLETE",
            "stage": "replay_verify_and_reduce", "certificate": {"kind": "none", "verified": None, "verifier": None}},
        "artifacts": {}, "directory": {"path": "/synthetic/nonlaunch", "path_sha256": hashlib.sha256(b"/synthetic/nonlaunch").hexdigest()},
        "admission": {"authorization_payload_sha256": "c"*64, "effective_contract_sha256": contract_hash,
            "schema_sha256": schema_hash, "handoff_sha256": "d"*64, "implementation_snapshot_commit": "e"*40,
            "review_archive_commit": "f"*40, "review_report_sha256": "1"*64},
    }}


def manifest_control(contract: CostContract, parameters: dict[str, Any], inputs: Any) -> None:
    original = manifest_data(inputs)
    # Independent expected inputs are fixed before mutating the candidate.
    expected_admission = copy.deepcopy(original["run"]["admission"])
    expected_code = copy.deepcopy(original["run"]["code"])
    candidate = copy.deepcopy(original)
    action = parameters["action"]
    if action == "source_digest":
        candidate["run"]["code"]["source_sha256"]["synthetic.py"] = "2"*64
    elif action == "handoff_digest":
        candidate["run"]["admission"]["handoff_sha256"] = "2"*64
    elif action == "dependency_digest":
        key = next(key for key in candidate["run"]["environment"]["dependencies"] if key.startswith("file:"))
        candidate["run"]["environment"]["dependencies"][key]["sha256"] = "2"*64
    elif action == "parameter_contract":
        candidate["run"]["inputs"]["parameters"]["effective_contract_sha256"] = "2"*64
    elif action != "metadata":
        raise AssertionError("unregistered manifest-binding action")
    def compare() -> Any:
        return compare_manifest_bindings(contract, candidate,
            runtime_bytes=(inputs / "runtime-binding.json").read_bytes(),
            public_key_bytes=(inputs / "launch-public.pem").read_bytes(),
            expected_admission=expected_admission, expected_code=expected_code)
    if action == "metadata":
        result = compare()
        require(result["metadata_bindings_match"] and not result["installed_runtime_verified"] and not result["authorization_authenticated"],
                "metadata equality does not become runtime or authorization evidence")
    else:
        refuses(compare)


def companion_control(contract: CostContract, parameters: dict[str, Any], inputs: Any) -> None:
    manifest = manifest_data(inputs)
    payload = b"synthetic companion data\n"
    manifest["run"]["artifacts"] = {"command.txt": {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}}
    action = parameters["action"]
    streams = [("command.txt", [payload[:3], payload[3:]])]
    if action == "tamper":
        streams = [("command.txt", [payload+b"x"])]
    elif action == "missing":
        streams = []
    elif action == "duplicate":
        streams += [("command.txt", [payload])]
    elif action == "self_hash":
        streams = [("manifest.yaml", [payload])]
    elif action != "exact":
        raise AssertionError("unregistered companion action")
    if action == "exact":
        result = compare_companion_bytes(contract, manifest, streams)
        require(result["observed_bytes"] == len(payload) and not result["artifact_semantics_validated"], "exact stream bytes only")
    else:
        refuses(lambda: compare_companion_bytes(contract, manifest, streams))


def manifest_relation_control(contract: CostContract, parameters: dict[str, Any], inputs: Any) -> None:
    manifest = manifest_data(inputs)
    run = manifest["run"]
    action = parameters["action"]
    if action == "same_instant":
        run["timing"].update(started_at="2026-01-01T00:00:00.000000001Z",
                             finished_at="2026-01-01T00:00:00.000000001+00:00")
        # UTC instants are independent of the observed monotonic wall timer;
        # no equality between these distinct clock sources is manufactured.
        contract.validate_manifest_local_relations(manifest)
        return
    if action == "nanosecond_regression":
        run["timing"].update(started_at="2026-01-01T00:00:00.000000002Z",
                             finished_at="2026-01-01T00:00:00.000000001Z")
    elif action == "calendar":
        run["timing"]["started_at"] = "2026-02-30T00:00:00Z"
    elif action == "display":
        run["timing"]["wall_seconds"] = 2.0
    elif action == "cpu_reason":
        run["resources"]["cpu_unavailable_reason"] = "capture_failed"
    elif action == "cpu_unknown_display":
        run["resources"].update(cpu_nanoseconds=None, cpu_unavailable_reason="capture_failed", cpu_seconds=0.0)
    elif action == "policy_alias":
        run["inference"]["requested_policy"] = "different-policy"
    elif action == "wrong_stage":
        run["result"]["stage"] = "authorize_and_claim_nonce"
    elif action == "invalid_reason":
        run["result"]["invalid_reason"] = "CONTROL_FAILED"
    elif action == "invalid_success_branch":
        run["result"]["metrics"]["branch"] = "finite_panel_signal_only"
    else:
        raise AssertionError("unregistered manifest relation action")
    refuses(lambda: contract.validate_manifest_local_relations(manifest))


def storage_failure_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    import sqlite3
    from unittest.mock import patch
    action = parameters["action"]
    if action == "initialize":
        with patch("sqlite3.connect", side_effect=sqlite3.OperationalError("synthetic connection failure")):
            try:
                CostLedger(contract, scratch)
            except CostError as error:
                require(error.code == "ledger_index_initialization_failed", "initialization is a typed infrastructure failure")
                require(error.primary_error["type"] == "OperationalError", "primary failure retained")
                require(error.retained_directory is not None, "owned temporary path retained")
            else:
                raise AssertionError("injected initialization failure was not observed")
        return
    ledger = CostLedger(contract, scratch)
    ledger.add(raw_record())
    ledger.finalize()
    actual = ledger._db

    class ConnectionProxy:
        def execute(self, *args: Any, **kwargs: Any) -> Any:
            if action in ("lookup", "iterate"):
                raise sqlite3.OperationalError("synthetic read failure")
            return actual.execute(*args, **kwargs)

        def close(self) -> None:
            actual.close()
            if action == "cleanup_preserves_primary":
                raise sqlite3.OperationalError("synthetic reported close failure after actual close")

    ledger._db = ConnectionProxy()
    try:
        if action == "lookup":
            refuses(lambda: ledger.get("synthetic-row-1"), "ledger_lookup_failed")
        elif action == "iterate":
            refuses(lambda: list(ledger.iter_rows()), "ledger_iteration_failed")
        elif action == "cleanup_preserves_primary":
            try:
                with ledger:
                    raise ValueError("synthetic primary failure")
            except ValueError as error:
                require(str(error) == "synthetic primary failure", "cleanup did not replace the primary failure")
                require(len(ledger.cleanup_errors) == 1, "cleanup failure separately retained")
            else:
                raise AssertionError("primary failure was suppressed")
        else:
            raise AssertionError("unregistered storage failure action")
    finally:
        # The real connection is closed even when the proxy reports failure.
        actual.close()


def interval_neighbour_control(contract: CostContract, parameters: dict[str, Any], scratch: Any) -> None:
    offset = 10**100 if parameters.get("large_offset") else 0
    with CostLedger(contract, scratch) as ledger:
        for i, (start, finish) in enumerate(parameters["spans"]):
            row = raw_record(ordinal=i+1)
            row.update(CPU_nanoseconds=finish-start, wall_nanoseconds=finish-start)
            row["capture_interval"].update(stream_id="synthetic-arrival-"+str(i),
                cpu_started_ns=offset+start, cpu_finished_ns=offset+finish,
                wall_started_ns=offset+start, wall_finished_ns=offset+finish)
            if i == len(parameters["spans"])-1 and parameters["refuse_last"]:
                refuses(lambda: ledger.add(row), "overlapping_exclusive_capture")
            else:
                ledger.add(row)
        if not parameters["refuse_last"]:
            ledger.finalize()
            require(actual_campaign_accounting(ledger)["CPU_nanoseconds"] == sum(end-begin for begin,end in parameters["spans"]),
                    "disjoint or empty spans retain exact physical totals")


def run_frozen_suite(attempt: Any) -> int:
    """One checker worker; outer source/process/RSS custody remains mandatory."""
    import json
    import os
    from pathlib import Path
    import re
    import signal
    import time
    import traceback

    attempt = Path(attempt).resolve(strict=True)
    coverage_bytes = (attempt / "coverage.json").read_bytes()
    coverage = json.loads(coverage_bytes)
    # A registry or compile invocation is still a supervised attempt. This
    # gate is not permission to invoke this draft as a diagnostic.
    if coverage.get("status") != "frozen_before_first_suite" or coverage.get("remaining_controls"):
        raise RuntimeError("coverage is not frozen and complete")
    cases = coverage["cases"]
    if not cases or len(cases) > 512 or len({case["id"] for case in cases}) != len(cases):
        raise RuntimeError("invalid fixed control registry cardinality or identities")
    dispatch = {
        "crosswalk_control": (crosswalk_control, "contract"),
        "candidate_control": (candidate_control, "parameters"),
        "panel_control": (panel_control, "parameters"),
        "timing_control": (timing_control, "parameters"),
        "json_control": (json_control, "parameters"),
        "csv_control": (csv_control, "contract"),
        "ledger_control": (ledger_control, "scratch"),
        "allocation_control": (allocation_control, "scratch"),
        "selection_control": (selection_control, "parameters"),
        "reduction_edge_control": (reduction_edge_control, "parameters"),
        "hard_control": (hard_control, "contract"),
        "resource_control": (resource_control, "contract"),
        "owner_control": (owner_control, "contract"),
        "operation_control": (operation_control, "scratch"),
        "checkpoint_control": (checkpoint_control, "scratch"),
        "joint_control": (joint_control, "parameters"),
        "connected_control": (connected_control, "scratch"),
        "partial_control": (partial_control, "scratch"),
        "selection_rollup_control": (selection_rollup_control, "scratch"),
        "dependency_control": (dependency_control, "inputs"),
        "manifest_control": (manifest_control, "contract_inputs"),
        "companion_control": (companion_control, "contract_inputs"),
        "manifest_relation_control": (manifest_relation_control, "contract_inputs"),
        "storage_failure_control": (storage_failure_control, "scratch"),
        "interval_neighbour_control": (interval_neighbour_control, "scratch"),
    }
    for case in cases:
        if (type(case.get("id")) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", case["id"]) is None or
            case.get("function") not in dispatch or type(case.get("parameters")) is not dict or
            not case.get("expected_predicate") or not case.get("contract_pointer")):
            raise RuntimeError("incomplete named control definition")
    contract = CostContract((attempt / "inputs" / "contract.yaml").read_bytes(),
                            (attempt / "inputs" / "schema.json").read_bytes())
    scratch_parent = attempt / "case-scratch"
    scratch_parent.mkdir(exist_ok=False)

    def timed_out(signum: int, frame: Any) -> None:
        raise TimeoutError("fixed control exceeded 10-second process watchdog")

    previous_handler = signal.signal(signal.SIGALRM, timed_out)
    failures = 0
    try:
        with (attempt / "case-journal.jsonl").open("x", encoding="utf-8") as journal:
            def persist(row: dict[str, Any]) -> None:
                journal.write(json.dumps(row, sort_keys=True, ensure_ascii=True, allow_nan=False) + "\n")
                journal.flush()
                os.fsync(journal.fileno())

            for case in cases:
                started_wall, started_cpu = time.monotonic_ns(), time.process_time_ns()
                identity = hashlib.sha256(json.dumps(case, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")).encode()).hexdigest()
                persist({"event": "case_start", "id": case["id"], "pid": os.getpid(),
                         "case_definition_sha256": identity, "monotonic_ns": started_wall,
                         "process_cpu_ns": started_cpu})
                signal.setitimer(signal.ITIMER_REAL, 10.0)
                error = None
                try:
                    body, mode = dispatch[case["function"]]
                    if mode == "parameters":
                        body(case["parameters"])
                    elif mode == "contract":
                        body(contract, case["parameters"])
                    elif mode == "inputs":
                        body(case["parameters"], attempt / "inputs")
                    elif mode == "contract_inputs":
                        body(contract, case["parameters"], attempt / "inputs")
                    else:
                        scratch = scratch_parent / case["id"]
                        scratch.mkdir(exist_ok=False)
                        body(contract, case["parameters"], scratch)
                except Exception as failure:
                    failures += 1
                    error = {"type": type(failure).__name__, "detail": str(failure),
                             "traceback": traceback.format_exc()}
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0.0)
                persist({"event": "case_result", "id": case["id"], "pid": os.getpid(),
                         "outcome": "pass" if error is None else "fail", "error": error,
                         "wall_ns": time.monotonic_ns() - started_wall,
                         "process_cpu_ns": time.process_time_ns() - started_cpu})
            persist({"event": "suite_terminal", "controls_completed": len(cases),
                     "failed": failures, "scientific_runs": 0, "fixture_children": 0})
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)
    return 1 if failures else 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    arguments = parser.parse_args()
    raise SystemExit(run_frozen_suite(arguments.attempt))
