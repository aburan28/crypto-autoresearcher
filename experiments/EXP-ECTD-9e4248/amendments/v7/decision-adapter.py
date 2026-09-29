"""Typed outer decision adapter for the unchanged ECTD v2 data branches.

All completeness, validity, ratios, band flags, extreme flags, and the single
global KS result are derived from typed replay receipts.  No caller-provided
decision booleans are accepted.  Fewer than eight complete matched pairs, any
invalid instrument receipt, any null primary value, or any unbounded ratio
outside the exact KS numeric domain returns resource_incomplete/instrument_void
before KS as specified.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

INPUT_SCHEMA = "crypto.autoresearch.ectd_v7_decision_input.v1"
DECISION_SCHEMA = "crypto.autoresearch.ectd_v7_decision.v1"
KS_SCHEMA = "crypto.autoresearch.ectd_v7_exact_ks.v1"
VECTOR_SCHEMA = "crypto.autoresearch.ectd_v7_meter_vector.v1"
HIGH_METERS = (
    "semaev_m3_relation_density",
    "semaev_m4_relation_density",
    "fb_decomposition_probability",
    "macaulay_rank_defect_at_first_fall",
)
LOW_METER = "groebner_solving_degree_d_reg"
ALL_METERS = HIGH_METERS + (LOW_METER,)
MIN_MATCHED_PAIRS = 8


class DecisionError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], code: str) -> None:
    actual, wanted = set(value), set(expected)
    if actual != wanted:
        raise DecisionError(code, f"missing={sorted(wanted-actual)}, extra={sorted(actual-wanted)}")


def _jcs_bytes(value: Any) -> bytes:
    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    raise DecisionError("FALSE_RECEIPT", "non-ASCII property")
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, float):
            raise DecisionError("FALSE_RECEIPT", "floats are not authoritative")

    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_jcs_bytes(value)).hexdigest()


def _ratio(value: Mapping[str, Any]) -> Fraction:
    _exact_keys(value, ("numerator", "denominator"), "FALSE_RECEIPT")
    try:
        numerator = int(value["numerator"])
        denominator = int(value["denominator"])
    except (TypeError, ValueError) as exc:
        raise DecisionError("FALSE_RECEIPT", "nonintegral ratio") from exc
    if str(numerator) != value["numerator"] or str(denominator) != value["denominator"] or denominator <= 0:
        raise DecisionError("FALSE_RECEIPT", "noncanonical ratio")
    exact = Fraction(numerator, denominator)
    if exact.numerator != numerator or exact.denominator != denominator:
        raise DecisionError("FALSE_RECEIPT", "ratio not reduced")
    return exact


def _validate_vector(
    vector: Mapping[str, Any],
    meter_replayer: Any,
    control_replayer: Any,
    raw_trace: Mapping[str, Any],
    control_triplet: Mapping[str, Any],
    arm_name: str,
    repository_root: Any,
) -> dict[str, Fraction | int]:
    expected = {"schema", "meter_vector_id", "raw_trace_id", *ALL_METERS}
    _exact_keys(vector, expected, "FALSE_RECEIPT")
    if vector["schema"] != VECTOR_SCHEMA:
        raise DecisionError("FALSE_RECEIPT", "meter vector schema")
    control_receipt = control_replayer.verify_atomic_triplet(control_triplet, repository_root)
    if not isinstance(control_receipt, Mapping) or control_receipt.get("status") != "accepted":
        raise DecisionError("FALSE_RECEIPT", "typed control replay failed")
    matching_arms = [arm for arm in control_triplet["arms"] if arm["arm"] == arm_name]
    if len(matching_arms) != 1:
        raise DecisionError("FALSE_RECEIPT", "unknown or duplicate control arm")
    arm = matching_arms[0]
    bundle_name = "planted" if arm["effective"] else "unplanted"
    target_bundle = control_triplet["target_bundles"][bundle_name]
    if target_bundle["target_bundle_id"] != arm["target_bundle_id"]:
        raise DecisionError("FALSE_RECEIPT", "arm/target bundle mismatch")
    root = control_triplet["root"]
    replayed_vector = meter_replayer.reduce_raw_trace(raw_trace, root, target_bundle, repository_root)
    if dict(vector) != replayed_vector:
        raise DecisionError("FALSE_RECEIPT", "typed raw-to-vector replay mismatch")
    body = {key: vector[key] for key in ("schema", *ALL_METERS)}
    if vector["meter_vector_id"] != _sha(body):
        raise DecisionError("FALSE_RECEIPT", "meter vector locator mismatch")
    out: dict[str, Fraction | int] = {}
    for meter in HIGH_METERS[:3]:
        out[meter] = _ratio(vector[meter])
    for meter in ("macaulay_rank_defect_at_first_fall", LOW_METER):
        value = vector[meter]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise DecisionError("FALSE_RECEIPT", f"invalid integral meter: {meter}")
        out[meter] = value
    return out


def _symmetric_ratio(left: Fraction | int, right: Fraction | int) -> Fraction | None:
    left, right = Fraction(left), Fraction(right)
    low, high = min(left, right), max(left, right)
    if low == 0:
        return Fraction(1, 1) if high == 0 else None
    return high / low


def _ratio_record(value: Fraction | None) -> Mapping[str, str] | None:
    if value is None:
        return None
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def exact_ks(sample_x: Sequence[Fraction], sample_y: Sequence[Fraction]) -> dict[str, Any]:
    if not sample_x or not sample_y:
        raise DecisionError("RESOURCE_LIMIT", "empty exact KS sample")
    x, y = sorted(sample_x), sorted(sample_y)
    n, m = len(x), len(y)
    support = sorted(set(x) | set(y))
    ix = iy = 0
    distance = Fraction(0, 1)
    for value in support:
        while ix < n and x[ix] <= value:
            ix += 1
        while iy < m and y[iy] <= value:
            iy += 1
        distance = max(distance, abs(Fraction(ix, n) - Fraction(iy, m)))
    a, b = distance.numerator, distance.denominator
    lhs = 625 * a * a * n * m
    rhs = 1156 * b * b * (n + m)
    return {
        "schema": KS_SCHEMA,
        "D": {"numerator": str(a), "denominator": str(b)},
        "n": n,
        "m": m,
        "comparison_lhs": str(lhs),
        "comparison_rhs": str(rhs),
        "rejects": lhs > rhs,
    }


def decide(
    decision_input: Mapping[str, Any],
    *,
    meter_replayer: Any,
    control_replayer: Any,
    certificate_replayer: Any,
    instrument_replayers: Mapping[str, Any],
    repository_root: Any,
) -> dict[str, Any]:
    _exact_keys(decision_input, ("schema", "edges", "instrument_receipts"), "FALSE_RECEIPT")
    if decision_input["schema"] != INPUT_SCHEMA:
        raise DecisionError("FALSE_RECEIPT", "decision input schema")
    instruments = decision_input["instrument_receipts"]
    if not isinstance(instruments, list) or not instruments:
        return {"schema": DECISION_SCHEMA, "decision_branch": "instrument_void", "reason": "missing_typed_instrument_receipts", "ks_result": None}
    for instrument in instruments:
        _exact_keys(instrument, ("instrument_id", "instrument_kind", "payload"), "FALSE_RECEIPT")
        replay = instrument_replayers.get(instrument["instrument_kind"])
        if not callable(replay):
            return {"schema": DECISION_SCHEMA, "decision_branch": "instrument_void", "reason": "typed_instrument_replay_failed", "ks_result": None}
        try:
            typed_receipt = replay(instrument["payload"])
        except Exception:
            return {"schema": DECISION_SCHEMA, "decision_branch": "instrument_void", "reason": "typed_instrument_replay_failed", "ks_result": None}
        if not isinstance(typed_receipt, Mapping) or typed_receipt.get("status") != "accepted":
            return {"schema": DECISION_SCHEMA, "decision_branch": "instrument_void", "reason": "typed_instrument_replay_failed", "ks_result": None}
    edges = decision_input["edges"]
    if not isinstance(edges, list) or len(edges) < MIN_MATCHED_PAIRS:
        return {
            "schema": DECISION_SCHEMA,
            "decision_branch": "resource_incomplete",
            "reason": "fewer_than_eight_vertical_edges",
            "n_complete_vertical_edges": len(edges) if isinstance(edges, list) else 0,
            "ks_result": None,
        }
    edge_ids: set[str] = set()
    vertical_samples: list[Fraction] = []
    horizontal_samples: list[Fraction] = []
    derived_edges: list[dict[str, Any]] = []
    endpoint_cache: dict[str, dict[str, Fraction | int]] = {}
    for edge in edges:
        _exact_keys(edge, ("edge_id", "vertical", "matched_horizontal", "certificate"), "FALSE_RECEIPT")
        edge_id = edge["edge_id"]
        if edge_id in edge_ids:
            raise DecisionError("FALSE_RECEIPT", "duplicate edge")
        try:
            cert_receipt = certificate_replayer.verify_certificate(edge["certificate"])
        except Exception as exc:
            raise DecisionError("FALSE_RECEIPT", "typed certificate replay failed") from exc
        if not isinstance(cert_receipt, Mapping) or cert_receipt.get("status") != "accepted" or cert_receipt.get("certificate_sha256") != _sha(edge["certificate"]):
            raise DecisionError("FALSE_RECEIPT", "invalid typed certificate replay")
        edge_ids.add(edge_id)
        vertical_pair = edge["vertical"]
        horizontal_pair = edge["matched_horizontal"]
        _exact_keys(vertical_pair, ("left", "right"), "FALSE_RECEIPT")
        _exact_keys(horizontal_pair, ("left", "right"), "FALSE_RECEIPT")

        def replay_endpoint(endpoint: Mapping[str, Any]) -> dict[str, Fraction | int]:
            _exact_keys(endpoint, ("meter_vector", "raw_trace", "control_triplet", "arm"), "FALSE_RECEIPT")
            cache_key = _sha(endpoint)
            if cache_key in endpoint_cache:
                return endpoint_cache[cache_key]
            replayed = _validate_vector(
                endpoint["meter_vector"], meter_replayer, control_replayer,
                endpoint["raw_trace"], endpoint["control_triplet"], endpoint["arm"],
                repository_root,
            )
            endpoint_cache[cache_key] = replayed
            return replayed

        v_left, v_right = replay_endpoint(vertical_pair["left"]), replay_endpoint(vertical_pair["right"])
        h_left, h_right = replay_endpoint(horizontal_pair["left"]), replay_endpoint(horizontal_pair["right"])
        vertical_ratios: dict[str, Fraction | None] = {}
        horizontal_ratios: dict[str, Fraction | None] = {}
        for meter in ALL_METERS:
            vertical_ratios[meter] = _symmetric_ratio(v_left[meter], v_right[meter])
            horizontal_ratios[meter] = _symmetric_ratio(h_left[meter], h_right[meter])
        if any(value is None for value in vertical_ratios.values()) or any(value is None for value in horizontal_ratios.values()):
            return {
                "schema": DECISION_SCHEMA,
                "decision_branch": "resource_incomplete",
                "reason": "unbounded_ratio_outside_exact_KS_domain",
                "edge_id": edge_id,
                "ks_result": None,
            }
        vertical_samples.extend(value for value in vertical_ratios.values() if value is not None)
        horizontal_samples.extend(value for value in horizontal_ratios.values() if value is not None)
        delta_d = abs(int(v_left[LOW_METER]) - int(v_right[LOW_METER]))
        any_extreme = any(value is not None and value >= 100 for value in vertical_ratios.values()) or delta_d >= 2
        all_in_band = all(value is not None and Fraction(1, 10) <= value <= 10 for value in vertical_ratios.values())
        derived_edges.append({
            "edge_id": edge_id,
            "vertical_ratios": {key: _ratio_record(value) for key, value in vertical_ratios.items()},
            "horizontal_ratios": {key: _ratio_record(value) for key, value in horizontal_ratios.items()},
            "delta_d_reg": delta_d,
            "any_ge_100_or_delta2": any_extreme,
            "all_in_band_0p1_10": all_in_band,
        })
    if len(edges) != len(derived_edges):
        raise DecisionError("RESOURCE_LIMIT", "incomplete matched horizontal set")
    ks = exact_ks(vertical_samples, horizontal_samples)
    any_extreme = any(edge["any_ge_100_or_delta2"] for edge in derived_edges)
    all_in_band = all(edge["all_in_band_0p1_10"] for edge in derived_edges)
    if ks["rejects"] and any_extreme:
        branch = "discontinuity_nominates_endpoint"
        shape = None
    elif all_in_band and not ks["rejects"]:
        branch = "continuity_scoped"
        shape = None
    else:
        branch = "moderate_effect_unresolved"
        shape = (
            "i_nonreject_with_out_of_band_edge"
            if not ks["rejects"] and not all_in_band
            else "ii_reject_without_individual_extreme"
        )
    body = {
        "schema": DECISION_SCHEMA,
        "decision_branch": branch,
        "moderate_effect_shape": shape,
        "ks_result": ks,
        "n_complete_vertical_edges": len(derived_edges),
        "n_matched_horizontal_pairs": len(derived_edges),
        "n_vertical_ratio_samples": len(vertical_samples),
        "n_horizontal_ratio_samples": len(horizontal_samples),
        "all_edges_in_band_0p1_10": all_in_band,
        "any_edge_ge_100_or_delta2": any_extreme,
        "edges": derived_edges,
    }
    return {**body, "decision_id": _sha(body)}


if __name__ == "__main__":
    raise SystemExit("static decision adapter; downstream Executor owns conformance")
