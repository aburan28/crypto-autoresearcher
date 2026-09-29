"""Exact reductions of supplied CM accounting observations.

This module does not run a workload or authenticate capture, replay, selection
freeze, or certificate assertions. Its timing carrier preserves those supplied
facts separately from the integer allocated charges used by the estimator.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import gcd
from typing import Any, Iterable, Iterator

from costs import (CostContract, CostError, CostLedger, CostCheckpoint,
                   actual_campaign_accounting, checkpoint_boundary, canonical_json, strict_json_loads)
from allocations import (FIXTURES, ENDPOINTS, CLASSES, INTERVALS, COORDINATES, SEEDS, QS,
                         AllocationContext, require_keys, integer_in,
                         expected_groups, edges_from_groups, validate_allocation_edges,
                         iter_allocation_issues)

BLOCKS = tuple(range(7))
CONTROL_ARMS = {
    "top_control": ("direct_3_iota", "scalar_m"),
    "identity_control": ("identity_iota_identity", "direct_iota"),
}
TIMING_AXES = ("plane", "fixture", "endpoint", "coordinate", "seed", "q", "arm", "block")
UNAVAILABLE = ("missing_input", "invalid_input", "below_resolution",
               "nonpositive_denominator", "invalid_cost_ledger", "infrastructure_stopped")
RESOLUTION_NS = 100_000_000


def nonnegative_integer(value: Any, code: str) -> int:
    if type(value) is not int or value < 0:
        raise CostError(code)
    return value


def decode_fraction(value: Any) -> Fraction:
    require_keys(value, {"numerator", "denominator"}, "fraction_fields")
    n = nonnegative_integer(value["numerator"], "fraction_numerator")
    d = nonnegative_integer(value["denominator"], "fraction_denominator")
    if d == 0 or gcd(n, d) != 1:
        raise CostError("fraction_not_canonical")
    return Fraction(n, d)


def encode_fraction(value: Fraction) -> dict[str, int]:
    if type(value) is not Fraction or value < 0:
        raise CostError("nonnegative_exact_fraction_required")
    return {"numerator": value.numerator, "denominator": value.denominator}


def unavailable(reason: str) -> dict[str, str]:
    if reason not in UNAVAILABLE:
        raise CostError("unavailable_reason_domain")
    return {"kind": "unavailable", "reason": reason}


def timing_key(value: Any) -> tuple[Any, ...]:
    """Validate all axes before using a tuple as an index key."""
    if type(value) is not dict or any(key not in value for key in TIMING_AXES):
        raise CostError("timing_axes_missing")
    plane = value["plane"]
    if type(plane) is not str or plane not in ("main", "selection", *CONTROL_ARMS):
        raise CostError("timing_plane")
    if type(value["fixture"]) is not str or value["fixture"] not in FIXTURES:
        raise CostError("timing_fixture")
    integer_in(value["coordinate"], COORDINATES, "timing_coordinate")
    integer_in(value["seed"], (606101,) if plane == "selection" else SEEDS, "timing_seed")
    integer_in(value["q"], (256,) if plane == "selection" else QS, "timing_q")
    integer_in(value["block"], BLOCKS, "timing_block")
    if plane in CONTROL_ARMS:
        if value["endpoint"] is not None:
            raise CostError("source_control_has_endpoint")
        if type(value["arm"]) is not str or value["arm"] not in CONTROL_ARMS[plane]:
            raise CostError("control_arm")
    else:
        if type(value["endpoint"]) is not str or value["endpoint"] not in ENDPOINTS:
            raise CostError("timing_endpoint")
        integer_in(value["arm"], range(2 if plane == "selection" else 1, 8), "timing_arm")
    return tuple(value[key] for key in TIMING_AXES)


def expected_timing_keys() -> Iterator[tuple[Any, ...]]:
    for plane in ("main", "selection", *CONTROL_ARMS):
        endpoints = (None,) if plane in CONTROL_ARMS else ENDPOINTS
        seeds = (606101,) if plane == "selection" else SEEDS
        qs = (256,) if plane == "selection" else QS
        arms = CONTROL_ARMS[plane] if plane in CONTROL_ARMS else range(2 if plane == "selection" else 1, 8)
        for axes in product(FIXTURES, endpoints, COORDINATES, seeds, qs, arms, BLOCKS):
            yield (plane, *axes)


@dataclass(frozen=True)
class TimingFact:
    key: tuple[Any, ...]
    repetitions: int | None
    observed_cpu_ns: int | None
    reason: str | None
    replay_verified: bool | None
    resource_accounted: bool | None
    observations_complete: bool


def parse_timing_fact(original: Any) -> TimingFact:
    """Read actual cumulative group CPU, not a primary cost surrogate.

    A nullable prefix entry explicitly denotes an unavailable observation.
    Complete observations retain one entry after every whole-q repetition.
    Partial/failed observations cannot become resolved merely because their
    retained prefix crosses the resolution threshold.
    """
    row = strict_json_loads(canonical_json(original))
    require_keys(row, set(TIMING_AXES) | {"record_type", "status", "repetitions",
        "cumulative_group_CPU_nanoseconds", "replay_verified", "resource_accounted"}, "timing_fields")
    if row["record_type"] != "cm_timing_block":
        raise CostError("timing_record_type")
    key = timing_key(row)
    status = row["status"]
    if type(status) is not str or status not in ("complete", "below_resolution", "partial", "failed"):
        raise CostError("timing_status")
    n = row["repetitions"]
    if n is not None:
        integer_in(n, range(1, 101), "timing_repetitions")
    prefix = row["cumulative_group_CPU_nanoseconds"]
    if prefix is not None and type(prefix) is not list:
        raise CostError("timing_prefix_type")
    if prefix is not None and (len(prefix) > 100 or (n is not None and len(prefix) != n)):
        raise CostError("timing_prefix_length")
    previous = None
    if prefix is not None:
        for index, observed in enumerate(prefix):
            if observed is None:
                continue
            nonnegative_integer(observed, "timing_prefix_cpu")
            if previous is not None and observed < previous:
                raise CostError("timing_cpu_regressed", (index,))
            previous = observed
            if index < len(prefix) - 1 and observed >= RESOLUTION_NS:
                raise CostError("timing_repeated_after_stop", (index,))
    for field in ("replay_verified", "resource_accounted"):
        if row[field] is not None and type(row[field]) is not bool:
            raise CostError("timing_prerequisite_type", (field,))
    observed_cpu = prefix[-1] if prefix else None
    if status in ("partial", "failed"):
        reason = "invalid_input"
    elif n is None or prefix is None or any(item is None for item in prefix):
        reason = "missing_input"
    elif n < 100 and observed_cpu < RESOLUTION_NS:
        raise CostError("timing_stopped_before_threshold_or_repetition_cap")
    elif (status == "below_resolution") != (observed_cpu < RESOLUTION_NS):
        raise CostError("timing_resolution_status_mismatch")
    elif observed_cpu < RESOLUTION_NS:
        reason = "below_resolution"
    else:
        reason = None
    if reason is None:
        if any(row[field] is False for field in ("replay_verified", "resource_accounted")):
            reason = "invalid_input"
        elif any(row[field] is None for field in ("replay_verified", "resource_accounted")):
            reason = "missing_input"
    observations_complete = (status in ("complete", "below_resolution") and n is not None and
                             prefix is not None and len(prefix) == n and all(item is not None for item in prefix))
    return TimingFact(key, n, observed_cpu, reason, row["replay_verified"], row["resource_accounted"], observations_complete)


class TimingIndex:
    """Bounded by the fixed 35,280 block identities, not raw capture volume."""

    def __init__(self, rows: Iterable[dict[str, Any]], *, checkpoint: CostCheckpoint | None = None) -> None:
        checkpoint_boundary(checkpoint, "timing_initialize")
        self.checkpoint = checkpoint
        self._facts: dict[tuple[Any, ...], TimingFact] = {}
        for row in rows:
            checkpoint_boundary(checkpoint, "timing_entry")
            fact = parse_timing_fact(row)
            if fact.key in self._facts:
                raise CostError("duplicate_timing_block", fact.key)
            self._facts[fact.key] = fact

    def get(self, key: tuple[Any, ...]) -> TimingFact | None:
        if type(key) is not tuple or len(key) != len(TIMING_AXES):
            raise CostError("timing_lookup_key")
        checked = timing_key(dict(zip(TIMING_AXES, key)))
        return self._facts.get(checked)

    def coverage(self) -> dict[str, int]:
        counts = {plane: 0 for plane in ("main", "selection", *CONTROL_ARMS)}
        for key in self._facts:
            counts[key[0]] += 1
        return counts

    def cost_related_hard_facts(self) -> dict[str, bool]:
        """Derived consistency of retained facts; their authenticity is external."""
        counts = self.coverage()
        return {
            "main_timing_block_row_count_equals_28224": counts["main"] == 28224,
            "top_control_block_row_count_equals_2016": counts["top_control"] == 2016,
            "identity_control_block_row_count_equals_2016": counts["identity_control"] == 2016,
            "every_required_block_present_and_typed_including_below_resolution": (
                len(self._facts) == 35280 and all(fact.observations_complete for fact in self._facts.values())),
            "every_measured_output_replay_valid": bool(self._facts) and all(fact.replay_verified is True for fact in self._facts.values()),
        }

    def iter_unresolved(self) -> Iterator[dict[str, Any]]:
        for key in expected_timing_keys():
            checkpoint_boundary(self.checkpoint, "timing_coverage")
            fact = self._facts.get(key)
            if fact is None or fact.reason is not None:
                yield {"axes": dict(zip(TIMING_AXES, key)),
                       "reason": "missing_input" if fact is None else fact.reason}


@dataclass(frozen=True)
class BlockEstimate:
    """Seven validated normalized blocks plus fixed integer setup.

    Instances are internal reducer values; an external caller cannot establish
    capture completeness by constructing this dataclass.
    """
    setup_ns: int | None
    blocks: tuple[Fraction, ...] | None
    reason: str | None

    def total(self, omitted_block: int | None = None) -> Fraction | None:
        if omitted_block is not None:
            integer_in(omitted_block, BLOCKS, "omission_label")
        if self.reason is not None:
            return None
        nonnegative_integer(self.setup_ns, "integer_setup_required")
        if type(self.blocks) is not tuple or len(self.blocks) != 7:
            raise CostError("seven_original_blocks_required")
        # Validate all seven before applying the omission, including the one
        # being omitted. A malformed original block cannot be rescued.
        if any(type(item) is not Fraction or item < 0 for item in self.blocks):
            raise CostError("invalid_original_normalized_block")
        ordered = sorted(value for label, value in enumerate(self.blocks) if label != omitted_block)
        median = ordered[3] if omitted_block is None else (ordered[2] + ordered[3]) / 2
        return Fraction(self.setup_ns) + median


def estimate_blocks(setup_ns: int | None, setup_reason: str | None,
                    workload: tuple[Any, ...], timing: TimingIndex,
                    charged_blocks: dict[int, int]) -> BlockEstimate:
    """Normalize allocated repeated leaves by retained actual repetition count.

    The caller must derive charged_blocks and setup from validated allocations;
    they are not substitutes for physical-leaf or required-component coverage.
    """
    if type(workload) is not tuple or len(workload) != len(TIMING_AXES) - 1:
        raise CostError("workload_key")
    if setup_ns is None:
        if setup_reason not in UNAVAILABLE:
            raise CostError("missing_setup_reason")
    else:
        nonnegative_integer(setup_ns, "setup_cost")
        if setup_reason is not None:
            raise CostError("observed_setup_has_reason")
    if type(charged_blocks) is not dict:
        raise CostError("charged_blocks_type")
    for label, value in charged_blocks.items():
        integer_in(label, BLOCKS, "charged_block_label")
        nonnegative_integer(value, "charged_block_cpu")
    reason = setup_reason
    normalized = []
    for label in BLOCKS:
        fact = timing.get((*workload, label))
        block_reason = "missing_input" if fact is None or label not in charged_blocks else fact.reason
        if block_reason is not None:
            if reason is None:
                reason = block_reason
        else:
            normalized.append(Fraction(charged_blocks[label], fact.repetitions))
    return BlockEstimate(setup_ns, tuple(normalized) if reason is None else None, reason)


def ratio_of_totals(scalar: Iterable[BlockEstimate], transport: Iterable[BlockEstimate],
                    omitted_block: int | None = None) -> dict[str, Any]:
    scalar, transport = tuple(scalar), tuple(transport)
    if not scalar or len(scalar) != len(transport):
        raise CostError("ratio_endpoint_coverage")
    # Read every original estimate before forming a ratio; setup stays fixed.
    sums = []
    reasons = []
    for estimates in (scalar, transport):
        total = Fraction(0)
        for estimate in estimates:
            if type(estimate) is not BlockEstimate:
                raise CostError("ratio_requires_internal_estimates")
            value = estimate.total(omitted_block)
            if value is None:
                if estimate.reason not in UNAVAILABLE:
                    raise CostError("estimate_unavailable_reason")
                reasons.append(estimate.reason)
            else:
                total += value
        sums.append(total)
    if reasons:
        return unavailable(reasons[0])
    if sums[1] <= 0:
        return unavailable("nonpositive_denominator")
    return {"kind": "value", "value": encode_fraction(sums[0] / sums[1])}


def select_candidates(estimates: dict[tuple[str, str, int, int], BlockEstimate]) -> list[dict[str, Any]]:
    """Exact six-candidate/eight-endpoint selection, without dropping invalids.

    Keys are fixture, endpoint, coordinate, candidate arm. This internal map is
    populated only from the selection_score_candidate allocation projection.
    """
    if type(estimates) is not dict:
        raise CostError("selection_estimate_map")
    expected = set(product(FIXTURES, ENDPOINTS, COORDINATES, range(2, 8)))
    for key in estimates:
        if type(key) is not tuple or len(key) != 4:
            raise CostError("selection_estimate_key")
        f, e, u, arm = key
        if type(f) is not str or type(e) is not str or f not in FIXTURES or e not in ENDPOINTS:
            raise CostError("selection_estimate_identity")
        integer_in(u, COORDINATES, "selection_estimate_coordinate")
        integer_in(arm, range(2, 8), "selection_estimate_arm")
    if set(estimates) - expected:
        raise CostError("extra_selection_estimate")
    results = []
    for interval, coordinate in product(INTERVALS, COORDINATES):
        scores = []
        reason = None
        for arm in range(2, 8):
            score = Fraction(0)
            candidate_reason = None
            for fixture, endpoint in product((interval + "F0", interval + "F1"), ENDPOINTS):
                estimate = estimates.get((fixture, endpoint, coordinate, arm))
                if estimate is None:
                    candidate_reason = candidate_reason or "missing_input"
                elif type(estimate) is not BlockEstimate:
                    raise CostError("selection_requires_internal_estimate")
                else:
                    value = estimate.total()
                    if value is None:
                        if estimate.reason not in UNAVAILABLE:
                            raise CostError("selection_estimate_reason")
                        candidate_reason = candidate_reason or estimate.reason
                    else:
                        score += value
            if candidate_reason is not None:
                reason = reason or candidate_reason
                scores.append({"arm": arm, "score": unavailable(candidate_reason)})
            else:
                scores.append({"arm": arm, "score": {"kind": "value", "value": encode_fraction(score / 8)}})
        winner = None if reason is not None else min(scores, key=lambda item: (decode_fraction(item["score"]["value"]), item["arm"]))["arm"]
        results.append({"interval": interval, "coordinate": coordinate,
                        "scores": scores, "winner": winner, "reason": reason})
    return results


def q_star_from_ladder(ratios: dict[int, dict[str, Any]]) -> dict[str, Any]:
    if type(ratios) is not dict or len(ratios) != len(QS):
        raise CostError("q_star_ladder_coverage")
    for q in ratios:
        integer_in(q, QS, "q_star_q")
    values = {}
    for q in QS:
        row = ratios[q]
        if type(row) is not dict:
            raise CostError("ratio_carrier")
        if row.get("kind") == "value":
            require_keys(row, {"kind", "value"}, "ratio_value_fields")
            values[q] = decode_fraction(row["value"])
        elif row.get("kind") == "unavailable":
            require_keys(row, {"kind", "reason"}, "ratio_unavailable_fields")
            if row["reason"] not in UNAVAILABLE:
                raise CostError("ratio_unavailable_reason")
            values[q] = None
        else:
            raise CostError("ratio_kind")
    for q in QS:
        if values[q] is None:
            return {"kind": "unresolved"}
        if values[q] >= 1:
            return {"kind": "crossing", "q": q}
    return {"kind": "greater_than_4096"}


def panel_cost_outputs(context: AllocationContext,
                       estimates: dict[tuple[str, str, str, int, int, int], BlockEstimate]
                       ) -> dict[str, Any]:
    """Produce the full 288/8/36 cost projection, including explicit unknowns.

    Keys are view, fixture, endpoint, coordinate, seed, q. This function is a
    cost projection only: it neither emits a whole-run validity flag nor chooses
    the final statistical branch without the independent hard prerequisites.
    """
    if type(estimates) is not dict:
        raise CostError("panel_estimate_map")
    for key, value in estimates.items():
        if type(key) is not tuple or len(key) != 6:
            raise CostError("panel_estimate_key")
        view, fixture, endpoint, coordinate, seed, q = key
        if type(view) is not str or view not in ("scalar", "transport"):
            raise CostError("panel_strategy")
        if type(fixture) is not str or type(endpoint) is not str or fixture not in FIXTURES or endpoint not in ENDPOINTS:
            raise CostError("panel_endpoint")
        integer_in(coordinate, COORDINATES, "panel_coordinate")
        integer_in(seed, SEEDS, "panel_seed")
        integer_in(q, QS, "panel_q")
        if type(value) is not BlockEstimate:
            raise CostError("panel_requires_internal_estimate")
    missing = BlockEstimate(None, None, "missing_input")

    def endpoint(view: str, fixture: str, label: str, coordinate: int, seed: int, q: int) -> BlockEstimate:
        return estimates.get((view, fixture, label, coordinate, seed, q), missing)

    cells = []
    ladders: dict[tuple[str, str, int], dict[int, dict[str, Any]]] = {}
    for fixture, class_id, coordinate, seed, q in product(FIXTURES, CLASSES, COORDINATES, SEEDS, QS):
        labels = context.class_labels(fixture, class_id)
        governing = seed == 606103 and q == 4096
        if labels is None:
            ratio = unavailable("missing_input")
            loo = [dict(unavailable("missing_input"), omitted_block=b) for b in BLOCKS] if governing else []
        else:
            scalar = tuple(endpoint("scalar", fixture, label, coordinate, seed, q) for label in labels)
            transport = tuple(endpoint("transport", fixture, label, coordinate, seed, q) for label in labels)
            ratio = ratio_of_totals(scalar, transport)
            loo = [dict(ratio_of_totals(scalar, transport, b), omitted_block=b) for b in BLOCKS] if governing else []
        cells.append({"fixture": fixture, "class": class_id, "coordinate": coordinate,
                      "seed": seed, "q": q, "ratio": ratio, "leave_one_out": loo})
        if seed == 606103:
            ladders.setdefault((fixture, class_id, coordinate), {})[q] = ratio
    global_rows = []
    for seed, q in product(SEEDS, QS):
        if not context.fixtures_complete:
            ratio = unavailable("missing_input")
        else:
            scalar = [endpoint("scalar", f, e, u, seed, q) for f, e, u in product(FIXTURES, ENDPOINTS, COORDINATES)]
            transport = [endpoint("transport", f, e, u, seed, q) for f, e, u in product(FIXTURES, ENDPOINTS, COORDINATES)]
            ratio = ratio_of_totals(scalar, transport)
        global_rows.append({"seed": seed, "q": q, "ratio": ratio})
    stars = [{"fixture": f, "class": c, "coordinate": u,
              "result": q_star_from_ladder(ladders[(f, c, u)])}
             for f, c, u in product(FIXTURES, CLASSES, COORDINATES)]
    return {"R_cells": cells, "R_global": global_rows, "q_star": stars}


class AllocationReduction:
    """Connect exact retained physical rows and edges to the cost projection.

    The inventory comparison is mandatory but does not authenticate the
    independent journal. Fixed workload/block aggregates bound memory; raw
    leaf records stay in CostLedger's owned disk index.
    """

    def __init__(self, ledger: CostLedger, context: AllocationContext,
                 timing: TimingIndex, supplied_edges: Iterable[dict[str, Any]]) -> None:
        if not ledger.capture_inventory_compared:
            raise CostError("reduction_requires_independent_capture_inventory_comparison")
        edge_check = validate_allocation_edges(ledger, context, iter(supplied_edges))
        if edge_check["unresolved_row_count"]:
            # No incomplete row is silently skipped into a zero-cost estimate.
            # Retained rows and iter_allocation_issues remain available to the
            # caller for the partial-outcome carrier.
            raise CostError("allocation_projection_unresolved")
        self.context = context
        self.timing = timing
        self._setup: dict[tuple[Any, ...], int] = {}
        self._blocks: dict[tuple[Any, ...], dict[int, int]] = {}
        self._repetitions: dict[tuple[Any, ...], int] = {}
        self._component_repetitions: dict[tuple[Any, ...], dict[str, int]] = {}
        self._warmup: set[tuple[Any, ...]] = set()
        self._warmup_verification: set[tuple[Any, ...]] = set()
        self._invalid: set[tuple[Any, ...]] = set()
        for row in ledger.iter_rows():
            if row["charge_kind"] != "exclusive_leaf":
                continue
            family = ledger.contract.crosswalk[row["component"]]["family"]
            if family == "arm_context":
                workload = tuple(row[name] for name in TIMING_AXES[:-1])
                # Reuse the closed timing axis check for each raw workload.
                timing_key(dict(zip(TIMING_AXES, (*workload, 0))))
                if row["status"] in ("partial", "failed", "below_resolution"):
                    self._invalid.add(workload)
                if row["component"] in ("transport_warmup", "scalar_warmup"):
                    self._warmup.add(workload)
                if row["component"] == "warmup_verification":
                    self._warmup_verification.add(workload)
                if row["scope"] == "block_repetition":
                    block_key = (*workload, row["block"])
                    fact = timing.get(block_key)
                    if fact is not None and fact.repetitions is not None and row["repetition"] > fact.repetitions:
                        raise CostError("raw_repetition_exceeds_retained_count", block_key)
                    self._repetitions[block_key] = self._repetitions.get(block_key, 0) | (1 << (row["repetition"] - 1))
                    components = self._component_repetitions.setdefault(block_key, {})
                    components[row["component"]] = components.get(row["component"], 0) | (1 << (row["repetition"] - 1))
            groups, issues = expected_groups(ledger.contract, row, context)
            if issues:
                raise CostError("allocation_changed_during_reduction")
            for edge in edges_from_groups(row, groups):
                view = edge["strategy_view"]
                if view == "actual_only_scaffolding":
                    continue
                if row["status"] in ("partial", "failed"):
                    raise CostError("primary_projection_has_partial_physical_charge", (row["raw_cost_row_id"],))
                target = edge["target"]
                scenario = edge["scenario"]
                if view == "selection_score_candidate":
                    projection_key = (view, target["fixture"], target["endpoint"], target["coordinate"], scenario["candidate_arm"])
                else:
                    projection_key = (view, target["fixture"], target["endpoint"], target["coordinate"], scenario["seed"], scenario["q"])
                charge = nonnegative_integer(edge["allocated_CPU_nanoseconds"], "allocated_cpu_unavailable")
                repeated = row["scope"] == "block_repetition" and (
                    view == "selection_score_candidate" or row["plane"] == "main")
                if repeated:
                    block = row["block"]
                    charges = self._blocks.setdefault(projection_key, {})
                    charges[block] = charges.get(block, 0) + charge
                else:
                    # Actual selection repetitions enter H in every scalar
                    # cold scenario. Only candidate-score copies normalize them.
                    self._setup[projection_key] = self._setup.get(projection_key, 0) + charge

    def _estimate(self, projection_key: tuple[Any, ...], workload: tuple[Any, ...]) -> BlockEstimate:
        reason = None
        if workload in self._invalid:
            reason = "invalid_input"
        elif workload not in self._warmup or workload not in self._warmup_verification:
            reason = "missing_input"
        for label in BLOCKS:
            fact = self.timing.get((*workload, label))
            if fact is not None and fact.repetitions is not None:
                mask = self._repetitions.get((*workload, label), 0)
                if mask != (1 << fact.repetitions) - 1:
                    reason = reason or "missing_input"
                # A serialization or verification leaf alone cannot stand in
                # for the required evaluator. These are the explicit outer
                # call-path components; opaque arm7 internals are not invented.
                required = ("psi_evaluation", "iota_evaluation", "phi_evaluation") if workload[-1] == 1 else ("scalar_multiplication",)
                required += ("output_verification", "query_serialization")
                if workload[-1] in (3, 4, 5, 6):
                    required += ("every_per_point_table",)
                observed = self._component_repetitions.get((*workload, label), {})
                if any(observed.get(component, 0) != (1 << fact.repetitions) - 1 for component in required):
                    reason = reason or "missing_input"
        setup = self._setup.get(projection_key)
        if setup is None:
            reason = reason or "missing_input"
        if reason is not None:
            return BlockEstimate(setup, None, reason)
        return estimate_blocks(setup, None, workload, self.timing, self._blocks.get(projection_key, {}))

    def selection_estimates(self) -> dict[tuple[str, str, int, int], BlockEstimate]:
        result = {}
        for fixture, endpoint, coordinate, arm in product(FIXTURES, ENDPOINTS, COORDINATES, range(2, 8)):
            key = (fixture, endpoint, coordinate, arm)
            workload = ("selection", fixture, endpoint, coordinate, 606101, 256, arm)
            result[key] = self._estimate(("selection_score_candidate", *key), workload)
        return result

    def outputs(self) -> dict[str, Any]:
        selections = select_candidates(self.selection_estimates())
        resolved = {}
        for selection in selections:
            key = (selection["interval"], selection["coordinate"])
            frozen = self.context.winner(*key)
            winner = selection["winner"]
            if winner is not None and frozen is not None and frozen != winner:
                raise CostError("frozen_winner_disagrees_with_retained_selection", key)
            resolved[key] = winner is not None and winner == frozen
        estimates = {}
        for fixture, endpoint, coordinate, seed, q in product(FIXTURES, ENDPOINTS, COORDINATES, SEEDS, QS):
            stratum = (fixture[:2], coordinate)
            winner = self.context.winner(*stratum)
            for view in ("scalar", "transport"):
                key = (view, fixture, endpoint, coordinate, seed, q)
                # An unresolved selection stratum cannot supply a primary
                # comparison, including its transport half.
                if not resolved[stratum]:
                    estimates[key] = BlockEstimate(None, None, "missing_input")
                    continue
                arm = 1 if view == "transport" else winner
                workload = ("main", fixture, endpoint, coordinate, seed, q, arm)
                estimates[key] = self._estimate(key, workload)
        return {"selection": selections, "cost_projection": panel_cost_outputs(self.context, estimates),
                "timing_coverage": self.timing.coverage(),
                "capture_authenticity_verified": False, "scientific_admission": False}


def supplied_hard_prerequisites(contract: CostContract, original: Any) -> dict[str, Any]:
    """Evaluate the exact frozen conjunction over explicitly supplied facts.

    The caller must establish each fact independently. This function checks
    their conjunction, and does not establish authorization or any fact's truth.
    Missing and nullable entries remain visible and cannot count as true.
    """
    supplied = strict_json_loads(canonical_json(original))
    names = contract.contract["runner"]["hard_validity_reducer"]["completed_valid_if_and_only_if"]
    if type(supplied) is not dict or any(key not in names for key in supplied):
        raise CostError("hard_prerequisite_fields")
    for key, value in supplied.items():
        if value is not None and type(value) is not bool:
            raise CostError("hard_prerequisite_boolean", (key,))
    missing = [name for name in names if name not in supplied or supplied[name] is None]
    rejected = [name for name in names if supplied.get(name) is False]
    return {"supplied_conjunction": bool(names) and not missing and not rejected,
            "missing_or_unknown": missing, "explicit_false": rejected,
            "prerequisites_authenticated_by_component": False}


def _ratio_value(original: Any) -> Fraction | None:
    if type(original) is not dict:
        raise CostError("ratio_object")
    if original.get("kind") == "value":
        require_keys(original, {"kind", "value"}, "ratio_fields")
        return decode_fraction(original["value"])
    require_keys(original, {"kind", "reason"}, "ratio_unavailable_fields")
    if original["kind"] != "unavailable" or original["reason"] not in UNAVAILABLE:
        raise CostError("ratio_unavailable_domain")
    return None


def index_cells(original: Any) -> dict[tuple[Any, ...], dict[str, Any]]:
    """Identity validation permits whole labelled LOO-item permutations."""
    if type(original) is not list or len(original) != 288:
        raise CostError("cell_coverage_288_required")
    result = {}
    for row in original:
        require_keys(row, {"fixture", "class", "coordinate", "seed", "q", "ratio", "leave_one_out"}, "cell_fields")
        if type(row["fixture"]) is not str or row["fixture"] not in FIXTURES or type(row["class"]) is not str or row["class"] not in CLASSES:
            raise CostError("cell_identity")
        integer_in(row["coordinate"], COORDINATES, "cell_coordinate")
        integer_in(row["seed"], SEEDS, "cell_seed")
        integer_in(row["q"], QS, "cell_q")
        key = tuple(row[name] for name in ("fixture", "class", "coordinate", "seed", "q"))
        if key in result:
            raise CostError("duplicate_cell", key)
        _ratio_value(row["ratio"])
        loo = row["leave_one_out"]
        if type(loo) is not list:
            raise CostError("loo_array")
        governing = row["seed"] == 606103 and row["q"] == 4096
        if len(loo) != (7 if governing else 0):
            raise CostError("loo_coverage")
        labels = {}
        for item in loo:
            if type(item) is not dict or "omitted_block" not in item:
                raise CostError("loo_item")
            label = item["omitted_block"]
            integer_in(label, BLOCKS, "loo_label")
            if label in labels:
                raise CostError("duplicate_loo_label")
            ratio = {name: value for name, value in item.items() if name != "omitted_block"}
            _ratio_value(ratio)
            labels[label] = item
        result[key] = dict(row, leave_one_out=[labels[b] for b in BLOCKS] if governing else [])
    return result


def statistical_branch(cells: Any, hard_prerequisites_hold: bool) -> str:
    """A conditional branch projection, not an authenticated run decision."""
    if type(hard_prerequisites_hold) is not bool:
        raise CostError("hard_prerequisite_conjunction_boolean")
    indexed = index_cells(cells)
    all_positive = True
    all_negative = True
    all_resolved = True
    for fixture, class_id, coordinate in product(FIXTURES, CLASSES, COORDINATES):
        row = indexed[(fixture, class_id, coordinate, 606103, 4096)]
        ratios = [row["ratio"], *[{key: value for key, value in item.items() if key != "omitted_block"} for item in row["leave_one_out"]]]
        for ratio in ratios:
            value = _ratio_value(ratio)
            if value is None:
                all_resolved = False
            else:
                all_positive = all_positive and value >= Fraction(6, 5)
                all_negative = all_negative and value <= 1
    if not hard_prerequisites_hold or not all_resolved:
        return "inconclusive"
    if all_positive:
        return "finite_panel_signal_only"
    if all_negative:
        return "exact_finite_cost_gap_only"
    return "inconclusive"


def compare_cell_projection(expected: Any, supplied: Any) -> dict[str, Any]:
    """Compare every exact ratio and labelled omission, independent of order."""
    left, right = index_cells(expected), index_cells(supplied)
    for key in left:
        if canonical_json(left[key]) != canonical_json(right[key]):
            raise CostError("cell_projection_disagrees_with_retained_costs", key)
    return {"cells_compared": len(left), "labelled_omissions_compared": 252,
            "whole_manifest_validated": False}


def _index_global(rows: Any) -> dict[tuple[int, int], dict[str, Any]]:
    if type(rows) is not list or len(rows) != 8:
        raise CostError("global_coverage_eight_required")
    result = {}
    for row in rows:
        require_keys(row, {"seed", "q", "ratio"}, "global_fields")
        integer_in(row["seed"], SEEDS, "global_seed")
        integer_in(row["q"], QS, "global_q")
        key = (row["seed"], row["q"])
        if key in result:
            raise CostError("duplicate_global_alternative", key)
        _ratio_value(row["ratio"])
        result[key] = row
    return result


def _index_q_star(rows: Any) -> dict[tuple[str, str, int], dict[str, Any]]:
    if type(rows) is not list or len(rows) != 36:
        raise CostError("q_star_coverage_36_required")
    result = {}
    for row in rows:
        require_keys(row, {"fixture", "class", "coordinate", "result"}, "q_star_fields")
        if type(row["fixture"]) is not str or row["fixture"] not in FIXTURES or type(row["class"]) is not str or row["class"] not in CLASSES:
            raise CostError("q_star_identity")
        integer_in(row["coordinate"], COORDINATES, "q_star_coordinate")
        key = (row["fixture"], row["class"], row["coordinate"])
        if key in result:
            raise CostError("duplicate_q_star_cell", key)
        value = row["result"]
        if type(value) is not dict:
            raise CostError("q_star_result_type")
        if value.get("kind") == "crossing":
            require_keys(value, {"kind", "q"}, "q_star_crossing_fields")
            integer_in(value["q"], QS, "q_star_crossing_q")
        else:
            require_keys(value, {"kind"}, "q_star_unresolved_fields")
            if value["kind"] not in ("greater_than_4096", "unresolved"):
                raise CostError("q_star_kind")
        result[key] = row
    return result


def compare_cost_projection(expected: Any, supplied: Any) -> dict[str, Any]:
    """All three output identity sets must match retained-cost reductions."""
    for value in (expected, supplied):
        require_keys(value, {"R_cells", "R_global", "q_star"}, "cost_projection_fields")
    cell_check = compare_cell_projection(expected["R_cells"], supplied["R_cells"])
    for name, indexer in (("R_global", _index_global), ("q_star", _index_q_star)):
        left, right = indexer(expected[name]), indexer(supplied[name])
        for key in left:
            if canonical_json(left[key]) != canonical_json(right[key]):
                raise CostError("cost_projection_disagrees_with_retained_data", (name, *key))
    return dict(cell_check, global_alternatives_compared=8, q_star_cells_compared=36)


def compare_manifest_costs(contract: CostContract, manifest: Any,
                           reduction: AllocationReduction,
                           prerequisites: Any) -> dict[str, Any]:
    """Recompute the cost-related manifest fields from retained observations.

    This does not accept a manifest as a source of its own prerequisite facts.
    An external trusted integration supplies those facts separately. Full
    artifact/resource/authorization validation remains outside this component.
    """
    checked = contract.validate_manifest_local_relations(manifest)
    run = checked["run"]
    metrics = run["result"]["metrics"]
    outputs = reduction.outputs()
    expected = outputs["cost_projection"]
    projection_check = compare_cost_projection(expected, {name: metrics[name] for name in ("R_cells", "R_global", "q_star")})
    hard = supplied_hard_prerequisites(contract, prerequisites)
    for name, observed in reduction.timing.cost_related_hard_facts().items():
        if prerequisites.get(name) is True and not observed:
            raise CostError("supplied_prerequisite_contradicts_retained_timing", (name,))
    result = run["result"]
    rules = contract.contract["artifact_custody"]["outcome_relation"]
    matching = [rule for rule in rules if rule["reason_code"] == result["reason_code"]]
    if len(matching) != 1:
        raise CostError("manifest_outcome_reason")
    rule = matching[0]
    if (run["status"] != rule["status"] or result["valid"] is not rule["valid"] or
        result["stage"] not in rule["stages"] or metrics["branch"] not in rule["branches"]):
        raise CostError("manifest_outcome_relation")
    invalid_reason = None if run["status"] == "completed_valid" else result["reason_code"]
    if result["invalid_reason"] != invalid_reason:
        raise CostError("manifest_invalid_reason_relation")
    if run["status"] == "completed_valid" and not hard["supplied_conjunction"]:
        raise CostError("manifest_completed_valid_without_supplied_prerequisites")
    branch = statistical_branch(expected["R_cells"], hard["supplied_conjunction"] and run["status"] == "completed_valid")
    if metrics["branch"] != branch:
        raise CostError("manifest_branch_disagrees_with_retained_costs")
    coverage = metrics["coverage"]
    count_fields = {"main": "main_block_rows", "selection": "selection_block_rows",
                    "top_control": "top_block_rows", "identity_control": "identity_block_rows"}
    for plane, field in count_fields.items():
        if coverage[field] != outputs["timing_coverage"][plane]:
            raise CostError("manifest_timing_coverage_mismatch", (field,))
    resolved = sum(row["seed"] == 606103 and row["q"] == 4096 and row["ratio"]["kind"] == "value" for row in expected["R_cells"])
    if coverage["resolved_primary_cells"] != resolved:
        raise CostError("manifest_resolved_cell_count_mismatch")
    supplied_context = reduction.context.as_json()
    accepted = sum(row["outcome"] == "accepted" for row in supplied_context["candidate_trace"])
    if coverage["accepted_fixtures"] != accepted:
        raise CostError("manifest_accepted_fixture_count_mismatch")
    controls = prerequisites.get("every_required_control_true") is True
    if coverage["all_controls_passed"] != controls:
        raise CostError("manifest_controls_disagree_with_supplied_prerequisite")
    return {"cost_projection": projection_check, "hard_prerequisite_projection": hard,
            "conditional_branch": branch, "whole_manifest_validated": False,
            "scientific_admission": False}


def reduce_cost_component(ledger: CostLedger, context: AllocationContext,
                          timing: TimingIndex, supplied_edges: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Retain actual costs when valid partial inputs cannot support ratios.

    Only the specific unresolved-allocation condition takes the partial route.
    Malformed input, mismatched edges and infrastructure errors remain typed
    exceptions; they cannot silently become a successful partial projection.
    """
    try:
        reduction = AllocationReduction(ledger, context, timing, supplied_edges)
    except CostError as error:
        if error.code != "allocation_projection_unresolved":
            raise
        return {"state": "partial_projection", "cost_projection": None,
                "reason": error.code,
                "unresolved_physical_row_count": sum(1 for _ in iter_allocation_issues(ledger, context)),
                "detail_access": "iter_allocation_issues and retained CostLedger rows",
                "actual_accounting": actual_campaign_accounting(ledger),
                "timing_coverage": timing.coverage(), "scientific_admission": False}
    return {"state": "cost_projection_computed", "outputs": reduction.outputs(),
            "actual_accounting": actual_campaign_accounting(ledger), "scientific_admission": False}
