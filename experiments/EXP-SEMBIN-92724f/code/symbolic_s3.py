#!/usr/bin/env python3
"""Arm C of EXP-SEMBIN-92724f: the SYMBOLIC F_2-degree expansion of
S_3(u, v_1 + y_1, v_2 + y_2) and of y_1 S_3(u, v_1 + y_1, v_2 + y_2).

WHAT "F_2-DEGREE" MEANS HERE, AND WHY IT IS NOT A SOLVING DEGREE. Over
F_{2^n}, the map x -> x^{2^a} is F_2-linear on coordinates, so a monomial
x^e has coordinate functions of total degree exactly the Hamming weight
w(e) of its exponent, and a monomial u^a y_1^b y_2^c has coordinate
functions of total degree at most w(a) + w(b) + w(c). This is a property of
the written-down polynomial. It is NOT a degree of regularity, a first-fall
degree, or a d_F4, and this run measures none of those.

REPRESENTATION. A polynomial in F_2[v_1, v_2][u, y_1, y_2] is a dict from a
variable exponent triple (a, b, c) to a coefficient, and a coefficient is a
set of (p, q) pairs meaning the F_2-sum of v_1^p v_2^q. v_1 and v_2 are FORMAL
here -- the expansion is symbolic in the coset representatives, so the verdict
covers every choice of them at once, including adversarial ones -- and the
concrete-field cross-check in the driver instantiates them and recomputes the
exact Boolean degree by Weil descent through an independent code path.
"""
from __future__ import annotations

from dataclasses import dataclass


def _w(e: int) -> int:
    return bin(e).count("1")


@dataclass
class SymPoly:
    """sum over (a,b,c) of coeff(a,b,c) * u^a y_1^b y_2^c, coeff in F_2[v1,v2]."""

    terms: dict  # (a,b,c) -> frozenset of (p,q); empty set means zero

    @classmethod
    def zero(cls) -> "SymPoly":
        return cls({})

    @classmethod
    def one(cls) -> "SymPoly":
        return cls({(0, 0, 0): {(0, 0)}})

    @classmethod
    def var(cls, which: str) -> "SymPoly":
        idx = {"u": (1, 0, 0), "y1": (0, 1, 0), "y2": (0, 0, 1)}[which]
        return cls({idx: {(0, 0)}})

    @classmethod
    def v(cls, which: int) -> "SymPoly":
        return cls({(0, 0, 0): {(1, 0) if which == 1 else (0, 1)}})

    @classmethod
    def symbol(cls, name: str) -> "SymPoly":
        """A formal constant B, carried as v_1^0 v_2^0 * (marker exponent)."""
        if name != "B":
            raise ValueError("only B is supported as an extra constant")
        return cls({(0, 0, 0): {("B", "B")}})

    def _norm(self) -> "SymPoly":
        return SymPoly({k: set(vv) for k, vv in self.terms.items() if vv})

    def __add__(self, other: "SymPoly") -> "SymPoly":
        out = {k: set(v) for k, v in self.terms.items()}
        for k, v in other.terms.items():
            out[k] = out.get(k, set()) ^ set(v)
        return SymPoly(out)._norm()

    def __mul__(self, other: "SymPoly") -> "SymPoly":
        out: dict = {}
        for k1, c1 in self.terms.items():
            for k2, c2 in other.terms.items():
                key = (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2])
                acc = out.setdefault(key, set())
                for p1 in c1:
                    for p2 in c2:
                        if "B" in (p1[0], p2[0]):
                            prod = ("B", "B")
                        else:
                            prod = (p1[0] + p2[0], p1[1] + p2[1])
                        acc ^= {prod}
        return SymPoly(out)._norm()

    def square(self) -> "SymPoly":
        """Characteristic 2: (sum t_i)^2 = sum t_i^2, exponents doubled."""
        out: dict = {}
        for (a, b, c), coeff in self.terms.items():
            key = (2 * a, 2 * b, 2 * c)
            acc = out.setdefault(key, set())
            for p in coeff:
                sq = ("B", "B") if p[0] == "B" else (2 * p[0], 2 * p[1])
                acc ^= {sq}
        return SymPoly(out)._norm()

    # -- reading off the F_2-degree ---------------------------------------
    def f2_degree_bound(self) -> int:
        return max((_w(a) + _w(b) + _w(c) for (a, b, c) in self.terms),
                   default=-1)

    def top_monomials(self) -> list[dict]:
        d = self.f2_degree_bound()
        out = []
        for (a, b, c), coeff in sorted(self.terms.items()):
            if _w(a) + _w(b) + _w(c) == d:
                out.append({"monomial": _render_monomial(a, b, c),
                            "exponents": [a, b, c],
                            "hamming_weights": [_w(a), _w(b), _w(c)],
                            "f2_degree": d,
                            "coefficient": _render_coeff(coeff),
                            "coefficient_is_the_constant_1":
                                set(coeff) == {(0, 0)}})
        return out

    def render(self) -> str:
        parts = []
        for (a, b, c), coeff in sorted(
                self.terms.items(),
                key=lambda kv: (-(_w(kv[0][0]) + _w(kv[0][1]) + _w(kv[0][2])),
                                kv[0])):
            mono = _render_monomial(a, b, c)
            co = _render_coeff(coeff)
            if len(coeff) > 1:
                co = f"({co})"
            deg = _w(a) + _w(b) + _w(c)
            term = mono if co == "1" else (co if mono == "1" else f"{co}*{mono}")
            parts.append(f"  {term:<34s} [F_2-degree {deg}"
                         f" = w({a})+w({b})+w({c})]")
        return "\n".join(parts)

    def degree_profile(self) -> dict:
        prof: dict = {}
        for (a, b, c) in self.terms:
            d = _w(a) + _w(b) + _w(c)
            prof[d] = prof.get(d, 0) + 1
        return dict(sorted(prof.items()))


def _render_monomial(a: int, b: int, c: int) -> str:
    bits = []
    for name, e in (("u", a), ("y1", b), ("y2", c)):
        if e == 1:
            bits.append(name)
        elif e > 1:
            bits.append(f"{name}^{e}")
    return "*".join(bits) if bits else "1"


def _render_coeff(coeff) -> str:
    terms = []
    for p, q in sorted(coeff, key=lambda x: (str(x[0]), str(x[1]))):
        if p == "B":
            terms.append("B")
            continue
        bits = []
        if p == 1:
            bits.append("v1")
        elif p > 1:
            bits.append(f"v1^{p}")
        if q == 1:
            bits.append("v2")
        elif q > 1:
            bits.append(f"v2^{q}")
        terms.append("*".join(bits) if bits else "1")
    return " + ".join(terms) if terms else "0"


# ---------------------------------------------------------------------------
# The two expansions the contract names
# ---------------------------------------------------------------------------
def s3_symbolic(typed: bool = True, with_B: bool = True) -> SymPoly:
    """S_3(u, v_1 + y_1, v_2 + y_2) = ((x1x2+x1x3+x2x3))^2 + x1x2x3 + B."""
    u = SymPoly.var("u")
    x2 = SymPoly.var("y1") + (SymPoly.v(1) if typed else SymPoly.zero())
    x3 = SymPoly.var("y2") + (SymPoly.v(2) if typed else SymPoly.zero())
    inner = (u * x2) + (u * x3) + (x2 * x3)
    out = inner.square() + (u * x2 * x3)
    if with_B:
        out = out + SymPoly.symbol("B")
    return out


def y1_s3_symbolic(typed: bool = True, with_B: bool = True) -> SymPoly:
    """y_1 * S_3(u, v_1 + y_1, v_2 + y_2), Semaev's section 4.5 second fact."""
    return SymPoly.var("y1") * s3_symbolic(typed=typed, with_B=with_B)


def x1_s3_untyped_symbolic(with_B: bool = True) -> SymPoly:
    """x_1 S_3(x_1, x_2, x_3) with the roles Semaev uses, for the baseline.

    Here the multiplied variable is the FIRST argument, as in the paper:
    deg_{F_2} x_1 S_3(x_1, x_2, x_3) = 3 despite deg x_1 + deg S_3 = 4.
    """
    u = SymPoly.var("u")
    return u * s3_symbolic(typed=False, with_B=with_B)


def naive_degree_bound(poly_degree: int, multiplier_degree: int = 1) -> int:
    """The bound the argument must beat: deg(fg) <= deg f + deg g."""
    return poly_degree + multiplier_degree


def expansion_report() -> dict:
    """Every expansion, its degree profile, its top monomials and the verdict."""
    items = {
        "S3_untyped_u_y1_y2": s3_symbolic(typed=False),
        "S3_typed_u_v1_plus_y1_v2_plus_y2": s3_symbolic(typed=True),
        "x1_S3_untyped": x1_s3_untyped_symbolic(),
        "y1_S3_typed": y1_s3_symbolic(typed=True),
        "y1_S3_untyped": y1_s3_symbolic(typed=False),
    }
    out = {}
    for name, poly in items.items():
        top = poly.top_monomials()
        out[name] = {
            "f2_degree_bound_from_exponent_weights": poly.f2_degree_bound(),
            "degree_profile_monomial_counts": poly.degree_profile(),
            "number_of_monomials": len(poly.terms),
            "top_degree_monomials": top,
            "some_top_monomial_has_constant_coefficient_1":
                any(t["coefficient_is_the_constant_1"] for t in top),
            "written_out": poly.render(),
        }
    out["naive_product_bound_for_y1_S3"] = naive_degree_bound(
        items["S3_typed_u_v1_plus_y1_v2_plus_y2"].f2_degree_bound(), 1)
    return out
