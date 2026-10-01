#!/usr/bin/env python3
"""Arm B of EXP-SEMBIN-92724f: Weil descent of Semaev's chained system (5),
typed and untyped, compared COEFFICIENT-WISE.

REPRESENTATION. A `FieldPoly` is a polynomial map (F_2)^N -> F_{2^n}: a dict
from a monomial in the Boolean variables (packed as a bitmask, since Boolean
variables are idempotent so a monomial is just its support) to a coefficient in
F_{2^n} (a packed int). Addition xors coefficients; multiplication ors supports
and multiplies coefficients in the field.

SQUARING IS LINEAR AND THAT IS THE WHOLE POINT. In characteristic 2,
(sum_M c_M M)^2 = sum_M c_M^2 M^2 = sum_M c_M^2 M, because the cross terms
appear twice and M^2 = M for a Boolean monomial. So squaring a FieldPoly keeps
its support and squares its coefficients, and a squared product of two
variables stays F_2-degree 2 rather than becoming 4. That is exactly the fact
Semaev's section 4.5 argument turns on, and it is implemented here as the
identity it is, then cross-checked against a general multiplication
(`square_via_multiplication`) so the shortcut cannot silently be wrong.

WEIL DESCENT. `coordinates()` reads off the n Boolean coordinate functions of a
FieldPoly by taking bit i of every coefficient. An equation S_3(...) = 0 over
F_{2^n} becomes n Boolean equations; the chain (5) has t-1 such equations, hence
n(t-1) Boolean equations in n(t-2) + kt Boolean variables.

NO DEGREE OF REGULARITY, FIRST-FALL DEGREE OR d_F4 IS COMPUTED HERE. The only
degree in this file is the total degree of an explicitly constructed Boolean
polynomial, which is a property of the written-down system and not a property
of any Groebner computation.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldPoly:
    """A polynomial in Boolean variables with coefficients in F_{2^n}."""

    field: object
    terms: dict  # bitmask -> field element (never 0)

    @classmethod
    def zero(cls, field) -> "FieldPoly":
        return cls(field, {})

    @classmethod
    def constant(cls, field, c: int) -> "FieldPoly":
        return cls(field, {0: c} if c else {})

    @classmethod
    def linear_form(cls, field, basis: list[int], var_ids: list[int],
                    constant: int = 0) -> "FieldPoly":
        """constant + sum_j basis[j] * y_{var_ids[j]}, the descent of a field
        variable restricted to the span of `basis` (all of F_{2^n} when the
        basis is 1, alpha, ..., alpha^{n-1})."""
        if len(basis) != len(var_ids):
            raise ValueError("basis and variable ids must have equal length")
        terms: dict = {}
        if constant:
            terms[0] = constant
        for b, v in zip(basis, var_ids):
            mask = 1 << v
            terms[mask] = terms.get(mask, 0) ^ b
            if terms[mask] == 0:
                del terms[mask]
        return cls(field, terms)

    # -- ring operations ---------------------------------------------------
    def __add__(self, other: "FieldPoly") -> "FieldPoly":
        out = dict(self.terms)
        for mask, c in other.terms.items():
            v = out.get(mask, 0) ^ c
            if v:
                out[mask] = v
            else:
                out.pop(mask, None)
        return FieldPoly(self.field, out)

    def __mul__(self, other: "FieldPoly") -> "FieldPoly":
        f = self.field
        out: dict = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                mask = m1 | m2
                v = out.get(mask, 0) ^ f.mul(c1, c2)
                if v:
                    out[mask] = v
                else:
                    out.pop(mask, None)
        return FieldPoly(f, out)

    def square(self) -> "FieldPoly":
        f = self.field
        return FieldPoly(f, {m: f.sqr(c) for m, c in self.terms.items()})

    def square_via_multiplication(self) -> "FieldPoly":
        return self * self

    # -- inspection --------------------------------------------------------
    def degree(self) -> int:
        return max((bin(m).count("1") for m in self.terms), default=-1)

    def coordinates(self, n: int) -> list[set]:
        """The n Boolean coordinate functions, each a set of monomial masks."""
        return [{m for m, c in self.terms.items() if (c >> i) & 1}
                for i in range(n)]

    def variables(self) -> set:
        out: set = set()
        for m in self.terms:
            while m:
                low = m & -m
                out.add(low.bit_length() - 1)
                m ^= low
        return out


def S3(x1: FieldPoly, x2: FieldPoly, x3: FieldPoly, B: int) -> FieldPoly:
    """Semaev's eq. (14): (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B.

    Built with the characteristic-2 identity that the square of a sum is the
    sum of squares, which is what makes the quadratic part F_2-degree 2.
    """
    f = x1.field
    inner = (x1 * x2) + (x1 * x3) + (x2 * x3)
    return inner.square() + (x1 * x2 * x3) + FieldPoly.constant(f, B)


def S3_via_general_squaring(x1: FieldPoly, x2: FieldPoly, x3: FieldPoly,
                            B: int) -> FieldPoly:
    """Same polynomial with the square taken by general multiplication."""
    f = x1.field
    inner = (x1 * x2) + (x1 * x3) + (x2 * x3)
    return inner.square_via_multiplication() + (x1 * x2 * x3) \
        + FieldPoly.constant(f, B)


# ---------------------------------------------------------------------------
# The chained system (5)
# ---------------------------------------------------------------------------
def build_chain(field, n: int, t: int, k: int, vbasis: list[int], B: int,
                RX: int, reps: list[int] | None = None) -> dict:
    """Semaev eq. (5), descended to Boolean coordinates.

        S_3(u_1, x_1, x_2) = 0
        S_3(u_i, u_{i+1}, x_{i+2}) = 0,   1 <= i <= t-3
        S_3(u_{t-2}, x_t, R_X) = 0

    with x_i in V (untyped) or x_i in V + v_i (typed, `reps` given), and
    u_j ranging over F_{2^n}. For t = 2 the system is the single equation
    S_3(x_1, x_2, R_X) = 0.

    Returns the field-level polynomials, the Boolean coordinate equations and
    the count/degree data the contract compares coefficient-wise.
    """
    if t < 2:
        raise ValueError("t must be at least 2; eq. (5) has t-1 equations")
    full_basis = [1 << i for i in range(n)]
    next_id = 0
    xs = []
    for i in range(t):
        ids = list(range(next_id, next_id + k))
        next_id += k
        const = reps[i] if reps is not None else 0
        xs.append(FieldPoly.linear_form(field, vbasis, ids, const))
    us = []
    for _ in range(max(0, t - 2)):
        ids = list(range(next_id, next_id + n))
        next_id += n
        us.append(FieldPoly.linear_form(field, full_basis, ids, 0))
    rx = FieldPoly.constant(field, RX)

    eqs: list[FieldPoly] = []
    if t == 2:
        eqs.append(S3(xs[0], xs[1], rx, B))
    else:
        eqs.append(S3(us[0], xs[0], xs[1], B))
        for i in range(1, t - 2):
            eqs.append(S3(us[i - 1], us[i], xs[i + 1], B))
        eqs.append(S3(us[t - 3], xs[t - 1], rx, B))

    boolean_eqs = []
    for e in eqs:
        boolean_eqs.extend(e.coordinates(n))

    per_eq = []
    for idx, supp in enumerate(boolean_eqs):
        by_deg: dict = {}
        for mask in supp:
            d = bin(mask).count("1")
            by_deg[d] = by_deg.get(d, 0) + 1
        per_eq.append({
            "index": idx,
            "monomials": len(supp),
            "max_degree": max((bin(m).count("1") for m in supp), default=-1),
            "monomials_by_degree": dict(sorted(by_deg.items())),
        })

    return {
        "n": n, "t": t, "k": k, "typed": reps is not None,
        "declared_equation_count_n_times_t_minus_1": n * (t - 1),
        "actual_boolean_equation_count": len(boolean_eqs),
        "declared_variable_count_n_t_minus_2_plus_kt": n * (t - 2) + k * t,
        "actual_variable_slots_allocated": next_id,
        "variables_actually_occurring":
            sorted(set().union(*[e.variables() for e in eqs])) if eqs else [],
        "field_level_max_degree": max(e.degree() for e in eqs),
        "boolean_max_degree": max(p["max_degree"] for p in per_eq),
        "per_equation": per_eq,
        "boolean_supports": boolean_eqs,
        "field_polys": eqs,
    }


def compare_builders(untyped: dict, typed: dict) -> dict:
    """Coefficient-wise comparison of the two descended systems.

    Reported separately, because they answer different questions:

      * counts and degrees -- whether typing is FREE (the zero-cost clause);
      * the degree-3 support -- whether the cubic part is literally identical,
        which it must be if x_i = v_i + y_i is only an affine change of
        variables (the top-degree coefficients cannot see the constant);
      * the largest per-equation per-degree monomial-count discrepancy, which
        is the number the contract asks for instead of a pass rate.
    """
    same_eq_count = (untyped["actual_boolean_equation_count"]
                     == typed["actual_boolean_equation_count"])
    same_var_count = (untyped["actual_variable_slots_allocated"]
                      == typed["actual_variable_slots_allocated"])
    same_max_degree = untyped["boolean_max_degree"] == typed["boolean_max_degree"]

    worst = {"equation_index": None, "degree": None, "untyped": None,
             "typed": None, "abs_difference": 0}
    degree3_identical = True
    degree3_mismatch_examples = []
    per_degree_diff_counts: dict = {}
    for eu, et in zip(untyped["per_equation"], typed["per_equation"]):
        degs = set(eu["monomials_by_degree"]) | set(et["monomials_by_degree"])
        for d in degs:
            a = eu["monomials_by_degree"].get(d, 0)
            b = et["monomials_by_degree"].get(d, 0)
            if a != b:
                per_degree_diff_counts[d] = per_degree_diff_counts.get(d, 0) + 1
            if abs(a - b) > worst["abs_difference"]:
                worst = {"equation_index": eu["index"], "degree": d,
                         "untyped": a, "typed": b, "abs_difference": abs(a - b)}
    for i, (su, st) in enumerate(zip(untyped["boolean_supports"],
                                     typed["boolean_supports"])):
        cu = {m for m in su if bin(m).count("1") == 3}
        ct = {m for m in st if bin(m).count("1") == 3}
        if cu != ct:
            degree3_identical = False
            if len(degree3_mismatch_examples) < 5:
                degree3_mismatch_examples.append(
                    {"equation_index": i,
                     "only_untyped": sorted(cu - ct)[:5],
                     "only_typed": sorted(ct - cu)[:5]})
    return {
        "equation_count_identical": same_eq_count,
        "variable_count_identical": same_var_count,
        "max_boolean_degree_identical": same_max_degree,
        "untyped_max_boolean_degree": untyped["boolean_max_degree"],
        "typed_max_boolean_degree": typed["boolean_max_degree"],
        "degree3_support_identical": degree3_identical,
        "degree3_mismatch_examples": degree3_mismatch_examples,
        "equations_with_a_per_degree_count_difference": per_degree_diff_counts,
        "largest_per_degree_monomial_count_discrepancy": worst,
        "zero_cost_clause_holds_on_counts_and_degree":
            same_eq_count and same_var_count and same_max_degree,
    }
