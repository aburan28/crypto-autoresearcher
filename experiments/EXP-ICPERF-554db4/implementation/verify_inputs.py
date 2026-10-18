"""Independently check serialized original/sorted XCNF and full curve points.

This reads the frozen bytes and evaluates their gates directly. It does not
call a SAT solver or use the sorted circuit producer to validate its output.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.icperf_binary_circuit_xcnf_verify import check_gate_definitions, parse  # noqa: E402
from tools.icperf_binary_root_certificate import certificate  # noqa: E402
from tools.icperf_binary_torsion_coordinate import phi_from_x  # noqa: E402
from tools.icperf_ordinary_binary_fixture import add, on_curve, scale  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
INPUTS = HERE / "inputs"
MANIFEST = INPUTS / "sorted_positive_manifest.json"
POSITIVE = ROOT / "experiments/EXP-ICPERF-018b0c/inputs/positive_manifest.json"
BASES = {
    "weighted": ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json",
    "local_random": ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json",
}
PRIMARY, WIDTH, OFFSET = 454, 11, 4096


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def check_xcnf_model(values: list[bool], clauses: list[list[int]],
                     xors: list[tuple[list[int], bool]]) -> None:
    for index, clause in enumerate(clauses):
        if not any(values[abs(lit)] == (lit > 0) for lit in clause):
            raise ValueError(f"CNF clause {index} fails")
    for index, (variables, parity) in enumerate(xors):
        if bool(sum(values[var] for var in variables) & 1) != parity:
            raise ValueError(f"native XOR row {index} fails")


def parse_model(text: str, nvars: int) -> list[bool]:
    values: dict[int, bool] = {}
    statuses = []
    for line in text.splitlines():
        if line.startswith("s "):
            statuses.append(line)
        elif line.startswith("v "):
            for token in line[2:].split():
                lit = int(token)
                if lit:
                    var = abs(lit)
                    if not 1 <= var <= nvars or var in values:
                        raise ValueError("duplicate or out-of-range model variable")
                    values[var] = lit > 0
    if statuses != ["s SATISFIABLE"] or set(values) != set(range(1, nvars + 1)):
        raise ValueError("incomplete serialized model")
    return [False] + [values[i] for i in range(1, nvars + 1)]


def primary_bits(values: list[bool], count: int) -> int:
    return sum(1 << (i - 1) for i in range(1, count + 1) if values[i])


def full_values(raw: bytes, primary: int, live_gates: dict) -> list[bool]:
    nvars, clauses, xors = parse(raw)
    arm = {"primary_variables": PRIMARY, "live_gates": live_gates}
    gates = check_gate_definitions(arm, nvars, clauses, xors)
    values = [False] * (nvars + 1)
    for index in range(PRIMARY):
        values[index + 1] = bool(primary >> index & 1)
    for var in range(PRIMARY + 1, nvars + 1):
        gate = gates[var]
        if gate[0] == "and":
            values[var] = values[gate[1]] and values[gate[2]]
        else:
            values[var] = bool(sum(values[operand] for operand in gate[1]) & 1) ^ gate[2]
    check_xcnf_model(values, clauses, xors)
    return values


def point_sum(points: list[tuple[int, int]], b: int) -> tuple[int, int] | None:
    total = None
    for point in points:
        if not on_curve(point, b):
            raise ValueError("point fails curve equation")
        total = add(total, point, b)
    return total


def primary_for(points: list[tuple[int, int]], gamma: int, b: int) -> int:
    if len(points) != 8:
        raise ValueError("point count")
    result = 0
    total = None
    for index, point in enumerate(points):
        value = phi_from_x(point[0], gamma) ^ OFFSET
        if not 0 <= value < (1 << WIDTH):
            raise ValueError("point outside base coordinate window")
        result |= value << (index * WIDTH)
        total = add(total, point, b)
        if 1 <= index <= 6:
            if total is None or total[0] in (0, gamma):
                raise ValueError("exceptional intermediate point")
            result |= phi_from_x(total[0], gamma) << (8 * WIDTH + (index - 1) * 61)
    return result


def stable_points(points: list[tuple[int, int]], gamma: int) -> list[tuple[int, int]]:
    return [point for _, point in sorted(enumerate(points),
                                        key=lambda item: phi_from_x(item[1][0], gamma) ^ OFFSET)]


def check_one(label: str, row: dict, source: dict, gamma: int) -> dict:
    source_row = source["source_row"]
    target = source_row["synthetic_control"]
    b = 31
    base_blob = BASES[label].read_bytes()
    base = json.loads(base_blob)
    if sha(base_blob) != row["base_sha256"]:
        raise ValueError("base digest mismatch")
    original_blob = (ROOT / source["formula_path"]).read_bytes()
    original_model_blob = (ROOT / source["known_model_path"]).read_bytes()
    sorted_blob = (ROOT / row["formula_path"]).read_bytes()
    model_blob = (ROOT / row["model_path"]).read_bytes()
    if (sha(original_blob) != source["formula_gzip_sha256"]
            or sha(original_model_blob) != source["known_model_sha256"]
            or sha(sorted_blob) != row["formula_gzip_sha256"]
            or sha(model_blob) != row["model_sha256"]):
        raise ValueError("bound input digest mismatch")
    original_raw, sorted_raw = gzip.decompress(original_blob), gzip.decompress(sorted_blob)
    if sha(original_raw) != row["original_raw_sha256"] or sha(sorted_raw) != row["raw_xcnf_sha256"]:
        raise ValueError("raw input digest mismatch")
    old_points = [tuple(rep[1:]) for rep in target["input_representatives"]]
    sorted_points = stable_points(old_points, gamma)
    if [list(point) for point in sorted_points] != row["sorted_points"]:
        raise ValueError("sorted point record mismatch")
    old_primary = primary_for(old_points, gamma, b)
    sorted_primary = primary_for(sorted_points, gamma, b)
    if old_primary != int(row["original_primary_hex"], 16) or sorted_primary != int(row["sorted_primary_hex"], 16):
        raise ValueError("primary assignment mismatch")
    if point_sum(old_points, b) != point_sum(sorted_points, b) != tuple(row["raw_target"]):
        raise ValueError("raw target changed")
    if scale(4, tuple(row["raw_target"]), b) != tuple(row["projected_target"]):
        raise ValueError("projected target changed")
    full_values(original_raw, old_primary, source_row["input_counts"]["live_gates"])
    old_nvars, old_clauses, old_xors = parse(original_raw)
    original_model = parse_model(original_model_blob.decode(), old_nvars)
    check_xcnf_model(original_model, old_clauses, old_xors)
    if primary_bits(original_model, PRIMARY) != old_primary:
        raise ValueError("archived original complete model primary mismatch")
    full_values(sorted_raw, sorted_primary, row["live_gates"])
    nvars, clauses, xors = parse(sorted_raw)
    model_values = parse_model(model_blob.decode(), nvars)
    check_xcnf_model(model_values, clauses, xors)
    if primary_bits(model_values, PRIMARY) != sorted_primary:
        raise ValueError("complete model primary mismatch")
    full_values(sorted_raw, sorted_primary, row["live_gates"])
    arm = {"kind": "torsion_phi", "base_dimension": WIDTH, "offset": OFFSET,
           "primary_variables": PRIMARY, "target_coordinate": row["target_coordinate"]}
    chain = {"gamma": gamma,
             "curve": {"b_polynomial_bits": b, "prime_order": 576460752557211763},
             "selected_channel": 0,
             "target_channels": [row["raw_target"]] * 4,
             "subgroup_target": row["projected_target"]}
    for name, primary in (("original", old_primary), ("sorted", sorted_primary)):
        certified = certificate(primary, base, chain, arm)
        if not certified.get("certified", False):
            raise ValueError(f"{name} planted primary fails full-point certificate")
    flip = certificate(sorted_primary ^ 1, base, chain, arm)
    if flip.get("certified", False):
        raise ValueError("first primary bit flip certified")
    reversed_points = list(reversed(old_points))
    reversed_primary = primary_for(reversed_points, gamma, b)
    full_values(original_raw, reversed_primary, source_row["input_counts"]["live_gates"])
    try:
        full_values(sorted_raw, reversed_primary, row["live_gates"])
    except ValueError:
        reverse_sorted_rejected = True
    else:
        reverse_sorted_rejected = False
    if not reverse_sorted_rejected:
        raise ValueError("reversed tuple satisfies sorted formula")
    recovered = stable_points(reversed_points, gamma)
    if primary_for(recovered, gamma, b) != sorted_primary:
        raise ValueError("reversed tuple does not recover sorted witness")
    full_values(sorted_raw, sorted_primary, row["live_gates"])
    # These two controls exercise the point permutation itself. They are not
    # claimed as formula positives: an opposite pair can have an infinity
    # intermediate, which this seven-S3 circuit does not represent.
    repeated = old_points.copy()
    repeated[-1] = old_points[0]
    opposite = old_points.copy()
    p = old_points[0]
    opposite[-1] = (p[0], p[0] ^ p[1])
    controls = {}
    for name, points in (("repeated_coordinate", repeated), ("opposite_sign", opposite)):
        sorted_control = stable_points(points, gamma)
        if point_sum(points, b) != point_sum(sorted_control, b):
            raise ValueError(f"{name}: stable point permutation changed sum")
        if sorted_control.count(points[-1]) != points.count(points[-1]):
            raise ValueError(f"{name}: point multiplicity or sign lost")
        controls[name] = {"stable_sort_preserves_full_points": True,
                          "raw_sum": list(point_sum(points, b)) if point_sum(points, b) else None,
                          "ties": sum((phi_from_x(q[0], gamma) == phi_from_x(points[-1][0], gamma))
                                      for q in points)}
    return {"base_kind": label, "original_cnf_xor_checked": True,
            "original_model_complete": True,
            "sorted_cnf_xor_checked": True, "sorted_model_complete": True,
            "original_and_sorted_full_point_certified": True,
            "reversed_original_complete_witness_accepted": True,
            "reversed_sorted_order_rejected": True,
            "reversed_resort_certified": True,
            "first_primary_bit_flip_rejected": True,
            "constructed_controls": controls,
            "original_constraints": sum(source_row["input_counts"][key]
                                        for key in ("cnf_clauses", "native_xor_rows")),
            "sorted_cnf_clauses": len(clauses), "sorted_native_xor_rows": len(xors),
            "sorted_model_sha256": sha(model_blob)}


def verify() -> dict:
    manifest_blob = MANIFEST.read_bytes()
    manifest = json.loads(manifest_blob)
    positive_blob = POSITIVE.read_bytes()
    positive = json.loads(positive_blob)
    if manifest["positive_manifest_sha256"] != sha(positive_blob):
        raise ValueError("source positive manifest digest mismatch")
    gamma = manifest["gamma"]
    rows = {label: check_one(label, manifest["arms"][label], positive["controls"][label], gamma)
            for label in ("weighted", "local_random")}
    return {"schema": "icperf-binary-m8-sorted-input-verification-v1",
            "scope": "complete Boolean and full-point positive controls; no solver trial",
            "manifest_sha256": sha(manifest_blob), "checker_sha256": sha(Path(__file__).read_bytes()),
            "controls": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify()
    if args.out:
        with args.out.open("xb") as stream:
            stream.write((json.dumps(result, sort_keys=True, indent=2) + "\n").encode())
    print(json.dumps({"verified": list(result["controls"]), "solver_calls": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
