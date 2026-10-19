"""Exact, bounded polynomial lattice instrument; importing runs no study.

Public exports are build_shift_lattice, reduce_and_certify, extract_and_verify.
Polynomials in returned dictionaries use [[exponent-list, integer-coefficient],
...] and explicit ordered variable names. All results are JSON-safe.

extract_and_verify context: curve (core Curve), G (actual points), target,
source_equations (Sympy expressions), allowed_base (optional actual points),
coordinate_sources (default each variable; entries are variable indices or
{"constant": x}), and auxiliary_chains (optional list of {A, x_indices,
image_point}; each chain uses y²=x³+A*x, a_next=-4*a and the actual degree-two
map). This verifies auxiliary rational y paths separately from target y signs.
No context accepts a point-log table. root_boxes are explicit integer lists.
Callers bind these boxes to lattice weights by abs(x)<weight_bound. The explicit
dependency gate enables full-precision integer JSON conversion, including exact
derived cap certificates; no arithmetic/row/bit cap is relaxed. CLI --check runs
that gate before parsing integer JSON. Modules and allocator remain shared.

The frozen study is called only by run_experiment/main. Software development
uses p5/p7/p11 and invented polynomials, never the study fixtures.

Programmatic calls are quiet unless passed telemetry=callable or a Telemetry
session; reduction_cell also accepts cell_id for the frozen run-case identity.
The execution CLI emits durable JSONL to its captured stderr, with no separate
telemetry artifact. polynomial_scientific_body finish marks only that function
returning; polynomial_cli finish follows write_artifacts. The writer's existing
whole-run clock includes prior logging but excludes terminal writer/run events
after writing. CLI event spans include prior instrumentation; event timestamps
precede their own persistence, which enclosing clocks pay. The final event's
own persistence has no later enclosing measurement. Cell inclusive_cost and
component/phase clocks include their logging; do not add child clocks.
Logging/serialization and integer bit complexity have no primitive-cost price.
No event releases partial scientific results or attests supervisor validation.
"""
from __future__ import annotations

import argparse
from collections import Counter as Bag
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
from fractions import Fraction
from functools import wraps
import inspect
from itertools import combinations, product
import json
import math
import os
from pathlib import Path
import random
import resource
import sys
import time

try:
    from tools.lattice_ic_core import Counter, Curve, Field, encode_point, is_prime, rank_mod, select_prime_subgroup, write_artifacts
except ModuleNotFoundError:
    from lattice_ic_core import Counter, Curve, Field, encode_point, is_prime, rank_mod, select_prime_subgroup, write_artifacts


STATUSES = ("measured", "zero_yield", "inadmissible", "bounded_instrument_stop", "invalid")
CAPS = {"n": 64, "D": 256, "coefficient_bits": 4096}
FIXTURE = {"curves": [[43, 1, 0], [97, 0, 2], [101, 2, 3]], "windows": [2, 4, 8],
           "oracle_m": [2, 3, 5], "reduction_m": [2, 3], "t": [1, 2], "L": [0, 1],
           "row_rank_cap": 64, "monomial_cap": 256, "coefficient_bit_cap": 4096,
           "target_schedule": "For reduction, canonical nonzero P,2P and first nonzero sum of lex ordered m-tuple of actual window base, deduplicated. Planting labeled separately; full all-target law comes from exhaustive count/DP oracle, never from this subset.",
           "reducer": "fpylll0.6.4 exact integer matrix LLL(delta=0.99,eta=0.51); exact Sympy1.14 HNF/Gram/Groebner and independent certificate checks; missing deps instrument-stop, no silent fallback"}
CONTROL_NAMES = ("dense_same_cap", "same_box_oracle", "random_base", "permuted_coordinates",
                 "generic_group", "planted_vs_uniform", "positive_dimension", "adverse_lifts", "univariate")


class InstrumentStop(RuntimeError):
    pass


class TelemetryIOError(OSError):
    """A telemetry sink failed; execution must stop rather than lose custody."""


class DurableJSONL:
    """Append events to the supplied stream, flushing and fsyncing its real fd.

    No seek, truncate, alternate artifact, or pipe-fsync fallback is permitted.
    The CLI supplies the supervisor-captured stderr stream.
    """
    def __init__(self, stream):
        self.stream = stream

    def __call__(self, event):
        try:
            line = json.dumps(event, sort_keys=True)+"\n"
            if self.stream.write(line) != len(line):
                raise OSError("short telemetry write")
            self.stream.flush()
            os.fsync(self.stream.fileno())
        except Exception as error:
            raise TelemetryIOError("durable telemetry write/flush/fsync failed: "+str(error)) from error


class Telemetry:
    """Optional callable sink, with one monotonic sequence per invocation context.

    Events are operational custody, never partial scientific results. Event
    clocks are sampled before the event's own sink call. Start persistence and
    nested logging are included in elapsed spans; terminal persistence is paid
    by enclosing spans and the cell's inclusive_cost, not its own event clock.
    Primitive counters do not count logging or price integer bit complexity.
    """
    def __init__(self, sink, seed=None):
        self.sink, self.seed, self.sequence = sink, seed, 0

    def emit(self, kind, key, event, wall, cpu, error=None, status=None):
        self.sequence += 1
        now, process = time.monotonic(), time.process_time()
        cell = _telemetry_cell.get()
        path = list(_telemetry_stages.get())
        record = {"schema": "lattice-ic.polynomial-telemetry.v1", "sequence": self.sequence,
                  "pid": os.getpid(), "seed": self.seed, "kind": kind,
                  "cell_id": cell, "stage": key if kind == "stage" else None,
                  "key": "/".join(([cell] if cell else [])+path) if kind == "stage" else key,
                  "stage_path": path,
                  "event": event, "monotonic_seconds": now, "process_cpu_seconds": process,
                  "elapsed_wall_seconds": now-wall, "elapsed_cpu_seconds": process-cpu,
                  "timing_scope": "clocks sampled before own sink; elapsed includes start and nested logging; enclosing spans pay terminal logging; no additive child totals",
                  "unpriced_work": "telemetry has no primitive/bit-cost count; event progress is not scientific yield"}
        if error is not None:
            record["exception"] = {"type": type(error).__name__, "message": str(error)}
        if status is not None:
            record["status"] = status
        try:
            self.sink(record)
        except TelemetryIOError:
            raise
        except Exception as error:
            raise TelemetryIOError("telemetry sink failed: "+str(error)) from error


_telemetry = ContextVar("polynomial_telemetry", default=None)
_telemetry_cell = ContextVar("polynomial_telemetry_cell", default=None)
_telemetry_stages = ContextVar("polynomial_telemetry_stages", default=())


@contextmanager
def _boundary(kind, key):
    telemetry = _telemetry.get()
    if telemetry is None:
        yield
        return
    cell_token = _telemetry_cell.set(key) if kind == "cell" else None
    stage_token = _telemetry_stages.set(_telemetry_stages.get()+(key,)) if kind == "stage" else None
    wall, cpu = time.monotonic(), time.process_time()
    outcome = {}
    try:
        telemetry.emit(kind, key, "start", wall, cpu)
        try:
            yield outcome
        except BaseException as error:
            if not isinstance(error, TelemetryIOError):
                telemetry.emit(kind, key, "exception", wall, cpu, error=error)
            raise
        else:
            telemetry.emit(kind, key, "finish", wall, cpu, status=outcome.get("status"))
    finally:
        if stage_token is not None:
            _telemetry_stages.reset(stage_token)
        if cell_token is not None:
            _telemetry_cell.reset(cell_token)


@contextmanager
def _phase(counter, name):
    # Counter phase time includes both durable boundaries; primitive counts
    # retain their old meaning. The aggregate component timer encloses this.
    with counter.phase(name):
        with _boundary("stage", name):
            yield


def _cell_call(identifier, function, *args, **kwargs):
    token = _telemetry_cell.set(identifier)
    try:
        wall, cpu = time.monotonic(), time.process_time()
        with _boundary("cell", identifier):
            result = function(*args, **kwargs)
        if _telemetry.get() is not None:
            _finish_component_cost(result, wall, cpu)
        return result
    finally:
        _telemetry_cell.reset(token)


def _finish_component_cost(result, wall, cpu):
    cost = (result.get("cost") if isinstance(result, dict) else
            result[-1] if isinstance(result, tuple) and isinstance(result[-1], dict) else None)
    if cost is not None and "wall_seconds" in cost and "cpu_seconds" in cost:
        cost["wall_seconds"], cost["cpu_seconds"] = time.monotonic()-wall, time.process_time()-cpu
        cost["scope"] += "; telemetry boundary persistence included; outer time, do not add phase/child times"


def _instrument(kind, key):
    """Add optional telemetry/cell_id keywords without changing scientific args."""
    def decorate(function):
        signature = inspect.signature(function)
        @wraps(function)
        def instrumented(*args, telemetry=None, cell_id=None, **kwargs):
            if telemetry is None and _telemetry.get() is None:
                return function(*args, **kwargs)
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            session = telemetry if isinstance(telemetry, Telemetry) else (
                Telemetry(telemetry, bound.arguments.get("seed")) if telemetry is not None else _telemetry.get())
            token = _telemetry.set(session)
            identifier = cell_id or (bound.arguments.get("identifier") or key+"/"+json.dumps(bound.arguments, sort_keys=True) if kind == "cell" else key)
            cell_token = _telemetry_cell.set(identifier) if kind == "cell" else None
            wall, cpu = time.monotonic(), time.process_time()
            try:
                with _boundary(kind, identifier) as outcome:
                    result = function(*args, **kwargs)
                    if isinstance(result, dict):
                        outcome["status"] = result.get("status")
                if kind == "cell" and "inclusive_cost" in result:
                    # Include result assembly and successful terminal fsync.
                    result["inclusive_cost"]["wall_seconds"] = time.monotonic()-wall
                    result["inclusive_cost"]["cpu_seconds"] = time.process_time()-cpu
                elif kind == "stage":
                    _finish_component_cost(result, wall, cpu)
                return result
            finally:
                if cell_token is not None:
                    _telemetry_cell.reset(cell_token)
                _telemetry.reset(token)
        return instrumented
    return decorate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dependencies():
    try:
        import sympy as sp
        import fpylll
    except ImportError as error:
        raise InstrumentStop("Required Sympy1.14/fpylll0.6.4 unavailable: "+str(error)) from error
    if sp.__version__ != "1.14.0" or fpylll.__version__ != "0.6.4":
        raise InstrumentStop(f"Required versions Sympy1.14.0/fpylll0.6.4; actual {sp.__version__}/{fpylll.__version__}")
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)  # exact cap/Gram artifacts, not a numerical arithmetic cap
    return sp, fpylll


def rss(scope):
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    require(sys.platform.startswith("linux") or sys.platform == "darwin", "unsupported ru_maxrss units")
    scale = 1 if sys.platform == "darwin" else 1024
    return {"peak_rss_bytes": int(value*scale), "native_peak_rss": value,
            "native_unit": "bytes" if scale == 1 else "KiB", "platform": sys.platform,
            "scope": scope+"; RUSAGE_SELF lifetime high-water, including imports/prior phases, excluding children; not incremental per-arm RSS"}


def _cost(counter, wall, cpu, scope):
    return {"wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu,
            "counter": counter.snapshot(), "resource": rss(scope), "scope": scope,
            "unpriced_work": ["Python allocation/serialization and arithmetic instructions below named calls; no heterogeneous operation total"],
            "cache_policy": "fresh counter/field/curve per scientific cell; algebra components symmetrically clear Sympy expression caches in named timed setup; Sympy/fpylll module imports and process allocator remain shared, with dependency setup paid separately"}


def _reset_symbolic_cache(counter):
    from sympy.core.cache import clear_cache
    clear_cache()
    counter.inc("setup.clear_sympy_expression_cache")


def _pack(poly, variables):
    sp, _ = dependencies()
    p = sp.Poly(poly.as_expr() if isinstance(poly, sp.Poly) else poly, *variables, domain=sp.ZZ)
    return [[list(e), int(c)] for e, c in p.terms() if c]


def _unpack(encoded, variables):
    sp, _ = dependencies()
    return sp.Add(*(sp.Integer(c)*sp.prod(x**int(a) for x, a in zip(variables, e)) for e, c in encoded))


def _symbols(names):
    sp, _ = dependencies()
    return tuple(sp.Symbol(name) for name in names)


def centered_polynomial(expr, variables, p):
    sp, _ = dependencies()
    q = sp.Poly(expr, *variables, modulus=p)
    return sp.Poly.from_dict({e: int(c) if int(c) <= p//2 else int(c)-p for e, c in q.terms()}, variables, domain=sp.ZZ).as_expr()


def s3(x1, x2, x3, A, B):
    return ((x1-x2)**2*x3**2-2*((x1+x2)*(x1*x2+A)+2*B)*x3
            +(x1*x2-A)**2-4*B*(x1+x2))


@_instrument("stage", "summation_polynomial")
def summation_polynomial(m, variables, target_x, A, B, p):
    sp, _ = dependencies()
    require(m in (2, 3) and len(variables) == m, "only expanded m2/m3 instrumented")
    if m == 2:
        expression = s3(*variables, target_x, A, B)
    else:
        T = sp.Dummy("T")
        expression = sp.resultant(s3(variables[0], variables[1], T, A, B),
                                  s3(variables[2], target_x, T, A, B), T)
    return centered_polynomial(expression, variables, p)


def _powers(length, bound):
    return sorted((e for e in product(range(bound+1), repeat=length) if sum(e) <= bound),
                  key=lambda e: (sum(e), e))


def _egcd(a, b):
    aa, bb, x0, x1, y0, y1 = a, b, 1, 0, 0, 1
    while bb:
        q = aa//bb
        aa, bb, x0, x1, y0, y1 = bb, aa-q*bb, x1, x0-q*x1, y1, y0-q*y1
    return (aa, x0, y0) if aa >= 0 else (-aa, -x0, -y0)


def _coordinates(row, basis, rightmost=False):
    value, coefficients = list(row), [0]*len(basis)
    indices = range(len(basis)-1, -1, -1) if rightmost else range(len(basis))
    for i in indices:
        nonzero = [j for j, x in enumerate(basis[i]) if x]
        require(nonzero, "zero row in claimed basis")
        j = nonzero[-1] if rightmost else nonzero[0]
        require(value[j] % basis[i][j] == 0, "noninteger row-lattice membership")
        coefficient = value[j]//basis[i][j]
        coefficients[i] = coefficient
        value = [a-coefficient*b for a, b in zip(value, basis[i])]
    require(not any(value), "row outside integer span")
    return coefficients


def _matmul(A, B):
    if not A:
        return []
    return [[sum(a*b for a, b in zip(row, column)) for column in zip(*B)] for row in A]


@_instrument("stage", "exact_integer_row_hnf")
def _integer_row_hnf(rows, counter):
    """Canonical row HNF with bounded tracking and exact two-way witnesses.

    Positive column contents are removed before arithmetic and restored at the
    end; diagonal column scaling preserves the canonical rightmost-pivot HNF.
    ALL generators are expressed in that basis. An independent subset of these
    coordinates is used only as an auxiliary finite-index sublattice T, never
    as a replacement for the original lattice. If d=abs(det(T)), d*Z^rank is
    contained in T. Cohen's right-to-left HNF operations can therefore track
    coefficients modulo d, then correct their residual using d*T^-1. Tracker
    entries stay in [0,d), instead of growing with successive Euclidean steps.
    This is an exact certificate construction, with no new arithmetic cap.
    """
    sp, _ = dependencies()
    from sympy.matrices.normalforms import hermite_normal_form
    from sympy.polys.matrices import DomainMatrix
    original = [list(row) for row in rows]
    require(original and original[0] and all(len(row) == len(original[0]) for row in original),
            "nonempty rectangular integer generators required")
    require(all(type(x) is int for row in original for x in row), "noninteger generator")
    count, width = len(original), len(original[0])
    contents = [math.gcd(*(row[j] for row in original)) or 1 for j in range(width)]
    normalized = [[x//g for x, g in zip(row, contents)] for row in original]
    counter.inc("hnf.column_content", count*width)
    counter.inc("hnf.sympy_call")
    H0 = [[int(x) for x in row] for row in hermite_normal_form(sp.Matrix(normalized).T).T.tolist()]
    rank = len(H0)
    if not rank:
        require(not any(x for row in original for x in row), "zero HNF mismatch")
        return [], [], [[] for row in original]
    coordinates = [_coordinates(row, H0, rightmost=True) for row in normalized]
    # Fraction-free rank selection is auxiliary ONLY: the subsequent transform
    # still includes every row in coordinates, including dependent generators.
    counter.inc("hnf.auxiliary_fraction_free_selection")
    _, _, selected = DomainMatrix.from_Matrix(sp.Matrix(coordinates).T).rref_den(method="FF")
    require(len(selected) == rank, "auxiliary full-rank sublattice missing")
    T = sp.Matrix([coordinates[i] for i in selected])
    counter.inc("hnf.auxiliary_inverse")
    numerator, denominator = DomainMatrix.from_Matrix(T).inv_den(method="rref")
    denominator = int(denominator)
    d = abs(int(T.det(method="domain-ge")))
    require(d and denominator and d % denominator == 0, "nonintegral auxiliary adjugate")
    correction_basis = [[int(x)*(d//denominator) for x in row] for row in numerator.to_Matrix().tolist()]
    require(_matmul(correction_basis, T.tolist()) == [[d*int(i == j) for j in range(rank)] for i in range(rank)],
            "auxiliary inverse certificate failed")

    coefficients = [[0]*count for _ in range(rank)]
    if d != 1:
        M = [row[:] for row in coordinates]
        tracking = [{i: 1} for i in range(count)]

        def combine(a, u, b, v):
            # Sparse support avoids allocating a dense count-by-count identity.
            result = {}
            for key in u.keys() | v.keys():
                value = (a*u.get(key, 0)+b*v.get(key, 0)) % d
                if value:
                    result[key] = value
            counter.inc("hnf.modular_coefficient", len(u.keys() | v.keys()))
            return result

        k = count
        for column in range(rank-1, -1, -1):
            k -= 1
            for j in range(k-1, -1, -1):
                if not M[j][column]:
                    continue
                a, b = M[k][column], M[j][column]
                g, u, v = _egcd(a, b)
                # The small Bezout choice is essential when a divides b.
                if a and b % a == 0:
                    g, u, v = abs(a), (1 if a > 0 else -1), 0
                R, S, U, V = M[k], M[j], tracking[k], tracking[j]
                M[k] = [u*x+v*y for x, y in zip(R, S)]
                M[j] = [(-b//g)*x+(a//g)*y for x, y in zip(R, S)]
                tracking[k] = combine(u, U, v, V)
                tracking[j] = combine(-b//g, U, a//g, V) if any(M[j]) else {}
                counter.inc("hnf.unimodular_euclid_step")
            pivot = M[k][column]
            if pivot < 0:
                M[k] = [-x for x in M[k]]
                tracking[k] = combine(-1, tracking[k], 0, {})
                pivot = -pivot
            require(pivot, "coordinate lattice lost rank")
            for j in range(k+1, count):
                quotient = M[j][column]//pivot
                if quotient:
                    M[j] = [x-quotient*y for x, y in zip(M[j], M[k])]
                    tracking[j] = combine(1, tracking[j], -quotient, tracking[k])
                    counter.inc("hnf.remainder_row_step")
        identity = [[int(i == j) for j in range(rank)] for i in range(rank)]
        require(M[k:] == identity and all(not any(row) for row in M[:k]),
                "all-generator coordinate lattice is not primitive")
        for i, row in enumerate(tracking[k:]):
            for j, value in row.items():
                coefficients[i][j] = value

    image = _matmul(coefficients, coordinates)
    residual = [[int(i == j)-image[i][j] for j in range(rank)] for i in range(rank)]
    require(all(x % d == 0 for row in residual for x in row), "modular transform residual")
    correction = _matmul([[x//d for x in row] for row in residual], correction_basis)
    for i, row in enumerate(correction):
        for j, value in zip(selected, row):
            coefficients[i][j] += value
    require(_matmul(coefficients, coordinates) == [[int(i == j) for j in range(rank)] for i in range(rank)],
            "exact coordinate retraction failed")
    H = [[x*g for x, g in zip(row, contents)] for row in H0]
    require(_matmul(coefficients, original) == H and _matmul(coordinates, H) == original,
            "two-way HNF membership failed")
    return H, coefficients, coordinates


@_instrument("stage", "gram_determinant")
def _gram_determinant(basis):
    sp, _ = dependencies()
    if len(basis) == len(basis[0]):
        # Canonical row HNF is lower triangular in this square case.
        require(all(basis[i][j] == 0 for i in range(len(basis)) for j in range(i+1, len(basis))), "square HNF shape")
        return math.prod(row[i] for i, row in enumerate(basis))**2
    B = sp.Matrix(basis)
    return int((B*B.T).det(method="domain-ge"))


@_instrument("stage", "build_shift_lattice")
def build_shift_lattice(polynomials, variables, p, weight_bounds, t, L, arm):
    """Build the exact prescribed dense or finite-union sparse weighted Z-lattice."""
    sp, _ = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with _phase(counter, "symbolic_setup"):
        _reset_symbolic_cache(counter)
    variables, weight_bounds = tuple(variables), tuple(weight_bounds)
    require(variables and all(isinstance(x, sp.Symbol) for x in variables) and len({str(x) for x in variables}) == len(variables)
            and len(variables) == len(weight_bounds), "variable/weight shape")
    require(is_prime(p) and all(type(w) is int and w > 0 for w in weight_bounds)
            and type(t) is int and type(L) is int and t >= 0 and L >= 0, "prime modulus/positive weights/nonnegative t,L")
    require(arm in ("dense", "sparse") and polynomials, "unknown/empty shift family")
    require(arm != "sparse" or len(polynomials) == 1, "finite-union sparse arm is single-polynomial only")
    polynomials = [sp.Poly(f.as_expr() if isinstance(f, sp.Poly) else f, *variables, domain=sp.ZZ) for f in polynomials]
    family, target_support = [], set()
    with _phase(counter, "shift_construction"):
        A_L = _powers(len(variables), L)
        if arm == "sparse":
            powers = [polynomials[0]**b for b in range(t+1)]
            for power in powers:
                for e, coefficient in power.terms():
                    if coefficient:
                        target_support.update(tuple(x+y for x, y in zip(e, a)) for a in A_L)
            maxima = [max(e[i] for e in target_support) for i in range(len(variables))]
        for b in _powers(len(polynomials), t):
            polynomial = sp.Poly(1, *variables, domain=sp.ZZ)
            for f, exponent in zip(polynomials, b):
                polynomial *= f**exponent
            support = {e for e, coefficient in polynomial.terms() if coefficient}
            candidates = A_L if arm == "dense" else product(*(range(x+1) for x in maxima))
            for a in candidates:
                counter.inc("shifts.translation_candidate")
                if arm == "sparse" and not all(tuple(x+y for x, y in zip(a, e)) in target_support for e in support):
                    continue
                expression = polynomial.as_expr()*sp.prod(x**e for x, e in zip(variables, a))*p**(t-sum(b))
                packed = _pack(expression, variables)
                family.append({"b": list(b), "a": list(a), "polynomial": packed})
        family.sort(key=lambda row: (-sum(row["b"]), tuple(-x for x in row["b"]), sum(row["a"]), row["a"]))
        support = sorted({tuple(e) for row in family for e, c in row["polynomial"] if c}, key=lambda e: (sum(e), e))
        weights = [math.prod(w**e for w, e in zip(weight_bounds, powers)) for powers in support]
        rows = []
        for row in family:
            values = {tuple(e): c for e, c in row["polynomial"]}
            rows.append([values.get(e, 0)*weight for e, weight in zip(support, weights)])
            counter.inc("shifts.weighted_entry", len(support))
    with _phase(counter, "integer_row_lattice"):
        H, h_from_rows, rows_from_h = _integer_row_hnf(rows, counter)
        counter.inc("lattice.gram_determinant")
        determinant = _gram_determinant(H)
        require(determinant > 0, "nonpositive full-rank Gram determinant")
        candidate_bits = max(abs(x).bit_length() for row in rows for x in row)
        basis_bits = max(abs(x).bit_length() for row in H for x in row)
        bits = max(candidate_bits, basis_bits)
        dimensions = {"candidate_rows": len(rows), "n": len(H), "D": len(support),
                      "coefficient_bits": bits, "candidate_coefficient_bits": candidate_bits, "basis_coefficient_bits": basis_bits}
        stops = [key for key, cap in CAPS.items() if dimensions[key] > cap]
    return {"variables": [str(x) for x in variables], "polynomials": [_pack(f, variables) for f in polynomials],
            "p": p, "weight_bounds": list(weight_bounds), "t": t, "L": L, "arm": arm,
            "target_support_K": [list(e) for e in sorted(target_support)], "shifts": family,
            "support": [list(e) for e in support], "column_weights": weights,
            "weighted_rows": rows, "weighted_basis": H,
            "membership": {"basis_from_rows": h_from_rows, "rows_from_basis": rows_from_h},
            "dimensions": dimensions, "gram_determinant": determinant,
            "covolume": {"square": determinant, "exact_sqrt": str(sp.sqrt(determinant))},
            "caps": dict(CAPS), "cap_exceeded": stops,
            "status": "bounded_instrument_stop" if stops else "measured",
            "cost": _cost(counter, wall, cpu, "shift construction, exact HNF and derived caps, before any LLL")}


def _gs(basis):
    orthogonal, mus, norms = [], [], []
    for i, row in enumerate(basis):
        vector, coefficients = [Fraction(x) for x in row], []
        for j, previous in enumerate(orthogonal):
            mu = sum(Fraction(x)*y for x, y in zip(row, previous))/norms[j]
            coefficients.append(mu)
            vector = [x-mu*y for x, y in zip(vector, previous)]
        norm = sum(x*x for x in vector)
        require(norm > 0, "dependent reduced row")
        orthogonal.append(vector)
        mus.append(coefficients)
        norms.append(norm)
    return mus, norms


def _lll_conditions(basis):
    mus, norms = _gs(basis)
    return all(abs(mu) <= Fraction(51, 100) for row in mus for mu in row) and all(
        norms[i] >= (Fraction(99, 100)-mus[i][i-1]**2)*norms[i-1] for i in range(1, len(basis)))


@_instrument("stage", "reduce_and_certify")
def reduce_and_certify(lattice):
    """Actual fpylll LLL and exact transform/norm/unweight certificates."""
    sp, fpylll = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    if lattice["cap_exceeded"]:
        return {"status": "bounded_instrument_stop", "reason": "derived caps: "+",".join(lattice["cap_exceeded"]),
                "reduced_basis": [], "vectors": [], "certified_equations": [],
                "cost": _cost(counter, wall, cpu, "cap refusal; no LLL attempted")}
    with _phase(counter, "reducer_setup"):
        _reset_symbolic_cache(counter)
    variables = _symbols(lattice["variables"])
    n, D = lattice["dimensions"]["n"], lattice["dimensions"]["D"]
    precision = max(128, 2*lattice["dimensions"]["coefficient_bits"]+64)
    failure = None
    with counter.phase("lll"):
        B = fpylll.IntegerMatrix.from_matrix(lattice["weighted_basis"])
        U = fpylll.IntegerMatrix.identity(n)
        counter.inc("lll.fpylll_call")
        try:
            with _boundary("stage", "lll_call"):
                fpylll.LLL.reduction(B, U=U, delta=0.99, eta=0.51,
                                    method="proved", float_type="mpfr", precision=precision)
        except TelemetryIOError:
            raise
        except Exception as error:
            failure = repr(error)
        if failure is None:
            reduced = [[int(B[i, j]) for j in range(D)] for i in range(n)]
            transform = [[int(U[i, j]) for j in range(n)] for i in range(n)]
    if failure is not None:
        return {"status": "bounded_instrument_stop", "reason": "actual fpylll failure: "+failure,
                "reduced_basis": [], "vectors": [], "certified_equations": [],
                "cost": _cost(counter, wall, cpu, "actual LLL failed; no alternate reducer")}
    with _phase(counter, "exact_reduction_certificates"):
        require(_matmul(transform, lattice["weighted_basis"]) == reduced, "LLL row transform failed")
        determinant = int(sp.Matrix(transform).det())
        require(abs(determinant) == 1 and _lll_conditions(reduced), "LLL exact unimodularity/conditions failed")
        inverse = [[int(x) for x in row] for row in sp.Matrix(transform).inv().tolist()]
        from_rows = _matmul(transform, lattice["membership"]["basis_from_rows"])
        rows_from_reduced = _matmul(lattice["membership"]["rows_from_basis"], inverse)
        vectors, equations = [], []
        for row in reduced:
            require(all(x % w == 0 for x, w in zip(row, lattice["column_weights"])), "nonintegral unweight")
            coefficients = [x//w for x, w in zip(row, lattice["column_weights"])]
            polynomial = [[e, c] for e, c in zip(lattice["support"], coefficients) if c]
            norm_squared = sum(x*x for x in row)
            margin = lattice["p"]**(2*lattice["t"])-D*norm_squared
            vector = {"weighted": row, "polynomial": polynomial, "norm_squared": norm_squared,
                      "strict_margin": margin, "strict": margin > 0}
            vectors.append(vector)
            if margin > 0 and polynomial:
                equations.append(polynomial)
            counter.inc("certificate.vector")
    return {"status": "measured" if equations else "zero_yield", "reduced_basis": reduced,
            "transform": transform, "transform_determinant": determinant,
            "membership": {"reduced_from_rows": from_rows, "rows_from_reduced": rows_from_reduced},
            "vectors": vectors, "certified_equations": equations,
            "parameters": {"delta": [99, 100], "eta": [51, 100], "method": "proved", "float_type": "mpfr", "precision": precision},
            "cost": _cost(counter, wall, cpu, "actual LLL plus exact transform/GS/norm/unweight checking")}


@_instrument("stage", "ideal_certificate")
def ideal_certificate(equations, variables, counter=None):
    """Exact QQ Groebner basis and Krull dimension from its leading ideal."""
    sp, _ = dependencies()
    if counter:
        counter.inc("groebner.call")
    basis = sp.groebner(equations, *variables, order="lex", domain=sp.QQ)
    # Clear rational denominators independently in each displayed basis member.
    packed, leading = [], []
    for polynomial in basis.polys:
        _, integer = polynomial.clear_denoms(convert=True)
        packed.append(_pack(integer, variables))
        leading.append(list(polynomial.monoms()[0]))
    n = len(variables)
    if any(not any(e) for e in leading):
        dimension, cover = -1, None  # unit ideal/empty variety
    else:
        supports = [{i for i, power in enumerate(e) if power} for e in leading]
        cover = next((list(indices) for size in range(n+1)
                      for indices in combinations(range(n), size)
                      if all(set(indices) & support for support in supports)), list(range(n)))
        dimension = n-len(cover)
    return {"basis": packed, "leading_exponents": leading,
            "dimension": dimension, "minimum_variable_cover": cover,
            "zero_dimensional": dimension == 0,
            "criterion": "Krull dimension n minus minimum variable hitting set of leading-monomial supports; unit ideal dimension -1"}


def _triangular_integer_roots(equations, variables, boxes, counter):
    """Exact lex elimination and rational-root factorization, never a box scan."""
    sp, _ = dependencies()
    trace = []
    def visit(current, symbols, current_boxes, assignments):
        counter.inc("extraction.triangular_node")
        if not symbols:
            return [assignments] if all(sp.expand(f) == 0 for f in current) else []
        counter.inc("groebner.call")
        basis = sp.groebner(current, *symbols, order="lex", domain=sp.QQ)
        if any(poly.total_degree() == 0 and poly.as_expr() != 0 for poly in basis.polys):
            return []
        last = symbols[-1]
        univariate = [poly.as_expr() for poly in basis.polys if poly.as_expr().free_symbols <= {last} and poly.as_expr() != 0]
        require(univariate, "zero-dimensional elimination polynomial missing")
        chosen = min(univariate, key=lambda f: sp.degree(f, last))
        _, integer_chosen = sp.Poly(chosen, last, domain=sp.QQ).clear_denoms(convert=True)
        chosen = integer_chosen.as_expr()
        counter.inc("extraction.univariate_factorization")
        roots = sp.polys.polytools.ground_roots(chosen, last)
        integers = sorted(int(root) for root in roots if root.is_Integer)
        allowed = [value for value in integers if value in current_boxes[-1]]
        trace.append({"assignments": [[str(x), value] for x, value in sorted(assignments.items(), key=lambda item: str(item[0]))],
                      "variable": str(last), "polynomial": _pack(chosen, (last,)),
                      "rational_roots": [[str(root), int(multiplicity)] for root, multiplicity in sorted(roots.items(), key=lambda item: str(item[0]))],
                      "integer_roots": integers, "retained_in_box": allowed})
        result = []
        for value in allowed:
            updated = dict(assignments)
            updated[last] = value
            result.extend(visit([sp.expand(poly.as_expr().subs(last, value)) for poly in basis.polys],
                                symbols[:-1], current_boxes[:-1], updated))
        return result
    mappings = visit(equations, tuple(variables), boxes, {})
    roots = sorted(set(tuple(mapping[x] for x in variables) for mapping in mappings))
    return [list(root) for root in roots], trace


def _sum(curve, points):
    total = None
    for point in points:
        total = curve.add(total, point)
    return total


def _decode_point(curve, encoded):
    if encoded is None:
        return None
    point = tuple(curve.field.coerce(x) for x in encoded)
    require(curve.is_on_curve(point) and encode_point(curve, point) == encoded, "bad point encoding")
    return point


def _auxiliary_lifts(root, context, counter):
    curve, all_chains = context["curve"], []
    f = curve.field
    for descriptor in context.get("auxiliary_chains", []):
        indices, a = descriptor["x_indices"], descriptor["A"]
        xs = [f.coerce(root[index]) for index in indices]
        source = Curve(f, a, 0)
        paths = []
        for point in source.points():
            if point is None or point[0] != xs[0]:
                continue
            counter.inc("verification.auxiliary_y_candidate")
            current, coefficients, path, valid = point, a, [point], True
            for expected_x in xs[1:]:
                if current is None or current[0] == f.zero:
                    valid = False
                    break
                x, y = current
                current = (f.add(x, f.mul(coefficients, f.inv(x))),
                           f.mul(y, f.sub(1, f.mul(coefficients, f.inv(f.mul(x, x))))))
                coefficients = -4*coefficients % f.p
                destination = Curve(f, coefficients, 0)
                if current[0] != expected_x or not destination.is_on_curve(current):
                    valid = False
                    break
                path.append(current)
            if valid and encode_point(f, current) == descriptor["image_point"]:
                paths.append([encode_point(f, point) for point in path])
        if not paths:
            return None
        all_chains.append(paths)
    return all_chains


def verify_root(root, variables, boxes, context, counter=None):
    """Original modular equations, actual rational lifts, subgroup and signed sum."""
    sp, _ = dependencies()
    counter = counter if counter is not None else Counter()
    require(len(root) == len(variables) == len(boxes), "root shape")
    if any(value not in box for value, box in zip(root, boxes)):
        return {"root": list(root), "accepted": False, "reason": "outside_integer_box", "witnesses": []}
    substitutions = dict(zip(variables, root))
    curve, target, group = context["curve"], context["target"], set(context["G"])
    p = curve.field.p
    residuals = [int(sp.Poly(expr, *variables).eval(substitutions)) % p for expr in context.get("source_equations", [])]
    counter.inc("verification.modular_equation", len(residuals))
    if any(residuals):
        return {"root": list(root), "accepted": False, "reason": "original_modular_equation", "residuals": residuals, "witnesses": []}
    sources = context.get("coordinate_sources", list(range(len(variables))))
    xs = [root[source] % p if isinstance(source, int) else source["constant"] % p for source in sources]
    rational, subgroup, admitted, allowed = [], [], [], set(context.get("allowed_base", context["G"]))
    for x in xs:
        points = [point for point in curve.points() if point is not None and point[0] == curve.field.coerce(x)]
        rational.append(points)
        subgroup.append([point for point in points if point in group])
        admitted.append([point for point in points if point in group and point in allowed])
        counter.inc("verification.rational_lift_candidate", len(points))
    reason = "no_rational_y" if any(not points for points in rational) else (
        "outside_subgroup" if any(not points for points in subgroup) else (
            "outside_actual_base" if any(not points for points in admitted) else None))
    auxiliary = _auxiliary_lifts(root, context, counter) if reason is None else None
    if reason is None and auxiliary is None:
        reason = "no_auxiliary_rational_chain"
    witnesses = []
    if reason is None:
        for points in product(*admitted):
            counter.inc("verification.sign_tuple")
            if _sum(curve, points) == target:
                witnesses.append({"points": [encode_point(curve, point) for point in points],
                                  "sum": encode_point(curve, target), "auxiliary_paths": auxiliary})
        if not witnesses:
            reason = "wrong_signed_point_sum"
    return {"root": list(root), "accepted": bool(witnesses), "reason": reason,
            "residuals": residuals, "rational_lifts": [[encode_point(curve, point) for point in points] for points in rational],
            "subgroup_lifts": [[encode_point(curve, point) for point in points] for points in subgroup],
            "admitted_lifts": [[encode_point(curve, point) for point in points] for points in admitted], "witnesses": witnesses}


def _clone_context(context, counter):
    source = context["curve"]
    copied = dict(context)
    copied["curve"] = Curve(Field(source.field.p, source.field.quadratic, counter=counter), source.A, source.B)
    return copied


def _context_certificate(context, variables):
    curve = context["curve"]
    return {"p": curve.field.p, "quadratic": None if curve.field.quadratic is None else list(curve.field.quadratic),
            "A": curve.field.encode(curve.A), "B": curve.field.encode(curve.B),
            "G": [encode_point(curve, point) for point in context["G"]],
            "target": encode_point(curve, context["target"]),
            "allowed_base": [encode_point(curve, point) for point in context.get("allowed_base", context["G"])],
            "source_equations": [_pack(f, variables) for f in context.get("source_equations", [])],
            "coordinate_sources": context.get("coordinate_sources", list(range(len(variables)))),
            "auxiliary_chains": context.get("auxiliary_chains", [])}


@_instrument("stage", "extract_and_verify")
def extract_and_verify(equations, variables, root_boxes, verification_context):
    """Zero-dimensional exact integer extraction; original point checks are mandatory.

    Positive-dimensional equations are returned with zero candidate yield. The
    exhaustive box oracle is a distinct exported diagnostic, never a fallback.
    """
    sp, _ = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    variables, boxes = tuple(variables), [list(box) for box in root_boxes]
    require(len(variables) == len(boxes) and all(len(box) == len(set(box)) and all(type(x) is int for x in box) for box in boxes), "explicit duplicate-free integer root boxes required")
    equations = [sp.expand(expr.as_expr() if isinstance(expr, sp.Poly) else expr) for expr in equations]
    with _phase(counter, "verification_setup"):
        _reset_symbolic_cache(counter)
        verification_context = _clone_context(verification_context, counter)
    with _phase(counter, "dimension"):
        ideal = ideal_certificate(equations, variables, counter)
    roots, trace, records = [], [], []
    if ideal["zero_dimensional"]:
        with _phase(counter, "triangular_extraction"):
            roots, trace = _triangular_integer_roots(equations, variables, boxes, counter)
        with _phase(counter, "original_verification"):
            for root in roots:
                require(all(sp.expand(f).subs(dict(zip(variables, root))) == 0 for f in equations), "extracted integer equation residual")
                records.append(verify_root(root, variables, boxes, verification_context, counter))
    valid = sum(record["accepted"] for record in records)
    return {"equations": [_pack(f, variables) for f in equations], "variables": [str(x) for x in variables],
            "verification_context": _context_certificate(verification_context, variables),
            "root_boxes": boxes, "ideal": ideal, "extracted_roots": roots, "triangular_trace": trace,
            "verification": records, "valid_root_count": valid,
            "finite_system_success": ideal["zero_dimensional"] and valid > 0,
            "status": "measured" if valid else "zero_yield",
            "cost": _cost(counter, wall, cpu, "exact dimension/triangular extraction and original modular/lift/sign/subgroup verification; no exhaustive box fallback")}


@_instrument("stage", "exhaustive_box_oracle")
def exhaustive_box_oracle(polynomials, variables, root_boxes, context):
    """Separately charged original modular-root oracle, never candidate extraction."""
    sp, _ = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    boxes, records, tested = [list(box) for box in root_boxes], [], 0
    with _phase(counter, "oracle_setup"):
        _reset_symbolic_cache(counter)
        context = _clone_context(context, counter)
    with _phase(counter, "exhaustive_box_oracle"):
        for root in product(*boxes):
            tested += 1
            counter.inc("oracle.box_candidate")
            if all(int(sp.Poly(f, *variables).eval(dict(zip(variables, root)))) % context["curve"].field.p == 0 for f in polynomials):
                records.append(verify_root(root, variables, boxes, context, counter))
    return {"role": "paid_exhaustive_box_oracle_not_lattice_extraction", "tested": tested,
            "modular_roots": records, "valid_root_count": sum(record["accepted"] for record in records),
            "cost": _cost(counter, wall, cpu, "independent exhaustive original box oracle; excluded from candidate yield")}


@_instrument("stage", "relation_rank")
def relation_rank(curve, base, target, decompositions, P, r):
    """Per-fixed-target marginal rank modulo public ±P only, never verifier logs."""
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    source_curve, base = curve, list(base)
    require(len(set(base)) == len(base) and None not in base, "distinct affine base required")
    def key(point):
        return () if point is None else point
    def representative(point):
        return min((point, curve.neg(point)), key=key)
    def rank(rows):
        counter.inc("rank.call")
        counter.inc("rank.input_entry", sum(len(row) for row in rows))
        return rank_mod(rows, r)
    with _phase(counter, "fixed_target_rank"):
        curve = Curve(Field(source_curve.field.p, source_curve.field.quadratic, counter=counter), source_curve.A, source_curve.B)
        f = curve.field
        raw_variables = list(base)
        if target is not None and target not in raw_variables:
            raw_variables.append(target)
        quotient_variables = sorted(set(representative(point) for point in base), key=key)
        if target is not None and representative(target) not in quotient_variables:
            quotient_variables.append(representative(target))
        raw_rows, rows = [], []
        for points in decompositions:
            require(len(points) > 0 and all(point in base for point in points)
                     and _sum(curve, points) == target, "rank row without actual point identity")
            raw, quotient = [0]*len(raw_variables), [0]*len(quotient_variables)
            for sign, point in [(1, point) for point in points]+([] if target is None else [(-1, target)]):
                raw[raw_variables.index(point)] += sign
                rep = representative(point)
                quotient[quotient_variables.index(rep)] += sign*(1 if point == rep else -1)
            raw_rows.append([x % r for x in raw])
            rows.append([x % r for x in quotient])
        known_points = {None: 0, P: 1, curve.neg(P): -1 % r}
        known_rows, known_witnesses = [], []
        for i, point in enumerate(quotient_variables):
            if point in known_points:
                row = [0]*(len(quotient_variables)+1)
                row[i], row[-1] = 1, -known_points[point] % r
                known_rows.append(row)
                known_witnesses.append({"point": encode_point(f, point), "value": known_points[point],
                                        "basis": "public P or its negation"})
        N = [row+[0] for row in rows]
        K_rank = rank(known_rows)
        all_rows = known_rows+N
        augmented_rank, coefficient_rank = rank(all_rows), rank([row[:-1] for row in all_rows])
        require(augmented_rank == coefficient_rank, "inconsistent affine relation system")
        marginal = augmented_rank-K_rank
        unknown = [i for i, point in enumerate(quotient_variables) if point not in known_points]
        normalized = [[row[i] for i in unknown]+[
            sum(row[i]*known_points[point] for i, point in enumerate(quotient_variables) if point in known_points) % r] for row in rows]
        require(rank(normalized) == marginal, "public normalization rank mismatch")
        formal_raw_rank, formal_quotient_rank = rank(raw_rows), rank(rows)
        target_base_alias = target in base if target is not None else False
        target_quotient_alias = target is not None and representative(target) in {representative(point) for point in base}
    return {"target": encode_point(f, target), "raw_variables": [encode_point(f, point) for point in raw_variables],
            "quotient_variables": [encode_point(f, point) for point in quotient_variables],
            "raw_rows": raw_rows, "quotient_rows": rows, "formal_raw_rank": formal_raw_rank,
            "formal_quotient_rank": formal_quotient_rank, "public_constraints": known_rows,
            "public_known_witnesses": known_witnesses, "known_rank": K_rank,
            "rank_with_known": augmented_rank, "marginal_new_rank": marginal,
            "normalized_rows": normalized, "affine_consistent": True,
            "target_base_alias": target_base_alias,
            "target_quotient_alias": target_quotient_alias,
            "dimensions": {"raw_unknowns": len(raw_variables), "quotient_unknowns": len(quotient_variables), "affine_columns": len(quotient_variables)+1},
            "scope": "one fixed target; public O/±P only; negation certified by point arithmetic; formal ranks are diagnostics; no pooling of target columns",
            "cost": _cost(counter, wall, cpu, "fixed-target exact rank and public-known normalization")}


@_instrument("stage", "group_density")
def group_density(curve, group, base, m):
    """Complete group-sum DP with one reconstructible witness per target."""
    source_curve = curve
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with _phase(counter, "density_setup"):
        curve = Curve(Field(source_curve.field.p, source_curve.field.quadratic, counter=counter), source_curve.A, source_curve.B)
    with _phase(counter, "density_dp_oracle"):
        counts, witnesses = {None: 1}, {None: ()}
        layers = []
        for level in range(m):
            new_counts, new_witnesses = Bag(), {}
            for total in group:
                if total not in counts:
                    continue
                for point in base:
                    counter.inc("oracle.dp_transition")
                    destination = curve.add(total, point)
                    new_counts[destination] += counts[total]
                    new_witnesses.setdefault(destination, witnesses[total]+(point,))
            counts, witnesses = dict(new_counts), new_witnesses
            layers.append([counts.get(point, 0) for point in group])
        histogram = [counts.get(point, 0) for point in group]
        require(sum(histogram) == len(base)**m, "DP first-moment identity")
        encoded = [[encode_point(curve, point) for point in witnesses[target]] if target in witnesses else None for target in group]
    return {"m": m, "M": len(base), "r": len(group), "base": [encode_point(curve, point) for point in base],
            "targets": [encode_point(curve, point) for point in group], "histogram": histogram,
            "layers": layers, "first_moment": {"numerator": len(base)**m, "denominator": len(group)},
            "coverage": sum(value > 0 for value in histogram), "witnesses": encoded,
            "role": "paid_all_target_DP_oracle_not_unknown_scalar_recovery",
            "cost": _cost(counter, wall, cpu, "complete all-target DP oracle")}


def addition_tree(curve, points):
    """Fixed five-leaf split ((1+2)+(3+4))+5, retaining O and heights."""
    require(len(points) == 5, "five actual leaves required")
    nodes = []
    for left, right in ((0, 1), (2, 3), (5, 6), (7, 4)):
        values = list(points)+[node["point"] for node in nodes]
        point = curve.add(values[left], values[right])
        nodes.append({"left": left, "right": right, "point": point})
    p = curve.field.p
    def encode(point):
        if point is None:
            return {"point": None, "branch": "O", "centered_x": None, "abs_centered_x": None}
        x = point[0][0]
        centered = x if x <= p//2 else x-p
        return {"point": encode_point(curve, point), "branch": "affine", "centered_x": centered,
                "abs_centered_x": abs(centered), "coordinate_bit_height": max(abs(centered).bit_length(), point[1][0].bit_length())}
    return {"leaves": [encode(point) for point in points],
            "nodes": [{"left": node["left"], "right": node["right"], **encode(node["point"])} for node in nodes],
            "sum": encode_point(curve, nodes[-1]["point"]),
            "expanded_m5_solver": "outside_initial_instrument; no expanded S6 or lattice extraction performed"}


def _case(identifier, panel, inputs, observables, certificates, work, status="measured", limits=None):
    require(status in STATUSES, "case status outside shared enum")
    return {"id": identifier, "panel": panel, "status": status, "inputs": inputs,
            "observables": observables, "certificates": certificates, "work": work, "limits": limits or []}


@_instrument("stage", "admit")
def _admit(p, A, B):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with _phase(counter, "curve_and_subgroup_admission"):
        curve = Curve(Field(p, counter=counter), A, B)
        admitted = select_prime_subgroup(curve)  # frozen shared min_prime=5, valuation-one
        certificate = {k: v for k, v in admitted.items() if k not in ("P", "G")}
        certificate.update(P=encode_point(curve, admitted["P"]),
                           G=None if admitted["G"] is None else [encode_point(curve, point) for point in admitted["G"]],
                           points=[encode_point(curve, point) for point in curve.points()])
    return curve, admitted, certificate, _cost(counter, wall, cpu, "fresh curve/full point census/largest valuation-one prime subgroup admission")


def _window(admitted, W):
    return sorted(point for point in admitted["G"] if point is not None and 0 <= point[0][0] < W)


@_instrument("stage", "target_schedule")
def _target_schedule(curve, admitted, base, m):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with _phase(counter, "target_schedule"):
        fresh = Curve(Field(curve.field.p, counter=counter), curve.A, curve.B)
        planted = None
        for points in product(base, repeat=m):
            counter.inc("schedule.planted_tuple_attempt")
            total = _sum(fresh, points)
            if total is not None:
                planted = (total, points)
                break
        candidates = [(admitted["P"], "public_P", None),
                      (fresh.mul(2, admitted["P"]), "public_2P", None)]
        if planted:
            candidates.append((planted[0], "planted_first_tuple", planted[1]))
        selected = []
        for target, cohort, points in candidates:
            existing = next((item for item in selected if item["point"] == encode_point(curve, target)), None)
            if existing is None:
                existing = {"point": encode_point(curve, target), "cohorts": [], "planted_witness": None}
                selected.append(existing)
            existing["cohorts"].append(cohort)
            if points:
                existing["planted_witness"] = [encode_point(curve, point) for point in points]
    return {"selected": selected, "planted_available": planted is not None,
            "uniform_law": "complete all-target DP histogram, never inferred from this selected subset",
            "cost": _cost(counter, wall, cpu, "public P/2P plus deterministic first nonzero lex tuple; planting is separate from uniform law")}


@_instrument("cell", "reduction")
def reduction_cell(p, A, B, W, m, target_encoded, t, L, arm, slice_value=None):
    """Fresh cold cell; candidate and oracle components have independent counters."""
    sp, _ = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with _phase(counter, "cold_input_setup"):
        _reset_symbolic_cache(counter)
        curve = Curve(Field(p, counter=counter), A, B)
        admitted = select_prime_subgroup(curve)
        require(admitted["admitted"], "reduction cell requires admitted group")
        base = _window(admitted, W)
        target = _decode_point(curve, target_encoded)
        require(target is not None and target in admitted["G"], "finite subgroup target required")
        variables = tuple(sp.Symbol("x"+str(i+1)) for i in range(m))
        equation = summation_polynomial(m, variables, target[0][0], A, B, p)
        coordinate_sources = list(range(m))
        if slice_value is not None:
            require(m == 2 and slice_value in (0, 1), "fixed x2 slices only")
            equation = centered_polynomial(equation.subs(variables[1], slice_value), variables[:1], p)
            variables = variables[:1]
            coordinate_sources = [0, {"constant": slice_value}]
        context = {"curve": curve, "G": admitted["G"], "target": target, "allowed_base": base,
                   "source_equations": [equation], "coordinate_sources": coordinate_sources}
        source = _context_certificate(context, variables)
    setup_cost = _cost(counter, wall, cpu, "cold admission, actual coordinate base and original S3/resultant polynomial; no inherited curve cache")
    lattice = build_shift_lattice([equation], variables, p, [W]*len(variables), t, L, arm)
    reduced = reduce_and_certify(lattice)
    equations = [_unpack(f, variables) for f in reduced["certified_equations"]]
    boxes = [list(range(W)) for _ in variables]
    extraction = extract_and_verify(equations, variables, boxes, context)
    oracle = exhaustive_box_oracle([equation], variables, boxes, context)
    decompositions = sorted(set(tuple(_decode_point(curve, point) for point in witness["points"])
                               for record in extraction["verification"] for witness in record["witnesses"]))
    with _boundary("stage", "candidate_relation_rank"):
        candidate_rank = relation_rank(curve, base, target, decompositions, admitted["P"], admitted["r"])
    with _boundary("stage", "homogeneous_relation_rank"):
        homogeneous_rank = relation_rank(curve, base, None, [], admitted["P"], admitted["r"])
    univariate = None
    if slice_value is not None:
        direct_counter, direct_wall, direct_cpu = Counter(), time.monotonic(), time.process_time()
        with _phase(direct_counter, "finite_field_factorization"):
            _reset_symbolic_cache(direct_counter)
            finite = sp.Poly(equation, *variables, modulus=p)
            factors = sp.factor_list(finite)
            direct_counter.inc("oracle.finite_field_factorization")
            full_roots = [x for x in range(p) if finite.eval(x) % p == 0]
            direct_counter.inc("oracle.field_root_trial", p)
            encoded_factors = [[_pack(centered_polynomial(poly.as_expr(), variables, p), variables), int(exponent)] for poly, exponent in factors[1]]
        univariate = {"slice_x2": slice_value, "coefficient": int(factors[0]), "factors": encoded_factors,
                      "identically_zero": finite.is_zero, "all_field_roots": full_roots,
                      "roots_in_box": [x for x in full_roots if x < W],
                      "candidate_roots": extraction["extracted_roots"],
                      "cost": _cost(direct_counter, direct_wall, direct_cpu, "separate direct finite-field factorization and complete field-root oracle")}
    return {"source": source, "variables": [str(x) for x in variables], "original_polynomial": _pack(equation, variables),
            "lattice": lattice, "reduction": reduced, "extraction": extraction, "oracle": oracle,
            "candidate_rank": candidate_rank, "homogeneous_candidate_rank": homogeneous_rank,
            "univariate": univariate, "setup_cost": setup_cost,
            "inclusive_cost": {"wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu,
                               "resource": rss("complete cold reduction cell"),
                               "scope": "whole cell inclusive of all candidate/oracle components and witness/report decoding; do not add child times", "unpriced_work": ["post-extraction witness decoding and result assembly have no primitive count"]},
            "work_components": ["setup_cost", "lattice.cost", "reduction.cost", "extraction.cost", "candidate_rank.cost", "homogeneous_candidate_rank.cost"],
            "oracle_components": ["oracle.cost"]+(["univariate.cost"] if univariate else []),
            "scope": "candidate rank uses extracted/certified equations only; O has no polynomial coordinate interface and homogeneous candidate rows are explicitly empty; oracle witnesses/log labels never enter candidate constraints"}


@_instrument("stage", "generic_density")
def _generic_density(curve, group, base, m, seed):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    r, permutation = len(group), list(range(len(group)))
    random.Random(seed).shuffle(permutation)
    inverse = {label: i for i, label in enumerate(permutation)}
    base_labels = [permutation[group.index(point)] for point in base]
    with _phase(counter, "relabeled_generic_dp"):
        counts = {permutation[0]: 1}
        for _ in range(m):
            updated = Bag()
            for label, count in counts.items():
                for other in base_labels:
                    counter.inc("oracle.generic_transition")
                    updated[permutation[(inverse[label]+inverse[other]) % r]] += count
            counts = updated
        histogram = [counts.get(permutation[i], 0) for i in range(r)]
    return {"permutation": permutation, "base_labels": base_labels, "histogram_in_point_order": histogram,
            "operation": "label(add(i,j)) with inverse relabeling; private scalar-index law is an oracle control only",
            "cost": _cost(counter, wall, cpu, "separate generic relabeled cyclic DP oracle; never candidate field arithmetic")}


@_instrument("stage", "coordinate_compatibility")
def _coordinate_compatibility(p, A, B, base_encoded, permutation):
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    tested, failures, identity = 0, [], 0
    with _phase(counter, "coordinate_label_control"):
        curve = Curve(Field(p, counter=counter), A, B)
        base = [_decode_point(curve, point) for point in base_encoded]
        for left, right in product(base, repeat=2):
            total = curve.add(left, right)
            if total is None:
                identity += 1
                continue
            tested += 1
            counter.inc("control.relabeled_s3_trial")
            residual = s3(permutation[left[0][0]], permutation[right[0][0]], permutation[total[0][0]], A, B) % p
            if residual:
                failures.append({"points": [encode_point(curve, left), encode_point(curve, right)],
                                 "target": encode_point(curve, total), "residual": residual})
    return {"coordinate_permutation": permutation, "affine_trials": tested,
            "identity_target_branches": identity, "failures": failures,
            "cost": _cost(counter, wall, cpu, "actual S3/group compatibility under permuted coordinate labels")}


@_instrument("stage", "positive_dimension_control")
def _positive_dimension_control(p):
    sp, _ = dependencies()
    x, y = sp.symbols("x y")
    lattice = build_shift_lattice([x-y], (x, y), p, (2, 2), 1, 1, "dense")
    reduced = reduce_and_certify(lattice)
    equations = [x-y, x*(x-y)]
    rows, coefficients = [], []
    for equation in equations:
        packed = dict((tuple(e), c) for e, c in _pack(equation, (x, y)))
        row = [packed.get(tuple(e), 0)*w for e, w in zip(lattice["support"], lattice["column_weights"])]
        rows.append(row)
        coefficients.append(_coordinates(row, lattice["weighted_basis"], rightmost=True))
    gram = sp.Matrix(rows)
    ideal = ideal_certificate(equations, (x, y))
    require(int(gram.rank()) == 2 and ideal["dimension"] == 1, "false-sufficiency control invalid")
    return {"lattice": lattice, "reduction": reduced, "equations": [_pack(equation, (x, y)) for equation in equations],
            "constructed_control_vectors": rows, "membership_in_basis": coefficients,
            "coefficient_rank": 2, "strict_margins": [p*p-len(lattice["support"])*sum(x*x for x in row) for row in rows],
            "ideal": ideal, "finite_system_success": False,
            "scope": "constructed lattice members, independently short/coefficient-independent but positive dimensional; not promoted to extracted equations"}


@_instrument("stage", "adverse_lifts")
def _adverse_lifts(p, A, B, P_encoded, G_encoded):
    sp, _ = dependencies()
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    repeated, outside = [], []
    with _phase(counter, "adverse_modular_lift_oracle"):
        _reset_symbolic_cache(counter)
        curve = Curve(Field(p, counter=counter), A, B)
        group = [_decode_point(curve, point) for point in G_encoded]
        P = _decode_point(curve, P_encoded)
        t, T = sp.symbols("t T")
        for target in group:
            if target is None:
                continue
            X = target[0][0]
            # S4(t,t,X,X) is an actual resultant, with every degenerate branch retained.
            polynomial = centered_polynomial(sp.resultant(s3(t, t, T, A, B), s3(X, X, T, A, B), T), (t,), p)
            for x in range(p):
                counter.inc("control.repeated_coordinate_trial")
                rhs = (x*x*x+A*x+B) % p
                residual = int(polynomial.subs(t, x)) % p
                if rhs and pow(rhs, (p-1)//2, p) == p-1 and residual == 0:
                    repeated.append({"target": encode_point(curve, target), "x": x, "rhs": rhs,
                                     "polynomial": _pack(polynomial, (t,)), "residual": residual})
        for x1, x2 in product(range(p), repeat=2):
            counter.inc("control.outside_group_trial")
            residual = s3(x1, x2, P[0][0], A, B) % p
            if residual:
                continue
            lifts = [[point for point in curve.points() if point is not None and point[0] == (x,)] for x in (x1, x2)]
            valid = [(left, right) for left, right in product(*lifts) if curve.add(left, right) == P]
            bad = [(left, right) for left, right in valid if left not in group or right not in group]
            if bad:
                outside.append({"x": [x1, x2], "residual": residual,
                                "outside_G_witnesses": [[encode_point(curve, left), encode_point(curve, right)] for left, right in bad]})
    return {"repeated_nonrational_roots": repeated, "outside_G_roots": outside,
            "scope": "only actual zero modular residuals reported; absence is bounded zero coverage, never an invented adverse witness",
            "cost": _cost(counter, wall, cpu, "full-field repeated-coordinate and rational outside-G adverse oracles")}


def _cell_status(cell):
    if cell["lattice"]["status"] == "bounded_instrument_stop" or cell["reduction"]["status"] == "bounded_instrument_stop":
        return "bounded_instrument_stop"
    return "measured" if cell["extraction"]["finite_system_success"] and cell["candidate_rank"]["marginal_new_rank"] else "zero_yield"


def _cell_observables(cell):
    return {"dimensions": cell["lattice"]["dimensions"], "strict_vectors": len(cell["reduction"]["certified_equations"]),
            "ideal_dimension": cell["extraction"]["ideal"]["dimension"], "valid_extracted_roots": cell["extraction"]["valid_root_count"],
            "formal_quotient_rank": cell["candidate_rank"]["formal_quotient_rank"],
            "marginal_new_rank": cell["candidate_rank"]["marginal_new_rank"],
            "oracle_valid_roots": cell["oracle"]["valid_root_count"],
            "oracle_point_witness_count": sum(len(record["witnesses"]) for record in cell["oracle"]["modular_roots"]),
            "finite_system_success": cell["extraction"]["finite_system_success"]}


def _control_references(cases):
    refs = {name: [] for name in CONTROL_NAMES}
    for case in cases:
        panel, inputs, identifier = case["panel"], case["inputs"], case["id"]
        if panel == "reduction":
            refs["same_box_oracle"].append(identifier)
            if inputs["arm"] == "dense":
                refs["dense_same_cap"].append(identifier)
        if panel == "univariate":
            refs["univariate"].append(identifier)
        if panel == "density" and inputs["base_kind"] == "random":
            refs["random_base"].append(identifier)
        if panel == "coordinate_control" or (panel == "density" and inputs["base_kind"] == "permuted"):
            refs["permuted_coordinates"].append(identifier)
        for match, control in (("generic", "generic_group"), ("cohorts", "planted_vs_uniform"),
                               ("positive_dimension", "positive_dimension"), ("adverse_lifts", "adverse_lifts")):
            if panel == match:
                refs[control].append(identifier)
    return refs


@_instrument("cell", "inadmissible")
def _inadmissible(identifier, panel, inputs, reason):
    return _case(identifier, panel, inputs, {"admitted": False, "reason": reason},
                 {"unexecuted_dependency": "admission/p"+str(inputs["p"])},
                 {"dependency": "admission/p"+str(inputs["p"]), "local_work": "not executed"},
                 status="inadmissible", limits=["Dependent cell unavailable under frozen min_prime=5/valuation-one rule; no substitute subgroup."])


@_instrument("run", "polynomial_scientific_body")
def run_experiment(seed=1729):
    """All frozen panels; this function is never invoked by software tests."""
    dep_wall, dep_cpu = time.monotonic(), time.process_time()
    with _boundary("stage", "dependency_setup"):
        sp, fpylll = dependencies()
    dependency_cost = {"wall_seconds": time.monotonic()-dep_wall, "cpu_seconds": time.process_time()-dep_cpu,
                       "versions": {"sympy": sp.__version__, "fpylll": fpylll.__version__, "python": sys.version},
                       "integer_serialization": "full precision; Python decimal digit guard disabled for exact cap/Gram certificates; arithmetic instrument caps unchanged",
                       "scope": "shared actual dependency import/version gate; charge once per cold run, never a fallback"}
    cases = []
    for p, A, B in FIXTURE["curves"]:
        curve, admitted, admission, work = _cell_call(f"admission/p{p}", _admit, p, A, B)
        cases.append(_case(f"admission/p{p}", "admission", {"p": p, "A": A, "B": B},
                           {"admitted": admitted["admitted"], "r": admitted["r"], "order": admitted["order"]},
                           admission, work, status="measured" if admitted["admitted"] else "inadmissible",
                           limits=[] if admitted["admitted"] else [admitted["reason"]]))
        for W in FIXTURE["windows"]:
            if admitted["admitted"]:
                actual = _window(admitted, W)
                rng = random.Random(f"{seed}:{p}:{W}:random-base")
                random_base = sorted(rng.sample([point for point in admitted["G"] if point is not None], len(actual)))
                permutation = list(range(p))
                random.Random(f"{seed}:{p}:{W}:coordinate-labels").shuffle(permutation)
                permuted = sorted(point for point in admitted["G"] if point is not None and permutation[point[0][0]] < W)
                bases = {"actual": actual, "random": random_base, "permuted": permuted}
            densities = {}
            for kind in ("actual", "random", "permuted"):
                for m in FIXTURE["oracle_m"]:
                    identifier, inputs = f"density/p{p}/W{W}/{kind}/m{m}", {"p": p, "A": A, "B": B, "W": W, "m": m, "base_kind": kind}
                    if not admitted["admitted"]:
                        cases.append(_inadmissible(identifier, "density", inputs, admitted["reason"]))
                        continue
                    density = _cell_call(identifier, group_density, curve, admitted["G"], bases[kind], m)
                    densities[kind, m] = density
                    cases.append(_case(identifier, "density", inputs,
                                       {"M": density["M"], "W": W, "coverage": density["coverage"], "first_moment": density["first_moment"]},
                                       density, {"components": ["certificates.cost"], "cold_dependencies": ["dependencies", f"admission/p{p}"]},
                                       status="measured" if density["coverage"] else "zero_yield"))
                tree_id, tree_inputs = f"tree/p{p}/W{W}/{kind}", {"p": p, "A": A, "B": B, "W": W, "base_kind": kind}
                if not admitted["admitted"]:
                    cases.append(_inadmissible(tree_id, "m5_tree", tree_inputs, admitted["reason"]))
                else:
                    tree_counter, tree_wall, tree_cpu = Counter(), time.monotonic(), time.process_time()
                    with _boundary("cell", tree_id), _phase(tree_counter, "fixed_m5_tree"):
                        fresh = Curve(Field(p, counter=tree_counter), A, B)
                        trees = []
                        for target, points in zip(densities[kind, 5]["targets"], densities[kind, 5]["witnesses"]):
                            if points is not None:
                                tree = addition_tree(fresh, [_decode_point(fresh, point) for point in points])
                                require(tree["sum"] == target, "m5 tree witness mismatch")
                                trees.append({"target": target, "tree": tree})
                    cases.append(_case(tree_id, "m5_tree", tree_inputs, {"witnessed_targets": len(trees)},
                                       {"trees": trees, "expanded_m5_solver": "outside_initial_instrument"},
                                       {"local": _cost(tree_counter, tree_wall, tree_cpu, "all covered-target fixed m5 trees and coordinate heights"),
                                        "dependency": f"density/p{p}/W{W}/{kind}/m5"},
                                       status="measured" if trees else "zero_yield",
                                       limits=["No expanded S6, m5 lattice reduction or root-solver coverage claimed."]))
            for m in FIXTURE["oracle_m"]:
                identifier, inputs = f"generic/p{p}/W{W}/m{m}", {"p": p, "A": A, "B": B, "W": W, "m": m}
                if not admitted["admitted"]:
                    cases.append(_inadmissible(identifier, "generic", inputs, admitted["reason"]))
                else:
                    generic = _cell_call(identifier, _generic_density, curve, admitted["G"], actual, m, f"{seed}:{p}:{W}:{m}:generic")
                    require(generic["histogram_in_point_order"] == densities["actual", m]["histogram"], "generic DP mismatch")
                    cases.append(_case(identifier, "generic", inputs, {"same_point_histogram": True}, generic,
                                       {"components": ["certificates.cost"], "dependency": f"admission/p{p}"}))
            identifier, inputs = f"coordinate/p{p}/W{W}", {"p": p, "A": A, "B": B, "W": W}
            if not admitted["admitted"]:
                cases.append(_inadmissible(identifier, "coordinate_control", inputs, admitted["reason"]))
            else:
                labels = _cell_call(identifier, _coordinate_compatibility, p, A, B, [encode_point(curve, point) for point in actual], permutation)
                cases.append(_case(identifier, "coordinate_control", inputs,
                                   {"affine_trials": labels["affine_trials"], "failures": len(labels["failures"])}, labels,
                                   {"components": ["certificates.cost"]}))
            for m in FIXTURE["reduction_m"]:
                schedule_id, inputs = f"schedule/p{p}/W{W}/m{m}", {"p": p, "A": A, "B": B, "W": W, "m": m}
                cohort_id = f"cohorts/p{p}/W{W}/m{m}"
                if not admitted["admitted"]:
                    cases.append(_inadmissible(schedule_id, "schedule", inputs, admitted["reason"]))
                    cases.append(_inadmissible(cohort_id, "cohorts", inputs, admitted["reason"]))
                    selected = [{"point": None, "cohorts": [name]} for name in ("public_P", "public_2P", "planted_first_tuple")]
                else:
                    schedule = _cell_call(schedule_id, _target_schedule, curve, admitted, actual, m)
                    selected = schedule["selected"]
                    cases.append(_case(schedule_id, "schedule", inputs, {"selected_targets": len(selected), "planted_available": schedule["planted_available"]},
                                       schedule, {"components": ["certificates.cost"], "dependency": f"admission/p{p}"}))
                    with _boundary("cell", cohort_id):
                        density = densities["actual", m]
                        cohort_data = [{"point": item["point"], "cohorts": item["cohorts"],
                                        "ordered_tuple_count": density["histogram"][density["targets"].index(item["point"])]} for item in selected]
                        cases.append(_case(cohort_id, "cohorts", inputs, {"uniform_first_moment": density["first_moment"]},
                                           {"selected": cohort_data, "uniform_histogram": density["histogram"], "scope": "selected/planted cohort is not a uniform-target estimate"},
                                           {"paid_dependencies": [schedule_id, f"density/p{p}/W{W}/actual/m{m}"], "local": "report assembly only"}))
                for j, selected_target in enumerate(selected):
                    for t, L, arm in product(FIXTURE["t"], FIXTURE["L"], ("dense", "sparse")):
                        root_id = f"reduction/p{p}/W{W}/m{m}/R{j}/t{t}/L{L}/{arm}"
                        for slice_value in ([None, 0, 1] if m == 2 else [None]):
                            identifier = root_id if slice_value is None else root_id+f"/x2={slice_value}"
                            panel = "reduction" if slice_value is None else "univariate"
                            cell_inputs = {**inputs, "target_index": j, "target": selected_target["point"], "t": t, "L": L,
                                           "arm": arm, "slice_x2": slice_value}
                            if not admitted["admitted"]:
                                cases.append(_inadmissible(identifier, panel, cell_inputs, admitted["reason"]))
                                continue
                            cell = reduction_cell(p, A, B, W, m, selected_target["point"], t, L, arm, slice_value, cell_id=identifier)
                            observations = _cell_observables(cell)
                            if slice_value is None:
                                truth_count = densities["actual", m]["histogram"][densities["actual", m]["targets"].index(selected_target["point"])]
                                require(observations["oracle_point_witness_count"] == truth_count, "same-box oracle/DP witness-count mismatch")
                            limits = ["Only certified zero-dimensional extracted equations can score candidate yield; oracle roots are separate."]
                            if cell["lattice"]["cap_exceeded"]:
                                limits.append("Derived instrument cap: "+",".join(cell["lattice"]["cap_exceeded"]))
                            cases.append(_case(identifier, panel, cell_inputs, observations, cell,
                                               {"candidate_components": cell["work_components"], "oracle_components": cell["oracle_components"],
                                                "cold_dependencies": ["dependencies"], "comparison": "fresh cold cell for each arm/t/L; no shared warm curve cache; no summed heterogeneous work or speedup claim"},
                                               status=_cell_status(cell), limits=limits))
        for panel in ("positive_dimension", "adverse_lifts"):
            identifier, inputs = f"{panel}/p{p}", {"p": p, "A": A, "B": B}
            if not admitted["admitted"]:
                cases.append(_inadmissible(identifier, panel, inputs, admitted["reason"]))
            elif panel == "positive_dimension":
                control_wall, control_cpu = time.monotonic(), time.process_time()
                control = _cell_call(identifier, _positive_dimension_control, p)
                cases.append(_case(identifier, panel, inputs, {"coefficient_rank": 2, "ideal_dimension": 1, "finite_system_success": False}, control,
                                   {"wall_seconds": time.monotonic()-control_wall, "cpu_seconds": time.process_time()-control_cpu,
                                    "components": ["certificates.lattice.cost", "certificates.reduction.cost"],
                                    "scope": "outer time inclusive, do not add child times; extra exact constructed-row/rank/Groebner work included"}, status="zero_yield"))
            else:
                control = _cell_call(identifier, _adverse_lifts, p, A, B, admission["P"], admission["G"])
                cases.append(_case(identifier, panel, inputs,
                                   {"nonrational_repeated_roots": len(control["repeated_nonrational_roots"]), "outside_G_roots": len(control["outside_G_roots"])},
                                   control, {"components": ["certificates.cost"]}))
    with _boundary("cell", "controls"):
        references = _control_references(cases)
        cases.append(_case("controls", "controls", {}, {"required_controls": list(CONTROL_NAMES)}, references,
                           {"scope": "references to paid cells; no free extra scientific computation"}))
    return {"schema_version": 1, "direction": "polynomial", "seed": seed, "parameters": FIXTURE,
            "cases": cases, "checks": {"internal_assertions": "not independent review"},
            "limitations": ["Tiny bounded synthetic scope; no complexity or ECDLP speedup claim.",
                            "m5 has all-target density and fixed split trees only; expanded S6/lattice solver outside initial instrument.",
                            "Sparse arm is finite support union, not convex Newton polytope.",
                            "Public-known rank uses only O/±P; no DP or planted verifier log constraints.",
                            "Dependency/cap/reducer failure is an instrument limit, never a negative mathematical conclusion."],
            "work_accounting": {"dependency_setup": dependency_cost, "resource": rss("trial through scientific cells before serialization"),
                                "convention": "Fresh scientific cells and independent candidate/oracle counters. Primitive layers overlap; counts have no aggregate unit. Sequential components may be inspected separately; outer inclusive times must not be added to child times. Each cold route pays dependency setup plus its named admission/source setup and components. All-target DP, exhaustive boxes, direct finite-field roots, generic controls and target planting are paid oracles, excluded from candidate recovery and rank.",
                                "unpriced_work": ["Python report assembly/serialization", "separate --check replay, reported with its own wall/CPU and lifetime RSS"]},
            "instrument_scope": {"protocol": "prospective-protocols.json/polynomial", "controls": list(CONTROL_NAMES),
                                 "expanded_reduction_m": [2, 3], "density_m": [2, 3, 5], "expanded_m5": False,
                                 "scientific_claim": False, "checker_is_independent_review": False}}


def _check_rss(record):
    platform = record["platform"]
    require(platform.startswith("linux") or platform == "darwin", "unknown RSS unit platform")
    scale = 1 if platform == "darwin" else 1024
    require(type(record["peak_rss_bytes"]) is int and type(record["native_peak_rss"]) is int
            and record["native_unit"] == ("bytes" if scale == 1 else "KiB")
            and record["peak_rss_bytes"] == int(record["native_peak_rss"]*scale)
            and record["peak_rss_bytes"] > 0 and "lifetime high-water" in record["scope"], "bad RSS units/value/scope")


def _check_cost(cost):
    require(cost["wall_seconds"] >= 0 and cost["cpu_seconds"] >= 0 and cost["scope"] and cost["unpriced_work"] and cost["cache_policy"], "missing cost scope")
    _check_rss(cost["resource"])
    counter = cost["counter"]
    require(all(type(value) is int and value >= 0 for value in counter["operations"].values()), "bad primitive counts")
    allocations = Bag()
    for phase in counter["phases"].values():
        require(phase["calls"] > 0 and phase["wall_seconds"] >= 0 and phase["cpu_seconds"] >= 0, "bad phase timing")
        require(all(type(value) is int and value >= 0 for value in phase["operations"].values()), "bad phase counts")
        allocations.update(phase["operations"])
    require(all(value <= counter["operations"].get(key, -1) for key, value in allocations.items()), "double allocated operation counts")
    # This instrument uses sequential phases within each returned component.
    require(sum(phase["wall_seconds"] for phase in counter["phases"].values()) <= cost["wall_seconds"]
            and sum(phase["cpu_seconds"] for phase in counter["phases"].values()) <= cost["cpu_seconds"], "overlapping/invented sequential phase times")


def _integers(matrix):
    return isinstance(matrix, list) and all(isinstance(row, list) and all(type(x) is int for x in row) for row in matrix)


def check_lattice(lattice):
    """Verify complete shift schedule and two-way integer row-lattice equality."""
    sp, _ = dependencies()
    variables = _symbols(lattice["variables"])
    polynomials = [_unpack(f, variables) for f in lattice["polynomials"]]
    p, t, L, arm = (lattice[key] for key in ("p", "t", "L", "arm"))
    require(is_prime(p) and type(t) is int and type(L) is int and t >= 0 and L >= 0, "wrong modulus/shift indices")
    require(arm in ("dense", "sparse") and (arm != "sparse" or len(polynomials) == 1), "wrong shift arm")
    require(len(variables) == len(lattice["weight_bounds"]) and all(type(w) is int and w > 0 for w in lattice["weight_bounds"]), "wrong weights")
    A_L, K = _powers(len(variables), L), set()
    if arm == "sparse":
        for b in range(t+1):
            support = [e for e, c in sp.Poly(polynomials[0]**b, *variables).terms() if c]
            K.update(tuple(x+y for x, y in zip(e, a)) for e in support for a in A_L)
        maxima = [max(e[i] for e in K) for i in range(len(variables))]
    require(lattice["target_support_K"] == [list(e) for e in sorted(K)], "wrong finite support union")
    shifts = []
    for b in _powers(len(polynomials), t):
        product_polynomial = sp.prod(f**power for f, power in zip(polynomials, b))
        support = [e for e, c in sp.Poly(product_polynomial, *variables).terms() if c]
        for a in (A_L if arm == "dense" else product(*(range(x+1) for x in maxima))):
            if arm == "sparse" and any(tuple(x+y for x, y in zip(a, e)) not in K for e in support):
                continue
            shifts.append({"b": list(b), "a": list(a), "polynomial": _pack(product_polynomial*sp.prod(x**e for x, e in zip(variables, a))*p**(t-sum(b)), variables)})
    shifts.sort(key=lambda row: (-sum(row["b"]), tuple(-x for x in row["b"]), sum(row["a"]), row["a"]))
    require(shifts == lattice["shifts"], "deleted/altered shift generator")
    support = sorted({tuple(e) for row in shifts for e, c in row["polynomial"] if c}, key=lambda e: (sum(e), e))
    weights = [math.prod(w**e for w, e in zip(lattice["weight_bounds"], powers)) for powers in support]
    rows = [[dict((tuple(e), c) for e, c in shift["polynomial"]).get(e, 0)*weight for e, weight in zip(support, weights)] for shift in shifts]
    require(lattice["support"] == [list(e) for e in support] and lattice["column_weights"] == weights
            and lattice["weighted_rows"] == rows, "wrong weighted coefficient matrix")
    H, membership = lattice["weighted_basis"], lattice["membership"]
    require(_integers(H) and H and all(len(row) == len(support) for row in H)
            and _integers(membership["basis_from_rows"]) and _integers(membership["rows_from_basis"]), "noninteger/ragged HNF membership")
    require(len(membership["basis_from_rows"]) == len(H) and all(len(row) == len(rows) for row in membership["basis_from_rows"])
            and len(membership["rows_from_basis"]) == len(rows) and all(len(row) == len(H) for row in membership["rows_from_basis"]), "HNF membership dimensions")
    require(_matmul(membership["basis_from_rows"], rows) == H and _matmul(membership["rows_from_basis"], H) == rows, "integer row lattice not preserved in both directions")
    pivots = [max(j for j, value in enumerate(row) if value) for row in H]
    require(pivots == sorted(set(pivots)) and all(H[i][j] > 0 and all(0 <= H[k][j] < H[i][j] for k in range(i+1, len(H))) for i, j in enumerate(pivots)), "noncanonical row HNF")
    determinant = _gram_determinant(H)
    require(determinant > 0 and lattice["gram_determinant"] == determinant
            and lattice["covolume"] == {"square": determinant, "exact_sqrt": str(sp.sqrt(determinant))}, "false Gram/covolume")
    candidate_bits, basis_bits = max(abs(x).bit_length() for row in rows for x in row), max(abs(x).bit_length() for row in H for x in row)
    dimensions = {"candidate_rows": len(rows), "n": len(H), "D": len(support), "coefficient_bits": max(candidate_bits, basis_bits),
                  "candidate_coefficient_bits": candidate_bits, "basis_coefficient_bits": basis_bits}
    stops = [key for key, cap in CAPS.items() if dimensions[key] > cap]
    require(lattice["dimensions"] == dimensions and lattice["caps"] == CAPS and lattice["cap_exceeded"] == stops
            and lattice["status"] == ("bounded_instrument_stop" if stops else "measured"), "false derived cap classification")
    _check_cost(lattice["cost"])
    counts = lattice["cost"]["counter"]["operations"]
    trials = len(_powers(len(polynomials), t))*(len(A_L) if arm == "dense" else math.prod(x+1 for x in maxima))
    require(counts.get("shifts.translation_candidate") == trials and counts.get("shifts.weighted_entry") == len(rows)*len(support)
            and counts.get("hnf.sympy_call") == counts.get("lattice.gram_determinant") == 1
            and counts.get("setup.clear_sympy_expression_cache") == 1, "unpaid shift/HNF/Gram/setup work")
    return True


def check_reduction(lattice, reduced):
    """Verify exact LLL membership/conditions/norms; never rerun LLL."""
    sp, _ = dependencies()
    _check_cost(reduced["cost"])
    if reduced["status"] == "bounded_instrument_stop":
        require(reduced["reduced_basis"] == reduced["vectors"] == reduced["certified_equations"] == [], "false outputs after instrument stop")
        if lattice["cap_exceeded"]:
            require(reduced["reason"] == "derived caps: "+",".join(lattice["cap_exceeded"])
                    and not reduced["cost"]["counter"]["operations"], "LLL charged after cap refusal")
        else:
            require(reduced["reason"].startswith("actual fpylll failure:")
                    and reduced["cost"]["counter"]["operations"].get("lll.fpylll_call") == 1, "unsupported reducer stop")
        return True
    require(not lattice["cap_exceeded"], "reduction accepted inadmissible capped lattice")
    n, D = lattice["dimensions"]["n"], lattice["dimensions"]["D"]
    U, B = reduced["transform"], reduced["reduced_basis"]
    require(_integers(U) and len(U) == n and all(len(row) == n for row in U)
            and _integers(B) and len(B) == n and all(len(row) == D for row in B), "bad LLL matrix shape")
    require(_matmul(U, lattice["weighted_basis"]) == B and abs(int(sp.Matrix(U).det())) == 1
            and reduced["transform_determinant"] == int(sp.Matrix(U).det()) and _lll_conditions(B), "false exact LLL certificate")
    membership = reduced["membership"]
    require(_integers(membership["reduced_from_rows"]) and _integers(membership["rows_from_reduced"])
            and len(membership["reduced_from_rows"]) == n and all(len(row) == len(lattice["weighted_rows"]) for row in membership["reduced_from_rows"])
            and len(membership["rows_from_reduced"]) == len(lattice["weighted_rows"]) and all(len(row) == n for row in membership["rows_from_reduced"])
            and _matmul(membership["reduced_from_rows"], lattice["weighted_rows"]) == B
            and _matmul(membership["rows_from_reduced"], B) == lattice["weighted_rows"], "LLL two-way integer membership failed")
    expected_vectors = []
    for row in B:
        require(all(x % weight == 0 for x, weight in zip(row, lattice["column_weights"])), "noninteger unweight")
        polynomial = [[e, x//weight] for e, x, weight in zip(lattice["support"], row, lattice["column_weights"]) if x]
        norm = sum(x*x for x in row)
        margin = lattice["p"]**(2*lattice["t"])-D*norm
        expected_vectors.append({"weighted": row, "polynomial": polynomial, "norm_squared": norm, "strict_margin": margin, "strict": margin > 0})
    equations = [vector["polynomial"] for vector in expected_vectors if vector["strict"] and vector["polynomial"]]
    require(reduced["vectors"] == expected_vectors and reduced["certified_equations"] == equations
            and reduced["status"] == ("measured" if equations else "zero_yield"), "false strict norm/unweight certificate")
    require(reduced["parameters"] == {"delta": [99, 100], "eta": [51, 100], "method": "proved", "float_type": "mpfr", "precision": max(128, 2*lattice["dimensions"]["coefficient_bits"]+64)}, "wrong reducer parameters")
    counts = reduced["cost"]["counter"]["operations"]
    require(counts.get("lll.fpylll_call") == 1 and counts.get("certificate.vector") == n
            and counts.get("setup.clear_sympy_expression_cache") == 1, "unpaid actual LLL/vector/setup work")
    return True


def check_extraction(extracted, equations, variables, root_boxes, context):
    sp, _ = dependencies()
    boxes = [list(box) for box in root_boxes]
    require(extracted["variables"] == [str(x) for x in variables] and extracted["root_boxes"] == boxes
            and extracted["equations"] == [_pack(f, variables) for f in equations]
            and extracted["verification_context"] == _context_certificate(context, variables), "altered extraction inputs")
    ideal = ideal_certificate(equations, variables)
    require(extracted["ideal"] == ideal, "false ideal dimension/basis")
    roots, trace = _triangular_integer_roots(equations, variables, boxes, Counter()) if ideal["zero_dimensional"] else ([], [])
    require(extracted["extracted_roots"] == roots and extracted["triangular_trace"] == trace, "incomplete/false triangular integer roots")
    records = [verify_root(root, variables, boxes, context) for root in roots]
    for root in roots:
        require(all(sp.expand(equation).subs(dict(zip(variables, root))) == 0 for equation in equations), "nonzero extracted equation")
    count = sum(record["accepted"] for record in records)
    require(extracted["verification"] == records and extracted["valid_root_count"] == count
            and extracted["finite_system_success"] == (ideal["zero_dimensional"] and count > 0)
            and extracted["status"] == ("measured" if count else "zero_yield"), "false lift/sign/subgroup/sum acceptance")
    _check_cost(extracted["cost"])
    counts = extracted["cost"]["counter"]["operations"]
    require(counts.get("extraction.univariate_factorization", 0) == len(trace)
            and counts.get("setup.clear_sympy_expression_cache") == 1
            and counts.get("verification.modular_equation", 0) == len(roots)*len(context.get("source_equations", [])), "unpaid extraction/verification work")
    return True


def _semantic(value):
    if isinstance(value, dict):
        return {key: _semantic(item) for key, item in value.items() if key not in ("cost", "setup_cost", "inclusive_cost")}
    if isinstance(value, list):
        return [_semantic(item) for item in value]
    return value


def check_cell(cell, inputs):
    sp, _ = dependencies()
    p, A, B, W, m, t, L, arm = (inputs[key] for key in ("p", "A", "B", "W", "m", "t", "L", "arm"))
    curve = Curve(Field(p), A, B)
    admitted = select_prime_subgroup(curve)
    require(admitted["admitted"], "unadmitted cell")
    base, target = _window(admitted, W), _decode_point(curve, inputs["target"])
    require(target is not None and target in admitted["G"], "false finite G target")
    variables = tuple(sp.Symbol("x"+str(i+1)) for i in range(m))
    polynomial = summation_polynomial(m, variables, target[0][0], A, B, p)
    sources, slice_value = list(range(m)), inputs["slice_x2"]
    if slice_value is not None:
        require(m == 2 and slice_value in (0, 1), "wrong univariate slice")
        polynomial = centered_polynomial(polynomial.subs(variables[1], slice_value), variables[:1], p)
        variables, sources = variables[:1], [0, {"constant": slice_value}]
    context = {"curve": curve, "G": admitted["G"], "target": target, "allowed_base": base,
               "source_equations": [polynomial], "coordinate_sources": sources}
    require(cell["source"] == _context_certificate(context, variables) and cell["variables"] == [str(x) for x in variables]
            and cell["original_polynomial"] == _pack(polynomial, variables), "wrong source curve/polynomial/base/target")
    lattice = cell["lattice"]
    require(lattice["polynomials"] == [_pack(polynomial, variables)] and lattice["p"] == p
            and lattice["variables"] == [str(x) for x in variables] and lattice["weight_bounds"] == [W]*len(variables)
            and lattice["t"] == t and lattice["L"] == L and lattice["arm"] == arm, "lattice not bound to cell")
    check_lattice(lattice)
    check_reduction(lattice, cell["reduction"])
    equations = [_unpack(f, variables) for f in cell["reduction"]["certified_equations"]]
    boxes = [list(range(W)) for _ in variables]
    require(all(abs(x) < W for box in boxes for x in box), "root box violates strict weight bound")
    check_extraction(cell["extraction"], equations, variables, boxes, context)
    oracle = exhaustive_box_oracle([polynomial], variables, boxes, context)
    require(_semantic(cell["oracle"]) == _semantic(oracle), "altered exhaustive modular/lift oracle")
    _check_cost(cell["oracle"]["cost"])
    require(cell["oracle"]["cost"]["counter"]["operations"].get("oracle.box_candidate") == W**len(variables), "unpaid box oracle")
    decompositions = sorted(set(tuple(_decode_point(curve, point) for point in witness["points"])
                               for record in cell["extraction"]["verification"] for witness in record["witnesses"]))
    for key, fixed_target, rows in (("candidate_rank", target, decompositions), ("homogeneous_candidate_rank", None, [])):
        expected = relation_rank(curve, base, fixed_target, rows, admitted["P"], admitted["r"])
        require(_semantic(cell[key]) == _semantic(expected), "false fixed-target/public-known marginal rank")
        _check_cost(cell[key]["cost"])
    if slice_value is None:
        require(cell["univariate"] is None, "unexpected slice solver")
    else:
        direct = cell["univariate"]
        finite = sp.Poly(polynomial, *variables, modulus=p)
        factor_coefficient, factors = sp.factor_list(finite)
        expected_factors = [[_pack(centered_polynomial(f.as_expr(), variables, p), variables), int(exponent)] for f, exponent in factors]
        roots = [x for x in range(p) if finite.eval(x) % p == 0]
        require(direct["slice_x2"] == slice_value and direct["coefficient"] == int(factor_coefficient)
                and direct["factors"] == expected_factors and direct["identically_zero"] == finite.is_zero
                and direct["all_field_roots"] == roots and direct["roots_in_box"] == [x for x in roots if x < W]
                and direct["candidate_roots"] == cell["extraction"]["extracted_roots"], "false direct finite-field root comparison")
        _check_cost(direct["cost"])
    _check_cost(cell["setup_cost"])
    require(cell["inclusive_cost"]["wall_seconds"] >= cell["setup_cost"]["wall_seconds"]
            and cell["inclusive_cost"]["cpu_seconds"] >= cell["setup_cost"]["cpu_seconds"], "bad inclusive cold cell timing")
    _check_rss(cell["inclusive_cost"]["resource"])
    require(cell["work_components"] == ["setup_cost", "lattice.cost", "reduction.cost", "extraction.cost", "candidate_rank.cost", "homogeneous_candidate_rank.cost"]
            and cell["oracle_components"] == ["oracle.cost"]+(["univariate.cost"] if slice_value is not None else []), "deleted candidate/oracle cost components")
    return True


def _expected_specs(admitted_by_p, schedules):
    specs = {}
    def add(identifier, panel, inputs):
        specs[identifier] = (panel, inputs)
    for p, A, B in FIXTURE["curves"]:
        add(f"admission/p{p}", "admission", {"p": p, "A": A, "B": B})
        for W in FIXTURE["windows"]:
            for kind in ("actual", "random", "permuted"):
                for m in FIXTURE["oracle_m"]:
                    add(f"density/p{p}/W{W}/{kind}/m{m}", "density", {"p": p, "A": A, "B": B, "W": W, "m": m, "base_kind": kind})
                add(f"tree/p{p}/W{W}/{kind}", "m5_tree", {"p": p, "A": A, "B": B, "W": W, "base_kind": kind})
            for m in FIXTURE["oracle_m"]:
                add(f"generic/p{p}/W{W}/m{m}", "generic", {"p": p, "A": A, "B": B, "W": W, "m": m})
            add(f"coordinate/p{p}/W{W}", "coordinate_control", {"p": p, "A": A, "B": B, "W": W})
            for m in FIXTURE["reduction_m"]:
                inputs = {"p": p, "A": A, "B": B, "W": W, "m": m}
                add(f"schedule/p{p}/W{W}/m{m}", "schedule", inputs)
                add(f"cohorts/p{p}/W{W}/m{m}", "cohorts", inputs)
                selected = schedules[p, W, m]["selected"] if admitted_by_p[p][1]["admitted"] else [{"point": None}]*3
                for j, target in enumerate(selected):
                    for t, L, arm in product(FIXTURE["t"], FIXTURE["L"], ("dense", "sparse")):
                        root_id = f"reduction/p{p}/W{W}/m{m}/R{j}/t{t}/L{L}/{arm}"
                        for slice_value in ([None, 0, 1] if m == 2 else [None]):
                            identifier = root_id if slice_value is None else root_id+f"/x2={slice_value}"
                            panel = "reduction" if slice_value is None else "univariate"
                            add(identifier, panel, {**inputs, "target_index": j, "target": target["point"],
                                                    "t": t, "L": L, "arm": arm, "slice_x2": slice_value})
        for panel in ("positive_dimension", "adverse_lifts"):
            add(f"{panel}/p{p}", panel, {"p": p, "A": A, "B": B})
    add("controls", "controls", {})
    return specs


def check_result(result):
    """Exact frozen coverage and mathematical certificates; does not rerun LLL."""
    require(result["schema_version"] == 1 and result["direction"] == "polynomial" and result["parameters"] == FIXTURE, "wrong schema/source fixture")
    require(result["instrument_scope"] == {"protocol": "prospective-protocols.json/polynomial", "controls": list(CONTROL_NAMES),
             "expanded_reduction_m": [2, 3], "density_m": [2, 3, 5], "expanded_m5": False,
             "scientific_claim": False, "checker_is_independent_review": False}, "altered instrument scope")
    case_map = {}
    for case in result["cases"]:
        require(set(("id", "panel", "status", "inputs", "observables", "certificates", "work", "limits")) <= set(case)
                and case["status"] in STATUSES and case["id"] not in case_map, "case schema/status/duplicate ID")
        case_map[case["id"]] = case
    require("controls" in case_map and set(case_map["controls"]["certificates"]) == set(CONTROL_NAMES), "deleted controls")
    sp, _ = dependencies()
    admitted_by_p, schedules = {}, {}
    for p, A, B in FIXTURE["curves"]:
        require(f"admission/p{p}" in case_map, "deleted curve admission")
        curve, admitted, certificate, _ = _admit(p, A, B)
        # Independent literal equation census, not core's square-to-y table.
        independent = [None]+[[[x], [y]] for x in range(p) for y in range(p) if (y*y-x*x*x-A*x-B) % p == 0]
        require(certificate["points"] == independent, "independent full curve enumeration mismatch")
        actual = case_map[f"admission/p{p}"]
        require(actual["certificates"] == certificate and actual["observables"] == {"admitted": admitted["admitted"], "r": admitted["r"], "order": admitted["order"]}
                and actual["status"] == ("measured" if admitted["admitted"] else "inadmissible"), "false subgroup admission/count")
        _check_cost(actual["work"])
        admitted_by_p[p] = (curve, admitted)
        if admitted["admitted"]:
            for W, m in product(FIXTURE["windows"], FIXTURE["reduction_m"]):
                schedules[p, W, m] = _target_schedule(curve, admitted, _window(admitted, W), m)
    specs = _expected_specs(admitted_by_p, schedules)
    require(list(case_map) == list(specs), "deleted/extra/reordered planned cells, including inadmissible dependencies")
    densities = {}
    for identifier, (panel, inputs) in specs.items():
        case = case_map[identifier]
        require(case["panel"] == panel and case["inputs"] == inputs, "altered case parameters")
        if panel in ("admission", "controls"):
            continue
        p, A, B = inputs["p"], inputs["A"], inputs["B"]
        curve, admitted = admitted_by_p[p]
        if not admitted["admitted"]:
            require(case == _inadmissible(identifier, panel, inputs, admitted["reason"]), "missing/false inadmissible dependent cell")
            continue
        require(case["status"] != "inadmissible", "admitted panel silently omitted")
        W = inputs.get("W")
        actual_base = _window(admitted, W) if W is not None else None
        permutation = list(range(p))
        if W is not None:
            random.Random(f"{result['seed']}:{p}:{W}:coordinate-labels").shuffle(permutation)
        if panel == "density":
            kind, m = inputs["base_kind"], inputs["m"]
            if kind == "actual":
                base = actual_base
            elif kind == "random":
                base = sorted(random.Random(f"{result['seed']}:{p}:{W}:random-base").sample([point for point in admitted["G"] if point is not None], len(actual_base)))
            else:
                base = sorted(point for point in admitted["G"] if point is not None and permutation[point[0][0]] < W)
            expected = group_density(curve, admitted["G"], base, m)
            density = case["certificates"]
            require(_semantic(density) == _semantic(expected), "false/incomplete all-target density law")
            _check_cost(density["cost"])
            require(density["cost"]["counter"]["operations"] == expected["cost"]["counter"]["operations"], "unpaid DP work")
            for target_encoded, count, witness in zip(density["targets"], density["histogram"], density["witnesses"]):
                require((witness is not None) == (count > 0), "DP witness coverage")
                if witness is not None:
                    points = [_decode_point(curve, point) for point in witness]
                    require(len(points) == m and all(point in base for point in points)
                            and encode_point(curve, _sum(curve, points)) == target_encoded, "DP point witness failed")
            require(case["observables"] == {"M": len(base), "W": W, "coverage": expected["coverage"], "first_moment": expected["first_moment"]}
                    and case["status"] == ("measured" if expected["coverage"] else "zero_yield"), "false density summary")
            densities[p, W, kind, m] = density
        elif panel == "m5_tree":
            density = densities[p, W, inputs["base_kind"], 5]
            trees = [{"target": target, "tree": addition_tree(curve, [_decode_point(curve, point) for point in points])}
                     for target, points in zip(density["targets"], density["witnesses"]) if points is not None]
            require(case["certificates"] == {"trees": trees, "expanded_m5_solver": "outside_initial_instrument"}
                    and case["observables"] == {"witnessed_targets": len(trees)}
                    and case["status"] == ("measured" if trees else "zero_yield"), "false m5 tree/height or expanded solver claim")
            _check_cost(case["work"]["local"])
            require(case["work"]["local"]["counter"]["operations"].get("curve.add", 0) == 4*len(trees), "unpaid m5 tree additions")
        elif panel == "generic":
            m = inputs["m"]
            expected = _generic_density(curve, admitted["G"], actual_base, m, f"{result['seed']}:{p}:{W}:{m}:generic")
            require(_semantic(case["certificates"]) == _semantic(expected)
                    and expected["histogram_in_point_order"] == densities[p, W, "actual", m]["histogram"]
                    and case["observables"] == {"same_point_histogram": True} and case["status"] == "measured", "false generic relabeling control")
            _check_cost(case["certificates"]["cost"])
        elif panel == "coordinate_control":
            expected = _coordinate_compatibility(p, A, B, [encode_point(curve, point) for point in actual_base], permutation)
            require(_semantic(case["certificates"]) == _semantic(expected)
                    and case["observables"] == {"affine_trials": expected["affine_trials"], "failures": len(expected["failures"])}
                    and case["status"] == "measured", "false coordinate-label compatibility control")
            _check_cost(case["certificates"]["cost"])
        elif panel == "schedule":
            expected = schedules[p, W, inputs["m"]]
            require(_semantic(case["certificates"]) == _semantic(expected)
                    and case["observables"] == {"selected_targets": len(expected["selected"]), "planted_available": expected["planted_available"]}
                    and case["status"] == "measured", "postselected/altered reduction targets")
            _check_cost(case["certificates"]["cost"])
        elif panel == "cohorts":
            m = inputs["m"]
            density = densities[p, W, "actual", m]
            expected = [{"point": item["point"], "cohorts": item["cohorts"], "ordered_tuple_count": density["histogram"][density["targets"].index(item["point"])]}
                        for item in schedules[p, W, m]["selected"]]
            require(case["certificates"] == {"selected": expected, "uniform_histogram": density["histogram"], "scope": "selected/planted cohort is not a uniform-target estimate"}
                    and case["observables"] == {"uniform_first_moment": density["first_moment"]}
                    and case["status"] == "measured", "planted cohort confused with uniform law")
        elif panel in ("reduction", "univariate"):
            cell = case["certificates"]
            check_cell(cell, inputs)
            require(case["observables"] == _cell_observables(cell) and case["status"] == _cell_status(cell), "false cell yield/status")
            limits = ["Only certified zero-dimensional extracted equations can score candidate yield; oracle roots are separate."]
            if cell["lattice"]["cap_exceeded"]:
                limits.append("Derived instrument cap: "+",".join(cell["lattice"]["cap_exceeded"]))
            require(case["limits"] == limits, "omitted cell limitation")
            if panel == "reduction":
                density = densities[p, W, "actual", inputs["m"]]
                count = density["histogram"][density["targets"].index(inputs["target"])]
                require(case["observables"]["oracle_point_witness_count"] == count, "DP/exact same-base oracle mismatch")
            require(case["work"]["candidate_components"] == cell["work_components"]
                    and case["work"]["oracle_components"] == cell["oracle_components"], "candidate/oracle costs merged or omitted")
        elif panel == "positive_dimension":
            control = case["certificates"]
            check_lattice(control["lattice"])
            check_reduction(control["lattice"], control["reduction"])
            x, y = sp.symbols("x y")
            equations = [x-y, x*(x-y)]
            require(control["equations"] == [_pack(f, (x, y)) for f in equations]
                    and control["lattice"]["polynomials"] == [_pack(x-y, (x, y))]
                    and control["lattice"]["p"] == p and control["lattice"]["weight_bounds"] == [2, 2], "wrong false-sufficiency inputs")
            rows = control["constructed_control_vectors"]
            require(_matmul(control["membership_in_basis"], control["lattice"]["weighted_basis"]) == rows
                    and int(sp.Matrix(rows).rank()) == control["coefficient_rank"] == 2, "false constructed vector independence/membership")
            weights, support = control["lattice"]["column_weights"], control["lattice"]["support"]
            for row, equation in zip(rows, equations):
                require(all(x % w == 0 for x, w in zip(row, weights))
                        and sp.expand(_unpack([[e, x//w] for e, x, w in zip(support, row, weights) if x], (x, y))-equation) == 0, "false control polynomial unweight")
            margins = [p*p-len(support)*sum(x*x for x in row) for row in rows]
            require(control["strict_margins"] == margins and all(margin > 0 for margin in margins)
                    and control["ideal"] == ideal_certificate(equations, (x, y)) and control["ideal"]["dimension"] == 1
                    and control["finite_system_success"] is False
                    and case["observables"] == {"coefficient_rank": 2, "ideal_dimension": 1, "finite_system_success": False}
                    and case["status"] == "zero_yield", "positive dimension falsely sufficient")
        elif panel == "adverse_lifts":
            expected = _adverse_lifts(p, A, B, encode_point(curve, admitted["P"]), [encode_point(curve, point) for point in admitted["G"]])
            control = case["certificates"]
            require(_semantic(control) == _semantic(expected) and case["observables"] == {
                "nonrational_repeated_roots": len(expected["repeated_nonrational_roots"]), "outside_G_roots": len(expected["outside_G_roots"])}
                and case["status"] == "measured", "false adverse modular/lift witness coverage")
            t = sp.Symbol("t")
            for witness in control["repeated_nonrational_roots"]:
                rhs = (witness["x"]**3+A*witness["x"]+B) % p
                require(rhs == witness["rhs"] and rhs and pow(rhs, (p-1)//2, p) == p-1
                        and int(_unpack(witness["polynomial"], (t,)).subs(t, witness["x"])) % p == 0, "adverse nonroot or rational lift")
            for witness in control["outside_G_roots"]:
                for points in witness["outside_G_witnesses"]:
                    left, right = [_decode_point(curve, point) for point in points]
                    require(curve.add(left, right) == admitted["P"] and (left not in admitted["G"] or right not in admitted["G"]), "false outside-G witness")
            _check_cost(control["cost"])
        else:
            raise ValueError("unimplemented required checker panel "+panel)
    require(case_map["controls"]["certificates"] == _control_references(result["cases"][:-1])
            and all(case_map["controls"]["certificates"][name] for name in CONTROL_NAMES)
            and case_map["controls"]["observables"] == {"required_controls": list(CONTROL_NAMES)}
            and case_map["controls"]["status"] == "measured", "deleted/misbound required controls")
    work = result["work_accounting"]
    _check_rss(work["resource"])
    require(work["convention"] and work["unpriced_work"] and result["limitations"] and result["checks"], "missing truthful accounting/scope")
    dep = work["dependency_setup"]
    require(dep["versions"]["sympy"] == "1.14.0" and dep["versions"]["fpylll"] == "0.6.4"
            and dep["versions"]["python"] and dep["wall_seconds"] >= 0 and dep["cpu_seconds"] >= 0
            and dep["integer_serialization"] == "full precision; Python decimal digit guard disabled for exact cap/Gram certificates; arithmetic instrument caps unchanged", "wrong/unpriced runtime dependencies")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if args.check:
        require(args.output_dir is None, "--check cannot write outputs")
        wall, cpu = time.monotonic(), time.process_time()
        dependencies()  # configure exact integer parsing before loading certificates
        check_result(json.loads(args.check.read_text()))
        print(json.dumps({"certificate_valid": True, "independent_review": False,
                          "checker_wall_seconds": time.monotonic()-wall, "checker_cpu_seconds": time.process_time()-cpu,
                          "resource": rss("separate native certificate checker"), "lll_rerun": False}, sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir required for execution")
    started, wall, cpu = datetime.now(timezone.utc).isoformat(), time.monotonic(), time.process_time()
    token = _telemetry.set(Telemetry(DurableJSONL(sys.stderr), seed=args.seed))
    try:
        with _boundary("run", "polynomial_cli"):
            result = run_experiment(args.seed)
            with _boundary("stage", "write_artifacts"):
                write_artifacts(result, args.output_dir, args.seed, started, wall, cpu)
    finally:
        _telemetry.reset(token)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TelemetryIOError as error:
        print("infrastructure_error: "+str(error), file=sys.stderr)
        raise SystemExit(3)
    except InstrumentStop as error:
        print("bounded_instrument_stop: "+str(error), file=sys.stderr)
        raise SystemExit(2)
    except (ValueError, KeyError, TypeError, ArithmeticError) as error:
        print("invalid polynomial instrument/certificate: "+str(error), file=sys.stderr)
        raise SystemExit(1)
