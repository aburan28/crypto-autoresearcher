"""Matched-control factor-base discovery instrumentation for toy ECDLP research.

This module deliberately separates three questions that are easy to conflate:

1. how a factor base is constructed;
2. whether an EC point decomposition actually exists over that base; and
3. how expensive the existing Semaev/Groebner path is on the same base.

The exact m=2 oracle below is independent of ``harness.semaev``.  It performs
elliptic-curve group arithmetic, handles both signs of every lifted x-coordinate,
and emits an independently verifiable certificate.  Groebner results are then
compared against that oracle rather than treated as ground truth.

Everything in this file is toy-scale instrumentation.  In particular,
``full_curve`` factor bases are useful for geometry/solver measurements but are
not automatically valid logarithm systems for the target prime-order subgroup.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Iterable, Iterator

import sympy

from . import semaev
from .toycurve import ECDLPInstance, EllipticCurve, Point, _seed_int


SUPPORTED_FAMILIES = {
    "interval",
    "centered_interval",
    "qr_window",
    "multiplicative_coset",
    "sparse_polynomial_predicate",
    "random_matched",
}


@dataclass(frozen=True)
class FactorBaseSpec:
    """Declarative, hashable-enough description of a factor-base family."""

    family: str
    requested_size: int
    seed: int = 0
    scope: str = "full_curve"
    params: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.family not in SUPPORTED_FAMILIES:
            raise ValueError(f"unsupported factor-base family: {self.family}")
        if self.requested_size < 0:
            raise ValueError("requested_size must be non-negative")
        if self.scope not in {"full_curve", "target_subgroup"}:
            raise ValueError(f"unsupported factor-base scope: {self.scope}")


@dataclass(frozen=True)
class BuiltFactorBase:
    spec: FactorBaseSpec
    xs: tuple[int, ...]
    construction_seconds: float
    candidates_examined: int
    liftable_candidates: int
    factor_base_hash: str

    @property
    def realized_size(self) -> int:
        return len(self.xs)

    @property
    def lift_fraction(self) -> float:
        if self.candidates_examined == 0:
            return 0.0
        return self.liftable_candidates / self.candidates_examined


@dataclass(frozen=True)
class TwoSumResult:
    found: bool
    multiplicity: int
    oracle_seconds: float
    summand_x: tuple[int, int] | None = None
    certificate: dict | None = None


@dataclass(frozen=True)
class CandidateMeasurement:
    family: str
    scope: str
    requested_size: int
    realized_size: int
    factor_base_hash: str
    construction_seconds: float
    lift_fraction: float
    targets: int
    decomposable_targets: int
    decomposition_yield: float
    mean_multiplicity: float
    oracle_seconds: float
    relation_rank: int
    solver_targets: int = 0
    solver_successes: int = 0
    solver_recall: float | None = None
    groebner_seconds: float = 0.0
    groebner_basis_size_mean: float | None = None
    groebner_basis_max_degree_mean: float | None = None


@dataclass(frozen=True)
class MatchedComparison:
    structured: CandidateMeasurement
    random_control: CandidateMeasurement

    @property
    def yield_ratio(self) -> float | None:
        denom = self.random_control.decomposition_yield
        return None if denom == 0 else self.structured.decomposition_yield / denom


def _factor_base_digest(spec: FactorBaseSpec, xs: Iterable[int]) -> str:
    payload = {
        "family": spec.family,
        "requested_size": spec.requested_size,
        "seed": spec.seed,
        "scope": spec.scope,
        "params": dict(sorted(spec.params.items())),
        "xs": list(xs),
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _centered_stream(p: int) -> Iterator[int]:
    yield 0
    for k in range(1, p):
        yield k
        if p - k != k:
            yield p - k


def _multiplicative_coset_stream(p: int, size: int, seed: int) -> Iterator[int]:
    """Yield one deterministic multiplicative coset with enough raw elements.

    We choose the smallest divisor of p-1 that is at least 2*size.  The factor
    of two is only a construction heuristic because roughly half of arbitrary
    x-values lift on a typical curve.  If no proper divisor is large enough,
    the full multiplicative group is a valid control family instance.
    """
    if p <= 3:
        return
    need = max(1, 2 * size)
    divisors = sorted(int(d) for d in sympy.divisors(p - 1) if int(d) >= need)
    order = divisors[0] if divisors else p - 1
    g = int(sympy.primitive_root(p))
    h = pow(g, (p - 1) // order, p)
    shift = _seed_int(seed, "fb-coset-shift") % (p - 1)
    a = pow(g, shift, p)
    seen: set[int] = set()
    x = a
    for _ in range(order):
        if x not in seen:
            seen.add(x)
            yield x
        x = (x * h) % p


def _candidate_stream(inst: ECDLPInstance, spec: FactorBaseSpec) -> Iterator[int]:
    p = inst.p
    family = spec.family
    if family == "interval":
        start = spec.params.get("start", 0) % p
        for i in range(p):
            yield (start + i) % p
        return
    if family == "centered_interval":
        yield from _centered_stream(p)
        return
    if family == "qr_window":
        start = spec.params.get("start", 0) % p
        for i in range(p):
            x = (start + i) % p
            if x == 0 or pow(x, (p - 1) // 2, p) == 1:
                yield x
        return
    if family == "sparse_polynomial_predicate":
        # h(x)=x^2+x+c is deliberately low degree and sparse.  The predicate
        # selects x for which h(x) is 0 or a quadratic residue.
        c = spec.params.get("c", 1) % p
        start = spec.params.get("start", 0) % p
        for i in range(p):
            x = (start + i) % p
            h = (x * x + x + c) % p
            if h == 0 or pow(h, (p - 1) // 2, p) == 1:
                yield x
        return
    if family == "multiplicative_coset":
        yield from _multiplicative_coset_stream(p, spec.requested_size, spec.seed)
        return
    if family == "random_matched":
        # A deterministic pseudorandom permutation is unnecessary at toy
        # scale; hash-derived candidates plus de-duplication are sufficient.
        for j in range(max(p * 2, spec.requested_size * 100 + 1000)):
            yield _seed_int(spec.seed, f"fb-random-{j}") % p
        return
    raise AssertionError(f"unreachable family: {family}")


def _eligible_lift(E: EllipticCurve, inst: ECDLPInstance, x: int, scope: str) -> Point:
    P = E.lift_x(x)
    if P is None:
        return None
    if scope == "target_subgroup" and E.mul(inst.n, P) is not None:
        return None
    return P


def build_factor_base(inst: ECDLPInstance, spec: FactorBaseSpec) -> BuiltFactorBase:
    """Construct exactly ``requested_size`` distinct eligible x-coordinates."""
    if spec.requested_size == 0:
        return BuiltFactorBase(spec, (), 0.0, 0, 0, _factor_base_digest(spec, ()))
    if spec.scope == "target_subgroup":
        maximum_size = (inst.n - 1) // 2
        if spec.requested_size > maximum_size:
            raise ValueError(
                f"target_subgroup requested size {spec.requested_size} exceeds "
                f"the x-coordinate maximum {maximum_size}"
            )

    E = inst.curve()
    t0 = time.perf_counter()
    xs: list[int] = []
    seen: set[int] = set()
    examined = 0
    liftable = 0
    for raw_x in _candidate_stream(inst, spec):
        x = int(raw_x) % inst.p
        if x in seen:
            continue
        seen.add(x)
        examined += 1
        if _eligible_lift(E, inst, x, spec.scope) is None:
            continue
        liftable += 1
        xs.append(x)
        if len(xs) == spec.requested_size:
            break

    elapsed = time.perf_counter() - t0
    if len(xs) != spec.requested_size:
        raise ValueError(
            f"factor-base shortfall for {spec.family}: requested "
            f"{spec.requested_size}, realized {len(xs)} after {examined} candidates"
        )
    tup = tuple(xs)
    return BuiltFactorBase(
        spec=spec,
        xs=tup,
        construction_seconds=elapsed,
        candidates_examined=examined,
        liftable_candidates=liftable,
        factor_base_hash=_factor_base_digest(spec, tup),
    )


def matched_random_control(inst: ECDLPInstance, base: BuiltFactorBase, *, seed: int) -> BuiltFactorBase:
    """Construct a random control with exactly the structured base's realized size."""
    spec = FactorBaseSpec(
        family="random_matched",
        requested_size=base.realized_size,
        seed=seed,
        scope=base.spec.scope,
    )
    return build_factor_base(inst, spec)


def signed_points(E: EllipticCurve, xs: Iterable[int]) -> tuple[Point, ...]:
    """Return every distinct point represented by the x-coordinate factor base."""
    out: list[Point] = []
    seen: set[tuple[int, int]] = set()
    for x in xs:
        P = E.lift_x(int(x))
        if P is None:
            continue
        for Q in (P, E.negate(P)):
            if Q is not None and Q not in seen:
                seen.add(Q)
                out.append(Q)
    return tuple(out)


def exact_two_sum(E: EllipticCurve, xs: Iterable[int], target: Point) -> TwoSumResult:
    """Exact m=2 decomposition oracle using EC group arithmetic, not Semaev."""
    if target is None:
        raise ValueError("target must be affine")
    t0 = time.perf_counter()
    points = signed_points(E, xs)
    point_set = set(points)
    representations: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    first: tuple[tuple[int, int], tuple[int, int]] | None = None

    for A in points:
        B = E.add(target, E.negate(A))
        if B is None or B not in point_set:
            continue
        pair = tuple(sorted((A, B)))
        if pair in representations:
            continue
        representations.add(pair)
        if first is None:
            first = pair

    elapsed = time.perf_counter() - t0
    if first is None:
        return TwoSumResult(False, 0, elapsed)
    cert = {
        "kind": "decomposition",
        "statement": {
            "curve": {"p": E.p, "a": E.a, "b": E.b},
            "target": list(target),
            "summands": [list(first[0]), list(first[1])],
        },
    }
    return TwoSumResult(
        True,
        len(representations),
        elapsed,
        summand_x=(first[0][0], first[1][0]),
        certificate=cert,
    )


def verify_two_sum_result(result: TwoSumResult) -> bool:
    if not result.found:
        return result.certificate is None
    return semaev.verify_decomposition_certificate(result.certificate)


def _target_points(inst: ECDLPInstance, count: int, seed: int) -> tuple[Point, ...]:
    if count < 0:
        raise ValueError("target count must be non-negative")
    E = inst.curve()
    out: list[Point] = []
    for j in range(count):
        scalar = _seed_int(seed, f"fb-target-{j}") % (inst.n - 1) + 1
        R = E.mul(scalar, inst.P)
        if R is None:
            raise AssertionError("nonzero scalar of prime-order generator produced O")
        out.append(R)
    return tuple(out)


def rank_mod_prime(rows: Iterable[Iterable[int]], modulus: int) -> int:
    """Exact Gaussian rank over F_modulus; modulus must be prime."""
    if modulus <= 1 or not sympy.isprime(modulus):
        raise ValueError("rank modulus must be prime")
    A = [[int(v) % modulus for v in row] for row in rows]
    if not A:
        return 0
    width = len(A[0])
    if any(len(row) != width for row in A):
        raise ValueError("ragged matrix")
    rank = 0
    for col in range(width):
        pivot = next((r for r in range(rank, len(A)) if A[r][col] % modulus), None)
        if pivot is None:
            continue
        A[rank], A[pivot] = A[pivot], A[rank]
        inv = pow(A[rank][col], -1, modulus)
        A[rank] = [(v * inv) % modulus for v in A[rank]]
        for r in range(len(A)):
            if r == rank or A[r][col] == 0:
                continue
            factor = A[r][col]
            A[r] = [(a - factor * b) % modulus for a, b in zip(A[r], A[rank])]
        rank += 1
        if rank == len(A):
            break
    return rank


def _relation_row(xs: tuple[int, ...], summand_x: tuple[int, int]) -> list[int]:
    index = {x: i for i, x in enumerate(xs)}
    row = [0] * len(xs)
    for x in summand_x:
        row[index[x]] += 1
    return row


def measure_candidate(
    inst: ECDLPInstance,
    base: BuiltFactorBase,
    *,
    target_count: int,
    target_seed: int,
    run_groebner: bool = False,
    groebner_target_limit: int = 4,
) -> CandidateMeasurement:
    """Measure exact m=2 yield and optionally the existing Semaev solver path."""
    E = inst.curve()
    targets = _target_points(inst, target_count, target_seed)
    decomposable = 0
    total_mult = 0
    oracle_seconds = 0.0
    relation_rows: list[list[int]] = []
    exact: list[TwoSumResult] = []

    for R in targets:
        result = exact_two_sum(E, base.xs, R)
        exact.append(result)
        oracle_seconds += result.oracle_seconds
        if result.found:
            if not verify_two_sum_result(result):
                raise AssertionError("exact oracle emitted an invalid certificate")
            decomposable += 1
            total_mult += result.multiplicity
            relation_rows.append(_relation_row(base.xs, result.summand_x))

    rank = rank_mod_prime(relation_rows, inst.n) if relation_rows else 0

    solver_targets = 0
    solver_successes = 0
    solver_truth_positives = 0
    gb_seconds = 0.0
    gb_sizes: list[int] = []
    gb_degrees: list[int] = []
    if run_groebner:
        limit = min(len(targets), max(0, groebner_target_limit))
        for R, truth in zip(targets[:limit], exact[:limit]):
            m = semaev.measure_s3_decomposition(
                inst,
                factor_base_size=base.realized_size,
                target=R,
                factor_base=list(base.xs),
            )
            solver_targets += 1
            gb_seconds += m.groebner_seconds
            gb_sizes.append(m.groebner_basis_size)
            gb_degrees.append(m.groebner_basis_max_degree)
            if m.decomposition_found:
                if not semaev.verify_decomposition_certificate(m.certificate):
                    raise AssertionError("Semaev solver emitted invalid decomposition certificate")
                solver_successes += 1
            if truth.found:
                solver_truth_positives += 1
            if bool(m.decomposition_found) != bool(truth.found):
                raise AssertionError(
                    "Semaev solver disagrees with exact two-sum oracle on decomposition existence"
                )

    solver_recall = None
    if run_groebner:
        solver_recall = 1.0 if solver_truth_positives == 0 else solver_successes / solver_truth_positives

    return CandidateMeasurement(
        family=base.spec.family,
        scope=base.spec.scope,
        requested_size=base.spec.requested_size,
        realized_size=base.realized_size,
        factor_base_hash=base.factor_base_hash,
        construction_seconds=base.construction_seconds,
        lift_fraction=base.lift_fraction,
        targets=len(targets),
        decomposable_targets=decomposable,
        decomposition_yield=(decomposable / len(targets) if targets else 0.0),
        mean_multiplicity=(total_mult / decomposable if decomposable else 0.0),
        oracle_seconds=oracle_seconds,
        relation_rank=rank,
        solver_targets=solver_targets,
        solver_successes=solver_successes,
        solver_recall=solver_recall,
        groebner_seconds=gb_seconds,
        groebner_basis_size_mean=(sum(gb_sizes) / len(gb_sizes) if gb_sizes else None),
        groebner_basis_max_degree_mean=(sum(gb_degrees) / len(gb_degrees) if gb_degrees else None),
    )


def compare_with_matched_random(
    inst: ECDLPInstance,
    spec: FactorBaseSpec,
    *,
    control_seed: int,
    target_count: int,
    target_seed: int,
    run_groebner: bool = False,
    groebner_target_limit: int = 4,
) -> MatchedComparison:
    """Build a structured base and an equal-cardinality random control."""
    if spec.family == "random_matched":
        raise ValueError("structured spec must not itself be random_matched")
    structured_base = build_factor_base(inst, spec)
    random_base = matched_random_control(inst, structured_base, seed=control_seed)
    if structured_base.realized_size != random_base.realized_size:
        raise AssertionError("matched-cardinality control construction failed")
    kwargs = dict(
        target_count=target_count,
        target_seed=target_seed,
        run_groebner=run_groebner,
        groebner_target_limit=groebner_target_limit,
    )
    return MatchedComparison(
        structured=measure_candidate(inst, structured_base, **kwargs),
        random_control=measure_candidate(inst, random_base, **kwargs),
    )
