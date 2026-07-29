"""A benchmark that can actually detect an ECDLP breakthrough.

The existing challenges (`EVAL-CAP-DLOG-12`, `EVAL-CAP-DLOG-16`) are capability
smoke tests: they ask "did you recover k?" and Pollard rho answers in under a
millisecond. Passing them says nothing about whether an approach beats rho,
which is the only thing a breakthrough claim is about. Four concrete defects,
each fixed here:

1. **Field size was decorative.** `generate_instance` takes the largest prime
   factor of `#E` as the subgroup order and does not bound the cofactor. Measured
   across seeds at 24 bits, `n` ranged from 349 to 20161 with cofactors up to
   31512 -- so a "24-bit challenge" was a sqrt(n) ~ 18-to-141 step problem and
   the advertised size meant nothing. Here the cofactor is bounded and both
   `cofactor` and `n_over_p` are recorded on every instance, so a degenerate one
   is visible rather than silent.

2. **No baseline.** A solve was scored pass/fail against nothing. Here every
   instance carries a rho baseline in COUNTED GROUP OPERATIONS, measured on that
   same instance with the same counter -- not a theoretical sqrt(n), and not
   wall-clock, which is a property of the machine and the language.

3. **Pass/fail cannot see an exponent.** A constant-factor win and an asymptotic
   win look identical at one size. Scoring here is the fitted slope of
   log(ops) against log(n) across a LADDER. Rho sits at 1/2. A breakthrough is a
   slope materially below 1/2 that persists across the ladder.

4. **Criteria that cannot fail.** Twice in one campaign this program shipped a
   success criterion that was true by construction -- EXP-GGM-001's control gate
   compared two hardcoded constants in the same file, and EXP-SUBRES-001's
   `beta_ops` was forced below its threshold by a loop whose cost did not depend
   on the quantity under test. So: no threshold appears anywhere in this module,
   scoring is a pure function of measured counts, and `verdict` is computed by
   the caller from a value this file never sees.

What this benchmark still cannot do, stated because a benchmark's silence is
where overclaiming starts: it runs at toy scale. Clearing it is necessary for a
breakthrough claim and nowhere near sufficient -- a real claim needs
cryptographic sizes, complete end-to-end accounting, and independent review.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Sequence

import sympy

from .toycurve import EllipticCurve, ECDLPInstance, _seed_int, _find_point_of_order

# The seven cost stages a complete-cost claim must account for. A submission
# that leaves any of these undeclared is INCOMPLETE, not merely fast: every
# failed candidate in this program's history omitted exactly one.
COST_STAGES = (
    "preprocessing",
    "relation_collection",
    "linear_algebra",
    "target_descent",
    "verification",
    "memory",
    "multi_target",
)


@dataclass
class HardInstance:
    """An ECDLP instance whose difficulty actually tracks its advertised size."""
    p: int
    a: int
    b: int
    P: tuple[int, int]
    Q: tuple[int, int]
    n: int                      # prime subgroup order
    cofactor: int               # #E / n -- bounded, and recorded so it is visible
    field_bits: int
    seed: int
    curve_order: int
    k: int | None = None        # withheld from solvers; present only for authoring

    @property
    def n_over_p(self) -> float:
        """Near 1 means the advertised size is honest. Near 0 means it is not."""
        return self.n / self.p

    @property
    def work_bits(self) -> float:
        """log2(sqrt(n)) -- the real difficulty, as opposed to field_bits."""
        return math.log2(self.n) / 2.0

    def public(self) -> dict[str, Any]:
        """Exactly what a solver may see. `k` is never included."""
        return {"p": self.p, "a": self.a, "b": self.b,
                "P": list(self.P), "Q": list(self.Q), "n": self.n,
                "cofactor": self.cofactor, "field_bits": self.field_bits,
                "n_over_p": round(self.n_over_p, 6),
                "work_bits": round(self.work_bits, 3)}

    def curve(self) -> EllipticCurve:
        return EllipticCurve(self.p, self.a, self.b)

    def instance(self) -> ECDLPInstance:
        """An ECDLPInstance carrying k=0, for solvers that must not see the scalar."""
        return ECDLPInstance(self.p, self.a, self.b, self.P, self.Q, self.n,
                             0, self.field_bits, self.seed)


def generate_hard_instance(seed: int, field_bits: int, *,
                           max_cofactor: int = 8,
                           max_curves: int = 4000) -> HardInstance:
    """Find a curve whose prime subgroup order is a real fraction of p.

    `max_cofactor` is the whole point. Cryptographic curves have cofactor 1
    (NIST) or 8 (Curve25519); the default here matches that, so `field_bits`
    means what it appears to mean. Raising it makes instances easier while
    leaving the advertised size unchanged, which is the defect this replaces.
    """
    if field_bits < 8:
        raise ValueError("field_bits must be >= 8 for a meaningful instance")
    p = int(sympy.nextprime(
        _seed_int(seed, "p") % (2 ** field_bits) | (1 << (field_bits - 1))))
    for t in range(1, max_curves):
        a = _seed_int(seed, f"a{t}") % p
        b = _seed_int(seed, f"b{t}") % p
        try:
            E = EllipticCurve(p, a, b)
        except ValueError:
            continue
        order = E.order() if field_bits <= 24 else E.order_bsgs()
        n = int(max(sympy.factorint(order)))
        cofactor = order // n
        if cofactor > max_cofactor:
            continue
        P = _find_point_of_order(E, n, cofactor, seed, t)
        if P is None:
            continue
        k = _seed_int(seed, f"k{t}") % (n - 2) + 2
        Q = E.mul(k, P)
        return HardInstance(p=p, a=a, b=b, P=P, Q=Q, n=n, cofactor=cofactor,
                            field_bits=field_bits, seed=seed,
                            curve_order=order, k=k)
    raise RuntimeError(
        f"no curve with cofactor <= {max_cofactor} for seed={seed}, "
        f"bits={field_bits} within {max_curves} candidates")


@dataclass
class Measurement:
    """One solver's result on one instance, in counted group operations."""
    instance_seed: int
    field_bits: int
    n: int
    work_bits: float
    solved: bool
    certificate_valid: bool
    group_operations: int | None      # the cost metric; None if unsolved
    wall_seconds: float               # diagnostic ONLY, never fitted
    stages_charged: tuple[str, ...] = ()
    stages_omitted: tuple[str, ...] = ()
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def rho_baseline(inst: HardInstance, *,
                 max_iterations: int | None = None) -> Measurement:
    """Measure what Pollard rho actually costs on THIS instance.

    Counted group operations, from rho's own instrumentation, including
    precompute and verification -- not a theoretical sqrt(n), and not wall-clock.
    A baseline computed from a formula rather than from the same counter the
    challenger uses is not a comparison.
    """
    from . import rho as rho_module

    started = time.monotonic()
    result = rho_module.solve(inst.instance(), max_iterations=max_iterations)
    wall = time.monotonic() - started
    k = getattr(result, "k", None)
    ops = getattr(result, "total_group_operations", None)
    valid = False
    if k is not None:
        valid = inst.curve().mul(int(k), inst.P) == inst.Q
    return Measurement(
        instance_seed=inst.seed, field_bits=inst.field_bits, n=inst.n,
        work_bits=inst.work_bits, solved=k is not None,
        certificate_valid=valid, group_operations=ops, wall_seconds=round(wall, 6),
        stages_charged=("relation_collection", "verification"),
        stages_omitted=("preprocessing", "linear_algebra", "target_descent",
                        "memory", "multi_target"),
        note="generic square-root baseline; charges no preprocessing and "
             "amortises over no targets")


def fit_exponent(points: Sequence[tuple[int, int]]) -> dict[str, Any]:
    """Estimate alpha in ops = C + c*n^alpha, and say when it cannot be estimated.

    A RAW log-log slope is wrong here, and dangerously so. Every solver carries a
    setup constant -- rho's own is its branch precompute -- and at toy n that
    constant dominates the n-dependent term. Measured on this harness's rho:

        ops = 732 + 5.06*sqrt(n)

    so the raw slope comes out 0.174 for an algorithm that is provably 0.5. A
    benchmark scoring raw slopes would rate *every* submission sub-square-root,
    passing false breakthroughs and rejecting true ones with equal confidence.

    So three quantities are reported and the caller is told which to trust:
      * `raw_slope` -- the naive fit, retained ONLY so its bias stays visible.
      * `offset_corrected_slope` -- fitted after estimating C from the ladder;
        this is the one that means something.
      * `ratio_trend` -- ops/sqrt(n) across the ladder. Flat means square-root.
        Falling means genuinely sub-square-root. This needs no fit at all and is
        the most robust of the three on a short ladder.

    `constant_dominates` is true when the estimated C exceeds the n-dependent
    term at the largest instance, which means the ladder is too small to resolve
    an exponent and NO exponent claim may be made from it.
    """
    usable = sorted([(n, ops) for n, ops in points if n > 1 and ops and ops > 0])
    if len(usable) < 2:
        return {"raw_slope": None, "offset_corrected_slope": None,
                "reason": "need at least two solved sizes", "points": len(usable)}

    xs = [math.log(n) for n, _ in usable]
    ys = [math.log(ops) for _, ops in usable]

    def _slope(a: Sequence[float], b: Sequence[float]) -> float | None:
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        d = sum((x - ma) ** 2 for x in a)
        return (sum((x - ma) * (y - mb) for x, y in zip(a, b)) / d) if d else None

    raw = _slope(xs, ys)
    pairwise = [round((ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]), 6)
                for i in range(len(xs) - 1) if xs[i + 1] != xs[i]]

    loo = []
    if len(usable) >= 3:
        for drop in range(len(usable)):
            sx = [x for i, x in enumerate(xs) if i != drop]
            sy = [y for i, y in enumerate(ys) if i != drop]
            s = _slope(sx, sy)
            if s is not None:
                loo.append(round(s, 6))

    # Estimate C by least squares against sqrt(n), then refit the exponent on
    # the residual. sqrt is the right probe because it is the incumbent's shape:
    # if the challenger really is sub-sqrt, the residual still reveals it.
    roots = [n ** 0.5 for n, _ in usable]
    obs = [float(ops) for _, ops in usable]
    mr, mo = sum(roots) / len(roots), sum(obs) / len(obs)
    dr = sum((r - mr) ** 2 for r in roots)
    c = (sum((r - mr) * (o - mo) for r, o in zip(roots, obs)) / dr) if dr else 0.0
    C = mo - c * mr

    corrected = None
    if len(usable) >= 3 and c > 0:
        resid = [(n, o - C) for (n, o) in usable if o - C > 0]
        if len(resid) >= 2:
            corrected = _slope([math.log(n) for n, _ in resid],
                               [math.log(v) for _, v in resid])

    # Resolvability. For any square-root algorithm with a setup constant,
    #     ops/sqrt(n) = C/sqrt(n) + c
    # which FALLS as n grows. So a falling ops/sqrt(n) is NOT evidence of
    # sub-square-root behaviour -- it is C being amortised, and it happens for
    # rho itself. The real discriminator is whether the ratio CONVERGES to a
    # positive constant (square-root) or keeps falling toward zero (genuinely
    # sub-square-root), and that is only visible once C stops mattering.
    #
    # Calibrated on this harness's rho, whose true exponent is known to be 0.5:
    # a five-rung ladder to n ~ 1.4e6 gave raw 0.236 and offset-corrected 0.732.
    # NEITHER recovered 0.5. At that ladder's top C still contributed 21% of the
    # ratio. Until that share is small, no exponent claim is admissible from
    # this data, and the benchmark says so rather than reporting a number.
    largest_n = usable[-1][0]
    n_dependent_term = c * (largest_n ** 0.5) if c > 0 else 0.0
    constant_share = (C / (C + n_dependent_term)) if (C + n_dependent_term) else 1.0
    resolvable = bool(c > 0 and constant_share < 0.10 and len(usable) >= 4)

    return {
        "raw_slope": round(raw, 6) if raw is not None else None,
        "raw_slope_note": "biased LOW by the setup constant; do not score on this",
        "offset_corrected_slope": (round(corrected, 6)
                                   if corrected is not None else None),
        "estimated_setup_constant": round(C, 2),
        "estimated_coefficient": round(c, 4),
        "ratio_trend": [round(ops / (n ** 0.5), 4) for n, ops in usable],
        "ratio_trend_note": ("ops/sqrt(n). A FALLING trend is NOT sub-square-root: "
                             "it is the setup constant being amortised, and rho "
                             "itself does it. Convergence to a positive constant "
                             "is square-root; continued decay toward zero is not."),
        "pairwise_slopes": pairwise,
        "leave_one_out_slopes": loo,
        "leave_one_out_spread": round(max(loo) - min(loo), 6) if loo else None,
        "setup_constant_share_at_ladder_top": round(constant_share, 4),
        "ladder_resolves_an_exponent": resolvable,
        "resolvability_note": (
            "requires >= 4 rungs and the setup constant contributing < 10% of "
            "ops/sqrt(n) at the largest instance. Calibration: on rho, whose "
            "true exponent is 0.5, a 5-rung ladder to n~1.4e6 (constant share "
            "21%) yielded raw 0.236 and corrected 0.732 -- both wrong. If this "
            "field is false, report NO exponent."),
        "points": len(usable),
    }


def compare(challenger: Sequence[Measurement],
            baseline: Sequence[Measurement]) -> dict[str, Any]:
    """Compare a challenger against rho on the same ladder.

    Returns measured quantities only. It computes NO verdict and contains NO
    threshold: the caller applies the criterion. That separation is deliberate --
    a scorer that knows the passing value is how a criterion stops being able to
    fail.
    """
    by_seed = {(m.instance_seed, m.field_bits): m for m in baseline}
    rows = []
    for c in challenger:
        b = by_seed.get((c.instance_seed, c.field_bits))
        row: dict[str, Any] = {
            "instance_seed": c.instance_seed, "field_bits": c.field_bits,
            "n": c.n, "work_bits": c.work_bits,
            "challenger_solved": c.solved,
            "challenger_certificate_valid": c.certificate_valid,
            "challenger_ops": c.group_operations,
            "baseline_ops": b.group_operations if b else None,
        }
        if (c.group_operations and b and b.group_operations
                and c.certificate_valid):
            row["speedup_vs_rho"] = round(b.group_operations / c.group_operations, 6)
        else:
            row["speedup_vs_rho"] = None
        rows.append(row)

    solved = [c for c in challenger if c.solved and c.certificate_valid]
    # Any stage the challenger never charges makes its cost incomparable, not
    # merely optimistic.
    omitted: set[str] = set()
    for c in challenger:
        omitted |= set(c.stages_omitted)
    unaccounted = [s for s in COST_STAGES
                   if all(s not in c.stages_charged for c in challenger)]

    return {
        "rows": rows,
        "challenger_exponent": fit_exponent(
            [(c.n, c.group_operations) for c in solved]),
        "baseline_exponent": fit_exponent(
            [(b.n, b.group_operations) for b in baseline
             if b.solved and b.certificate_valid]),
        "instances_solved": len(solved),
        "instances_attempted": len(challenger),
        "stages_never_charged": unaccounted,
        "cost_accounting_complete": not unaccounted,
        "scope": ("toy-scale measurement of counted group operations. Clearing "
                  "this is necessary for a breakthrough claim and nowhere near "
                  "sufficient: it is not cryptographic scale, not end-to-end "
                  "cost, and not independently reviewed."),
    }


def build_ladder(seeds: Sequence[int], sizes: Sequence[int], *,
                 max_cofactor: int = 8,
                 on_instance: Callable[[HardInstance], None] | None = None
                 ) -> list[HardInstance]:
    """Generate the instance ladder. Point counting dominates; cache the result."""
    out = []
    for bits in sizes:
        for seed in seeds:
            inst = generate_hard_instance(seed, bits, max_cofactor=max_cofactor)
            if on_instance:
                on_instance(inst)
            out.append(inst)
    return out
