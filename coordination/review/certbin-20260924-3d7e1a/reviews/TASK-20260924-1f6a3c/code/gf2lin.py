"""GF(2) row spaces with Python-int bit vectors.

Elimination method (declared per BR-1): incremental echelon basis keyed by
leading bit (highest set bit = leading monomial in descending degrevlex). A new
vector is reduced by XOR-ing the basis vector with the same leading bit until it
is zero or has a new leading bit, which it then owns. The basis is echelon (all
leading bits distinct) but not reduced. Consequences used throughout:
  * dim = number of basis vectors;
  * since the order is degree-graded, the basis vectors whose leading bit is
    < N(d) form a basis of (space cap B_{<=d});
  * 1 is in the space iff the basis has a vector with leading bit 0, and that
    vector is exactly the constant 1.
"""


class Space:
    __slots__ = ("basis",)

    def __init__(self):
        self.basis = {}

    @property
    def dim(self):
        return len(self.basis)

    def reduce(self, v):
        basis = self.basis
        while v:
            lb = v.bit_length() - 1
            b = basis.get(lb)
            if b is None:
                return v
            v ^= b
        return 0

    def insert(self, v):
        basis = self.basis
        while v:
            lb = v.bit_length() - 1
            b = basis.get(lb)
            if b is None:
                basis[lb] = v
                return True
            v ^= b
        return False

    def contains(self, v):
        return self.reduce(v) == 0

    def has_one(self):
        return 0 in self.basis

    def dim_below(self, nbits):
        """dim(space cap span of bits < nbits)."""
        return sum(1 for lb in self.basis if lb < nbits)

    def low_basis(self, nbits):
        """Basis of (space cap span of bits < nbits), in ascending leading-bit order."""
        return [self.basis[lb] for lb in sorted(self.basis) if lb < nbits]


class TrackedSpace:
    """Echelon basis that also tracks, for each basis vector, the set of generator
    ids (as an int bitmask) whose sum it is."""
    __slots__ = ("basis",)

    def __init__(self):
        self.basis = {}

    @property
    def dim(self):
        return len(self.basis)

    def insert(self, v, tr):
        basis = self.basis
        while v:
            lb = v.bit_length() - 1
            b = basis.get(lb)
            if b is None:
                basis[lb] = (v, tr)
                return True
            v ^= b[0]
            tr ^= b[1]
        return False

    def has_one(self):
        return 0 in self.basis

    def low_basis(self, nbits):
        return [self.basis[lb] for lb in sorted(self.basis) if lb < nbits]


def rank_of(rows):
    S = Space()
    for r in rows:
        S.insert(r)
    return S
