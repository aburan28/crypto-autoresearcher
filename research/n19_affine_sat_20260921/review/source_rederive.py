#!/usr/bin/env python3
"""Static, independent N19 source review. This script never invokes a solver."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "research/n19_affine_sat_20260921"
R = ROOT / "experiments/EXP-KIC-c3c732/runs/RUN-KIC-859f34"
N = 19
MASK = (1 << N) - 1
MOD = (1 << N) | 39
ORDER = 262543


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def mul(a: int, b: int) -> int:
    raw = 0
    for k in range(N):
        if b & (1 << k):
            raw ^= a << k
    for k in range(2 * N - 2, N - 1, -1):
        if raw & (1 << k):
            raw ^= MOD << (k - N)
    return raw


def square(a: int) -> int:
    return mul(a, a)


def inverse(a: int) -> int:
    if not a:
        raise ZeroDivisionError
    result = 1
    exponent = (1 << N) - 2
    while exponent:
        if exponent & 1:
            result = mul(result, a)
        a = square(a)
        exponent >>= 1
    return result


def on_curve(point) -> bool:
    if point is None:
        return True
    x, y = point
    return (0 <= x <= MASK and 0 <= y <= MASK
            and (square(y) ^ mul(x, y)) == (mul(square(x), x) ^ square(x) ^ 1))


def negative(point):
    return None if point is None else (point[0], point[0] ^ point[1])


def add(left, right):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u:
        if y != v or x == 0:
            return None
        slope = x ^ mul(y, inverse(x))
        z = square(slope) ^ slope ^ 1
        return z, square(x) ^ mul(slope ^ 1, z)
    slope = mul(y ^ v, inverse(x ^ u))
    z = square(slope) ^ slope ^ x ^ u ^ 1
    return z, mul(slope, x ^ z) ^ z ^ y


def scalar(point, amount: int):
    result = None
    while amount:
        if amount & 1:
            result = add(result, point)
        point = add(point, point)
        amount >>= 1
    return result


def s3(a: int, b: int, c: int) -> int:
    ab = mul(a, b)
    return square(mul(c, a ^ b)) ^ mul(c, ab) ^ square(ab) ^ 1


def base_from_seeds(recipe: dict):
    points = set()
    xvalues = set()
    for row in recipe["seed_points"]:
        point = tuple(row["point"])
        assert on_curve(point) and scalar(point, ORDER) is None
        for _ in range(N):
            points.add(point)
            points.add(negative(point))
            xvalues.add(point[0])
            point = square(point[0]), square(point[1])
    assert len(points) == 152 and len(xvalues) == 76
    assert all(on_curve(point) for point in points)
    return tuple(sorted(points)), tuple(sorted(xvalues))


def selector_map(recipe: dict) -> dict[int, tuple[int, int, int]]:
    a, b, c = recipe["affine_coordinates"]
    result = {}
    for j in range(N):
        for u in range(2):
            for v in range(2):
                x = a ^ (b if u else 0) ^ (c if v else 0)
                for _ in range(j):
                    x = square(x)
                assert x not in result
                result[x] = j, u, v
    assert len(result) == 76
    return result


def put_bits(assignment: dict[int, bool], variables: list[int], value: int):
    for bit, variable in enumerate(variables):
        assert variable not in assignment
        assignment[variable] = bool(value & (1 << bit))


def lit_value(literal: int, assignment: dict[int, bool]) -> bool:
    return assignment[abs(literal)] == (literal > 0)


def assign_domains(manifest: dict, values: tuple[int, int, int], arm: str,
                   xvalues: tuple[int, ...], selector: dict[int, tuple[int, int, int]],
                   assignment: dict[int, bool]) -> list[dict]:
    descriptors = []
    for number, x in enumerate(values, 1):
        assert x in xvalues
        if arm == "explicit_onehot":
            chosen = xvalues.index(x)
            vars_ = manifest["domain"][f"d{number}"]["selectors"]
            assert len(vars_) == 76
            for index, variable in enumerate(vars_):
                assert variable not in assignment
                assignment[variable] = index == chosen
            descriptors.append({"explicit_index": chosen})
        else:
            j, u, v = selector[x]
            entry = manifest["domain"][f"d{number}"]
            vars_ = entry["shifts"] if arm == "flat_onehot" else entry["shift_bits"]
            if arm == "flat_onehot":
                assert len(vars_) == 19
                for index, variable in enumerate(vars_):
                    assert variable not in assignment
                    assignment[variable] = index == j
            else:
                assert arm == "flat_binary" and len(vars_) == 5
                put_bits(assignment, vars_, j)
            uv = (entry["u"][0], entry["v"][0])
            assert all(variable not in assignment for variable in uv)
            assignment[uv[0]], assignment[uv[1]] = bool(u), bool(v)
            descriptors.append({"shift": j, "u": u, "v": v})
    return descriptors


def complete_ops(manifest: dict, assignment: dict[int, bool]):
    for op in manifest["ops"]:
        kind = op["kind"]
        if kind == "and":
            value = all(lit_value(literal, assignment) for literal in op["inputs"])
        elif kind == "xor":
            left, right = op["inputs"]
            value = lit_value(left, assignment) != lit_value(right, assignment)
        elif kind == "linear":
            value = bool(op["parity"] ^ (sum(assignment[v] for v in op["variables"]) & 1))
        elif kind == "prefix_or":
            value = any(assignment[v] for v in op["selectors"])
        else:
            raise ValueError(f"unknown archived operation {kind}")
        out = op["out"]
        if out in assignment:
            assert assignment[out] == value
        assignment[out] = value
    assert set(assignment) == set(range(1, manifest["nvars"] + 1))


def parse_and_compare_instance(path: Path, manifest: dict):
    cnf, xors = [], []
    lines = path.read_text().splitlines()
    header = lines[0].split()
    assert header[:2] == ["p", "cnf"]
    assert int(header[2]) == manifest["nvars"]
    assert int(header[3]) == len(manifest["clauses"]) + len(manifest["xor_rows"])
    for line in lines[1:]:
        if not line or line.startswith("c "):
            continue
        is_xor = line.startswith("x ")
        raw = line.split()[1:] if is_xor else line.split()
        row = [int(value) for value in raw]
        assert row[-1] == 0
        (xors if is_xor else cnf).append(row[:-1])
    assert cnf == manifest["clauses"]
    expected = []
    for item in manifest["xor_rows"]:
        variables = list(item["variables"])
        if item["rhs"] == 0:
            variables[0] = -variables[0]
        expected.append(variables)
    assert xors == expected
    return len(cnf), len(xors)


def validate_rows(manifest: dict, assignment: dict[int, bool]):
    assert set(assignment) == set(range(1, manifest["nvars"] + 1))
    bad_cnf = sum(not any(lit_value(literal, assignment) for literal in row)
                  for row in manifest["clauses"])
    bad_xor = sum((sum(assignment[v] for v in row["variables"]) & 1) != row["rhs"]
                  for row in manifest["xor_rows"])
    return bad_cnf, bad_xor


def parse_archived_model(stdout: str, exit_code: int, nvars: int):
    statuses, assignment = [], {}
    for line in stdout.splitlines():
        if line.startswith("s "):
            statuses.append(line[2:].strip())
        elif line.startswith("v "):
            for word in line.split()[1:]:
                literal = int(word)
                if not literal:
                    continue
                variable = abs(literal)
                if not 1 <= variable <= nvars:
                    raise ValueError("model variable out of range")
                value = literal > 0
                if variable in assignment and assignment[variable] != value:
                    raise ValueError("conflicting model literal")
                assignment[variable] = value
    expected = {10: "SATISFIABLE", 20: "UNSATISFIABLE", 15: "INDETERMINATE"}
    if exit_code not in expected or statuses != [expected[exit_code]]:
        raise ValueError("solver status/exit mismatch")
    if exit_code == 10 and set(assignment) != set(range(1, nvars + 1)):
        raise ValueError("incomplete SAT model")
    if exit_code != 10 and assignment:
        raise ValueError("model on non-SAT result")
    return assignment


def witness_from_x(values: tuple[int, int, int], q, points):
    lifts = [[p for p in points if p[0] == x] for x in values]
    assert all(len(row) == 2 for row in lifts)
    for candidate in itertools.product(*lifts):
        if add(add(candidate[0], candidate[1]), candidate[2]) == q:
            return candidate
    raise AssertionError("complete model has no exact group witness")


def model_lits(assignment: dict[int, bool]) -> list[int]:
    return [v if assignment[v] else -v for v in range(1, len(assignment) + 1)]


def run():
    recipe = load(P / "inputs/base.json")
    case_manifest = load(R / "case_manifest.json")
    points, xvalues = base_from_seeds(recipe)
    mapping = selector_map(recipe)
    assert set(mapping) == set(xvalues)
    science = case_manifest["science_cases"]
    by_index = {(c["case_index"], c["arm"]): c for c in science}
    constructed = []
    for case_index in (1, 3, 5, 7):
        native = by_index[case_index, "native_mitm"]
        raw = R / "raw/science" / f"{native['ordinal']:03d}_{native['id']}"
        result = load(raw / "result.json")
        assert result["status"] == "SAT" and result["arm"] == "native_mitm"
        q = tuple(native["Q"])
        ordered = tuple(sorted((tuple(row) for row in result["witness"]), key=lambda p: (p[0], p[1])))
        assert all(p in points for p in ordered)
        intermediate = add(ordered[0], ordered[1])
        assert intermediate is not None
        assert add(intermediate, ordered[2]) == q
        values = tuple(p[0] for p in ordered)
        assert values == tuple(sorted(values)) and s3(values[0], values[1], intermediate[0]) == 0
        assert s3(intermediate[0], values[2], q[0]) == 0
        for arm in ("explicit_onehot", "flat_onehot", "flat_binary"):
            case = by_index[case_index, arm]
            raw = R / "raw/science" / f"{case['ordinal']:03d}_{case['id']}"
            manifest_path = raw / "INSTANCE.manifest.json"
            manifest = load(manifest_path)
            assert manifest["public_q"] == list(q)
            assert len(manifest["inputs"]["t"]) == 19
            counts = parse_and_compare_instance(raw / "INSTANCE.cnf", manifest)
            assignment = {}
            for number, x in enumerate(values, 1):
                put_bits(assignment, manifest["inputs"][f"x{number}"], x)
            put_bits(assignment, manifest["inputs"]["t"], intermediate[0])
            selectors = assign_domains(manifest, values, arm, xvalues, mapping, assignment)
            complete_ops(manifest, assignment)
            bad_cnf, bad_xor = validate_rows(manifest, assignment)
            assert (bad_cnf, bad_xor) == (0, 0)
            recovered_x = tuple(sum(int(assignment[v]) << bit for bit, v in
                                    enumerate(manifest["inputs"][f"x{number}"]))
                                for number in (1, 2, 3))
            assert recovered_x == values
            group_witness = witness_from_x(values, q, points)
            literals = model_lits(assignment)
            constructed.append({
                "case_id": case["id"], "case_index": case_index, "arm": arm,
                "source": "reviewer_constructed_from_archived_native_witness_not_CMS",
                "public_q": list(q), "native_witness_sorted": [list(p) for p in ordered],
                "decoded_group_witness": [list(p) for p in group_witness],
                "x_values": list(values), "finite_intermediate_x": intermediate[0],
                "selector_values": selectors, "nvars": manifest["nvars"],
                "cnf_rows": counts[0], "xor_rows": counts[1],
                "original_cnf_sha256": digest((raw / "INSTANCE.cnf").read_bytes()),
                "original_manifest_sha256": digest(manifest_path.read_bytes()),
                "assignment_sha256": digest(json.dumps(literals, separators=(",", ":")).encode()),
                "signed_assignment": literals, "bad_original_cnf_rows": bad_cnf,
                "bad_original_xor_rows": bad_xor, "s3_links_zero": True,
                "exact_group_identity": True,
            })
    assert len(constructed) == 12

    control_replay = []
    for case in case_manifest["control_cases"]:
        raw = R / "raw/controls" / f"{case['ordinal']:03d}_{case['id']}"
        manifest = load(raw / "INSTANCE.manifest.json")
        counts = parse_and_compare_instance(raw / "INSTANCE.cnf", manifest)
        receipt = load(raw / "cms.receipt.json")
        code = receipt["exit_code"]
        model = parse_archived_model((raw / "cms.stdout").read_text(), code, manifest["nvars"])
        expected = 10 if case["stratum"] == "SAT" else 20
        assert code == expected
        if code == 10:
            assert validate_rows(manifest, model) == (0, 0)
            xvalues_control = tuple(sum(int(model[v]) << bit for bit, v in
                                        enumerate(manifest["inputs"][f"x{k}"]))
                                    for k in (1, 2, 3))
            assert xvalues_control == tuple(sorted(xvalues_control))
            generator = tuple(recipe["generator"])
            small = (generator, negative(generator))
            assert all(x == generator[0] for x in xvalues_control)
            witness = witness_from_x(xvalues_control, tuple(case["Q"]), small)
            group_valid = add(add(*witness[:2]), witness[2]) == tuple(case["Q"])
            assert group_valid
        else:
            group_valid = None
        control_replay.append({"case_id": case["id"], "exit_code": code,
                               "declared_variables": manifest["nvars"],
                               "cnf_rows": counts[0], "xor_rows": counts[1],
                               "complete_model": len(model) == manifest["nvars"] if code == 10 else None,
                               "original_rows_valid": validate_rows(manifest, model) == (0, 0) if code == 10 else None,
                               "group_valid": group_valid})
    assert len(control_replay) == 12
    science_cms_replay = []
    for case in science:
        if case["arm"] == "native_mitm":
            continue
        raw = R / "raw/science" / f"{case['ordinal']:03d}_{case['id']}"
        manifest = load(raw / "INSTANCE.manifest.json")
        counts = parse_and_compare_instance(raw / "INSTANCE.cnf", manifest)
        receipt = load(raw / "cms.receipt.json")
        assert manifest["public_q"] == case["Q"]
        assert receipt["exit_code"] == 15
        assert not parse_archived_model((raw / "cms.stdout").read_text(), 15, manifest["nvars"])
        science_cms_replay.append({"case_id": case["id"], "arm": case["arm"],
                                   "exit_code": 15, "status": "INDETERMINATE",
                                   "model_present": False, "nvars": manifest["nvars"],
                                   "cnf_rows": counts[0], "xor_rows": counts[1]})
    assert len(science_cms_replay) == 24
    pair_sums = {}
    for i, left in enumerate(points):
        for right in points[i:]:
            pair_sums.setdefault(add(left, right), (left, right))
    native_science_replay = []
    for case in science:
        if case["arm"] != "native_mitm":
            continue
        raw = R / "raw/science" / f"{case['ordinal']:03d}_{case['id']}"
        result = load(raw / "result.json")
        q = tuple(case["Q"])
        assert q not in points
        witness = None
        for point in points:
            remainder = add(q, negative(point))
            if remainder in pair_sums:
                left, right = pair_sums[remainder]
                witness = (left, right, point)
                break
        oracle = "SAT" if witness else "UNSAT"
        assert result["status"] == oracle
        if oracle == "SAT":
            actual = [tuple(x) for x in result["witness"]]
            assert len(actual) == 3 and all(x in points for x in actual)
            assert add(add(actual[0], actual[1]), actual[2]) == q
        native_science_replay.append({"case_id": case["id"], "status": oracle,
                                      "independent_pair_sum_oracle": oracle,
                                      "archived_witness_valid": True if oracle == "SAT" else None})
    assert len(native_science_replay) == 8
    first_control = case_manifest["control_cases"][0]
    control_raw = R / "raw/controls" / f"{first_control['ordinal']:03d}_{first_control['id']}"
    control_manifest = load(control_raw / "INSTANCE.manifest.json")
    genuine = parse_archived_model((control_raw / "cms.stdout").read_text(), 10,
                                   control_manifest["nvars"])
    flipped = genuine.copy()
    flipped[1] = not flipped[1]
    assert sum(validate_rows(control_manifest, flipped)) > 0
    missing_last = model_lits(genuine)[:-1]
    forged_stdout = "s SATISFIABLE\nv " + " ".join(map(str, missing_last)) + " 0\n"
    try:
        parse_archived_model(forged_stdout, 10, control_manifest["nvars"])
    except ValueError:
        missing_rejected = True
    else:
        missing_rejected = False
    assert missing_rejected
    generator = tuple(recipe["generator"])
    small = (generator, negative(generator))
    control_x = (generator[0],) * 3
    genuine_witness = witness_from_x(control_x, tuple(first_control["Q"]), small)
    changed_q = tuple(case_manifest["control_cases"][1]["Q"])
    forgery_rejections = {
        "original_row_bit": sum(validate_rows(control_manifest, flipped)) > 0,
        "missing_last_variable": missing_rejected,
        "changed_Q": control_manifest["public_q"] != list(changed_q),
        "nonbase_point": (0, 0) not in small and not on_curve((0, 0)),
        "wrong_group_sum": add(add(genuine_witness[0], genuine_witness[1]),
                               genuine_witness[2]) != changed_q,
        "swapped_case_label": load(control_raw / "result.json")["case_id"] !=
                              case_manifest["control_cases"][1]["id"],
    }
    assert all(forgery_rejections.values())
    output = {
        "schema": "crypto.autoresearch.n19_reviewer_constructed_models.v1",
        "task_id": "TASK-20260921-538005", "run_id": "RUN-KIC-859f34",
        "method": "Independent long-division GF(2^19), coordinate group law, Frobenius selector inverse, archived acyclic gate evaluation, complete original serialized CNF/native-XOR and exact group replay. No CMS/native worker launched.",
        "source_warning": "These 12 assignments are reviewer-constructed satisfiability certificates for already archived instances, not solver-produced completions, solver timings, or new scientific worker results.",
        "selected_base_points": len(points), "selected_base_x_values": len(xvalues),
        "selector_domain_values": len(mapping), "constructed_count": len(constructed),
        "constructed": constructed, "archived_external_control_replay": control_replay,
        "archived_science_cms_replay": science_cms_replay,
        "independent_native_science_oracle": native_science_replay,
        "forgery_rejections": forgery_rejections,
    }
    path = P / "review/constructed_sat_models.json"
    path.write_text(json.dumps(output, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"constructed": len(constructed), "control_sat_models": sum(x["exit_code"] == 10 for x in control_replay),
                      "control_unsat_statuses": sum(x["exit_code"] == 20 for x in control_replay),
                      "science_indeterminate_statuses": len(science_cms_replay),
                      "native_science_oracle": {status: sum(x["status"] == status for x in native_science_replay)
                                                for status in ("SAT", "UNSAT")},
                      "forgeries_rejected": forgery_rejections,
                      "dimensions": {arm: (next(x for x in constructed if x["arm"] == arm)["nvars"],
                                           next(x for x in constructed if x["arm"] == arm)["cnf_rows"],
                                           next(x for x in constructed if x["arm"] == arm)["xor_rows"])
                                     for arm in ("explicit_onehot", "flat_onehot", "flat_binary")},
                      "artifact_sha256": digest(path.read_bytes())}, indent=2))


if __name__ == "__main__":
    run()
