"""The forced-arity constraint, and which (curve, m) cells can ever beat rho.

Depends on costmodel.py for the charged cost, and on EXP-FROB-ec08b5's lattice /
orbits / analysis modules for the Frobenius orbit reduction factor R(l), which
is what decides whether the linear-algebra gate can be relaxed at all.
"""
import sys
from math import log2
from pathlib import Path

# EXP-FROB-ec08b5 owns the stable-subspace lattice and the orbit census.
_FROB = Path(__file__).resolve().parents[2] / "EXP-FROB-ec08b5" / "impl"
if str(_FROB) not in sys.path:
    sys.path.insert(0, str(_FROB))

from costmodel import charged_budget, rho_log2, index_calculus          # noqa: E402
from analysis import spectrum                                            # noqa: E402


def orbit_reduction(q, n):
    """l -> mean Frobenius orbit size on a stable V of dimension l, else 1.

    A dimension that is not attainable, or attainable only as the fixed line,
    gets R = 1: EXP-FROB-ec08b5 showed sigma acts trivially on exactly one line.
    """
    sp = spectrum(q, n)
    faithful = {d for d, v in sp.items() if v["max_orbit_size"] > 1 and d < n}
    return lambda l: (sp[l]["reduction_factor"] if l in faithful else 1.0)


def best_cell(q, n, m, use_frobenius=True):
    """The l maximising the per-decomposition budget at this arity."""
    R = orbit_reduction(q, n) if use_frobenius else (lambda l: 1.0)
    best = None
    for l in range(1, n + 1):
        r = charged_budget(q, n, m, l, R(l))
        if r.get("log2_budget") is None:
            continue
        if best is None or r["log2_budget"] > best["log2_budget"]:
            best = r
    return best


def minimum_viable_arity(q, n, use_frobenius=True, m_max=16):
    """Smallest m whose best cell has a positive budget: below it, even a FREE
    decomposition oracle loses to rho."""
    for m in range(2, m_max + 1):
        b = best_cell(q, n, m, use_frobenius)
        if b is not None and b["log2_budget"] > 0:
            return m
    return None


def boolean_degree(m, l):
    """Weil-descended Boolean degree of S_{m+1} with a dimension-l factor base.

    Every Frobenius power z -> z^(2^k) is F_2-linear, so a K-monomial x^e costs
    Boolean degree equal to the Hamming weight of e, not e.  S_{m+1} has degree
    2^(m-1) in each of its m free variables, whose largest Hamming weight is
    m-1 (the exponent 2^(m-1) - 1).  Each x_i is a linear form in only l Boolean
    variables, so a product of w of its Frobenius powers has degree at most
    min(w, l).  Hence m * min(m-1, l), which is m(m-1) in the usual regime
    l >= m-1 and strictly less when the factor base is very low-dimensional.

    The `min` is not a guess: the driver MEASURES the degree, and the l = 2,
    m = 4 cell came back 8 rather than 12, which is what put it here.
    """
    return m * min(m - 1, l)


def anf_log2_monomials(variables, degree):
    """log2 of the dense monomial count of the descended system, sum_i<=D C(v,i).

    Forming the descended system at all costs at least one operation per
    monomial, so this is a solver-independent lower bound on ONE decomposition
    attempt -- for any method that materialises the system, which is what every
    implemented approach (Groebner, WDSat, CNF-SAT, crossbred, msolve) does.
    Measured density on the toy cells is 0.27-0.81 of this bound, so it is tight
    to within about two bits and is NOT a loose over-estimate.
    """
    from math import comb
    return log2(sum(comb(variables, i) for i in range(min(degree, variables) + 1)))


def curve_table(q, targets, m_values, use_frobenius=True):
    rows = []
    for n, note in targets:
        row = dict(q=q, n=n, note=note, log2_rho=rho_log2(q, n),
                   minimum_viable_arity=minimum_viable_arity(q, n, use_frobenius),
                   minimum_viable_arity_no_frobenius=minimum_viable_arity(q, n, False),
                   cells=[])
        for m in m_values:
            b = best_cell(q, n, m, use_frobenius)
            if b is None:
                row["cells"].append(dict(m=m, viable=False,
                                         reason="linear algebra alone exceeds rho"))
                continue
            row["cells"].append(dict(
                m=m, l=b["l"], R=b["R"],
                log2_budget=b["log2_budget"],
                free_oracle_loses=b["free_oracle_loses"],
                log2_factor_base=b["log2_factor_base"],
                log2_linear_algebra=b["log2_linear_algebra_share"],
                log2_memory_entries=b["log2_memory_entries"],
                log2_attempts=b["log2_attempts"],
                boolean_variables=b["boolean_variables"],
                boolean_degree=boolean_degree(m, b["l"]),
                log2_anf_monomials=anf_log2_monomials(
                    int(b["boolean_variables"]), boolean_degree(m, b["l"])),
                anf_exceeds_budget=(anf_log2_monomials(
                    int(b["boolean_variables"]), boolean_degree(m, b["l"]))
                    > b["log2_budget"]),
                log2_anf_deficit=(anf_log2_monomials(
                    int(b["boolean_variables"]), boolean_degree(m, b["l"]))
                    - b["log2_budget"]),
                required_solver_exponent=b["required_solver_exponent"]))
        rows.append(row)
    return rows
