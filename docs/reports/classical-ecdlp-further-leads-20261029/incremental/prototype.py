"""Truth-free incremental prototype; not an admitted scientific runner.

Dependencies are the frozen transfer-successor source modules. Import this
module with that directory on sys.path. Only the additive primitive evaluation
changes; compute.ungated_attempt supplies the copied interval/witness semantics.
No cohort, sampling, scalar table, timer, scientific CLI or persistent cache.
"""
from __future__ import annotations

from constructor import normalized_miller_coefficient, result
from curve import Counter, Curve, point_json
from compute import add_counts, scalar_inverse


def _next_z(field, value: int, slope: int) -> int:
    field.counter.tick("incremental_z_update")
    return field.add(field.mul(2, value), slope)


def _answer_from_z(prepared, target, z, curve):
    """Internal circuit body, after the same membership/identity boundary."""
    x, y = target
    alpha, beta = prepared.arm["alpha"], prepared.arm["beta"]
    offset = curve.f.mul(prepared.c, curve.f.sub(x, prepared.base[0]))
    bracket = curve.f.add(alpha, curve.f.mul(beta, offset))
    numerator = curve.f.add(z, curve.f.mul(curve.f.mul(prepared.c, y), bracket))
    if curve.f.equal(numerator, 0):
        curve.counter.tick("exception_zero_numerator")
        return result("UNDEFINED", reason="ZERO_NUMERATOR", z=z, g=numerator,
                      anchor=prepared.anchor)
    normalized = curve.f.mul(numerator, prepared.inverse_anchor)
    character = curve.f.power(normalized, (curve.p - 1) // 2)
    if character not in (1, curve.p - 1):
        raise ValueError("non-Legendre character in declared prime field")
    return result("BIT", bit=0 if character == 1 else 1, z=z, g=numerator,
                  anchor=prepared.anchor, normalized=normalized)


def incremental_ungated_attempt(prepared, original_base, original_target,
                                base_multiplier, target_multiplier,
                                include_query_counters=False):
    """Same public inputs and non-counter outputs as compute.ungated_attempt.

    Primitive state is local to one attempt. A ready candidate initializes it
    using the original subgroup-checking Miller chain. Slope reuse occurs only
    at the doubling already required by the reduction. Undefined numerator
    calls never stop the fixed-length sequence. Undefined setups and wrong-root
    controls retain their original evaluator and require no primitive cache.
    """
    model, r = prepared.model, prepared.model["r"]
    blinding = Curve(model["p"], model["a"], model["b"])
    if not blinding.contains(original_target) or original_target is None:
        raise ValueError("primary target must be a nonidentity public point")
    transformed_target = blinding.multiply(original_target, target_multiplier)
    curve = Curve(model["p"], model["a"], model["b"])
    transitions = Curve(model["p"], model["a"], model["b"])
    length = r.bit_length() + 1
    value, current, fully_defined = 0, transformed_target, True
    evaluate, trace, reasons = Counter(), [], []
    use_z = not prepared.setup_reason and prepared.arm["kind"] != "wrong_root"
    z, z_initialized = None, False
    for index in range(length):
        if not use_z:
            answer, counts = prepared.evaluate(current)
        else:
            query = Curve(model["p"], model["a"], model["b"])
            if not query.contains(current):
                raise ValueError("target is not a canonical point on curve")
            if current is None:
                query.counter.tick("exception_identity_predicate")
                z, z_initialized = 0, True
                answer = result("BIT", bit=0, z=0, anchor=prepared.anchor)
            else:
                if not z_initialized:
                    z = normalized_miller_coefficient(query, current, r, prepared.inverse_r)
                    z_initialized = True
                answer = _answer_from_z(prepared, current, z, query)
            counts = query.counter.snapshot()
        add_counts(evaluate, counts)
        entry = {"index": index, "target": point_json(current), "answer": answer}
        if include_query_counters:
            entry["counters"] = counts
        trace.append(entry)
        curve.counter.tick("recovery_scalar_digit_update")
        if answer["status"] != "BIT":
            fully_defined = False
            reasons.append(answer["reason"])
        value = 2 * value + (answer["bit"] if answer["status"] == "BIT" else 0)
        if index + 1 < length:
            current, slope = curve.add_with_slope(current, current)
            if use_z and z_initialized:
                z = _next_z(transitions.f, z, slope)
    denominator = 1 << length
    curve.counter.tick("recovery_scalar_interval_round")
    lower = r * value
    upper = r * (value + 1)
    candidate_prime = (lower + denominator - 1) // denominator if fully_defined else None
    nonempty = bool(fully_defined and candidate_prime < r and denominator * candidate_prime < upper)
    conversion = Counter()
    inverse_b = scalar_inverse(target_multiplier, r, conversion)
    candidate = None
    transformed_check = original_check = None
    if nonempty:
        conversion.tick("order_mul", 2)
        conversion.tick("order_reduce", 2)
        candidate = (base_multiplier * inverse_b % r) * candidate_prime % r
        transformed_check = curve.equal(curve.multiply(prepared.base, candidate_prime), transformed_target)
        original_check = curve.equal(curve.multiply(original_base, candidate), original_target)
    recovered = bool(nonempty and transformed_check and original_check)
    status = "RECOVERED" if recovered else "UNDEFINED" if not fully_defined else "EMPTY_INTERVAL" if not nonempty else "REJECTED_FINAL_VERIFICATION"
    reason = None if recovered else ",".join(sorted(set(reasons))) if not fully_defined else "EMPTY_BINARY_INTERVAL" if not nonempty else "FINAL_VERIFICATION_FAILED"
    return transformed_target, {
        "status": status, "reason": reason, "L": length,
        "candidate_scalar_prime": candidate_prime, "candidate_scalar": candidate,
        "scalar_prime": candidate_prime if recovered else None,
        "scalar": candidate if recovered else None,
        "target_multiplier_inverse": inverse_b,
        "interval": {"value": value if fully_defined else None, "denominator": denominator,
                     "lower_numerator": lower if fully_defined else None,
                     "upper_numerator": upper if fully_defined else None, "nonempty": nonempty},
        "predicate_evaluations": length, "retained_bit_reads": 0, "predicate_trace": trace,
        "counts": {"blinding": blinding.counter.snapshot(), "evaluate": evaluate.snapshot(),
                   "state_updates": transitions.counter.snapshot(),
                   "reduction": curve.counter.snapshot(), "conversion": conversion.snapshot()},
        "public_checks": {"transformed": transformed_check, "original": original_check}}
