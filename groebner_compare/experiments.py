"""Bounded GF(2) solver experiments; every returned claim is checked by runner.

These are transparent research prototypes for small Boolean systems, not the
published WDSat, F4, Crossbred, or M5GB implementations.
"""

from .certificate import certify, monomial_key, terms, vanishes


def bits(rows):
    return [sum(1 << monomial for monomial in row) for row in rows]


def unpack(polynomial):
    result = []
    while polynomial:
        bit = polynomial & -polynomial
        result.append(bit.bit_length() - 1)
        polynomial ^= bit
    return result


class BooleanF4:
    """Batch pair reduction with symbolic reducer multiples and field pairs."""

    def __init__(self, n, blocks=None, *, max_rows=4096, max_pairs=20000,
                 progress=None):
        self.n = n
        self.blocks = blocks
        self.key = lambda mask: monomial_key(mask, n, blocks)
        self.max_rows, self.max_pairs = max_rows, max_pairs
        self.progress = progress
        self.stats = dict(highest_degree=0, largest_matrix_rows=0,
                          largest_matrix_columns=0, pairs=0, batch_count=0)

    def leading(self, polynomial):
        return max(unpack(polynomial), key=self.key)

    def multiply(self, polynomial, multiplier):
        result = 0
        for monomial in unpack(polynomial):
            result ^= 1 << (monomial | multiplier)
        return result

    def normal(self, polynomial, basis):
        remainder = 0
        reducers = sorted((b for b in basis if b), key=lambda b: self.key(self.leading(b)),
                          reverse=True)
        while polynomial:
            lead = self.leading(polynomial)
            reducer = next((b for b in reducers
                            if self.leading(b) & lead == self.leading(b)), None)
            if reducer is None:
                polynomial ^= 1 << lead
                remainder ^= 1 << lead
            else:
                polynomial ^= self.multiply(reducer, lead & ~self.leading(reducer))
        return remainder

    def solve(self, equations):
        basis = []
        for polynomial in bits(terms(equations, self.n)):
            remainder = self.normal(polynomial, basis)
            if remainder:
                basis.append(remainder)
        pending = []

        def install(index):
            leader = self.leading(basis[index])
            for i in range(index):
                if leader & self.leading(basis[i]):
                    pending.append((i, index))
            for variable in range(self.n):
                if leader & (1 << variable):
                    pending.append((index, -variable - 1))

        for index in range(len(basis)):
            install(index)
        while pending:
            if self.stats["pairs"] >= self.max_pairs:
                raise TimeoutError("Boolean F4 pair budget")
            pending.sort(key=lambda pair: self.key(
                self.leading(basis[pair[0]]) | (
                    self.leading(basis[pair[1]]) if pair[1] >= 0 else 0)), reverse=True)
            selected = [pending.pop() for _ in range(min(12, len(pending)))]
            rows = []
            for i, j in selected:
                left = basis[i]
                if j < 0:
                    # In the Boolean quotient x_i * LT(f) = LT(f) here.
                    polynomial = self.multiply(left, 1 << (-j - 1)) ^ left
                else:
                    right = basis[j]
                    lcm = self.leading(left) | self.leading(right)
                    polynomial = (self.multiply(left, lcm & ~self.leading(left))
                                  ^ self.multiply(right, lcm & ~self.leading(right)))
                if polynomial:
                    rows.append(polynomial)
            self.stats["pairs"] += len(selected)
            if not rows:
                continue
            # F4 symbolic preprocessing: add reducer multiples for discovered
            # columns, then eliminate the entire sparse batch over GF(2).
            seen = set(rows)
            columns = set()
            to_visit = [m for row in rows for m in unpack(row)]
            while to_visit:
                monomial = to_visit.pop()
                if monomial in columns:
                    continue
                columns.add(monomial)
                for reducer in basis:
                    lead = self.leading(reducer)
                    if lead & monomial != lead:
                        continue
                    multiple = self.multiply(reducer, monomial & ~lead)
                    if multiple not in seen:
                        seen.add(multiple)
                        rows.append(multiple)
                        to_visit.extend(unpack(multiple))
                        if len(rows) > self.max_rows:
                            self.stats["largest_matrix_rows"] = len(rows)
                            self.stats["largest_matrix_columns"] = len(columns)
                            if self.progress:
                                self.progress(self.stats)
                            raise TimeoutError("Boolean F4 matrix-row budget")
            self.stats["largest_matrix_rows"] = max(self.stats["largest_matrix_rows"], len(rows))
            self.stats["largest_matrix_columns"] = max(self.stats["largest_matrix_columns"],
                                                        len(columns))
            self.stats["highest_degree"] = max(self.stats["highest_degree"],
                                               *(m.bit_count() for m in columns))
            self.stats["batch_count"] += 1
            if self.progress:
                self.progress(self.stats)
            pivots = {}
            for row in rows:
                while row:
                    lead = self.leading(row)
                    if lead not in pivots:
                        pivots[lead] = row
                        break
                    row ^= pivots[lead]
            for row in sorted(pivots.values(), key=lambda b: self.key(self.leading(b))):
                remainder = self.normal(row, basis)
                if remainder:
                    basis.append(remainder)
                    install(len(basis) - 1)
        return [unpack(row) for row in basis]


def elimlin(equations, n, *, degree=3, rounds=3, max_rows=12000):
    """Derive affine consequences from degree-bounded Macaulay rows.

    RREF rows remain in the original ideal. Returns them as extra generators;
    the independent certificate checks the final basis, including the inputs.
    """
    source = bits(terms(equations, n))
    consequences = []
    stats = dict(elimlin_rows=0, elimlin_rounds=0, elimlin_affine=0)
    for _ in range(rounds):
        rows = []
        for original in source + consequences:
            for multiplier in range(1 << n):
                if multiplier.bit_count() >= degree:
                    continue
                product = 0
                for term in unpack(original):
                    product ^= 1 << (term | multiplier)
                if product and max(m.bit_count() for m in unpack(product)) <= degree:
                    rows.append(product)
                if len(rows) > max_rows:
                    raise TimeoutError("ElimLin Macaulay-row budget")
        pivots = {}
        for row in rows:
            while row:
                lead = max(unpack(row), key=lambda m: monomial_key(m, n))
                if lead not in pivots:
                    pivots[lead] = row
                    break
                row ^= pivots[lead]
        # Backward elimination reveals low-degree consequences hidden by pivots.
        for lead in sorted(pivots, key=lambda m: monomial_key(m, n)):
            for other in pivots:
                if other != lead and pivots[other] & (1 << lead):
                    pivots[other] ^= pivots[lead]
        found = [row for row in pivots.values() if row
                 and all(term.bit_count() <= 1 for term in unpack(row))
                 and row not in source and row not in consequences]
        stats["elimlin_rows"] += len(rows)
        stats["elimlin_rounds"] += 1
        consequences.extend(found)
        if not found:
            break
    stats["elimlin_affine"] = len(consequences)
    return [unpack(row) for row in consequences], stats


def xor_sat(equations, n, *, branch_limit=100000):
    """XOR Gaussian propagation plus AND Tseitin gates and binary branching.

    Finds one assignment; no UNSAT claim or complete basis is returned.
    Internal bounded control used when an external XOR-SAT engine is absent.
    """
    polys = terms(equations, n)
    nonlinear = sorted({m for row in polys for m in row if m.bit_count() > 1})
    symbol = {m: n + i for i, m in enumerate(nonlinear)}
    linear = []
    for row in polys:
        mask, rhs = 0, 0
        for monomial in row:
            if monomial == 0:
                rhs ^= 1
            else:
                mask ^= 1 << (symbol[monomial] if monomial in symbol else
                              monomial.bit_length() - 1)
        linear.append((mask, rhs))
    nodes = 0

    def visit(values):
        nonlocal nodes
        nodes += 1
        if nodes > branch_limit:
            raise TimeoutError("XOR-SAT branch budget")
        values = dict(values)
        while True:
            prior = len(values)
            # Unit and pairwise XOR elimination under assigned variables.
            pivots = {}
            for mask, rhs in linear:
                for index, bit in values.items():
                    if mask & (1 << index):
                        mask ^= 1 << index
                        rhs ^= bit
                while mask:
                    lead = mask.bit_length() - 1
                    if lead not in pivots:
                        pivots[lead] = (mask, rhs)
                        break
                    reduction, parity = pivots[lead]
                    mask ^= reduction
                    rhs ^= parity
                if mask == 0 and rhs:
                    return None
            for mask, rhs in pivots.values():
                if mask.bit_count() == 1:
                    index = mask.bit_length() - 1
                    if index in values and values[index] != rhs:
                        return None
                    values[index] = rhs
            # Propagate every AND gate in both directions.
            for monomial, gate in symbol.items():
                factors = [i for i in range(n) if monomial & (1 << i)]
                known = [values.get(i) for i in factors]
                gate_value = values.get(gate)
                if 0 in known:
                    if gate_value == 1:
                        return None
                    values[gate] = 0
                elif all(value == 1 for value in known):
                    if gate_value == 0:
                        return None
                    values[gate] = 1
                elif gate_value == 1:
                    for i in factors:
                        values[i] = 1
                elif gate_value == 0 and known.count(None) == 1 and all(
                        value in (1, None) for value in known):
                    values[factors[known.index(None)]] = 0
            if len(values) == prior:
                break
        if all(i in values for i in range(n)):
            assignment = sum(values[i] << i for i in range(n))
            return assignment if vanishes(polys, assignment) else None
        # Original variables first to avoid treating auxiliary gate values as
        # an alternative solution dimension.
        variable = next(i for i in range(n) if i not in values)
        for bit in (0, 1):
            found = visit({**values, variable: bit})
            if found is not None:
                return found
        return None

    return visit({}), {"xor_sat_nodes": nodes, "xor_sat_gates": len(nonlinear),
                       "xor_sat_linear_equations": len(linear)}


def hybrid(equations, n, *, guess=2, blocks=None, branch_solver=None,
           progress=None):
    """Sequential guess-and-solve, charging each failed branch."""
    if not 0 <= guess <= min(n, 5):
        raise ValueError("hybrid guess must be in 0..min(n,5)")
    masks = terms(equations, n)
    # Score by appearances in high-degree input terms; stable tie-break.
    scores = [sum(2 ** (m.bit_count() - 1) for row in masks for m in row
                  if m & (1 << v)) for v in range(n)]
    chosen = sorted(range(n), key=lambda v: (-scores[v], v))[:guess]
    survivors = [v for v in range(n) if v not in chosen]
    attempts = []
    for candidate in range(1 << guess):
        fixed = {v: candidate >> i & 1 for i, v in enumerate(chosen)}
        specialized = []
        for row in masks:
            result = set()
            for monomial in row:
                if any(monomial & (1 << v) and not fixed[v] for v in chosen):
                    continue
                reduced = sum(1 << i for i, v in enumerate(survivors)
                              if monomial & (1 << v))
                result.symmetric_difference_update((reduced,))
            specialized.append(sorted(result))
        if not survivors:
            if vanishes(specialized, 0):
                answer = sum(fixed[v] << v for v in chosen)
                attempts.append({"branch": candidate, "status": "verified_witness"})
                return answer, attempts
            attempts.append({"branch": candidate, "status": "exhausted"})
            continue
        reduced_blocks = None
        if blocks and all(blocks):
            split, reduced_blocks = 0, []
            for size in blocks:
                remaining = sum(split <= v < split + size for v in survivors)
                if remaining:
                    reduced_blocks.append(remaining)
                split += size
        if branch_solver is not None:
            root, metrics = branch_solver(specialized, len(survivors))
            if root is None:
                # This path does not provide an independently checked UNSAT
                # proof, unlike a complete and certified F4 branch.
                attempts.append({"branch": candidate, "status": "no_witness",
                                 "metrics": metrics})
                continue
            assignment = sum(fixed[v] << v for v in chosen)
            assignment |= sum(((root >> i) & 1) << v for i, v in enumerate(survivors))
            if not vanishes(masks, assignment):
                raise ValueError("hybrid SAT branch returned an invalid root")
            attempts.append({"branch": candidate, "status": "verified_witness",
                             "metrics": metrics})
            return assignment, attempts
        solver = BooleanF4(len(survivors), reduced_blocks,
                           progress=(lambda report: progress({"branch": candidate,
                                                               **report})) if progress else None)
        basis = solver.solve(specialized)
        certificate = certify(len(survivors), specialized, basis, blocks=reduced_blocks)
        if not certificate["verified"]:
            raise ValueError("hybrid branch basis failed independent certificate")
        roots = certificate["solutions"]
        if roots is None:  # solve only instances with <= 256 roots per branch
            raise ValueError("hybrid branch has too many roots for bounded extraction")
        if roots:
            assignment = sum(fixed[v] << v for v in chosen)
            assignment |= sum(((roots[0] >> i) & 1) << v for i, v in enumerate(survivors))
            attempts.append({"branch": candidate, "status": "verified_witness",
                             "metrics": solver.stats})
            return assignment, attempts
        attempts.append({"branch": candidate, "status": "exhausted",
                         "metrics": solver.stats})
    return None, attempts
