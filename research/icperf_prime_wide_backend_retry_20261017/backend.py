"""Exact prime-field polynomial/root interface for TASK-20261017-68782f.

Run with the pinned Sage executable: ``sage -python backend.py --request in.json
--output out.json --raw-stdout stdout.log --raw-stderr stderr.log``.  The
request schema is described by ``solve_request``.  The CLI does not solve
archived natural systems; ``--parse-archive`` only validates their encoding.
All large input integers are parsed as Python integers and root coordinates
are serialized as decimal strings for consumers that cannot safely read JSON
integers above 2^53.
"""

from __future__ import annotations

import argparse
from decimal import Decimal
import gzip
import json
import signal
import sys
import time
import traceback
from pathlib import Path


def _no_float(value: str) -> None:
    raise ValueError(f"nonintegral JSON number {value!r}")


def load_json(path: str | Path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream, parse_int=int, parse_float=_no_float)


def load_scan_metadata(path: str | Path):
    """Parse the pinned scan's timing metadata without rounding arithmetic.

    Only the scan's documented timing and load-average paths may be decimal.
    Every coefficient, coordinate, seed and coset parameter remains an int.
    """
    with open(path, "rt", encoding="utf-8") as stream:
        data = json.load(stream, parse_int=int, parse_float=Decimal)

    def allowed(path: tuple) -> bool:
        if len(path) == 2 and path[0] == "scan" and path[1] in ("wall_seconds", "cpu_seconds"):
            return True
        if len(path) == 4 and path[0] == "attempts" and type(path[1]) is int and path[2] == "preparation" and path[3] in ("wall_seconds", "cpu_seconds"):
            return True
        return (len(path) == 5 and path[0] == "attempts" and type(path[1]) is int
                and path[2:4] == ("preparation", "loadavg_end") and type(path[4]) is int)

    def visit(value, path: tuple = ()) -> None:
        if isinstance(value, Decimal) and not allowed(path):
            raise ValueError(f"nonintegral arithmetic JSON number at {path}")
        if isinstance(value, dict):
            for key, child in value.items():
                visit(child, path + (key,))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, path + (index,))

    visit(data)
    return data


def exact_int(value, label: str) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str) and value and value.lstrip("-").isdigit():
        return int(value, 10)
    raise ValueError(f"{label} must be a decimal integer")


def validate_encoding(encoding: dict, p: int) -> dict:
    names = encoding["variables"]
    if not names or len(set(names)) != len(names):
        raise ValueError("variable names are empty or duplicate")
    if encoding["variable_count"] != len(names):
        raise ValueError("variable_count mismatch")
    equations = encoding["equations"]
    if encoding["equation_count"] != len(equations):
        raise ValueError("equation_count mismatch")
    count = 0
    largest = 0
    for equation in equations:
        if not equation:
            raise ValueError("empty equation")
        for term in equation:
            c = exact_int(term["coefficient"], "coefficient")
            if not 0 <= c < p:
                raise ValueError("coefficient outside GF(p)")
            largest = max(largest, c)
            seen = set()
            for index, exponent in term["powers"]:
                if type(index) is not int or not 0 <= index < len(names):
                    raise ValueError("variable index outside encoding")
                if index in seen or type(exponent) is not int or exponent <= 0:
                    raise ValueError("duplicate variable or nonpositive exponent")
                seen.add(index)
            count += 1
    if encoding.get("monomial_occurrences") != count:
        raise ValueError("monomial_occurrences mismatch")
    return {"variables": len(names), "equations": len(equations),
            "terms": count, "largest_coefficient": str(largest)}


def parse_archive(path: str | Path) -> dict:
    data = load_json(path)
    p = exact_int(data["curve"]["p"], "p")
    if p <= 2**53:
        raise ValueError("expected a prime-field input wider than 2^53")
    systems = data["systems"]
    if len(systems) != 21:
        raise ValueError("expected exactly 21 archived systems")
    rows = []
    for system in systems:
        target = system["target_point"]
        if len(target) != 2 or any(type(v) is not int or not 0 <= v < p for v in target):
            raise ValueError("invalid target coordinates")
        encodings = {name: validate_encoding(encoded, p)
                     for name, encoded in system["encodings"].items()}
        rows.append({"arm": system["arm"], "m": system["m"],
                     "target_x": str(target[0]), "target_y": str(target[1]),
                     "encodings": encodings})
    return {"status": "ok", "systems_parsed": len(rows), "p": str(p),
            "rows": rows, "systems_solved": 0}


def s3_value(p: int, a: int, b: int, x1: int, x2: int, x3: int) -> int:
    """Direct integer evaluation of the third summation polynomial."""
    square = ((x1 - x2) ** 2 * x3**2) % p
    middle = (-2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) * x3) % p
    constant = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    return (square + middle + constant) % p


def _polynomial_ring(request: dict):
    from sage.all import GF, PolynomialRing

    p = exact_int(request["p"], "p")
    if not (3 <= p < 2**63):
        raise ValueError("p outside supported exact 63-bit range")
    names = request["variables"]
    if not names or len(set(names)) != len(names):
        raise ValueError("invalid variable names")
    ring = PolynomialRing(GF(p), names=tuple(names), order="degrevlex")
    gens = ring.gens()
    polynomials = []
    for equation in request["equations"]:
        f = ring.zero()
        for term in equation:
            coefficient = exact_int(term["coefficient"], "coefficient")
            if not 0 <= coefficient < p:
                raise ValueError("coefficient outside GF(p)")
            monomial = ring(coefficient)
            seen = set()
            for index, exponent in term["powers"]:
                if type(index) is not int or not 0 <= index < len(gens):
                    raise ValueError("variable index outside ring")
                if index in seen or type(exponent) is not int or exponent <= 0:
                    raise ValueError("invalid exponent")
                seen.add(index)
                monomial *= gens[index] ** exponent
            f += monomial
        polynomials.append(f)
    return ring, polynomials


def solve_request(request: dict) -> dict:
    """Solve a bounded synthetic ideal, preserving every candidate variable.

    ``certified_no_solution`` is reserved for a unit ideal, witnessed by 1 in
    the Groebner basis.  A positive-dimensional ideal is ``unsupported``.
    Other empty finite-field root lists are returned as ``ok`` with an empty
    list and are not asserted inconsistent over an algebraic closure.
    """
    t0 = time.monotonic()
    try:
        ring, polynomials = _polynomial_ring(request)
        ideal = ring.ideal(polynomials)
        gb = ideal.groebner_basis()
        if any(f == ring.one() for f in gb):
            return {"status": "certified_no_solution", "roots": [],
                    "certificate": "Groebner basis contains 1",
                    "dimension": -1, "seconds": time.monotonic() - t0}
        dimension = int(ideal.dimension())
        if dimension > 0:
            return {"status": "unsupported", "reason": "positive_dimension",
                    "dimension": dimension, "roots": [],
                    "seconds": time.monotonic() - t0}
        names = request["variables"]
        roots = []
        for entry in ideal.variety():
            coordinates = [str(int(entry[ring.gen(i)])) for i in range(len(names))]
            roots.append({"variables": dict(zip(names, coordinates))})
        roots.sort(key=lambda entry: tuple(int(entry["variables"][name]) for name in names))
        return {"status": "ok", "roots": roots, "dimension": dimension,
                "root_count": len(roots), "seconds": time.monotonic() - t0}
    except MemoryError:
        return {"status": "memory", "roots": [], "seconds": time.monotonic() - t0}
    except TimeoutError:
        return {"status": "timeout", "roots": [], "seconds": time.monotonic() - t0}
    except (ValueError, KeyError, TypeError) as exc:
        return {"status": "invalid", "reason": str(exc), "roots": [],
                "seconds": time.monotonic() - t0}
    except NotImplementedError as exc:
        return {"status": "unsupported", "reason": str(exc), "roots": [],
                "seconds": time.monotonic() - t0}
    except Exception as exc:
        return {"status": "crashed", "reason": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(), "roots": [],
                "seconds": time.monotonic() - t0}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", help="JSON request with p, variables and equations")
    parser.add_argument("--parse-archive", help="validate 21 archived systems only")
    parser.add_argument("--output", required=True, help="machine-readable JSON response")
    parser.add_argument("--raw-stdout", required=True, help="external stdout capture path")
    parser.add_argument("--raw-stderr", required=True, help="external stderr capture path")
    parser.add_argument("--timeout-seconds", type=int, default=0,
                        help="positive per-call alarm; external watchdog remains required")
    args = parser.parse_args(argv)
    if bool(args.request) == bool(args.parse_archive):
        parser.error("choose exactly one of --request and --parse-archive")
    try:
        if args.timeout_seconds < 0:
            raise ValueError("negative timeout")
        if args.timeout_seconds:
            signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError()))
            signal.alarm(args.timeout_seconds)
        try:
            result = parse_archive(args.parse_archive) if args.parse_archive else solve_request(load_json(args.request))
        finally:
            if args.timeout_seconds:
                signal.alarm(0)
    except Exception as exc:
        result = {"status": "invalid", "reason": f"{type(exc).__name__}: {exc}"}
    result["raw_stdout_path"] = args.raw_stdout
    result["raw_stderr_path"] = args.raw_stderr
    Path(args.output).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "output": args.output}, sort_keys=True))
    return 0 if result["status"] in ("ok", "certified_no_solution") else 2


if __name__ == "__main__":
    sys.exit(main())
