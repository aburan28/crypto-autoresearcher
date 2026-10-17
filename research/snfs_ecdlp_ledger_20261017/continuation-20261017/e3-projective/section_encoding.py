"""Prospective E3 coefficient encoding, not a scientific experiment launcher.

Short Weierstrass models in characteristic > 3.  D is a projective encoding
degree, never a canonical height or a rank/coverage certificate.  A union of
primitive charts for D <= D_max is needed for a bounded search.  The zero
section is deliberately outside the monic-Z charts.
"""
from dataclasses import dataclass
from sage.all import GF, Integer, PolynomialRing


def model(p, a, b, chi):
    if not Integer(p).is_prime() or p <= 3:
        raise ValueError("An actual prime greater than 3 is required")
    if not isinstance(chi, int) or chi < 0:
        raise ValueError("chi must be a nonnegative supplied model parameter")
    ring = PolynomialRing(GF(p), "t")
    a, b = ring(a), ring(b)
    if a.degree() > 4 * chi or b.degree() > 6 * chi:
        raise ValueError("Model coefficient degrees exceed the supplied bounds")
    delta = -16 * (4 * a**3 + 27 * b**2)
    if not delta:
        raise ValueError("The generic fibre is singular")
    return ring, a, b, delta


def normalize(x, y, z):
    """Remove constant weighted scaling only; never cancel polynomial factors."""
    if not z:
        raise ValueError("The zero section is not an affine monic-Z chart")
    unit = 1 / z.leading_coefficient()
    return x * unit**2, y * unit**3, z * unit


def check_section(p, a, b, chi, D, x, y, z):
    ring, a, b, _ = model(p, a, b, chi)
    if not isinstance(D, int) or D < 0:
        raise ValueError("D must be nonnegative")
    x, y, z = normalize(ring(x), ring(y), ring(z))
    nx, ny = 2 * (D + chi), 3 * (D + chi)
    if x.degree() > nx or y.degree() > ny or z.degree() > D:
        raise ValueError("Section exceeds the encoding degree")
    if y**2 != x**3 + a * x * z**4 + b * z**6:
        raise ValueError("Section equation fails")
    if x.gcd(z).degree() != 0:
        raise ValueError("Nonprimitive finite denominator")
    if z.degree() < D and (not x[nx] or not y[ny]):
        raise ValueError("Nonprimitive projective chart at base infinity")
    return x, y, z


def specialize(p, a, b, chi, D, x, y, z, parameter):
    ring, a, b, delta = model(p, a, b, chi)
    x, y, z = check_section(p, a, b, chi, D, x, y, z)
    if parameter == "infinity":
        av, bv = a[4 * chi], b[6 * chi]
        if not -16 * (4 * av**3 + 27 * bv**2):
            raise ValueError("Target fibre at infinity is not smooth")
        xv, yv, zv = x[2 * (D + chi)], y[3 * (D + chi)], z[D]
    else:
        t0 = ring.base_ring()(parameter)
        if not delta(t0):
            raise ValueError("Target fibre is not smooth")
        xv, yv, zv = x(t0), y(t0), z(t0)
    return "O" if not zv else (xv / zv**2, yv / zv**3)


@dataclass
class CoefficientSystem:
    ring: object
    equations: list
    primary_names: list
    auxiliary_names: list
    metadata: dict
    x: object
    y: object
    z: object

    def accepts(self, assignment):
        if set(assignment) != set(self.ring.variable_names()):
            raise ValueError("Supply every coefficient and saturation witness exactly")
        values = [self.ring.base_ring()(assignment[n]) for n in self.ring.variable_names()]
        return all(eq(*values) == 0 for eq in self.equations)


def coefficient_system(p, a, b, chi, D, denominator_degree, target_parameter,
                       target_point):
    """Build exact coefficient equations, Bezout saturation and target chart.

    Input is the surface and target only. No generator or planted section is
    consumed. This constructs equations; it neither solves nor times them.
    """
    base, a, b, delta = model(p, a, b, chi)
    e = denominator_degree
    if not isinstance(D, int) or D < 0 or not isinstance(e, int) or not 0 <= e <= D:
        raise ValueError("Require integers 0 <= denominator_degree <= D")
    nx, ny = 2 * (D + chi), 3 * (D + chi)
    primary = ([f"x{i}" for i in range(nx + 1)] +
               [f"y{i}" for i in range(ny + 1)] + [f"z{i}" for i in range(e)])
    auxiliary = ([f"u{i}" for i in range(e)] + [f"v{i}" for i in range(nx)]) if e else []
    if e < D:
        auxiliary.append("infinity_unit")
    if target_point != "O" and target_parameter != "infinity" and e:
        auxiliary.append("target_unit")
    coeff = PolynomialRing(base.base_ring(), primary + auxiliary, order="degrevlex")
    variables = dict(zip(coeff.variable_names(), coeff.gens()))
    polynomials = PolynomialRing(coeff, "t")
    t = polynomials.gen()
    x = sum((variables[f"x{i}"] * t**i for i in range(nx + 1)), polynomials.zero())
    y = sum((variables[f"y{i}"] * t**i for i in range(ny + 1)), polynomials.zero())
    z = t**e + sum((variables[f"z{i}"] * t**i for i in range(e)), polynomials.zero())
    equations = list(y**2 - x**3 - polynomials(a) * x * z**4 - polynomials(b) * z**6)
    if e:
        u = sum(variables[f"u{i}"] * t**i for i in range(e))
        v = sum(variables[f"v{i}"] * t**i for i in range(nx))
        equations.extend(list(x * u + z * v - 1))
    if e < D:
        equations.append(variables["infinity_unit"] * x[nx] - 1)
    if target_parameter == "infinity":
        av, bv = a[4 * chi], b[6 * chi]
        xv, yv, zv = x[nx], y[ny], z[D]
        if target_point == "O" and e == D:
            raise ValueError("This denominator chart cannot specialize to O at infinity")
        if target_point != "O" and e < D:
            raise ValueError("This denominator chart specializes to O at infinity")
    else:
        t0 = base.base_ring()(target_parameter)
        av, bv, xv, yv, zv = a(t0), b(t0), x(t0), y(t0), z(t0)
    if not -16 * (4 * av**3 + 27 * bv**2):
        raise ValueError("Target fibre is not smooth")
    if target_point == "O":
        equations.append(zv)
    else:
        rx, ry = map(base.base_ring(), target_point)
        if ry**2 != rx**3 + av * rx + bv:
            raise ValueError("Target point is not on the specified smooth fibre")
        equations.extend([xv - rx * zv**2, yv - ry * zv**3])
        if "target_unit" in variables:
            equations.append(variables["target_unit"] * zv - 1)
    equations = [coeff(eq) for eq in equations if eq != 0]
    metadata = dict(p=int(p), chi=chi, D=D, denominator_degree=e,
                    degree_bounds=dict(X=nx, Y=ny, Z=e),
                    primary_unknowns=len(primary), saturation_unknowns=len(auxiliary),
                    coefficient_equations=len(equations),
                    equation_total_degrees=[int(eq.total_degree()) for eq in equations],
                    target_parameter=str(target_parameter), target_point=str(target_point),
                    height_conversion_certified=False, model_minimality_certified=False,
                    rank_coverage_or_complexity_claim=False, scientific_trials_launched=0)
    return CoefficientSystem(coeff, equations, primary, auxiliary, metadata, x, y, z)


def fixture_assignment(system, x, y, z, target_parameter):
    """Construct witnesses for known fixture data; never input to a blind solver."""
    values = {}
    for prefix, poly in (("x", x), ("y", y), ("z", z)):
        for name in system.primary_names:
            if name.startswith(prefix):
                values[name] = poly[int(name[1:])]
    if z.degree():
        g, u, v = x.xgcd(z)
        if g != 1:
            raise ValueError("Fixture is not primitive")
        for name in system.auxiliary_names:
            if name[0] in ("u", "v") and name[1:].isdigit():
                values[name] = (u if name[0] == "u" else v)[int(name[1:])]
    if "infinity_unit" in system.auxiliary_names:
        values["infinity_unit"] = 1 / x[system.metadata["degree_bounds"]["X"]]
    if "target_unit" in system.auxiliary_names:
        values["target_unit"] = 1 / z(z.base_ring()(target_parameter))
    return values
