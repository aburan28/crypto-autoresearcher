"""Exact Boolean certificates, independent of a solver's completion flag.

Uses the zeros-and-staircase argument also used by cryptanalysis's
experiments/pdp-scaling/boolean_basis.py. Limited to twelve variables on purpose.
"""


def terms(rows, nvars):
    if not isinstance(rows, list):
        raise ValueError("polynomials must be lists of monomial masks")
    result = []
    for row in rows:
        if not isinstance(row, list):
            raise ValueError("polynomial must be a list")
        parity = set()
        for mask in row:
            if type(mask) is not int or not 0 <= mask < 1 << nvars:
                raise ValueError("invalid Boolean monomial")
            parity.symmetric_difference_update((mask,))
        result.append(sorted(parity))
    return result


def vanishes(rows, assignment):
    return all(sum((mask & assignment) == mask for mask in row) % 2 == 0
               for row in rows)


def certify(nvars, equations, basis):
    """Prove ideal equality AND the GB property in the Boolean quotient.

    If G vanishes on all input zeros Z, <G> is contained in I(Z).
    The number of standard squarefree monomials bounds dim(R/<G>) above.
    Equality with |Z| proves ideal equality and the leading-ideal property.
    This certificate does not assert reducedness or a curve relation.
    """
    if type(nvars) is not int or not 1 <= nvars <= 12:
        raise ValueError("exact certificate requires 1..12 Boolean variables")
    equations = terms(equations, nvars)
    basis = terms(basis, nvars)
    roots = [a for a in range(1 << nvars) if vanishes(equations, a)]
    leading = [max(row, key=lambda m: (m.bit_count(), -m))
               for row in basis if row]
    dimension = sum(not any(m & a == m for m in leading)
                    for a in range(1 << nvars))
    verified = (dimension == len(roots)
                and all(vanishes(basis, a) for a in roots))
    return {"verified": verified, "method": "exact-Boolean-zeros-and-staircase",
            "root_count": len(roots), "standard_monomials": dimension,
            "solutions": roots if verified else None,
            "ideal_equality": verified, "groebner_basis": verified}


class Rank:
    """Incremental rank of already independently verified relation vectors."""

    def __init__(self, modulus, width):
        # Deliberately bounded trial division: this is the toy protocol, not a
        # probable-prime certificate for a production subgroup.
        if (type(modulus) is not int or not 2 <= modulus <= 65521
                or any(modulus % d == 0 for d in range(2, int(modulus ** .5) + 1))):
            raise ValueError("relation modulus must be a prime <= 65521")
        if type(width) is not int or not 1 <= width <= 4096:
            raise ValueError("invalid relation width")
        self.modulus, self.width, self.pivots = modulus, width, {}

    def add(self, vectors):
        # Validate the entire batch before mutating rank.
        if not isinstance(vectors, list) or any(
                not isinstance(v, list) or len(v) != self.width
                or any(type(x) is not int for x in v) for v in vectors):
            raise ValueError("invalid verified relation vectors")
        before = len(self.pivots)
        for vector in vectors:
            row = [x % self.modulus for x in vector]
            for col in range(self.width):
                if row[col] == 0:
                    continue
                if col in self.pivots:
                    factor = row[col]
                    row = [(x - factor * y) % self.modulus
                           for x, y in zip(row, self.pivots[col])]
                else:
                    inv = pow(row[col], -1, self.modulus)
                    self.pivots[col] = [x * inv % self.modulus for x in row]
                    break
        return len(self.pivots) - before
