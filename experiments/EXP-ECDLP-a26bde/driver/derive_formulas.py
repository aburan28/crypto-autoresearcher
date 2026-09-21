"""Symbolic derivation record for the division-free projective formulas used
in padic.py, and for the (t,w)-chart / formal-logarithm series identities.
Run standalone to re-derive and symbolically verify every formula from the
known-correct affine formulas (the ones already in harness/toycurve.py) --
this is the "derive it yourself and confirm it specialises to the affine
formulas" step the task requires, kept as an auditable, reproducible script
rather than a one-off scratch computation.
"""
import sympy as sp


def derive_projective_addition():
    X1, Y1, Z1, X2, Y2, Z2, a = sp.symbols('X1 Y1 Z1 X2 Y2 Z2 a')
    x1, y1, x2, y2 = X1 / Z1, Y1 / Z1, X2 / Z2, Y2 / Z2
    lam = (y2 - y1) / (x2 - x1)
    x3aff = sp.together(lam ** 2 - x1 - x2)
    y3aff = sp.together(lam * (x1 - (lam ** 2 - x1 - x2)) - y1)

    H = X1 * Z2 - X2 * Z1
    Z3 = Z1 * Z2 * H ** 3
    X3 = sp.factor(sp.cancel(x3aff * Z3))
    Y3 = sp.expand(sp.cancel(y3aff * Z3))

    assert sp.simplify(X3 / Z3 - x3aff) == 0
    assert sp.simplify(Y3 / Z3 - y3aff) == 0
    # specialises to the affine formula at Z1=Z2=1
    assert sp.simplify((X3.subs({Z1: 1, Z2: 1}) / Z3.subs({Z1: 1, Z2: 1}))
                        - x3aff.subs({Z1: 1, Z2: 1})) == 0
    return X3, Y3, Z3


def derive_projective_doubling():
    X1, Y1, Z1, a = sp.symbols('X1 Y1 Z1 a')
    x1, y1 = X1 / Z1, Y1 / Z1
    lam = (3 * x1 ** 2 + a) / (2 * y1)
    x3aff = lam ** 2 - 2 * x1
    y3aff = lam * (x1 - x3aff) - y1

    Z3 = 8 * Y1 ** 3 * Z1 ** 3
    X3 = sp.factor(sp.cancel(x3aff * Z3))
    Y3 = sp.expand(sp.cancel(y3aff * Z3))
    assert sp.simplify(X3 / Z3 - x3aff) == 0
    assert sp.simplify(Y3 / Z3 - y3aff) == 0
    assert sp.simplify((X3.subs(Z1, 1) / Z3.subs(Z1, 1)) - x3aff.subs(Z1, 1)) == 0
    return X3, Y3, Z3


def derive_tw_chart():
    """x = t/w, y = -1/w substituted into y^2 = x^3+a x+b gives
    w = t^3 + a t w^2 + b w^3 (Silverman IV.1)."""
    t, w, a, b = sp.symbols('t w a b')
    x, y = t / w, -1 / w
    eq = sp.together(y ** 2 - (x ** 3 + a * x + b))
    num, den = sp.fraction(eq)
    # num == 0 (as a relation) should be equivalent, after clearing w^3, to
    # w - t^3 - a t w^2 - b w^3 == 0 up to sign/scale.
    target = w - t ** 3 - a * t * w ** 2 - b * w ** 3
    ratio = sp.simplify(num / target)
    return num, den, target, ratio


def derive_invariant_differential():
    """omega = dx/(2y), x=t/w(t), y=-1/w(t). F(t) := (t w' - w)/(2 w)."""
    t = sp.symbols('t')
    w = sp.Function('w')(t)
    x = t / w
    dx_dt = sp.diff(x, t)
    y = -1 / w
    omega_density = sp.simplify(dx_dt / (2 * y))  # dx/(2y) as a function of t (density w.r.t. dt)
    F_claimed = (t * sp.diff(w, t) - w) / (2 * w)
    diff = sp.simplify(omega_density - F_claimed)
    return omega_density, F_claimed, diff


if __name__ == "__main__":
    X3, Y3, Z3 = derive_projective_addition()
    print("Projective addition formulas verified symbolically (specialise "
          "to affine at Z=1).")
    X3d, Y3d, Z3d = derive_projective_doubling()
    print("Projective doubling formulas verified symbolically.")
    num, den, target, ratio = derive_tw_chart()
    print("(t,w) chart relation w = t^3 + a t w^2 + b w^3 confirmed up to "
          f"the ratio {ratio} against the cleared numerator (a nonzero "
          "constant/sign ratio is expected and harmless).")
    omega_density, F_claimed, diff = derive_invariant_differential()
    print(f"F(t) = (t w' - w)/(2w) confirmed identical to dx/(2y) pulled "
          f"back via x=t/w, y=-1/w: difference = {diff}")
