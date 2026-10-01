"""Adapters: SymPy reference, Sage PolyBoRi, repository Boolean F5B.

Run from the repository root with python -m groebner_compare.worker NAME.
All imported solver output is redirected to stderr to preserve JSONL framing.
"""

import contextlib
import json
from pathlib import Path
import sys


def solve(name, request):
    from .certificate import terms
    n = request["ring"]["nvars"]
    equations = terms(request["instance"]["equations"], n)
    if request["operation"] != "solve":
        return {"status": "incompatible", "reason": "adapter has no tracing API"}
    if name == "sympy":
        import sympy as sp
        variables = sp.symbols(f"x0:{n}")
        polys = [sum(sp.prod(variables[i] for i in range(n) if mask >> i & 1)
                     for mask in row) for row in equations]
        polys += [x*x + x for x in variables]
        basis = sp.groebner(polys, *variables, modulus=2, order="grevlex")
        rows = []
        for poly in basis.polys:
            row = [sum(1 << i for i, power in enumerate(exponents) if power)
                   for exponents, coefficient in poly.terms() if int(coefficient) % 2]
            rows.append(row)
        version = sp.__version__
    elif name == "polybori":
        from sage.all import BooleanPolynomialRing
        from sage.env import SAGE_VERSION
        ring = BooleanPolynomialRing(n, names=tuple(f"x{i}" for i in range(n)),
                                     order="degrevlex")
        variables = ring.gens()
        polys = []
        for row in equations:
            polynomial = ring.zero()
            for mask in row:
                monomial = ring.one()
                for i in range(n):
                    if mask >> i & 1:
                        monomial *= variables[i]
                polynomial += monomial
            polys.append(polynomial)
        # Sage's BooleanPolynomialRing(..., order="degrevlex") returns monomial
        # .variables() tuples whose *name* is reversed relative to the ring's own
        # gens() (variables[i] reports as variables()[n-1-i]); matching by object
        # or name against `variables` silently mismasks every non-palindromic
        # monomial. The monomial's own string form is not affected, so mask
        # from that instead. An explicit empty-generator groebner_basis() call
        # also raises IndexError in this Sage/PolyBoRi version; the zero ideal's
        # basis is the empty list by definition, so skip the call entirely.
        basis = ring.ideal(polys).groebner_basis() if polys else []
        names = {f"x{i}": i for i in range(n)}
        def mask_of(monomial):
            mask = 0
            for token in str(monomial).split("*"):
                token = token.strip()
                if token in names:
                    mask |= 1 << names[token]
                elif token != "1":
                    raise ValueError(f"unrecognized PolyBoRi monomial token: {token!r}")
            return mask
        rows = [[mask_of(monomial) for monomial in polynomial.monomials()]
                for polynomial in basis]
        version = SAGE_VERSION
    elif name == "repository-f5b":
        source = Path(__file__).resolve().parents[1] / "experiments/pdp-scaling"
        if not (source / "boolean_f5b.py").is_file():
            return {"status": "unavailable", "reason": "repository BooleanF5B source absent"}
        sys.path.insert(0, str(source))
        from boolean_f5b import BooleanF5B
        solver = BooleanF5B(n)
        basis = solver.basis([solver.from_terms(row) for row in equations])
        rows = [list(solver.terms(polynomial)) for polynomial in basis]
        import hashlib
        version = "sha256:" + hashlib.sha256((source / "boolean_f5b.py").read_bytes()).hexdigest()
    else:
        raise ValueError(f"unknown adapter: {name}")
    return {"status": "ok", "basis_terms": terms(rows, n),
            "solver_version": version, "metrics": {}}


def main():
    name = sys.argv[1]
    for line in sys.stdin:
        request = json.loads(line)
        try:
            with contextlib.redirect_stdout(sys.stderr):
                response = solve(name, request)
        except ImportError as error:
            response = {"status": "unavailable", "reason": str(error)}
        except Exception as error:
            response = {"status": "error", "reason": str(error)}
        response["request_id"] = request["request_id"]
        print(json.dumps(response, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
