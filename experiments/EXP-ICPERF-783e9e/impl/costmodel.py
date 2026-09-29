"""Fully charged cost model for Gaudry/Diem index calculus on E(F_{q^n}),
inverted to give the DECOMPOSITION-SOLVER BUDGET that would make it beat rho.

Everything is in log2 of group operations (or of F_q operations, treated as
comparable to within the log factors this model already drops -- stated, not
hidden).

Pipeline, factor base F_V = {P : x(P) in V}, dim_{F_q} V = l, m summands:
  |F|        ~ q^l                         factor-base size
  R          = mean Frobenius orbit size    (n where a faithful stable V exists,
                                             else 1; EXP-FROB-ec08b5 decides it)
  D          = |F| / R                      linear-algebra dimension
  p          = min(1, q^(ml-n) / m!)        a random target decomposes
  relations  = D                            relations needed
  attempts   = D / p                        decomposition attempts
  RELATION COLLECTION = attempts * C_solve
  LINEAR ALGEBRA      = m * D^2             sparse Wiedemann/Lanczos, m nonzeros/row
  MEMORY              = D                   factor base + relations held at once

Baseline: Pollard rho, sqrt(pi*N/4) group ops, divided by sqrt(2n) on a subfield
curve (Frobenius classes and negation) or sqrt(2) otherwise.  Memory O(1).

The inversion: index calculus beats rho only if BOTH the linear algebra and the
relation collection come in under the rho cost.  The linear algebra does not
depend on the solver at all, so it is a hard feasibility gate on l; given an l
that passes it, the relation stage leaves a budget

      C_solve_max = rho / (D / p) = rho * p * R / q^l

which is the number of operations one point decomposition may take.  That is the
target this whole research programme is actually chasing.

ASSUMPTIONS, stated so they can be attacked:
  A1 |F| ~ q^l.  Each x in V lifts to 0 or 2 points, so |F| ~ q^l on average.
  A2 Decompositions behave like uniform random m-multisets of F (the standard
     heuristic; it is the one Gaudry, Diem and Joux-Vitse all make).
  A3 Sparse linear algebra costs m*D^2 field operations.  The double-large-prime
     variant lowers this and is modelled separately as `dlp_linear_algebra`.
  A4 Group operations and F_q operations are compared directly; polylog factors
     are dropped on BOTH sides, so the comparison is fair to within them.
  A5 Memory is charged but not priced -- it is reported, not converted into time.
"""
from math import log2, lgamma, pi, sqrt


def log2_factorial(m):
    return lgamma(m + 1) / log2(2.718281828459045) / 1.4426950408889634 if False else lgamma(m + 1) / 0.6931471805599453


def rho_log2(q, n, subfield_curve=True):
    """log2 of Pollard rho cost in group operations, with the symmetry speedup."""
    N = n * log2(q)
    base = 0.5 * N + log2(sqrt(pi / 4))
    speed = 0.5 * log2(2 * n) if subfield_curve else 0.5 * log2(2)
    return base - speed


def index_calculus(q, n, m, l, R=1.0):
    """Charged cost of one (m, l, R) choice. All fields are log2."""
    lq = log2(q)
    N = n * lq
    logF = l * lq
    logD = logF - log2(R)
    logp = min(0.0, (m * l - n) * lq - log2_factorial(m))
    log_attempts = logD - logp
    log_la = log2(m) + 2 * logD
    return dict(q=q, n=n, m=m, l=l, R=R, N=N,
                log2_factor_base=logF, log2_la_dimension=logD,
                log2_decomposition_probability=logp,
                log2_attempts=log_attempts,
                log2_linear_algebra=log_la,
                log2_memory_entries=logD)


def solver_budget(q, n, m, l, R=1.0, subfield_curve=True):
    """How fast one point decomposition must be for this cell to beat rho."""
    ic = index_calculus(q, n, m, l, R)
    rho = rho_log2(q, n, subfield_curve)
    la_ok = ic["log2_linear_algebra"] < rho
    budget = rho - ic["log2_attempts"]        # log2 ops allowed per decomposition
    # the descended Boolean system this budget has to be spent on
    boolean_vars = m * l * log2(q)
    return dict(ic, log2_rho=rho,
                linear_algebra_fits=la_ok,
                log2_la_headroom=rho - ic["log2_linear_algebra"],
                log2_solver_budget=budget,
                boolean_variables=boolean_vars,
                log2_exhaustive_solve=boolean_vars,
                log2_speedup_needed_over_exhaustive=boolean_vars - budget,
                required_solver_exponent=(budget / boolean_vars) if boolean_vars else None,
                feasible=la_ok and budget > 0)


def best_cell(q, n, R_available, m_range=range(2, 13), subfield_curve=True):
    """The (m, l) that leaves the LARGEST solver budget while the LA still fits."""
    best = None
    for m in m_range:
        for l in range(1, n + 1):
            r = solver_budget(q, n, m, l, R_available, subfield_curve)
            if not r["linear_algebra_fits"]:
                continue
            if best is None or r["log2_solver_budget"] > best["log2_solver_budget"]:
                best = r
    return best


def charged_budget(q, n, m, l, R=1.0, subfield_curve=True):
    """Stricter than solver_budget: charge relation collection AND linear algebra
    against the SAME rho budget, rather than gating them separately.

    budget_per_decomposition = (rho - linear_algebra) / attempts

    A negative or near-zero value means the cell is dead even with a FREE
    decomposition oracle -- no solver engineering whatsoever can rescue it.
    """
    ic = index_calculus(q, n, m, l, R)
    rho = rho_log2(q, n, subfield_curve)
    la = ic["log2_linear_algebra"]
    if la >= rho:
        return dict(ic, log2_rho=rho, free_oracle_loses=True,
                    log2_budget=None,
                    reason="linear algebra alone exceeds rho")
    # rho - la, in log2
    remaining = rho + log2(1.0 - 2.0 ** (la - rho))
    budget = remaining - ic["log2_attempts"]
    return dict(ic, log2_rho=rho, log2_linear_algebra_share=la,
                log2_remaining_for_relations=remaining,
                log2_budget=budget,
                free_oracle_loses=(budget <= 0),
                boolean_variables=m * l * log2(q),
                required_solver_exponent=budget / (m * l * log2(q)))


def best_charged(q, n, R_fn, m, subfield_curve=True):
    best = None
    for l in range(1, n + 1):
        r = charged_budget(q, n, m, l, R_fn(l), subfield_curve)
        if r.get("log2_budget") is None:
            continue
        if best is None or r["log2_budget"] > best["log2_budget"]:
            best = r
    return best
