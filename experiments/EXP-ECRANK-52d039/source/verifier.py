#!/usr/bin/env python3
"""Independent verifier for EXP-ECRANK-52d039.

The verifier intentionally does not import ``producer``.  It reconstructs the
abstract declarations, interval LDL arithmetic, curve arithmetic, logarithm
enclosure, and the height-pairing checks from the frozen declarations.  The
CLI consumes a producer JSON object and emits an exact comparison report.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def q(value):
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, str):
        return Fraction(value) if "/" in value else Fraction(int(value), 1)
    raise TypeError(value)


def text(value):
    value = q(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def encode(value):
    if isinstance(value, Fraction):
        return text(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def interval(lo, hi=None):
    lo, hi = q(lo), q(lo if hi is None else hi)
    if lo > hi:
        raise ValueError("inverted interval")
    return lo, hi


def add_i(a, b):
    return a[0] + b[0], a[1] + b[1]


def neg_i(a):
    return -a[1], -a[0]


def sub_i(a, b):
    return add_i(a, neg_i(b))


def mul_i(a, b):
    products = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return min(products), max(products)


def div_i(a, b):
    if b[0] <= 0 <= b[1]:
        raise ZeroDivisionError("interval denominator contains zero")
    return mul_i(a, (Fraction(1, b[1]), Fraction(1, b[0])))


def square_i(a):
    return mul_i(a, a)


def ldl_i(matrix):
    size = len(matrix)
    lower = [[interval(0) for _ in range(size)] for _ in range(size)]
    pivots = []
    failed = None
    for row in range(size):
        pivot = matrix[row][row]
        for k in range(row):
            pivot = sub_i(pivot, mul_i(square_i(lower[row][k]), pivots[k]))
        pivots.append(pivot)
        if pivot[0] <= 0 <= pivot[1]:
            failed = row
            break
        lower[row][row] = interval(1)
        for col in range(row + 1, size):
            numerator = matrix[col][row]
            for k in range(row):
                numerator = sub_i(
                    numerator,
                    mul_i(mul_i(lower[col][k], lower[row][k]), pivots[k]),
                )
            try:
                lower[col][row] = div_i(numerator, pivot)
            except ZeroDivisionError:
                failed = row
                break
        if failed is not None:
            break
    determinant = None
    if len(pivots) == size:
        determinant_i = interval(1)
        for pivot in pivots:
            determinant_i = mul_i(determinant_i, pivot)
        determinant = [text(determinant_i[0]), text(determinant_i[1])]
    return {
        "pivots": [[text(a), text(b)] for a, b in pivots],
        "pivot_lower_bounds": [text(a) for a, _ in pivots],
        "pivot_upper_bounds": [text(b) for _, b in pivots],
        "L": [[[text(a), text(b)] for a, b in row] for row in lower],
        "positive": failed is None and len(pivots) == size and all(a > 0 for a, _ in pivots),
        "unresolved_pivot": failed,
        "determinant_interval": determinant,
    }


def exact_ldl(matrix):
    return ldl_i([[interval(value) for value in row] for row in matrix])


def box(matrix, width):
    width = q(width)
    return [[interval(q(matrix[i][j]) - width, q(matrix[i][j]) + width) for j in range(len(matrix))] for i in range(len(matrix))]


def permuted(matrix, order):
    return [[matrix[order[i]][order[j]] for j in range(len(matrix))] for i in range(len(matrix))]


def declarations():
    one = Fraction(1)
    quarter = Fraction(1, 4)
    identity = [[one, Fraction(0), Fraction(0)], [Fraction(0), one, Fraction(0)], [Fraction(0), Fraction(0), one]]
    near = [[one, quarter, quarter], [quarter, one, quarter], [quarter, quarter, Fraction(1, 10) + Fraction(1, 2**20)]]
    singular = [[one, quarter, quarter], [quarter, one, quarter], [quarter, quarter, Fraction(1, 10)]]
    dependent = [[one, quarter, Fraction(2)], [quarter, one, Fraction(1, 2)], [Fraction(2), Fraction(1, 2), Fraction(4)]]
    return {"A0": identity, "A1": identity, "A2": near, "A3": singular, "A4": singular, "G_dep": dependent}


def start_facts():
    matrices = declarations()
    exact = {name: exact_ldl(matrix) for name, matrix in matrices.items() if name != "A4"}
    a3_member = [row[:] for row in matrices["A3"]]
    a3_member[2][2] += Fraction(1, 2**10)
    dep_member = [row[:] for row in matrices["G_dep"]]
    dep_member[2][2] += Fraction(1, 2**10)
    result = {
        "declared_pivots": {name: exact[name]["pivot_lower_bounds"] for name in exact},
        "A2_margin": text(Fraction(1, 2**20)),
        "A3_positive_box_member": {"matrix": encode(a3_member), "pivots": exact_ldl(a3_member)["pivot_lower_bounds"]},
        "G_dep_positive_box_member": {"matrix": encode(dep_member), "pivots": exact_ldl(dep_member)["pivot_lower_bounds"]},
        "G_dep_row3_equals_2_row1": all(matrices["G_dep"][2][j] == 2 * matrices["G_dep"][0][j] for j in range(3)),
        "schedule": [text(Fraction(1, 2**10 * 4**n)) for n in range(17)],
    }
    result["A0_control"] = exact["A0"]["positive"] and exact["A0"]["pivot_lower_bounds"] == ["1", "1", "1"] and exact["A0"]["determinant_interval"] == ["1", "1"]
    return result


def verdict(ldl):
    if ldl["positive"]:
        return "INDEPENDENT"
    if ldl["unresolved_pivot"] is not None or ldl["determinant_interval"] is None:
        return "UNRESOLVED"
    return "REJECTED"


def abstract_record(name, width, schedule_n=None, order=None):
    matrices = declarations()
    derived = q(width)
    declared = derived
    if name == "A4":
        derived = Fraction(1, 2**10)
        declared = q(width)
    if name.startswith("G_dep"):
        matrix = permuted(matrices["G_dep"], order)
    else:
        matrix = matrices[name]
    if name == "A4":
        if declared != derived:
            return {
                "object": name,
                "width": text(declared),
                "derived_width": text(derived),
                "verdict": "REJECTED",
                "witness_complete": False,
                "verifier_agreement": None,
                "rejection_reason": "declared width is not the derived width",
                "pivot_lower_bounds": [],
                "pivot_upper_bounds": [],
            }
    result_ldl = ldl_i(box(matrix, derived))
    result = {
        "object": name,
        "width": text(declared),
        "derived_width": text(derived),
        "schedule_n": schedule_n,
        "verdict": verdict(result_ldl),
        "witness_complete": bool(result_ldl["positive"]),
        "verifier_agreement": None,
        "pivot_lower_bounds": result_ldl["pivot_lower_bounds"],
        "pivot_upper_bounds": result_ldl["pivot_upper_bounds"],
        "pivots": result_ldl["pivots"],
        "determinant_interval": result_ldl["determinant_interval"],
        "L": result_ldl["L"],
        "widths": [[text(derived) for _ in row] for row in matrix],
    }
    if result_ldl["positive"]:
        result["witness"] = {"kind": "rational_interval_ldl", "pivot_lower_bounds": result_ldl["pivot_lower_bounds"], "determinant_interval": result_ldl["determinant_interval"], "L": result_ldl["L"]}
    if order is not None:
        result["permutation"] = list(order)
    return result


def verify_r1(produced):
    errors = []
    if produced.get("stage") != "R1":
        errors.append("stage is not R1")
    facts = start_facts()
    if produced.get("run_start_reverification") != facts:
        errors.append("run-start exact facts differ")
    if not facts["A0_control"]:
        errors.append("independent C1 recomputation failed")
    expected = []
    expected.append(abstract_record("A0", Fraction(0)))
    for name, width in (("A1", Fraction(1, 2**10)), ("A1", Fraction(1, 2**30)), ("A3", Fraction(1, 2**10)), ("A3", Fraction(1, 2**30))):
        expected.append(abstract_record(name, width))
    for n in range(17):
        expected.append(abstract_record("A2", Fraction(1, 2**10 * 4**n), schedule_n=n))
    expected.append(abstract_record("A4", Fraction(1, 2**30), schedule_n=0))
    for idx, order in enumerate(((0, 1, 2), (2, 1, 0), (0, 2, 1))):
        for width in (Fraction(1, 2**10), Fraction(1, 2**30)):
            expected.append(abstract_record(f"G_dep_perm_{idx}", width, order=order))
    nstars = {}
    matrices = declarations()
    for name in ("A1", "A2"):
        values = []
        for n in range(17):
            if ldl_i(box(matrices[name], Fraction(1, 2**10 * 4**n)))["positive"]:
                values.append(n)
        nstars[name] = min(values) if values else None
    for record in expected:
        if record["object"] in nstars and record["schedule_n"] is not None:
            record["n_star"] = nstars[record["object"]]
    actual = produced.get("verdict_ledger") or []
    if len(actual) != len(expected):
        errors.append(f"expected 29 abstract records, got {len(actual)}")
    for index, (want, got) in enumerate(zip(expected, actual)):
        got_core = dict(got)
        got_core["verifier_agreement"] = None
        if got_core != want:
            errors.append(f"abstract record {index} differs")
            if len(errors) > 8:
                break
    if produced.get("n_star") != nstars:
        errors.append("n_star differs")
    first = actual[0] if actual else {}
    if not (first.get("verdict") == "INDEPENDENT" and first.get("pivot_lower_bounds") == ["1", "1", "1"] and first.get("determinant_interval") == ["1", "1"]):
        errors.append("C1 producer admission record differs")
    return {"stage": "R1", "independent_rederivation": True, "agreement": not errors, "errors": errors, "record_count": len(actual), "n_star": nstars, "run_start_facts_match": produced.get("run_start_reverification") == facts}


# -------------------------- independent elliptic path --------------------------

INFINITY = None


def curve_from_serialized(value):
    return {key: q(value[key]) if key != "label" else value[key] for key in ("a1", "a2", "a3", "a4", "a6", "label")}


def neg(E, point):
    if point is INFINITY:
        return INFINITY
    x, y = point
    return x, -E["a1"] * x - E["a3"] - y


def add(E, left, right):
    if left is INFINITY:
        return right
    if right is INFINITY:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2:
        if y2 == -E["a1"] * x1 - E["a3"] - y1:
            return INFINITY
        denominator = 2 * y1 + E["a1"] * x1 + E["a3"]
        if denominator == 0:
            return INFINITY
        slope = (3 * x1 * x1 + 2 * E["a2"] * x1 + E["a4"] - E["a1"] * y1) / denominator
        intercept = (-x1**3 + E["a4"] * x1 + 2 * E["a6"] - E["a3"] * y1) / denominator
    else:
        slope = (y2 - y1) / (x2 - x1)
        intercept = (y1 * x2 - y2 * x1) / (x2 - x1)
    x3 = slope * slope + E["a1"] * slope - E["a2"] - x1 - x2
    y3 = -(slope + E["a1"]) * x3 - intercept - E["a3"]
    return x3, y3


def double(E, point):
    return add(E, point, point)


def bit_length(point):
    if point is INFINITY:
        return {"x_num": 0, "x_den": 0, "y_num": 0, "y_den": 0, "max": 0}
    x, y = point
    values = {"x_num": abs(x.numerator).bit_length(), "x_den": x.denominator.bit_length(), "y_num": abs(y.numerator).bit_length(), "y_den": y.denominator.bit_length()}
    values["max"] = max(values.values())
    return values


def invariant_data(E):
    a1, a2, a3, a4, a6 = (E[x] for x in ("a1", "a2", "a3", "a4", "a6"))
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    delta = -b2 * b2 * b8 - 8 * b4**3 - 27 * b6 * b6 + 9 * b2 * b4 * b6
    return b2, b4, b6, b8, delta


def derive_c(E):
    b2, b4, b6, b8, delta = invariant_data(E)
    bound = max(Fraction(1), abs(b2), abs(b4), abs(b6), abs(b8))
    first = 8 * bound + 4
    second = 2 * first + 2
    c = second + 1
    checks = [
        {"name": "B_bounds_b2", "lhs": text(bound), "rhs": text(abs(b2)), "holds": bound >= abs(b2)},
        {"name": "B_bounds_b4", "lhs": text(bound), "rhs": text(abs(b4)), "holds": bound >= abs(b4)},
        {"name": "B_bounds_b6", "lhs": text(bound), "rhs": text(abs(b6)), "holds": bound >= abs(b6)},
        {"name": "B_bounds_b8", "lhs": text(bound), "rhs": text(abs(b8)), "holds": bound >= abs(b8)},
        {"name": "delta_nonzero", "lhs": text(delta), "holds": delta != 0},
        {"name": "k0_positive", "lhs": text(first), "holds": first > 0},
        {"name": "k1_ge_k0", "lhs": text(second), "rhs": text(first), "holds": second >= first},
        {"name": "C_positive", "lhs": text(c), "holds": c > 0},
    ]
    return {"B": text(bound), "k0": text(first), "k1": text(second), "C": text(c), "delta": text(delta), "invariants": {"b2": text(b2), "b4": text(b4), "b6": text(b6), "b8": text(b8)}, "checks": checks, "all_checks": all(item["holds"] for item in checks)}


def log_interval(value, bits=96):
    value = q(value)
    if value <= 0:
        raise ValueError("log domain")
    power = value.numerator.bit_length() - value.denominator.bit_length()
    scaled = value / (2**power) if power >= 0 else value * (2**(-power))
    while scaled >= 2:
        scaled /= 2
        power += 1
    while scaled < 1:
        scaled *= 2
        power -= 1

    def series(x):
        t = (x - 1) / (x + 1)
        terms = 1
        while True:
            remainder = 2 * abs(t) ** (2 * terms + 1) / (Fraction(2 * terms + 1) * (1 - t * t))
            if remainder < Fraction(1, 2 ** (bits + 8)):
                break
            terms *= 2
        total = Fraction(0)
        term = t
        for index in range(terms):
            total += 2 * term / (2 * index + 1)
            term *= t * t
        remainder = 2 * abs(t) ** (2 * terms + 1) / (Fraction(2 * terms + 1) * (1 - t * t))
        return total - remainder, total + remainder, terms, remainder

    ln_two = series(Fraction(2))
    ln_scaled = series(scaled)
    lower = power * ln_two[0] + ln_scaled[0]
    upper = power * ln_two[1] + ln_scaled[1]
    return {"interval": [text(lower), text(upper)], "terms_ln2": ln_two[2], "terms_scaled": ln_scaled[2], "remainder_ln2": text(ln_two[3]), "remainder_scaled": text(ln_scaled[3]), "scale_power_two": power}


def height(point):
    if point is INFINITY:
        return {"interval": ["0", "0"], "H": "1", "log_certificate": None}
    x, _ = point
    numerator = max(Fraction(1), abs(x.numerator), x.denominator)
    certificate = log_interval(numerator)
    return {"interval": certificate["interval"], "H": text(numerator), "log_certificate": certificate}


def sub_interval(a, b):
    return a[0] - b[1], a[1] - b[0]


def pair_ldl(first, second, cross):
    pivot_one = first
    try:
        lower = div_i(cross, pivot_one)
        pivot_two = sub_interval(second, mul_i(mul_i(lower, lower), pivot_one))
    except ZeroDivisionError:
        return {"pivots": [[text(pivot_one[0]), text(pivot_one[1])]], "pivot_lower_bounds": [text(pivot_one[0])], "positive": False, "unresolved_pivot": 1, "determinant_interval": None}
    return {"pivots": [[text(pivot_one[0]), text(pivot_one[1])], [text(pivot_two[0]), text(pivot_two[1])]], "pivot_lower_bounds": [text(pivot_one[0]), text(pivot_two[0])], "pivot_upper_bounds": [text(pivot_one[1]), text(pivot_two[1])], "positive": pivot_one[0] > 0 and pivot_two[0] > 0, "unresolved_pivot": None if not (pivot_two[0] <= 0 <= pivot_two[1]) else 1, "determinant_interval": [text(pivot_one[0] * pivot_two[0]), text(pivot_one[1] * pivot_two[1])], "L21": [text(lower[0]), text(lower[1])]}


def canonical(height_interval_value, c, exponent):
    denominator = 4**exponent
    correction = q(c) / denominator
    return height_interval_value[0] / denominator - correction, height_interval_value[1] / denominator + correction


def elliptic_record(E, point, c, n):
    p = point
    p2 = double(E, point)
    p3 = add(E, p2, point)
    for _ in range(n):
        p, p2, p3 = double(E, p), double(E, p2), double(E, p3)
    h1 = height(p)
    h2 = height(p2)
    h3 = height(p3)
    i1 = canonical((q(h1["interval"][0]), q(h1["interval"][1])), c, n)
    i2 = canonical((q(h2["interval"][0]), q(h2["interval"][1])), c, n)
    i3 = canonical((q(h3["interval"][0]), q(h3["interval"][1])), c, n)
    pairing_i = sub_interval(sub_interval(i3, i1), i2)
    pairing_i = pairing_i[0] / 2, pairing_i[1] / 2
    first = {"object": "O1", "n": n, "verdict": "INDEPENDENT" if i1[0] > 0 else "UNRESOLVED", "witness_complete": i1[0] > 0, "pivot_lower_bounds": [text(i1[0])], "pivot_upper_bounds": [text(i1[1])], "enclosures": {"lambda_P": [text(i1[0]), text(i1[1])]}, "verifier_agreement": None}
    ldl = pair_ldl(i1, i2, pairing_i)
    second = {"object": "O2", "n": n, "verdict": "INDEPENDENT" if ldl["positive"] else "UNRESOLVED", "witness_complete": ldl["positive"], "pivot_lower_bounds": ldl["pivot_lower_bounds"], "pivot_upper_bounds": ldl.get("pivot_upper_bounds", []), "enclosures": {"lambda_P": [text(i1[0]), text(i1[1])], "lambda_2P": [text(i2[0]), text(i2[1])], "pairing": [text(pairing_i[0]), text(pairing_i[1])]}, "ldl": ldl, "verifier_agreement": None}
    return first, second


def verify_r2(produced):
    errors = []
    if produced.get("stage") != "R2":
        errors.append("stage is not R2")
    curve_data = produced.get("curve")
    point_data = produced.get("point_P")
    derivation = produced.get("C_E_derivation")
    if not isinstance(curve_data, dict) or not isinstance(point_data, list) or not isinstance(derivation, dict):
        return {"stage": "R2", "independent_rederivation": False, "agreement": False, "errors": ["missing curve, point, or C(E) derivation"], "record_count": len(produced.get("verdict_ledger") or [])}
    E = curve_from_serialized(curve_data)
    point = (q(point_data[0]), q(point_data[1]))
    own_derivation = derive_c(E)
    if own_derivation != derivation:
        errors.append("C(E) blind derivation differs")
    if produced.get("C_E") != own_derivation["C"]:
        errors.append("C(E) differs")
    actual = produced.get("verdict_ledger") or []
    expected = []
    c = q(own_derivation["C"])
    for n in range(len(actual) // 2):
        expected.extend(elliptic_record(E, point, c, n))
    if len(actual) != len(expected):
        errors.append(f"elliptic record count differs: expected paired replay for {len(actual)} records")
    for index, (want, got) in enumerate(zip(expected, actual)):
        got_core = dict(got)
        got_core["verifier_agreement"] = None
        if got_core != want:
            errors.append(f"elliptic record {index} differs")
            if len(errors) > 8:
                break
    # The verifier checks the selected point and curve independently.  The
    # large Mazur multiples remain producer-side archival observations; every
    # load-bearing C(E), enclosure, pivot, and verdict is re-derived here.
    if not (invariant_data(E)[4] != 0):
        errors.append("selected curve is singular")
    x, y = point
    if y * y + E["a1"] * x * y + E["a3"] * y != x**3 + E["a2"] * x * x + E["a4"] * x + E["a6"]:
        errors.append("selected point is off curve")
    return {"stage": "R2", "independent_rederivation": True, "agreement": not errors, "errors": errors, "record_count": len(actual), "C_E": own_derivation["C"], "candidate_checks_rederived": True}


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in {"r1", "r2"}:
        raise SystemExit("usage: verifier.py r1|r2 producer.json")
    with open(sys.argv[2], encoding="utf-8") as handle:
        produced = json.load(handle)
    result = verify_r1(produced) if sys.argv[1] == "r1" else verify_r2(produced)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    raise SystemExit(0 if result["agreement"] else 1)


if __name__ == "__main__":
    main()
