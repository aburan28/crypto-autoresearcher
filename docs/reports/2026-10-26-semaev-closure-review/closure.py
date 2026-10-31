"""Compute a precisely defined finite Boolean-quotient filtration.

This is a fixed-point calculation on one frozen draw, not a claim about the
polynomial-ring V_{F,D} of Caminata--Gorla or about all Semaev systems.
"""

import hashlib
import json
import subprocess

import audit


def row_degree(row):
    result = -1
    while row:
        bit = row & -row
        result = max(result, audit.degree(bit.bit_length() - 1))
        row ^= bit
    return result


class FilteredBasis:
    """Echelon basis with high-degree columns first.

    A row's leading pivot has its actual degree. Each later row is reduced
    against earlier pivots, so the rows with pivot degree <= d span exactly
    the degree-<=d intersection of the current span.
    """

    def __init__(self, rows=(), nvars=8):
        self.pivots = {}
        self.order = sorted(range(1 << nvars),
                            key=lambda m: (-audit.degree(m), -m))
        for row in rows:
            self.add(row)

    def add(self, row):
        for column in self.order:
            if row & (1 << column):
                if column in self.pivots:
                    row ^= self.pivots[column]
                else:
                    self.pivots[column] = row
                    return True
        return False

    @property
    def rank(self):
        return len(self.pivots)

    def rows(self):
        return list(self.pivots.values())


class NumericBasis:
    """Independent highest-mask echelon basis; it does not filter by degree."""

    def __init__(self, rows=()):
        self.pivots = {}
        for row in rows:
            self.add(row)

    def add(self, row):
        while row:
            pivot = row.bit_length() - 1
            if pivot not in self.pivots:
                self.pivots[pivot] = row
                return True
            row ^= self.pivots[pivot]
        return False

    def rows(self):
        return list(self.pivots.values())


def closure(equations, bound, method, nvars=8):
    """Least degree-bounded span closed under allowed Boolean products.

    `variables` uses one-variable products repeatedly. `all_monomials` adds
    every monomial within the current vector's remaining degree budget.
    Their independent fixed points must have the same row space.
    """
    seed = [audit.packed(eq) for eq in equations
            if max(map(audit.degree, eq)) <= bound]
    basis = FilteredBasis(seed, nvars)
    variables = tuple(1 << bit for bit in range(nvars))
    passes = 0
    while True:
        snapshot = list(basis.pivots.items())
        new_rows = 0
        for pivot, row in snapshot:
            allowance = bound - audit.degree(pivot)
            if method == "variables":
                multipliers = variables if allowance >= 1 else ()
            elif method == "all_monomials":
                multipliers = (m for m in range(1 << nvars)
                               if audit.degree(m) <= allowance)
            else:
                raise ValueError(method)
            for multiplier in multipliers:
                product = audit.multiply_boolean(row, multiplier)
                if row_degree(product) > bound:
                    raise RuntimeError("degree budget was exceeded")
                if basis.add(product):
                    new_rows += 1
        if not new_rows:
            break
        passes += 1
        if passes > 256:
            raise RuntimeError("finite closure failed to stabilize")
    top = audit.packed(m for m in range(1 << nvars)
                       if audit.degree(m) == bound)
    projected_rank = audit.rank(row & top for row in basis.rows())
    return basis, {
        "seed_rank": audit.rank(seed), "rank": basis.rank,
        "projected_rank": projected_rank,
        "low_degree_dimension": basis.rank - projected_rank,
        "expansion_passes": passes,
    }


def projection_kernel_closure(equations, bound, nvars=8):
    """Third method: find low-degree vectors as a projection kernel.

    The basis uses numeric pivots. Gaussian elimination of its top-degree
    projections tracks the same combinations of full rows; zero projections
    supply a basis of the low-degree intersection. Multiply those by each
    variable and repeat. This does not rely on FilteredBasis or ORDER.
    """
    seed = [audit.packed(eq) for eq in equations
            if max(map(audit.degree, eq)) <= bound]
    basis = NumericBasis(seed)
    high = audit.packed(m for m in range(1 << nvars)
                        if audit.degree(m) >= bound)
    variables = tuple(1 << bit for bit in range(nvars))
    passes = 0
    while True:
        projected_pivots = {}
        low_vectors = []
        for full_row in basis.rows():
            projected = full_row & high
            residual = full_row
            while projected:
                pivot = projected.bit_length() - 1
                if pivot not in projected_pivots:
                    projected_pivots[pivot] = (projected, residual)
                    break
                old_projected, old_full = projected_pivots[pivot]
                projected ^= old_projected
                residual ^= old_full
            if not projected and residual:
                low_vectors.append(residual)
        new_rows = 0
        for row in low_vectors:
            if row_degree(row) >= bound:
                raise RuntimeError("projection kernel was not low degree")
            for variable in variables:
                if basis.add(audit.multiply_boolean(row, variable)):
                    new_rows += 1
        if not new_rows:
            break
        passes += 1
        if passes > 256:
            raise RuntimeError("projection-kernel closure failed to stabilize")
    projected_rank = audit.rank(row & high for row in basis.rows())
    return basis, {
        "seed_rank": audit.rank(seed), "rank": len(basis.pivots),
        "projected_rank": projected_rank,
        "low_degree_dimension": len(basis.pivots) - projected_rank,
        "expansion_passes": passes,
    }


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    raw = subprocess.check_output(["git", "show", "HEAD:" + audit.ARCHIVE])
    archive = json.loads(raw)
    matches = [draw for draw in archive["draws"] if
               (draw["n"], draw["nprime"], draw["draw"]) == (4, 4, 1)]
    check(len(matches) == 1, "frozen draw identity changed")
    draw = matches[0]
    equations = draw["equations"]
    check(draw["equations_sha256"] == audit.EQUATIONS_SHA256 and
          audit.derive_equations(draw["basis"], draw["xR"]) == equations,
          "source-bound equations changed")

    profiles = {}
    spaces = {}
    for bound in (1, 2, 3):
        first, a = closure(equations, bound, "variables")
        second, b = closure(equations, bound, "all_monomials")
        third, c = projection_kernel_closure(equations, bound)
        check((a["rank"], a["projected_rank"]) ==
              (b["rank"], b["projected_rank"]) and
              (a["rank"], a["projected_rank"]) ==
              (c["rank"], c["projected_rank"]) and
              audit.rank(first.rows() + second.rows() + third.rows()) == a["rank"],
              "independent closure methods disagree")
        for policy in ("strict_multiplier_budget", "product_degree"):
            direct = audit.rows_for_degree(equations, bound, policy)
            check(audit.rank(first.rows() + direct) == a["rank"],
                  "direct rows not contained in the closed space")
        profiles[str(bound)] = {"variable_steps": a,
                                "all_monomials": b,
                                "projection_kernel": c}
        spaces[bound] = first

    expected = ((1, 1), (11, 10), (79, 56))
    check(tuple((profiles[str(d)]["variable_steps"]["rank"],
                 profiles[str(d)]["variable_steps"]["projected_rank"])
                for d in (1, 2, 3)) == expected,
          "closed finite ranks changed")
    check(audit.rank(spaces[3].rows() + spaces[2].rows()) == 79,
          "closed degree-two space is not contained in degree three")
    witness = audit.packed(audit.WITNESS_TERMS)
    product = audit.multiply_boolean(witness, 1)
    check(audit.rank(spaces[2].rows() + [witness]) == 12,
          "published witness entered closed degree-two span")
    check(audit.rank(spaces[3].rows() + [witness, product]) == 79,
          "published witness or its product absent from closed degree-three span")
    check(row_degree(witness) == 2 and row_degree(product) == 3,
          "witness degrees changed")

    result = {
        "schema": "semaev-boolean-closure-audit/v1",
        "archive_sha256": hashlib.sha256(raw).hexdigest(),
        "equations_sha256": audit.EQUATIONS_SHA256,
        "ring": "F2[u0..u7]/(ui^2-ui), squarefree monomial degree",
        "filtration_rule": "least span of input equations closed under f*g when deg(g)<=D-deg(f)",
        "profiles": profiles,
        "new_falls": {
            "2": profiles["2"]["variable_steps"]["low_degree_dimension"] -
                 profiles["1"]["variable_steps"]["rank"],
            "3": profiles["3"]["variable_steps"]["low_degree_dimension"] -
                 profiles["2"]["variable_steps"]["rank"],
        },
        "witness_outside_closed_degree_two": True,
        "witness_and_u0_product_inside_closed_degree_three": True,
        "closed_degree_two_in_closed_degree_three": True,
        "scope": "one finite Boolean quotient; no polynomial-ring transfer",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
