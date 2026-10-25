"""Bounded representation controls, not authoritative experiment records.

These diagnostics calibrate software on small public synthetic curves. They do
not approve trials, close research questions, or establish an attack-cost bound.
"""

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import platform
from math import isqrt
from random import Random
import secrets
from time import process_time

from .representation_arithmetic import Curve, IDENTITY, Lift, Point, is_prime, ordinary_curve, solve_mod


def curve_metadata(curve: Curve, generator: Point | None = None, *, order=None) -> dict:
    """Use the repository's EC1 metadata convention, without certifying a map."""
    from tools.curve_identity import curve_identity

    generator = curve.generator if generator is None else generator
    field = {"characteristic": curve.p, "degree": 1,
             "representation": "prime-field-residues", "element_encoding": "integer"}
    record = {"model": "short-weierstrass", "a": curve.a, "b": curve.b,
              "subgroup_order": curve.order if order is None else order, "cofactor": 1,
              "generator": list(generator), "target_group": "E(F_p)"}
    return {"field": field, "curve": record, **curve_identity(field, record, "rep")}


def audit_additive_map(curve: Curve, mapper, *, seed=20261021, samples=24) -> dict:
    """Audit a supplied public-point -> F_p callable on a bounded prime group.

    Algebraic checks cannot establish independence from a hidden scalar or
    cheap construction. Exceptions propagate as software failures, not negative
    mathematical evidence. Callers must account for construction separately.
    """
    if samples < 1 or not is_prime(curve.order):
        raise ValueError("Use a prime-order toy curve and at least one sample")
    rng, cache = Random(seed), {}
    repeat_failures = 0
    p, r, base = curve.p, curve.order, curve.generator

    def image(point):
        nonlocal repeat_failures
        if point not in cache:
            value, repeated = mapper(point), mapper(point)
            if type(value) is not int or type(repeated) is not int:
                raise TypeError("The map must return an integer representing F_p")
            repeat_failures += value % p != repeated % p
            cache[point] = value % p
        return cache[point]

    pairs = [(None, base), (base, curve.neg(base)),
             (curve.mul(r-1, base), base)]
    pairs += [(rng.choice(curve.points), rng.choice(curve.points)) for _ in range(samples)]
    scalars = [(0, base), (1, base), (r, base), (r-1, base)]
    scalars += [(rng.randrange(2*r+1), rng.choice(curve.points)) for _ in range(samples)]
    additions = sum(image(curve.add(a, b)) != (image(a)+image(b)) % p for a, b in pairs)
    multiplications = sum(image(curve.mul(k, point)) != k*image(point) % p
                          for k, point in scalars)
    identity_zero = image(None) == 0
    return {"map_addition_failures": additions, "map_scalar_failures": multiplications,
            "identity_maps_to_zero": identity_zero,
            "map_repeated_value_failures": repeat_failures,
            "sampled_algebra_passes": additions == multiplications == repeat_failures == 0 and identity_zero,
            "nonzero_image_observed": any(cache.values()),
            "nonzero_additive_map_structurally_impossible": r != p,
            "map_evaluations": 2*len(cache), "construction_cost_verified": False,
            "secret_independence_verified": False}


@dataclass(frozen=True)
class PublicInstance:
    curve: Curve
    base: Point
    target: Point
    order: int

    def __post_init__(self):
        if self.order != self.curve.order or not is_prime(self.order):
            raise ValueError("Public subgroup order must match the certified prime-order toy curve")
        if self.base is None or not self.curve.contains(self.base) or not self.curve.contains(self.target):
            raise ValueError("Public points must be on the curve, with a nonidentity base")


def recover_by_digit(instance: PublicInstance, precision=3, curve_shift=0,
                     x_shift=0, torsion=False) -> int | None:
    """Candidate receives public data only. A result still needs group verification."""
    lift = Lift(instance.curve, precision, curve_shift, x_shift)
    denominator = lift.first_digit(instance.base, torsion)
    if denominator == 0:
        return None
    numerator = lift.first_digit(instance.target, torsion)
    return numerator * pow(denominator, -1, instance.curve.p) % instance.curve.p


def bsgs(instance: PublicInstance) -> int | None:
    """Cost-charged generic baseline; the table is rebuilt for every instance."""
    curve, p, q, r = instance.curve, instance.base, instance.target, instance.order
    width = isqrt(r) + 1
    table = {}
    current = None
    for j in range(width):
        table.setdefault(current, j)
        current = curve.add(current, p)
    step = curve.neg(curve.mul(width, p))
    current = q
    for i in range(width):
        if current in table:
            candidate = (i*width+table[current]) % r
            if curve.mul(candidate, p) == q:
                return candidate
        current = curve.add(current, step)
    return None


def check_dependencies(dependencies: tuple[str, ...]) -> dict:
    """A declared-provenance gate, not a proof about arbitrary program behavior."""
    forbidden = sorted(set(dependencies) & {
        "unknown_scalar", "secret_label", "discrete_log_oracle"
    })
    return {"passed": not forbidden, "forbidden_dependencies": forbidden,
            "scope": "declared dependencies; source and cost review still required"}


def check_map(curve: Curve, lift: Lift, torsion: bool, rng: Random,
              samples: int) -> dict:
    p, r, base = curve.p, curve.order, curve.generator
    pairs = [(None, base), (base, curve.neg(base)),
             (curve.mul(r-1, base), base)]
    pairs += [(rng.choice(curve.points), rng.choice(curve.points))
              for _ in range(samples)]
    section = lift.torsion_point if torsion else lift.point
    cache = {}

    def mapped(point):
        if point not in cache:
            cache[point] = lift.first_digit(point, torsion)
        return cache[point]

    add_failures = section_failures = 0
    for left, right in pairs:
        total = curve.add(left, right)
        add_failures += mapped(total) != (mapped(left)+mapped(right)) % p
        section_failures += not lift.equal(
            section(total), lift.add(section(left), section(right)))
    scalar_cases = [(0, base), (1, base), (r, base), (r-1, base)]
    scalar_cases += [(rng.randrange(2*r+1), rng.choice(curve.points))
                     for _ in range(samples)]
    scalar_failures = section_scalar_failures = 0
    for scalar, point in scalar_cases:
        multiple = curve.mul(scalar, point)
        scalar_failures += mapped(multiple) != scalar*mapped(point) % p
        section_scalar_failures += not lift.equal(
            section(multiple), lift.mul(scalar, section(point)))
    nonzero = any(cache.values())
    return {
        "precision": lift.precision, "curve_shift": (lift.a-curve.a)//p,
        "x_shift": lift.x_shift, "tested_additions": len(pairs),
        "tested_scalar_multiplications": len(scalar_cases),
        "map_addition_failures": add_failures,
        "map_scalar_failures": scalar_failures,
        "section_addition_failures": section_failures,
        "section_scalar_failures": section_scalar_failures,
        "identity_maps_to_zero": mapped(None) == 0,
        "nonzero_image_observed": nonzero,
        "r_times_base_image_mod_p": r*mapped(base) % p,
        "base_image": mapped(base),
        "nonzero_additive_map_structurally_impossible": r != p,
    }


def circularity_controls(seed=20261021, samples=24, hidden_trials=12) -> dict:
    start = process_time()
    anomalous = Curve(1019, 373, 837)
    ordinary = ordinary_curve()
    if anomalous.order != anomalous.p:
        raise AssertionError("Anomalous positive control is invalid")
    fixtures_cpu = process_time()-start
    variants = [(2, 0, 0), (3, 0, 0), (4, 0, 0), (3, 0, 1), (3, 1, 0)]
    reports = []
    for name, curve, torsion in (
        ("anomalous_smart_positive", anomalous, False),
        ("ordinary_naive_linearization_negative", ordinary, False),
        ("ordinary_homomorphic_torsion_lift_zero_signal", ordinary, True),
    ):
        case_start = process_time()
        diagnostics = [check_map(curve, Lift(curve, *variant), torsion,
                                 Random(seed), samples) for variant in variants]
        # The judge alone creates these labels. Neither the seed nor a label is
        # provided to recover_by_digit. This is API separation, not isolation.
        challenges = []
        for _ in range(hidden_trials):
            scalar = secrets.randbelow(curve.order-1)+1
            public = PublicInstance(curve, curve.generator,
                                    curve.mul(scalar, curve.generator), curve.order)
            challenges.append((public, scalar))
        successes = [0]*len(variants)
        certificates = []
        stable = 0
        recovery_cpu = 0.0
        for public, label in challenges:
            results = []
            for index, variant in enumerate(variants):
                tick = process_time()
                answer = recover_by_digit(public, *variant, torsion=torsion)
                recovery_cpu += process_time()-tick
                verified = (answer is not None and
                            curve.mul(answer, public.base) == public.target)
                if verified and answer % curve.order != label:
                    raise AssertionError("Judge and group verification disagree")
                successes[index] += verified
                results.append(answer)
            stable += len(set(results)) == 1 and results[0] is not None
            certificates.append({"base": public.base, "target": public.target,
                                 "answers_by_variant": results})
        baseline_tick = process_time()
        baseline_successes = sum(bsgs(public) == label for public, label in challenges)
        baseline_cpu = process_time()-baseline_tick
        algebra_passes = all(d["map_addition_failures"] == 0 and
                             d["map_scalar_failures"] == 0 and
                             d["identity_maps_to_zero"] for d in diagnostics)
        signal = all(d["base_image"] != 0 for d in diagnostics)
        accepted = (curve.order == curve.p and algebra_passes and signal and
                    all(n == hidden_trials for n in successes) and stable == hidden_trials)
        reports.append({
            "name": name, "p": curve.p, "r": curve.order,
            "curve": {"a": curve.a, "b": curve.b},
            "curve_identity": curve_metadata(curve),
            "status": "passes_bounded_signal_checks" if accepted else "rejected_as_shortcut",
            "diagnostics": diagnostics,
            "precision_first_digit_stable": len({d["base_image"] for d in diagnostics[:3]}) == 1,
            "raw_base_image_depends_on_lift": len({d["base_image"] for d in diagnostics}) > 1,
            "hidden_trials": hidden_trials,
            "verified_recoveries_by_variant": successes,
            "public_challenge_certificates": certificates,
            "stable_answers_across_precision_and_lifts": stable,
            "candidate_recovery_cpu_seconds_all_variants": recovery_cpu,
            "bsgs_verified_recoveries": baseline_successes,
            "bsgs_cpu_seconds": baseline_cpu,
            "case_total_cpu_seconds": process_time()-case_start,
        })
    # A known answer can force compatibility on any curve; this fixture must be
    # rejected by provenance even though the displayed scalar relation holds.
    lift = Lift(ordinary)
    known_k = 12
    known_q = ordinary.mul(known_k, ordinary.generator)
    forced_q_lift = lift.mul(known_k, lift.point(ordinary.generator))
    return {
        "shared_fixture_cpu_seconds": fixtures_cpu,
        "cases": reports,
        "circular_known_k_control": {
            "known_calibration_scalar": known_k,
            "forced_lift_reduces_to_target": lift.reduce(forced_q_lift) == known_q,
            "scalar_relation_preserved_by_construction": True,
            "dependency_check": check_dependencies(("unknown_scalar",)),
            "hidden_instance_evaluation": "denied: construction requires the hidden label",
        },
        "hidden_label_boundary": "fresh OS randomness; labels absent from candidate API; not a security sandbox",
        "interpretation": "Passing sampled identities and hidden trials is evidence on these fixtures, not a proof of independence or an attack on other curves.",
        "total_cpu_seconds": process_time()-start,
    }


def factor_base(curve: Curve, size: int, policy: str, seed: int) -> list[Point]:
    points = list(curve.points[1:])
    if not 2 <= size < len(points):
        raise ValueError("Factor-base size must be between 2 and r-2")
    if policy == "random":
        return Random(seed).sample(points, size)
    if policy == "coordinate":
        return sorted(points)[:size]
    if policy == "low_degree":
        return sorted(points, key=lambda point: (
            (point[0]**2+3*point[1]) % curve.p, point))[:size]
    raise ValueError("Unknown factor-base policy")


def pair_table(curve: Curve, base: list[Point]) -> dict:
    pairs = {}
    for i, left in enumerate(base):
        for j in range(i, len(base)):
            pairs.setdefault(curve.add(left, base[j]), (i, j))
    return pairs


def relation_rows(a: int, b: int, i: int, j: int, size: int) -> list[int]:
    row = [a, b]+[0]*size
    row[2+i] -= 1
    row[2+j] -= 1
    return row


def benchmark_one_model(source: Curve, u: int, policy: str, size: int,
                        seed: int, attempts: list[tuple[int, int]],
                        base_point: Point, target: Point) -> dict:
    start = process_time()
    curve = source.scaled(u)
    p, q = source.transport(base_point, u), source.transport(target, u)
    r = source.order
    if not curve.contains(p) or not curve.contains(q) or curve.mul(r, p) is not None:
        raise AssertionError("Isomorphism did not preserve the public instance")
    build_tick = process_time()
    if policy == "transported":
        base = [source.transport(point, u)
                for point in factor_base(source, size, "random", seed)]
    else:
        base = factor_base(curve, size, "coordinate", seed)
    pairs = pair_table(curve, base)
    build_cpu = process_time()-build_tick
    rows, values, transcript = [], [], []
    solution, rank = None, 0
    solve_cpu = 0.0
    count = 0
    relation_tick = process_time()
    inconsistent = False
    for count, (a, b) in enumerate(attempts, 1):
        total = curve.add(curve.mul(a, p), curve.mul(b, q))
        if total not in pairs:
            continue
        i, j = pairs[total]
        full_row = relation_rows(a, b, i, j, size)
        rows.append(full_row[1:])
        values.append(-a)
        transcript.append([count, a, b, i, j])
        tick = process_time()
        solution, rank = solve_mod(rows, values, r)
        solve_cpu += process_time()-tick
        if solution is None:
            inconsistent = True
            break
        if rank == size+1:
            break
    relation_cpu = process_time()-relation_tick-solve_cpu
    verification_tick = process_time()
    answer = solution[0] if solution is not None and rank == size+1 else None
    verified = answer is not None and curve.mul(answer, p) == q
    verification_cpu = process_time()-verification_tick
    total_cpu = process_time()-start
    return {
        "u": u, "a": curve.a, "b": curve.b, "policy": policy,
        "curve_identity": curve_metadata(curve, p, order=r),
        "source_curve_uid": curve_metadata(source, base_point)["curve_uid"],
        "isomorphism": {"u": u, "x_exponent": 2, "y_exponent": 3},
        "factor_base_size": size, "unique_pair_sums": len(pairs),
        "attempts": count, "successful_relations": len(rows),
        "decomposition_misses": count-len(rows),
        "matrix_rank": rank, "unknowns": size+1,
        "solver_failures": int(inconsistent or not verified),
        "recovery_verified_in_original_group": bool(verified and
            source.mul(answer, base_point) == target),
        "recovered_scalar": answer,
        "construction_cpu_seconds": build_cpu,
        "relation_search_cpu_seconds": relation_cpu,
        "linear_algebra_cpu_seconds": solve_cpu,
        "verification_cpu_seconds": verification_cpu,
        "total_recovery_cpu_seconds": total_cpu,
        "relations_per_total_cpu_second": len(rows)/total_cpu if total_cpu else None,
        "relation_transcript_sha256": hashlib.sha256(json.dumps(transcript).encode()).hexdigest(),
        "factor_base": base,
        "factor_base_set_sha256": hashlib.sha256(
            json.dumps(sorted(base), separators=(",", ":")).encode()).hexdigest(),
    }


def model_benchmark(seed=20261021, size=16, max_attempts=5000) -> dict:
    start = process_time()
    source = ordinary_curve()
    p, r = source.generator, source.order
    # Public diagnostic instance; solvers only receive P and Q, never this label.
    label = secrets.randbelow(r-1)+1
    q = source.mul(label, p)
    fixture_cpu = process_time()-start
    rng = Random(seed+17)
    attempts = [(rng.randrange(r), rng.randrange(r)) for _ in range(max_attempts)]
    rows = [benchmark_one_model(source, u, policy, size, seed, attempts, p, q)
            for policy in ("transported", "fresh_coordinate") for u in (1, 2, 3, 5)]
    transported = [row for row in rows if row["policy"] == "transported"]
    match = len({row["relation_transcript_sha256"] for row in transported}) == 1
    for row in rows:
        row["judge_label_matches"] = row["recovered_scalar"] == label
    tick = process_time()
    baseline = bsgs(PublicInstance(source, p, q, r))
    baseline_cpu = process_time()-tick
    return {
        "p": source.p, "r": r, "seed": seed,
        "shared_fixture_cpu_seconds": fixture_cpu,
        "paired_coefficient_stream": True,
        "transported_relation_transcripts_match": match,
        "runs": rows, "bsgs_cpu_seconds": baseline_cpu,
        "bsgs_verified": baseline == label,
        "search_method": "exhaustive two-factor sums; public point enumeration charged where performed",
        "interpretation": "Toy cost benchmark. Transported bases must give identical relation transcripts. Fresh coordinate bases change the subset. No asymptotic advantage follows.",
        "twists": "Excluded: quadratic twists are not assumed isomorphic over the base field.",
        "total_cpu_seconds": process_time()-start,
    }


def collect_relations(curve, p, q, base, seed, count, max_attempts=20000):
    pairs = pair_table(curve, base)
    rng = Random(seed)
    seen, result = set(), []
    for attempt in range(1, max_attempts+1):
        a, b = rng.randrange(curve.order), rng.randrange(curve.order)
        total = curve.add(curve.mul(a, p), curve.mul(b, q))
        if total in pairs:
            i, j = pairs[total]
            item = (a, b, i, j)
            if item not in seen:
                result.append(item)
                seen.add(item)
                if len(result) == count:
                    return result, attempt
    raise RuntimeError(f"Residual budget exhausted: {len(result)}/{count} relations")


def coordinate_features(point: Point) -> list[int]:
    if point is None:
        raise ValueError("Factor-base features exclude the identity")
    x, y = point
    return [1, x, y, x*x, x*y, y*y]


def dot(left, right, modulus):
    return sum(a*b for a, b in zip(left, right)) % modulus


def residual_experiment(seed=20261021, size=16, train_count=40,
                        heldout_count=48) -> dict:
    start = process_time()
    curve = ordinary_curve()
    p, r = curve.p, curve.order
    base_point = curve.generator
    # Reproducible diagnostic labels are allowed here: no DLP success is claimed.
    target = curve.mul(Random(seed+31).randrange(1, r), base_point)
    lift = Lift(curve, 3)
    runs = []
    for policy in ("random", "coordinate", "low_degree"):
        tick = process_time()
        base = factor_base(curve, size, policy, seed)
        relations, attempts = collect_relations(
            curve, base_point, target, base, seed+59, train_count+heldout_count)
        Random(seed+71).shuffle(relations)
        construction_cpu = process_time()-tick
        points = [base_point, target]+base
        lifted = [lift.point(point) for point in points]
        logs, features, valuations = [], [], Counter()
        measure_tick = process_time()
        for a, b, i, j in relations:
            coefficients = relation_rows(a, b, i, j, size)
            residual = IDENTITY
            for coefficient, point in zip(coefficients, lifted):
                if coefficient:
                    residual = lift.add(residual, lift.mul(coefficient, point))
            value = lift.formal_log(residual)
            valuation = 0
            if value == 0:
                key = f">={lift.precision}"
            else:
                while value % p == 0:
                    value //= p
                    valuation += 1
                key = str(valuation)
            valuations[key] += 1
            logs.append(lift.normalized_log(residual))
            features.append(coefficients)
        measurement_cpu = process_time()-measure_tick
        normalized_modulus = p**(lift.precision-1)
        correction_tick = process_time()
        corrections = [lift.normalized_log(lift.mul(r, point)) *
                       pow(r, -1, normalized_modulus) % normalized_modulus
                       for point in lifted]
        correction_cpu = process_time()-correction_tick
        analytic_matches = sum(dot(row, corrections, normalized_modulus) == value
                               for row, value in zip(features, logs))
        polynomial_features = [coordinate_features(point) for point in points]
        polynomial_rows = [[sum(c*f[j] for c, f in zip(row, polynomial_features)) % p
                            for j in range(6)] for row in features]
        models = []
        for name, rows in (("degree_two_coordinate_model", polynomial_rows),
                           ("per_point_linear_control", features)):
            tick = process_time()
            model, rank = solve_mod(rows[:train_count],
                                    [value % p for value in logs[:train_count]], p)
            fit_cpu = process_time()-tick
            tick = process_time()
            predictions = None if model is None else [dot(row, model, p) for row in rows]
            prediction_cpu = process_time()-tick
            models.append({
                "name": name, "parameters": len(rows[0]), "training_rank": rank,
                "fit_status": "exact_fit" if model is not None else "no_exact_training_fit",
                "training_accuracy": None if predictions is None else sum(
                    a == b % p for a, b in zip(predictions[:train_count], logs[:train_count]))/train_count,
                "heldout_accuracy": None if predictions is None else sum(
                    a == b % p for a, b in zip(predictions[train_count:], logs[train_count:]))/heldout_count,
                "fit_cpu_seconds": fit_cpu,
                "prediction_cpu_seconds_all_relations": prediction_cpu,
                "conservative_construction_cpu_seconds_including_all_diagnostic_data":
                    construction_cpu+measurement_cpu+fit_cpu,
                "evaluation_modulus": p,
                "generalization_scope": "new relations on the same P, Q and factor base only",
            })
        precision_matches = 0
        # A bounded precision control checks the same residual, not merely a
        # numerically plausible answer, across all supported precisions.
        for relation, reference in zip(relations[:8], logs[:8]):
            consistent = True
            for precision in (2, 4):
                other = Lift(curve, precision)
                residual = IDENTITY
                for coefficient, point in zip(relation_rows(*relation, size), points):
                    if coefficient:
                        residual = other.add(residual, other.mul(coefficient, other.point(point)))
                expected_modulus = p**(min(precision, 3)-1)
                consistent &= other.normalized_log(residual) % expected_modulus == reference % expected_modulus
            precision_matches += consistent
        split_zero = all(lift.equal(lift.mul(r, lift.torsion_point(point)), IDENTITY)
                         for point in points)
        runs.append({
            "factor_base_policy": policy, "factor_base_size": size,
            "relations": len(relations), "attempts_to_collect": attempts,
            "training_relations": train_count, "heldout_relations": heldout_count,
            "precision": lift.precision, "residual_valuation_histogram": dict(valuations),
            "zero_model_heldout_accuracy": sum(v % p == 0 for v in logs[train_count:])/heldout_count,
            "relation_construction_cpu_seconds": construction_cpu,
            "residual_measurement_cpu_seconds": measurement_cpu,
            "models": models,
            "analytic_per_point_correction": {
                "formula": "c(R) = log([r]s(R)) / (r*p) mod p^(N-1)",
                "matching_residuals": analytic_matches,
                "evaluation_modulus": normalized_modulus,
                "construction_cpu_seconds": correction_cpu,
                "all_split_torsion_formal_signals_zero": split_zero,
            },
            "precision_control": {"checked_relations": min(8, len(relations)),
                                  "matching_relations": precision_matches},
            "end_to_end_improvement": "not demonstrated; exact per-point prediction is a structural negative control",
        })
    return {
        "p": p, "r": r, "seed": seed, "runs": runs,
        "valuation_zero_convention": "Zero mod p^N gives only v_p >= N, not an infinite valuation.",
        "success_gate": "Require a verified measured improvement over the frozen matched index-calculus pipeline, including relation collection, correction construction, solving and verification. Report the matched rho gap separately; beating rho is not the improvement gate. This diagnostic establishes no such improvement.",
        "total_cpu_seconds": process_time()-start,
    }


def cm_traces_j1728(p: int) -> tuple[int, ...]:
    """Necessary traces for y^2=x^3+a*x, a != 0, p > 3.

    If p == 3 mod 4, the trace is zero. Otherwise Frobenius is in Z[i], so
    t^2 + 4*v^2 = 4*p. This deliberately retains all signs and orientations.
    """
    if p % 4 == 3:
        return (0,)
    bound = isqrt(4*p)
    return tuple(t for t in range(-bound, bound+1)
                 if (4*p-t*t) % 4 == 0 and
                 isqrt((4*p-t*t)//4)**2 == (4*p-t*t)//4)


def constraint_benchmark() -> dict:
    start = process_time()
    candidates = [(p, a, r) for p in (101, 103, 107, 109, 127, 131)
                  for a in range(1, 21) for r in (5, 7, 11, 13)]

    def run(filtered):
        tick = process_time()
        accepted, counted, rejected = [], 0, 0
        orders, traces = {}, {}
        for p, a, r in candidates:
            if filtered:
                if p not in traces:
                    traces[p] = cm_traces_j1728(p)
                if not any((p+1-t) % r == 0 for t in traces[p]):
                    rejected += 1
                    continue
            # Both arms reuse the count across requested subgroup primes. The
            # filter must beat this equally cached baseline, not repeated work.
            key = (p, a)
            if key not in orders:
                orders[key] = Curve(p, a, 0).order
                counted += 1
            if orders[key] % r == 0:
                accepted.append((p, a, r))
        return {"cpu_seconds": process_time()-tick,
                "point_counts": counted, "pre_count_rejections": rejected,
                "subgroup_valid_candidates": len(accepted)}, set(accepted)

    unfiltered, reference = run(False)
    filtered, actual = run(True)
    return {
        "family": "j=1728 curves y^2=x^3+a*x over the listed toy primes",
        "candidate_count": len(candidates),
        "filters": "CM norm/trace, Hasse bound, and required subgroup divisibility",
        "shared_optimization": "Both arms cache point counts per curve across subgroup primes",
        "unfiltered": unfiltered, "filtered": filtered,
        "lost_positive_controls": len(reference-actual),
        "introduced_false_positives": len(actual-reference),
        "positive_control_sets_identical": reference == actual,
        "useful_transfer_candidates": None,
        "interpretation": "Subgroup existence only; no transfer, descent or endomorphism compatibility claim is made.",
        "total_cpu_seconds": process_time()-start,
    }


def build_report(experiment="all", seed=20261021) -> dict:
    """Build a software-control report without touching the research ledger."""
    if experiment not in ("all", "controls", "models", "residuals", "filters"):
        raise ValueError("Unknown representation control suite")
    start = process_time()
    report = {"schema": "ecdlp-representation-controls/v1", "seed": seed,
              "scope": "toy software controls; not an approved trial or attack-cost claim",
              "timing": "single-process CPU seconds; not a measured bound",
              "python_version": platform.python_version(),
              "source_pdf_status": "Filename supplied; contents and page-specific claims unverified",
              "knowledge_refs": ["KN-TECH-73630e", "KN-OPEN-3417fc"]}
    suites = (("controls", circularity_controls), ("models", model_benchmark),
              ("residuals", residual_experiment), ("filters", lambda _: constraint_benchmark()))
    for name, suite in suites:
        if experiment in ("all", name):
            report[name] = suite(seed)
    report["total_cpu_seconds"] = process_time()-start
    return report
