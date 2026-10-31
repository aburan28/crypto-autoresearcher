"""Truth-free fixed public coordinate circuits and conditional recovery.

The normalized Miller coefficient is computed by its binary line-coefficient
recurrence. Neither this module nor curve.py constructs a scalar orbit/table.
Primality certification is a separately charged harness responsibility.
"""
from __future__ import annotations

from dataclasses import dataclass

from curve import Counter, Curve, Point, point_json


def normalized_miller_coefficient(curve: Curve, point: Point, r: int, inverse_r: int | None = None) -> int:
    """Z(R)=-D_r(R)/r, with D_n=Z(nR)-nZ(R) on the declared subgroup."""
    curve.counter.tick("miller_coefficient_call")
    if point is None:
        curve.counter.tick("miller_identity_shortcut")
        return 0
    inverse_r = curve.f.inverse(r % curve.p) if inverse_r is None else inverse_r
    carry, coefficient = point, 0
    for bit in bin(r)[3:]:
        curve.counter.tick("miller_chain_double")
        carry, slope = curve.add_with_slope(carry, carry)
        coefficient = curve.f.add(curve.f.mul(2, coefficient), slope)
        if bit == "1":
            curve.counter.tick("miller_chain_add")
            carry, slope = curve.add_with_slope(carry, point)
            coefficient = curve.f.add(coefficient, slope)
    if carry is not None:
        curve.counter.tick("exception_outside_subgroup")
        raise ValueError("point is outside declared r-torsion subgroup")
    return curve.f.neg(curve.f.mul(coefficient, inverse_r))


def result(status: str, bit: int | None = None, reason: str | None = None, **fields: object) -> dict:
    return {"status": status, "bit": bit, "reason": reason,
            "z": None, "g": None, "anchor": None, "normalized": None, **fields}


@dataclass(frozen=True)
class Prepared:
    model: dict
    base: Point
    arm: dict
    setup_counts: dict[str, int]
    setup_reason: str | None
    inverse_r: int | None = None
    z_base: int | None = None
    c: int | None = None
    anchor: int | None = None
    inverse_anchor: int | None = None
    root_factor: int | None = None

    def evaluate(self, target: Point) -> tuple[dict, dict[str, int]]:
        curve = Curve(self.model["p"], self.model["a"], self.model["b"])
        if self.setup_reason:
            curve.counter.tick("exception_undefined_setup")
            return result("UNDEFINED", reason=self.setup_reason, anchor=self.anchor), curve.counter.snapshot()
        if not curve.contains(target):
            raise ValueError("target is not a canonical point on curve")
        if target is None:
            curve.counter.tick("exception_identity_predicate")
            return result("BIT", bit=0, z=0, anchor=self.anchor), curve.counter.snapshot()
        if self.arm["kind"] == "wrong_root":
            # This control is an anchored field-root circuit, not a character.
            x, y = target
            f_x = curve.f.add(curve.f.add(curve.f.mul(curve.f.square(x), x), curve.f.mul(curve.a, x)), curve.b)
            sigma = curve.f.mul(self.root_factor, curve.f.power(f_x, (curve.p + 1) // 4))
            if curve.f.equal(y, sigma):
                bit = 0
            elif curve.f.equal(y, curve.f.neg(sigma)):
                bit = 1
            else:
                return result("UNDEFINED", reason="ROOT_SIGN_MISMATCH", anchor=self.anchor, root=sigma), curve.counter.snapshot()
            return result("BIT", bit=bit, anchor=self.anchor, root=sigma), curve.counter.snapshot()
        z = normalized_miller_coefficient(curve, target, self.model["r"], self.inverse_r)
        x, y = target
        a, b = self.arm["alpha"], self.arm["beta"]
        offset = curve.f.mul(self.c, curve.f.sub(x, self.base[0]))
        bracket = curve.f.add(a, curve.f.mul(b, offset))
        g = curve.f.add(z, curve.f.mul(curve.f.mul(self.c, y), bracket))
        if curve.f.equal(g, 0):
            curve.counter.tick("exception_zero_numerator")
            return result("UNDEFINED", reason="ZERO_NUMERATOR", z=z, g=g, anchor=self.anchor), curve.counter.snapshot()
        normalized = curve.f.mul(g, self.inverse_anchor)
        character = curve.f.power(normalized, (curve.p - 1) // 2)
        if character not in (1, curve.p - 1):
            raise ValueError("non-Legendre character in declared prime field")
        return result("BIT", bit=0 if character == 1 else 1, z=z, g=g,
                      anchor=self.anchor, normalized=normalized), curve.counter.snapshot()


def prepare(model: dict, base: Point, arm: dict) -> Prepared:
    p, a, b, r = (model[key] for key in ("p", "a", "b", "r"))
    curve = Curve(p, a, b)
    common = dict(model=dict(model), base=base, arm=dict(arm))

    def finish(reason: str | None = None, **values: object) -> Prepared:
        return Prepared(**common, setup_counts=curve.counter.snapshot(), setup_reason=reason, **values)

    if p % 4 != 3 or r <= 2 or r % 2 == 0 or r == p:
        return finish("DOMAIN_UNSUPPORTED")
    if base is None or not curve.contains(base):
        raise ValueError("base must be a nonidentity canonical point on curve")
    if curve.f.equal(base[1], 0):
        return finish("ZERO_BASE_Y")
    inverse_r = curve.f.inverse(r % p)
    z_base = normalized_miller_coefficient(curve, base, r, inverse_r)
    if arm["kind"] == "wrong_root":
        x, y = base
        f_x = curve.f.add(curve.f.add(curve.f.mul(curve.f.square(x), x), curve.f.mul(a, x)), b)
        anchor = curve.f.power(f_x, (p + 1) // 4)
        if curve.f.equal(anchor, 0):
            return finish("ZERO_ANCHOR", inverse_r=inverse_r, z_base=z_base, anchor=anchor)
        factor = curve.f.mul(y, curve.f.inverse(anchor))
        return finish(inverse_r=inverse_r, z_base=z_base, anchor=anchor, root_factor=factor)
    if curve.f.equal(z_base, 0):
        return finish("ZERO_BASE_Z", inverse_r=inverse_r, z_base=z_base)
    c = curve.f.mul(z_base, curve.f.inverse(base[1]))
    anchor = curve.f.mul(curve.f.add(1, arm["alpha"]), z_base)
    if curve.f.equal(anchor, 0):
        return finish("ZERO_ANCHOR", inverse_r=inverse_r, z_base=z_base, c=c, anchor=anchor)
    return finish(inverse_r=inverse_r, z_base=z_base, c=c, anchor=anchor,
                  inverse_anchor=curve.f.inverse(anchor))


def conditional_recover(prepared: Prepared, target: Point) -> dict:
    """O(log r) predicate calls; return a scalar only after public verification.

    Correct recovery for all targets is conditional on all-target half ordering,
    which is the experiment's question. No fallback and no discrete-log search.
    """
    model, r = prepared.model, prepared.model["r"]
    curve = Curve(model["p"], model["a"], model["b"])
    if not curve.contains(target):
        raise ValueError("invalid recovery target")
    length, value, current = r.bit_length() + 1, 0, target
    calls, evaluation_counts, trace = 0, Counter(), []
    for index in range(length):
        answer, counts = prepared.evaluate(current)
        calls += 1
        trace.append({"target": point_json(current), "answer": answer, "counters": counts})
        for name, amount in counts.items():
            evaluation_counts.tick(name, amount)
        if answer["status"] != "BIT":
            return {"status": "UNDEFINED", "scalar": None, "reason": answer["reason"],
                    "predicate_calls": calls, "evaluate_counts": evaluation_counts.snapshot(),
                    "predicate_evaluations": calls, "retained_bit_reads": 0,
                    "oracle_table_verifier_only": False, "predicate_trace": trace,
                    "reduction_counts": curve.counter.snapshot()}
        curve.counter.tick("recovery_scalar_digit_update")
        value = 2 * value + answer["bit"]
        if index + 1 < length:
            current = curve.add(current, current)
    denominator = 1 << length
    curve.counter.tick("recovery_scalar_interval_round")
    scalar = (r * value + denominator - 1) // denominator
    recovered = scalar < r and curve.equal(curve.multiply(prepared.base, scalar), target)
    return {"status": "RECOVERED" if recovered else "REJECTED_FINAL_VERIFICATION",
            "scalar": scalar if recovered else None, "candidate_scalar": scalar,
            "reason": None if recovered else "FINAL_VERIFICATION_FAILED",
            "predicate_calls": calls, "evaluate_counts": evaluation_counts.snapshot(),
            "predicate_evaluations": calls, "retained_bit_reads": 0,
            "oracle_table_verifier_only": False, "predicate_trace": trace,
            "reduction_counts": curve.counter.snapshot()}
