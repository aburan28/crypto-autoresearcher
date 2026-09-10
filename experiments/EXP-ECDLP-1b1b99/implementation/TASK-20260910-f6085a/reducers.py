"""Exact pure reducers for the CM cost component; no runtime or authorization API."""
from __future__ import annotations
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

class ReductionError(ValueError): pass
def _int(x: Any, name: str, low: int = 0) -> int:
    if isinstance(x, bool) or not isinstance(x, int) or x < low: raise ReductionError(f"{name} must be integer >= {low}")
    return x
def rat(x: Any) -> Fraction:
    if isinstance(x, Fraction): return x
    if isinstance(x, int) and not isinstance(x, bool): return Fraction(x)
    if isinstance(x, Mapping): return Fraction(_int(x.get("numerator"), "numerator"), _int(x.get("denominator"), "denominator", 1))
    raise ReductionError("not an exact rational")
def encode(x: Fraction) -> dict[str, int]: return {"numerator": x.numerator, "denominator": x.denominator}
def median7(values: Sequence[Any]) -> Fraction:
    if len(values) != 7: raise ReductionError("Med7 requires exactly seven values")
    return sorted(rat(v) for v in values)[3]
def median6(values: Sequence[Any]) -> Fraction:
    if len(values) != 6: raise ReductionError("Med6 requires exactly six values")
    vals = sorted(rat(v) for v in values); return (vals[2] + vals[3]) / 2
def normalized_blocks(blocks: Sequence[Mapping[str, Any]], *, omitted: int | None = None) -> Fraction:
    required = set(range(7)) - ({omitted} if omitted is not None else set())
    labels = [b.get("block") for b in blocks if omitted is None or b.get("block") != omitted]
    if set(labels) != required or len(labels) != len(required): raise ReductionError("missing or duplicate block")
    values = []
    for row in blocks:
        if omitted is not None and row.get("block") == omitted: continue
        if row.get("status", "complete") not in ("complete",) or row.get("below_resolution", False): raise ReductionError("invalid or below-resolution block")
        values.append(Fraction(_int(row.get("CPU_nanoseconds"), "block CPU"), _int(row.get("repetitions"), "repetitions", 1)))
    return median6(values) if omitted is not None else median7(values)
def select_baselines(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, int], int]:
    """Use U_integer + Med7(B/n) per endpoint and exact eight-endpoint average."""
    groups: dict[tuple[str, int, int, str], list[Mapping[str, Any]]] = {}
    setup: dict[tuple[str, int, int, str], int] = {}
    for row in rows:
        interval, coordinate, arm, endpoint = row.get("interval"), row.get("coordinate"), row.get("candidate_arm"), row.get("endpoint")
        if interval not in ("I0", "I1", "I2") or coordinate not in (1,2,3) or arm not in range(2,8) or not isinstance(endpoint, str): raise ReductionError("bad selection row")
        key = (interval, coordinate, arm, endpoint); groups.setdefault(key, []).append(row)
        setup[key] = setup.get(key, 0) + _int(row.get("setup_CPU_nanoseconds", 0), "setup")
    winners: dict[tuple[str, int], int] = {}
    for interval in ("I0", "I1", "I2"):
        for coordinate in (1,2,3):
            scores: dict[int, Fraction] = {}
            for arm in range(2,8):
                keys = [k for k in groups if k[:3] == (interval, coordinate, arm)]
                if len(keys) != 8: raise ReductionError("selection requires six arms and eight endpoints")
                scores[arm] = sum((Fraction(setup[k]) + normalized_blocks(groups[k]) for k in keys), Fraction()) / 8
            winners[(interval, coordinate)] = min(scores, key=lambda arm: (scores[arm], arm))
    return winners
def endpoint_total(endpoint: Mapping[str, Any], *, omitted: int | None = None) -> Fraction:
    return Fraction(_int(endpoint.get("fixed_CPU_nanoseconds"), "fixed CPU")) + normalized_blocks(endpoint.get("blocks", ()), omitted=omitted)
def cell_ratio(cell: Mapping[str, Any], *, omitted: int | None = None) -> Fraction:
    scalar, transport = cell.get("scalar"), cell.get("transport")
    if not isinstance(scalar, Sequence) or not isinstance(transport, Sequence) or len(scalar) != len(transport) or len(scalar) != 2: raise ReductionError("cell requires two class endpoints per strategy")
    s = sum((endpoint_total(e, omitted=omitted) for e in scalar), Fraction())
    t = sum((endpoint_total(e, omitted=omitted) for e in transport), Fraction())
    if t <= 0: raise ReductionError("transport denominator is unresolved")
    return s / t
def reduce_primary(cells: Mapping[tuple[str, str, int], Mapping[str, Any]]) -> dict[str, Any]:
    if len(cells) != 36: return {"state": "unresolved", "reason": "requires 36 cells"}
    try:
        full = {key: cell_ratio(cell) for key, cell in cells.items()}
        loo = {b: {key: cell_ratio(cell, omitted=b) for key, cell in cells.items()} for b in range(7)}
    except ReductionError as exc: return {"state": "unresolved", "reason": str(exc)}
    success = all(value >= Fraction(6,5) and all(loo[b][key] >= Fraction(6,5) for b in range(7)) for key, value in full.items())
    negative = all(value <= 1 and all(loo[b][key] <= 1 for b in range(7)) for key, value in full.items())
    return {"state": "valid", "classification": "success_stable" if success else "negative_stable" if negative else "statistically_inconclusive", "full": {str(k): encode(v) for k,v in full.items()}, "leave_one_out": {str(b): {str(k): encode(v) for k,v in table.items()} for b,table in loo.items()}}
def q_star(ladder: Mapping[int, Any]) -> str | int:
    for q in (1,16,256,4096):
        if q not in ladder: return "unresolved"
        value = rat(ladder[q])
        if value >= 1:
            return q if all(rat(ladder[x]) < 1 for x in (1,16,256,4096) if x < q) else "unresolved"
    return "greater_than_4096"
def hard_validity(facts: Mapping[str, Any]) -> bool:
    required = ("authorization_and_nonce_valid", "all_six_fixtures_and_certificates_valid", "four_labels_two_classes_per_fixture_valid", "all_exact_duals_and_map_conjugations_valid", "every_required_control_true", "baseline_dependency_and_nine_freezes_valid", "main_timing_block_row_count_equals_28224", "top_control_block_row_count_equals_2016", "identity_control_block_row_count_equals_2016", "every_required_block_present_and_typed_including_below_resolution", "every_measured_output_replay_valid", "cost_allocation_reconciles_exactly", "resource_and_custody_receipts_valid", "all_required_artifacts_nonempty_parsed_and_hash_bound")
    return all(facts.get(field) is True for field in required)
