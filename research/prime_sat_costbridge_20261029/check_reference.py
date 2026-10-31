"""Independent certificate checker, conditional on the mathematical prime premise.

Uses the univariate S3 identity for completeness and division-free equations
for witnesses. Does not import producer routines or prove execution counters.
"""
import argparse
import hashlib
import json


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _field(value, p):
    _require(type(value) is int and 0 <= value < p, "noncanonical field element")
    return value


def _domain(spec, p):
    if type(spec) is list:
        values = [_field(x, p) for x in spec]
        index = frozenset(values)
        _require(len(index) == len(values), "duplicate domain coordinate")
        return iter(values), len(values), index.__contains__
    _require(type(spec) is dict and set(spec) == {"kind", "offset", "size"}, "malformed domain")
    _require(spec["kind"] == "interval", "unknown domain kind")
    start, length = _field(spec["offset"], p), spec["size"]
    _require(type(length) is int and 0 <= length <= p, "invalid window size")
    return ((start + i) % p for i in range(length)), length, lambda x: (x - start) % p < length


def _point(obj, p, a, b):
    _require(type(obj) is list and len(obj) == 2, "malformed point")
    x, y = (_field(v, p) for v in obj)
    _require((y*y - x*x*x - a*x - b) % p == 0, "point off curve")
    return x, y


def _witness(w, pair, p, a, b, target, in_first, in_second):
    _require(type(w) is dict and set(w) == {"P", "Q"}, "malformed witness")
    x, y = _point(w["P"], p, a, b)
    u, v = _point(w["Q"], p, a, b)
    _require(pair == (x, u) and in_first(x) and in_second(u), "witness projection/domain mismatch")
    r, t = target
    if x == u:
        _require((y + v) % p != 0, "witness sum is infinity")
        _require(y == v, "same-x witness is neither tangent nor inverse")
        numerator, denominator = (3*x*x + a) % p, 2*y % p
    else:
        numerator, denominator = (v - y) % p, (u - x) % p
    _require(denominator != 0, "zero witness slope denominator")
    _require((numerator*numerator - (r + x + u)*denominator*denominator) % p == 0,
             "witness sum has wrong abscissa")
    _require((numerator*(x - r) - (t + y)*denominator) % p == 0,
             "witness sum has wrong ordinate")


def _verify(instance, result):
    _require(type(instance) is dict, "instance must be object")
    fields = {"p", "a", "b", "target", "D1", "D2"}
    _require(fields <= set(instance) and not set(instance) - fields - {"nonresidue"}, "wrong instance fields")
    p = instance["p"]
    _require(type(p) is int and p > 3 and p % 2 == 1, "p must be prime > 3 (assumed)")
    _require(type(instance["a"]) is int and type(instance["b"]) is int, "invalid curve coefficients")
    a, b = instance["a"] % p, instance["b"] % p
    _require((4*a**3 + 27*b**2) % p != 0, "singular curve")
    r, t = _point(instance["target"], p, a, b)
    _require(t != 0, "target has zero ordinate")
    first_iter, first_size, in_first = _domain(instance["D1"], p)
    _, _, in_second = _domain(instance["D2"], p)
    _require(type(result) is dict, "result must be object")
    _require(result["schema"] == "prime-complement-reference/v1", "wrong result schema")
    mode = result["mode"]
    _require(mode in ("all", "first"), "unknown mode")
    _require(result["complete"] is (mode == "all"), "false completeness flag")
    _require(result["prime_assumed"] is True and result["primality_verified"] is False,
             "prime-premise flags must be explicit")
    digest = hashlib.sha256(json.dumps(instance, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    _require(result["input_sha256"] == digest, "input digest mismatch")
    z = _field(result["setup"]["nonresidue"], p)
    _require(pow(z, (p - 1)//2, p) == p - 1, "global Z is not Euler-certified nonsquare")
    if "nonresidue" in instance:
        _require(_field(instance["nonresidue"], p) == z, "supplied nonresidue mismatch")
    records = result["lift_records"]
    _require(type(records) is list, "lift records must be list")
    _require(len(records) <= first_size, "extra D1 records")
    if mode == "all":
        _require(len(records) == first_size, "incomplete D1 coverage")
    expected = set()
    for row in records:
        _require(type(row) is dict, "malformed lift record")
        x = _field(row["x"], p)
        _require(x == next(first_iter), "D1 records missing, duplicated or out of order")
        value = (x**3 + a*x + b) % p
        kind = row["kind"]
        if kind == "nonsquare":
            _require(set(row) == {"x", "kind", "twisted_root"}, "malformed nonroot row")
            w = _field(row["twisted_root"], p)
            _require(value != 0 and w != 0 and w*w % p == z*value % p, "invalid nonroot certificate")
            continue
        _require(kind in ("zero", "square") and set(row) == {"x", "kind", "roots"}, "malformed root row")
        roots = row["roots"]
        _require(type(roots) is list and len(roots) in (1, 2), "wrong root multiplicity")
        roots = [_field(y, p) for y in roots]
        y = roots[0]
        _require(y*y % p == value, "false square root")
        _require(roots == sorted({y, (-y) % p}), "missing or duplicate square-root sign")
        _require((kind == "zero") == (value == 0), "wrong zero-root classification")
        h = (x - r) % p
        c = (-r*x - 2*r*r - a) % p
        if h == 0:
            # S3 is linear: -4t^2*z + c^2 - 8t^2*r = 0.
            second_roots = {(c*c - 8*t*t*r) * pow(4*t*t, -1, p) % p}
        else:
            beta = (2*h*c - 4*t*t) % p
            inverse = pow(2*h*h, -1, p)
            second_roots = {(-beta + 4*t*y0) * inverse % p for y0 in roots}
        expected.update((x, second) for second in second_roots if in_second(second))
    output = result["projected_pairs"]
    _require(type(output) is list, "projected pairs must be list")
    pairs = []
    for pair in output:
        _require(type(pair) is list and len(pair) == 2, "malformed projected pair")
        pairs.append(tuple(_field(v, p) for v in pair))
    _require(pairs == sorted(set(pairs)), "projected pairs duplicated or unsorted")
    if mode == "all":
        _require(set(pairs) == expected, "projected set incomplete or spurious")
    else:
        _require(len(pairs) <= 1 and set(pairs) <= expected, "invalid first witness")
        if not pairs:
            _require(len(records) == first_size and not expected, "false first-mode exhaustion")
    witnesses = result["witnesses"]
    _require(type(witnesses) is list and len(witnesses) == len(pairs), "witness count mismatch")
    for pair, witness in zip(pairs, witnesses):
        _witness(witness, pair, p, a, b, (r, t), in_first, in_second)
    return {"valid": True, "findings": [], "completeness_verified": mode == "all",
            "witness_verified": bool(pairs), "prime_assumed": True,
            "primality_verified": False, "execution_counts_verified": False}


def verify(instance, result):
    try:
        return _verify(instance, result)
    except (ValueError, KeyError, TypeError, IndexError, StopIteration) as error:
        return {"valid": False, "findings": [str(error)], "completeness_verified": False,
                "witness_verified": False, "prime_assumed": True,
                "primality_verified": False, "execution_counts_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    with open(args.input) as f:
        instance = json.load(f)
    with open(args.result) as f:
        result = json.load(f)
    checked = verify(instance, result)
    print(json.dumps(checked, indent=2))
    raise SystemExit(0 if checked["valid"] else 1)


if __name__ == "__main__":
    main()
