"""Raw-first ECTD v2 meter adapter.

The public path never calls legacy ``compute_curve_meters`` because its planted
branch directly assigns a primary metric.  Instead it evaluates the bound low
level S3/S4, Groebner, and Macaulay predicates on an already-verified target
bundle, retains the raw residues/statistics, and reduces them in one arm-blind
function.  The exact schedule is 6 m3, 6 m4, 24 decomposition, and one shared
Groebner/Macaulay target.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
import types
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

RAW_SCHEMA = "crypto.autoresearch.ectd_v7_raw_trace.v1"
VECTOR_SCHEMA = "crypto.autoresearch.ectd_v7_meter_vector.v1"
TRIPLET_MEASUREMENT_SCHEMA = "crypto.autoresearch.ectd_v7_meter_triplet.v1"
COUNTS = {"m3": 6, "m4": 6, "fb_decomposition": 24, "solver": 1}
PRIMARY_METERS = (
    "semaev_m3_relation_density",
    "semaev_m4_relation_density",
    "fb_decomposition_probability",
    "macaulay_rank_defect_at_first_fall",
    "groebner_solving_degree_d_reg",
)
BOUND_METER_SHA256 = "8a90c94b5a2b7101b4266224c441f34552cb786ed51120c4396df87c22fe312f"


class MeterError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _exact_keys(value: Mapping[str, Any], expected: Iterable[str], code: str) -> None:
    actual, wanted = set(value), set(expected)
    if actual != wanted:
        raise MeterError(code, f"missing={sorted(wanted-actual)}, extra={sorted(actual-wanted)}")


def _jcs_bytes(value: Any) -> bytes:
    def walk(item: Any) -> None:
        if isinstance(item, Mapping):
            for key, child in item.items():
                if not isinstance(key, str) or not key.isascii():
                    raise MeterError("CONTROL_MEASUREMENT_INVALID", "non-ASCII property")
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, float):
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "raw traces cannot contain floats")
        elif isinstance(item, int) and abs(item) > 9_007_199_254_740_991:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "large integer requires decimal text")

    walk(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _sha(value: Any) -> str:
    return hashlib.sha256(_jcs_bytes(value)).hexdigest()


def _decimal(value: Any, name: str) -> int:
    if not isinstance(value, str) or value != str(int(value)):
        raise MeterError("CONTROL_MEASUREMENT_INVALID", f"{name} is not canonical decimal text")
    return int(value)


def _ratio(numerator: int, denominator: int) -> dict[str, str]:
    value = Fraction(numerator, denominator)
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def _load_bound_modules(repository_root: Path) -> Mapping[str, Any]:
    manifest = json.loads(
        (Path(__file__).resolve().parent / "arithmetic-input-manifest.json").read_text(encoding="utf-8")
    )
    bindings = {entry["role"]: entry for entry in manifest["bound_sources"]}
    required = {"fp", "curve", "semaev", "mvpoly", "groebner", "macaulay", "meters"}
    if not required.issubset(bindings):
        raise MeterError("SOURCE_GAP", f"missing roles: {sorted(required-set(bindings))}")
    for role in required:
        binding = bindings[role]
        data = (repository_root / binding["path"]).read_bytes()
        if len(data) != binding["size_bytes"] or hashlib.sha256(data).hexdigest() != binding["sha256"]:
            raise MeterError("CUSTODY_FAILURE", binding["path"])
    if bindings["meters"]["sha256"] != BOUND_METER_SHA256:
        raise MeterError("CUSTODY_FAILURE", "operative v2 meter source drift")
    package_name = "_ectd_v7_bound_reused"
    package_dir = (repository_root / bindings["meters"]["path"]).parent
    if package_name not in sys.modules:
        package = types.ModuleType(package_name)
        package.__path__ = [str(package_dir)]
        package.__package__ = package_name
        sys.modules[package_name] = package
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        return {
            role: importlib.import_module(f"{package_name}.{role}")
            for role in ("fp", "curve", "semaev", "mvpoly", "groebner", "macaulay", "meters")
        }
    finally:
        sys.dont_write_bytecode = old


def _poly_terms(poly: Any) -> list[dict[str, Any]]:
    return [
        {"monomial": list(monomial), "coefficient": str(coefficient)}
        for monomial, coefficient in sorted(poly.terms.items())
    ]


def _target_index(target_bundle: Mapping[str, Any]) -> dict[tuple[str, int], Mapping[str, Any]]:
    _exact_keys(
        target_bundle,
        ("schema", "curve_id", "meter_subseed", "counts", "factor_base", "targets", "target_bundle_id"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    if target_bundle["schema"] != "crypto.autoresearch.ectd_v7_target_bundle.v1" or target_bundle["counts"] != COUNTS:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "target bundle schema/counts")
    body = {key: target_bundle[key] for key in ("schema", "curve_id", "meter_subseed", "counts", "factor_base", "targets")}
    if target_bundle["target_bundle_id"] != _sha(body):
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "target bundle locator mismatch")
    targets = target_bundle["targets"]
    if not isinstance(targets, list) or len(targets) != sum(COUNTS.values()):
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "target cardinality")
    index: dict[tuple[str, int], Mapping[str, Any]] = {}
    forbidden = set(PRIMARY_METERS) | {"hit", "hits", "success", "expected", "valid", "metric", "metrics"}
    for target in targets:
        _exact_keys(target, ("meter_id", "sample_index", "point", "construction", "selected_attempt"), "CONTROL_MEASUREMENT_INVALID")
        if forbidden.intersection(target):
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "caller outcome truth in target")
        key = (target["meter_id"], target["sample_index"])
        if key in index:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "duplicate target")
        index[key] = target
    expected = {(meter, sample) for meter, count in COUNTS.items() for sample in range(count)}
    if set(index) != expected:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "target index gap")
    return index


def _point(target: Mapping[str, Any], a: int, b: int, p: int) -> tuple[int, int]:
    point = target["point"]
    _exact_keys(point, ("x", "y"), "CONTROL_MEASUREMENT_INVALID")
    x, y = _decimal(point["x"], "x"), _decimal(point["y"], "y")
    if not 0 <= x < p or not 0 <= y < p or (y * y - x * x * x - a * x - b) % p:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "off-curve target")
    return x, y


def _curve_root(root: Mapping[str, Any]) -> tuple[int, int, int]:
    curve = root["curve"]
    _exact_keys(curve, ("curve_id", "model", "p", "a", "b"), "CONTROL_MEASUREMENT_INVALID")
    p, a, b = (_decimal(curve[key], key) for key in ("p", "a", "b"))
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "singular curve")
    return p, a, b


def collect_raw_trace(
    root: Mapping[str, Any],
    target_bundle: Mapping[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    """Evaluate the exact v2 predicate schedule; no arm parameter is accepted."""
    _exact_keys(root, ("curve", "meter_subseed", "config", "draw_plan_id", "root_id"), "CONTROL_MEASUREMENT_INVALID")
    if target_bundle.get("curve_id") != root["curve"]["curve_id"] or target_bundle.get("meter_subseed") != root["meter_subseed"]:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "curve/subseed binding mismatch")
    index = _target_index(target_bundle)
    modules = _load_bound_modules(repository_root)
    semaev, meters, groebner, macaulay = (
        modules["semaev"], modules["meters"], modules["groebner"], modules["macaulay"]
    )
    p, a, b = _curve_root(root)
    config = root["config"]
    fb = meters.get_fb(a, b, p, config["fb_size"])
    if target_bundle["factor_base"] != [str(x) for x in fb]:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "factor base mismatch")
    m3_records: list[dict[str, Any]] = []
    for sample_index in range(COUNTS["m3"]):
        xR, _ = _point(index[("m3", sample_index)], a, b, p)
        residues = [
            {"x1": str(x1), "x2": str(x2), "residue": str(semaev.S3(x1, x2, xR, a, b, p))}
            for x1 in fb for x2 in fb
        ]
        m3_records.append({"sample_index": sample_index, "target_x": str(xR), "residues": residues})
    m4_records: list[dict[str, Any]] = []
    for sample_index in range(COUNTS["m4"]):
        xR, _ = _point(index[("m4", sample_index)], a, b, p)
        residues: list[dict[str, Any]] = []
        for x1 in fb:
            for x2 in fb:
                left = semaev.S3_coeffs_in_X(x1, x2, a, b, p)
                for x3 in fb:
                    right = semaev.S3_coeffs_in_X(x3, xR, a, b, p)
                    residue = semaev.sylvester_resultant_quadratics(left, right, p)
                    residues.append({"x1": str(x1), "x2": str(x2), "x3": str(x3), "residue": str(residue)})
        m4_records.append({"sample_index": sample_index, "target_x": str(xR), "residues": residues})
    decomposition: list[dict[str, Any]] = []
    for sample_index in range(COUNTS["fb_decomposition"]):
        xR, _ = _point(index[("fb_decomposition", sample_index)], a, b, p)
        residues = [
            {"x1": str(x1), "x2": str(x2), "residue": str(semaev.S3(x1, x2, xR, a, b, p))}
            for x1 in fb for x2 in fb
        ]
        decomposition.append({"sample_index": sample_index, "target_x": str(xR), "residues": residues})
    solver_x, _ = _point(index[("solver", 0)], a, b, p)
    nvars = 2
    generators = [
        meters._s3_as_mpoly(solver_x, a, b, p, nvars),
        meters._fb_defining_poly(fb, nvars, 0, p),
        meters._fb_defining_poly(fb, nvars, 1, p),
    ]
    gb = config["gb_budget"]
    _, gb_stats = groebner.buchberger(
        generators,
        p,
        nvars,
        max_pairs=gb["max_pairs"],
        max_degree=gb["max_degree"],
        wall_seconds=gb["wall_seconds"],
    )
    ff = macaulay.first_fall_scan(generators, nvars, p, max_extra_degrees=config["macaulay_cap"])
    solver = {
        "sample_index": 0,
        "target_x": str(solver_x),
        "system": [_poly_terms(poly) for poly in generators],
        "groebner": {
            "max_spoly_degree": gb_stats["max_spoly_degree"],
            "pairs_processed": gb_stats["pairs_processed"],
            "basis_size": gb_stats["basis_size"],
            "timed_out": gb_stats["timed_out"],
        },
        "macaulay": ff,
    }
    body = {
        "schema": RAW_SCHEMA,
        "curve_id": root["curve"]["curve_id"],
        "meter_subseed": root["meter_subseed"],
        "target_bundle_id": target_bundle["target_bundle_id"],
        "fb": [str(x) for x in fb],
        "m3": m3_records,
        "m4": m4_records,
        "fb_decomposition": decomposition,
        "solver": solver,
    }
    return {**body, "raw_trace_id": _sha(body)}


def verify_raw_trace(
    raw_trace: Mapping[str, Any],
    root: Mapping[str, Any],
    target_bundle: Mapping[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    """Recompute every predicate and solver output before reduction."""
    _validate_raw_trace_structure(raw_trace)
    expected = collect_raw_trace(root, target_bundle, repository_root)
    if dict(raw_trace) != expected:
        raise MeterError("FALSE_RECEIPT", "raw trace semantic replay mismatch")
    return expected


def _check_residue_row(
    row: Mapping[str, Any],
    arity: int,
    fb: Sequence[int],
    expected: int,
) -> tuple[int, list[list[int]]]:
    residues = row.get("residues")
    if not isinstance(residues, list) or len(residues) != expected:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "raw residue cardinality")
    expected_tuples: list[list[int]] = []
    if arity == 2:
        expected_tuples = [[x1, x2] for x1 in fb for x2 in fb]
        coordinate_keys = ("x1", "x2")
    else:
        expected_tuples = [[x1, x2, x3] for x1 in fb for x2 in fb for x3 in fb]
        coordinate_keys = ("x1", "x2", "x3")
    observed: list[list[int]] = []
    zero_count = 0
    for receipt in residues:
        _exact_keys(receipt, (*coordinate_keys, "residue"), "CONTROL_MEASUREMENT_INVALID")
        observed.append([_decimal(receipt[key], key) for key in coordinate_keys])
        residue = _decimal(receipt["residue"], "residue")
        if residue == 0:
            zero_count += 1
    if observed != expected_tuples:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "raw predicate order or tuple drift")
    return zero_count, observed


def _validate_raw_trace_structure(
    raw_trace: Mapping[str, Any],
) -> tuple[list[int], int, int, int, Mapping[str, Any], Mapping[str, Any]]:
    """Derive the first structural/resource terminal without trusting a hash."""
    _exact_keys(
        raw_trace,
        ("schema", "curve_id", "meter_subseed", "target_bundle_id", "fb", "m3", "m4", "fb_decomposition", "solver", "raw_trace_id"),
        "CONTROL_MEASUREMENT_INVALID",
    )
    if raw_trace["schema"] != RAW_SCHEMA:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "raw schema")
    fb = [_decimal(value, "fb") for value in raw_trace["fb"]]
    if not fb or fb != sorted(set(fb)):
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "factor base order/uniqueness")
    if len(raw_trace["m3"]) != 6 or len(raw_trace["m4"]) != 6 or len(raw_trace["fb_decomposition"]) != 24:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "6/6/24 schedule mismatch")
    m3_hits = 0
    for index, row in enumerate(raw_trace["m3"]):
        if row.get("sample_index") != index:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "m3 sample index")
        hits, _ = _check_residue_row(row, 2, fb, len(fb) ** 2)
        m3_hits += hits
    m4_hits = 0
    for index, row in enumerate(raw_trace["m4"]):
        if row.get("sample_index") != index:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "m4 sample index")
        hits, _ = _check_residue_row(row, 3, fb, len(fb) ** 3)
        m4_hits += hits
    decomposition_hits = 0
    for index, row in enumerate(raw_trace["fb_decomposition"]):
        if row.get("sample_index") != index:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "decomposition sample index")
        hits, _ = _check_residue_row(row, 2, fb, len(fb) ** 2)
        decomposition_hits += int(hits > 0)
    solver = raw_trace["solver"]
    _exact_keys(solver, ("sample_index", "target_x", "system", "groebner", "macaulay"), "CONTROL_MEASUREMENT_INVALID")
    if solver["sample_index"] != 0:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "solver target index")
    gb, ff = solver["groebner"], solver["macaulay"]
    _exact_keys(gb, ("max_spoly_degree", "pairs_processed", "basis_size", "timed_out"), "CONTROL_MEASUREMENT_INVALID")
    if gb["timed_out"] is not False:
        raise MeterError("RESOURCE_LIMIT", "Groebner budget exhausted; no d_reg claim")
    if not isinstance(ff, Mapping) or ff.get("observed") is not True or ff.get("defect") is None:
        raise MeterError("RESOURCE_LIMIT", "Macaulay fall unobserved; defect remains null")
    body = {key: raw_trace[key] for key in ("schema", "curve_id", "meter_subseed", "target_bundle_id", "fb", "m3", "m4", "fb_decomposition", "solver")}
    if raw_trace["raw_trace_id"] != _sha(body):
        raise MeterError("FALSE_RECEIPT", "raw trace locator mismatch")
    return fb, m3_hits, m4_hits, decomposition_hits, gb, ff


def _reduce_verified_raw_trace(raw_trace: Mapping[str, Any]) -> dict[str, Any]:
    """Construct primary metric keys only from a semantically replayed trace."""
    fb, m3_hits, m4_hits, decomposition_hits, gb, ff = _validate_raw_trace_structure(raw_trace)
    vector_body = {
        "schema": VECTOR_SCHEMA,
        "semaev_m3_relation_density": _ratio(m3_hits, 6 * len(fb) ** 2),
        "semaev_m4_relation_density": _ratio(m4_hits, 6 * len(fb) ** 3),
        "fb_decomposition_probability": _ratio(decomposition_hits, 24),
        "macaulay_rank_defect_at_first_fall": ff["defect"],
        "groebner_solving_degree_d_reg": gb["max_spoly_degree"],
    }
    return {**vector_body, "meter_vector_id": _sha(vector_body), "raw_trace_id": raw_trace["raw_trace_id"]}


def reduce_raw_trace(
    raw_trace: Mapping[str, Any],
    root: Mapping[str, Any],
    target_bundle: Mapping[str, Any],
    repository_root: Path,
) -> dict[str, Any]:
    """The sole public, arm-blind raw-to-metric path; replay precedes reduction."""
    verified = verify_raw_trace(raw_trace, root, target_bundle, repository_root)
    return _reduce_verified_raw_trace(verified)


def measure_atomic_triplet(
    triplet: Mapping[str, Any],
    repository_root: Path,
    control_module: Any,
) -> dict[str, Any]:
    """Collect/reduce three arms only after atomic control replay succeeds."""
    control_receipt = control_module.verify_atomic_triplet(triplet, repository_root)
    if control_receipt.get("status") != "accepted":
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "control replay failed")
    bundles = triplet["target_bundles"]
    rows: list[dict[str, Any]] = []
    for arm in triplet["arms"]:
        bundle = bundles["planted"] if arm["effective"] else bundles["unplanted"]
        if bundle["target_bundle_id"] != arm["target_bundle_id"]:
            raise MeterError("CONTROL_MEASUREMENT_INVALID", "arm/bundle binding")
        raw = collect_raw_trace(triplet["root"], bundle, repository_root)
        vector = reduce_raw_trace(raw, triplet["root"], bundle, repository_root)
        rows.append({
            "arm": arm["arm"],
            "target_bundle_id": bundle["target_bundle_id"],
            "raw_trace": raw,
            "meter_vector": vector,
        })
    if rows[0]["target_bundle_id"] != rows[2]["target_bundle_id"]:
        raise MeterError("CONTROL_MEASUREMENT_INVALID", "ordinary/disabled bundle mismatch")
    body = {
        "schema": TRIPLET_MEASUREMENT_SCHEMA,
        "control_triplet_id": triplet["triplet_id"],
        "curve_id": control_receipt["curve_id"],
        "meter_subseed": control_receipt["meter_subseed"],
        "counts": dict(COUNTS),
        "arms": rows,
    }
    return {**body, "measurement_id": _sha(body)}


if __name__ == "__main__":
    raise SystemExit("static meter adapter; downstream Executor owns conformance")
