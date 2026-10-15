"""Exact tiny-field software primitives; importing this module executes no study.

Elements are coefficient tuples (constant coefficient first), points are pairs of
elements, and None denotes O. All enumeration is deterministic. Arithmetic is
stdlib-only and intended for explicitly bounded toy inputs, not cryptographic
field construction. ``python tools/lattice_ic_core.py --check DIR`` checks only
the artifact envelope/hash, not a scientific conclusion or execution authority.
"""
from __future__ import annotations

from collections import Counter as _Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
from importlib import metadata
from itertools import product
import json
import math
from numbers import Integral
from operator import index
from pathlib import Path
import platform
import shlex
import sys
import time


def is_prime(n):
    """Exact trial-division primality for bounded toy parameters."""
    return isinstance(n, int) and not isinstance(n, bool) and n >= 2 and all(
        n % d for d in range(2, math.isqrt(n) + 1))


def factorize(n):
    """Exact positive-integer factorization; integer-keyed arithmetic dictionary."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("factorization requires a positive integer")
    factors, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


class Counter:
    """Stable operation/phase interface: inc(name,n=1), phase(name), snapshot().

    snapshot() returns JSON-safe {operations: {name: count}, phases: {name:
    {calls, wall_seconds, cpu_seconds, operations}}}. Global operation counts are
    inclusive; each operation belongs to the innermost named phase only. Phase
    timings are inclusive (nested intervals overlap), never an additive total.
    High-level operation counts and their field primitives also overlap; no common
    unit-cost weighting is asserted. Timing contexts measure actual local calls.
    """

    def __init__(self):
        self.operations = _Counter()
        self.phases = {}
        self._active = []

    def inc(self, name, n=1):
        if not isinstance(name, str) or not name or not isinstance(n, int) or n < 0:
            raise ValueError("operation name and nonnegative integer increment required")
        self.operations[name] += n
        if self._active:
            self.phases[self._active[-1]]["operations"][name] += n

    bump = inc

    @contextmanager
    def phase(self, name):
        if not isinstance(name, str) or not name:
            raise ValueError("phase name required")
        record = self.phases.setdefault(name, {"calls": 0, "wall_seconds": 0.0,
                                              "cpu_seconds": 0.0, "operations": _Counter()})
        record["calls"] += 1
        wall, cpu = time.monotonic(), time.process_time()
        self._active.append(name)
        try:
            yield self
        finally:
            self._active.pop()
            record["wall_seconds"] += time.monotonic() - wall
            record["cpu_seconds"] += time.process_time() - cpu

    def snapshot(self):
        return {"operations": dict(sorted(self.operations.items())),
                "phases": {name: {**record, "operations": dict(sorted(record["operations"].items()))}
                           for name, record in sorted(self.phases.items())}}


OperationCounter = Counter


class Field:
    """Field(p, quadratic=None or (c0,c1)), for X²+c1*X+c0.

    Canonical elements are length-one/two tuples; integers embed as constants.
    coerce accepts integers or a tuple/list of exactly degree coefficients.
    elements() yields coefficient-lexicographic tuples. key() is a canonical tuple;
    encode() is the corresponding JSON list. zero, one, degree, order/q, p,
    quadratic and counter are public. Counts record calls, not CPU instructions.
    """

    def __init__(self, p, quadratic=None, *, counter=None):
        if not is_prime(p):
            raise ValueError("p must be an exactly verified prime")
        self.p, self.counter = p, counter if counter is not None else Counter()
        self.quadratic = None
        self.degree = 1
        if quadratic is not None:
            if not isinstance(quadratic, (tuple, list)) or len(quadratic) != 2:
                raise ValueError("quadratic must be (c0,c1)")
            if any(not isinstance(c, Integral) for c in quadratic):
                raise TypeError("polynomial coefficients must be integers")
            c0, c1 = (int(c) % p for c in quadratic)
            if p == 2:
                reducible = any((x*x+c1*x+c0) % p == 0 for x in range(p))
            else:
                discriminant = (c1*c1-4*c0) % p
                reducible = discriminant == 0 or pow(discriminant, (p-1)//2, p) == 1
            if reducible:
                raise ValueError("quadratic polynomial is reducible")
            self.quadratic, self.degree = (c0, c1), 2
        self.order = self.q = p ** self.degree
        self.zero = (0,) * self.degree
        self.one = (1,) + (0,) * (self.degree - 1)

    def coerce(self, value):
        if isinstance(value, Integral):
            return (int(value) % self.p,) + (0,) * (self.degree-1)
        if (not isinstance(value, (tuple, list)) or len(value) != self.degree
                or any(not isinstance(c, Integral) for c in value)):
            raise TypeError(f"expected integer or {self.degree} integer coefficients")
        return tuple(int(c) % self.p for c in value)

    def key(self, value):
        return self.coerce(value)

    def encode(self, value):
        return list(self.coerce(value))

    def elements(self):
        return product(range(self.p), repeat=self.degree)

    def add(self, a, b):
        self.counter.inc("field.add")
        return tuple((x+y) % self.p for x, y in zip(self.coerce(a), self.coerce(b)))

    def neg(self, a):
        self.counter.inc("field.neg")
        return tuple(-x % self.p for x in self.coerce(a))

    def sub(self, a, b):
        self.counter.inc("field.sub")
        return tuple((x-y) % self.p for x, y in zip(self.coerce(a), self.coerce(b)))

    def mul(self, a, b):
        self.counter.inc("field.mul")
        a, b = self.coerce(a), self.coerce(b)
        if self.degree == 1:
            return (a[0]*b[0] % self.p,)
        c0, c1 = self.quadratic
        return ((a[0]*b[0]-c0*a[1]*b[1]) % self.p,
                (a[0]*b[1]+a[1]*b[0]-c1*a[1]*b[1]) % self.p)

    def inv(self, a):
        self.counter.inc("field.inv")
        a = self.coerce(a)
        if a == self.zero:
            raise ZeroDivisionError("zero has no field inverse")
        if self.degree == 1:
            return (pow(a[0], -1, self.p),)
        c0, c1 = self.quadratic
        norm = (a[0]*a[0]-c1*a[0]*a[1]+c0*a[1]*a[1]) % self.p
        inverse_norm = pow(norm, -1, self.p)
        return ((a[0]-c1*a[1])*inverse_norm % self.p,
                -a[1]*inverse_norm % self.p)

    def pow(self, a, exponent):
        self.counter.inc("field.pow")
        if not isinstance(exponent, Integral):
            raise TypeError("integer exponent required")
        a, exponent = self.coerce(a), int(exponent)
        if exponent < 0:
            a, exponent = self.inv(a), -exponent
        value = self.one
        while exponent:
            if exponent & 1:
                value = self.mul(value, a)
            exponent >>= 1
            if exponent:
                a = self.mul(a, a)
        return value


class Curve:
    """Short Weierstrass Curve(field,A,B), characteristic >3; None is O.

    points() returns a fresh list, O first then lexicographic (x,y) coefficient
    tuples; the immutable enumeration cache uses a square-to-all-y table in O(q)
    field operations plus sorting. add/neg/mul accept only actual curve points,
    normalize coefficients, and handle verticals, zero-y doubling and O explicitly.
    Scalar multiplication uses mul(integer,point), including negative integers.
    Public A/B and a/b aliases are field elements; field/counter are shared.
    """

    def __init__(self, field, A, B):
        if not isinstance(field, Field) or field.p <= 3:
            raise ValueError("short Weierstrass implementation requires characteristic >3")
        self.field = self.f = field
        self.counter = field.counter
        self.A = self.a = field.coerce(A)
        self.B = self.b = field.coerce(B)
        discriminant = field.add(field.mul(4, field.pow(self.A, 3)),
                                 field.mul(27, field.pow(self.B, 2)))
        if discriminant == field.zero:
            raise ValueError("singular curve")
        self._points = None

    def rhs(self, x):
        f = self.field
        return f.add(f.add(f.pow(x, 3), f.mul(self.A, x)), self.B)

    def is_on_curve(self, point):
        if point is None:
            return True
        try:
            if len(point) != 2:
                return False
            x, y = (self.field.coerce(c) for c in point)
            return self.field.mul(y, y) == self.rhs(x)
        except (TypeError, ValueError):
            return False

    def _point(self, point):
        if point is None:
            return None
        if not self.is_on_curve(point):
            raise ValueError("point is not on this curve")
        return tuple(self.field.coerce(c) for c in point)

    def points(self):
        if self._points is None:
            self.counter.inc("curve.enumeration")
            f, roots = self.field, {}
            elements = list(f.elements())
            for y in elements:
                roots.setdefault(f.mul(y, y), []).append(y)
            self._points = (None,) + tuple((x, y) for x in elements
                                           for y in roots.get(self.rhs(x), ()))
        else:
            self.counter.inc("curve.enumeration_cache_hit")
        return list(self._points)

    def neg(self, point):
        self.counter.inc("curve.neg")
        point = self._point(point)
        return None if point is None else (point[0], self.field.neg(point[1]))

    def add(self, left, right):
        self.counter.inc("curve.add")
        left, right = self._point(left), self._point(right)
        if left is None:
            return right
        if right is None:
            return left
        f, (x1, y1), (x2, y2) = self.field, left, right
        if x1 == x2:
            if f.add(y1, y2) == f.zero:
                return None
            slope = f.mul(f.add(f.mul(3, f.mul(x1, x1)), self.A), f.inv(f.mul(2, y1)))
        else:
            slope = f.mul(f.sub(y2, y1), f.inv(f.sub(x2, x1)))
        x3 = f.sub(f.sub(f.mul(slope, slope), x1), x2)
        return x3, f.sub(f.mul(slope, f.sub(x1, x3)), y1)

    def mul(self, scalar, point):
        self.counter.inc("curve.mul")
        if not isinstance(scalar, Integral):
            raise TypeError("integer scalar required")
        point, scalar = self._point(point), int(scalar)
        if scalar < 0:
            point, scalar = self.neg(point), -scalar
        value = None
        while scalar:
            if scalar & 1:
                value = self.add(value, point)
            scalar >>= 1
            if scalar:
                point = self.add(point, point)
        return value


def encode_point(field, point):
    """encode_point(field_or_curve,point) -> null or [encoded_x,encoded_y].

    For convenience encode_point(point,field_or_curve) is also accepted. This
    encodes representation only; use curve.is_on_curve for an actual point check.
    """
    if isinstance(point, (Field, Curve)):
        field, point = point, field
    if isinstance(field, Curve):
        field = field.field
    if not isinstance(field, Field):
        raise TypeError("Field or Curve required")
    if point is None:
        return None
    if len(point) != 2:
        raise ValueError("point must contain two field elements")
    return [field.encode(point[0]), field.encode(point[1])]


def select_prime_subgroup(curve, r=None, min_prime=5, require_valuation_one=True):
    """Return deterministic dict {admitted,reason,order,factorization,r,P,G,certificate}.

    Count the complete rational group, factor exactly, choose largest admissible
    prime (or requested r), then the first lexicographic nonzero point killed by
    r. G[j]=[j]P, j=0..r-1, is deterministic scalar order, not point-lex order.
    P/G retain canonical tuples for arithmetic. factorization uses string prime
    keys for JSON stability. Rejected cells have P/G/r null plus requested_r;
    reasons never substitute another requested cell. No endomorphism stability
    certificate is inferred when r² divides the rational group order.
    """
    if not isinstance(min_prime, int) or min_prime < 2:
        raise ValueError("min_prime must be at least two")
    points = curve.points()
    order = len(points)
    factors = factorize(order)
    result = {"admitted": False, "reason": None, "order": order,
              "factorization": {str(p): e for p, e in factors.items()},
              "requested_r": r, "r": None, "P": None, "G": None,
              "certificate": {"count_method": "complete_rational_point_enumeration",
                              "field_order": curve.field.order,
                              "require_valuation_one": require_valuation_one}}
    if r is not None and (not is_prime(r) or r < min_prime):
        result["reason"] = "requested r is not a prime meeting min_prime"
        return result
    candidates = [r] if r is not None else sorted(factors, reverse=True)
    candidates = [p for p in candidates if p >= min_prime and p in factors
                  and (not require_valuation_one or factors[p] == 1)]
    if not candidates:
        result["reason"] = "no requested/admissible prime divisor with required valuation"
        return result
    r = candidates[0]
    generator = next((point for point in points if point is not None
                      and curve.mul(r, point) is None), None)
    if generator is None:
        raise ArithmeticError("enumerated group has prime divisor but no order-r point")
    group = [None]
    for _ in range(1, r):
        group.append(curve.add(group[-1], generator))
    if len(set(group)) != r or curve.add(group[-1], generator) is not None:
        raise ArithmeticError("subgroup enumeration/order certificate failed")
    result.update(admitted=True, r=r, P=generator, G=group)
    result["certificate"].update(prime_verified=True, nonzero_generator=True,
                                  r_times_P_is_O=True, distinct_group_points=r,
                                  valuation=factors[r], cofactor=order//r,
                                  unique_r_subgroup=factors[r] == 1)
    return result


def rank_mod(rows, r):
    """Exact row rank over prime F_r, including empty/rectangular matrices."""
    if not is_prime(r):
        raise ValueError("rank modulus must be prime")
    matrix = [[index(x) % r for x in row] for row in rows]
    if not matrix:
        return 0
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("ragged matrix")
    rank = 0
    for column in range(columns):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, r)
        matrix[rank] = [x*inverse % r for x in matrix[rank]]
        for i in range(rank+1, len(matrix)):
            coefficient = matrix[i][column]
            matrix[i] = [(x-coefficient*y) % r for x, y in zip(matrix[i], matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def poly_eval_mod(coefficients, x, modulus):
    """Evaluate integer polynomial, coefficients ascending, modulo modulus."""
    if not isinstance(modulus, int) or modulus < 2:
        raise ValueError("modulus must be at least two")
    x = index(x)
    result = 0
    for coefficient in reversed(list(coefficients)):
        result = (result*x+index(coefficient)) % modulus
    return result


def _json_safe(value):
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite result value")
        return value
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (tuple, list)):
        return [_json_safe(x) for x in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, (str, int)) or isinstance(key, bool):
                raise TypeError("JSON object keys must be strings/integers")
            text = str(key)
            if text in result:
                raise ValueError("JSON key normalization collision")
            result[text] = _json_safe(item)
        return result
    raise TypeError(f"unsupported exact result type: {type(value).__name__}")


def _json_bytes(value):
    return (json.dumps(_json_safe(value), sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def _installed_dependencies():
    result = {}
    for distribution, module in (("sympy", "sympy"), ("fpylll", "fpylll"), ("PyYAML", "yaml")):
        try:
            version, reason = metadata.version(distribution), None
        except metadata.PackageNotFoundError:
            version, reason = None, "not installed in this Python runtime"
        result[distribution] = {"installed_version": version, "loaded": module in sys.modules,
                                "unavailable_reason": reason}
    return result


def _read_object(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def write_artifacts(result, directory, seed, started, wall_start, cpu_start):
    """Write raw-result.json and nested manifest.yaml exactly once (JSON is YAML).

    Inputs: JSON-safe result with parameters/checks, output directory, integer seed,
    ISO started timestamp and time.monotonic()/process_time() starts. Read actual
    launch.json/environment.json from that directory; never invoke Git, infer a
    clean tree, authorize execution, or overwrite supervisor files. Real EXP comes
    from launch or canonical EXP/runs/RUN path; RUN/argv/commit/source bindings
    come from supplied supervisor metadata and are cross-checked when available.
    Missing provenance stays null with reasons. Partial supervisor metadata fails.
    Standalone and explicitly softwarecheck-labelled fixture envelopes are always
    development_only, never completed scientific runs. Actual supervisor launch
    authorization/checker results remain separate responsibilities.
    Returns the manifest dictionary. Creation can leave a raw file after an I/O
    failure; it is never removed/reused as if no attempt occurred.
    """
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("artifact directory must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    raw_path, manifest_path = directory/"raw-result.json", directory/"manifest.yaml"
    if raw_path.exists() or manifest_path.exists():
        raise FileExistsError("artifact paths already exist")
    payload = _json_safe(result)
    if not isinstance(payload, dict) or not isinstance(payload.get("parameters"), dict) or "checks" not in payload:
        raise ValueError("result requires parameters object and checks")
    raw_bytes = _json_bytes(payload)
    launch_path, environment_path = directory/"launch.json", directory/"environment.json"
    if launch_path.exists() != environment_path.exists():
        raise ValueError("partial supervisor metadata; require both launch and environment")
    supervised = launch_path.exists()
    launch = _read_object(launch_path) if supervised else {}
    environment = _read_object(environment_path) if supervised else {}
    softwarecheck = bool(launch.get("softwarecheck") or environment.get("softwarecheck")
                         or payload.get("softwarecheck"))
    run_id, experiment_id = launch.get("run_id"), launch.get("experiment_id")
    canonical_directory = directory.parent.name == "runs" and directory.parent.parent.name.startswith("EXP-")
    if canonical_directory:
        path_experiment = directory.parent.parent.name
        if experiment_id is not None and experiment_id != path_experiment:
            raise ValueError("supervisor/path experiment mismatch")
        experiment_id = path_experiment
        if run_id is not None and run_id != directory.name:
            raise ValueError("supervisor/path run mismatch")
    argv = launch.get("argv") if supervised else [sys.executable, *sys.argv]
    if argv is not None and (not isinstance(argv, list) or not argv
                             or not all(isinstance(arg, str) for arg in argv)):
        raise ValueError("supervisor argv must be a nonempty string array")
    commit = environment.get("commit")
    authority = launch.get("authority") or {}
    if authority.get("commit") is not None and commit != authority["commit"]:
        raise ValueError("supervisor authority/environment commit mismatch")
    dirty = environment.get("dirty_tree")
    if dirty is not None and not isinstance(dirty, bool):
        raise ValueError("dirty_tree must be boolean or null")
    source_binding = environment.get("source_sha256")
    canonical_ready = supervised and not softwarecheck and all(
        (run_id, experiment_id, commit, argv, isinstance(source_binding, dict) and bool(source_binding)))
    now_wall, now_cpu = time.monotonic(), time.process_time()
    if (not isinstance(started, str) or not started or now_wall < wall_start or now_cpu < cpu_start):
        raise ValueError("valid actual timing origins required")
    timestamp = datetime.fromisoformat(started.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("started timestamp must include its timezone")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("integer seed required")
    manifest = {"run": {
        "id": run_id, "experiment_id": experiment_id,
        "status": "completed" if canonical_ready else "development_only",
        "development_only": not canonical_ready, "softwarecheck": softwarecheck,
        "provenance_note": "Supervisor metadata observed, not independently authenticated or execution-authorized by this writer.",
        "missing_provenance": [name for name, value in (("run_id", run_id), ("experiment_id", experiment_id),
                               ("commit", commit), ("argv", argv), ("source_binding", source_binding)) if not value],
        "code": {"commit": commit, "command": shlex.join(argv) if argv else None,
                 "argv": argv, "dirty_tree": dirty, "source_binding": source_binding,
                 "dirty_tree_note": "Not sampled by writer; null means supervisor did not supply full tree state.",
                 "provenance": "softwarecheck_supervisor_fixture" if softwarecheck else
                               "supervisor_metadata" if supervised else "standalone_development"},
        "environment": {**environment, "writer_python": sys.version,
                        "writer_platform": platform.platform(), "installed_dependencies": _installed_dependencies()},
        "supervisor": launch if supervised else None,
        "inputs": {"parameters": payload["parameters"], "seeds": [seed],
                   "instance_policy": "public synthetic finite-field curves/subgroups with supplied parameters; no planted ambient lattice orders"},
        "timing": {"started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                   "wall_seconds": now_wall-wall_start, "process_cpu_seconds": now_cpu-cpu_start,
                   "measurement_scope": "driver through result assembly; artifact I/O and checker/supervisor costs separate"},
        "result": {"raw_result": "raw-result.json", "raw_result_sha256": hashlib.sha256(raw_bytes).hexdigest(),
                   "outcome": "observations_only", "checks": payload["checks"],
                   "certificate": {"kind": "none"},
                   "interpretation": "No scientific validation, novelty, speedup or official status promotion."}}}
    manifest_bytes = _json_bytes(manifest)
    for path, contents in ((raw_path, raw_bytes), (manifest_path, manifest_bytes)):
        with path.open("xb") as stream:
            stream.write(contents)
    return manifest


def check_artifacts(directory):
    """Read-only envelope/hash check; no rerun or scientific validation."""
    directory = Path(directory)
    raw = _read_object(directory/"raw-result.json")
    manifest = _read_object(directory/"manifest.yaml")
    run = manifest["run"]
    digest = hashlib.sha256((directory/"raw-result.json").read_bytes()).hexdigest()
    if digest != run["result"]["raw_result_sha256"]:
        raise ValueError("raw result hash mismatch")
    if run["inputs"]["parameters"] != raw["parameters"] or run["result"]["checks"] != raw["checks"]:
        raise ValueError("manifest/result mismatch")
    if run["softwarecheck"] and run["status"] != "development_only":
        raise ValueError("softwarecheck fixture presented as scientific run")
    return {"envelope_valid": True, "scientific_validation": False,
            "development_only": run["development_only"]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check_artifacts(args.check), sort_keys=True))
